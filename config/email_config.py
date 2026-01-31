#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-mail Konfigürasyonu
SMTP ayarları ve e-mail gönderim yapılandırması
"""

import os
from config.icons import Icons

# SMTP Ayarları
TEST_MODE = os.getenv('TEST_MODE', 'False') == 'True'
EMAIL_CONFIG = {
    # SMTP Sunucu Bilgileri - Digage
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.digage.tr'),  # Digage SMTP
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),  # Port 587
    'use_tls': os.getenv('USE_TLS', 'False') == 'True',  # TLS/SSL yok

    # Gönderen Bilgileri
    'sender_email': os.getenv('SENDER_EMAIL', 'system@digage.tr'),
    'sender_password': os.getenv('SENDER_PASSWORD', ''),  # Şifre (ENV ile girin)
    'sender_name': os.getenv('SENDER_NAME', 'Sustainage SDG Platform'),

    # E-mail Ayarları
    'enabled': os.getenv('EMAIL_ENABLED', 'True') == 'True',  # Varsayılan açık (gerçek gönderim)
    'max_retries': 3,
    'retry_delay': 5,  # saniye
}

# E-mail Şablonları
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
