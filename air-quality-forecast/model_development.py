import mlflow
import mlflow.sklearn
import subprocess
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import mean_squared_error, root_mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from skopt import BayesSearchCV
from skopt.space import Real, Integer, Categorical
from typing import Dict, Any
import socket
import pandas as pd
import warnings
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
import yaml
import os

warnings.filterwarnings("ignore")

RANDOM_SEED = 4242


class RegressorTrainer:
    def __init__(
        self,
        experiment_name: str,
        regressor: BaseEstimator,
        param_space: Dict[str, Any],
        cv_splits: int = 5,
        n_iter: int = 50,
    ):
        """
        Initialize the RegressorTrainer.

        Parameters:
            experiment_name (str): The name of the MLflow experiment.
            regressor (sklearn model): The regressor to optimize.
            param_space (dict): The parameter space for Bayesian optimization.
            cv_splits (int): Number of splits for cross-validation (default is 5).
        """
        self._experiment_name = experiment_name
        self._regressor = regressor
        self._param_space = param_space
        self._cv_splits = cv_splits
        self._bayes_search: BayesSearchCV | None = (
            None  # Will hold the BayesSearchCV object
        )
        self._x_train: np.ndarray | None = None
        self._y_train: np.ndarray | None = None
        self._x_test: np.ndarray | None = None
        self._y_test: np.ndarray | None = None
        self._n_iter = n_iter
        self._current_run = None

    @staticmethod
    def port_in_use(port: int) -> bool:
        """
        Check if a port is in use.

        Parameters:
            port (int): Port to check.

        Returns:
            bool: True if the port is in use, False otherwise.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # This actually returns an int and not a bool
            return s.connect_ex(("localhost", port)) == 0

    @staticmethod
    def launch_mlflow_server() -> None:
        """
        Launch MLflow server at http://127.0.0.1:5000, if not already running.

        If the port is already in use, it will print a message saying so.
        If there is an error launching the server, it will print the error.
        """
        port = 5000
        if not RegressorTrainer.port_in_use(port):
            try:
                subprocess.Popen(
                    ["py", "-m", "mlflow", "ui", "--port", str(port)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                print(f"MLflow server launched at http://127.0.0.1:{port}")
            except Exception:
                try:
                    subprocess.Popen(
                        ["python", "-m", "mlflow", "ui", "--port", str(port)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    print(f"MLflow server launched at http://127.0.0.1:{port}")
                except Exception as e:
                    print("Error launching MLflow server:", e)
                    print(
                        "Both py -m mlflow ui and python -m mlflow ui failed. Please run the server yourself."
                    )
        else:
            print(f"MLflow server is running at http://127.0.0.1:{port}")

    def _set_data(
        self,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_test: np.ndarray,
        y_test: np.ndarray,
    ) -> None:
        """
        Set the training and test data as class attributes.

        Parameters:
            x_train (np.ndarray): Training data features.
            y_train (np.ndarray): Training data labels.
            x_test (np.ndarray): Test data features.
            y_test (np.ndarray): Test data labels.
        """
        self._x_train = np.array(x_train)
        self._y_train = np.array(y_train)
        self._x_test = np.array(x_test)
        self._y_test = np.array(y_test)

    def _setup_mlflow(self) -> None:
        """
        Set up MLflow configuration.

        This method launches the MLflow server, sets the MLflow experiment name and
        tracking URI, enables system metrics logging, and turns on autologging of
        metrics and parameters.

        """
        RegressorTrainer.launch_mlflow_server()
        mlflow.set_experiment(self._experiment_name)
        mlflow.set_tracking_uri("http://localhost:5000/")
        mlflow.enable_system_metrics_logging()
        mlflow.autolog(silent=True)

    def _perform_search(self) -> None:
        """
        Perform Bayesian optimization for hyperparameters.

        This method initializes and performs a BayesSearchCV search for the best
        hyperparameters of the regressor. The search is performed on the training
        data using a TimeSeriesSplit cross-validation scheme. The best
        hyperparameters and the corresponding mean squared error are logged to
        MLflow.

        Raises:
            ValueError: If training data has not been set. Call `_set_data` first.
        """
        if self._x_train is None or self._y_train is None:
            raise ValueError("Training data has not been set. Call `_set_data` first.")

        # Set up TimeSeriesSplit for cross-validation
        time_series_split = TimeSeriesSplit(n_splits=self._cv_splits)

        # Initialize and perform BayesSearchCV
        self._bayes_search = BayesSearchCV(
            estimator=self._regressor,
            search_spaces=self._param_space,
            n_iter=self._n_iter,  # Number of iterations for the search
            cv=time_series_split,  # Cross-validation scheme
            scoring="neg_mean_squared_error",  # Metric for scoring
            n_jobs=-1,  # Use all available CPU cores
            verbose=1,  # To display progress
            random_state=RANDOM_SEED,  # Ensures reproducibility
        )
        self._bayes_search.fit(self._x_train, self._y_train)

        mlflow.log_params(self._bayes_search.best_params_)

        
        best_regressor = self._bayes_search.best_estimator_
        train_mse = mean_squared_error(
            self._y_train, best_regressor.predict(self._x_train)
        )
        
        mlflow.log_metric("Correct Train MSE", train_mse)
        
    def _evaluate_model(self) -> None:
        """
        Evaluate the best model on the test data and log metrics.

        Raises:
            ValueError: If test data has not been set. Call `_set_data` first.
            ValueError: If Bayesian search has not been performed. Call `_perform_search` first.
        """
        if self._x_test is None or self._y_test is None:
            raise ValueError("Test data has not been set. Call `_set_data` first.")
        if self._bayes_search is None:
            raise ValueError(
                "Bayesian search has not been performed. Call `_perform_search` first."
            )

        best_regressor = self._bayes_search.best_estimator_

        # Evaluate the best model
        test_mse = mean_squared_error(
            self._y_test, best_regressor.predict(self._x_test)
        )
        test_rmse = root_mean_squared_error(
            self._y_test, best_regressor.predict(self._x_test)
        )

        mlflow.log_metric("Correct Test MSE", test_mse)
        mlflow.log_metric("Correct Test RMSE", test_rmse)

    def _optimize_and_evaluate(self):
        """
        Perform Bayesian optimization for hyperparameters and evaluate the best model on the test data.

        This method wraps `_perform_search` and `_evaluate_model` in a single MLflow run.

        """
        with mlflow.start_run():
            self._perform_search()
            self._evaluate_model()
            mlflow.end_run()

    def run(
        self,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_test: np.ndarray,
        y_test: np.ndarray,
    ) -> None:
        """
        Run the Bayesian optimization workflow.

        Parameters:
            x_train (np.ndarray): Training data features.
            y_train (np.ndarray): Training data labels.
            x_test (np.ndarray): Test data features.
            y_test (np.ndarray): Test data labels.
        """
        self._set_data(x_train, y_train, x_test, y_test)
        self._setup_mlflow()
        self._optimize_and_evaluate()

def convert_param_space(param_space: dict):
    """
    Convert a parameter space dictionary to a format usable by skopt.

    This function takes a dictionary where the keys are parameter names and the
    values are lists of two values that represent the range of possible values
    for that parameter. The function then converts these ranges to skopt
    parameter objects and returns a new dictionary where the parameter names
    are the same but the values are now skopt parameter objects.

    Parameters:
        param_space (dict): A dictionary with parameter names as keys and ranges
            of possible values as values.

    Returns:
        dict: A dictionary with parameter names as keys and skopt parameter
            objects as values.
    """
    converted_space = {}
    for param, values in param_space.items():
        if isinstance(values[0], bool):
            converted_space[param] = Categorical(values)
        elif all(isinstance(v, int) for v in values):
            converted_space[param] = Integer(values[0], values[1])
        elif all(isinstance(v, float) for v in values):
            converted_space[param] = Real(values[0], values[1])
        elif all(isinstance(v, str) for v in values):
            converted_space[param] = Categorical(values)
        else:
            raise ValueError(f"Unknown parameter type for {param}")
    return converted_space

def run_bayesian_optimization(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    experiment_name: str,
    regressor: BaseEstimator,
    param_space: Dict[str, Any],
    n_iter: int,
) -> None:
    """
    Run Bayesian optimization to search for the best hyperparameters for a given regressor.

    Parameters:
        x_train (np.ndarray): Training data features.
        y_train (np.ndarray): Training data labels.
        x_test (np.ndarray): Test data features.
        y_test (np.ndarray): Test data labels.
        experiment_name (str): The name of the MLflow experiment.
        regressor (sklearn model): The regressor to optimize.
        param_space (dict): The parameter space for Bayesian optimization.
        n_iter (int): Number of iterations for the search.

    """
    trainer = RegressorTrainer(
        experiment_name=experiment_name,
        regressor=regressor,
        param_space=param_space,
        n_iter=n_iter,
    )
    trainer.run(x_train, y_train, x_test, y_test)


def train_all_models():
    """
    Train all models using Bayesian optimization.

    This function is used to train the three models (DecisionTreeRegressor, XGBRegressor, and RandomForestRegressor)
    using Bayesian optimization.

    The training and test data are loaded from the "data/processed" directory.

    The hyperparameter search spaces for each model are loaded from "configs/hyperparameter_search_spaces.yaml".

    The trained models are logged to the MLflow server.

    """
    np.random.seed(RANDOM_SEED)

    project_root = os.path.dirname(os.path.dirname(__file__))
    processed_data_path = os.path.join(project_root, "data", "processed")

    x_train, y_train = (
        pd.read_csv(os.path.join(processed_data_path, "x_train.csv"), index_col=0),
        pd.read_csv(os.path.join(processed_data_path, "y_train.csv"), index_col=0),
    )
    x_test, y_test = (
        pd.read_csv(os.path.join(processed_data_path, "x_test.csv"), index_col=0),
        pd.read_csv(os.path.join(processed_data_path, "y_test.csv"), index_col=0),
    )

    configs_data_path = os.path.join(project_root, "configs")

    with open(
        os.path.join(configs_data_path, "hyperparameter_search_spaces.yaml"), "r"
    ) as stream:
        param_space_config = yaml.safe_load(stream)
        
    param_space_config["decision_tree"] = convert_param_space(param_space_config["decision_tree"])
    print(param_space_config["decision_tree"])
    param_space_config["xgboost"] = convert_param_space(param_space_config["xgboost"])
    param_space_config["random_forest"] = convert_param_space(param_space_config["random_forest"])

    run_bayesian_optimization(
        x_train,
        y_train,
        x_test,
        y_test,
        experiment_name="DecisionTree-BayesianOptimization",
        regressor=DecisionTreeRegressor(),
        param_space=param_space_config["decision_tree"],
        n_iter=1,
    )
    run_bayesian_optimization(
        x_train,
        y_train,
        x_test,
        y_test,
        experiment_name="XGBoost-BayesianOptimization",
        regressor=XGBRegressor(),
        param_space=param_space_config["xgboost"],
        n_iter=1,
    )
    run_bayesian_optimization(
        x_train,
        y_train,
        x_test,
        y_test,
        experiment_name="RandomForest-BayesianOptimization",
        regressor=RandomForestRegressor(),
        param_space=param_space_config["random_forest"],
        n_iter=1,
    )


if __name__ == "__main__":
    #train_all_models()
    RegressorTrainer.launch_mlflow_server()