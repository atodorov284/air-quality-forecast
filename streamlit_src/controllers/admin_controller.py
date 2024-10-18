from views.admin_view import AdminView
import streamlit as st
from controllers.user_controller import UserController


class AdminController(UserController):
    def __init__(self):
        super().__init__()
        self._view = AdminView()

    def show_dashboard(self):
        st.markdown("ADMIN DASHBOARD")
        super().show_dashboard()

    def welcome_back(self):
        self._view.welcome_back()
