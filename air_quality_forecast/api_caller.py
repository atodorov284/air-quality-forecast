import requests
import pandas as pd
from datetime import datetime, timedelta

class APICaller:
    def __init__(self) -> None:
        self._luchtmeet_griftpark = "NL10643"
        self._luchtmeet_erzeijstraat = "NL10639"
        self._base_url = "https://api.luchtmeetnet.nl/open_api/measurements"
        self._components_griftpark = "O3,NO2,PM25"
        self._components_erzeijstraat = "PM10"
        

    def _current_time(self) -> str:
        """
        Returns the current time in the format "YYYY-MM-DD HH:MM:SS".
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _three_days_ago(self) -> str:
        """
        Returns the date and time three days before the current time.
        """
        return (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")

    def _get_luchtmeet_data(self, components: str, station_number: int) -> list:
        """
        Fetches luchtmeet data for a specific formula from the API over the past three days.
        
        :param formula: The formula to query (e.g., 'O3', 'NO2').
        :return: List of JSON data from the API response for the given formula.
        """
        end_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        start_time = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
        url = f"{self._base_url}?station_number={station_number}&components={components}&page=1&order_by=timestamp_measured&order_direction=desc&start={start_time}&end={end_time}"
        
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            raise Exception(f"API request failed with status code: {response.status_code}")

    def get_luchtmeet_data(self) -> pd.DataFrame:
        """
        Averages out the luchtmeet data for all required formulas over the past three days.
        
        :return: A pandas DataFrame with daily averaged data for each formula.
        """
        all_data = []

        # Loop over each formula and fetch the data
        griftpark_data = self._get_luchtmeet_data(self._components_griftpark, self._luchtmeet_griftpark)
        if griftpark_data:
            all_data.extend(griftpark_data)
            
        eizeijstraat_data = self._get_luchtmeet_data(self._components_erzeijstraat, self._luchtmeet_erzeijstraat)
        if eizeijstraat_data:
            all_data.extend(eizeijstraat_data)
        
        if not all_data:
            raise Exception("No data retrieved from the API.")
        
        df = pd.DataFrame(all_data)
        df['timestamp_measured'] = pd.to_datetime(df['timestamp_measured'])
        
        df['date'] = df['timestamp_measured'].dt.date
        
        df_avg = df.groupby(['date', 'formula']).agg({'value': 'mean'}).reset_index()
        
        df_pivot = df_avg.pivot(index='date', columns='formula', values='value').reset_index()
        df_pivot = df_pivot.rename_axis(None, axis=1)
        
        #This is needed as NO2 also extracts NO...
        df_pivot.drop('NO', axis=1, inplace=True)

        df_pivot = df_pivot.set_index('date')
        return df_pivot

if __name__ == "__main__":
    caller = APICaller()
    print(caller.get_averaged_data())
