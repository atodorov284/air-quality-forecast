import streamlit as st

class HomeView:
    
    def __init__(self):
        self.set_layout()
    
    def set_layout(self):
        st.set_page_config(page_title="Air Quality Monitoring Dashboard", layout="wide")
        st.sidebar.title("Air Quality Monitoring")
        
    def show_dashboard_switch(self):
        page = st.sidebar.radio("Go to", ["User Dashboard", "Admin Dashboard"])
        return page
    
    def prompt_admin_password(self):
        st.sidebar.markdown("### Admin Access Required")
        return st.sidebar.text_input("Enter Admin Password:", type="password")