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
            if not self._is_current_data_available():
                self._view.data_not_available()
            else:
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        grandparent_dir = os.path.dirname(parent_dir)
        feature_importances_path = os.path.join(
            grandparent_dir,
            "data",
            "other",
            "feature_importance.csv",
        )

        feature_importances = pd.read_csv(feature_importances_path)

        self._view.display_feature_importance(feature_importances)

    def _show_current_data(self) -> None:
        """
        Shows the current data on the main page of the user interface.
        """
        merged_data_df = self._prepare_data_for_view()
        self._check_data_out_of_distribution(self._model.get_all_data_last_three_days())
        self._view.show_current_data(merged_data_df)

    def _model_metrics(self) -> None:
        """
        Computes the metrics for the admin interface.
        """
        df = self._model.calculate_metrics()
        self._view.display_datatable(df, "Model Metrics over Last Three Days")

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
            "Humidity should be in percentages": False,
            "Visibility should be in kilometers": False,
            "Solar Radiation should be in watts per square meter (W/m²).": False,
            "Precipitation should be in millimeters": False,
            "Wind Speed should be in kilometers per hour (km/h).": False,
            "Wind Direction should be in degrees": False,
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

        if not ((data_without_date >= 0) | data_without_date.isna()).all().all():
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
        if "date" in input_data.columns:
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
