import streamlit as st

def ask_for_admin_password():
    password = st.text_input("Enter admin password", type="password")
    if password == "admin":
        return True
    else:
        return False

def start_admin_dashboard():
    if ask_for_admin_password():
        st.title("Admin Dashboard")
    else:
        st.error("Invalid password. Please try again.")