# Documentation - Sphinx

This `docs` folder contains the configuration and source files needed to build the HTML documentation for the **Air Quality Forecasting** project using Sphinx. Sphinx allows us to generate clean, navigable HTML documentation directly from the project's docstrings and reStructuredText (`.rst`) files.

## 📂 Folder Structure

```plaintext
docs/
├── _build/                   # Output directory for built documentation files
│   ├── doctrees/             # Stores the intermediate doctree files used by Sphinx
│   └── html/                 # Contains the generated HTML files for the documentation
├── .gitkeep                  # Keeps the _build folder in the version control system
├── Makefile                  # Makefile for building the documentation on Unix-based systems
├── air_quality_forecast.rst  # Documentation for the air quality forecasting module
├── conf.py                   # Configuration file for Sphinx
├── index.rst                 # Main index file for the documentation
├── make.bat                  # Batch file for building the documentation on Windows
├── modules.rst               # Auto-generated list of all modules in the project
├── streamlit_src.controllers.rst  # Documentation for controllers module
├── streamlit_src.models.rst       # Documentation for models module
├── streamlit_src.rst              # General documentation for the streamlit_src folder
└── streamlit_src.views.rst        # Documentation for views module
```
---

## 📖 Usage

### Generating HTML Documentation

To build the HTML documentation, navigate to the `docs` folder in your terminal and use one of the following commands:

- **On Unix-based systems** (Linux/macOS):
  ```bash
- **On Windows systems**
  ```bash
