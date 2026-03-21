# Sphinx configuration for Ghost Brain API docs.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

project = "Ghost Brain"
copyright = "Ghost Brain"
author = "Ghost Brain"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_member_order = "bysource"
autodoc_default_options = {"members": True, "undoc-members": True}
napoleon_use_param = True

templates_path = ["_templates"]
exclude_patterns = []
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
