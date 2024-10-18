from views.admin_view import AdminView
import streamlit as st
from controllers.user_controller import UserController
import pandas as pd
from air_quality_forecast.prediction import PredictorModels


class AdminController(UserController):
    """
    A class to handle the admin interface.
    """

    def __init__(self) -> None:
        """
        Initializes the AdminController class.
        """
        super().__init__()
        self._view = AdminView()

    def show_dashboard(self) -> None:
        """
        Shows the main page of the admin interface.
        """
        st.markdown("ADMIN DASHBOARD")
        self._show_current_data()
        self._display_plots()
        self._make_custom_predictions()

    def welcome_back(self) -> None:
        """
        Shows a welcome message for the admin interface.
        """
        self._view.welcome_back()

    def _compute_metrics(self) -> None:
        """
        Computes the metrics for the admin interface.
        """
        pass

    def _make_custom_predictions(self) -> None:
        """
        Makes a custom prediction for the admin interface.
        """
        self._view.upload_instructions()
        checks = {
            "The data must be unnormalized.": False,
            "PM25, PM10, O3, NO2 should be in micrograms per cubic meter (µg/m³).": False,
            "Temperature should be in degrees Celcius": False,
            "Add the others later": False,
            "The dataset must contain a total of 33 columns in the specified order.": False,
            "I accept that my data will be used for a prediction using a custom model.": False,
            "I understand that my data will not be saved.": False,
        }

        all_checks_marked = self._view.confirm_checks(checks)

        if all_checks_marked:
            dataset = self._view.upload_dataset()
            if dataset is not None:
                data = pd.read_csv(dataset)

                self._perform_data_validation(data)
                if "date" in data.columns or "datetime" in data.columns:
                    data.set_index(
                        "date" if "date" in data.columns else "datetime", inplace=True
                    )

                data.columns = [
                    "pm25 - day 1",
                    "pm10 - day 1",
                    "o3 - day 1",
                    "no2 - day 1",
                    "temp - day 1",
                    "humidity - day 1",
                    "visibility - day 1",
                    "solarradiation - day 1",
                    "precip - day 1",
                    "windspeed - day 1",
                    "winddir - day 1",
                    "pm25 - day 2",
                    "pm10 - day 2",
                    "o3 - day 2",
                    "no2 - day 2",
                    "temp - day 2",
                    "humidity - day 2",
                    "visibility - day 2",
                    "solarradiation - day 2",
                    "precip - day 2",
                    "windspeed - day 2",
                    "winddir - day 2",
                    "pm25 - day 3",
                    "pm10 - day 3",
                    "o3 - day 3",
                    "no2 - day 3",
                    "temp - day 3",
                    "humidity - day 3",
                    "visibility - day 3",
                    "solarradiation - day 3",
                    "precip - day 3",
                    "windspeed - day 3",
                    "winddir - day 3",
                ]
                self._view.display_datatable(data, message="### User Data")

                prediction = self._make_prediction(data)
                self._view.display_datatable(
                    prediction, message="### XGBoost Model Prediction (first 6 rows)"
                )
                self._view.download_button(
                    label="Download predictions as CSV",
                    data=prediction.to_csv(index=True),
                    file_name="predictions.csv",
                )

        else:
            st.warning("Please confirm all the requirements by marking the checkboxes.")

    def _make_prediction(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Makes a prediction using an XGBoost model.

        Args:
            data (pd.DataFrame): The data to make the prediction on.

        Returns:
            pd.DataFrame: The prediction.
        """
        predictor = PredictorModels()
        prediction = predictor.xgb_predictions(data, normalized=False)
        prediction = pd.DataFrame(
            prediction,
            columns=[
                "NO2 + day 1",
                "O3 + day 1",
                "NO2 + day 2",
                "O3 + day 2",
                "NO2 + day 3",
                "O3 + day 3",
            ],
            index=data.index,
        )

        return prediction

    def _perform_data_validation(self, data: pd.DataFrame) -> None:
        """
        Performs data validation on the user data.

        Args:
            data (pd.DataFrame): The user data.
        """
        pass
