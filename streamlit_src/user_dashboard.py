import streamlit as st
import pandas as pd
from datetime import date
import numpy as np

# Constants for WHO guideline levels
WHO_NO2_LEVEL = 25
WHO_O3_LEVEL = 100

# Main function to display user dashboard
def show_user_dashboard():
    # Set layout and sidebar
    set_layout()
    set_sidebar()
    
    # Main content layout
    set_columns()

# Function to set the layout of the app
def set_layout():
    st.set_page_config(page_title="Air Quality Monitoring Dashboard", layout="wide")
    st.sidebar.title("Air Quality Monitoring")

# Function to retrieve current air quality data (replace with actual predictions)
def get_today_data():
    today_data = {
        "NO2 (µg/m³)": np.random.uniform(20, 60),  # Simulated data
        "O3 (µg/m³)": np.random.uniform(50, 120)   # Simulated data
    }
    return today_data

# Function to retrieve predictions for the next three days (replace with actual model predictions)
def next_three_day_predictions():
    next_three_days = pd.DataFrame({
        "Day": ["Day 1", "Day 2", "Day 3"],
        "NO2 (µg/m³)": np.random.uniform(20, 60, 3),
        "O3 (µg/m³)": np.random.uniform(50, 120, 3)
    })
    return next_three_days

# Function to compare current data to WHO guidelines
def compare_to_who(today_data):
    if today_data["NO2 (µg/m³)"] > WHO_NO2_LEVEL:
        st.sidebar.error("⚠️ NO2 levels are above WHO guidelines!")
    else:
        st.sidebar.success("✅ NO2 levels are within safe limits.")

    if today_data["O3 (µg/m³)"] > WHO_O3_LEVEL:
        st.sidebar.error("⚠️ O3 levels are above WHO guidelines!")
    else:
        st.sidebar.success("✅ O3 levels are within safe limits.")

# Sidebar setup to display today's data and WHO guidelines
def set_sidebar():
    today_data = get_today_data()
    st.sidebar.markdown(f"Today's Date: **{date.today().strftime('%B %d, %Y')}**")
    
    # Current Pollutant Concentrations
    st.sidebar.markdown("### Current Pollutant Concentrations")
    today_data_df = pd.DataFrame([today_data])  # Create a DataFrame without index
    st.sidebar.dataframe(today_data_df.style.hide(axis="index"))  # Hide the index
    
    # WHO guideline values
    who_guidelines = {
        "Pollutant": ["NO2 (µg/m³)", "O3 (µg/m³)"],
        "WHO Guideline": [WHO_NO2_LEVEL, WHO_O3_LEVEL]
    }
    st.sidebar.markdown("### WHO Guidelines")
    who_guidelines_df = pd.DataFrame(who_guidelines)
    st.sidebar.dataframe(who_guidelines_df.style.hide(axis="index"))  # Hide the index
    
    # WHO guideline alerts
    compare_to_who(today_data)

# Function to handle the admin dashboard button (placeholder for now)
def start_admin_dashboard():
    st.info("Navigating to admin dashboard...")

# Set right column to include navigation to admin dashboard
def set_right_column(column):
    with column:
        st.button(label="Admin Dashboard",
                  help="Navigate to the admin dashboard.",
                  on_click=start_admin_dashboard,
                  icon="🔧")

# Middle column for future use (e.g., prediction graphs)
def set_middle_column(column):
    with column:
        next_three_days = next_three_day_predictions()
        st.markdown("### Predictions for the Next 3 Days")
        st.line_chart(next_three_days.set_index("Day"))

        st.markdown("### About Air Pollution")
        st.write("""
        **Air pollution** is harmful to human health and the environment. NO2 and O3 are key pollutants monitored
        to assess air quality. The World Health Organization (WHO) provides guidelines on safe levels of these
        pollutants to minimize health risks.
        """)

# Left column for any additional content (e.g., awareness information)
def set_left_column(column):
    pass

# Function to set the column layout for the main dashboard
def set_columns():
    col = st.columns((1, 3, 1), gap="medium")
    set_right_column(col[2])
    set_middle_column(col[1])
    set_left_column(col[0])
