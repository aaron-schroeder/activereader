# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../'))


# -- Project information -----------------------------------------------------
from activereader import __version__
project = 'activereader'
copyright = '2021, Aaron Schroeder'
author = 'Aaron Schroeder'

# The short X.Y version.
version = __version__

# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
  'sphinx.ext.autodoc',
  'sphinx.ext.napoleon',
  'sphinx.ext.todo',
  'sphinx.ext.intersphinx',
  'sphinx.ext.autosummary',
]

# Napoleon options
# Full list here:
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#configuration
#napoleon_google_docstring = False
#napoleon_use_param = False
#napoleon_use_ivar = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Add mappings so I can link to external docs
intersphinx_mapping = {
  'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
  'lxml': ('https://lxml.de/apidoc/', None),
  'dateutil': ('https://dateutil.readthedocs.io/en/stable/', None),
}

# Show docstring for __init__
autoclass_content = 'both'

# autosummary options
autosummary_generate = False

# autodoc options
autodoc_member_order = 'bysource'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# meant to add custom css 
def setup(app):
  # app.add_javascript('custom.js')
  app.add_css_file('custom.css')