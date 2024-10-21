import pandas as pd
import os
from datetime import datetime, timedelta
from sklearn.metrics import root_mean_squared_error

PREDICTION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "model_predictions",
    "prediction_data.csv",
)

PAST_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "model_predictions",
    "last_three_days.csv",
)


class AirQualityModel:
    def __init__(self) -> None:
        self.WHO_NO2_LEVEL = 25
        self.WHO_O3_LEVEL = 100

    def get_today_data(self):
        """
        Returns the air quality data for today from the past 3 days data.

        The data is obtained from a CSV file located at PAST_DATA_PATH.

        Returns
        -------
        pd.Series
            A pandas Series with the air quality data for today.
        """
        last_three_days = self.get_last_three_days()
        today = last_three_days.iloc[0]
        return today

    def next_three_day_predictions(self):
        # Load data from the specified path (assuming it's a CSV file)
        data = pd.read_csv(PREDICTION_PATH)

        # correct data is todays data row
        data = data[data["date"] == pd.Timestamp.now().strftime("%Y-%m-%d")]

        # Create a DataFrame with the relevant information for the next three days
        next_three_days = pd.DataFrame(
            {
                "Day": ["Day 1", "Day 2", "Day 3"],
                "NO2 (µg/m³)": [
                    data["NO2 + day 1"].values[0],
                    data["NO2 + day 2"].values[0],
                    data["NO2 + day 3"].values[0],
                ],
                "O3 (µg/m³)": [
                    data["O3 + day 1"].values[0],
                    data["O3 + day 2"].values[0],
                    data["O3 + day 3"].values[0],
                ],
            }
        )

        return next_three_days

    def get_all_data_last_three_days(self):
        data = pd.read_csv(PAST_DATA_PATH)
        return data

    def get_last_three_days(self):
        # Extract NO2 and O3 values for the last three days
        data = pd.read_csv(PAST_DATA_PATH)
        last_three_days = pd.DataFrame(
            {
                "Day": ["Today", "Yesterday", "Day Before Yesterday"],
                "NO2 (µg/m³)": [
                    data["NO2 - day 0"].values[0],
                    data["NO2 - day 1"].values[0],
                    data["NO2 - day 2"].values[0],
                ],
                "O3 (µg/m³)": [
                    data["O3 - day 0"].values[0],
                    data["O3 - day 1"].values[0],
                    data["O3 - day 2"].values[0],
                ],
            }
        )
        return last_three_days

    def calculate_metrics(self):
        model_predictions = pd.read_csv(PREDICTION_PATH)

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

        yesterday_prediction = model_predictions[model_predictions["date"] == yesterday]
        two_days_ago_prediction = model_predictions[
            model_predictions["date"] == two_days_ago
        ]
        three_days_ago_prediction = model_predictions[
            model_predictions["date"] == three_days_ago
        ]

        current_data = pd.read_csv(PAST_DATA_PATH)

        current_data = current_data.filter(
            [
                "NO2 - day 0",
                "O3 - day 0",
                "NO2 - day 1",
                "O3 - day 1",
                "NO2 - day 2",
                "O3 - day 2",
            ]
        )

        today_ozone_prediction = pd.DataFrame(
            {
                "O3 Actual Value": current_data["O3 - day 0"].values[0],
                "Latest Model Prediction for O3": yesterday_prediction[
                    "O3 + day 1"
                ].values[0],
            },
            index=[yesterday],
        )
        today_nitrogen_dioxide_prediction = pd.DataFrame(
            {
                "NO2 Actual Value": current_data["NO2 - day 0"].values[0],
                "Latest Model Prediction for NO2": yesterday_prediction[
                    "NO2 + day 1"
                ].values[0],
            },
            index=[yesterday],
        )

        today_full_row = pd.concat(
            [today_ozone_prediction, today_nitrogen_dioxide_prediction], axis=1
        )

        yesterday_ozone_prediction = pd.DataFrame(
            {
                "O3 Actual Value": current_data["O3 - day 1"].values[0],
                "Latest Model Prediction for O3": two_days_ago_prediction[
                    "O3 + day 1"
                ].values[0],
            },
            index=[two_days_ago],
        )
        yesterday_nitrogen_dioxide_prediction = pd.DataFrame(
            {
                "NO2 Actual Value": current_data["NO2 - day 1"].values[0],
                "Latest Model Prediction for NO2": two_days_ago_prediction[
                    "NO2 + day 1"
                ].values[0],
            },
            index=[two_days_ago],
        )

        yesterday_full_row = pd.concat(
            [yesterday_ozone_prediction, yesterday_nitrogen_dioxide_prediction], axis=1
        )

        two_days_ago_ozone_prediction = pd.DataFrame(
            {
                "O3 Actual Value": current_data["O3 - day 2"].values[0],
                "Latest Model Prediction for O3": three_days_ago_prediction[
                    "O3 + day 1"
                ].values[0],
            },
            index=[three_days_ago],
        )
        two_days_ago_nitrogen_dioxide = pd.DataFrame(
            {
                "NO2 Actual Value": current_data["NO2 - day 2"].values[0],
                "Latest Model Prediction for NO2": three_days_ago_prediction[
                    "NO2 + day 1"
                ].values[0],
            },
            index=[three_days_ago],
        )

        two_days_ago_full_row = pd.concat(
            [two_days_ago_ozone_prediction, two_days_ago_nitrogen_dioxide], axis=1
        )

        full_metrics_last_three_days = pd.concat(
            [today_full_row, yesterday_full_row, two_days_ago_full_row], axis=0
        )

        full_metrics_last_three_days["O3 RMSE"] = full_metrics_last_three_days.apply(
            lambda row: root_mean_squared_error(
                [row["O3 Actual Value"]], [row["Latest Model Prediction for O3"]]
            ),
            axis=1,
        )
        full_metrics_last_three_days["NO2 RMSE"] = full_metrics_last_three_days.apply(
            lambda row: root_mean_squared_error(
                [row["NO2 Actual Value"]], [row["Latest Model Prediction for NO2"]]
            ),
            axis=1,
        )

        full_metrics_last_three_days = full_metrics_last_three_days.reindex(
            columns=[
                "O3 Actual Value",
                "Latest Model Prediction for O3",
                "O3 RMSE",
                "NO2 Actual Value",
                "Latest Model Prediction for NO2",
                "NO2 RMSE",
            ]
        )

        return full_metrics_last_three_days
