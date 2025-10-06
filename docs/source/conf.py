# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import data_collections_api

project = 'Data Collections API'
author = data_collections_api.__author__
copyright = f'2025, {author}'
release = data_collections_api.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "aiida.sphinxext",
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinxcontrib.contentui",
]

# Add the numpydoc_show_inherited_class_members option
numpydoc_show_inherited_class_members = False

numpydoc_validation_checks = {"all", "EX01", "SA01", "ES01"}
# numpydoc_validation_exclude

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}


templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
