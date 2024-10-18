import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime


class UserView:
    """
    A class to handle all user interface elements.
    """

    def show_current_data(self, merged_data_df: pd.DataFrame) -> None:
        """
        Show the current pollutant concentrations along with WHO guidelines.

        Args:
            merged_data_df (pd.DataFrame): A pandas DataFrame containing the current pollutant concentrations and WHO guidelines.
        """
        st.sidebar.markdown(
            f"Today's Date: **{datetime.date.today().strftime('%B %d, %Y')}**"
        )
        st.sidebar.markdown("### Current Pollutant Concentrations and WHO Guidelines")
        st.sidebar.dataframe(merged_data_df, hide_index=True)

    def success(self, message: str) -> None:
        """
        Show a success message.

        Args:
            message (str): The message to be displayed.
        """
        st.success(message)

    def error(self, message: str) -> None:
        """
        Show an error message.

        Args:
            message (str): The message to be displayed.
        """
        st.error(message)

    def display_predictions_lineplot(self, fig: go.Figure) -> None:
        """
        Show a line plot of the predictions.

        Args:
            fig (go.Figure): The plotly figure to be displayed.
        """
        st.plotly_chart(fig)

    def display_predictions_gaugeplot(self, gauge_plots: list) -> None:
        """
        Show a gauge plot of the predictions.

        Args:
            gauge_plots (list): A list of tuples containing the day, formatted date, and two plotly figures (for NO2 and O3).
        """
        for day, formatted_date, fig_no2, fig_o3 in gauge_plots:
            st.markdown(f"#### Day {day}: {formatted_date}")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.plotly_chart(fig_no2)
            with col2:
                st.plotly_chart(fig_o3)

    def view_option_selection(self, plot_type: list) -> str:
        """
        Ask the user to select a plot type.

        Args:
            plot_type (list): A list of strings containing the options to be displayed.

        Returns:
            str: The selected option.
        """
        st.markdown("### Visualizing Air Quality Predictions")
        return st.selectbox("", plot_type)

    def compare_to_who(self, warnings: list) -> None:
        """
        Compare the current pollutant concentrations with WHO guidelines and display the results.

        Args:
            warnings (list): A list of tuples containing the pollutant, message, and level (error or success) of the warning.
        """
        for pollutant, message, level in warnings:
            if level == "error":
                st.sidebar.error(message)
            elif level == "success":
                st.sidebar.success(message)

    def raise_awareness(
        self, random_fact: str, awareness_expanders: list, health_message: dict
    ) -> None:
        """
        Raise awareness about air quality issues and provide health recommendations.

        Args:
            random_fact (str): A random fact about air quality.
            awareness_expanders (list): A list of tuples containing the title and content of the expanders.
            health_message (dict): A dictionary containing the health recommendation message and type (error or success).
        """
        st.markdown("### Air Quality Awareness")
        # Awareness sections
        for expander_title, expander_content in awareness_expanders:
            with st.expander(expander_title):
                st.write(expander_content)

        # Fact section
        st.markdown("### Did You Know?")
        st.info(random_fact)

        # Health recommendation section
        st.markdown("### Health Recommendations Based on Current Levels")
        if health_message["type"] == "error":
            st.error(health_message["message"])
        else:
            st.success(health_message["message"])

    def quiz(self, question: str, options: list) -> tuple:
        """
        Ask a quiz question and return the answer and whether the answer was correct.

        Args:
            question (str): The question to be asked.
            options (list): A list of strings containing the options.

        Returns:
            tuple: A tuple containing the answer and a boolean indicating whether the answer was correct.
        """
        st.markdown("### Quick Quiz: How Much Do You Know About Air Pollution?")
        with st.form(key="quiz_form"):
            st.write(question)
            answer = st.radio("Choose an option:", options)
            submit_button = st.form_submit_button("Submit Answer")
        return submit_button, answer

    def print_sources(self, sources: list) -> None:
        """
        Print the sources used in the application.

        Args:
            sources (list): A list of tuples containing the source text and URL.
        """
        st.markdown("### Learn More")
        for source_text, source_url in sources:
            st.markdown(f"[{source_text}]({source_url})")
