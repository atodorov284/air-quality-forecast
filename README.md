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

## 🚀 How to Run the App

To launch the Utrecht Air Quality Monitoring application on a localhost, follow these simple steps:

1. **Navigate to the `streamlit_src` folder** in your terminal where the app files are located.

2. **Run the Streamlit application** by entering the following command:
   ```bash
   streamlit run app.py
> [!TIP]
> **Alternative Path**: If you are not in the `streamlit_src` folder, provide the full path to `app.py`. For example, from the root directory:
> - **Windows**:
>   ```bash
>   streamlit run .\streamlit_src\app.py
>   ```
> - **macOS/Linux**:
>   ```bash
>   streamlit run ./streamlit_src/app.py
>   ```


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
cd air_quality_forecast
```
**📊 View the MLFlow Dashboard**:
To track experiments, run `model_development.py`, which will start an MLFlow server on `localhost` at port `5000`.

```bash
python model_development.py
```
> [!TIP]
> If the server does not start automatically, manually run the MLFlow UI using:
> ```bash
> mlflow ui --port 5000
>  ```
> You might need to grant admin permissions for this process

**🔄 Using the parser to retrain the model or make predictions on new data**:
Instructions on how to use the retraining protocol or making predictions on new data can be found in the `README.md` in the `air-quality-forecast` directory

> [!NOTE]
>The retrain datasets need to be under data/retrain and the prediction dataset needs to be under data/inference.
---
> [!IMPORTANT]
> The notebooks in this project were used as scratch for analysis and data merge and do not reflect our thorough methodology (source is under air-quality-forecast). Some extra scripts for the generation of our plots in the report can be found under extra_scripts.
---
## 📖 Viewing the Documentation

The project documentation is generated using Sphinx and can be viewed as HTML files. To access the documentation:

1. Navigate to the `_build/html/` directory inside the `docs` folder:
```bash
cd docs\_build\html\
```
2. Open the `index.html` file in your web browser. You can do this by double-clicking the file in your file explorer or using the following command:
```bash
open index.html  # macOS
xdg-open index.html  # Linux
start index.html  # Windows
```
3. Alternatively you can navigate to the `index.html` file through the file explorer and double click it to run it
---
## 📂 Project Folder Structure

```plaintext
├── LICENSE               <- Open-source MIT license
├── Makefile              <- Makefile with convenience commands like `make data` or `make train`
├── README.md             <- The top-level README for developers using this project.
├── data                  <- Folder containing data used for training, testing, and inference
│   ├── inference         <- Data for inference predictions
│   ├── model_predictions <- Folder containing model-generated predictions
│   ├── other             <- Additional data or miscellaneous files
│   ├── processed         <- The final, canonical data sets for modeling. Contains the train-test split.
│   └── raw               <- The original, immutable data dump.
│
├── .github               <- Contains automated workflows for reproducibility, flake8 checks, and scheduled updates.
│
├── docs                  <- Contains files to make the HTML documentation for this project using Sphinx
│
├── mlruns                <- Contains all the experiments ran using mlflow.
│
├── mlartifacts           <- Contains the artifacts generated by mlflow experiments.
│
├── notebooks             <- Scratch Jupyter notebooks (not to be evaluated, source code is in air-quality-forecast)
│
├── pyproject.toml        <- Project configuration file with package metadata for
│                            air-quality-forecast and configuration for tools like black
│
├── reports               <- Generated analysis as HTML, PDF, LaTeX, etc.
│
├── requirements.txt      <- The requirements file for reproducing the analysis environment, e.g.
│                            generated with `pip freeze > requirements.txt`
│
├── setup.cfg             <- Configuration file for flake8
│
├── configs               <- Configuration folder for the hyperparameter search space (for now)
│
├── saved_models          <- Folder with the saved models in `.pkl` and `.xgb`.
│
├── extra_scripts         <- Some extra scripts in R and .tex to generate figures
│
├── streamlit_src         <- Streamlit application source code
│   ├── controllers       <- Handles application logic and data flow for different app sections
│   ├── json_interactions <- Manages JSON data interactions for configuration and storage
│   ├── models            <- Contains model loading, preprocessing, and prediction logic
│   └── views             <- Manages the UI components for different app sections
│
└── air_quality_forecast  <- Source code used in this project.
    │
    ├── api_caller.py             <- Manages API requests to retrieve air quality and meteorological data
    ├── data_pipeline.py          <- Loads, extracts, and preprocesses the data. Final result is the train-test under data/processed
    ├── get_prediction_data.py    <- Prepares input data required for generating forecasts
    ├── main.py                   <- Main entry point for executing the forecasting pipeline
    ├── model_development.py      <- Trains the models using k-fold CV and Bayesian hyperparameter tuning
    ├── parser_ui.py              <- Manages configuration settings and command-line arguments
    ├── prediction.py             <- Generates forecasts using the trained model
    └── utils.py                  <- Utility functions for common tasks across scripts
```
---
