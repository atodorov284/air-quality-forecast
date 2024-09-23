# Air Quality Forecast

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

Air pollution is a significant environmental concern, especially in urban areas, where the high levels of nitrogen dioxide and ozone can have a negative impact on human health, the ecosystem and on the overall quality of life. Given these risks, monitoring and forecasting the level of air pollution is an important task in order to allow for timely actions to reduce the harmful effects. 

In the Netherlands, cities like Utrecht experience challenges concerning air quality due to urbanization, transportation, and industrial activities. Developing a system that can provide accurate and robust real-time air quality monitoring and reliable forecasts for future pollution levels would allow authorities and residents to take preventive measures and adjust their future activities based on expected air quality. This project focuses on the time-series forecasting of air pollution levels, specifically NO$_2$ and O$_3$ concentrations, for the next three days. This task can be framed as a regression problem, where the goal is to predict continuous values based on historical environmental data. Moreover, it provides infrastructure for real-time prediction, based on recent measurements.

## How To Run This Code

Currently, this repository is at the data engineering stage. To run the data pipeline, run main.py under air-quality-forecast, which contains the source code of this project. The processed and split datasets can be found under data/processed, namely x_train, x_val, x_test, y_train, y_val, y_test.

The notebooks in this project were used as scratch for analysis and data merge and do not reflect our thorough methodology (source is under air-quality-forecast). Some extra scripts for the generation of our plots in the report can be found under extra_scripts.

## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         air-quality-forecast and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── air-quality-forecast   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes air-quality-forecast a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations
```

--------

# air-quality-forecast
