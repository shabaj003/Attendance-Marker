#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="AttendanceSystem"

python -m pip install --upgrade pip
python -m pip install -r "${PROJECT_DIR}/requirements.txt"

python "${PROJECT_DIR}/manage.py" collectstatic --noinput
python "${PROJECT_DIR}/manage.py" migrate --noinput
