import os
import sys
from prediction import PredictorModels
import pandas as pd
import shap
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    x_test = pd.read_csv("data/processed/x_test.csv", index_col=0)
    y_test = pd.read_csv("data/processed/y_test.csv", index_col=0)

    predictor = PredictorModels()

    xgb_model = predictor._xgboost
    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer.shap_values(x_test)

    # Sum over the output dimension (axis=2) to get overall feature importance
    shap_values_sum = shap_values.sum(axis=2)

    # Compute the mean absolute SHAP values for each feature
    shap_importance = pd.DataFrame(
        {"feature": x_test.columns, "importance": np.abs(shap_values_sum).mean(axis=0)}
    ).sort_values(by="importance", ascending=False)

    # shap_importance.to_csv("shap_importance.csv", index=False)

    # PLOTTING
    plt.figure(figsize=(10, 6))
    bars = plt.barh(
        shap_importance["feature"], shap_importance["importance"], color="skyblue"
    )

    # Add text labels to the bars
    for bar in bars:
        plt.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.4f}",
            va="center",
        )

    plt.xlabel("Mean |SHAP value| (Feature Importance)")
    plt.ylabel("Feature")
    plt.title("Overall Feature Importance based on SHAP values")
    plt.gca().invert_yaxis()

    # Save the bar plot to shap_data folder in the data folder
    # plt.savefig("shap_data/shap_feature_importance.png", format='png', dpi=300, bbox_inches='tight')

    # OTHER PLOTS
    """output_features = ['NO2 - Day 1', 'O3 - Day 1', 'NO2 - Day 2', 'O3 - Day 2', 'NO2 - Day 3', 'O3 - Day 3']

    shap_values = explainer.shap_values(x_test)
    n_outputs = shap_values.shape[2] 
    
    
    for i in range(n_outputs):
        print(f"Generating summary plot for {output_features[i]}")
        plt.figure(figsize=(33, 16))
        
        shap.summary_plot(shap_values[:, :, i], x_test, plot_type="dot", show=False)
        
        plt.title(f"SHAP Summary Plot for {output_features[i]}")
        
        plt.savefig(f"shap_summary_plot_{output_features[i].replace(' ', '_').replace('-', '')}.png", format='png', dpi=300, bbox_inches='tight')
    
        plt.close()
"""
