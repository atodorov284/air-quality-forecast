# views/user_view.py
import streamlit as st
from views.user_view import UserView


class AdminView(UserView):
    def __init__(self):
        super().__init__()

    def welcome_back(self):
        st.empty()
        st.success("Welcome back!")
        st.empty()
