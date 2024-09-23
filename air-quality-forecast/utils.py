import pandas as pd
import os


class InputValidator:
    @staticmethod
    def validate_type(value, expected_type, variable_name: str) -> None:
        """
        Validate the type of the given variable.

        :param value: The value to validate.
        :param expected_type: The expected type of the value.
        :param variable_name: The name of the variable for error messages.
        :raises TypeError: If the value is not of the expected type.
        """
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{variable_name} must be of type {expected_type.__name__}."
            )

    @staticmethod
    def validate_file_exists(path: str, variable_name: str) -> None:
        """
        Validate that the file path exists.

        :param path: The file path to validate.
        :param variable_name: The name of the variable for error messages.
        :raises FileNotFoundError: If the path does not exist.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"{variable_name} path {path} does not exist.")


class FeatureSelector:
    def uninformative_columns() -> list:
        """Those columns provide no information that the model can use"""
        return [
            "Unnamed: 0",
            "name",
            "datetime",
            "sunrise",
            "sunset",
            "preciptype",
            "conditions",
            "description",
            "icon",
            "stations",
        ]

    def rename_initial_columns(data):
        """Rename the columns of the datasets to remove whitespaces."""
        data = data.rename(
            columns={
                " pm25": "pm25",
                " pm10": "pm10",
                " o3": "o3",
                " no2": "no2",
                " so2": "so2",
            }
        )
        return data

    def change_to_numeric(data):
        """Change each entry to a numerical value."""
        data.loc[:, data.columns != "date"] = data.loc[:, data.columns != "date"].apply(
            pd.to_numeric, errors="coerce"
        )
        return data

    def select_cols_by_correlation(data) -> list:
        """Select columns based on correlation criteria."""
        # Step 1: Calculate correlations between features and O3/NO2
        corr_no2 = abs(data.loc[:, data.columns != "date"].corr()["no2"])
        corr_o3 = abs(data.loc[:, data.columns != "date"].corr()["o3"])

        # Step 2: Remove the columns not correlated with any of the labels
        columns_above_threshold = (corr_no2 > 0.3) | (corr_o3 > 0.3)
        selected_columns = columns_above_threshold[columns_above_threshold].index

        # Step 3: Remove the columns with high correlations with each other (chosen by manual inspection of the correlation matrix)
        to_remove = [
            "feelslikemax",
            "feelslikemin",
            "feelslike",
            "tempmin",
            "tempmax",
            "dew",
            "solarenergy",
            "uvindex",
        ]
        selected_columns = [item for item in selected_columns if item not in to_remove]
        return selected_columns
