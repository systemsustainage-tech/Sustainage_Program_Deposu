#!/bin/bash
cd /var/www/sustainage
source venv/bin/activate
nohup gunicorn --bind 0.0.0.0:5001 web_app:app > output.log 2>&1 &
echo "Started gunicorn with PID $!"
