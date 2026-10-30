"""WSGI entry point for production WSGI servers (gunicorn / uWSGI / waitress).

Used by:
    - Procfile / PaaS start commands:  gunicorn --chdir backend --bind 0.0.0.0:$PORT wsgi:app
    - Docker:                           gunicorn --chdir /app/student-performance-system/backend --bind 0.0.0.0:8000 wsgi:app
    - Local:                            gunicorn --chdir backend --bind 127.0.0.1:8000 wsgi:app

Importing :mod:`app` reuses the exact same Flask application instance as
``python backend/app.py`` — no duplicated application logic.
"""

import os
import sys

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app import app  # noqa: E402, F401

__all__ = ["app"]
