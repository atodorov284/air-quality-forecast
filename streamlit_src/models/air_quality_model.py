import pandas as pd
import numpy as np

class AirQualityModel():
    def __init__(self) -> None:
        
        self.WHO_NO2_LEVEL = 25
        self.WHO_O3_LEVEL = 100
        pass
    
    def get_today_data(self):
        today_data = {
            "NO2 (µg/m³)": np.random.uniform(20, 60),  # Simulated data
            "O3 (µg/m³)": np.random.uniform(50, 120)   # Simulated data
        }
        return today_data

        # Function to retrieve predictions for the next three days (replace with actual model predictions)
    def next_three_day_predictions(self):
        next_three_days = pd.DataFrame({
            "Day": ["Day 1", "Day 2", "Day 3"],
            "NO2 (µg/m³)": np.random.uniform(20, 60, 3),
            "O3 (µg/m³)": np.random.uniform(50, 120, 3)
        })
        return next_three_days