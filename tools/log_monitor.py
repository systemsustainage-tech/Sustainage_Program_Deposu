#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SustainAge Log Monitor
Checks error logs for critical issues and sends notifications.
"""

import os
import sys
import time
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Adjust path to find backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

try:
    from backend.services.email_service import EmailService
except ImportError:
    try:
        from services.email_service import EmailService
    except ImportError:
        print("Error: Could not import EmailService")
        EmailService = None

# Configuration
LOG_FILE = '/var/www/sustainage/logs/error.log'  # Remote path
# LOG_FILE = 'c:\\SUSTAINAGESERVER\\logs\\error.log' # Local path for testing
STATE_FILE = os.path.join(os.path.dirname(__file__), '.log_monitor_state')
ADMIN_EMAILS = ['admin@sustainage.com'] # Configure recipients

def get_last_position():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_last_position(pos):
    with open(STATE_FILE, 'w') as f:
        f.write(str(pos))

def send_alert(errors):
    if not EmailService:
        print("EmailService not available, skipping email.")
        return

    try:
        email_service = EmailService()
        
        subject = f"CRITICAL: SustainAge Error Log Alert - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .error-box {{ background-color: #ffebee; border: 1px solid #ef5350; padding: 15px; border-radius: 5px; }}
                .error-line {{ font-family: monospace; border-bottom: 1px solid #ddd; padding: 5px 0; }}
            </style>
        </head>
        <body>
            <h2>SustainAge System Alert</h2>
            <p>The following errors were detected in the system logs:</p>
            <div class="error-box">
                {''.join([f'<div class="error-line">{e}</div>' for e in errors])}
            </div>
            <p>Please check the server immediately.</p>
        </body>
        </html>
        """
        
        # Send to each admin
        # Note: EmailService might need specific implementation for ad-hoc emails
        # If EmailService.send_email expects a template name, we might need to bypass it or use a generic template.
        # Assuming we can use a raw send or we added a generic 'alert' template.
        # For now, let's try to use the internal _send_email if accessible or assume send_email handles it.
        # Looking at previous EmailService usage, it uses templates.
        # Let's mock a simple send using smtplib if EmailService is strict, 
        # but better to rely on EmailService if it has a 'raw' mode.
        # If not, we will rely on a basic SMTP send here using config.
        
        # Fallback to direct SMTP if EmailService doesn't support raw HTML easily without template
        # But wait, we added templates! We could add an 'admin_alert' template.
        # Or just use the standard smtplib here to be safe and independent.
        
        config_path = os.path.join(os.path.dirname(__file__), '../backend/config/smtp_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            msg = MIMEMultipart()
            msg['From'] = config.get('sender_email', 'noreply@sustainage.tr')
            msg['To'] = ', '.join(ADMIN_EMAILS)
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            print(f"Alert sent to {ADMIN_EMAILS}")
            
    except Exception as e:
        print(f"Failed to send alert: {e}")

def monitor():
    if not os.path.exists(LOG_FILE):
        print(f"Log file not found: {LOG_FILE}")
        return

    last_pos = get_last_position()
    current_size = os.path.getsize(LOG_FILE)

    if current_size < last_pos:
        # Log rotated
        last_pos = 0

    new_errors = []
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            f.seek(last_pos)
            for line in f:
                if "ERROR" in line or "CRITICAL" in line or "Exception" in line:
                    new_errors.append(line.strip())
            
            save_last_position(f.tell())
            
        if new_errors:
            print(f"Found {len(new_errors)} new errors.")
            send_alert(new_errors)
        else:
            print("No new errors found.")
            
    except Exception as e:
        print(f"Error reading log file: {e}")

if __name__ == "__main__":
    monitor()
