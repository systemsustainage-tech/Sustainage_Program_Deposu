#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Güvenlik Özellikleri
Multi-factor authentication, IP whitelist, session recording, threat detection
"""

import os
import secrets
import sqlite3

# İsteğe bağlı bağımlılıklar — eksikse belirli özellikler devre dışı
try:
    import qrcode
except Exception:
    qrcode = None

try:
    import pyotp
except Exception:
    pyotp = None
import ipaddress
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List
from config.database import DB_PATH


class AdvancedSecurityManager:
    """Gelişmiş Güvenlik Özellikleri Yöneticisi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_advanced_security_tables()
        self._setup_logging()

    def _init_advanced_security_tables(self) -> None:
        """Gelişmiş güvenlik tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Multi-factor authentication tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mfa_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    mfa_enabled BOOLEAN DEFAULT FALSE,
                    mfa_secret TEXT,
                    backup_codes TEXT,
                    recovery_email TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # IP whitelist tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ip_whitelist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    ip_address TEXT NOT NULL,
                    ip_range TEXT,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Session recording tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    login_time DATETIME,
                    logout_time DATETIME,
                    actions_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Session actions tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_description TEXT,
                    module_name TEXT,
                    ip_address TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES session_recordings(session_id)
                )
            """)

            # Threat detection tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threat_detection (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    threat_type TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    description TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    detection_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_resolved BOOLEAN DEFAULT FALSE,
                    resolution_notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Security events tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    event_type TEXT NOT NULL,
                    event_description TEXT,
                    severity TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    additional_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Penetration testing tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS penetration_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    test_date DATETIME NOT NULL,
                    tester_name TEXT,
                    vulnerabilities_found INTEGER DEFAULT 0,
                    critical_vulnerabilities INTEGER DEFAULT 0,
                    high_vulnerabilities INTEGER DEFAULT 0,
                    medium_vulnerabilities INTEGER DEFAULT 0,
                    low_vulnerabilities INTEGER DEFAULT 0,
                    test_report_path TEXT,
                    recommendations TEXT,
                    status TEXT DEFAULT 'Completed',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Vulnerability details tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vulnerability_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER NOT NULL,
                    vulnerability_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    affected_component TEXT,
                    remediation_steps TEXT,
                    status TEXT DEFAULT 'Open',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES penetration_tests(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Gelişmiş güvenlik tabloları oluşturuldu")

        except Exception as e:
            logging.error(f"[HATA] Gelişmiş güvenlik tabloları oluşturulamadı: {e}")
        finally:
            conn.close()

    def _setup_logging(self) -> None:
        """Güvenlik loglarını ayarla"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/security.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.security_logger = logging.getLogger('security')

    # ==================== MULTI-FACTOR AUTHENTICATION ====================

    def setup_mfa(self, user_id: int, recovery_email: str = None) -> Dict[str, Any]:
        """MFA kurulumu yap"""
        try:
            if pyotp is None or qrcode is None:
                missing = []
                if pyotp is None:
                    missing.append('pyotp')
                if qrcode is None:
                    missing.append('qrcode')
                raise RuntimeError(
                    "Eksik paketler: " + ", ".join(missing) +
                    ". Kurulum: pip install pyotp qrcode"
                )
            # MFA secret oluştur
            mfa_secret = pyotp.random_base32()

            # Backup kodları oluştur
            backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]

            # QR kod oluştur
            totp = pyotp.TOTP(mfa_secret)
            qr_data = totp.provisioning_uri(
                name=f"user_{user_id}@sustainage.com",
                issuer_name="Sustainage SDG"
            )

            # QR kod dosyasını oluştur
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)

            qr_path = f"security/mfa_qr_{user_id}.png"
            os.makedirs("security", exist_ok=True)
            qr.make_image().save(qr_path)

            # Veritabanına kaydet
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO mfa_settings 
                (user_id, mfa_enabled, mfa_secret, backup_codes, recovery_email)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, False, mfa_secret, json.dumps(backup_codes), recovery_email))

            conn.commit()
            conn.close()

            return {
                'success': True,
                'mfa_secret': mfa_secret,
                'backup_codes': backup_codes,
                'qr_path': qr_path,
                'qr_data': qr_data
            }

        except Exception as e:
            self.security_logger.error(f"MFA kurulum hatası: {e}")
            return {'success': False, 'error': str(e)}

    def verify_mfa_code(self, user_id: int, code: str) -> bool:
        """MFA kodunu doğrula"""
        try:
            if pyotp is None:
                self.security_logger.error("pyotp eksik; MFA doğrulama yapılamaz.")
                return False
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT mfa_secret, backup_codes FROM mfa_settings 
                WHERE user_id = ? AND mfa_enabled = TRUE
            """, (user_id,))

            result = cursor.fetchone()
            if not result:
                return False

            mfa_secret, backup_codes_json = result
            backup_codes = json.loads(backup_codes_json) if backup_codes_json else []

            # TOTP kodu kontrol et
            totp = pyotp.TOTP(mfa_secret)
            if totp.verify(code, valid_window=1):
                return True

            # Backup kod kontrol et
            if code in backup_codes:
                # Backup kodu kullanıldı, listeden çıkar
                backup_codes.remove(code)
                cursor.execute("""
                    UPDATE mfa_settings SET backup_codes = ? WHERE user_id = ?
                """, (json.dumps(backup_codes), user_id))
                conn.commit()
                return True

            return False

        except Exception as e:
            self.security_logger.error(f"MFA doğrulama hatası: {e}")
            return False
        finally:
            conn.close()

    def enable_mfa(self, user_id: int) -> bool:
        """MFA'yı etkinleştir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE mfa_settings SET mfa_enabled = TRUE WHERE user_id = ?
            """, (user_id,))

            conn.commit()
            conn.close()

            self.security_logger.info(f"MFA etkinleştirildi - Kullanıcı: {user_id}")
            return True

        except Exception as e:
            self.security_logger.error(f"MFA etkinleştirme hatası: {e}")
            return False

    # ==================== IP WHITELIST ====================

    def add_ip_to_whitelist(self, user_id: int, ip_address: str, description: str = None) -> bool:
        """IP adresini whitelist'e ekle"""
        try:
            # IP adresini doğrula
            ipaddress.ip_address(ip_address)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO ip_whitelist (user_id, ip_address, description)
                VALUES (?, ?, ?)
            """, (user_id, ip_address, description))

            conn.commit()
            conn.close()

            self.security_logger.info(f"IP whitelist'e eklendi - Kullanıcı: {user_id}, IP: {ip_address}")
            return True

        except Exception as e:
            self.security_logger.error(f"IP whitelist ekleme hatası: {e}")
            return False

    def check_ip_whitelist(self, user_id: int, ip_address: str) -> bool:
        """IP adresinin whitelist'te olup olmadığını kontrol et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM ip_whitelist 
                WHERE user_id = ? AND ip_address = ? AND is_active = TRUE
            """, (user_id, ip_address))

            count = cursor.fetchone()[0]
            conn.close()

            return count > 0

        except Exception as e:
            self.security_logger.error(f"IP whitelist kontrol hatası: {e}")
            return False

    def get_user_whitelisted_ips(self, user_id: int) -> List[Dict[str, Any]]:
        """Kullanıcının whitelist'teki IP'lerini getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, ip_address, description, is_active, created_at
                FROM ip_whitelist WHERE user_id = ? ORDER BY created_at DESC
            """, (user_id,))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    'id': row[0],
                    'ip_address': row[1],
                    'description': row[2],
                    'is_active': bool(row[3]),
                    'created_at': row[4]
                }
                for row in results
            ]

        except Exception as e:
            self.security_logger.error(f"IP whitelist getirme hatası: {e}")
            return []

    # ==================== SESSION RECORDING ====================

    def start_session_recording(self, user_id: int, session_id: str, ip_address: str, user_agent: str) -> bool:
        """Session kaydını başlat"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO session_recordings 
                (user_id, session_id, ip_address, user_agent, login_time)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_id, ip_address, user_agent, datetime.now()))

            conn.commit()
            conn.close()

            self.security_logger.info(f"Session kaydı başlatıldı - Kullanıcı: {user_id}, Session: {session_id}")
            return True

        except Exception as e:
            self.security_logger.error(f"Session kaydı başlatma hatası: {e}")
            return False

    def record_session_action(self, session_id: str, action_type: str, action_description: str,
                            module_name: str = None, ip_address: str = None) -> bool:
        """Session aksiyonunu kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO session_actions 
                (session_id, action_type, action_description, module_name, ip_address)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, action_type, action_description, module_name, ip_address))

            # Session'daki aksiyon sayısını artır
            cursor.execute("""
                UPDATE session_recordings 
                SET actions_count = actions_count + 1 
                WHERE session_id = ?
            """, (session_id,))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            self.security_logger.error(f"Session aksiyon kaydetme hatası: {e}")
            return False

    def end_session_recording(self, session_id: str) -> bool:
        """Session kaydını sonlandır"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE session_recordings 
                SET logout_time = ?, is_active = FALSE 
                WHERE session_id = ?
            """, (datetime.now(), session_id))

            conn.commit()
            conn.close()

            self.security_logger.info(f"Session kaydı sonlandırıldı - Session: {session_id}")
            return True

        except Exception as e:
            self.security_logger.error(f"Session kaydı sonlandırma hatası: {e}")
            return False

    def get_session_recordings(self, user_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Session kayıtlarını getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if user_id:
                cursor.execute("""
                    SELECT session_id, ip_address, user_agent, login_time, logout_time, 
                           actions_count, is_active
                    FROM session_recordings 
                    WHERE user_id = ? 
                    ORDER BY login_time DESC LIMIT ?
                """, (user_id, limit))
            else:
                cursor.execute("""
                    SELECT user_id, session_id, ip_address, user_agent, login_time, 
                           logout_time, actions_count, is_active
                    FROM session_recordings 
                    ORDER BY login_time DESC LIMIT ?
                """, (limit,))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    'user_id': row[0] if not user_id else user_id,
                    'session_id': row[1] if user_id else row[1],
                    'ip_address': row[2] if user_id else row[2],
                    'user_agent': row[3] if user_id else row[3],
                    'login_time': row[4] if user_id else row[4],
                    'logout_time': row[5] if user_id else row[5],
                    'actions_count': row[6] if user_id else row[6],
                    'is_active': bool(row[7] if user_id else row[7])
                }
                for row in results
            ]

        except Exception as e:
            self.security_logger.error(f"Session kayıtları getirme hatası: {e}")
            return []

    # ==================== THREAT DETECTION ====================

    def detect_threat(self, user_id: int, threat_type: str, threat_level: str,
                     description: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Tehdit tespit et ve kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO threat_detection 
                (user_id, threat_type, threat_level, description, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, threat_type, threat_level, description, ip_address, user_agent))

            conn.commit()
            conn.close()

            # Güvenlik olayını kaydet
            self.log_security_event(user_id, "THREAT_DETECTED",
                                  f"{threat_type} tehdidi tespit edildi: {description}",
                                  threat_level, ip_address, user_agent)

            self.security_logger.warning(f"Tehdit tespit edildi - Kullanıcı: {user_id}, Tip: {threat_type}, Seviye: {threat_level}")
            return True

        except Exception as e:
            self.security_logger.error(f"Tehdit tespit kaydetme hatası: {e}")
            return False

    def analyze_login_patterns(self, user_id: int, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Giriş kalıplarını analiz et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Son 30 günün giriş verilerini al
            thirty_days_ago = datetime.now() - timedelta(days=30)

            cursor.execute("""
                SELECT ip_address, login_time, user_agent
                FROM session_recordings 
                WHERE user_id = ? AND login_time >= ?
                ORDER BY login_time DESC
            """, (user_id, thirty_days_ago))

            sessions = cursor.fetchall()
            conn.close()

            if not sessions:
                return {'risk_level': 'LOW', 'anomalies': []}

            # Anomali tespiti
            anomalies = []
            risk_level = 'LOW'

            # Yeni IP adresi kontrolü
            known_ips = set(session[0] for session in sessions)
            if ip_address not in known_ips:
                anomalies.append(f"Yeni IP adresi: {ip_address}")
                risk_level = 'MEDIUM'

            # Yeni user agent kontrolü
            known_agents = set(session[2] for session in sessions if session[2])
            if user_agent not in known_agents:
                anomalies.append(f"Yeni user agent: {user_agent}")
                risk_level = 'MEDIUM'

            # Çok sık giriş kontrolü
            recent_logins = [s for s in sessions if (datetime.now() - datetime.fromisoformat(s[1])).days < 1]
            if len(recent_logins) > 10:
                anomalies.append(f"Çok sık giriş: {len(recent_logins)} giriş son 24 saatte")
                risk_level = 'HIGH'

            # Gece girişi kontrolü
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 22:
                anomalies.append(f"Olağandışı saat: {current_hour}:00")
                risk_level = 'MEDIUM'

            return {
                'risk_level': risk_level,
                'anomalies': anomalies,
                'total_sessions': len(sessions),
                'unique_ips': len(known_ips),
                'unique_agents': len(known_agents)
            }

        except Exception as e:
            self.security_logger.error(f"Giriş kalıp analizi hatası: {e}")
            return {'risk_level': 'UNKNOWN', 'anomalies': []}

    def log_security_event(self, user_id: int, event_type: str, event_description: str,
                          severity: str, ip_address: str = None, user_agent: str = None,
                          additional_data: str = None) -> bool:
        """Güvenlik olayını kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO security_events 
                (user_id, event_type, event_description, severity, ip_address, user_agent, additional_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, event_type, event_description, severity, ip_address, user_agent, additional_data))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            self.security_logger.error(f"Güvenlik olayı kaydetme hatası: {e}")
            return False

    # ==================== PENETRATION TESTING ====================

    def create_penetration_test(self, test_name: str, test_type: str, test_date: datetime,
                              tester_name: str) -> int:
        """Penetration test oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO penetration_tests 
                (test_name, test_type, test_date, tester_name)
                VALUES (?, ?, ?, ?)
            """, (test_name, test_type, test_date, tester_name))

            test_id = cursor.lastrowid
            conn.commit()
            conn.close()

            self.security_logger.info(f"Penetration test oluşturuldu - Test: {test_name}, ID: {test_id}")
            return test_id

        except Exception as e:
            self.security_logger.error(f"Penetration test oluşturma hatası: {e}")
            return 0

    def add_vulnerability(self, test_id: int, vulnerability_name: str, severity: str,
                         description: str, affected_component: str, remediation_steps: str) -> bool:
        """Vulnerability ekle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO vulnerability_details 
                (test_id, vulnerability_name, severity, description, affected_component, remediation_steps)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (test_id, vulnerability_name, severity, description, affected_component, remediation_steps))

            # Test'teki vulnerability sayısını güncelle
            cursor.execute("""
                UPDATE penetration_tests 
                SET vulnerabilities_found = vulnerabilities_found + 1,
                    critical_vulnerabilities = critical_vulnerabilities + CASE WHEN ? = 'Critical' THEN 1 ELSE 0 END,
                    high_vulnerabilities = high_vulnerabilities + CASE WHEN ? = 'High' THEN 1 ELSE 0 END,
                    medium_vulnerabilities = medium_vulnerabilities + CASE WHEN ? = 'Medium' THEN 1 ELSE 0 END,
                    low_vulnerabilities = low_vulnerabilities + CASE WHEN ? = 'Low' THEN 1 ELSE 0 END
                WHERE id = ?
            """, (severity, severity, severity, severity, test_id))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            self.security_logger.error(f"Vulnerability ekleme hatası: {e}")
            return False

    def get_penetration_tests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Penetration testlerini getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, test_name, test_type, test_date, tester_name,
                       vulnerabilities_found, critical_vulnerabilities, high_vulnerabilities,
                       medium_vulnerabilities, low_vulnerabilities, status, created_at
                FROM penetration_tests 
                ORDER BY test_date DESC LIMIT ?
            """, (limit,))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    'id': row[0],
                    'test_name': row[1],
                    'test_type': row[2],
                    'test_date': row[3],
                    'tester_name': row[4],
                    'vulnerabilities_found': row[5],
                    'critical_vulnerabilities': row[6],
                    'high_vulnerabilities': row[7],
                    'medium_vulnerabilities': row[8],
                    'low_vulnerabilities': row[9],
                    'status': row[10],
                    'created_at': row[11]
                }
                for row in results
            ]

        except Exception as e:
            self.security_logger.error(f"Penetration testleri getirme hatası: {e}")
            return []

    def get_vulnerabilities_by_test(self, test_id: int) -> List[Dict[str, Any]]:
        """Test'e ait vulnerability'leri getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, vulnerability_name, severity, description, 
                       affected_component, remediation_steps, status, created_at
                FROM vulnerability_details 
                WHERE test_id = ? 
                ORDER BY severity DESC, created_at DESC
            """, (test_id,))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    'id': row[0],
                    'vulnerability_name': row[1],
                    'severity': row[2],
                    'description': row[3],
                    'affected_component': row[4],
                    'remediation_steps': row[5],
                    'status': row[6],
                    'created_at': row[7]
                }
                for row in results
            ]

        except Exception as e:
            self.security_logger.error(f"Vulnerability'ler getirme hatası: {e}")
            return []

    def analyze_audit_logs_for_threats(self) -> List[Dict[str, Any]]:
        """Audit logları analiz ederek tehditleri tespit et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Son 24 saatteki audit logları
            cursor.execute("""
                SELECT user_id, action, COALESCE(timestamp, created_at) as time, 
                       payload_json, username
                FROM audit_logs 
                WHERE COALESCE(timestamp, created_at) >= datetime('now', '-1 day')
                ORDER BY time DESC
            """)

            logs = cursor.fetchall()
            detected_threats = []

            # Failed login analizi
            failed_logins = {}
            for user_id, action, time, payload, username in logs:
                if 'failed' in action.lower() or 'başarısız' in action.lower():
                    key = user_id or username or 'unknown'
                    failed_logins[key] = failed_logins.get(key, 0) + 1

            # 5'ten fazla başarısız giriş = tehdit
            for user_key, count in failed_logins.items():
                if count >= 5:
                    detected_threats.append({
                        'user_id': user_key if isinstance(user_key, int) else None,
                        'threat_type': 'BRUTE_FORCE',
                        'threat_level': 'HIGH' if count >= 10 else 'MEDIUM',
                        'description': f'{count} başarısız giriş denemesi tespit edildi',
                        'ip_address': None
                    })

            # SQL injection pattern tespiti
            for user_id, action, time, payload, username in logs:
                if payload:
                    payload_lower = payload.lower()
                    if any(pattern in payload_lower for pattern in ['select ', 'drop ', 'union ', '--', 'or 1=1']):
                        detected_threats.append({
                            'user_id': user_id,
                            'threat_type': 'SQL_INJECTION',
                            'threat_level': 'CRITICAL',
                            'description': f'SQL Injection denemesi: {action}',
                            'ip_address': None
                        })

            # Gece saatlerinde yoğun aktivite
            night_activities = [log for log in logs if self._is_night_hour(log[2])]
            if len(night_activities) > 20:
                detected_threats.append({
                    'user_id': None,
                    'threat_type': 'UNUSUAL_ACTIVITY',
                    'threat_level': 'MEDIUM',
                    'description': f'Gece saatlerinde {len(night_activities)} aktivite tespit edildi',
                    'ip_address': None
                })

            # Yeni tehditleri kaydet
            for threat in detected_threats:
                self.detect_threat(
                    threat.get('user_id'),
                    threat['threat_type'],
                    threat['threat_level'],
                    threat['description'],
                    threat.get('ip_address')
                )

            conn.close()

            return detected_threats

        except Exception as e:
            self.security_logger.error(f"Audit log analizi hatası: {e}")
            return []

    def _is_night_hour(self, timestamp_str: str) -> bool:
        """Gece saati kontrolü (22:00 - 06:00)"""
        try:
            if not timestamp_str:
                return False
            dt = datetime.fromisoformat(timestamp_str)
            hour = dt.hour
            return hour >= 22 or hour < 6
        except Exception as e:
            logging.error(f"Night hour check error: {e}")
            return False

    def scan_for_threats_realtime(self) -> Dict[str, Any]:
        """Gerçek zamanlı tehdit taraması yap"""
        try:
            threats_found = self.analyze_audit_logs_for_threats()

            return {
                'success': True,
                'threats_found': len(threats_found),
                'threats': threats_found,
                'scan_time': datetime.now().isoformat()
            }
        except Exception as e:
            self.security_logger.error(f"Tehdit taraması hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_security_report(self, user_id: int = None) -> Dict[str, Any]:
        """Güvenlik raporu oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # MFA istatistikleri
            cursor.execute("SELECT COUNT(*) FROM mfa_settings WHERE mfa_enabled = TRUE")
            mfa_enabled_count = cursor.fetchone()[0]

            # IP whitelist istatistikleri
            cursor.execute("SELECT COUNT(*) FROM ip_whitelist WHERE is_active = TRUE")
            whitelisted_ips_count = cursor.fetchone()[0]

            # Session istatistikleri
            cursor.execute("SELECT COUNT(*) FROM session_recordings WHERE is_active = TRUE")
            active_sessions_count = cursor.fetchone()[0]

            # Tehdit istatistikleri
            cursor.execute("SELECT COUNT(*) FROM threat_detection WHERE is_resolved = FALSE")
            active_threats_count = cursor.fetchone()[0]

            # Güvenlik olayları
            cursor.execute("""
                SELECT severity, COUNT(*) FROM security_events 
                WHERE created_at >= datetime('now', '-30 days')
                GROUP BY severity
            """)
            security_events = dict(cursor.fetchall())

            # Penetration test istatistikleri
            cursor.execute("""
                SELECT COUNT(*), SUM(vulnerabilities_found), 
                       SUM(critical_vulnerabilities), SUM(high_vulnerabilities)
                FROM penetration_tests 
                WHERE test_date >= datetime('now', '-1 year')
            """)
            pen_test_stats = cursor.fetchone()

            conn.close()

            return {
                'mfa_enabled_count': mfa_enabled_count,
                'whitelisted_ips_count': whitelisted_ips_count,
                'active_sessions_count': active_sessions_count,
                'active_threats_count': active_threats_count,
                'security_events': security_events,
                'penetration_tests_count': pen_test_stats[0] or 0,
                'total_vulnerabilities': pen_test_stats[1] or 0,
                'critical_vulnerabilities': pen_test_stats[2] or 0,
                'high_vulnerabilities': pen_test_stats[3] or 0,
                'report_generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.security_logger.error(f"Güvenlik raporu oluşturma hatası: {e}")
            return {}
