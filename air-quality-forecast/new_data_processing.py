import pandas as pd
from data_pipeline import FeatureProcessor


def merge_data(aqi_path=None, vc_path=None):
    """
    Merge the datasets from data.csv and previousdaysAQI.csv by datetime
    """
    # read the data from the two csv files
    left = pd.read_csv(aqi_path)
    right = pd.read_csv(vc_path)

    # merge the data based on datetime
    # if the dates dont match, warn the user by raising an error
    try:
        result = pd.merge(left, right, on='datetime')
    except ValueError:
        print("Error: The dates in the two datasets do not match.",
              "Check whether the data is correct and try again.")
        result = None
    return result


def reshape_data(result):
    """
    Reshape the data to have the desired format
    """
    # rearrange the columns
    desired_order = ['datetime', 'pm25', 'pm10',
                     'o3', 'no2', 'temp',
                     'humidity', 'visibility', 'solarradiation',
                     'precip', 'windspeed', 'winddir']
    result = result[desired_order]
    return result


def drop_future_columns(result):
    """
    Drop the columns with +1 and +2
    """
    result = result.drop(columns=['o3 + day 1',
                                  'no2 + day 1',
                                  'o3 + day 2',
                                  'no2 + day 2'])
    return result


def save_to_csv(result, path):
    """
    Save the data to a CSV file
    """
    result.to_csv(path, index=False)


if __name__ == "__main__":
    print("BEFORE RUNNING MAKE SURE THAT THE DATA IS UPDATED BY CALLING",
          "api_data_call.py")
    aqi_path = "previousdaysAQI.csv"
    vc_path = "data.csv"
    result = merge_data(aqi_path, vc_path)
    result = reshape_data(result)

    # initialize the feature processor (arguments are necessary
    # but do not matter here)
    feature_processor = FeatureProcessor(result, result)
    feature_processor.merged_data = result

    # rename datetime to date
    feature_processor.merged_data.rename(columns={'datetime': 'date'},
                                         inplace=True)

    # apply time shift
    feature_processor.merged_data.set_index("date", inplace=True)
    result = feature_processor.apply_time_shift(t_max=2)

    # drop the future columns
    result = drop_future_columns(result)

    # save the data to a CSV file
    result = result.head(1)
    path = "currentdata.csv"
    save_to_csv(result, path)
    print(f"Data saved to {path}")
