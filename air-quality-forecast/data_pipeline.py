import pandas as pd
import os
from utils import FeatureSelector
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from typing import Tuple

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
            raise TypeError(f"{variable_name} must be of type {expected_type.__name__}.")
    
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

        self.raw_griftpark_data = pd.read_csv(os.path.join(self.raw_data_path, 'v1_raw_griftpark,-utrecht-air-quality.csv'))
        self.raw_utrecht_data = pd.read_csv(os.path.join(self.raw_data_path, 'v1_utrecht 2014-01-29 to 2024-09-11.csv'))
        return self.raw_griftpark_data, self.raw_utrecht_data

    def save_to_csv(self, name: str, data: pd.DataFrame) -> None:
        """
        Save the data to a CSV file.

        :param name: The name of the file to save.
        :param data: The Pandas DataFrame to save as a CSV.
        """
        InputValidator.validate_type(name, str, "name")
        InputValidator.validate_type(data, pd.DataFrame, "data")
    
        data.to_csv(os.path.join(self.processed_data_path, name))


class FeatureProcessor:
    def __init__(self, griftpark_data: pd.DataFrame, utrecht_data: pd.DataFrame) -> None:
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
        self.utrecht_data['datetime'] = pd.to_datetime(self.utrecht_data['datetime'], format='%Y-%m-%d').dt.strftime('%d/%m/%Y')
        self.merged_data = pd.merge(self.griftpark_data, self.utrecht_data, left_on='date', right_on='datetime')
        return self.merged_data

    def sort_data_by_date(self) -> pd.DataFrame:
        """
        Sort the merged data by date, starting from the most recent to the oldest.

        :return: The sorted Pandas DataFrame.
        """
        if self.merged_data is None:
            raise ValueError("Merged data not available. Please merge data first.")
        self.merged_data['datetime'] = pd.to_datetime(self.merged_data['datetime'], format='%d/%m/%Y')
        self.merged_data.sort_values(by='datetime', ascending=False, inplace=True)
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
        self.merged_data.drop(cols_to_drop, axis=1, inplace=True, errors='ignore')
        self.merged_data = FeatureSelector.rename_initial_columns(self.merged_data)
        self.merged_data = FeatureSelector.change_to_numeric(self.merged_data)
        
        selected_columns = FeatureSelector.select_cols_by_correlation(self.merged_data)
        domain_knowledge_columns = ['precip','windspeed', 'winddir']
        selected_columns = ['date'] + selected_columns + domain_knowledge_columns
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
                self.merged_data[[f'{col} - day {t}']] = self.merged_data[[col]].shift(-t)
        
        for t in range(1, 3):
            for col in ['o3', 'no2']:
                self.merged_data[[f'{col} + day {t}']] = self.merged_data[[col]].shift(t)
        
        self.merged_data[self.merged_data.columns] = self.merged_data[self.merged_data.columns].apply(pd.to_numeric)
        return self.merged_data

    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the data by applying feature selection, missing value removal, and time shift.

        :return: The preprocessed Pandas DataFrame.
        """
        self.select_features()
        self.merged_data.set_index('date', inplace=True)
        self.merged_data.dropna(subset=['o3', 'no2'])
        self.apply_time_shift()

        # Drop unnecessary columns
        self.merged_data.drop(['pm25', 'pm10', 'temp', 'humidity', 'visibility', 'solarradiation', 'precip', 'windspeed', 'winddir'], axis=1, inplace=True)
        self.merged_data.drop(index=['29/01/2014', '30/01/2014', '31/01/2014', '10/09/2024', '11/09/2024'], inplace=True)

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


class Normalizer:
    def normalize_data(self, data: pd.DataFrame, normalizer_type: str = "MinMax") -> pd.DataFrame:
        """
        Normalize the dataset using a specified normalizer.

        :param data: The data to normalize as a Pandas DataFrame.
        :param normalizer_type: The type of normalizer to use. Options are 'MinMax', 'Standard', and 'Robust'.
        :return: The normalized data as a Pandas DataFrame.
        """
        InputValidator.validate_type(data, pd.DataFrame, "data")
        InputValidator.validate_type(normalizer_type, str, "normalizer_type")

        normalizers = {
            "MinMax": MinMaxScaler,
            "Standard": StandardScaler,
            "Robust": RobustScaler
        }

        if normalizer_type not in normalizers:
            raise ValueError(f"Invalid normalizer_type '{normalizer_type}'. Valid options are: 'MinMax', 'Standard', or 'Robust'.")
    
        scaler = normalizers[normalizer_type]()
        return pd.DataFrame(scaler.fit_transform(data), columns=data.columns, index=data.index)

    def __call__(self, data: pd.DataFrame, normalizer_type: str = "MinMax") -> pd.DataFrame:
        """
        Normalize the data when the class is called.

        :param data: The data to normalize as a Pandas DataFrame.
        :param normalizer_type: The type of normalizer to use.
        :return: The normalized data as a Pandas DataFrame.
        """
        return self.normalize_data(data, normalizer_type)


class PreprocessingPipeline:
    def __init__(self) -> None:
        """
        Initializes the PreprocessingPipeline with paths to raw and processed data directories.
        """
        project_root = os.path.dirname(os.path.dirname(__file__))
        raw_data_path = os.path.join(project_root, 'data', 'raw')
        processed_data_path = os.path.join(project_root, 'data', 'processed')

        self.data_loader = DataLoader(raw_data_path, processed_data_path)
        self.feature_processor = None
        self.normalizer = Normalizer()

    def run_pipeline(self, normalizer_type: str = "MinMax") -> pd.DataFrame:
        """
        Run the entire preprocessing pipeline: load data, process features, normalize, and save to CSV.

        :param normalizer_type: The type of normalizer to use.
        :return: The final normalized Pandas DataFrame.
        """
        InputValidator.validate_type(normalizer_type, str, "normalizer_type")
        
        # Step 1: Load raw data
        griftpark_data, utrecht_data = self.data_loader()

        # Step 2: Process features (merge, sort, feature selection, preprocessing, time shift)
        self.feature_processor = FeatureProcessor(griftpark_data, utrecht_data)
        preprocessed_data = self.feature_processor()

        # Step 3: Normalize data
        # normalized_data = self.normalizer(preprocessed_data, normalizer_type)

        # Convert the normalized NumPy array back to a DataFrame
        # normalized_df = pd.DataFrame(normalized_data, columns=preprocessed_data.columns, index=preprocessed_data.index)

        # Step 4: Save processed data
        self.data_loader.save_to_csv('test.csv', preprocessed_data)

        return preprocessed_data

pipeline = PreprocessingPipeline()
pipeline.run_pipeline(normalizer_type="MinMax")