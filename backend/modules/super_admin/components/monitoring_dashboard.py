import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitoring Dashboard Component
Real-time system monitoring and email notifications
"""

import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

import psutil

from config.database import DB_PATH
from services.email_service import EmailService


class MonitoringDashboard:
    """Real-time monitoring and notifications"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.email_service = EmailService()

    def get_live_stats(self) -> Dict[str, Any]:
        """Get real-time system statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Active users (sessions in last 15 minutes)
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) 
                FROM session_recordings
                WHERE is_active = 1 
                AND login_time > datetime('now', '-15 minutes')
            """)
            active_users = cursor.fetchone()[0]

            # Total sessions today
            cursor.execute("""
                SELECT COUNT(*) FROM session_recordings
                WHERE DATE(login_time) = DATE('now')
            """)
            sessions_today = cursor.fetchone()[0]

            # Failed logins (last hour)
            cursor.execute("""
                SELECT COUNT(*) FROM login_attempts
                WHERE success = 0 
                AND timestamp > datetime('now', '-1 hour')
            """)
            failed_logins = cursor.fetchone()[0]

            # Security events (last 24h)
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM security_events
                    WHERE timestamp > datetime('now', '-1 day')
                """)
                security_events = cursor.fetchone()[0]
            except Exception:
                # Eski tablo yapısı
                cursor.execute("""
                    SELECT COUNT(*) FROM security_events
                    WHERE created_at > datetime('now', '-1 day')
                """)
                security_events = cursor.fetchone()[0]

            conn.close()

            # System resources
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                system_stats = {
                    'cpu_usage': round(cpu_percent, 1),
                    'memory_usage': round(memory.percent, 1),
                    'disk_usage': round(disk.percent, 1)
                }
            except Exception as e:
                logging.error(f"System stats error: {e}")
                system_stats = {
                    'cpu_usage': 0,
                    'memory_usage': 0,
                    'disk_usage': 0
                }

            return {
                'active_users': active_users,
                'sessions_today': sessions_today,
                'failed_logins': failed_logins,
                'security_events': security_events,
                **system_stats,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"Error getting live stats: {e}")
            return {
                'active_users': 0,
                'sessions_today': 0,
                'failed_logins': 0,
                'security_events': 0,
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'timestamp': datetime.now().isoformat()
            }

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent system events"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT event_type, severity, description, user_id, timestamp
                FROM security_events
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            events = []
            for row in cursor.fetchall():
                events.append({
                    'type': row[0],
                    'severity': row[1],
                    'description': row[2],
                    'user_id': row[3],
                    'timestamp': row[4]
                })

            conn.close()
            return events
        except Exception:
            return []

    def get_chart_data(self, chart_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get data for charts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if chart_type == 'login_activity':
                # Hourly login counts
                cursor.execute("""
                    SELECT 
                        strftime('%Y-%m-%d %H:00', timestamp) as hour,
                        COUNT(*) as count
                    FROM login_attempts
                    WHERE timestamp > datetime('now', ?)
                    GROUP BY hour
                    ORDER BY hour
                """, (f'-{hours} hours',))

            elif chart_type == 'failed_logins':
                cursor.execute("""
                    SELECT 
                        strftime('%Y-%m-%d %H:00', timestamp) as hour,
                        COUNT(*) as count
                    FROM login_attempts
                    WHERE success = 0 
                    AND timestamp > datetime('now', ?)
                    GROUP BY hour
                    ORDER BY hour
                """, (f'-{hours} hours',))

            else:
                return []

            data = [{'time': row[0], 'value': row[1]} for row in cursor.fetchall()]
            conn.close()
            return data

        except Exception:
            return []

    def send_email_notification(
        self,
        event_type: str,
        details: Dict[str, Any],
        recipients: List[str],
        smtp_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Format details for HTML
            details_html = "<ul>"
            for key, value in details.items():
                details_html += f"<li><strong>{key}:</strong> {value}</li>"
            details_html += "</ul>"

            # Send email using standard template
            success_count = 0
            last_error = ""

            for recipient in recipients:
                result = self.email_service.send_template_email_with_result(
                    to_email=recipient,
                    template_key='system_alert',
                    variables={
                        'alert_type': event_type,
                        'alert_details': details_html,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                )
                
                if result.get('success'):
                    success_count += 1
                else:
                    last_error = result.get('error', 'Unknown error')
            
            # Log to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if success_count > 0:
                cursor.execute("""
                    INSERT INTO email_notifications 
                    (notification_type, recipient_email, subject, body, sent_status, sent_at)
                    VALUES (?, ?, ?, ?, 'sent', datetime('now'))
                """, (
                    event_type, 
                    ', '.join(recipients), 
                    f"Sistem Uyarısı: {event_type}", 
                    details_html
                ))
            else:
                cursor.execute("""
                    INSERT INTO email_notifications 
                    (notification_type, recipient_email, subject, sent_status, error_message)
                    VALUES (?, ?, ?, 'failed', ?)
                """, (
                    event_type, 
                    ', '.join(recipients), 
                    f"Sistem Uyarısı: {event_type}", 
                    last_error
                ))

            conn.commit()
            conn.close()

            if success_count > 0:
                return {'success': True, 'message': f'Email sent successfully to {success_count} recipients'}
            else:
                return {'success': False, 'message': f'Error: {last_error}'}

        except Exception as e:
            # Log error
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO email_notifications 
                    (notification_type, recipient_email, subject, sent_status, error_message)
                    VALUES (?, ?, ?, 'failed', ?)
                """, (event_type, ', '.join(recipients), f"[SUSTAINAGE SDG] {event_type}", str(e)))
                conn.commit()
                conn.close()
            except Exception as e2:
                logging.error(f"Silent error caught: {str(e2)}")

            return {'success': False, 'message': f'Error: {str(e)}'}

    def get_alerts(self) -> List[Dict]:
        """Get active system alerts"""
        alerts = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check for expiring licenses (30 days)
            try:
                cursor.execute("""
                    SELECT COUNT(*), company_name FROM licenses
                    WHERE expiry_date BETWEEN datetime('now') AND datetime('now', '+30 days')
                    AND is_active = 1
                    GROUP BY company_name
                """)
            except Exception:
                # Tablo yoksa veya hata varsa skip et
                cursor.execute("SELECT 0, 'None' WHERE 1=0")
            for row in cursor.fetchall():
                alerts.append({
                    'severity': 'warning',
                    'message': f"License for {row[1]} expiring soon",
                    'timestamp': datetime.now().isoformat()
                })

            # Check for failed login attempts
            cursor.execute("""
                SELECT COUNT(*) FROM login_attempts
                WHERE success = 0 
                AND timestamp > datetime('now', '-1 hour')
            """)
            failed_count = cursor.fetchone()[0]
            if failed_count > 10:
                alerts.append({
                    'severity': 'critical',
                    'message': f"{failed_count} failed login attempts in last hour",
                    'timestamp': datetime.now().isoformat()
                })

            # Check system resources
            try:
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory().percent

                if cpu > 80:
                    alerts.append({
                        'severity': 'warning',
                        'message': f"High CPU usage: {cpu}%",
                        'timestamp': datetime.now().isoformat()
                    })

                if memory > 85:
                    alerts.append({
                        'severity': 'critical',
                        'message': f"High memory usage: {memory}%",
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

            conn.close()

        except Exception as e:
            logging.error(f"Error getting alerts: {e}")

        return alerts

