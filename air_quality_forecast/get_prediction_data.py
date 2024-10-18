from prediction import PredictorModels
from api_caller import APICaller
import pandas as pd
import os
import sys


def main():
    project_root = os.path.dirname(os.path.dirname(__file__))
    parent_dir = os.path.dirname(project_root)
    sys.path.append(parent_dir)

    predictor = PredictorModels()

    project_root = os.path.dirname(os.path.dirname(__file__))
    parent_dir = os.path.dirname(project_root)
    sys.path.append(parent_dir)

    caller = APICaller()
    predictor = PredictorModels()
    current_data = caller.lag_data()
    df = pd.DataFrame(predictor.xgb_predictions(current_data))
    df.columns = ["NO2", "O3", "NO2 + day 1", "O3 + day 1", "NO2 + day 2", "O3 + day 2"]

    save_dir = os.path.join(project_root, "data", "inference")

    pd.DataFrame(current_data).to_csv(os.path.join(save_dir, "last_three_days.csv"))
    df.to_csv(os.path.join(save_dir, "current_prediction_data.csv"))


if __name__ == "__main__":
    main()
