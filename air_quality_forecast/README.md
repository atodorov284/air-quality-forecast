# Air Quality Forecasting - Utrecht

This folder contains the core scripts for the **Air Quality Forecasting** project in Utrecht. The scripts here handle data collection, processing, model training, and prediction generation for air pollutants like NO₂ and O₃.

## 📂 Folder Structure

```plaintext
air_quality_forecast/
├── api_caller.py              # Manages API requests to retrieve air quality and meteorological data
├── data_pipeline.py           # Handles data preprocessing for model training and inference
├── get_prediction_data.py     # Prepares input data required for generating forecasts
├── main.py                    # Main entry point for executing the forecasting pipeline
├── model_development.py       # Contains model training, tuning, and evaluation scripts
├── parser_ui.py               # Manages retraining protocol and command-line arguments
├── prediction.py              # Generates forecasts using the trained model
├── utils.py                   # Utility functions for common tasks across scripts
└── README.md                  # Documentation for the `air_quality_forecast` folder
```
---
### 📊 Data Flow

Below is a simplified flow of data in the project:

1. **Data Collection**: `api_caller.py` → retrieves raw data.
2. **Data Preprocessing**: `data_pipeline.py` → cleans and transforms data.
3. **Model Training**: `model_development.py` → trains the forecasting model.
4. **Prediction**: `prediction.py` → generates forecasts using the trained model.
---
### 🔄 Retraining Protocol

The **`parser_ui.py`** script manages the **retraining protocol** and provides a flexible command-line interface to control model retraining and prediction generation. Key functionalities include:

- **Retraining Mode (`--retrain`)**: When the `--retrain` flag is used, the script:
  - Loads the training and testing datasets specified by the user via `--x_train_path`, `--y_train_path`, `--x_test_path`, and `--y_test_path` arguments.
  - Normalizes the data using a pre-trained normalizer to ensure consistency in input format.
  - Reads model-specific hyperparameter search spaces from a configuration file (`hyperparameter_search_spaces.yaml`), which are then converted to a format compatible with Bayesian optimization.
  - Trains the specified model (`decision_tree`, `xgboost`, or `random_forest`) with Bayesian optimization over the defined parameter space and saves the retrained model for future predictions.

- **Prediction Mode (`--predict`)**: When the `--predict` flag is used, the script:
  - Loads the dataset for inference from the path specified by `--prediction_dataset`.
  - Uses the specified model (`decision_tree`, `xgboost`, or `random_forest`) to generate predictions on the new data.
  - Prints the prediction results, providing a quick way to evaluate the model’s forecast.

These modes allow users to seamlessly switch between retraining and prediction tasks, making it easy to keep the model updated and generate new forecasts as required.

### 💻 Example Usage of the Retraining Protocol

Below are example commands for using the **retraining** and **prediction** functionalities in `parser_ui.py`.

#### Retraining the Model

To retrain a model (e.g., `xgboost`) with a specified dataset:

```bash
python main.py --retrain x_train_path y_train_path x_test_path y_test_path n_iter --model xgboost
```
By specifying the paths to the data in the placeholders.

To generate predictions with a trained model (e.g., `xgboost`) on a new dataset:
```bash
python main.py --predict prediction_path --model xgboost
```
