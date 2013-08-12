#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
#sys.stdout = sys.stderr
import cgitb
cgitb.enable()
import cherrypy

ROOT = os.path.dirname(os.path.abspath(__file__)) # '/home/albert/www/cherrypy/magiokis/'
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from magiokis import HomePage


cherrypy.config.update({'environment': 'embedded'})

application = cherrypy.tree.mount(HomePage(), config=os.path.join(ROOT,
    'magiokis.conf'))
cherrypy.config.update({'engine.autoreload_on': False,
        })
