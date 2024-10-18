import pandas as pd
import numpy as np
import os

PREDICTION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "inference",
    "current_prediction_data.csv",
)

PAST_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "inference",
    "last_three_days.csv",
)


class AirQualityModel:
    def __init__(self) -> None:
        self.WHO_NO2_LEVEL = 25
        self.WHO_O3_LEVEL = 100

    def get_today_data_fake(self):
        today_data = {
            "NO2 (µg/m³)": np.random.uniform(20, 60),  # Simulated data
            "O3 (µg/m³)": np.random.uniform(50, 120),  # Simulated data
        }
        return today_data

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
        today = last_three_days.iloc[1]
        return today

    def next_three_day_predictions(self):
        # Load data from the specified path (assuming it's a CSV file)
        data = pd.read_csv(PREDICTION_PATH)

        # Create a DataFrame with the relevant information for the next three days
        next_three_days = pd.DataFrame(
            {
                "Day": ["Day 1", "Day 2", "Day 3"],
                "NO2 (µg/m³)": [
                    data["NO2"].values[0],
                    data["NO2 + day 1"].values[0],
                    data["NO2 + day 2"].values[0],
                ],
                "O3 (µg/m³)": [
                    data["O3"].values[0],
                    data["O3 + day 1"].values[0],
                    data["O3 + day 2"].values[0],
                ],
            }
        )

        return next_three_days

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
        pass
