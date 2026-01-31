#!/bin/bash
SERVER_DIR="/var/www/sustainage"
cd $SERVER_DIR

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing/Updating requirements..."
# Update pip first
pip install --upgrade pip
# Install requirements
pip install -r requirements.txt
# Ensure gunicorn is installed
pip install gunicorn

echo "Venv setup complete."
