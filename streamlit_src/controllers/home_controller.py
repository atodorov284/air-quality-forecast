import streamlit as st
import time
from controllers.user_controller import UserController
from controllers.admin_controller import AdminController
from views.home_view import HomeView
import hashlib


class HomeController:
    __ADMIN_PASSWORD_HASH = (
        "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
    )

    def __init__(self):
        self.home_view = HomeView()
        self.user_controller = UserController()
        self.admin_controller = AdminController()
        self._run()

    def _hash_password(self, password):
        """Hash the input password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def _run(self):
        if "is_admin_logged_in" not in st.session_state:
            st.session_state.is_admin_logged_in = False

        # Show the sidebar switch
        switch = self.home_view.show_dashboard_switch()

        if switch == "User Dashboard":
            self.user_controller.show_dashboard()

        elif switch == "Admin Dashboard":
            # Check if the admin is already logged in
            if st.session_state.is_admin_logged_in:
                self.admin_controller.welcome_back()
                self.admin_controller.show_dashboard()
            else:
                password = self.home_view.prompt_admin_password()

                if self._hash_password(password) == self.__ADMIN_PASSWORD_HASH:
                    st.session_state.is_admin_logged_in = True
                    self.admin_controller.show_dashboard()
                else:
                    time.sleep(5)
                    self.user_controller.show_dashboard()
