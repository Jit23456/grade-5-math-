# -*- coding: utf-8 -*-
"""WSGI entry point.

Gunicorn:   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
uWSGI:      uwsgi --http :8000 --module wsgi:application
waitress:   waitress-serve --port=8000 wsgi:application
mod_wsgi:   WSGIScriptAlias / /path/to/app/wsgi.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application, init_db

# Build the schema and seed the curriculum on first import, so the app is
# ready under any WSGI server without a separate setup step.
init_db()

app = application

if __name__ == "__main__":
    application.run()
