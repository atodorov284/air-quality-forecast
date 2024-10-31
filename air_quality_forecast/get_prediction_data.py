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
    caller = APICaller()
    all_predictions = caller.lag_data()

    df = pd.DataFrame(predictor.xgb_predictions(all_predictions, normalized=False))
    df.columns = [
        "NO2 + day 1",
        "O3 + day 1",
        "NO2 + day 2",
        "O3 + day 2",
        "NO2 + day 3",
        "O3 + day 3",
    ]
    current_date = pd.Timestamp.today().strftime("%d-%m-%Y")
    df.index = pd.DatetimeIndex([current_date])

    save_dir = os.path.join(project_root, "data", "model_predictions")

    pd.DataFrame(all_predictions).to_csv(os.path.join(save_dir, "last_three_days.csv"))

    try:
        all_predictions = pd.read_csv(
            os.path.join(save_dir, "prediction_data.csv"),
            index_col="date",
            parse_dates=True,
        )
    except FileNotFoundError:
        all_predictions = pd.DataFrame(columns=df.columns, index=pd.DatetimeIndex([]))

    if current_date in all_predictions.index:
        all_predictions.loc[current_date] = df.loc[current_date]
    else:
        # Append the new row using pd.concat
        all_predictions = pd.concat([all_predictions, df])

    all_predictions.to_csv(
        os.path.join(save_dir, "prediction_data.csv"), index_label="date"
    )


if __name__ == "__main__":
    main()
