import os
from typing import Tuple
from views.admin_view import AdminView
import streamlit as st
from controllers.user_controller import UserController
import pandas as pd
from air_quality_forecast.prediction import PredictorModels


class AdminController(UserController):
    """
    A class to handle the admin interface. Inherits from UserController
    """

    def __init__(self) -> None:
        """
        Initializes the AdminController class.
        """
        super().__init__()
        self._view = AdminView()
        self._distribution_means, self._distribution_stds = (
            self._compute_distribution_statistics()
        )

    def show_dashboard(self) -> None:
        """
        Shows the main page of the admin interface.
        """

        switch = self._view.show_admin_pages()

        if switch == "Display Predictions":
            self._show_current_data()
            self._display_plots()

        elif switch == "Make Predictions":
            self._make_custom_predictions()

        elif switch == "Feature Importances":
            self._feature_importance()

        elif switch == "Model Metrics":
            self._model_metrics()

    def _feature_importance(self) -> Tuple[list, list]:
        """
        Retrieves the feature importance values and their corresponding feature names.

        Returns:
            Tuple[list, list]: A tuple containing the feature names and their importance values.
        """

        # This is sad but has to be done like this
        features = [
            "Temperature (lag=1)",
            "O₃ (lag=1)",
            "PM₂.₅ (lag=1)",
            "Humidity (lag=1)",
            "Solar Radiation (lag=1)",
            "O₃ (lag=3)",
            "Solar Radiation (lag=2)",
            "Solar Radiation (lag=3)",
            "NO₂ (lag=1)",
            "O₃ (lag=2)",
            "Wind Direction (lag=1)",
            "Visibility (lag=1)",
            "PM₁₀ (lag=1)",
            "Visibility (lag=3)",
            "Precipitation (lag=1)",
            "Precipitation (lag=3)",
            "Precipitation (lag=2)",
            "Temperature (lag=2)",
            "NO₂ (lag=3)",
            "Humidity (lag=3)",
            "Wind Speed (lag=2)",
            "Wind Speed (lag=3)",
            "PM₂.₅ (lag=3)",
            "Temperature (lag=3)",
            "Wind Speed (lag=1)",
            "PM₂.₅ (lag=2)",
            "Humidity (lag=2)",
            "PM₁₀ (lag=2)",
            "NO₂ (lag=2)",
            "Visibility (lag=2)",
            "Wind Direction (lag=3)",
            "Wind Direction (lag=2)",
            "PM₁₀ (lag=3)",
        ]

        importance_values = [
            5.766941,
            5.63263,
            3.5815392,
            3.475367,
            3.456865,
            2.3959482,
            1.8265718,
            1.6795981,
            1.5732919,
            1.464834,
            1.2373743,
            0.8109572,
            0.60146403,
            0.5048162,
            0.49500573,
            0.44572872,
            0.41351405,
            0.4023266,
            0.38021353,
            0.3769183,
            0.3461746,
            0.3079201,
            0.285651,
            0.28092846,
            0.23774858,
            0.20836349,
            0.1959943,
            0.18470103,
            0.1738453,
            0.16350256,
            0.14222378,
            0.14136884,
            0.09763571,
        ]

        self._view.display_feature_importance(features, importance_values)

    def welcome_back(self) -> None:
        """
        Shows a welcome message for the admin interface.
        """
        self._view.welcome_back()

    def _model_metrics(self) -> None:
        """
        Computes the metrics for the admin interface.
        """
        pass

    def _compute_distribution_statistics(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Computes the means and standard deviations of the features in the dataset.

        Returns:
            A tuple of two DataFrames. The first DataFrame contains the means of the features
                and the second DataFrame contains the standard deviations of the features.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        grandparent_dir = os.path.dirname(parent_dir)
        distribution_data = pd.read_csv(
            os.path.join(
                grandparent_dir,
                "data",
                "processed/",
                "v2_merged_selected_features_with_missing.csv",
            ),
            index_col=0,
        )

        distribution_means = (
            distribution_data.mean().reset_index(drop=False).transpose()
        )
        distribution_means.columns = distribution_means.iloc[0]
        distribution_means = distribution_means[1:]

        distribution_stds = distribution_data.std().reset_index(drop=False).transpose()
        distribution_stds.columns = distribution_stds.iloc[0]
        distribution_stds = distribution_stds[1:]

        formatted_means = pd.concat(
            [
                distribution_means.add_suffix(" - day 0"),
                distribution_means.add_suffix(" - day 1"),
                distribution_means.add_suffix(" - day 2"),
            ],
            axis=1,
        )

        formatted_stds = pd.concat(
            [
                distribution_stds.add_suffix(" - day 0"),
                distribution_stds.add_suffix(" - day 1"),
                distribution_stds.add_suffix(" - day 2"),
            ],
            axis=1,
        )

        return formatted_means, formatted_stds

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

                if not self._data_is_valid(data):
                    return

                self._check_data_out_of_distribution(data)

                if "date" in data.columns or "datetime" in data.columns:
                    data.set_index(
                        "date" if "date" in data.columns else "datetime", inplace=True
                    )

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

    def _data_is_valid(self, data: pd.DataFrame) -> bool:
        """
        Performs data validation on the uploaded user data.

        Args:
            data (pd.DataFrame): The user data.

        Returns:
            bool: True if the data is valid, otherwise False.
        """
        columns = data.columns
        expected_columns_count = 33
        has_date_column = "date" in columns

        if has_date_column:
            if len(columns) != expected_columns_count + 1:
                self._view.error(
                    f"Invalid column count. Expected {expected_columns_count + 1} columns including 'date', but got {len(columns)}."
                )
                return False
        else:
            # Dataset should have exactly 33 columns
            if len(columns) != expected_columns_count:
                self._view.error(
                    f"Invalid column count. Expected {expected_columns_count} columns, but got {len(columns)}."
                )
                return False

        data_without_date = data.drop(columns=["date"], errors="ignore")

        if (
            not data_without_date.map(
                lambda x: isinstance(x, (float, int)) or pd.isna(x)
            )
            .all()
            .all()
        ):
            self._view.error(
                "The dataset contains values that are not floats or NaN. All values must be floats or NaN."
            )
            return False

        if not (data_without_date >= 0).all().all():
            self._view.error(
                "The dataset contains negative values. All values must be positive."
            )
            return False

        # If all checks passed
        self._view.success("Data validation passed successfully.")
        return True

    def _check_data_out_of_distribution(
        self, input_data: pd.DataFrame, threshold: float = 3
    ) -> bool:
        """
        Checks if the input data is out of distribution compared to the training data.
        Displays which features exceed the threshold.

        Args:
            data (pd.DataFrame): The new input data to validate.
            threshold (float): The Z-score threshold to determine out of distribution.

        Returns:
            bool: True if the input data is out of distribution, False otherwise.
        """
        input_data.drop("date", axis=1, inplace=True)

        z_scores = (
            input_data - self._distribution_means.values.squeeze()
        ) / self._distribution_stds.values.squeeze()

        out_of_distribution_flags = z_scores.abs() > threshold

        ood_rows = out_of_distribution_flags.sum(axis=1)

        if ood_rows.any():
            error_message = f"Input data might contain out-of-distribution values. {ood_rows.sum()} {'feature exceeds' if ood_rows.sum() == 1 else 'features exceed'} exceed the z-score threshold. Model prediction might be inaccurate.\n\n"

            ood_details = z_scores[out_of_distribution_flags]
            for index, row in ood_details.iterrows():
                ood_features = row.dropna().index.tolist()
                ood_values = input_data.loc[index, ood_features]

                # Loop through each feature individually for better readability
                for feature, value in zip(ood_features, ood_values):
                    error_message += f"Row {index + 1}: The feature '{feature}' has a value of {value:.2f}.\n\n"

            self._view.error(error_message)

            return

        self._view.success("Input data is within the expected distribution.")
