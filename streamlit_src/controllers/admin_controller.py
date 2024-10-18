from models.air_quality_model import AirQualityModel
from views.admin_view import AdminView


class AdminController:
    def __init__(self):
        self.model = AirQualityModel()
        self.view = AdminView()

    def show_dashboard(self):
        return
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
        self.view.display_predictions(next_three_days)

        # Compare to WHO guidelines
        self.view.compare_to_who(
            today_data, self.model.WHO_NO2_LEVEL, self.model.WHO_O3_LEVEL
        )

    def welcome_back(self):
        self.view.welcome_back()
