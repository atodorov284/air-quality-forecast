---
title: Air Quality Forecasting
emoji: 📈
colorFrom: yellow
colorTo: gray
sdk: streamlit
sdk_version: 1.39.0
app_file: streamlit_src/app.py
pinned: false
---
# Air Quality Forecast

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Air pollution is a significant environmental concern, especially in urban areas, where the high levels of nitrogen dioxide and ozone can have a negative impact on human health, the ecosystem and on the overall quality of life. Given these risks, monitoring and forecasting the level of air pollution is an important task in order to allow for timely actions to reduce the harmful effects. 

In the Netherlands, cities like Utrecht experience challenges concerning air quality due to urbanization, transportation, and industrial activities. Developing a system that can provide accurate and robust real-time air quality monitoring and reliable forecasts for future pollution levels would allow authorities and residents to take preventive measures and adjust their future activities based on expected air quality. This project focuses on the time-series forecasting of air pollution levels, specifically NO<sub>2</sub> and O<sub>3</sub> concentrations, for the next three days. This task can be framed as a regression problem, where the goal is to predict continuous values based on historical environmental data. Moreover, it provides infrastructure for real-time prediction, based on recent measurements.

---
## Streamlit Application

Explore the interactive air quality forecast for Utrecht through our Streamlit app on Hugging Face Spaces:

[Air Quality Forecasting App](https://huggingface.co/spaces/03chrisk/air-quality-forecasting)

---

## 🚀 How to Run the Scripts

### Setting Up

**Clone the Repository**: Start by cloning the repository to your local machine.
   ```bash
   git clone https://github.com/atodorov284/air-quality-forecast.git
   cd air-quality-forecast
   ```
**Set Up Environment**:
   Make sure all dependencies are installed by running the following `requirements.txt` file from the repository root:
   ```bash
   pip install -r requirements.txt
   ```
### Running Source Code
First, navigate to the `air-quality-forecast` folder, which contains the source code for the project:

```bash
cd air-quality-forecast
```

**Running the Data Pipeline**: 
Execute `data_pipeline.py` within the `air-quality-forecast` folder, which contains the source code for this project. This script will preprocess the data and store the processed datasets in `data/processed`, with files named `x_train`, `x_test`, `y_train`, and `y_test`.

   ```bash
   python data_pipeline.py
   ```

**View the MLFlow Dashboard**: 
To track experiments, run `model_development.py`, which will start an MLFlow server on `localhost` at port `5000`.

```bash
python model_development.py
```
> [!TIP]
> If the server does not start automatically, manually run the MLFlow UI using:
> ```bash
> mlflow ui --port 5000
>  ```

> [!NOTE]
> You might need to grant admin permissions for this process
---
**Using the parser to retrain the model or make predictions on new data**
To retrain a model or predict, run `main.py` with the following arguments:
positional arguments:
  {xgboost,decision_tree,random_forest}
                        Model to retrain or predict.

options:
  -h, --help            show this help message and exit
  --retrain             Re-train the model.
  --predict             Predict using the trained model.


**IMPORTANT**
The retrain datasets need to be under data/retrain and the prediction dataset needs to be under data/inference.

If --retrain is selected, specify the dataset name, which has to be under data/inference. For example, if the dataset is named x_test.csv and you want to predict using the xgboost model, run:
`main.py --predict --prediction_dataset x_test.csv xgboost`

Similarly, to retrain xgboost for example, run:
`main.py --retrain --x_train x_train.csv --x_test x_test.csv --y_train y_train.csv --y_test y_test.csv --n_iter 50 xgboost`


> [!IMPORTANT]
> The notebooks in this project were used as scratch for analysis and data merge and do not reflect our thorough methodology (source is under air-quality-forecast). Some extra scripts for the generation of our plots in the report can be found under extra_scripts.

---
## 📂 Project Folder Structure

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── processed      <- The final, canonical data sets for modeling. Contains the train-test split.
│   └── raw            <- The original, immutable data dump.
│
├──.github             <- Contains automated workflows for reproducibility, flake8 checks and scheduled updates. 
│
├── docs               <- Contains files to make the HTML documentation for this project usign Sphinx
│
├───mlruns             <- Contains all the experiments ran using mlflow.
│
├───mlartifacts        <- Contains the artifacts generated by mlflow experiments.
│
├── notebooks          <- Jupyter notebooks (not to be evaluated, source code is in air-quality-forecast)
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         air-quality-forecast and configuration for tools like black
│
├── references         <- TODO: Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- TODO: Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- TODO: Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
├── configs            <- Configuration folder for the hyperparameter search space (for now)
│
├── saved_models       <- Folder with the saved models in `.pkl` and `.xgb`.
│
├── extra_scripts      <- Some extra scripts in R and .tex to generate figures
│
└── air-quality-forecast   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes air-quality-forecast a Python module
    │
    ├── data_pipeline.py        <- Loads, extracts, and preprocesses the data. Final result is the train-test under data/processed
    │
    ├── model_development.py    <- Trains the three models using k-fold CV and Bayesian hyperparameter tuning, displays the ML dashboard if executed
    │
    ├── prediction.py           <- Loads the models and makes an example prediction
    │
    ├── utils.py                <- Utility functions, e.g. validation
    │
    └── main.py                 <- To execute and start the project. Currently to make predictions.
```
---

