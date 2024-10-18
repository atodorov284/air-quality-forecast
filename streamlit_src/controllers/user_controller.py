from typing import Callable, Dict, List, Tuple
import streamlit as st
import numpy as np
from models.air_quality_model import AirQualityModel
from views.user_view import UserView
import os
import pandas as pd
import random
import json
from datetime import date, timedelta
import plotly.graph_objects as go


class UserController:
    """
    A class to handle the user interface.
    """

    def __init__(self) -> None:
        """
        Initializes the UserController class.
        """
        self.model = AirQualityModel()
        self.view = UserView()
        self.today_data = self.model.get_today_data()
        self.next_three_days = self.model.next_three_day_predictions()

        self.who_guidelines = {
            "Pollutant": ["NO2 (µg/m³)", "O3 (µg/m³)"],
            "WHO Guideline": [self.model.WHO_NO2_LEVEL, self.model.WHO_O3_LEVEL],
        }

        # Ensure session state for quiz and quiz answer tracking
        if "is_first_run" not in st.session_state:
            st.session_state.is_first_run = True
        if "question_choice" not in st.session_state:
            st.session_state.question_choice = np.random.randint(0, 5)

        # Paths for external data
        self.interactions_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "json_interactions/"
        )
        self.facts_path = os.path.join(self.interactions_path, "facts.json")
        self.questions_path = os.path.join(self.interactions_path, "question.json")
        self.awareness_path = os.path.join(self.interactions_path, "awareness.json")

    def show_dashboard(self) -> None:
        """
        Shows the main page of the user interface.
        """
        self.show_current_data()

        self.two_columns_layout(0.7, self.raise_awareness, self.quiz)

        # Plot selection and rendering
        plot_type = self.view.view_option_selection(["Line Plot", "Gauge Plot"])
        if plot_type == "Line Plot":
            line_fig = self.prepare_line_plot()
            self.view.display_predictions_lineplot(line_fig)
        elif plot_type == "Gauge Plot":
            gauge_plots = self.prepare_gauge_plots()
            self.view.display_predictions_gaugeplot(gauge_plots)

        # WHO comparison
        who_comparisons = self.compare_to_who()
        self.view.compare_to_who(who_comparisons)

        # Sources
        sources = [
            (
                "WHO Air Quality Guidelines",
                "https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health",
            ),
            (
                "Air Pollution Facts",
                "https://www.un.org/sustainabledevelopment/air-pollution/",
            ),
        ]
        self.view.print_sources(sources)

    def show_current_data(self) -> None:
        """
        Shows the current data on the main page of the user interface.
        """
        merged_data_df = self.prepare_data_for_view()
        self.view.show_current_data(merged_data_df)

    def prepare_data_for_view(self) -> pd.DataFrame:
        """
        Prepares the current data for the view.

        Returns
        -------
        pd.DataFrame
            The current data in a pandas DataFrame.
        """
        merged_data = {
            "Pollutant": ["NO2 (µg/m³)", "O3 (µg/m³)"],
            "Current Concentration": [
                self.today_data["NO2 (µg/m³)"],
                self.today_data["O3 (µg/m³)"],
            ],
            "WHO Guideline": self.who_guidelines["WHO Guideline"],
        }
        return pd.DataFrame(merged_data)

    def raise_awareness(self) -> None:
        """
        Shows the awareness content on the main page of the user interface.
        """
        random_fact, awareness_expanders, health_message = (
            self.prepare_awareness_content()
        )
        self.view.raise_awareness(random_fact, awareness_expanders, health_message)

    def prepare_awareness_content(
        self,
    ) -> Tuple[str, List[Tuple[str, str]], Dict[str, str]]:
        """
        Prepare awareness content including a random fact, expanders, and health message based on air quality data.

        Returns
        -------
        Tuple[str, List[Tuple[str, str]], Dict[str, str]]
            A tuple containing the random fact, awareness expanders, and health message.
        """
        with open(self.facts_path, "r") as facts_file:
            facts = json.load(facts_file)
            random_fact = random.choice(facts["facts"])

        with open(self.awareness_path, "r") as awareness_file:
            awareness = json.load(awareness_file)
            awareness_expanders = [
                (title, "\n".join(text)) for title, text in awareness.items()
            ]

        health_message = {"message": "", "type": ""}
        if (
            self.today_data["NO2 (µg/m³)"] > self.who_guidelines["WHO Guideline"][0]
            or self.today_data["O3 (µg/m³)"] > self.who_guidelines["WHO Guideline"][1]
        ):
            health_message["message"] = (
                "🚨 High pollution levels today. Avoid outdoor activities if possible, especially for vulnerable groups."
            )
            health_message["type"] = "error"
        else:
            health_message["message"] = (
                "✅ Air quality is within safe limits today. Enjoy your outdoor activities!"
            )
            health_message["type"] = "success"

        return random_fact, awareness_expanders, health_message

    def quiz(self) -> None:
        """
        Show a quiz question and return the answer and whether the answer was correct.

        Returns
        -------
        tuple
            A tuple containing the answer and a boolean indicating whether the answer was correct.
        """
        question_number = st.session_state.question_choice
        with open(self.questions_path, "r") as questions_file:
            quiz_data = json.load(questions_file)
            question = quiz_data["quiz"][question_number]["question"]
            options = quiz_data["quiz"][question_number]["options"]
            submitted, answer = self.view.quiz(question, options)

        if submitted:
            correct_answer = quiz_data["quiz"][question_number]["answer"]
            if answer == correct_answer:
                self.view.success("Correct answer!")
            else:
                self.view.error(
                    f"Wrong answer! The correct answer was {correct_answer[0].lower() + correct_answer[1:]}."
                )

    def two_columns_layout(
        self, ratio: float, left_function: Callable, right_function: Callable
    ) -> None:
        """
        Divide the page into two columns and call the left and right functions within them.

        Parameters
        ----------
        ratio : float
            The ratio of the left to the right column.
        left_function : Callable
            The function to be called in the left column.
        right_function : Callable
            The function to be called in the right column.
        """
        left, right = st.columns([ratio, 1 - ratio], gap="large")

        with left:
            left_function()

        with right:
            right_function()

    def prepare_line_plot(self) -> go.Figure:
        """
        Prepare a line plot for the next three days' NO2 and O3 levels.

        Returns:
            go.Figure: A plotly figure object.
        """
        tomorrow, day_after_tomorrow, two_days_after_tomorrow = (
            self.get_next_three_days_dates()
        )
        self.next_three_days["Date"] = [
            tomorrow,
            day_after_tomorrow,
            two_days_after_tomorrow,
        ]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=self.next_three_days["Date"],
                y=self.next_three_days["NO2 (µg/m³)"],
                mode="lines+markers+text",
                name="NO2",
                line=dict(color="blue"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=self.next_three_days["Date"],
                y=self.next_three_days["O3 (µg/m³)"],
                mode="lines+markers+text",
                name="O3",
                line=dict(color="lightblue"),
            )
        )

        # WHO guideline as horizontal dotted lines
        fig.add_hline(
            y=self.who_guidelines["WHO Guideline"][0],
            line_dash="dot",
            line_color="blue",
            annotation_text="WHO NO2 Guideline",
        )
        fig.add_hline(
            y=self.who_guidelines["WHO Guideline"][1],
            line_dash="dot",
            line_color="lightblue",
            annotation_text="WHO O3 Guideline",
        )

        fig.update_layout(
            title="Predictions for the Next 3 Days",
            xaxis_title="Date",
            yaxis_title="Pollutant Concentration (µg/m³)",
            hovermode="x unified",
        )
        return fig

    def get_next_three_days_dates(self) -> tuple:
        """
        Get the next three days' dates.

        Returns:
            tuple: A tuple of three date objects.
        """
        tomorrow = date.today() + timedelta(days=1)
        day_after_tomorrow = date.today() + timedelta(days=2)
        two_days_after_tomorrow = date.today() + timedelta(days=3)
        return tomorrow, day_after_tomorrow, two_days_after_tomorrow

    def compare_to_who(self) -> list:
        """
        Compare the current pollutant levels to WHO guidelines.

        Returns:
            list: A list of tuples containing the pollutant name, comparison message, and message type.
        """
        comparisons = []
        for i, pollutant in enumerate(["NO2 (µg/m³)", "O3 (µg/m³)"]):
            if self.today_data[pollutant] > self.who_guidelines["WHO Guideline"][i]:
                comparisons.append(
                    (
                        pollutant,
                        f"🚨 {pollutant} levels exceed WHO guidelines!",
                        "error",
                    )
                )
            else:
                comparisons.append(
                    (
                        pollutant,
                        f"✅ {pollutant} levels are within safe limits",
                        "success",
                    )
                )
        return comparisons

    def prepare_gauge_plots(self) -> list:
        """
        Prepare gauge plots for the next three days' NO2 and O3 levels.

        Returns:
            list: A list of tuples containing the day index, formatted date, and two plotly figures (for NO2 and O3).
        """
        tomorrow, day_after_tomorrow, two_days_after_tomorrow = (
            self.get_next_three_days_dates()
        )
        self.next_three_days["Date"] = [
            tomorrow,
            day_after_tomorrow,
            two_days_after_tomorrow,
        ]

        gauge_plots = []
        for i, day in enumerate(
            [tomorrow, day_after_tomorrow, two_days_after_tomorrow]
        ):
            no2_value = self.next_three_days["NO2 (µg/m³)"][i]
            o3_value = self.next_three_days["O3 (µg/m³)"][i]
            fig_no2 = self.create_gauge_plot(
                no2_value, self.who_guidelines["WHO Guideline"][0], "NO2 (µg/m³)"
            )
            fig_o3 = self.create_gauge_plot(
                o3_value, self.who_guidelines["WHO Guideline"][1], "O3 (µg/m³)"
            )
            gauge_plots.append((i + 1, day.strftime("%B %d, %Y"), fig_no2, fig_o3))
        return gauge_plots

    def create_gauge_plot(
        self, value: float, guideline: float, title: str
    ) -> go.Figure:
        """
        Create a gauge plot for a given pollutant value and guideline.

        Args:
            value (float): The pollutant concentration value.
            guideline (float): The WHO guideline value for the pollutant.
            title (str): The title of the gauge plot.

        Returns:
            go.Figure: A Plotly figure representing the gauge plot.
        """
        color = "green" if value <= guideline else "red"
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=value,
                title={"text": title},
                gauge={"axis": {"range": [0, 2 * guideline]}, "bar": {"color": color}},
            )
        )
        fig.update_layout(height=250, width=250, margin=dict(t=0, b=0, l=0, r=0))
        return fig
