#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUSTAINAGE SDG - Email Şablonları
- Kurumsal email şablonları
- Logo entegrasyonu
- Güzel tasarım
"""

# Email şablonları
EMAIL_TEMPLATES = {
    'welcome': {
        'subject': 'SUSTAINAGE SDG - Hoşgeldiniz!',
        'html_template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SUSTAINAGE SDG</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {{
            background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        .logo {{
            width: 60px;
            height: 60px;
            margin: 0 auto 20px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: #2E8B57;
        }
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }
        .header p {{
            margin: 10px 0 0;
            font-size: 16px;
            opacity: 0.9;
        }
        .content {{
            padding: 40px 30px;
        }
        .content h2 {{
            color: #2E8B57;
            font-size: 24px;
            margin: 0 0 20px;
            font-weight: 400;
        }
        .content p {{
            font-size: 16px;
            margin: 0 0 20px;
            line-height: 1.6;
        }
        .info-box {
            background-color: #f8f9fa;
            border-left: 4px solid #2E8B57;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }
        .info-box h3 {
            margin: 0 0 10px;
            color: #2E8B57;
            font-size: 18px;
        }
        .info-box ul {
            margin: 0;
            padding-left: 20px;
        }
        .info-box li {
            margin: 5px 0;
            font-size: 14px;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            margin: 20px 0;
            transition: transform 0.2s;
        }
        .button:hover {
            transform: translateY(-2px);
        }
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }
        .footer p {{
            margin: 0 0 10px;
            font-size: 14px;
            color: #666;
        }
        .footer .company {{
            font-weight: bold;
            color: #2E8B57;
            font-size: 16px;
        }
        .security-note {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            font-size: 14px;
            color: #856404;
        }
        .security-note strong {
            color: #d63031;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo"></div>
            <h1>SUSTAINAGE SDG</h1>
            <p>Sürdürülebilir Kalkınma Hedefleri</p>
        </div>
        
        <div class="content">
            <h2>Hoşgeldiniz!</h2>
            
            <p>Merhaba <strong>{username}</strong>,</p>
            
            <p>SUSTAINAGE SDG sistemine hoşgeldiniz! Hesabınız başarıyla oluşturuldu ve artık sistemi kullanmaya başlayabilirsiniz.</p>
            
            <div class="info-box">
                <h3>Giriş Bilgileriniz</h3>
                <ul>
                    <li><strong>Kullanıcı Adı:</strong> {username}</li>
                    <li><strong>Geçici Şifre:</strong> {temp_password}</li>
                    <li><strong>Email:</strong> {email}</li>
                </ul>
            </div>
            
            <p>İlk girişinizde güvenlik nedeniyle şifrenizi değiştirmeniz gerekecektir.</p>
            
            <div class="security-note">
                <strong>Güvenlik Uyarısı:</strong> Bu bilgileri kimseyle paylaşmayın ve ilk girişinizde şifrenizi değiştirin.
            </div>
            
            <p>Sistem hakkında sorularınız için bizimle iletişime geçebilirsiniz.</p>
            
            <p>İyi çalışmalar,<br>
            <strong>SUSTAINAGE SDG Ekibi</strong></p>
        </div>
        
        <div class="footer">
            <p class="company">SUSTAINAGE SDG</p>
            <p>Sürdürülebilir Kalkınma Hedefleri Yönetim Sistemi</p>
            <p>Bu email otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'password_reset': {
        'subject': 'SUSTAINAGE SDG - Şifre Sıfırlama',
        'html_template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SUSTAINAGE SDG - Şifre Sıfırlama</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {{
            background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        .logo {{
            width: 60px;
            height: 60px;
            margin: 0 auto 20px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: #2E8B57;
        }
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }
        .header p {{
            margin: 10px 0 0;
            font-size: 16px;
            opacity: 0.9;
        }
        .content {{
            padding: 40px 30px;
        }
        .content h2 {{
            color: #2E8B57;
            font-size: 24px;
            margin: 0 0 20px;
            font-weight: 400;
        }
        .content p {{
            font-size: 16px;
            margin: 0 0 20px;
            line-height: 1.6;
        }
        .otp-box {
            background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
            color: white;
            padding: 30px;
            margin: 30px 0;
            border-radius: 10px;
            text-align: center;
        }
        .otp-box h3 {
            margin: 0 0 15px;
            font-size: 20px;
        }
        .otp-code {
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 5px;
            margin: 20px 0;
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 8px;
            display: inline-block;
        }
        .info-box {
            background-color: #f8f9fa;
            border-left: 4px solid #2E8B57;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }
        .info-box h3 {
            margin: 0 0 10px;
            color: #2E8B57;
            font-size: 18px;
        }
        .security-note {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            font-size: 14px;
            color: #856404;
        }
        .security-note strong {
            color: #d63031;
        }
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }
        .footer p {{
            margin: 0 0 10px;
            font-size: 14px;
            color: #666;
        }
        .footer .company {{
            font-weight: bold;
            color: #2E8B57;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo"></div>
            <h1>SUSTAINAGE SDG</h1>
            <p>Şifre Sıfırlama</p>
        </div>
        
        <div class="content">
            <h2>Şifre Sıfırlama Talebi</h2>
            
            <p>Merhaba <strong>{username}</strong>,</p>
            
            <p>Hesabınız için şifre sıfırlama talebi alınmıştır. Aşağıdaki OTP kodunu kullanarak şifrenizi sıfırlayabilirsiniz.</p>
            
            <div class="otp-box">
                <h3>OTP Kodunuz</h3>
                <div class="otp-code">{otp_code}</div>
                <p>Bu kod 15 dakika geçerlidir</p>
            </div>
            
            <div class="info-box">
                <h3>Nasıl Kullanılır?</h3>
                <ul>
                    <li>OTP kodunu kopyalayın</li>
                    <li>Şifre sıfırlama sayfasına gidin</li>
                    <li>Kodu girin ve yeni şifrenizi belirleyin</li>
                </ul>
            </div>
            
            <div class="security-note">
                <strong>Güvenlik Uyarısı:</strong> Bu kodu kimseyle paylaşmayın. Eğer bu talebi siz yapmadıysanız, lütfen hemen bizimle iletişime geçin.
            </div>
            
            <p>İyi çalışmalar,<br>
            <strong>SUSTAINAGE SDG Ekibi</strong></p>
        </div>
        
        <div class="footer">
            <p class="company">SUSTAINAGE SDG</p>
            <p>Sürdürülebilir Kalkınma Hedefleri Yönetim Sistemi</p>
            <p>Bu email otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        '''
    },

    'notification': {
        'subject': 'SUSTAINAGE SDG - Bildirim',
        'html_template': '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SUSTAINAGE SDG - Bildirim</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {{
            background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        .logo {{
            width: 60px;
            height: 60px;
            margin: 0 auto 20px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: #2E8B57;
        }
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }
        .header p {{
            margin: 10px 0 0;
            font-size: 16px;
            opacity: 0.9;
        }
        .content {{
            padding: 40px 30px;
        }
        .content h2 {{
            color: #2E8B57;
            font-size: 24px;
            margin: 0 0 20px;
            font-weight: 400;
        }
        .content p {{
            font-size: 16px;
            margin: 0 0 20px;
            line-height: 1.6;
        }
        .notification-box {
            background-color: #f8f9fa;
            border-left: 4px solid #2E8B57;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }
        .footer p {{
            margin: 0 0 10px;
            font-size: 14px;
            color: #666;
        }
        .footer .company {{
            font-weight: bold;
            color: #2E8B57;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo"></div>
            <h1>SUSTAINAGE SDG</h1>
            <p>Sistem Bildirimi</p>
        </div>
        
        <div class="content">
            <h2>Sistem Bildirimi</h2>
            
            <p>Merhaba <strong>{username}</strong>,</p>
            
            <div class="notification-box">
                <h3>{notification_title}</h3>
                <p>{notification_message}</p>
            </div>
            
            <p>Bu bildirim hakkında sorularınız için bizimle iletişime geçebilirsiniz.</p>
            
            <p>İyi çalışmalar,<br>
            <strong>SUSTAINAGE SDG Ekibi</strong></p>
        </div>
        
        <div class="footer">
            <p class="company">SUSTAINAGE SDG</p>
            <p>Sürdürülebilir Kalkınma Hedefleri Yönetim Sistemi</p>
            <p>Bu email otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
        '''
    }
}

# Varsayılan şablon
DEFAULT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SUSTAINAGE SDG</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {{
            background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        .logo {{
            width: 60px;
            height: 60px;
            margin: 0 auto 20px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: #2E8B57;
        }
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }
        .header p {{
            margin: 10px 0 0;
            font-size: 16px;
            opacity: 0.9;
        }
        .content {{
            padding: 40px 30px;
        }
        .content h2 {{
            color: #2E8B57;
            font-size: 24px;
            margin: 0 0 20px;
            font-weight: 400;
        }
        .content p {{
            font-size: 16px;
            margin: 0 0 20px;
            line-height: 1.6;
        }
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }
        .footer p {{
            margin: 0 0 10px;
            font-size: 14px;
            color: #666;
        }
        .footer .company {{
            font-weight: bold;
            color: #2E8B57;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo"></div>
            <h1>SUSTAINAGE SDG</h1>
            <p>Sürdürülebilir Kalkınma Hedefleri</p>
        </div>
        
        <div class="content">
            <h2>{subject}</h2>
            
            <p>{message}</p>
            
            <p>İyi çalışmalar,<br>
            <strong>SUSTAINAGE SDG Ekibi</strong></p>
        </div>
        
        <div class="footer">
            <p class="company">SUSTAINAGE SDG</p>
            <p>Sürdürülebilir Kalkınma Hedefleri Yönetim Sistemi</p>
            <p>Bu email otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
'''
