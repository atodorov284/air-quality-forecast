import streamlit as st
import time
from controllers.user_controller import UserController
from controllers.admin_controller import AdminController
from views.home_view import HomeView
import hashlib


class HomeController:
    """
    Handles the logic for the home page, including switching between user and admin views.

    The home page is the main entry point for the Streamlit application.
    It contains a text input for the admin password, which is hashed and compared to the stored hash.
    If the password is correct, the user is logged in as an admin and the admin view is displayed.
    Otherwise, the user view is displayed.
    """

    # This needs to be hidden as an env variable but we couldn't manage with HuggingFace yet, severe security issue
    __ADMIN_PASSWORD_HASH = (
        "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
    )

    def __init__(self) -> None:
        """
        Initializes the HomeController class by setting up the home view, user controller,
        and admin controller. Also triggers the _run method to start the application.
        """
        self.home_view = HomeView()
        self.user_controller = UserController()
        self.admin_controller = AdminController()
        self._run()

    def _hash_password(self, password: str) -> str:
        """Hash the input password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _run(self) -> None:
        """
        Runs the application logic for the home page.

        This method is responsible for rendering the home page and
        handling the user's choice of whether to view the user dashboard
        or admin dashboard. If the user chooses to view the admin dashboard,
        the user is prompted to enter the admin password. If the password
        is valid, the user is logged in as an admin and the admin dashboard
        is displayed. If the password is invalid, the user is logged out and
        the user dashboard is displayed.
        """
        if "is_admin_logged_in" not in st.session_state:
            st.session_state.is_admin_logged_in = False

        # Show the sidebar switch
        switch = self.home_view.show_dashboard_switch()

        if switch == "User Dashboard":
            self.user_controller.show_dashboard()

        elif switch == "Admin Dashboard":
            # Check if the admin is already logged in
            if st.session_state.is_admin_logged_in:
                self.admin_controller.show_dashboard()
            else:
                password = self.home_view.prompt_admin_password()

                if self._hash_password(password) == self.__ADMIN_PASSWORD_HASH:
                    st.session_state.is_admin_logged_in = True
                    self.admin_controller.show_dashboard()
                else:
                    time.sleep(5)
                    self.user_controller.show_dashboard()
