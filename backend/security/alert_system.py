import logging
import os
import json
from datetime import datetime
from backend.services.email_service import EmailService

# Configure a specific logger for security alerts
alert_logger = logging.getLogger('security_alerts')
alert_logger.setLevel(logging.CRITICAL)

# Create a file handler for alerts
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

alert_file = os.path.join(log_dir, 'security_alerts.log')
file_handler = logging.FileHandler(alert_file)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
alert_logger.addHandler(file_handler)

# Initialize Email Service
# Try to get DB_PATH from config if possible, otherwise rely on defaults
try:
    from backend.config.database import DB_PATH
    email_service = EmailService(db_path=DB_PATH)
except ImportError:
    email_service = EmailService()

# Admin emails to notify (should be in config/env)
ADMIN_EMAILS = os.getenv('ADMIN_EMAILS', 'admin@sustainage.com').split(',')

def report_violation(violation_type, source_ip, details=None):
    """
    Reports a security violation.
    
    Args:
        violation_type (str): Type of violation (e.g., 'RATE_LIMIT', 'CAPTCHA_FAIL', 'BRUTE_FORCE')
        source_ip (str): IP address of the source
        details (dict): Additional details about the violation
    """
    timestamp = datetime.now().isoformat()
    
    alert_data = {
        'timestamp': timestamp,
        'type': violation_type,
        'source_ip': source_ip,
        'details': details or {}
    }
    
    # Log to file (CRITICAL level)
    alert_logger.critical(json.dumps(alert_data))
    
    print(f"SECURITY ALERT: {violation_type} from {source_ip}")

    # Send Email Alert for critical violations or repeated offenses
    # For now, we alert on everything that reaches here, as report_violation is called on failures
    try:
        subject = f"🚨 GÜVENLİK UYARISI: {violation_type}"
        
        details_html = "<ul>"
        if details:
            for k, v in details.items():
                details_html += f"<li><strong>{k}:</strong> {v}</li>"
        details_html += "</ul>"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; }}
                .alert-box {{ background-color: #ffebee; border: 1px solid #ffcdd2; color: #b71c1c; padding: 20px; border-radius: 5px; }}
                .detail-box {{ margin-top: 20px; background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="alert-box">
                <h2>⚠️ Güvenlik İhlali Tespit Edildi</h2>
                <p><strong>Tür:</strong> {violation_type}</p>
                <p><strong>Kaynak IP:</strong> {source_ip}</p>
                <p><strong>Zaman:</strong> {timestamp}</p>
            </div>
            
            <div class="detail-box">
                <h3>Detaylar</h3>
                {details_html}
            </div>
            
            <p><small>Bu otomatik bir güvenlik uyarısıdır.</small></p>
        </body>
        </html>
        """
        
        for admin_email in ADMIN_EMAILS:
            if admin_email.strip():
                email_service.send_email(
                    to_email=admin_email.strip(),
                    subject=subject,
                    body=body
                )
                
    except Exception as e:
        logging.error(f"Failed to send security alert email: {e}")

def check_for_active_threats(source_ip):
    """
    Checks if there are active threats from this IP (e.g., recent alerts).
    Returns True if blocked/suspicious.
    """
    # Simple implementation: Check if IP is in recent alerts (would require reading the log or DB)
    # For now, just return False
    return False
