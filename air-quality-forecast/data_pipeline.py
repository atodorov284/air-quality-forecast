import pandas as pd
import os


class PreprocessingPipeline:
    def __init__(self):
        """
        Initialize the preprocessing pipeline.

        :param raw_data_path: Path to the raw data directory
        :param processed_data_path: Path to the processed data directory
        """

        project_root = os.path.dirname(os.path.dirname(__file__))
        raw_data_path = os.path.join(project_root, 'data', 'raw')
        
        print(raw_data_path)
        for file in os.listdir(raw_data_path):
            print(file)

    def load_raw_data(self):
        """
        Load the raw data from the specified path.

        :return: Raw data as a Pandas DataFrame
        """
        # TO DO: Implement loading of raw data
        pass

    def merge_raw_data(self, raw_data):
        """
        Merge the raw data with additional data from the specified path.

        :param raw_data: Raw data as a Pandas DataFrame
        :return: Merged data as a Pandas DataFrame
        """
        # TO DO: Implement merging of raw data
        pass

    def preprocess_data(self, raw_data):
        """
        Preprocess the raw data according to the steps outlined in the notebooks.

        :param raw_data: Raw data as a Pandas DataFrame
        :return: Preprocessed data as a Pandas DataFrame
        """
        # TO DO: Implement preprocessing steps
        pass

    def save_to_csv(self, name, data):
        """
        Save the preprocessed data to the specified path.

        :param preprocessed_data: Preprocessed data as a Pandas DataFrame
        """
        # TO DO: Implement saving of preprocessed data
        pass

    def run_pipeline(self):
        """
        Run the entire preprocessing pipeline.
        """
        raw_data = self.load_raw_data()
        merged_data = self.merge_raw_data(raw_data)
        preprocessed_data = self.preprocess_data(raw_data)
        self.save_processed_data(preprocessed_data)

pipeline = PreprocessingPipeline()