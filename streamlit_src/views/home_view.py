import streamlit as st


class HomeView:
    """
    The HomeView class manages the layout and logic for the home page,
    including the user and admin dashboard navigation.

    Attributes:
        None

    Methods:
        __init__: Initializes the HomeView class by setting up the home layout.
        set_layout: Sets the layout of the home page.
        show_dashboard_switch: Displays the user and admin dashboard navigation.
        prompt_admin_password: Prompts the user for the admin password.
    """

    def __init__(self) -> None:
        """
        Initializes the HomeView class by setting up the home layout.

        This method is responsible for setting up the Streamlit page configuration and
        creating the sidebar title.
        """
        self.set_layout()

    def set_layout(self) -> None:
        """
        Sets the layout of the home page.

        This method is responsible for setting up the Streamlit page configuration
        and creating the sidebar title.
        """
        st.set_page_config(page_title="Air Quality Monitoring Dashboard", layout="wide")
        st.sidebar.title("Air Quality Monitoring")

    def show_dashboard_switch(self) -> str:
        """
        Displays the user and admin dashboard navigation.

        This method is responsible for displaying the user and admin dashboard navigation
        in the sidebar. It returns the page selected by the user.

        Returns:
            str: The page selected by the user.
        """
        page = st.sidebar.radio("Go to", ["User Dashboard", "Admin Dashboard"])
        return page

    def prompt_admin_password(self) -> str:
        """
        Prompts the user for the admin password.

        This method is responsible for prompting the user for the admin password
        when the user navigates to the admin dashboard. It displays a text input
        field in the sidebar with a placeholder saying "Enter Admin Password:".

        Returns:
            str: The password entered by the user.
        """
        st.sidebar.markdown("### Admin Access Required")
        return st.sidebar.text_input("Enter Admin Password:", type="password")
