# views/user_view.py
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import time
import plotly.graph_objects as go


class AdminView:
    def show_current_data(self, today_data, who_guidelines):
        st.sidebar.markdown(f"Today's Date: **{datetime.now().strftime('%B %d, %Y')}**")

        # Display today's pollutant data along with WHO guidelines
        merged_data = {
            "Pollutant": ["NO2 (µg/m³)", "O3 (µg/m³)"],
            "Current Concentration": [
                today_data["NO2 (µg/m³)"],
                today_data["O3 (µg/m³)"],
            ],
            "WHO Guideline": [
                who_guidelines["WHO Guideline"][0],
                who_guidelines["WHO Guideline"][1],
            ],
        }
        merged_data_df = pd.DataFrame(merged_data)
        st.sidebar.markdown("### Current Pollutant Concentrations and WHO Guidelines")
        st.sidebar.dataframe(merged_data_df, hide_index=True)

    def show_model_performance(self, model_metrics):
        st.markdown("### Model Performance Metrics")
        for model, metrics in model_metrics.items():
            st.markdown(f"**{model}**")
            st.write(f"RMSE: {metrics['RMSE']}, MAE: {metrics['MAE']}")

    def display_predictions_lineplot(self, next_three_days, who_guidelines):
        tomorrow, day_after_tomorrow, two_days_after_tomorrow = self.get_next_three_days_dates()

        # Update the dataframe with actual dates
        next_three_days["Date"] = [tomorrow, day_after_tomorrow, two_days_after_tomorrow]

        # Create line plot for the predictions
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=next_three_days["Date"], y=next_three_days["NO2 (µg/m³)"], mode="lines+markers", name="NO2"))
        fig.add_trace(go.Scatter(x=next_three_days["Date"], y=next_three_days["O3 (µg/m³)"], mode="lines+markers", name="O3"))

        # Add WHO guidelines as reference lines
        fig.add_hline(y=who_guidelines["WHO Guideline"][0], line_dash="dot", annotation_text="WHO NO2 Guideline")
        fig.add_hline(y=who_guidelines["WHO Guideline"][1], line_dash="dot", annotation_text="WHO O3 Guideline")

        # Update layout
        fig.update_layout(
            title="Pollutant Predictions for Next 3 Days",
            xaxis_title="Date",
            yaxis_title="Concentration (µg/m³)",
            hovermode="x unified"
        )

        st.plotly_chart(fig)

    def display_model_comparisons(self, actual, predicted):
        st.markdown("### Model Prediction Comparisons")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=actual, y=predicted, mode="markers", name="Predictions vs Actual"))
        fig.update_layout(title="Actual vs Predicted Pollutant Levels", xaxis_title="Actual", yaxis_title="Predicted")
        st.plotly_chart(fig)

    def get_next_three_days_dates(self):
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)
        two_days_after_tomorrow = today + timedelta(days=3)
        return tomorrow, day_after_tomorrow, two_days_after_tomorrow

    def welcome_back(self):
        st.empty()
        placeholder = st.empty()
        placeholder.success("Welcome back!")
        time.sleep(2)
        placeholder.empty()
