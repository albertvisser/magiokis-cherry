#! /usr/bin/env python3
"""Startup script voor Magiokis CherryPy version
"""
import sys
import os
import pathlib
# sys.stdout = sys.stderr
import cgitb
cgitb.enable()
import cherrypy

ROOT = pathlib.Path(__file__).parent.resolve()
os.chdir(str(ROOT))
sys.path.insert(0, str(ROOT))
from magiokis import HomePage

application = cherrypy.tree.mount(HomePage(), config=str(ROOT / 'magiokis.conf'))
cherrypy.config.update({'environment': 'embedded'})
## cherrypy.config.update({'engine.autoreload_on': False,
        ## })
