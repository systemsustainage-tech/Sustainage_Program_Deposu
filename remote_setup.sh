#!/bin/bash
# Remote Setup Script
SERVER_DIR="/var/www/sustainage"
mkdir -p $SERVER_DIR
cd $SERVER_DIR

echo "Extracting package..."
tar -xzf deploy_package_v3.tar.gz --overwrite

echo "Installing dependencies..."
# Use venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
else
    # Check if pip3 exists, else install it (optional, assuming env is ready)
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt --break-system-packages
    else
        echo "pip3 not found, skipping dependency install (or install python3-pip manually)"     
    fi
fi

echo "Restarting application..."
# Kill existing instance
pkill -f "python3 web_app.py" || true
pkill -f "python web_app.py" || true
pkill -f "gunicorn" || true

# Start new instance
if [ -d "venv" ]; then
    nohup venv/bin/python3 web_app.py > app.log 2>&1 &
else
    nohup python3 web_app.py > app.log 2>&1 &
fi

echo "Application restarted. Logs are in app.log."
