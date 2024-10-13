import argparse
from prediction import PredictorModels
from model_development import (
    run_bayesian_optimization,
    convert_param_space,
    train_one_model,
)
import joblib
import os
import pandas as pd
import sys
import yaml


def create_parser() -> argparse.ArgumentParser:
    """
    Parse command line arguments.
    It is quite nice to use command line arguments if you just want to plot or test a single algorithm
    without having to run all other algorithms.
    """
    parser = argparse.ArgumentParser(description="Retrain a model or predict.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--retrain", type=bool, default=False, help="Re-train the model."
    )
    group.add_argument(
        "--predict", type=bool, default=False, help="Predict using the trained model."
    )
    if "--retrain" in sys.argv:
        parser.add_argument(
            "--x_train_path", type=str, help="Path to the x_train dataset CSV file."
        )
        parser.add_argument(
            "--y_train_path", type=str, help="Path to the y_train dataset CSV file."
        )
        parser.add_argument(
            "--x_test_path", type=str, help="Path to the x_test dataset CSV file."
        )
        parser.add_argument(
            "--y_test_path", type=str, help="Path to the y_test dataset CSV file."
        )
        parser.add_argument(
            "--n_iter",
            type=int,
            default=50,
            help="Number of iterations for the search.",
        )
    elif "--predict" in sys.argv:
        parser.add_argument(
            "--prediction_dataset", type=str, help="Path to the prediction dataset."
        )
    parser.add_argument(
        "model",
        type=str,
        choices=["xgboost", "decision_tree", "random_forest"],
        help="Model to retrain or predict.",
    )
    return parser


def main():
    parser = create_parser()

    project_root = os.path.dirname(os.path.dirname(__file__))
    saved_models_path = os.path.join(project_root, "saved_models")
    normalizer = joblib.load(os.path.join(saved_models_path, "normalizer.joblib"))
    args = parser.parse_args()

    retrain_data_folder = os.path.join(project_root, "data", "retrain")
    x_train = pd.read_csv(os.path.join(retrain_data_folder, args.x_train_path))
    x_test = pd.read_csv(os.path.join(retrain_data_folder, args.x_test_path))
    y_train = pd.read_csv(os.path.join(retrain_data_folder, args.y_train_path))
    y_test = pd.read_csv(os.path.join(retrain_data_folder, args.y_test_path))

    x_train = normalizer.transform(x_train)
    x_test = normalizer.transform(x_test)

    predictor = PredictorModels()

    configs_data_path = os.path.join(project_root, "configs")
    with open(
        os.path.join(configs_data_path, "hyperparameter_search_spaces.yaml"), "r"
    ) as stream:
        param_space_config = yaml.safe_load(stream)

    param_space_config["decision_tree"] = convert_param_space(
        param_space_config["decision_tree"]
    )
    param_space_config["xgboost"] = convert_param_space(param_space_config["xgboost"])
    param_space_config["random_forest"] = convert_param_space(
        param_space_config["random_forest"]
    )

    model = args.models

    if args.retrain:
        if args.model == "decision_tree":
            train_one_model(
                x_train,
                y_train,
                x_test,
                y_test,
                experiment_name=f"retrain_{model}",
                model="decision_tree",
                param_space=param_space_config["decision_tree"],
                n_iter=args.n_iter,
            )
        if args.model == "xgboost":
            train_one_model(
                x_train,
                y_train,
                x_test,
                y_test,
                experiment_name=f"retrain_{model}",
                model="xgboost",
                param_space=param_space_config["xgboost"],
                n_iter=args.n_iter,
            )
        if args.model == "random_forest":
            train_one_model(
                x_train,
                y_train,
                x_test,
                y_test,
                experiment_name=f"retrain_{model}",
                model="random_forest",
                param_space=param_space_config["random_forest"],
                n_iter=args.n_iter,
            )
            
    if args.predict:
        if args.decision_tree:
            predictor.decision_tree_predictions(x_train)
        if args.random_forest:
            predictor.random_forest_predictions(x_train)
        if args.xgboost:
            predictor.xgb_predictions(x_train)
