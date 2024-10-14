import os
import sys
import pandas as pd
import joblib

project_root = os.path.dirname(__file__)
parent_dir = os.path.dirname(project_root)
sys.path.append(parent_dir)
from air_quality_forecast.prediction import PredictorModels

def predictions_xgb_from_datapath(data_path):
    updated_data_path = os.path.join(parent_dir, data_path) #"data", "inference", "x_test.csv"
    data = pd.read_csv(updated_data_path)
    return predictions_xgb_from_data(data)
    
def load_normalizer():
    saved_models_path = os.path.join(parent_dir, "saved_models")
    normalizer = joblib.load(os.path.join(saved_models_path, "normalizer.joblib"))
    return normalizer

def predictions_xgb_from_data(data, normalized=False):
    
    if data.columns[0] == "date":
        data.set_index("date", inplace=True)
        
    
    if not normalized:    normalizer = load_normalizer()
        data = normalizer.transform(data)
    
    predictor = Predic
        els()
    return predictor.xgb_predictions(data)


if __name__ == "__main__":
    print(predictions_xgb_from_datapath("data/inference/x_test.csv"))
