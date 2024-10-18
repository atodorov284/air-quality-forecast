# views/user_view.py
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.graph_objects as go


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
        today = datetime.now()  # Get the current date and time
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)
        two_days_after_tomorrow = today + timedelta(days=3)
        return tomorrow, day_after_tomorrow, two_days_after_tomorrow

    def display_predictions_lineplot(self, next_three_days, who_guidelines):
        st.markdown("### Predictions for the Next 3 Days")

        tomorrow, day_after_tomorrow, two_days_after_tomorrow = \
            self.get_next_three_days_dates()

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

    def get_no2_color(self, value, who_limit):
        # Define the gradient points
        if value <= who_limit:
            # Blue -> Purple gradient
            return f"rgba({int(0 + (255 * value / who_limit))}, 0, 255, 1)"  # Gradient from blue to purple
        else:
            # Purple -> Red gradient
            excess_value = min(who_limit, value - who_limit)
            return f"rgba(255, 0, {int(255 - (255 * excess_value / who_limit))}, 1)"  # Gradient from purple to red

    def display_predictions_gaugeplot(self, next_three_days, who_guidelines):
        st.markdown("### Predictions for the Next 3 Days")
        # Convert date to datetime and calculate future dates
        tomorrow, day_after_tomorrow, two_days_after_tomorrow = \
            self.get_next_three_days_dates()

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
                no2_color = self.get_no2_color(no2_value, who_guidelines["WHO Guideline"][0])
                fig_no2 = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=next_three_days["NO2 (µg/m³)"][i],
                        title={"text": "NO2 (µg/m³)"},
                        gauge={
                            "axis": {
                                "range": [
                                    0,
                                    max(who_guidelines["WHO Guideline"][0], 100),
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
                fig_o3 = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=next_three_days["O3 (µg/m³)"][i],
                        title={"text": "O3 (µg/m³)"},
                        gauge={
                            "axis": {
                                "range": [
                                    0,
                                    max(who_guidelines["WHO Guideline"][1], 150),
                                ]
                            },
                            "bar": {"color": "lightblue"},
                        },
                        domain={"x": [0, 1], "y": [0, 1]},  # Controls size
                    )
                )
                fig_o3.update_layout(
                    height=250, width=250, margin=dict(t=0, b=0, l=0, r=0)
                )
                st.plotly_chart(fig_o3)

    def view_option_selection(self) -> str:
        plot_type = st.selectbox(
            "Choose Visualization Type",
            ("Line Plot", "Gauge Plot")
        )
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

    def raise_awareness(self):
        st.sidebar.markdown("""
        **Air pollution** is a serious concern that affects the environment and public health. 
        High levels of pollutants, such as ozone (O₃) and nitrogen dioxide (NO₂), can lead to 
        respiratory problems, aggravate pre-existing conditions like asthma, and contribute to 
        cardiovascular diseases. On particularly bad days, vulnerable groups such as children, 
        the elderly, and those with respiratory issues are at even greater risk. 
        """)

        st.sidebar.markdown("""
        **Key Pollutants:**
        - **Ozone (O₃):** Formed by chemical reactions in the atmosphere, particularly on sunny days.
        - **Nitrogen Dioxide (NO₂):** Mostly emitted from vehicles and industrial activities, this can cause 
        irritation of the respiratory system.
        """)
