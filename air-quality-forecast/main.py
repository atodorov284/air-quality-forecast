from prediction import PredictorModels
from sklearn.metrics import mean_squared_error, root_mean_squared_error
import pandas as pd
import os
import sys


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(__file__))
    parent_dir = os.path.dirname(project_root)
    sys.path.append(parent_dir)

    predictor = PredictorModels()

    x_train = pd.read_csv("data/processed/x_train.csv", index_col=0)
    y_train = pd.read_csv("data/processed/y_train.csv", index_col=0)

    y_test_pred_dtree = predictor.decision_tree_predictions(x_train)
    y_test_pred_rf = predictor.random_forest_predictions(x_train)
    y_test_pred_xgb = predictor.xgb_predictions(x_train)

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
    y_test_pred_xgb = predictor.xgb_predictions(x_test)

    print("Test Decision Tree MSE: ", mean_squared_error(y_test, y_test_pred_dtree))
    print("Test Random Forest MSE: ", mean_squared_error(y_test, y_test_pred_rf))
    print("Test XGBoost MSE: ", mean_squared_error(y_test, y_test_pred_xgb))

    print(
        "Test Decision Tree RMSE: ", root_mean_squared_error(y_test, y_test_pred_dtree)
    )
    print("Test Random Forest RMSE: ", root_mean_squared_error(y_test, y_test_pred_rf))
    print("Test XGBoost RMSE: ", root_mean_squared_error(y_test, y_test_pred_xgb))
