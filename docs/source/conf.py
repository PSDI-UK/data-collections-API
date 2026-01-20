# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from __future__ import annotations

import time
import sys
from pathlib import Path

DOCS_SRC = Path(__file__).parent.resolve()
sys.path.append(str(DOCS_SRC.parents[2]))
sys.path.append(str(DOCS_SRC))

import data_collections_api
from scripts.schema_gen import main as gen_schema


project = "Data Collections API"
copyright_first_year = "2024"
author = data_collections_api.__author__
copyright = f"{copyright_first_year}-{time.localtime().tm_year}, {author}. All rights reserved."
release = data_collections_api.__version__
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "numpydoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.apidoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinxcontrib.contentui",
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

apidoc_modules = [
    {"path": "../../data_collections_api", "destination": "api/"},
]

gen_schema(["-Fv", f"-o={DOCS_SRC / 'schemas'}", "-O=%s.md", "all"])

always_use_bars_union = True
napoleon_include_special_with_doc = True
napoleon_use_param = True

# Add the numpydoc_show_inherited_class_members option
numpydoc_show_inherited_class_members = False

numpydoc_validation_checks = {"all", "EX01", "SA01", "ES01"}
# numpydoc_validation_exclude

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_title = f"data-collections-api v{release}"
html_theme_options = {
    "source_repository": "https://github.com/PSDI-UK/data-collections-API/",
    "source_branch": "main",
    "source_directory": "docs/source",
}
