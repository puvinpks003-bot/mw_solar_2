#!/bin/bash
# Build the project
echo "Building the project..."
python3.9 -m pip install -r requirements.txt

echo "Running Migrations..."
python3.9 manage.py migrate --noinput

echo "Collecting Static Files..."
python3.9 manage.py collectstatic --noinput --clear
