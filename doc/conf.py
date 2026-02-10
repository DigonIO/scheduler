# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys

from sphinx.locale import _

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

with open("../scheduler/__init__.py", "r") as file:
    for line in file:
        if "__version__" in line:
            version = line.split('"')[1]
        if "__author__" in line:
            author = line.split('"')[1]

project = "scheduler"
copyright = "2026, " + author
author = author

# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.imgconverter",
    "sphinx.ext.coverage",
    "sphinx.ext.imgmath",
    "sphinx.ext.viewcode",
    "numpydoc",
    "myst_parser",
]

with open("_assets/prolog.rst", encoding="utf-8") as f:
    rst_prolog = f.read()

imgmath_image_format = "svg"
# Add any paths that contain templates here, relative to this directory.
numpydoc_show_class_members = False
templates_path = ["_templates"]
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
master_doc = "index"

autosummary_generate = True
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_assets"]
pygments_style = "manni"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_theme_path = [
    "_themes",
]
html_favicon = "favicon.png"
html_logo = "logo_w_border.svg"


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["custom.css", "custom_pygments.css"]

imgmath_latex_preamble = (
    "\\usepackage{xcolor}\n\\definecolor{formulacolor}{RGB}{128,128,128}" "\\color{formulacolor}"
)
imgmath_image_format = "svg"


latex_elements = {
    "preamble": [
        r"\usepackage[columns=1]{idxlayout}\makeindex",
    ],
}
