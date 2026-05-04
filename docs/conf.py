# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
sys.path.insert(0, '../')
from detectda import __version__

project = 'detecTDA'
copyright = '2026, Andrew Michael Thomas'
author = 'Andrew Michael Thomas'
release = __version__ 

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "myst_parser", 
    "autoapi.extension",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax"
]

def skip_click_version(app, what, name, obj, skip, options):
    if what == "class" and "click_event" in name:
       skip = True
    elif "version" in name:
       skip = True
    elif what == "attribute":
       skip = True
    elif what == "package" and "test" in name:
       skip = True
    return skip

def setup(sphinx):
   sphinx.connect("autoapi-skip-member", skip_click_version)

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

autoapi_dirs = ["../detectda"]
autoapi_member_order = "groupwise"
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_css_files = [
    'css/custom.css',
]

html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': False,
    'logo_only': True,
    'style_nav_header_background': '#cfffff',
    'style_external_links': True,
    'version_selector': 'attached'
}

html_logo = '../detectda_logo.png'
html_favicon = 'AMT_logo.png'
