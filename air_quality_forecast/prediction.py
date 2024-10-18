import os
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import root_mean_squared_error, mean_squared_error
import pickle
import xgboost
import joblib


class PredictorModels:
    def __init__(self) -> None:
        """
        Initializes the predictor models by loading the pre-trained models from the saved_models directory.

        The models are loaded in the following order:
        1. XGBoost
        2. Decision Tree
        3. Random Forest
        """
        self._xgboost: xgboost.Booster = xgboost.Booster()
        self._d_tree: BaseEstimator = None
        self._random_forest: BaseEstimator = None
        self._load_models()

    def _load_models(self) -> None:
        """
        Loads the pre-trained models from the saved_models directory.

        The models are loaded in the following order:

        1. Decision Tree Regressor
        2. Random Forest Regressor
        3. XGBoost Regressor

        The models are loaded from the following paths:

        - Decision Tree Regressor: saved_models/decision_tree.pkl
        - Random Forest Regressor: saved_models/random_forest.pkl
        - XGBoost Regressor: saved_models/xgboost.xgb
        """

        project_root = os.path.dirname(os.path.dirname(__file__))
        models_path = os.path.join(project_root, "saved_models")

        self._d_tree = pickle.load(
            open(os.path.join(models_path, "decision_tree.pkl"), "rb")
        )
        self._random_forest = pickle.load(
            open(os.path.join(models_path, "random_forest.pkl"), "rb")
        )
        self._xgboost.load_model(os.path.join(models_path, "xgboost.xgb"))

    def xgb_predictions(self, x_test: pd.DataFrame, normalized: bool) -> np.ndarray:
        """
        Makes predictions using the loaded XGBoost regressor.

        Parameters
        ----------
        x_test : pd.DataFrame
            Data points to make predictions on.

        normalized : bool
            Whether the data is normalized or not.

        Returns
        -------
        y_pred : np.ndarray
            Predicted values for the input data points.
        """
        if x_test is None:
            raise ValueError("x_test is None")
        if x_test.ndim != 2:
            raise ValueError("x_test must be 2 dimensional, got {}".format(x_test.ndim))

        x_test.columns = [
            "pm25 - day 1",
            "pm10 - day 1",
            "o3 - day 1",
            "no2 - day 1",
            "temp - day 1",
            "humidity - day 1",
            "visibility - day 1",
            "solarradiation - day 1",
            "precip - day 1",
            "windspeed - day 1",
            "winddir - day 1",
            "pm25 - day 2",
            "pm10 - day 2",
            "o3 - day 2",
            "no2 - day 2",
            "temp - day 2",
            "humidity - day 2",
            "visibility - day 2",
            "solarradiation - day 2",
            "precip - day 2",
            "windspeed - day 2",
            "winddir - day 2",
            "pm25 - day 3",
            "pm10 - day 3",
            "o3 - day 3",
            "no2 - day 3",
            "temp - day 3",
            "humidity - day 3",
            "visibility - day 3",
            "solarradiation - day 3",
            "precip - day 3",
            "windspeed - day 3",
            "winddir - day 3",
        ]
        if not normalized:
            project_root = os.path.dirname(os.path.dirname(__file__))
            saved_models_path = os.path.join(project_root, "saved_models")
            normalizer = joblib.load(
                os.path.join(saved_models_path, "normalizer.joblib")
            )
            x_test = normalizer.transform(x_test)

        xgb_test = xgboost.DMatrix(x_test)
        y_pred = self._xgboost.predict(xgb_test)
        return y_pred

    def random_forest_predictions(self, x_test: pd.DataFrame) -> np.ndarray:
        """
        Makes predictions using the loaded Random Forest regressor.

        Parameters
        ----------
        x_test : pd.DataFrame
            Data points to make predictions on.

        Returns
        -------
        y_pred : np.ndarray
            Predicted values for the input data points.
        """
        if x_test is None:
            raise ValueError("x_test is None")
        if x_test.ndim != 2:
            raise ValueError("x_test must be 2 dimensional, got {}".format(x_test.ndim))
        y_pred = self._random_forest.predict(x_test)
        return y_pred

    def decision_tree_predictions(self, x_test: pd.DataFrame) -> np.ndarray:
        """
        Makes predictions using the loaded decision tree regressor.

        Parameters
        ----------
        x_test : pd.DataFrame
            Input data to make predictions on.

        Returns
        -------
        y_pred : np.ndarray
            Predicted values.
        """
        if x_test is None:
            raise ValueError("x_test is None")
        if x_test.ndim != 2:
            raise ValueError("x_test must be 2 dimensional, got {}".format(x_test.ndim))
        y_pred = self._d_tree.predict(x_test)
        return y_pred


if __name__ == "__main__":
    predictor = PredictorModels()

    x_train = pd.read_csv("data/processed/x_train.csv", index_col=0)
    y_train = pd.read_csv("data/processed/y_train.csv", index_col=0)

    y_test_pred_dtree = predictor.decision_tree_predictions(x_train)
    y_test_pred_rf = predictor.random_forest_predictions(x_train)
    y_test_pred_xgb = predictor.xgb_predictions(x_train, normalized=True)

    print("Train Decision Tree MSE: ", mean_squared_error(y_train, y_test_pred_dtree))
    print("Train Random Forest MSE: ", mean_squared_error(y_train, y_test_pred_rf))
    print("Train XGBoost MSE: ", mean_squared_error(y_train, y_test_pred_xgb))

    print(
        "Train Decision Tree RMSE: ",
        root_mean_squared_error(y_train, y_test_pred_dtree),
    )
    print(
        "Train Random Forest RMSE: ", root_mean_squared_error(y_train, y_test_pred_rf)
    )
    print("Train XGBoost RMSE: ", root_mean_squared_error(y_train, y_test_pred_xgb))

    x_test = pd.read_csv("data/processed/x_test.csv", index_col=0)
    y_test = pd.read_csv("data/processed/y_test.csv", index_col=0)

    y_test_pred_dtree = predictor.decision_tree_predictions(x_test)
    y_test_pred_rf = predictor.random_forest_predictions(x_test)
    y_test_pred_xgb = predictor.xgb_predictions(x_test, normalized=True)

    print("Test Decision Tree MSE: ", mean_squared_error(y_test, y_test_pred_dtree))
    print("Test Random Forest MSE: ", mean_squared_error(y_test, y_test_pred_rf))
    print("Test XGBoost MSE: ", mean_squared_error(y_test, y_test_pred_xgb))

    print(
        "Test Decision Tree RMSE: ", root_mean_squared_error(y_test, y_test_pred_dtree)
    )
    print("Test Random Forest RMSE: ", root_mean_squared_error(y_test, y_test_pred_rf))
    print("Test XGBoost RMSE: ", root_mean_squared_error(y_test, y_test_pred_xgb))
