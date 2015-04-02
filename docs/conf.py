# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('_themes'))
import guardrail
import alabaster


extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'alabaster',
]

html_theme = 'alabaster'
html_static_path = ['_static']
html_theme_path = [alabaster.get_path()]

html_sidebars = {
    '**': [
        'about.html', 'navigation.html', 'searchbox.html', 'donate.html',
    ],
}
html_theme_options = {
    'github_banner': True,
    'travis_button': True,
    'github_user': 'jmcarp',
    'github_repo': 'guardrail',
}

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = 'guardrail'
copyright = '2014-2015'
version = release = guardrail.__version__
language = 'en'

exclude_patterns = ['_build']

default_role = 'py:obj'

autodoc_member_order = 'bysource'
