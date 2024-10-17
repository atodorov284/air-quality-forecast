import requests
import pandas as pd
import os
import sys

SUCCESSFUL_API_CALL_CODE = 200
MAX_WAIT_TIME = 10  # in seconds per API request
AQI_PATH = "data/api_data/previousdaysAQI.csv"
VC_PATH = "data/api_data/previousdaysVC.csv"

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)


def update_data_AQI(api_AQI_url) -> None:
    try:
        response_AQI = requests.get(api_AQI_url, timeout=MAX_WAIT_TIME)
        response_AQI.raise_for_status()  # Raises HTTPError for bad responses
        data_aqi = response_AQI.json()
        if response_AQI.status_code == SUCCESSFUL_API_CALL_CODE:
            selected_columns = ["pm25", "pm10", "o3", "no2"]
            extracted_data = {}
            extracted_data["date"] = data_aqi["data"]["time"]["s"].split()[0]
            for key in selected_columns:
                extracted_data[key] = data_aqi["data"]["iaqi"][key]["v"]
            df = pd.DataFrame(extracted_data, index=[0])
            df.rename(columns={"date": "datetime"}, inplace=True)
            previous_data = pd.read_csv(AQI_PATH)
            last_previous_date = previous_data["datetime"].iloc[-1]
            new_date = df["datetime"].iloc[0]
            if new_date == last_previous_date:
                print("There is no new data. Will only update todays values.")
                previous_data = previous_data.head(2)  # Keep first 2 entries
            else:
                print("Found new data, replacing the oldest data in", AQI_PATH)
                previous_data = previous_data.tail(2)  # Keep last 2 entries
            # Concatenate the new data
            updated_data = pd.concat([previous_data, df], ignore_index=True)
            updated_data.to_csv(AQI_PATH, index=False)
            print("Success! Data saved to", AQI_PATH)
        else:
            print(f"Failed. Status code: {response_AQI.status_code}")
        if data_aqi["status"] != "ok":
            print(
                "There is something wrong with a fetch from the dataset.",
                "Please make sure the data is correct.",
            )
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def update_data_VC() -> None:
    # AQI for yday and the day before
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/"
    url += "rest/services/timeline/utrecht/last7days?unitGroup=metric&"
    url += "include=days&key=3LBMJ7SAH5BCSL5H2DYS5YQ5K&contentType=json"
    VC_get_last_2_days(url)

    # AQI for today
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices"
    url += "/rest/services/timeline/utrecht/today?unitGroup=metric&"
    url += "include=days&key=3LBMJ7SAH5BCSL5H2DYS5YQ5K&contentType=json"
    VC_get_today(url)


def VC_get_last_2_days(api_VC_url) -> None:
    try:
        response_VC = requests.get(api_VC_url, timeout=MAX_WAIT_TIME)
        response_VC.raise_for_status()  # Raises HTTPError for bad responses
        data_vc = response_VC.json()  # change data to JSOn
        if response_VC.status_code == SUCCESSFUL_API_CALL_CODE:
            last_2_days = data_vc["days"][-2:]
            selected_columns = [
                "datetime",
                "temp",
                "humidity",
                "visibility",
                "solarradiation",
                "precip",
                "windspeed",
                "winddir",
            ]

            extracted_data = [
                {key: day[key] for key in selected_columns if key in day}
                for day in last_2_days
            ]
            # print(extracted_data['data'])

            df = pd.DataFrame(extracted_data)
            df.to_csv(VC_PATH, index=False)
            print("Success! Data fetched to", VC_PATH)
        else:
            print(f"Failed. Status code: {response_VC.status_code}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


def VC_get_today(api_VC_url) -> None:
    try:
        response_VC = requests.get(api_VC_url, timeout=MAX_WAIT_TIME)
        response_VC.raise_for_status()  # Raises HTTPError for bad responses
        data_vc = response_VC.json()
        if response_VC.status_code == SUCCESSFUL_API_CALL_CODE:
            last_2_days = data_vc["days"]
            selected_columns = [
                "datetime",
                "temp",
                "humidity",
                "visibility",
                "solarradiation",
                "precip",
                "windspeed",
                "winddir",
            ]

            extracted_data = [
                {key: day[key] for key in selected_columns if key in day}
                for day in last_2_days
            ]
            df = pd.DataFrame(extracted_data)
            df.to_csv(VC_PATH, mode="a", header=False, index=False)
            print("Success! Data appended to", VC_PATH)
        else:
            print(f"Failed. Status code: {response_VC.status_code}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")


if __name__ == "__main__":
    url = "https://api.waqi.info/feed/@6332/"
    url += "?token=5f47b9d38f81c06ea16622bb3a9ff483a7a49236"
    api_AQI_url = (
        url
    )
    update_data_AQI(api_AQI_url)
    update_data_VC()
