import pandas as pd
import numpy as np
import os

PREDICTION_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "inference",
    "current_prediction_data.csv",
)


class AirQualityModel:
    def __init__(self) -> None:
        self.WHO_NO2_LEVEL = 25
        self.WHO_O3_LEVEL = 100

    def get_today_data(self):
        today_data = {
            "NO2 (µg/m³)": np.random.uniform(20, 60),  # Simulated data
            "O3 (µg/m³)": np.random.uniform(50, 120),  # Simulated data
        }
        return today_data

    def get_next_three_day_predictions_fake(self):
        """
        Get predictions for the next three days using the api data from the path"""

        next_three_days = pd.read_csv(
            os.path.join(PREDICTION_PATH, "current_prediction_data.csv")
        )

        next_three_days = pd.DataFrame(
            {
                "Day": ["Day 1", "Day 2", "Day 3"],
            }
        )

        return next_three_days

    def next_three_day_predictions(self):
        # Load data from the specified path (assuming it's a CSV file)
        data = pd.read_csv(PREDICTION_PATH)

        # Create a DataFrame with the relevant information for the next three days
        next_three_days = pd.DataFrame(
            {
                "Day": ["Day 1", "Day 2", "Day 3"],
                "NO2 (µg/m³)": [
                    data["NO2 + day 1"].values[0],
                    data["NO2 + day 2"].values[0],
                    data["NO2"].values[0],
                ],
                "O3 (µg/m³)": [
                    data["O3 + day 1"].values[0],
                    data["O3 + day 2"].values[0],
                    data["O3"].values[0],
                ],
            }
        )

        return next_three_days
