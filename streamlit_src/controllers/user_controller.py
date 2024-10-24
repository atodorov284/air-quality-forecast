from typing import Dict, List, Tuple
import streamlit as st
import numpy as np
from models.air_quality_model import AirQualityModel
from views.user_view import UserView
import os
import pandas as pd
import random
import json
from datetime import date, datetime, timedelta
import plotly.graph_objects as go


class UserController:
    """
    A class to handle the user interface.
    """

    def __init__(self) -> None:
        """
        Initializes the UserController class.
        """
        self._model = AirQualityModel()
        self._view = UserView()

        if self._is_current_data_available():
            self._today_data = self._model.get_today_data()
            self._next_three_days = self._model.next_three_day_predictions()

        self._who_guidelines = {
            "Pollutant": ["NO2 (µg/m³)", "O3 (µg/m³)"],
            "WHO Guideline": [self._model.WHO_NO2_LEVEL, self._model.WHO_O3_LEVEL],
        }

        # Ensure session state for _quiz and _quiz answer tracking
        if "is_first_run" not in st.session_state:
            st.session_state.is_first_run = True
        if "question_choice" not in st.session_state:
            st.session_state.question_choice = np.random.randint(0, 5)

        # Paths for external data
        self._interactions_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "json_interactions/"
        )
        self._facts_path = os.path.join(self._interactions_path, "facts.json")
        self._questions_path = os.path.join(self._interactions_path, "question.json")
        self._awareness_path = os.path.join(self._interactions_path, "awareness.json")

    def show_dashboard(self) -> None:
        """
        Shows the main page of the user interface.
        """
        if self._is_current_data_available():
            self._view.two_columns_layout(0.7, self._raise_awareness, self._quiz)

        if not self._is_current_data_available():
            self._view.data_not_available()
        else:
            self._show_current_data()

            self._display_plots()

            self._display_compare_who()

        self._display_sources()

    def _is_current_data_available(self) -> bool:
        """
        Checks if the current data is available.

        The current data is not available from 00:00 to 04:15.
        This is because the API is queried every 15 minutes, and the
        data is not available for a short period of time before and after
        the new data is fetched.

        :return: True if the current data is available, False otherwise.
        """
        current_time = datetime.now().time()
        start_time = datetime.strptime("00:00", "%H:%M").time()
        end_time = datetime.strptime("04:15", "%H:%M").time()
        if start_time <= current_time <= end_time:
            return False
        return True

    def _display_sources(self) -> None:
        """
        Displays the sources on the main page of the user interface.
        """
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
        self._view.print_sources(sources)

    def _display_compare_who(self) -> None:
        """
        Displays the WHO comparison on the main page of the user interface.
        """
        who_comparisons = self._compare_to_who()
        self._view.compare_to_who(who_comparisons)

    def _display_plots(self) -> None:
        """
        Displays the plots on the main page of the user interface.
        """
        plot_type = self._view.view_option_selection(["Line Plot", "Gauge Plot"])
        if plot_type == "Line Plot":
            line_fig = self._prepare_line_plot()
            self._view.display_predictions_lineplot(line_fig)
        elif plot_type == "Gauge Plot":
            gauge_plots = self._prepare_gauge_plots()
            self._view.display_predictions_gaugeplot(gauge_plots)

    def _show_current_data(self) -> None:
        """
        Shows the current data on the main page of the user interface.
        """
        merged_data_df = self._prepare_data_for_view()
        self._view.show_current_data(merged_data_df)

    def _prepare_data_for_view(self) -> pd.DataFrame:
        """
        Prepares the current data for the view.

        Returns
        -------
        pd.DataFrame
            The current data in a pandas DataFrame.
        """
        merged_data = {
            "Pollutant": ["NO₂ (µg/m³)", "O₃ (µg/m³)"],
            "Current": [
                round(self._today_data["NO2 (µg/m³)"], 2),
                round(self._today_data["O3 (µg/m³)"], 2),
            ],
            "WHO Guideline": self._who_guidelines["WHO Guideline"],
        }
        return pd.DataFrame(merged_data)

    def _raise_awareness(self) -> None:
        """
        Shows the awareness content on the main page of the user interface.
        """
        random_fact, awareness_expanders, health_message = (
            self._prepare_awareness_content()
        )
        self._view.raise_awareness(random_fact, awareness_expanders, health_message)

    def _prepare_awareness_content(
        self,
    ) -> Tuple[str, List[Tuple[str, str]], Dict[str, str]]:
        """
        Prepare awareness content including a random fact, expanders, and health message based on air quality data.

        Returns
        -------
        Tuple[str, List[Tuple[str, str]], Dict[str, str]]
            A tuple containing the random fact, awareness expanders, and health message.
        """
        with open(self._facts_path, "r", encoding="utf-8") as facts_file:
            facts = json.load(facts_file)
            random_fact = random.choice(facts["facts"])

        with open(self._awareness_path, "r", encoding="utf-8") as awareness_file:
            awareness = json.load(awareness_file)
            awareness_expanders = [
                (title, "\n".join(text)) for title, text in awareness.items()
            ]

        health_message = {"message": "", "type": ""}
        if (
            self._today_data["NO2 (µg/m³)"] > self._who_guidelines["WHO Guideline"][0]
            or self._today_data["O3 (µg/m³)"] > self._who_guidelines["WHO Guideline"][1]
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

    def _quiz(self) -> None:
        """
        Show a _quiz question and return the answer and whether the answer was correct.

        Returns
        -------
        tuple
            A tuple containing the answer and a boolean indicating whether the answer was correct.
        """
        question_number = st.session_state.question_choice
        with open(self._questions_path, "r") as questions_file:
            quiz_data = json.load(questions_file)
            question = quiz_data["quiz"][question_number]["question"]
            options = quiz_data["quiz"][question_number]["options"]
            submitted, answer = self._view.quiz(question, options)

        if submitted:
            correct_answer = quiz_data["quiz"][question_number]["answer"]
            if answer == correct_answer:
                self._view.success("Correct answer!")
            else:
                self._view.error(
                    f"Wrong answer! The correct answer was {correct_answer[0].lower() + correct_answer[1:]}."
                )

    def _prepare_line_plot(self) -> go.Figure:
        """
        Prepare a line plot for the next three days' NO2 and O3 levels.

        Returns:
            go.Figure: A plotly figure object.
        """
        tomorrow, day_after_tomorrow, two_days_after_tomorrow = (
            self._get_next_three_days_dates()
        )
        self._next_three_days["Date"] = [
            tomorrow,
            day_after_tomorrow,
            two_days_after_tomorrow,
        ]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=self._next_three_days["Date"],
                y=self._next_three_days["NO2 (µg/m³)"],
                mode="lines+markers+text",  # Add 'text' to display the values on the graph
                name="NO2 (µg/m³)",
                text=[
                    f"{v:.2f} µg/m³" for v in self._next_three_days["NO2 (µg/m³)"]
                ],  # Values displayed at each point
                textposition="top right",  # Set the position of the text
                line=dict(color="blue"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=self._next_three_days["Date"],
                y=self._next_three_days["O3 (µg/m³)"],
                mode="lines+markers+text",
                name="O3",
                text=[
                    f"{v:.2f} µg/m³" for v in self._next_three_days["O3 (µg/m³)"]
                ],  # Values displayed at each point
                textposition="top right",  # Set the position of the text
                line=dict(color="lightblue"),
            )
        )

        # WHO guideline as horizontal dotted lines
        fig.add_hline(
            y=self._who_guidelines["WHO Guideline"][0],
            line_dash="dot",
            line_color="blue",
            annotation_text="WHO NO2 Guideline",
        )
        fig.add_hline(
            y=self._who_guidelines["WHO Guideline"][1],
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

    def _get_next_three_days_dates(self) -> tuple:
        """
        Get the next three days' dates.

        Returns:
            tuple: A tuple of three date objects.
        """
        tomorrow = date.today() + timedelta(days=1)
        day_after_tomorrow = date.today() + timedelta(days=2)
        two_days_after_tomorrow = date.today() + timedelta(days=3)
        return tomorrow, day_after_tomorrow, two_days_after_tomorrow

    def _compare_to_who(self) -> list:
        """
        Compare the current pollutant levels to WHO guidelines.

        Returns:
            list: A list of tuples containing the pollutant name, comparison message, and message type.
        """
        comparisons = []
        for i, pollutant in enumerate(["NO2 (µg/m³)", "O3 (µg/m³)"]):
            if self._today_data[pollutant] > self._who_guidelines["WHO Guideline"][i]:
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

    def _prepare_gauge_plots(self) -> list:
        """
        Prepare gauge plots for the next three days' NO2 and O3 levels.

        Returns:
            list: A list of tuples containing the day index, formatted date, and two plotly figures (for NO2 and O3).
        """
        tomorrow, day_after_tomorrow, two_days_after_tomorrow = (
            self._get_next_three_days_dates()
        )
        self._next_three_days["Date"] = [
            tomorrow,
            day_after_tomorrow,
            two_days_after_tomorrow,
        ]

        gauge_plots = []
        for i, day in enumerate(
            [tomorrow, day_after_tomorrow, two_days_after_tomorrow]
        ):
            no2_value = self._next_three_days["NO2 (µg/m³)"][i]
            o3_value = self._next_three_days["O3 (µg/m³)"][i]
            fig_no2 = self._create_gauge_plot(
                no2_value, self._who_guidelines["WHO Guideline"][0], "NO2 (µg/m³)"
            )
            fig_o3 = self._create_gauge_plot(
                o3_value, self._who_guidelines["WHO Guideline"][1], "O3 (µg/m³)"
            )
            gauge_plots.append((i + 1, day.strftime("%B %d, %Y"), fig_no2, fig_o3))
        return gauge_plots

    def _create_gauge_plot(
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
        color = self._get_color(value, guideline)
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=value,
                title={"text": title},
                gauge={"axis": {"range": [0, guideline]}, "bar": {"color": color}},
            )
        )
        fig.update_layout(height=250, width=250, margin=dict(t=0, b=0, l=0, r=0))
        return fig

    def _get_color(self, value: float, who_limit: float) -> str:
        """
        Calculate a color based on a given pollutant value and WHO guideline.

        Args:
            value (float): The pollutant concentration value.
            who_limit (float): The WHO guideline value for the pollutant.

        Returns:
            str: A hex color code representing the calculated color.
        """

        half_who_limit = who_limit / 2

        if value <= half_who_limit:
            # Green to Bright Yellow (exaggerated contrast)
            return f"rgba(0, {int(255 * value / half_who_limit)}, 0, 1)"  # Gradient from dark green to bright green
        elif value <= who_limit:
            # Yellow to Dark Orange (stronger contrast between safe and danger)
            excess_value = value - half_who_limit
            return f"rgba(255, {int(200 - (200 * excess_value / half_who_limit))}, 0, 1)"  # Gradient from bright yellow to dark orange
        else:
            # Dark Red for exceeding WHO limit
            return "rgba(180, 0, 0, 1)"  # Dark red for dangerous levels
