.. Air Quality Forecast documentation master file, created by
   sphinx-quickstart on Wed Oct 23 23:02:06 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Air Quality Forecast documentation
==================================

Problem Statement
-----------------
The objective of this project is to develop an air quality forecasting system that predicts future air quality levels based on historical environmental data. The system is required to provide accurate predictions and offer a user-friendly interface for interaction. The solution consists of a backend for data processing and machine learning, and a frontend built with Streamlit for displaying results.

Project Structure
-----------------

Codebase
~~~~~~~~
The code is organized into two main directories:

- `streamlit_src/`: Contains the Streamlit views for the web interface.
- `air_quality_forecast/`: Contains the backend logic for data pipeline, prediction models, and utility functions.

Directory Breakdown
~~~~~~~~~~~~~~~~~~~

1. ``streamlit_src/``
   This directory handles the user interface and interactions via Streamlit.
   It uses the Model-View-Controller (MVC) design pattern for separation of logic.

   - `controllers/`: Contains logic for handling JSON interactions.
   - `models/`: Placeholder directory for any future model handling within the frontend.
   - `views/`: Contains the view files for the web interface, organized as per different user views.

   **Files in `views/`:**

   - `admin_view.py`: Handles the admin-specific views.
   - `home_view.py`: Manages the homepage view for regular users.
   - `user_view.py`: Manages the user interface for general users.
   - `app.py`: The main entry point for launching the Streamlit application.

2. ``air_quality_forecast/``
   This directory contains the core functionality for the air quality forecasting and the pipelines used during the data engineering and model development stages.
   The Streamlit app only accesses `prediction.py`.

   - `api_caller.py`: Defines logic for interacting with external APIs (such as fetching external data). Used in the CI/CD workflows.
   - `data_pipeline.py`: Handles data collection, transformation, and preprocessing steps.
   - `get_prediction_data.py`: Retrieves and processes prediction data for display.
   - `main.py`: Entry point for executing backend operations.
   - `model_development.py`: Defines and trains the machine learning model used for air quality prediction.
   - `parser_ui.py`: Manages any parsing related to the UI input. Contains a custom prediction and a retrain protocol.
   - `prediction.py`: Contains functions for running predictions based on the trained model. Can load models, perform validation, and output predictions.
   - `utils.py`: Contains utility functions used across the backend.

Workflow
--------

1. **Data Collection & Preprocessing**:

   The `data_pipeline.py` script handles the data collection from various sources and transforms it into a suitable format for model training and inference.
   External APIs are utilized for real-time data through `api_caller.py`.

2. **Model Development**:

   In `model_development.py`, the machine learning model is developed using techniques such as decision trees, random forests, or other appropriate algorithms. The model is trained using historical air quality data.

3. **Prediction**:

   After the model is trained, predictions can be made using the `prediction.py` script. It loads the trained model and provides air quality forecasts based on the incoming data.

4. **Streamlit Interface**:

   The `views/` directory contains the frontend built with Streamlit. Users interact with the application through the homepage (`home_view.py`) or admin page (`admin_view.py`). The main application is launched via `app.py`, which brings together all views and backend interactions.

Deployment
----------

The web application is deployed using Streamlit. To run the app locally, you can execute the following command:

.. code-block:: bash

   streamlit run ./streamlit_src/views/app.py

The app integrates both backend logic (for fetching and processing data) and frontend views, providing real-time air quality predictions to users.

Retraining Protocol
-------------------

Run `main.py` to access the parser information. After changing the hyperparameter search spaces in `configs/hyperparameter_search_spaces.yaml`, you can choose which model to train or retrain with the command:

.. code-block:: bash

   python main.py --retrain x_train_path y_train_path x_test_path y_test_path n_iter

By specifying the paths to the data in the placeholders.

Alternatively, one can make a custom prediction locally by running:

.. code-block:: bash

   python main.py --predict prediction_path

Note that the prediction dataset has to obey certain requirements, specified in the admin dashboard (easier prediction from there).

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   modules

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
