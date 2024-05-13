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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import sphinx_rtd_theme


# -- Project information -----------------------------------------------------

project = 'CO2Pipeline'
copyright = '2023, NETL-RIC'
author = 'NETL-RIC'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
        'sphinx_rtd_theme',
        'myst_parser',
        'sphinxcontrib.bibtex',
        'sphinx_copybutton',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

#bibtex configuration
bibtex_bibfiles = ['refs.bib']
bibtex_default_style= 'alpha'
bibtex_reference_style = 'author_year'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# suffix control for parsers
source_suuffix = {
    '.rst' : 'restructuredtext',
    '.txt' : 'restructuredtext',
    '.md' : 'markdown',
}

# Additional MyST settings
myst_enable_extensions = [
        "amsmath", # for LaTeX equations.
        "html_admonition",
        "colon_fence",
]

myst_heading_anchors = 3 # Creates "anchors" for h1, h2, h3 headings (you can then create links to headings)

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path=['_static']
html_logo='_static/netl_logo_transparent2.png'
html_short_title='CO2P'
html_show_sourcelink=False
