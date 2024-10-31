import argparse
from prediction import PredictorModels
from model_development import convert_param_space, train_one_model
import joblib
import os
import pandas as pd
import sys
from typing import Dict, Tuple, Any
import yaml


def create_parser() -> argparse.ArgumentParser:
    """
    Parse command line arguments.
    It is quite nice to use command line arguments if you just want to plot or test a single algorithm
    without having to run all other algorithms.
    """
    parser = argparse.ArgumentParser(
        description="Retrain a model or predict. The retrain datasets need to be under data/retrain and the prediction dataset needs to be under data/inference."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--retrain", action="store_true", help="Re-train the model.")
    group.add_argument(
        "--predict", action="store_true", help="Predict using the trained model."
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


def load_data(
    x_train_path: str, y_train_path: str, x_test_path: str, y_test_path: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load the data from the given paths.
    """
    x_train = pd.read_csv(x_train_path)
    y_train = pd.read_csv(y_train_path)
    x_test = pd.read_csv(x_test_path)
    y_test = pd.read_csv(y_test_path)
    for df in [x_train, x_test, y_train, y_test]:
        if df.columns[0] == "date":
            df.set_index("date", inplace=True)
    return x_train, y_train, x_test, y_test


def normalize_data(normalizer, x_train, x_test) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Normalize the data using the given normalizer.
    """
    x_train = normalizer.transform(x_train)
    x_test = normalizer.transform(x_test)
    return x_train, x_test


def train_model(
    x_train: pd.DataFrame,
    y_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_test: pd.DataFrame,
    experiment_name: str,
    model: str,
    param_space: Dict[str, Any],
    n_iter: int,
) -> None:
    """
    Train a model using Bayesian optimization.
    """
    if model == "decision_tree":
        train_one_model(
            x_train,
            y_train,
            x_test,
            y_test,
            experiment_name=experiment_name,
            model="decision_tree",
            param_space=param_space,
            n_iter=n_iter,
        )
    if model == "xgboost":
        train_one_model(
            x_train,
            y_train,
            x_test,
            y_test,
            experiment_name=experiment_name,
            model="xgboost",
            param_space=param_space,
            n_iter=n_iter,
        )
    if model == "random_forest":
        train_one_model(
            x_train,
            y_train,
            x_test,
            y_test,
            experiment_name=experiment_name,
            model="random_forest",
            param_space=param_space,
            n_iter=n_iter,
        )


def main():
    parser = create_parser()
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(__file__))
    saved_models_path = os.path.join(project_root, "saved_models")
    normalizer = joblib.load(os.path.join(saved_models_path, "normalizer.joblib"))

    if args.retrain:
        x_train, y_train, x_test, y_test = load_data(
            args.x_train_path, args.y_train_path, args.x_test_path, args.y_test_path
        )
        x_train, x_test = normalize_data(normalizer, x_train, x_test)

        configs_data_path = os.path.join(project_root, "configs")
        with open(
            os.path.join(configs_data_path, "hyperparameter_search_spaces.yaml"), "r"
        ) as stream:
            param_space_config = yaml.safe_load(stream)

        param_space_config["decision_tree"] = convert_param_space(
            param_space_config["decision_tree"]
        )
        param_space_config["xgboost"] = convert_param_space(
            param_space_config["xgboost"]
        )
        param_space_config["random_forest"] = convert_param_space(
            param_space_config["random_forest"]
        )

        train_model(
            x_train,
            y_train,
            x_test,
            y_test,
            experiment_name=f"retrain_{args.model}",
            model=args.model,
            param_space=param_space_config[args.model],
            n_iter=args.n_iter,
        )

    if args.predict:
        inference_data_folder = os.path.join(project_root, "data", "inference")
        predict_dataset = pd.read_csv(
            os.path.join(inference_data_folder, args.prediction_dataset)
        )
        if predict_dataset.columns[0] == "date":
            predict_dataset.set_index("date", inplace=True)

        predictor = PredictorModels()
        model = args.model
        if model == "decision_tree":
            y_pred = predictor.decision_tree_predictions(predict_dataset)
        if model == "random_forest":
            y_pred = predictor.random_forest_predictions(predict_dataset)
        if model == "xgboost":
            y_pred = predictor.xgb_predictions(predict_dataset, normalized=True)

        print(pd.DataFrame(y_pred).head())


if __name__ == "__main__":
    main()
