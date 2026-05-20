"""Gunicorn configuration for Render deployment.

Render executes the start command from repository root. Our Django project
and its ``config`` package live under ``AttendanceSystem/``, so we change the
working directory before loading ``config.wsgi``.
"""

chdir = "AttendanceSystem"
