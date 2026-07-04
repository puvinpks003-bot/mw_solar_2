#!/bin/bash
# Build the project
echo "Building the project..."
python3 -m pip install -r requirements.txt --break-system-packages

echo "Running Migrations..."
python3 manage.py migrate --noinput

echo "Collecting Static Files..."
python3 manage.py collectstatic --noinput --clear
