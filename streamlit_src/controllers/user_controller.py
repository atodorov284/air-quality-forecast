import streamlit as st
import numpy as np
from models.air_quality_model import AirQualityModel
from views.user_view import UserView


class UserController:
    def __init__(self):
        self.model = AirQualityModel()
        self.view = UserView()

        # Ensure session state for first run and quiz question
        if "is_first_run" not in st.session_state:
            st.session_state.is_first_run = True

        if "question_choice" not in st.session_state:
            st.session_state.question_choice = np.random.randint(0, 5)

    def show_dashboard(self):
        # Get today's data and predictions
        today_data = self.model.get_today_data()
        next_three_days = self.model.next_three_day_predictions()

        # WHO Guidelines
        who_guidelines = {
            "Pollutant": ["NO2 (µg/m³)", "O3 (µg/m³)"],
            "WHO Guideline": [self.model.WHO_NO2_LEVEL, self.model.WHO_O3_LEVEL],
        }

        # Display current data and predictions
        self.view.show_current_data(today_data, who_guidelines)

        # Use session state to avoid resetting the quiz question after each interaction
        if st.session_state.is_first_run:
            st.session_state.question_choice = np.random.randint(0, 5)
            st.session_state.is_first_run = False

        # Raise awareness and display the quiz with the saved question number
        self.view.raise_awareness_and_quiz(
            today_data, who_guidelines, question_nr=st.session_state.question_choice
        )

        # Plot selection
        plot_type = self.view.view_option_selection()
        if plot_type == "Line Plot":
            self.view.display_predictions_lineplot(next_three_days, who_guidelines)
        elif plot_type == "Gauge Plot":
            self.view.display_predictions_gaugeplot(next_three_days, who_guidelines)

        # Compare to WHO guidelines
        self.view.compare_to_who(
            today_data, self.model.WHO_NO2_LEVEL, self.model.WHO_O3_LEVEL
        )

        # Print sources
        self.view.print_sources()
