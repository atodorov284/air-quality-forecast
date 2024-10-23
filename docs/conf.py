# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

project = "Air Quality Forecast"
copyright = "2024, Aleksandar Todorov, Christian Kobriger, Lukasz Sawala, Csenge Szoke"
author = "Aleksandar Todorov, Christian Kobriger, Lukasz Sawala, Csenge Szoke"


sys.path.insert(0, os.path.abspath(os.path.join("../")))
sys.path.insert(0, os.path.abspath(os.path.join("../streamlit_src")))
sys.path.insert(0, os.path.abspath(os.path.join("../air_quality_forecast")))


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
