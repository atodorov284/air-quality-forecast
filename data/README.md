# Data Directory

The `data` folder organizes all datasets used in the **Air Quality Forecasting** project. It includes raw data, processed data ready for model training, inference datasets, and model predictions, ensuring a clear workflow from data collection to model evaluation.

---

## 📂 Data Folder Structure

```plaintext
data/
├── inference/             # The folder, in which data needs to be stored to use the parser's functionality for custom predictions.
├── model_predictions/     # Stores model output predictions for evaluation and analysis. This folder is updated by the automated workflows every 6 hours.
├── other/                 # Contains miscellaneous data files such as the feature importance values.
├── processed/             # Preprocessed datasets ready for model training and testing.
└── raw/                   # Raw, unprocessed datasets collected from the World Air Quality Index and Visual Crossing.
