import requests
import pandas as pd
from datetime import datetime, timedelta
import os


class APICaller:
    def __init__(self) -> None:
        """
        Initializes the APICaller class. Gets the luchtmeet data for the griftpark and erzeijstraat stations.
        Also can merge the data and present it in a lagged format for the model's input.
        """
        self._luchtmeet_griftpark = "NL10643"
        self._luchtmeet_erzeijstraat = "NL10639"
        self._base_luchtmeet_url = "https://api.luchtmeetnet.nl/open_api/measurements"
        self._components_griftpark = "O3,NO2,PM25"
        self._components_erzeijstraat = "PM10"
        self._vc_base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata/history"
        # probably need to hide this lol (it's Lukasz' key but its public anyway)
        self._vc_key = os.environ.get("VC_KEY")
        print(self._vc_key)
        self._vc_max_wait = 10
        self._successful_request_code = 200

    def _current_time(self) -> str:
        """
        Returns the current time in the format "YYYY-MM-DD HH:MM:SS".
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _three_days_ago(self) -> str:
        """
        Returns the date and time three days before the current time.
        """
        return (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")

    def _get_luchtmeet_data(self, components: str, station_number: int) -> list:
        """
        Fetches luchtmeet data for a specific formula from the API over the past three days.

        :param components: The components to query (e.g., 'O3,NO2,PM25').
        :param station_number: The station number to query.
        :return: List of JSON data from the API response for the given components.
        """
        end_time = self._current_time()
        start_time = self._three_days_ago()
        url = f"{self._base_luchtmeet_url}?station_number={station_number}&components={components}&page=1&order_by=timestamp_measured&order_direction=desc&start={start_time}&end={end_time}"

        response = requests.get(url)
        if response.status_code == self._successful_request_code:
            return response.json().get("data", [])
        else:
            raise Exception(
                f"API request failed with status code: {response.status_code}"
            )

    def get_luchtmeet_data(self) -> pd.DataFrame:
        """
        Averages out the luchtmeet data for all required formulas over the past three days.

        :return: A pandas DataFrame with daily averaged data for each formula.
        """
        all_data = []

        # Loop over each formula and fetch the data
        griftpark_data = self._get_luchtmeet_data(
            self._components_griftpark, self._luchtmeet_griftpark
        )
        if griftpark_data:
            all_data.extend(griftpark_data)

        erzeijstraat_data = self._get_luchtmeet_data(
            self._components_erzeijstraat, self._luchtmeet_erzeijstraat
        )
        if erzeijstraat_data:
            all_data.extend(erzeijstraat_data)

        if not all_data:
            raise Exception("No data retrieved from the API.")

        df = pd.DataFrame(all_data)
        df["timestamp_measured"] = pd.to_datetime(df["timestamp_measured"])
        df["date"] = df["timestamp_measured"].dt.date

        df_avg = df.groupby(["date", "formula"]).agg({"value": "mean"}).reset_index()
        df_pivot = df_avg.pivot(
            index="date", columns="formula", values="value"
        ).reset_index()
        df_pivot = df_pivot.rename_axis(None, axis=1)

        # This is needed as NO2 also extracts NO...
        df_pivot.drop("NO", axis=1, inplace=True)
        df_pivot = df_pivot.set_index("date")

        return df_pivot

    def get_vc_data(self) -> pd.DataFrame:
        """
        Fetches weather data for Utrecht for the last three days from Visual Crossing API.

        :return: A pandas DataFrame with the weather data for the last three days.
        """
        start_date = self._three_days_ago()
        end_date = self._current_time()
        url = f"{self._vc_base_url}?&aggregateHours=24&startDateTime={start_date}&endDateTime={end_date}&unitGroup=metric&contentType=json&dayStartTime=0:0:00&dayEndTime=0:0:00&location=Utrecht&key={self._vc_key}"

        try:
            response = requests.get(url, timeout=self._vc_max_wait)
            response.raise_for_status()
            data = response.json()

            if response.status_code == self._successful_request_code:
                selected_columns = [
                    "datetimeStr",
                    "temp",
                    "humidity",
                    "visibility",
                    "solarradiation",
                    "precip",
                    "wspd",
                    "wdir",
                ]
                df = pd.DataFrame(data["locations"]["Utrecht"]["values"])

                df = df.reindex(columns=selected_columns)
                df = df[selected_columns]
                df.set_index("datetimeStr", inplace=True)

                df.index = pd.to_datetime(df.index)

                df["date"] = df.index.date

                df.set_index("date", inplace=True)
                return df
            else:
                print(f"Failed. Status code: {response.status_code}")
                return pd.DataFrame()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return pd.DataFrame()
        except Exception as err:
            print(f"Other error occurred: {err}")
            return pd.DataFrame()

    def lag_data(self) -> pd.DataFrame:
        """
        Lag the air quality and weather data into a single row.

        :return: DataFrame with lagged data in a single row.
        """
        air_data = self.get_luchtmeet_data()
        weather_data = self.get_vc_data()

        print(air_data)
        print(weather_data)

        df = pd.merge(air_data, weather_data, on="date")

        # Need to reindex for model
        df = df.reindex(
            columns=[
                "PM25",
                "PM10",
                "O3",
                "NO2",
                "temp",
                "humidity",
                "visibility",
                "solarradiation",
                "precip",
                "wspd",
                "wdir",
            ]
        )

        flattened = df.to_numpy().flatten()

        new_column_names = []
        for day_offset in reversed(range(len(df))):
            for col in df.columns:
                new_column_names.append(f"{col} - day {day_offset}")

        lagged_df = pd.DataFrame([flattened], columns=new_column_names)

        lagged_df.insert(0, "date", df.index[-1].strftime("%m/%d/%Y"))

        lagged_df.set_index("date", inplace=True)
        return lagged_df


if __name__ == "__main__":
    caller = APICaller()
    print(caller.lag_data())
