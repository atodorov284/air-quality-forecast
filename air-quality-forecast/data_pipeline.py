import pandas as pd
import os
from utils import FeatureSelector, InputValidator
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from typing import Tuple
import numpy as np
import joblib


class DataLoader:
    def __init__(self, raw_data_path: str, processed_data_path: str) -> None:
        """
        Initializes the DataLoader with paths to raw and processed data.

        :param raw_data_path: Path to the raw data directory.
        :param processed_data_path: Path to the processed data directory.
        """
        InputValidator.validate_type(raw_data_path, str, "raw_data_path")
        InputValidator.validate_type(processed_data_path, str, "processed_data_path")

        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.raw_griftpark_data = None
        self.raw_utrecht_data = None

    def __call__(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load raw datasets when the class is called.

        :return: Two Pandas DataFrames containing Griftpark and Utrecht data.
        """
        InputValidator.validate_file_exists(self.raw_data_path, "raw_data_path")

        self.raw_griftpark_data = pd.read_csv(
            os.path.join(
                self.raw_data_path, "v1_raw_griftpark,-utrecht-air-quality.csv"
            )
        )
        self.raw_utrecht_data = pd.read_csv(
            os.path.join(self.raw_data_path, "v1_utrecht 2014-01-29 to 2024-09-11.csv")
        )
        return self.raw_griftpark_data, self.raw_utrecht_data

    def save_to_csv(self, name: str, data: pd.DataFrame) -> None:
        """
        Save the data to a CSV file.

        :param name: The name of the file to save.
        :param data: The Pandas DataFrame to save as a CSV.
        """
        InputValidator.validate_type(name, str, "name")

        # If the data is a numpy array, convert it to a Pandas DataFrame
        if isinstance(data, np.ndarray):
            data = pd.DataFrame(data)

        data.to_csv(os.path.join(self.processed_data_path, name))


class FeatureProcessor:
    def __init__(
        self, griftpark_data: pd.DataFrame, utrecht_data: pd.DataFrame
    ) -> None:
        """
        Initializes the FeatureProcessor with Griftpark and Utrecht data.

        :param griftpark_data: Data from Griftpark in Pandas DataFrame format.
        :param utrecht_data: Data from Utrecht in Pandas DataFrame format.
        """
        InputValidator.validate_type(griftpark_data, pd.DataFrame, "griftpark_data")
        InputValidator.validate_type(utrecht_data, pd.DataFrame, "utrecht_data")

        self.griftpark_data = griftpark_data
        self.utrecht_data = utrecht_data
        self.merged_data = None

    def merge_raw_data(self) -> pd.DataFrame:
        """
        Merge the raw datasets based on date.

        :return: The merged Pandas DataFrame.
        """
        self.utrecht_data["datetime"] = pd.to_datetime(
            self.utrecht_data["datetime"], format="%Y-%m-%d"
        ).dt.strftime("%d/%m/%Y")
        self.merged_data = pd.merge(
            self.griftpark_data, self.utrecht_data, left_on="date", right_on="datetime"
        )
        return self.merged_data

    def sort_data_by_date(self) -> pd.DataFrame:
        """
        Sort the merged data by date, starting from the most recent to the oldest.

        :return: The sorted Pandas DataFrame.
        """
        if self.merged_data is None:
            raise ValueError("Merged data not available. Please merge data first.")
        self.merged_data["datetime"] = pd.to_datetime(
            self.merged_data["datetime"], format="%d/%m/%Y"
        )
        self.merged_data.sort_values(by="datetime", ascending=True, inplace=True)
        return self.merged_data

    def select_features(self) -> pd.DataFrame:
        """
        Select relevant features from the merged data.

        :return: A Pandas DataFrame with selected features.
        """
        if self.merged_data is None:
            raise ValueError("Merged data not available. Please merge data first.")

        InputValidator.validate_type(self.merged_data, pd.DataFrame, "merged_data")

        # Feature selection logic
        cols_to_drop = FeatureSelector.uninformative_columns()
        self.merged_data.drop(cols_to_drop, axis=1, inplace=True, errors="ignore")
        self.merged_data = FeatureSelector.rename_initial_columns(self.merged_data)
        self.merged_data = FeatureSelector.change_to_numeric(self.merged_data)

        selected_columns = FeatureSelector.select_cols_by_correlation(self.merged_data)
        domain_knowledge_columns = ["precip", "windspeed", "winddir"]
        selected_columns = ["date"] + selected_columns + domain_knowledge_columns
        self.merged_data = self.merged_data[selected_columns]

        return self.merged_data

    def apply_time_shift(self, t_max: int = 3) -> pd.DataFrame:
        """
        Apply time shift to the dataset.

        :param t_max: Maximum time shift, representing the number of days used to predict future values.
        :return: The time-shifted Pandas DataFrame.
        """
        if self.merged_data is None:
            raise ValueError("Data not available. Please process data first.")

        InputValidator.validate_type(t_max, int, "t_max")

        # Time shifting logic
        all_cols = self.merged_data.columns
        for t in range(1, t_max + 1):
            for col in all_cols:
                self.merged_data[[f"{col} - day {t}"]] = self.merged_data[[col]].shift(
                    -t
                )

        for t in range(1, 3):
            for col in ["o3", "no2"]:
                self.merged_data[[f"{col} + day {t}"]] = self.merged_data[[col]].shift(
                    t
                )

        self.merged_data[self.merged_data.columns] = self.merged_data[
            self.merged_data.columns
        ].apply(pd.to_numeric)
        return self.merged_data

    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the data by applying feature selection, missing value removal, and time shift.

        :return: The preprocessed Pandas DataFrame.
        """
        self.select_features()
        self.merged_data.set_index("date", inplace=True)
        self.merged_data.dropna(subset=["o3", "no2"], inplace=True)
        self.apply_time_shift()

        # Drop unnecessary columns
        self.merged_data.drop(
            [
                "pm25",
                "pm10",
                "temp",
                "humidity",
                "visibility",
                "solarradiation",
                "precip",
                "windspeed",
                "winddir",
            ],
            axis=1,
            inplace=True,
        )
        self.merged_data.drop(
            index=[
                "29/01/2014",
                "30/01/2014",
                "31/01/2014",
                "10/09/2024",
                "11/09/2024",
            ],
            inplace=True,
        )

        self.preprocessed_data = self.merged_data
        return self.preprocessed_data

    def __call__(self) -> pd.DataFrame:
        """
        Perform the entire feature processing when the class is called.

        :return: The preprocessed Pandas DataFrame.
        """
        self.merge_raw_data()
        self.sort_data_by_date()
        self.preprocess_data()
        return self.preprocessed_data


class PreprocessingPipeline:
    def __init__(self) -> None:
        """
        Initializes the PreprocessingPipeline with paths to raw and processed data directories.
        """
        project_root = os.path.dirname(os.path.dirname(__file__))
        raw_data_path = os.path.join(project_root, "data", "raw")
        processed_data_path = os.path.join(project_root, "data", "processed")

        self.data_loader = DataLoader(raw_data_path, processed_data_path)
        self.feature_processor = None
        self.normalizer = MinMaxScaler()

    def train_test_split(
        self, x: pd.DataFrame, y: pd.DataFrame, test_size: float = 0.2
    ) -> Tuple[
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
    ]:
        """
        Split the data into training and testing sets.

        :param data: The data to split as a Pandas DataFrame.
        :return: A tuple of the training and testing data as Pandas DataFrames.
        """
        InputValidator.validate_type(x, pd.DataFrame, "data")
        InputValidator.validate_type(y, pd.DataFrame, "data")
        InputValidator.validate_type(test_size, float, "test_size")

        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=test_size, shuffle=False
        )

        return x_train, x_test, y_train, y_test

    def run_pipeline(self) -> pd.DataFrame:
        """
        Run the entire preprocessing pipeline: load data, process features, normalize, and save to CSV.

        :param normalizer_type: The type of normalizer to use.
        :return: The final normalized Pandas DataFrame.
        """

        # Step 1: Load raw data
        griftpark_data, utrecht_data = self.data_loader()

        # Step 2: Process features (merge, sort, feature selection, preprocessing, time shift)
        self.feature_processor = FeatureProcessor(griftpark_data, utrecht_data)
        preprocessed_data = self.feature_processor()

        # Step 3: Save processed data
        self.data_loader.save_to_csv(
            "v3_lagged_no_missing_predicted_data.csv", preprocessed_data
        )

        # Step 4: Split data into train and test sets
        columns_to_predict = [
            "no2",
            "o3",
            "no2 + day 1",
            "o3 + day 1",
            "no2 + day 2",
            "o3 + day 2",
        ]
        x = preprocessed_data.drop(columns_to_predict, axis=1)
        y = preprocessed_data[columns_to_predict]
        x_train, x_test, y_train, y_test = self.train_test_split(x, y)

        # Step 5: Normalize data for 2 sets (x_train, x_test)
        x_train[x_train.columns] = self.normalizer.fit_transform(
            x_train[x_train.columns]
        )
        x_test[x_test.columns] = self.normalizer.transform(x_test[x_test.columns])
        
        project_root = os.path.dirname(os.path.dirname(__file__))
        saved_models_path = os.path.join(project_root, "saved_models")
        joblib.dump(self.normalizer, os.path.join(saved_models_path, 'normalizer.joblib'))

        # Convert the normalized NumPy array back to a DataFrame
        # normalized_x_train = pd.DataFrame(x_train, columns=preprocessed_data.columns, index=preprocessed_data.index)

        # Step 6: Save normalized data
        self.data_loader.save_to_csv("x_train.csv", x_train)
        self.data_loader.save_to_csv("x_test.csv", x_test)
        self.data_loader.save_to_csv("y_train.csv", y_train)
        self.data_loader.save_to_csv("y_test.csv", y_test)

        # Convert the normalized NumPy array back to a DataFrame
        # normalized_df = pd.DataFrame(normalized_data, columns=preprocessed_data.columns, index=preprocessed_data.index)

        return preprocessed_data


if __name__ == "__main__":
    pipeline = PreprocessingPipeline()
    pipeline.run_pipeline()
