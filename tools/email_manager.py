import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Manager - Mail Gönderme Sistemi
SMTP ile mail gönderme, şifre sıfırlama ve anket dağıtımı
"""

import json
import os
import poplib
import secrets
import smtplib
import sqlite3
import ssl
import string
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

import sys

# Add project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EmailManager:
    """Email gönderme yöneticisi"""
    
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self.smtp_config = self.load_smtp_config()
        self.email_templates = self.load_email_templates()
        
    def _decrypt_password(self, encrypted_password: str) -> str:
        """Decrypts the password if a key file exists"""
        key_file = "config/smtp.key"
        if not os.path.exists(key_file) or not Fernet:
            return encrypted_password
            
        try:
            with open(key_file, "rb") as kf:
                key = kf.read()
            f = Fernet(key)
            return f.decrypt(encrypted_password.encode()).decode()
        except Exception as e:
            logging.error(f"Password decryption failed: {e}")
            return encrypted_password

    def load_smtp_config(self) -> Dict:
        """SMTP ayarlarını yükle"""
        # Use backend config path
        config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/config/smtp_config.json'))
        
        # Varsayılan ayarlar
        default_config = {
            "smtp_server": "smtp.digage.tr",
            "smtp_port": 587,
            "sender_email": "sdg@digage.tr",
            "sender_password": "",
            "use_tls": True,
            "use_auth": True,
            "sender_name": "SUSTAINAGE SDG",
            "pop3_server": "pop3.digage.tr",
            "pop3_port": 995,
            "use_pop3_ssl": True,
            "web_base_url": os.getenv("WEB_BASE_URL", "http://localhost:8080"),
            "is_encrypted": False
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    # Eksik anahtarlar için varsayılanları uygula
                    for k, v in default_config.items():
                        if k not in cfg:
                            cfg[k] = v
                    # Reply-To ve alias destekleri
                    if 'reply_to' not in cfg:
                        cfg['reply_to'] = None
                    
                    # Decrypt password if flagged as encrypted
                    if cfg.get("is_encrypted", False):
                        cfg["sender_password"] = self._decrypt_password(cfg["sender_password"])
                        
                    return cfg
            else:
                # Config dosyası oluştur
                os.makedirs("config", exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                return default_config
        except Exception as e:
            logging.error(f"SMTP config yükleme hatası: {e}")
            return default_config
        finally:
            try:
                env_email = os.getenv('SENDER_EMAIL')
                env_pass = os.getenv('SENDER_PASSWORD')
                env_host = os.getenv('SMTP_SERVER')
                env_port = os.getenv('SMTP_PORT')
                env_tls = os.getenv('USE_TLS')
                env_auth = os.getenv('SMTP_USE_AUTH')
                if env_email:
                    default_config['sender_email'] = env_email
                if env_pass:
                    default_config['sender_password'] = env_pass
                if env_host:
                    default_config['smtp_server'] = env_host
                if env_port:
                    try:
                        default_config['smtp_port'] = int(env_port)
                    except Exception as e:
                        logging.error(f"Silent error caught: {str(e)}")
                if env_tls in ('True', 'False'):
                    default_config['use_tls'] = (env_tls == 'True')
                if env_auth in ('True', 'False'):
                    default_config['use_auth'] = (env_auth == 'True')
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
    
    def load_email_templates(self) -> Dict:
        """Email şablonlarını yükle"""
        templates = {
            "password_reset": {
                "subject": "SUSTAINAGE SDG - Şifre Sıfırlama",
                "html_template": """
                <html>
                <body style="font-family: Segoe UI, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background-color: #2E8B57; color: white; padding: 20px; text-align: center;">
                            <h1>SUSTAINAGE SDG</h1>
                        </div>
                        
                        <div style="padding: 30px; background-color: #f9f9f9;">
                            <h2>Şifre Sıfırlama Talebi</h2>
                            <p>Merhaba <strong>{username}</strong>,</p>
                            <p>SUSTAINAGE SDG sisteminde şifre sıfırlama talebinde bulundunuz.</p>
                            
                            <div style="background-color: white; padding: 20px; border-left: 4px solid #2E8B57; margin: 20px 0;">
                                <p><strong>Kullanıcı Adı:</strong> {username}</p>
                                <p><strong>Sıfırlama Kodu:</strong> <code style="background-color: #f0f0f0; padding: 5px;">{reset_token}</code></p>
                                <p><strong>Geçerlilik Süresi:</strong> 1 saat</p>
                            </div>
                            
                            <p><strong>Şifrenizi sıfırlamak için:</strong></p>
                            <ol>
                                <li>Aşağıdaki bağlantıya tıklayın</li>
                                <li>Sıfırlama kodunu girin</li>
                                <li>Yeni şifrenizi belirleyin</li>
                            </ol>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{reset_url}" style="background-color: #2E8B57; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Şifremi Sıfırla</a>
                            </div>
                            
                            <p><strong>Önemli Güvenlik Uyarıları:</strong></p>
                            <ul>
                                <li>Bu bağlantı sadece 1 saat geçerlidir</li>
                                <li>Bağlantıyı kimseyle paylaşmayın</li>
                                <li>Şüpheli aktivite fark ederseniz hemen sistem yöneticisiyle iletişime geçin</li>
                            </ul>
                        </div>
                        
                        <div style="background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px;">
                            <p>Bu email SUSTAINAGE SDG sistemi tarafından otomatik olarak gönderilmiştir.</p>
                            <p>Bu talebi siz yapmadıysanız, lütfen sistem yöneticisiyle iletişime geçin.</p>
                        </div>
                    </div>
                </body>
                </html>
                """,
                "text_template": """
                SUSTAINAGE SDG - Şifre Sıfırlama
                
                Merhaba {username},
                
                SUSTAINAGE SDG sisteminde şifre sıfırlama talebinde bulundunuz.
                
                Kullanıcı Adı: {username}
                Sıfırlama Kodu: {reset_token}
                Geçerlilik Süresi: 1 saat
                
                Şifrenizi sıfırlamak için bu bağlantıya tıklayın:
                {reset_url}
                
                Önemli: Bu bağlantı sadece 1 saat geçerlidir!
                
                Bu email otomatik olarak gönderilmiştir.
                """
            },
            
            "survey_invitation": {
                "subject": "SUSTAINAGE SDG - Anket Daveti",
                "html_template": """
                <html>
                <body style="font-family: Segoe UI, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background-color: #2E8B57; color: white; padding: 20px; text-align: center;">
                            <h1>SUSTAINAGE SDG</h1>
                        </div>
                        
                        <div style="padding: 30px; background-color: #f9f9f9;">
                            <h2>Anket Daveti</h2>
                            <p>Merhaba <strong>{recipient_name}</strong>,</p>
                            <p>Sürdürülebilirlik raporlama sürecimizde sizin görüşlerinize ihtiyacımız var.</p>
                            
                            <div style="background-color: white; padding: 20px; border-left: 4px solid #2E8B57; margin: 20px 0;">
                                <h3>{survey_title}</h3>
                                <p><strong>Açıklama:</strong> {survey_description}</p>
                                <p><strong>Tahmini Süre:</strong> {estimated_time} dakika</p>
                                <p><strong>Son Tarih:</strong> {deadline}</p>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{survey_url}" style="background-color: #2E8B57; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Ankete Katıl</a>
                            </div>
                            
                            <p><strong>Anket Kodu:</strong> <code style="background-color: #f0f0f0; padding: 5px;">{survey_code}</code></p>
                        </div>
                        
                        <div style="background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px;">
                            <p>Bu email SUSTAINAGE SDG sistemi tarafından gönderilmiştir.</p>
                        </div>
                    </div>
                </body>
                </html>
                """,
                "text_template": """
                SUSTAINAGE SDG - Anket Daveti
                
                Merhaba {recipient_name},
                
                {survey_title}
                
                Açıklama: {survey_description}
                Tahmini Süre: {estimated_time} dakika
                Son Tarih: {deadline}
                
                Ankete katılmak için: {survey_url}
                Anket Kodu: {survey_code}
                
                Görüşleriniz bizim için değerlidir.
                """
            },

            "survey_reminder": {
                "subject": "SUSTAINAGE SDG - Anket Hatırlatması",
                "html_template": """
                <html>
                <body style="font-family: Segoe UI, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background-color: #2E8B57; color: white; padding: 20px; text-align: center;">
                            <h1>SUSTAINAGE SDG</h1>
                        </div>
                        
                        <div style="padding: 30px; background-color: #f9f9f9;">
                            <h2>Anket Hatırlatması</h2>
                            <p>Merhaba <strong>{recipient_name}</strong>,</p>
                            <p>Aşağıdaki anket için katılımınızı bekliyoruz. Henüz tamamlamadıysanız, lütfen en kısa sürede tamamlayınız.</p>
                            
                            <div style="background-color: white; padding: 20px; border-left: 4px solid #FFA500; margin: 20px 0;">
                                <h3>{survey_title}</h3>
                                <p><strong>Açıklama:</strong> {survey_description}</p>
                                <p><strong>Son Tarih:</strong> {deadline}</p>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{survey_url}" style="background-color: #2E8B57; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px;">Ankete Git</a>
                            </div>
                        </div>
                        
                        <div style="background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px;">
                            <p>Bu email SUSTAINAGE SDG sistemi tarafından gönderilmiştir.</p>
                        </div>
                    </div>
                </body>
                </html>
                """,
                "text_template": """
                SUSTAINAGE SDG - Anket Hatırlatması
                
                Merhaba {recipient_name},
                
                Aşağıdaki anket için katılımınızı bekliyoruz:
                
                {survey_title}
                Son Tarih: {deadline}
                
                Ankete gitmek için: {survey_url}
                """
            },

            "survey_thank_you": {
                "subject": "SUSTAINAGE SDG - Teşekkürler",
                "html_template": """
                <html>
                <body style="font-family: Segoe UI, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background-color: #2E8B57; color: white; padding: 20px; text-align: center;">
                            <h1>SUSTAINAGE SDG</h1>
                        </div>
                        
                        <div style="padding: 30px; background-color: #f9f9f9;">
                            <h2>Teşekkürler</h2>
                            <p>Merhaba <strong>{recipient_name}</strong>,</p>
                            <p><strong>{survey_title}</strong> anketini tamamladığınız için teşekkür ederiz.</p>
                            <p>Görüşleriniz sürdürülebilirlik hedeflerimize ulaşmamızda bize yol gösterecektir.</p>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <p style="color: #2E8B57; font-size: 18px; font-weight: bold;">Katılımınız Başarıyla Kaydedildi</p>
                            </div>
                        </div>
                        
                        <div style="background-color: #333; color: white; padding: 15px; text-align: center; font-size: 12px;">
                            <p>Bu email SUSTAINAGE SDG sistemi tarafından gönderilmiştir.</p>
                        </div>
                    </div>
                </body>
                </html>
                """,
                "text_template": """
                SUSTAINAGE SDG - Teşekkürler
                
                Merhaba {recipient_name},
                
                {survey_title} anketini tamamladığınız için teşekkür ederiz.
                
                Katılımınız başarıyla kaydedildi.
                """
            }
        }
        
        return templates
    
    def generate_temp_password(self, length: int = 12) -> str:
        """Geçici şifre oluştur"""
        characters = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def send_password_reset_email(self, username: str, reset_token: str, email: str) -> bool:
        """Şifre sıfırlama emaili gönder (token tabanlı)"""
        try:
            # Email şablonunu hazırla
            template = self.email_templates["password_reset"]
            
            # Reset URL oluştur (token ile)
            base_url = self.smtp_config.get("web_base_url") or os.getenv("WEB_BASE_URL", "http://localhost:8080")
            base_url = base_url.rstrip('/')
            reset_url = f"{base_url}/reset-password?token={reset_token}"
            
            # Template değişkenlerini doldur
            html_content = template["html_template"].format(
                username=username,
                reset_token=reset_token,
                reset_url=reset_url
            )
            
            text_content = template["text_template"].format(
                username=username,
                reset_token=reset_token,
                reset_url=reset_url
            )
            
            # Email gönder
            result = self.send_email(
                to_email=email,
                subject=template["subject"],
                html_content=html_content,
                text_content=text_content
            )
            
            return result["success"]
            
        except Exception as e:
            logging.error(f"Şifre sıfırlama emaili gönderme hatası: {e}")
            return False
    
    def send_survey_invitation(self, recipient_email: str, recipient_name: str, 
                              survey_data: Dict) -> Dict:
        """Anket davet emaili gönder"""
        try:
            template = self.email_templates["survey_invitation"]
            
            # Template değişkenlerini doldur
            base_url = (self.smtp_config.get("web_base_url") or os.getenv("WEB_BASE_URL", "http://localhost:8080")).rstrip('/')
            token = survey_data.get("token")
            default_survey_url = f"{base_url}/survey.php" + (f"?token={token}" if token else "")
            html_content = template["html_template"].format(
                recipient_name=recipient_name,
                survey_title=survey_data.get("title", "Sürdürülebilirlik Anketi"),
                survey_description=survey_data.get("description", ""),
                estimated_time=survey_data.get("estimated_time", "10"),
                deadline=survey_data.get("deadline", "Belirtilmemiş"),
                survey_url=survey_data.get("url", default_survey_url),
                survey_code=survey_data.get("code", "N/A")
            )
            
            text_content = template["text_template"].format(
                recipient_name=recipient_name,
                survey_title=survey_data.get("title", "Sürdürülebilirlik Anketi"),
                survey_description=survey_data.get("description", ""),
                estimated_time=survey_data.get("estimated_time", "10"),
                deadline=survey_data.get("deadline", "Belirtilmemiş"),
                survey_url=survey_data.get("url", default_survey_url),
                survey_code=survey_data.get("code", "N/A")
            )
            
            # Email gönder
            result = self.send_email(
                to_email=recipient_email,
                subject=template["subject"],
                html_content=html_content,
                text_content=text_content
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Anket davet emaili gönderme hatası: {str(e)}"
            }
    
    def send_email(self, to_email: str, subject: str, 
                   html_content: str = None, text_content: str = None,
                   attachments: List[str] = None) -> Dict:
        """Email gönder"""
        try:
            # Email mesajı oluştur
            msg = MIMEMultipart('alternative')
            sender_name = self.smtp_config.get('sender_name', 'SUSTAINAGE SDG')
            sender_email = self.smtp_config.get('sender_email', '')
            msg['From'] = f"{sender_name} <{sender_email}>" if sender_email else sender_name
            msg['To'] = to_email
            msg['Subject'] = subject
            if self.smtp_config.get('reply_to'):
                msg['Reply-To'] = self.smtp_config.get('reply_to')
            
            # Text ve HTML içerik ekle
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            if html_content:
                part2 = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(part2)
            
            # Ek dosyalar ekle
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            msg.attach(part)
            
            # SMTP bağlantısı kur ve email gönder
            context = ssl.create_default_context()
            if not self.smtp_config.get('validate_ssl', True):
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                if self.smtp_config.get('use_tls', True):
                    server.starttls(context=context)
                if self.smtp_config.get('use_auth', True) and self.smtp_config.get('sender_email') and self.smtp_config.get('sender_password'):
                    server.login(self.smtp_config['sender_email'], self.smtp_config['sender_password'])
                server.send_message(msg)
            
            return {
                "success": True,
                "message": f"Email başarıyla gönderildi: {to_email}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Email gönderme hatası: {str(e)}"
            }
    
    def save_temp_password(self, username: str, temp_password: str) -> bool:
        """Geçici şifreyi veritabanına kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Geçici şifre tablosu oluştur (yoksa)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS temp_passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) NOT NULL,
                    temp_password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    used BOOLEAN DEFAULT 0
                )
            """)
            
            # Eski geçici şifreleri temizle
            cursor.execute("DELETE FROM temp_passwords WHERE username = ?", (username,))
            
            # Yeni geçici şifreyi kaydet (24 saat geçerli)
            #  GÜVENLİK: Argon2 kullanılıyor
            from yonetim.security.core.crypto import hash_password
            expires_at = datetime.now() + timedelta(hours=24)
            temp_password_hash = hash_password(temp_password)
            
            cursor.execute("""
                INSERT INTO temp_passwords (username, temp_password, expires_at)
                VALUES (?, ?, ?)
            """, (username, temp_password_hash, expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Geçici şifre kaydetme hatası: {e}")
            return False
    
    def verify_temp_password(self, username: str, temp_password: str) -> bool:
        """Geçici şifreyi doğrula"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            #  GÜVENLİK: Geriye dönük uyumlu doğrulama
            temp_password_hash = temp_password  # Ham şifre (verify_password_compat kullanacağız)
            
            cursor.execute("""
                SELECT id FROM temp_passwords 
                WHERE username = ? AND temp_password = ? AND used = 0 
                AND expires_at > datetime('now')
            """, (username, temp_password_hash))
            
            result = cursor.fetchone()
            
            if result:
                # Geçici şifreyi kullanılmış olarak işaretle
                cursor.execute("""
                    UPDATE temp_passwords SET used = 1 
                    WHERE id = ?
                """, (result[0],))
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            logging.error(f"Geçici şifre doğrulama hatası: {e}")
            return False

    # Bağlantı test metodunu sınıf dışında sağlayacağız
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Kullanıcı bilgilerini getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, display_name, email, is_active
                FROM users 
                WHERE username = ? AND is_active = 1
            """, (username,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    "id": user[0],
                    "username": user[1],
                    "display_name": user[2],
                    "email": user[3],
                    "is_active": user[4]
                }
            return None
            
        except Exception as e:
            logging.error(f"Kullanıcı bilgisi getirme hatası: {e}")
            return None

# Test fonksiyonu
def test_connection_from_config() -> Dict:
    """Config dosyasına göre SMTP ve POP3 bağlantı testlerini yap"""
    # Config yükle
    try:
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/config/smtp_config.json'))
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    except Exception as e:
        return {"smtp": {"success": False, "message": f"Config okunamadı: {e}"},
                "pop3": {"success": False, "message": "Config okunamadı"}}

    results = {"smtp": {"success": False, "message": ""},
               "pop3": {"success": False, "message": ""}}

    # SMTP test
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(cfg['smtp_server'], int(cfg['smtp_port']), timeout=10) as server:
            if cfg.get('use_tls', True):
                server.starttls(context=context)
            if cfg.get('use_auth', True) and cfg.get('sender_email') and cfg.get('sender_password'):
                server.login(cfg['sender_email'], cfg['sender_password'])
        results["smtp"] = {"success": True, "message": "SMTP bağlantısı başarılı"}
    except Exception as e:
        results["smtp"] = {"success": False, "message": f"SMTP hata: {e}"}

    # POP3 test
    try:
        pop3_host = cfg.get('pop3_server')
        pop3_port = int(cfg.get('pop3_port', 110))
        use_ssl = bool(cfg.get('use_pop3_ssl', False))
        if not pop3_host:
            raise Exception('POP3 yapılandırılmamış')
        if use_ssl:
            pop = poplib.POP3_SSL(pop3_host, pop3_port, timeout=10)
        else:
            pop = poplib.POP3(pop3_host, pop3_port, timeout=10)
        if cfg.get('sender_email') and cfg.get('sender_password'):
            pop.user(cfg['sender_email'])
            pop.pass_(cfg['sender_password'])
        count, _ = pop.stat()
        pop.quit()
        results["pop3"] = {"success": True, "message": f"POP3 bağlantısı başarılı, kutuda {count} mesaj"}
    except Exception as e:
        results["pop3"] = {"success": False, "message": f"POP3 hata: {e}"}

    return results

def test_email_system() -> None:
    """Email sistemini test et"""
    email_manager = EmailManager()
    
    logging.info("=== EMAIL SİSTEMİ TEST ===")
    logging.info(f"SMTP Server: {email_manager.smtp_config['smtp_server']}")
    logging.info(f"Sender Email: {email_manager.smtp_config['sender_email']}")
    
    # SMTP ve POP3 bağlantı testleri
    logging.info("\nBağlantı testleri yapılıyor...")
    results = test_connection_from_config()
    logging.info(f"SMTP: {results['smtp']}")
    logging.info(f"POP3: {results['pop3']}")

if __name__ == "__main__":
    test_email_system()
