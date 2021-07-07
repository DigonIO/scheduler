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

project = "scheduler"
copyright = "2021, Jendrik A. Potyka, Fabian A. Preiss"
author = "Jendrik A. Potyka, Fabian A. Preiss"

# The full version, including alpha/beta/rc tags
release = "0.5.1"


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
    "m2r2",
]

imgmath_image_format = "svg"
# Add any paths that contain templates here, relative to this directory.
numpydoc_show_class_members = False
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"

autosummary_generate = True
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "default"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_theme_path = [
    "_themes",
]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

latex_elements = {
    "preamble": r"\usepackage[columns=1]{idxlayout}\makeindex",
}
