"""
File with utilities 
"""

class FeatureSelector:
    def uninformative_columns() -> list:
        """ Those columns provide no information that the model can use"""
        return ["Unnamed: 0", 'name', 'datetime', 'sunrise', 'sunset', 'preciptype', 'conditions', 'description', 'icon', 'stations']
    def rename_initial_columns(data):
        """ Rename the columns of the datasets to remove whitespaces."""
        data = data.rename(columns={" pm25": "pm25", " pm10": "pm10", " o3": "o3", " no2": "no2", " so2": "so2"})
        return data
    def change_to_numeric(data):
        """ Change each entry to a numerical value."""
        data.loc[:, data.columns != 'date'] = data.loc[:, data.columns != 'date'].apply(pd.to_numeric, errors='coerce')
        return data
    def select_cols_by_correlation(data) -> list:
        """ Select columns based on correlation criteria."""
        #Step 1: Calculate correlations between features and O3/NO2
        corr_no2 = abs(data.loc[:, data.columns != 'date'].corr()['no2'])
        corr_o3 = abs(data.loc[:, data.columns != 'date'].corr()['o3'])
        #Step 2: Remove the columns not correlated with any of the labels
        columns_above_threshold = (corr_no2 > 0.3) | (corr_o3 > 0.3)
        selected_columns = columns_above_threshold[columns_above_threshold].index
        #Step 3: Remove the columns with high correlations with each other (chosen by manual inspection of the correlation matrix)
        to_remove = ['feelslikemax', 'feelslikemin', 'feelslike', 'tempmin', 'tempmax', 'dew', 'solarenergy', 'uvindex']
        selected_columns = [item for item in selected_columns if item not in to_remove]
        return selected_columns
 