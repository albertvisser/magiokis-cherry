#! /usr/bin/env python3
"""Startup script voor Magiokis CherryPy version
"""
import sys
import os
# sys.stdout = sys.stderr
import cgitb
cgitb.enable()
import cherrypy

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from magiokis import HomePage

application = cherrypy.tree.mount(HomePage(), config=os.path.join(ROOT, 'magiokis.conf'))
cherrypy.config.update({'environment': 'embedded'})
## cherrypy.config.update({'engine.autoreload_on': False,
        ## })
