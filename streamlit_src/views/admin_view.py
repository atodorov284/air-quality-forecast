# views/user_view.py
import streamlit as st
import pandas as pd
from datetime import date
import time

class AdminView:
    def show_current_data(self, today_data, who_guidelines):
        return 
        st.sidebar.markdown(f"ADMIN Today's Date: **{date.today().strftime('%B %d, %Y')}**")
        st.sidebar.markdown("### Current Pollutant Concentrations")
        today_data_df = pd.DataFrame([today_data])
        st.sidebar.dataframe(today_data_df.style.hide(axis="index"))
        
        st.sidebar.markdown("### WHO Guidelines")
        who_guidelines_df = pd.DataFrame(who_guidelines)
        st.sidebar.dataframe(who_guidelines_df.style.hide(axis="index"))

    def display_predictions(self, next_three_days):
        return  
        st.markdown("### Predictions for the Next 3 Days")
        st.line_chart(next_three_days.set_index("Day"))

    def compare_to_who(self, today_data, no2_level, o3_level):
        return  
        if today_data["NO2 (µg/m³)"] > no2_level:
            st.sidebar.error("⚠️ NO2 levels are above WHO guidelines!")
        else:
            st.sidebar.success("✅ NO2 levels are within safe limits.")

        if today_data["O3 (µg/m³)"] > o3_level:
            st.sidebar.error("⚠️ O3 levels are above WHO guidelines!")
        else:
            st.sidebar.success("✅ O3 levels are within safe limits.")
            
    def welcome_back(self):
        st.empty()
        placeholder = st.empty()
        placeholder.success("Welcome back!")
        time.sleep(2)
        placeholder.empty()