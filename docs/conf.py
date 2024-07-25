# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'detecTDA'
copyright = '2023, Andrew Michael Thomas'
author = 'Andrew Michael Thomas'
release = '0.5.0' 

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
