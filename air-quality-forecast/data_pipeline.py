import pandas as pd
import os

from utils import FeatureSelector
from sklearn.preprocessing import MinMaxScaler


class PreprocessingPipeline:
    def __init__(self):
        """
        Initialize the preprocessing pipeline.

        :param raw_data_path: Path to the raw data directory
        :param processed_data_path: Path to the processed data directory
        """
        
        # Global project root path
        project_root = os.path.dirname(os.path.dirname(__file__))

        # Path to the raw data directory
        self.raw_data_path = os.path.join(project_root, 'data', 'raw')

        # Path to the processed data directory
        self.processed_data_path = os.path.join(project_root, 'data', 'processed')
        
        # Initializing the raw datasets
        self.raw_griftpark_data, self.raw_utrecht_data = self.load_raw_data()

        # Initializing the merged dataset
        self.merged_data = self.merge_raw_data()
    
    def load_raw_data(self):
        """
        Load the raw data from the specified path.

        :return: Raw data as a Pandas DataFrame
        """
        # Load the first data file
        raw_griftpark_data = pd.read_csv(os.path.join(self.raw_data_path, 'v1_raw_griftpark,-utrecht-air-quality.csv'))

        # Load the second data file
        raw_utrecht_data = pd.read_csv(os.path.join(self.raw_data_path, 'v1_utrecht 2014-01-29 to 2024-09-11.csv'))

        return raw_griftpark_data, raw_utrecht_data

    def merge_raw_data(self):
        """
        Merge the raw data with additional data from the specified path.

        :param raw_data: Raw data as a Pandas DataFrame
        :return: Merged data as a Pandas DataFrame
        """
        raw_additional_data = self.raw_utrecht_data
        griftpark_data = self.raw_griftpark_data
        
        # Convert the 'date' column to datetime format and format the datetime column to 'dd/mm/yyyy'
        raw_additional_data['datetime'] = pd.to_datetime(raw_additional_data['datetime'], format='%Y-%m-%d').dt.strftime('%d/%m/%Y')

        # Merge the additional data with the raw data
        merged_df = pd.merge(griftpark_data, raw_additional_data, left_on='date', right_on='datetime')
        
        # Save the merged data
        self.save_to_csv('v1_merged_weather_data.csv', merged_df, self.processed_data_path)

        return merged_df

    def select_features(self, data):
        """
        Select the relevant features from the raw data.

        :param data: Raw data as a Pandas DataFrame
        :return: Data with selected features as a Pandas DataFrame
        """
        #Remove textual/uninformative features
        cols_to_drop = FeatureSelector.uninformative_columns()
        data.drop(cols_to_drop, axis=1, inplace=True)

        #Rename wrongly named columns
        data = FeatureSelector.rename_initial_columns(data)

        #Convert columns to numeric
        data = FeatureSelector.change_to_numeric(data)

        #Calculate correlations between features and O3/NO2
        selected_columns = FeatureSelector.select_cols_by_correlation(data)
        
        #Add domain knowledge columns
        domain_knowledge_columns = ['precip','windspeed', 'winddir']
        selected_columns = selected_columns + domain_knowledge_columns

        return data[selected_columns]
        
    def apply_time_shift(self, data, t = 3):
        """ 
        Applies the time shift to the dataset and adds the shifted columns.
        """
        all_cols = data.columns
        
        for t in range(1,t+1):
            for col in all_cols:
                data[[f'{col} - day {t}']] = data[[col]].shift(-t)

        for t in range(1,t):
            for col in ['o3', 'no2']:
                data[[f'{col} + day {t}']] = data[[col]].shift(t)

        data[data.columns] = data[data.columns].apply(pd.to_numeric)
        return data
    
    def preprocess_data(self, data):
        """
        Preprocess the raw data according to the steps outlined in the notebooks.

        :param raw_data: Raw data as a Pandas DataFrame
        :return: Preprocessed data as a Pandas DataFrame
        """
        data = self.select_features(data)
        data = self.apply_time_shift(data)
        data.drop(['pm25','pm10','temp','humidity','visibility','solarradiation','precip','windspeed','winddir'], axis=1, inplace=True)
        data.drop(index=['29/01/2014','30/01/2014','31/01/2014', '10/09/2024', '11/09/2024'], inplace=True)
    
        return data
    
    def normalize_data(self, data, normalizer_type = ""):
        if normalizer_type == "":
            ss = MinMaxScaler()
        

    def save_to_csv(self, name, data, path):
        """
        Save the preprocessed data to the specified path.

        :param preprocessed_data: Preprocessed data as a Pandas DataFrame
        """
        data.to_csv(os.path.join(path, name))

    def run_pipeline(self):
        """
        Run the entire preprocessing pipeline.
        """
        raw_data = self.load_raw_data()
        merged_data = self.merge_raw_data(raw_data)
        preprocessed_data = self.preprocess_data(raw_data)
        self.save_processed_data(preprocessed_data)

pipeline = PreprocessingPipeline()