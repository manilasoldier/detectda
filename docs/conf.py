# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'detectda'
copyright = '2023, Andrew Michael Thomas'
author = 'Andrew Michael Thomas'
release = '0.4.3' 

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb", 
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax"
]

def autodoc_skip_member_handler(app, what, name, obj, skip, options):
    if what == "package" and "tests" in name:
        skip=True
    return skip

def setup(sphinx):
   sphinx.connect("autoapi-skip-member", autodoc_skip_member_handler)

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

autoapi_dirs = ["../detectda"]
autoapi_ignore = ["*/tests"]
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
