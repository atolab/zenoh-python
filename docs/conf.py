# Configuration file for the Sphinx documentation builder.
import os
import sys
sys.path.insert(0, os.path.abspath('../'))
sys.setrecursionlimit(1500)

# -- Project information -----------------------------------------------------
project = 'zenoh-python'
copyright = '2019, ATOLabs'
author = 'ATOLabs'
release = '0.3.0'

# -- General configuration ---------------------------------------------------
master_doc = 'index'
extensions = ['sphinx.ext.autodoc']
language = 'python'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
