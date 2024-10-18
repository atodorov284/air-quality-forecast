# views/user_view.py
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import json
import random
import os

FACTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "facts.json")

QUESTIONS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "question.json"
)


class UserView:
    def show_current_data(self, today_data, who_guidelines):
        st.sidebar.markdown(f"Today's Date: **{date.today().strftime('%B %d, %Y')}**")

        # Merge today_data and who_guidelines into one DataFrame
        merged_data = {
            "Pollutant": ["NO2 (µg/m³)", "O3 (µg/m³)"],
            "Current Concentration": [
                today_data["NO2 (µg/m³)"],
                today_data["O3 (µg/m³)"],
            ],
            "WHO Guideline": [
                who_guidelines["WHO Guideline"][0],  # NO2 guideline
                who_guidelines["WHO Guideline"][1],  # O3 guideline
            ],
        }

        merged_data_df = pd.DataFrame(merged_data)

        # Use Streamlit column configuration with hide_index=True
        st.sidebar.markdown("### Current Pollutant Concentrations and WHO Guidelines")
        st.sidebar.dataframe(merged_data_df, hide_index=True)

    def get_next_three_days_dates(self):
        """
        Returns the next three days' dates in datetime format as a tuple.

        :return: tuple of three datetime objects, representing tomorrow, day after tomorrow, and two days after tomorrow.
        """
        today = datetime.now()  # Get the current date and time
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)
        two_days_after_tomorrow = today + timedelta(days=3)
        return tomorrow, day_after_tomorrow, two_days_after_tomorrow

    def display_predictions_lineplot(self, next_three_days, who_guidelines):
        tomorrow, day_after_tomorrow, two_days_after_tomorrow = (
            self.get_next_three_days_dates()
        )

        # Update the dataframe with actual dates in datetime format
        next_three_days["Date"] = [
            tomorrow,
            day_after_tomorrow,
            two_days_after_tomorrow,
        ]

        # Create the plot using Plotly for more customization
        fig = go.Figure()

        # Add NO2 line
        fig.add_trace(
            go.Scatter(
                x=next_three_days["Date"],
                y=next_three_days["NO2 (µg/m³)"],
                mode="lines+markers+text",
                name="NO2 (µg/m³)",
                text=[f"{v:.2f} µg/m³" for v in next_three_days["NO2 (µg/m³)"]],
                textposition="top right",
                line=dict(color="blue"),
            )
        )

        # Add O3 line
        fig.add_trace(
            go.Scatter(
                x=next_three_days["Date"],
                y=next_three_days["O3 (µg/m³)"],
                mode="lines+markers+text",
                name="O3 (µg/m³)",
                text=[f"{v:.2f} µg/m³" for v in next_three_days["O3 (µg/m³)"]],
                textposition="top right",
                line=dict(color="lightblue"),
            )
        )

        # Add WHO guideline as horizontal dotted lines
        fig.add_hline(
            y=who_guidelines["WHO Guideline"][0],
            line_dash="dot",
            line_color="blue",
            annotation_text="WHO NO2 Guideline",
            annotation_position="bottom right",
        )
        fig.add_hline(
            y=who_guidelines["WHO Guideline"][1],
            line_dash="dot",
            line_color="lightblue",
            annotation_text="WHO O3 Guideline",
            annotation_position="bottom right",
        )

        # Update layout for better visuals
        fig.update_layout(
            title="Predictions for the Next 3 Days with WHO Guidelines",
            xaxis_title="Date",
            yaxis_title="Pollutant Concentration (µg/m³)",
            hovermode="x unified",
        )

        # Display the plot in Streamlit
        st.plotly_chart(fig)

    def get_color(self, value, who_limit):
        half_who_limit = who_limit / 2

        if value <= half_who_limit:
            # Green -> Yellow gradient
            return f"rgba({int(255 * value / half_who_limit)}, 255, 0, 1)"  # Gradient from green to yellow
        elif value <= who_limit:
            # Yellow -> Red gradient
            excess_value = value - half_who_limit
            return f"rgba(255, {int(255 - (255 * excess_value / half_who_limit))}, 0, 1)"  # Gradient from yellow to red
        else:
            # Beyond the WHO limit, fully red
            return "rgba(255, 0, 0, 1)"  # Fully red

    def display_predictions_gaugeplot(self, next_three_days, who_guidelines):
        st.markdown("### Predictions for the Next 3 Days")
        # Convert date to datetime and calculate future dates
        tomorrow, day_after_tomorrow, two_days_after_tomorrow = (
            self.get_next_three_days_dates()
        )

        # Update the dataframe with actual dates in datetime format
        next_three_days["Date"] = [
            tomorrow,
            day_after_tomorrow,
            two_days_after_tomorrow,
        ]
        for i in range(3):
            formatted_date = next_three_days["Date"][i].strftime("%B %d, %Y")

            st.markdown(f"#### Day {i+1}: {formatted_date}")

            # use multiple columns for centering
            _, col1, _, col2, _ = st.columns([0.2, 1, 0.2, 1, 0.2], gap="small")

            # NO2 Gauge
            with col1:
                # Get color based on NO2 value
                no2_value = next_three_days["NO2 (µg/m³)"][i]
                no2_color = self.get_color(
                    no2_value, who_guidelines["WHO Guideline"][0]
                )
                fig_no2 = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=next_three_days["NO2 (µg/m³)"][i],
                        title={"text": "NO2 (µg/m³)"},
                        gauge={
                            "axis": {
                                "range": [
                                    0,
                                    2 * who_guidelines["WHO Guideline"][0],
                                ]
                            },
                            "bar": {"color": no2_color},
                        },
                        domain={"x": [0, 1], "y": [0, 1]},  # Controls size
                    )
                )
                fig_no2.update_layout(
                    height=250, width=250, margin=dict(t=0, b=0, l=0, r=0)
                )
                st.plotly_chart(fig_no2)

            # O3 Gauge
            with col2:
                o3_value = next_three_days["O3 (µg/m³)"][i]
                o3_color = self.get_color(o3_value, who_guidelines["WHO Guideline"][1])
                fig_o3 = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=next_three_days["O3 (µg/m³)"][i],
                        title={"text": "O3 (µg/m³)"},
                        gauge={
                            "axis": {
                                "range": [
                                    0,
                                    1.5 * who_guidelines["WHO Guideline"][1],
                                ]
                            },
                            "bar": {"color": o3_color},
                        },
                        domain={"x": [0, 1], "y": [0, 1]},  # Controls size
                    )
                )
                fig_o3.update_layout(
                    height=250, width=250, margin=dict(t=0, b=0, l=0, r=0)
                )
                st.plotly_chart(fig_o3)

    def view_option_selection(self) -> str:
        st.markdown("### Visualizing Air Quality Predictions")
        plot_type = st.selectbox("", ("Line Plot", "Gauge Plot"))
        return plot_type

    def compare_to_who(self, today_data, no2_level, o3_level):
        if today_data["NO2 (µg/m³)"] > no2_level:
            st.sidebar.error("⚠️ NO2 levels are above WHO guidelines!")
        else:
            st.sidebar.success("✅ NO2 levels are within safe limits.")

        if today_data["O3 (µg/m³)"] > o3_level:
            st.sidebar.error("⚠️ O3 levels are above WHO guidelines!")
        else:
            st.sidebar.success("✅ O3 levels are within safe limits.")

    def raise_awareness(self, today_data, who_guidelines):
        st.markdown("### Air Quality Awareness")

        # Load facts from the JSON file
        with open(FACTS_PATH, "r") as f:
            facts = json.load(f)["facts"]

        # Randomly select a fact from the list
        random_fact = random.choice(facts)

        # Create expandable sections for key pollutant information
        with st.expander("🌍 What is Air Pollution?"):
            st.write("""
            **Air pollution** is a serious concern that affects the environment and public health.
            High levels of pollutants, such as ozone (O₃) and nitrogen dioxide (NO₂), can lead to
            respiratory problems, aggravate pre-existing conditions like asthma, and contribute to
            cardiovascular diseases.
            """)

        with st.expander("⚠️ Why O₃ and NO₂ Matter"):
            st.write("""
            **Ozone (O₃):** Formed by chemical reactions in the atmosphere, particularly on sunny days.
            High levels can cause chest pain, coughing, throat irritation, and airway inflammation.

            **Nitrogen Dioxide (NO₂):** Mostly emitted from vehicles and industrial activities, this can cause
            irritation of the respiratory system and decrease lung function, especially during long-term exposure.
            """)

        self.add_spaces(num_lines=3)

        # Display the random fact for user awareness
        st.markdown("### Did You Know?")
        st.info(random_fact)  # Display the random fact in an info box

        self.add_spaces(num_lines=3)

        # Show real-time suggestions for high pollution days
        st.markdown("### Health Recommendations Based on Current Levels")
        if (
            today_data["NO2 (µg/m³)"] > who_guidelines["WHO Guideline"][0]
            or today_data["O3 (µg/m³)"] > who_guidelines["WHO Guideline"][1]
        ):
            st.error(
                "🚨 High pollution levels today. Avoid outdoor activities if possible, especially for vulnerable groups."
            )
        else:
            st.success(
                "✅ Air quality is within safe limits today. Enjoy your outdoor activities!"
            )

        self.add_spaces(num_lines=3)

    def print_sources(self):
        # Provide user links to external resources or reports
        st.markdown("### Learn More")
        st.markdown(
            "[WHO Air Quality Guidelines](https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health)"
        )
        st.markdown(
            "[Air Pollution Facts](https://www.un.org/sustainabledevelopment/air-pollution/)"
        )

    def quiz(self, question_nr=0):
        with open(QUESTIONS_PATH, "r") as f:
            quiz_data = json.load(f)
        # Access the quiz questions
        questions = quiz_data["quiz"]
        random_question = questions[question_nr]

        # Add a simple quiz to engage the user
        st.markdown("### Quick Quiz: How Much Do You Know About Air Pollution?")
        with st.form(key="quiz_form"):
            # Display the first question and options
            st.write(random_question["question"])
            options = random_question["options"]
            answer = st.radio("Choose an option:", options)
            submitted = st.form_submit_button("Submit Answer")

            if submitted:
                if answer == random_question["answer"]:
                    st.success("Correct!")
                else:
                    st.error(
                        "Incorrect. The correct answer is: " + random_question["answer"]
                    )

    def raise_awareness_and_quiz(self, today_data, who_guidelines, question_nr=0):
        # Create two columns: main column for awareness and right column for the quiz
        col_main, col_right = st.columns(
            [0.7, 0.3], gap="large"
        )  # 70% for awareness, 30% for quiz

        # Left column: Raise awareness
        with col_main:
            self.raise_awareness(today_data, who_guidelines)

        # Right column: Quiz
        with col_right:
            self.quiz(question_nr)

    def add_spaces(self, num_lines=1):
        """Add vertical space between sections by adding empty lines.

        Args:
            num_lines (int): Number of blank lines to add. Default is 1.
        """
        for _ in range(num_lines):
            st.write("")  # This adds a blank line to create space
