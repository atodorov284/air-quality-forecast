from models.air_quality_model import AirQualityModel
from views.admin_view import AdminView
import streamlit as st


class AdminController:
    def __init__(self):
        self.model = AirQualityModel()
        self.view = AdminView()

    def show_dashboard(self):
        # Fetch today's data and the next three days' predictions from the model
        today_data = self.model.get_today_data()
        next_three_days = self.model.next_three_day_predictions()
        # model_metrics = self.model.get_model_metrics()

        # Define WHO guidelines for pollutant levels
        who_guidelines = {
            "Pollutant": ["NO2 (µg/m³)", "O3 (µg/m³)"],
            "WHO Guideline": [self.model.WHO_NO2_LEVEL, self.model.WHO_O3_LEVEL],
        }

        # Define layout: main content on the left and additional information on the right
        col_main, col_right = st.columns([0.7, 0.3])

        # Main content in the left column
        with col_main:
            # Display current data and future predictions
            self.view.show_current_data(today_data, who_guidelines)

            # Display predictions line plot

            self.view.display_predictions_lineplot(next_three_days, who_guidelines)

        # Right column content for additional details or actions
        with col_right:
            st.markdown("### Model Performance")
            # self.view.show_model_performance(model_metrics)

    def welcome_back(self):
        self.view.welcome_back()
