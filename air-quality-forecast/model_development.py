import mlflow
import mlflow.sklearn
import subprocess
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import mean_squared_error, root_mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from skopt import BayesSearchCV
from typing import Dict, Any
import socket
import pandas as pd
import warnings
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
import yaml
import os
import sys

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

    def _port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # This actually returns an int and not a bool
            return s.connect_ex(("localhost", port)) == 0

    def _launch_mlflow_server(self) -> None:
        port = 5000
        if not self._port_in_use(port):
            try:
                subprocess.Popen(
                    ["py", "-m", "mlflow", "ui", "--port", str(port)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                print(f"MLflow server launched at http://127.0.0.1:{port}")
            except Exception as e:
                print("Error launching MLflow server:", e)
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
        """Set up MLflow configuration."""
        self._launch_mlflow_server()
        mlflow.set_experiment(self._experiment_name)
        mlflow.set_tracking_uri("http://localhost:5000/")
        mlflow.enable_system_metrics_logging()
        mlflow.autolog()

    def _perform_search(self) -> None:
        """Perform Bayesian optimization for hyperparameters."""
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

    def _evaluate_model(self) -> None:
        """Evaluate the best model on the test data and log metrics."""
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

        print(
            "Best hyperparameters found by Bayesian optimization:",
            self._bayes_search.best_params_,
        )
        print("Test MSE: ", test_mse)
        print("Test RMSE: ", test_rmse)

    def run(
        self,
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_test: np.ndarray,
        y_test: np.ndarray,
    ) -> None:
        self._set_data(x_train, y_train, x_test, y_test)
        self._setup_mlflow()
        self._perform_search()
        self._evaluate_model()


def set_path() -> None:
    """
    Set the path to include the parent directory of the current file.

    This is needed to import modules from the parent directory.

    Parameters:
        None

    Returns:
        None
    """
    currentdir = os.path.dirname(os.path.realpath(__file__))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, parentdir)


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
    set_path()

    np.random.seed(RANDOM_SEED)

    x_train, y_train = (
        pd.read_csv("data/processed/x_train.csv", index_col=0),
        pd.read_csv("data/processed/y_train.csv", index_col=0),
    )
    x_test, y_test = (
        pd.read_csv("data/processed/x_test.csv", index_col=0),
        pd.read_csv("data/processed/y_test.csv", index_col=0),
    )

    with open("configs/hyperparameter_search_spaces.yaml", "r") as stream:
        param_space_config = yaml.safe_load(stream)

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
    train_all_models()
