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
    """
    A class that loads the air quality model and makes predictions.

    The model is loaded from a pickle file located at PREDICTION_PATH.

    Attributes
    ----------
    _WHO_NO2_LEVEL : int
        The WHO air quality level for NO2 in micrograms per cubic meter.
    _WHO_O3_LEVEL : int
        The WHO air quality level for O3 in micrograms per cubic meter.
    """

    def __init__(self) -> None:
        self._WHO_NO2_LEVEL = 25
        self._WHO_O3_LEVEL = 100

    @property
    def WHO_NO2_LEVEL(self):
        return self._WHO_NO2_LEVEL

    @property
    def WHO_O3_LEVEL(self):
        return self._WHO_O3_LEVEL

    def get_today_data(self) -> pd.Series:
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

    def next_three_day_predictions(self) -> pd.DataFrame:
        """
        Returns the predictions for the next three days.
        """
        data = pd.read_csv(PREDICTION_PATH)

        filtered = data[data["date"] == datetime.today().strftime("%Y-%d-%m")]

        if len(filtered) == 0:
            filtered = data[data["date"] == datetime.today().strftime("%Y-%m-%d")]

        data = filtered

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

    def get_all_data_last_three_days(self) -> pd.DataFrame:
        """
        Returns all the air quality data for the last three days from the past 3 days data.

        The data is obtained from a CSV file located at PAST_DATA_PATH.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame with the air quality data for the last three days.
        """
        data = pd.read_csv(PAST_DATA_PATH)
        return data

    def get_last_three_days(self) -> pd.DataFrame:
        """
        Returns all the air quality data for the last three days from the past 3 days data.

        The data is obtained from a CSV file located at PAST_DATA_PATH.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame with the air quality data for the last three days.
        """
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

    def calculate_metrics(self) -> pd.DataFrame:
        """
        Calculates the root mean squared error for the predictions of the last three days.

        The data is obtained from a CSV file located at PREDICTION_PATH.

        Returns
        -------
        pd.DataFrame
            A pandas DataFrame with the root mean squared error for the predictions of the last three days.
        """
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
