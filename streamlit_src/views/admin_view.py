# views/user_view.py
from typing import Dict
import streamlit as st
from views.user_view import UserView
import pandas as pd


class AdminView(UserView):
    """
    A class to handle all user interface elements for the admin.

    """

    def __init__(self) -> None:
        """
        Initializes the AdminView class.
        """
        super().__init__()

    def welcome_back(self) -> None:
        """
        Welcomes the user back to the admin page.
        """
        st.empty()
        st.success("Welcome back!")
        st.empty()

    def upload_dataset(self) -> pd.DataFrame:
        """
        Uploads a dataset for prediction.

        :return: A pandas DataFrame containing the uploaded dataset.
        """
        return st.file_uploader("Choose a CSV file", type=["csv"])

    def upload_instructions(self) -> None:
        """
        Displays instructions for uploading a dataset.
        """
        st.subheader("Upload Dataset for Prediction")
        st.markdown(
            "Make your own custom predictions using a dataset. Note that the dataset has to adhere to the following:"
        )
        st.markdown("""
    - **Normalization**: The data must be **unnormalized**.
    - **Units**: All measurements should be in **micrograms/m³**.
    - **Data Structure**: The dataset must contain a total of **33 columns** with the following order:
        - **Optional**: `date`
        - `PM25` (today)
        - `PM10` (today)
        - `O3` (today)
        - `NO2` (today)
        - `Temperature` (today)
        - `Humidity` (today)
        - `Visibility` (today)
        - `Solar Radiation` (today)
        - `Precipitation` (today)
        - `Wind Speed` (today)
        - `Wind Direction` (today)
        - `PM25` (yesterday)
        - `PM10` (yesterday)
        - `O3` (yesterday)
        - `NO2` (yesterday)
        - `Temperature` (yesterday)
        - `Humidity` (yesterday)
        - `Visibility` (yesterday)
        - `Solar Radiation` (yesterday)
        - `Precipitation` (yesterday)
        - `Wind Speed` (yesterday)
        - `Wind Direction` (yesterday)
        - `PM25` (two days ago)
        - `PM10` (two days ago)
        - `O3` (two days ago)
        - `NO2` (two days ago)
        - `Temperature` (two days ago)
        - `Humidity` (two days ago)
        - `Visibility` (two days ago)
        - `Solar Radiation` (two days ago)
        - `Precipitation` (two days ago)
        - `Wind Speed` (two days ago)
        - `Wind Direction` (two days ago)
    """)

    def download_button(self, label: str, data: str, file_name: str) -> None:
        """
        Creates a download button for the user to download the data.

        :param label: The label of the button.
        :param data: The data to be downloaded.
        :param file_name: The name of the file to be downloaded.
        """
        st.download_button(
            label=label,
            data=data,
            file_name=file_name,
            mime="csv",
        )

    def confirm_checks(self, checks: Dict[str, bool]) -> bool:
        """
        Displays a confirmation checkbox for the user to confirm the requirements.

        :param checks: A dictionary of requirements and their current values.
        :return: True if all the requirements are confirmed, False otherwise.
        """
        st.markdown("Select the requirements that have been checked:")
        for requirement in checks.keys():
            checks[requirement] = st.checkbox(requirement, value=checks[requirement])

        return all(checks.values())

    def display_datatable(self, data: pd.DataFrame, message: str) -> None:
        """
        Displays a table of the data.

        :param data: The data to be displayed.
        :param message: The message to be displayed above the table.
        """
        st.markdown(message)
        st.dataframe(data.head())
