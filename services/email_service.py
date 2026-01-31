#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-mail Servisi
"""

import os
import sys
import logging
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Any
from .icons import Icons

# .env dosyasını yükle (varsa)
try:
    from dotenv import load_dotenv
    # Üst dizindeki .env dosyasını yüklemeyi dene
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(env_path)
except ImportError:
    pass

# --- KONFIGURASYON ---

TEST_MODE = os.getenv('TEST_MODE', 'False') == 'True'

# Try to load from centralized JSON config
JSON_CONFIG = {}
try:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, 'backend', 'config', 'smtp_config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            JSON_CONFIG = json.load(f)
except Exception as e:
    logging.warning(f"Failed to load smtp_config.json: {e}")

EMAIL_CONFIG = {
    # SMTP Sunucu Bilgileri
    'smtp_server': JSON_CONFIG.get('smtp_server', os.getenv('SMTP_SERVER', 'smtp.digage.tr')),
    'smtp_port': JSON_CONFIG.get('smtp_port', int(os.getenv('SMTP_PORT', '587'))),
    'use_tls': JSON_CONFIG.get('use_tls', os.getenv('USE_TLS', 'False') == 'True'),

    # Gönderen Bilgileri
    'sender_email': JSON_CONFIG.get('sender_email', os.getenv('SENDER_EMAIL', 'system@digage.tr')),
    'sender_password': JSON_CONFIG.get('sender_password', os.getenv('SENDER_PASSWORD', '')),
    'sender_name': JSON_CONFIG.get('sender_name', os.getenv('SENDER_NAME', 'Sustainage SDG Platform')),

    # E-mail Ayarları
    'enabled': JSON_CONFIG.get('enabled', os.getenv('EMAIL_ENABLED', 'True') == 'True'),
    'max_retries': 3,
    'retry_delay': 5,
}

EMAIL_TEMPLATES = {
    'task_assigned': {
        'subject': ' Yeni Görev Atandı: {task_title}',
        'template': f'''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yeni Görev Atandı</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #2E8B57, #3CB371); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }}
        .content {{ padding: 30px; }}
        .task-card {{ background: #f8f9fa; border-left: 4px solid #2E8B57; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .task-title {{ font-size: 20px; font-weight: 600; color: #2E8B57; margin: 0 0 15px 0; }}
        .task-detail {{ margin: 8px 0; color: #555; }}
        .task-detail strong {{ color: #333; }}
        .priority-high {{ color: #e74c3c; font-weight: 600; }}
        .priority-medium {{ color: #f39c12; font-weight: 600; }}
        .priority-low {{ color: #27ae60; font-weight: 600; }}
        .action-steps {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .action-steps h3 {{ margin: 0 0 15px 0; color: #2E8B57; }}
        .action-steps ol {{ margin: 0; padding-left: 20px; }}
        .action-steps li {{ margin: 8px 0; color: #555; }}
        .deadline {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }}
        .deadline strong {{ color: #856404; font-size: 18px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }}
        .button {{ display: inline-block; background: #2E8B57; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 10px 0; }}
        .button:hover {{ background: #27ae60; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Yeni Görev Atandı</h1>
            <p>Size yeni bir görev atandı!</p>
        </div>
        
        <div class="content">
            <div class="task-card">
                <div class="task-title">{{task_title}}</div>
                <div class="task-detail"><strong>Açıklama:</strong> {{task_description}}</div>
                <div class="task-detail"><strong>Öncelik:</strong> <span class="priority-{{priority.lower()}}">{{priority}}</span></div>
                <div class="task-detail"><strong>Bitiş Tarihi:</strong> {{due_date}}</div>
                <div class="task-detail"><strong>Atayan:</strong> {{assigned_by}}</div>
            </div>
            
            <div class="action-steps">
                <h3> Yapmanız Gerekenler</h3>
                <ol>
                    <li>Sisteme giriş yapın</li>
                    <li>"Görevlerim" bölümüne gidin</li>
                    <li>Görevi inceleyin ve detaylarını okuyun</li>
                    <li>Görevi kabul edin veya reddedin</li>
                    <li>Veri girişi yapın ve ilerleme kaydedin</li>
                </ol>
            </div>
            
            <div class="deadline">
                <strong>{Icons.TIME} Son Tarih: {{due_date}}</strong>
            </div>
            
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{task_url}}" class="button">Sisteme Giriş Yap</a>
                </div>
        </div>
        
        <div class="footer">
            <p>Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.</p>
            <p>Sorularınız için lütfen yöneticinize başvurun.</p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'new_user_welcome': {
        'subject': ' Hoş Geldiniz: {program_name}',
        'template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hoş Geldiniz</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .container { max-width: 640px; margin: 24px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }
        .header { background: #0B5ED7; color: white; padding: 28px; text-align: center; }
        .logo { margin-bottom: 14px; }
        .logo img { width: 64px; height: 64px; border-radius: 50%; box-shadow: 0 2px 10px rgba(0,0,0,0.15); }
        .header h1 { margin: 0; font-size: 22px; font-weight: 600; }
        .header p { margin: 8px 0 0; opacity: 0.95; font-size: 15px; }
        /* Header içindeki metin beyaz okunabilir olsun */
        .header .muted { color: #fff; }
        .content { padding: 28px; color: #333; }
        .card { background: #f8f9fa; border-left: 4px solid #0B5ED7; padding: 18px; margin: 18px 0; border-radius: 8px; }
        .card-title { font-size: 18px; font-weight: 600; color: #0B5ED7; margin: 0 0 12px; }
        .muted { color: #666; }
        .info { margin: 10px 0; }
        .button { display: inline-block; background: #0B5ED7; color: white; padding: 12px 22px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 14px 0; }
        .button:hover { background: #0A53BE; }
        .footer { background: #f8f9fa; padding: 16px; text-align: center; color: #666; font-size: 13px; border-top: 1px solid #e9ecef; }
    </style>
 </head>
 <body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <!-- Inline görsel: cid:sustainage_logo olarak eklenecek -->
                <img src="cid:sustainage_logo" alt="Sustainage Logo" width="72" height="72" style="display:block;width:72px;height:72px;margin:12px auto 8px;" />
            </div>
            <h1>{program_name}</h1>
            <p class="muted">Sustainage SDG Platformuna hoş geldiniz!</p>
        </div>

        <div class="content">
            <div class="card">
                <div class="card-title">Yeni Kullanıcı Tanımlandı</div>
                <div class="info">Merhaba <strong>{user_name}</strong>,</div>
                <div class="info">{short_description}</div>
                <div class="info muted">Bu e-posta, sizin adınıza yeni bir kullanıcı hesabı tanımlandığı için gönderilmiştir.</div>
            </div>

            <p>Hesabınıza giriş yapmak için aşağıdaki bağlantıyı kullanabilirsiniz:</p>
            <p style="text-align: center;">
                <a href="{login_url}" class="button">Sisteme Giriş Yap</a>
            </p>

            <p class="muted">Herhangi bir sorunuz olduğunda bizimle iletişime geçebilirsiniz: <strong>{support_email}</strong></p>
        </div>

        <div class="footer">
            <p>Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
 </body>
 </html>
        '''
    },

    'new_user_credentials': {
        'subject': ' Yeni Kullanıcı Bilgileri ve Geçici Şifre',
        'template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yeni Kullanıcı Bilgileri</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .container { max-width: 640px; margin: 24px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }
        .header { background: #2E8B57; color: white; padding: 28px; text-align: center; }
        .logo { margin-bottom: 14px; }
        .logo img { width: 64px; height: 64px; border-radius: 50%; box-shadow: 0 2px 10px rgba(0,0,0,0.15); }
        .header h1 { margin: 0; font-size: 22px; font-weight: 600; }
        .header p { margin: 8px 0 0; opacity: 0.95; font-size: 15px; }
        .content { padding: 28px; color: #333; }
        .card { background: #f8f9fa; border-left: 4px solid #2E8B57; padding: 18px; margin: 18px 0; border-radius: 8px; }
        .card-title { font-size: 18px; font-weight: 600; color: #2E8B57; margin: 0 0 12px; }
        .credentials { background: #eef7ea; padding: 16px; border-radius: 8px; margin: 16px 0; }
        .credentials div { margin: 6px 0; }
        .button { display: inline-block; background: #2E8B57; color: white; padding: 12px 22px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 14px 0; }
        .button:hover { background: #3CB371; }
        .footer { background: #f8f9fa; padding: 16px; text-align: center; color: #666; font-size: 13px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="cid:sustainage_logo" alt="Sustainage Logo" width="72" height="72" style="display:block;width:72px;height:72px;margin:12px auto 8px;" />
            </div>
            <h1>Kullanıcı Giriş Bilgileri</h1>
            <p>Hesap bilgileriniz oluşturuldu.</p>
        </div>

        <div class="content">
            <div class="card">
                <div class="card-title">Merhaba {user_name},</div>
                <div class="info">Aşağıdaki bilgilerle sisteme giriş yapabilirsiniz. Lütfen ilk girişinizde şifrenizi değiştirin.</div>
            </div>

            <div class="credentials">
                <div><strong>Kullanıcı Adı:</strong> {username}</div>
                <div><strong>Geçici Şifre:</strong> {temp_password}</div>
            </div>

            <p style="text-align: center;">
                <a href="{login_url}" class="button">Sisteme Giriş Yap</a>
            </p>

            <p class="muted">Güvenliğiniz için bu bilgileri kimseyle paylaşmayınız.</p>
        </div>

        <div class="footer">
            <p>Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'survey_invitation': {
        'subject': ' Anket Daveti: {survey_name}',
        'template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anket Daveti</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #2E8B57; color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
        .content { padding: 30px; }
        .info-box { background: #e8f5e8; border-left: 4px solid #2E8B57; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .button { display: inline-block; background: #2E8B57; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 10px 0; }
        .button:hover { background: #27ae60; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sustainage Anket Daveti</h1>
        </div>
        
        <div class="content">
            <p>Merhaba <strong>{stakeholder_name}</strong>,</p>
            <p>{company_name} olarak sürdürülebilirlik hedeflerimiz doğrultusunda görüşlerinize değer veriyoruz.</p>
            
            <div class="info-box">
                <h3>{survey_name}</h3>
                <p>{survey_description}</p>
                <p><strong>Son Katılım Tarihi:</strong> {deadline_date}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{survey_url}" class="button">Ankete Katıl</a>
            </div>
            
            <p>Katkılarınız için teşekkür ederiz.</p>
        </div>
        
        <div class="footer">
            <p>Bu e-posta Sustainage SDG Platform tarafından gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'survey_reminder': {
        'subject': ' Anket Hatırlatma: {survey_name}',
        'template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anket Hatırlatma</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #FFA500; color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
        .content { padding: 30px; }
        .info-box { background: #fff3cd; border-left: 4px solid #FFA500; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .button { display: inline-block; background: #FFA500; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 10px 0; }
        .button:hover { background: #e69500; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Anket Hatırlatma</h1>
        </div>
        
        <div class="content">
            <p>Merhaba <strong>{stakeholder_name}</strong>,</p>
            <p>{company_name} tarafından gönderilen anket için son katılım tarihi yaklaşmaktadır.</p>
            
            <div class="info-box">
                <h3>{survey_name}</h3>
                <p><strong>Son Tarih:</strong> {deadline_date}</p>
                <p><strong>Kalan Gün:</strong> {days_left}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{survey_url}" class="button">Ankete Git</a>
            </div>
            
            <p>Henüz katılmadıysanız, lütfen en kısa sürede anketimizi tamamlayın.</p>
        </div>
        
        <div class="footer">
            <p>Bu e-posta Sustainage SDG Platform tarafından gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'survey_thank_you': {
        'subject': ' Teşekkürler: {survey_name}',
        'template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teşekkürler</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #2E8B57; color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
        .content { padding: 30px; text-align: center; }
        .success-icon { font-size: 48px; color: #2E8B57; margin-bottom: 20px; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Teşekkürler!</h1>
        </div>
        
        <div class="content">
            <div class="success-icon">✓</div>
            <p>Merhaba <strong>{stakeholder_name}</strong>,</p>
            <p><strong>{survey_name}</strong> anketine katılımınız başarıyla kaydedilmiştir.</p>
            <p>Değerli görüşleriniz sürdürülebilirlik yolculuğumuzda bize ışık tutacaktır.</p>
            
            <p style="margin-top: 30px; font-size: 14px; color: #666;">
                Yanıt Tarihi: {response_date}
            </p>
        </div>
        
        <div class="footer">
            <p>Bu e-posta Sustainage SDG Platform tarafından gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'task_updated': {
        'subject': ' Görev Güncellendi: {task_title}',
        'template': '''
GÖREV DETAYLARI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Başlık: {task_title}
Yeni Durum: {status}
İlerleme: %{progress}
Güncelleme Notu: {note}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Görevin detaylarını görmek için lütfen sisteme giriş yapın.

---
Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.
        '''
    },

    'task_completed': {
        'subject': ' Görev Tamamlandı: {task_title}',
        'template': '''
GÖREV TAMAMLANDI!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Başlık: {task_title}
Tamamlanma Tarihi: {completion_date}
Tamamlayan: {completed_by}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Onaylamak için lütfen sisteme giriş yapın.

---
Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.
        '''
    },
    
    'password_reset': {
        'subject': ' Şifre Sıfırlama Talebi',
        'template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Şifre Sıfırlama</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #d35400; color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
        .content { padding: 30px; }
        .code-box { background: #fdf2e9; border: 1px solid #fae5d3; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }
        .code { font-size: 32px; font-weight: 700; color: #d35400; letter-spacing: 5px; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Şifre Sıfırlama</h1>
            <p>Hesabınız için şifre sıfırlama talebi aldık.</p>
        </div>
        
        <div class="content">
            <p>Merhaba <strong>{user_name}</strong>,</p>
            <p>Aşağıdaki kodu kullanarak şifrenizi sıfırlayabilirsiniz. Bu kod 10 dakika süreyle geçerlidir.</p>
            
            <div class="code-box">
                <div class="code">{reset_code}</div>
            </div>
            
            <p>Eğer bu talebi siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
            <p>Sorularınız için: <strong>{support_email}</strong></p>
        </div>
        
        <div class="footer">
            <p>Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        '''
    }
}

class EmailService:
    """E-mail gönderim servisi"""

    def __init__(self) -> None:
        self.config = EMAIL_CONFIG.copy()
        self.templates = EMAIL_TEMPLATES.copy()
        self.test_mode = TEST_MODE
        
        # Ensure config is up to date from env (in case env loaded after import)
        # (Already done in EMAIL_CONFIG definition above, but good for runtime updates if needed)

    def _replace_icons(self, text: str) -> str:
        """Replace Icons.XXX with actual icon values"""
        if not text:
            return text
        
        if "Icons." not in text:
            return text
        
        # Sort attributes by length descending
        attrs = [a for a in dir(Icons) if a.isupper() and not a.startswith('_')]
        attrs.sort(key=len, reverse=True)
        
        for attr in attrs:
            token = f"Icons.{attr}"
            if token in text:
                text = text.replace(token, getattr(Icons, attr))
        return text

    def send_email(self, to_email: str, subject: str, body: str, to_name: str = None, cc: str = None, bcc: str = None, attachments: List[str] = None) -> bool:
        """E-mail gönder"""

        if not self.config['enabled'] and not self.test_mode:
            logging.info(f"[BILGI] E-mail servisi devre disi. E-mail gonderilmedi: {to_email}")
            return False

        # İkonları değiştir
        subject = self._replace_icons(subject)
        body = self._replace_icons(body)

        if self.test_mode:
            logging.info("\n" + "=" * 80)
            logging.info("TEST MODU - E-MAIL GONDERILMEDI")
            logging.info("=" * 80)
            logging.info(f"Kime: {to_name} <{to_email}>")
            logging.info(f"Konu: {subject}")
            logging.info("-" * 80)
            logging.info("Body hidden (HTML)")
            logging.info("=" * 80 + "\n")
            return True

        try:
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.config['sender_name']} <{self.config['sender_email']}>"
            message['To'] = f"{to_name} <{to_email}>" if to_name else to_email
            if cc: message['Cc'] = cc
            if bcc: message['Bcc'] = bcc
            message['Subject'] = subject

            if body.strip().startswith('<!DOCTYPE html>') or body.strip().startswith('<html'):
                html_part = MIMEText(body, 'html', 'utf-8')
                message.attach(html_part)
            else:
                text_part = MIMEText(body, 'plain', 'utf-8')
                message.attach(text_part)

            if attachments:
                for filepath in attachments:
                    try:
                        if os.path.exists(filepath):
                            filename = os.path.basename(filepath)
                            with open(filepath, "rb") as attachment:
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
                            message.attach(part)
                    except Exception as e:
                        logging.error(f"[HATA] Ek dosyasi eklenemedi ({filepath}): {e}")

            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                if self.config['use_tls']:
                    server.starttls()
                server.login(self.config['sender_email'], self.config['sender_password'])
                server.send_message(message)

            logging.info(f"[OK] E-mail gonderildi: {to_email}")
            return True

        except Exception as e:
            logging.error(f"[HATA] E-mail gonderilemedi ({to_email}): {e}")
            return False

    def render_template(self, template_key: str, variables: dict) -> tuple:
        tpl = self.templates.get(template_key)
        if not tpl:
            raise ValueError(f"Şablon bulunamadı: {template_key}")
        subject = tpl.get('subject', '').format(**variables)
        html = tpl.get('template', '')
        for k, v in (variables or {}).items():
            token = '{' + str(k) + '}'
            html = html.replace(token, str(v))
        return subject, html

    def send_template_email(self, to_email: str, template_key: str, variables: dict) -> bool:
        try:
            subject, html = self.render_template(template_key, variables)
            return self.send_email(to_email, subject, html)
        except Exception as e:
            logging.error(f"Template email sending failed: {e}")
            return False

    def send_template_email_with_result(self, to_email: str, template_key: str, variables: dict) -> dict:
        try:
            subject, html = self.render_template(template_key, variables)
            success = self.send_email(to_email, subject, html)
            if success:
                return {'success': True}
            else:
                return {'success': False, 'error': 'SMTP send failed'}
        except Exception as e:
            logging.error(f"Template email sending failed: {e}")
            return {'success': False, 'error': str(e)}

    def send_password_reset_email(self, to_email: str, user_name: str, reset_code: str) -> bool:
        """Şifre sıfırlama emaili gönder"""
        template = self.templates['password_reset']
        subject = template['subject']
        html_content = template['template']
        
        variables = {
            'user_name': user_name,
            'reset_code': reset_code,
            'support_email': 'support@sustainage.tr'
        }
        
        for k, v in variables.items():
            token = '{' + str(k) + '}'
            html_content = html_content.replace(token, str(v))
            
        return self.send_email(to_email, subject, html_content, to_name=user_name)
