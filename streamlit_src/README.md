# Utrecht Air Quality Monitoring Application 🌍💨

Welcome to the **Utrecht Air Quality Monitoring** application! This interactive app, built with Streamlit, provides timely insights into the levels of key air pollutants—NO₂ and O₃—in Utrecht, helping users monitor and forecast air quality based on WHO standards.

---

## 🌟 Features

- **Real-Time Monitoring:** Stay updated on today’s air quality with data updated every 6 hours.
- **3-Day Forecasts:** View predicted NO₂ and O₃ levels for the upcoming three days.
- **User & Admin Dashboards:** Easy-to-use interfaces for general users and detailed analytics for admins.
- **Comprehensive MVC Structure:** Organized codebase for easy navigation, maintenance, and scalability.

---

## 📂 Folder Structure
```plaintext
streamlit_src/
├── controllers/
│   ├── home_controller.py      # Manages logic for the main dashboard and user access
│   ├── user_controller.py      # Controls data display on the user dashboard
│   └── admin_controller.py     # Extends user_controller for admin-specific features
│
├── json_interactions/          # Handles JSON data interactions for configuration and storage
│   └── (JSON handling scripts)
│
├── models/
│   └── air_quality_model.py    # Contains model loading, preprocessing, and prediction logic
│
├── views/
│   ├── home_view.py            # Sets up the main interface and role selection
│   ├── user_view.py            # Displays air quality data and forecasts for users
│   └── admin_view.py           # Presents analytics and monitoring tools for admins
│
├── README.md                   # Documentation for the Streamlit application
├── __init__.py                 # Initializes the streamlit_src package
└── app.py                      # Main entry point to run the Streamlit application
```

---

## ⚙️ Design Pattern: MVC

To make the application easy to manage and extend, we’ve structured it using the **Model-View-Controller (MVC)** design pattern. Here’s how each part contributes:

### 1. Model (`air_quality_model.py`)

Our **Model** forms the backbone of the application, handling:
   - **Data loading and preprocessing** to ensure consistency in predictions.
   - **Air quality prediction models** for NO₂ and O₃, using data collected over past days.
   - **Prediction logic** that leverages our trained models to provide accurate, actionable forecasts.

### 2. Views (`home_view.py`, `user_view.py`, `admin_view.py`)

The **View** components shape the look of the application, providing different displays for each user role:
   - **`home_view.py`:** Sets up the main page layout, including a field for users to switch roles or log in as an admin.
   - **`user_view.py`:** Manages the visual elements and display of air quality forecasts for NO₂ and O₃ on the user dashboard.
   - **`admin_view.py`:** Handles all visual elements on the admin dashboard, including advanced metrics, monitoring tools, and model performance data.

### 3. Controllers (`home_controller.py`, `user_controller.py`, `admin_controller.py`)

Our **Controller** modules serve as intermediaries, connecting the model's data and logic with the views’ visual representation. Each controller is aligned with a specific view:
   - **`home_controller.py`:** Manages the logic for the main dashboard, handling user access and controlling the display of either the user or admin dashboard.
   - **`user_controller.py`:** Manages the logic for the user dashboard, making use of the `user_view.py` script to correctly format the user dashboard including. 
   - **`admin_controller.py`:** Manages the logic for the admin dashboard, extending the `UserController` to provide additional features tailored to admin needs.

---
