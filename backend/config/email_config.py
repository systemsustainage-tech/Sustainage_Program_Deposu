#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E-mail Konfigürasyonu
SMTP ayarları ve e-mail gönderim yapılandırması
"""

import os
from config.icons import Icons

# SMTP Ayarları
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
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .warning strong { color: #856404; }
        .footer { background: #f8f9fa; padding: 16px; text-align: center; color: #666; font-size: 13px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="cid:sustainage_logo" alt="Sustainage Logo" width="72" height="72" style="display:block;width:72px;height:72px;margin:12px auto 8px;" />
            </div>
            <h1>Sustainage SDG Platform</h1>
            <p>Yeni Kullanıcı Bilgileri</p>
        </div>

        <div class="content">
            <div class="card">
                <div class="card-title">Hoş Geldiniz, {user_name}</div>
                <p>Hesabınız oluşturuldu. Aşağıda giriş bilgileriniz yer almaktadır:</p>
                <div class="credentials">
                    <div><strong>Kullanıcı Adı:</strong> {username}</div>
                    <div><strong>Geçici Şifre:</strong> {temp_password}</div>
                </div>
                <div class="warning">
                    <strong>Önemli:</strong> İlk girişinizde şifrenizi değiştirmeniz zorunludur.
                    Güvenliğiniz için bu bilgileri kimseyle paylaşmayın.
                </div>
                <p style="text-align: center;">
                    <a href="{login_url}" class="button">Sisteme Giriş Yap</a>
                </p>
                <p style="color:#666;font-size:13px;">Destek: {support_email}</p>
            </div>
        </div>

        <div class="footer">
            <p>Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'task_updated': {
        'subject': ' Görev Güncellendi: {task_title}',
        'template': '''
Merhaba {user_name},

Görevinizde bir güncelleme yapıldı.

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
Merhaba {user_name},

"{task_title}" görevi tamamlandı!

 GÖREV ÖZETİ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Başlık: {task_title}
Tamamlayan: {completed_by}
Tamamlanma Tarihi: {completed_date}
Süre: {duration}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Tebrikler! Görev başarıyla tamamlandı.

{note}

---
Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.
        '''
    },

    'task_overdue': {
        'subject': '️ Görev Süresi Doldu: {task_title}',
        'template': '''
Merhaba {user_name},

UYARI: "{task_title}" görevinin süresi doldu!

 GÖREV DETAYLARI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Başlık: {task_title}
Bitiş Tarihi: {due_date}
Gecikme: {overdue_days} gün
Durum: {status}
İlerleme: %{progress}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

️ Bu görev acil olarak tamamlanmalıdır!

Lütfen en kısa sürede:
1. Sisteme giriş yapın
2. Görevi tamamlayın
3. Eğer sorun varsa yöneticinize bildirin

---
Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.
        '''
    },

    'task_rejected': {
        'subject': ' Görev Reddedildi: {task_title}',
        'template': '''
Merhaba {user_name},

"{task_title}" görevi reddedildi.

 GÖREV DETAYLARI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Başlık: {task_title}
Reddeden: {rejected_by}
Red Nedeni: {rejection_reason}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Lütfen red nedenini inceleyip gerekli aksiyonları alın.
Görevi yeniden atayabilir veya düzenleyebilirsiniz.

---
Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.
        '''
    },

    'daily_reminder': {
        'subject': ' Günlük Görev Özeti',
        'template': f'''
Merhaba {{user_name}},

Bugünkü görev özeti:

 İSTATİSTİKLER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Tamamlanan: {{completed_count}}
 Devam Eden: {{in_progress_count}}
{Icons.TIME} Bekleyen: {{pending_count}}
️ Geciken: {{overdue_count}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{task_list}}

Lütfen görevlerinizi zamanında tamamlamaya özen gösterin.

---
Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.
        '''
    },

    'due_reminder': {
        'subject': f"{Icons.TIME} Yaklaşan Son Tarih: {{task_title}}",
        'template': '''
Merhaba {user_name},

Aşağıdaki görevin son tarihi yaklaşıyor:

- Görev: {task_title}
- Öncelik: {priority}
- Son Tarih: {due_date}

Görev detayları: {task_url}

Zamanında tamamlamanız için hatırlatıyoruz.

---
Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.
        '''
    },

    'weekly_digest': {
        'subject': ' Haftalık Görev Özeti - {user_name}',
        'template': '''
Merhaba {user_name},

Haftalık görev özetiniz:

 Tamamlanan: {completed_count}
 Devam Eden: {in_progress_count}
 Bekleyen: {pending_count}
 Geciken: {overdue_count}

 Öne çıkan görevler:
{task_list}

Başarılar ve iyi çalışmalar.

---
Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.
        '''
    },

    'password_reset': {
        'subject': ' Şifre Sıfırlama Kodu - {code}',
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
        .header { background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }
        .content { padding: 30px; }
        .code-card { background: #f8f9fa; border: 2px dashed #e74c3c; padding: 30px; margin: 20px 0; border-radius: 8px; text-align: center; }
        .code { font-size: 32px; font-weight: bold; color: #e74c3c; letter-spacing: 5px; margin: 10px 0; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .warning strong { color: #856404; }
        .steps { background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .steps h3 { margin: 0 0 15px 0; color: #27ae60; }
        .steps ol { margin: 0; padding-left: 20px; }
        .steps li { margin: 8px 0; color: #555; }
        .footer { background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }
        .button { display: inline-block; background: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600; margin: 10px 0; }
        .button:hover { background: #c0392b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> Şifre Sıfırlama</h1>
            <p>Hesabınız için şifre sıfırlama kodu</p>
        </div>
        
        <div class="content">
            <p>Merhaba <strong>{user_name}</strong>,</p>
            <p>Hesabınız için şifre sıfırlama talebinde bulundunuz. Aşağıdaki kodu kullanarak şifrenizi sıfırlayabilirsiniz:</p>
            
            <div class="code-card">
                <div class="code">{code}</div>
                <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">Bu kod 10 dakika geçerlidir</p>
            </div>
            
            <div class="warning">
                <strong>️ Güvenlik Uyarısı:</strong><br>
                Bu kodu kimseyle paylaşmayın. Eğer bu talebi siz yapmadıysanız, lütfen hemen bizimle iletişime geçin.
            </div>
            
            <div class="steps">
                <h3> Şifre Sıfırlama Adımları</h3>
                <ol>
                    <li>Sisteme giriş yapın</li>
                    <li>"Şifremi Unuttum" bölümüne gidin</li>
                    <li>Yukarıdaki kodu girin</li>
                    <li>Yeni şifrenizi belirleyin</li>
                    <li>Değişiklikleri kaydedin</li>
                </ol>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" class="button">Şifre Sıfırla</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Bu e-posta Sustainage SDG Platform tarafından otomatik olarak gönderilmiştir.</p>
            <p>Sorularınız için: <strong>{support_email}</strong></p>
        </div>
    </div>
</body>
</html>
        '''
    },

    # ===================
    # ANKET SİSTEMİ ŞABLONLARI
    # ===================

    'survey_invitation': {
        'subject': f"{Icons.CLIPBOARD} {{survey_name}} - Görüşleriniz Bizim İçin Önemli",
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
        .header { background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 40px 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 28px; font-weight: 600; }
        .header p { margin: 15px 0 0 0; opacity: 0.95; font-size: 16px; line-height: 1.5; }
        .logo { max-width: 120px; margin-bottom: 20px; }
        .content { padding: 40px 30px; }
        .greeting { font-size: 18px; color: #333; margin-bottom: 20px; }
        .survey-info { background: #f8f9fa; border-left: 4px solid #2E7D32; padding: 20px; margin: 25px 0; border-radius: 8px; }
        .survey-title { font-size: 20px; font-weight: 600; color: #2E7D32; margin: 0 0 15px 0; }
        .survey-detail { margin: 10px 0; color: #555; line-height: 1.6; }
        .survey-detail strong { color: #333; }
        .importance { background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 25px 0; }
        .importance h3 { margin: 0 0 15px 0; color: #2E7D32; font-size: 18px; }
        .importance p { margin: 0; color: #555; line-height: 1.6; }
        .cta-section { text-align: center; margin: 35px 0; }
        .button { display: inline-block; background: #2E7D32; color: white; padding: 16px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 2px 10px rgba(46,125,50,0.3); }
        .button:hover { background: #27ae60; }
        .time-estimate { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 25px 0; text-align: center; }
        .time-estimate strong { color: #856404; font-size: 16px; }
        .deadline { background: #ffebee; border: 1px solid #ffcdd2; padding: 15px; border-radius: 8px; margin: 25px 0; text-align: center; }
        .deadline strong { color: #c62828; font-size: 16px; }
        .footer { background: #f8f9fa; padding: 25px 30px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }
        .footer a { color: #2E7D32; text-decoration: none; }
        .contact { margin-top: 20px; padding-top: 20px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Icons.CLIPBOARD Anket Daveti</h1>
            <p>Sürdürülebilirlik stratejimizi geliştirmek için görüşlerinize ihtiyacımız var</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Sayın <strong>{stakeholder_name}</strong>,
            </div>
            
            <p style="color: #555; line-height: 1.6; margin: 20px 0;">
                {company_name} olarak sürdürülebilirlik yolculuğumuzda paydaşlarımızın görüşleri bizim için çok değerli. 
                Bu nedenle, aşağıdaki ankete katılım göstermenizi rica ediyoruz.
            </p>
            
            <div class="survey-info">
                <div class="survey-title">{survey_name}</div>
                <div class="survey-detail"><strong>Icons.MEMO Konu:</strong> {survey_description}</div>
                <div class="survey-detail"><strong>🏢 Şirket:</strong> {company_name}</div>
                <div class="survey-detail"><strong>Icons.CALENDAR Son Tarih:</strong> {deadline_date}</div>
            </div>
            
            <div class="importance">
                <h3>🎯 Neden Önemli?</h3>
                <p>
                    Görüşleriniz, hangi sürdürülebilirlik konularının öncelikli olduğunu belirlememize yardımcı olacak. 
                    Materyalite analizimizde paydaş perspektifi kritik bir rol oynamaktadır.
                </p>
            </div>
            
            <div class="time-estimate">
                <strong>⏱️ Tahmini Süre: 10-15 dakika</strong>
            </div>
            
            <div class="cta-section">
                <a href="{survey_url}" class="button">Icons.ROCKET Anketi Doldur</a>
            </div>
            
            <div class="deadline">
                <strong>Icons.TIME Son Yanıt Tarihi: {deadline_date}</strong>
            </div>
            
            <p style="color: #555; line-height: 1.6; margin: 30px 0 0 0;">
                Katılımınız için şimdiden teşekkür ederiz. Sürdürülebilir bir gelecek için birlikte çalışıyoruz.
            </p>
        </div>
        
        <div class="footer">
            <p style="margin: 0 0 10px 0;"><strong>{company_name}</strong></p>
            <p style="margin: 0;">Sürdürülebilirlik Ekibi</p>
            
            <div class="contact">
                <p style="margin: 5px 0; font-size: 12px;">
                    Sorularınız için: <a href="mailto:anket@sustainage.tr">anket@sustainage.tr</a>
                </p>
                <p style="margin: 5px 0; font-size: 12px; color: #999;">
                    Bu email otomatik olarak gönderilmiştir.
                </p>
            </div>
        </div>
    </div>
</body>
</html>
        '''
    },

    'survey_reminder': {
        'subject': 'Icons.TIME Hatırlatma: {survey_name} - Son {days_left} Gün',
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
        .header { background: linear-gradient(135deg, #F57C00, #FF9800); color: white; padding: 35px 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 26px; font-weight: 600; }
        .header p { margin: 15px 0 0 0; opacity: 0.95; font-size: 15px; }
        .content { padding: 35px 30px; }
        .reminder-box { background: #fff3e0; border-left: 4px solid #F57C00; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .urgent { background: #ffebee; border-left: 4px solid #e74c3c; padding: 20px; margin: 25px 0; border-radius: 8px; text-align: center; }
        .urgent strong { color: #c62828; font-size: 18px; }
        .button { display: inline-block; background: #F57C00; color: white; padding: 16px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; }
        .button:hover { background: #E65100; }
        .footer { background: #f8f9fa; padding: 25px 30px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Icons.TIME Anket Hatırlatma</h1>
            <p>Yanıtınızı bekliyoruz</p>
        </div>
        
        <div class="content">
            <p style="color: #555; line-height: 1.6;">
                Sayın <strong>{stakeholder_name}</strong>,
            </p>
            
            <p style="color: #555; line-height: 1.6; margin: 20px 0;">
                <strong>{survey_name}</strong> anketimize henüz yanıt vermediniz. 
                Görüşleriniz bizim için çok önemli!
            </p>
            
            <div class="urgent">
                <strong>Icons.TIME Kalan Süre: {days_left} Gün</strong><br>
                <span style="color: #666; font-size: 14px;">Son Tarih: {deadline_date}</span>
            </div>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{survey_url}" class="button">Icons.ROCKET Şimdi Anketi Doldur</a>
            </div>
            
            <p style="color: #555; line-height: 1.6; font-size: 14px;">
                ⏱️ Tahmini Süre: 10-15 dakika
            </p>
        </div>
        
        <div class="footer">
            <p style="margin: 0;"><strong>{company_name}</strong> - Sürdürülebilirlik Ekibi</p>
            <p style="margin: 10px 0 0 0; font-size: 12px; color: #999;">
                Bu email otomatik olarak gönderilmiştir.
            </p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'survey_thank_you': {
        'subject': '🙏 Teşekkürler - {survey_name}',
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
        .header { background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 40px 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 32px; font-weight: 600; }
        .header p { margin: 15px 0 0 0; opacity: 0.95; font-size: 16px; }
        .content { padding: 40px 30px; text-align: center; }
        .checkmark { font-size: 80px; color: #4CAF50; margin: 20px 0; }
        .message { font-size: 18px; color: #555; line-height: 1.8; margin: 25px 0; }
        .stats { background: #e8f5e9; padding: 25px; border-radius: 8px; margin: 30px 0; }
        .stats-item { margin: 15px 0; font-size: 16px; color: #333; }
        .footer { background: #f8f9fa; padding: 25px 30px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="checkmark">Icons.SUCCESS</div>
            <h1>Teşekkürler!</h1>
            <p>Yanıtınız başarıyla kaydedildi</p>
        </div>
        
        <div class="content">
            <p style="color: #555; line-height: 1.6;">
                Sayın <strong>{stakeholder_name}</strong>,
            </p>
            
            <div class="message">
                <strong>{survey_name}</strong> anketine katılımınız için teşekkür ederiz. 
                Görüşleriniz, sürdürülebilirlik stratejimizi şekillendirmede çok değerli.
            </div>
            
            <div class="stats">
                <div class="stats-item">Icons.REPORT Yanıtlanan Soru Sayısı: <strong>{question_count}</strong></div>
                <div class="stats-item">Icons.CALENDAR Yanıt Tarihi: <strong>{response_date}</strong></div>
                <div class="stats-item">Icons.USERS Toplam Katılımcı: <strong>{total_responses}</strong></div>
            </div>
            
            <p style="color: #555; line-height: 1.6; margin: 30px 0;">
                Anket sonuçları değerlendirildikten sonra, sürdürülebilirlik raporumuzda 
                paydaş görüşlerini nasıl değerlendirdiğimizi paylaşacağız.
            </p>
        </div>
        
        <div class="footer">
            <p style="margin: 0 0 10px 0;"><strong>{company_name}</strong></p>
            <p style="margin: 0;">Sürdürülebilirlik Ekibi</p>
            <p style="margin: 20px 0 0 0; font-size: 12px; color: #999;">
                Sorularınız için: anket@sustainage.tr
            </p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'survey_closed': {
        'subject': 'Icons.REPORT {survey_name} - Sonuçlar Değerlendiriliyor',
        'template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anket Kapandı</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #1976D2, #2196F3); color: white; padding: 40px 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 28px; font-weight: 600; }
        .content { padding: 40px 30px; }
        .summary-box { background: #e3f2fd; border-left: 4px solid #1976D2; padding: 25px; margin: 25px 0; border-radius: 8px; }
        .stat { margin: 15px 0; font-size: 16px; color: #333; }
        .stat strong { color: #1976D2; font-size: 20px; }
        .next-steps { background: #f8f9fa; padding: 25px; border-radius: 8px; margin: 25px 0; }
        .next-steps h3 { margin: 0 0 15px 0; color: #1976D2; }
        .next-steps ul { margin: 0; padding-left: 20px; }
        .next-steps li { margin: 10px 0; color: #555; line-height: 1.6; }
        .footer { background: #f8f9fa; padding: 25px 30px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Icons.REPORT Anket Sonuçlandı</h1>
            <p>{survey_name}</p>
        </div>
        
        <div class="content">
            <p style="color: #555; line-height: 1.6;">
                Değerli Paydaşlarımız,
            </p>
            
            <p style="color: #555; line-height: 1.6; margin: 20px 0;">
                <strong>{survey_name}</strong> anketimiz sona erdi. 
                Katılımınız ve değerli görüşleriniz için teşekkür ederiz!
            </p>
            
            <div class="summary-box">
                <h3 style="margin: 0 0 20px 0; color: #1976D2;">Icons.CHART_UP Özet İstatistikler</h3>
                <div class="stat">Icons.USERS Toplam Katılımcı: <strong>{total_responses}</strong></div>
                <div class="stat">Icons.REPORT Toplam Konu: <strong>{total_topics}</strong></div>
                <div class="stat">Icons.CALENDAR Anket Süresi: <strong>{survey_duration} gün</strong></div>
                <div class="stat">Icons.SUCCESS Katılım Oranı: <strong>{participation_rate}%</strong></div>
            </div>
            
            <div class="next-steps">
                <h3>🎯 Sonraki Adımlar</h3>
                <ul>
                    <li>Anket sonuçları detaylı olarak analiz edilecek</li>
                    <li>Materyalite matrisi güncellenecek</li>
                    <li>Öncelikli konular belirlenecek</li>
                    <li>Sonuçlar sürdürülebilirlik raporunda paylaşılacak</li>
                </ul>
            </div>
            
            <p style="color: #555; line-height: 1.6; margin: 30px 0;">
                Değerlendirme süreci tamamlandığında, paydaş görüşlerinin stratejimizi 
                nasıl şekillendirdiğini sizlerle paylaşacağız.
            </p>
        </div>
        
        <div class="footer">
            <p style="margin: 0 0 10px 0;"><strong>{company_name}</strong></p>
            <p style="margin: 0;">Sürdürülebilirlik Ekibi</p>
            <p style="margin: 20px 0 0 0; font-size: 12px; color: #999;">
                İletişim: anket@sustainage.tr
            </p>
        </div>
    </div>
</body>
</html>
        '''
    }
}

# Test modunda console'a yazdır
TEST_MODE = False  # Gerçek e-mail göndermek için False yapın

