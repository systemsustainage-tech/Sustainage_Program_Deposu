#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUSTAINAGE SDG - GİRİŞ EKRANI
- SDG arkaplan resmi
- Modern giriş paneli
- Şifre göster/gizle özelliği
"""

# Dil/çeviri sistemi kaldırıldı: ilgili importlar temizlendi
import math
import logging
import os
import sqlite3
import subprocess  # nosec B404
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from PIL import Image, ImageTk

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

# from security.core.auth import security_auth
# from security.core.crypto import secure_verify_password

class LoginScreen:
    def __init__(self, parent) -> None:
        self.parent = parent
        # Dil yöneticisi başlat
        self.lm = LanguageManager()
        
        # Tema (SUSTAINAGE-SDG stiline uyumlu)
        self.theme = {
            'primary': '#2E8B57',
            'primary_hover': '#3CB371',
            'danger': '#DC143C',
            'bg_light': '#f0f0f0',
            'white': '#ffffff',
            'text_dark': '#333333',
            'text_muted': '#666666'
        }
        # Proje kökünden mutlak veritabanı yolu
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Tek kullanıcı veritabanına geçiş: RBAC ana DB
        self.db_path = os.path.join(self.base_dir, "data", "sdg_desktop.sqlite")
        # self.ensure_database()  # Devre dışı - mevcut veritabanını kullan

        # Admin kontrolü
        if not self.check_admin_exists():
            self.setup_admin_registration()
        else:
            self.setup_ui()
            
        # Dil çevirisi başlangıçta uygulanmıyor; sistem kaldırıldı

        # Süper admin gizli erişim sistemi
        self.setup_super_admin_access()

    def check_admin_exists(self) -> bool:
        """Sistemde admin kullanıcısı var mı kontrol et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Users tablosu var mı kontrol et
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                conn.close()
                return False
                
            # Admin rolüne sahip kullanıcı var mı?
            cursor.execute("SELECT COUNT(*) FROM users WHERE role IN ('admin', 'super_admin') AND is_active = 1")
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception as e:
            logging.error(f"Admin kontrolü hatası: {e}")
            return False

    def setup_admin_registration(self) -> None:
        """İlk kurulum ekranı - Admin kaydı"""
        self.parent.title("Sustainage - İlk Kurulum")
        self.parent.state('zoomed')
        apply_theme(self.parent)
        
        # Grid temizle
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        # Arkaplan
        self.bg_canvas = tk.Canvas(self.parent, bg=self.theme['primary'], highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        self.setup_background_image()

        # Kayıt Kartı
        card_frame = tk.Frame(self.parent, bg=self.theme['white'])
        card_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Gölge efekti (basit)
        shadow = tk.Frame(self.parent, bg='#aaaaaa')
        shadow.place(relx=0.5, rely=0.5, anchor="center", x=4, y=4, width=400, height=550)
        card_frame.lift()

        # İçerik
        inner_frame = tk.Frame(card_frame, bg=self.theme['white'], padx=40, pady=40)
        inner_frame.pack()

        # Başlık
        tk.Label(inner_frame, text="HOŞ GELDİNİZ", font=('Segoe UI', 24, 'bold'), 
                 fg=self.theme['primary'], bg=self.theme['white']).pack(pady=(0, 10))
        
        tk.Label(inner_frame, text="Sistemi kullanmaya başlamak için\nlütfen yönetici hesabı oluşturun.", 
                 font=('Segoe UI', 10), fg=self.theme['text_muted'], bg=self.theme['white']).pack(pady=(0, 30))

        # Form alanları
        self.reg_entries = {}
        
        fields = [
            ("Kullanıcı Adı", "username", False),
            ("E-posta", "email", False),
            ("Şifre", "password", True),
            ("Şifre (Tekrar)", "password_confirm", True)
        ]

        for label_text, key, is_password in fields:
            lbl = tk.Label(inner_frame, text=label_text, font=('Segoe UI', 10, 'bold'), 
                         fg=self.theme['text_dark'], bg=self.theme['white'], anchor="w")
            lbl.pack(fill="x", pady=(10, 5))
            
            entry = ttk.Entry(inner_frame, font=('Segoe UI', 11), show="*" if is_password else "")
            entry.pack(fill="x", ipady=5)
            self.reg_entries[key] = entry

        # Kayıt Butonu
        btn_frame = tk.Frame(inner_frame, bg=self.theme['white'])
        btn_frame.pack(fill="x", pady=(30, 0))

        tk.Button(btn_frame, text="KAYDET VE BAŞLA", font=('Segoe UI', 11, 'bold'),
                 bg=self.theme['primary'], fg='white', relief='flat',
                 command=self.register_admin, cursor="hand2", pady=10).pack(fill="x")

    def register_admin(self) -> None:
        """Admin kaydını gerçekleştir"""
        data = {k: v.get().strip() for k, v in self.reg_entries.items()}
        
        # Validasyon
        if not all(data.values()):
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun.")
            return
            
        if len(data['password']) < 6:
            messagebox.showwarning("Uyarı", "Şifre en az 6 karakter olmalıdır.")
            return
            
        if data['password'] != data['password_confirm']:
            messagebox.showwarning("Uyarı", "Şifreler eşleşmiyor.")
            return

        try:
            # Hash password
            try:
                from yonetim.security.core.crypto import hash_password
                pwd_hash = hash_password(data['password'])
            except ImportError:
                # Fallback
                import hashlib
                pwd_hash = hashlib.sha256(data['password'].encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Kullanıcı oluştur
            now = __import__('datetime').datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active, created_at, first_login)
                VALUES (?, ?, ?, 'admin', 1, ?, 0)
            """, (data['username'], data['email'], pwd_hash, now))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarılı", "Yönetici hesabı başarıyla oluşturuldu.\nLütfen giriş yapın.")
            
            # UI temizle ve giriş ekranına dön
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            self.setup_ui()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu kullanıcı adı veya e-posta zaten kullanılıyor.")
        except Exception as e:
            logging.error(f"Kayıt hatası: {e}")
            messagebox.showerror("Hata", f"Kayıt işlemi başarısız: {e}")

    def send_welcome_email(self, username: str, email: str) -> None:
        """Yeni yöneticiye hoşgeldin emaili gönder"""
        try:
            from services.email_service import EmailService
            
            # Servisi başlat
            service = EmailService(self.db_path)
            
            # Şablon değişkenleri
            vars = {
                'program_name': 'Sustainage SDG',
                'user_name': username,
                'short_description': 'Yönetici hesabınız başarıyla oluşturuldu. Sistemin tüm özelliklerine erişebilirsiniz.',
                'login_url': 'Sustainage Desktop App',
                'support_email': 'support@sustainage.com'
            }
            
            # Gönder
            service.send_template_email(
                to_email=email,
                template_key='new_user_welcome',
                variables=vars
            )
            logging.info(f"Welcome email sent to {email}")
            
        except Exception as e:
            logging.error(f"Email sending failed: {e}")
            # Kullanıcıya hata göstermiyoruz, logluyoruz

    def setup_ui(self) -> None:
        """Giriş ekranı arayüzünü oluştur - Overlay Layout"""
        # Ana pencere ayarları
        self.parent.title("Sustainage - Giriş")
        self.parent.state('zoomed')  # Tam ekran
        apply_theme(self.parent)
        
        # Grid konfigürasyonu temizle (Full screen canvas için)
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=0)
        self.parent.rowconfigure(0, weight=1)

        # 1. Background Layer (Full Screen Canvas)
        self.bg_canvas = tk.Canvas(self.parent, bg=self.theme['primary'], highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)

        # Arkaplan görseli
        self.setup_background_image()
        
        # 2. Login Card (Centered Overlay)
        self.setup_login_card()

    def setup_background_image(self) -> None:
        """Arkaplan görselini yükle ve ayarla (Tam Ekran)"""
        try:
            resimler_dir = os.path.join(self.base_dir, 'resimler')
            candidates = [
                os.path.join(resimler_dir, 'login.png'),
                os.path.join(resimler_dir, 'login.jpg'),
            ]
            image_path = None
            for p in candidates:
                if os.path.exists(p):
                    image_path = p
                    break

            if image_path:
                self._bg_image_original = Image.open(image_path)
                
                def _render_bg(_=None):
                    w = self.bg_canvas.winfo_width()
                    h = self.bg_canvas.winfo_height()
                    if w <= 0 or h <= 0:
                        return
                    
                    # Full Screen Cover Logic
                    img_w, img_h = self._bg_image_original.size
                    ratio = max(w / img_w, h / img_h)
                    new_w = int(img_w * ratio)
                    new_h = int(img_h * ratio)
                    
                    try:
                        resample = Image.Resampling.LANCZOS
                    except AttributeError:
                        resample = Image.LANCZOS
                    
                    img = self._bg_image_original.resize((new_w, new_h), resample)
                    
                    # Center Crop
                    left = (new_w - w) // 2
                    top = (new_h - h) // 2
                    img = img.crop((left, top, left + w, top + h))
                    
                    photo = ImageTk.PhotoImage(img)
                    self.bg_canvas.delete("bg_img")
                    self.bg_canvas.create_image(w // 2, h // 2, image=photo, anchor='center', tags="bg_img")
                    self.bg_canvas.image = photo # Referansı sakla

                self.bg_canvas.bind("<Configure>", _render_bg)
            else:
                # Görsel yoksa düz renk
                self.bg_canvas.create_text(
                    self.parent.winfo_screenwidth() // 2, 
                    self.parent.winfo_screenheight() // 2,
                    text="SUSTAINAGE", 
                    font=('Segoe UI', 36, 'bold'), 
                    fill='white'
                )
        except Exception as e:
            logging.error(f"Görsel yükleme hatası: {e}")

    def setup_login_card(self) -> None:
        """Giriş Formu Kartı (Sağa Yaslanmış)"""
        # Kart Çerçevesi
        self.login_card_frame = tk.Frame(self.parent, bg=self.theme['white'])
        # Kullanıcı isteği: Panel sağ taraftaki boş alana taşındı (relx=0.75)
        self.login_card_frame.place(relx=0.85, rely=0.5, anchor='center')
        
        # İçerik Container
        container = tk.Frame(self.login_card_frame, bg=self.theme['white'], padx=40, pady=40)
        container.pack(fill='both', expand=True)
        
        # Başlık
        tk.Label(container, text=self.lm.tr("header_title", "Hoş Geldiniz"), 
                 font=('Segoe UI', 24, 'bold'), fg=self.theme['text_dark'], bg=self.theme['white']).pack(anchor='center', pady=(0, 5))
        
        tk.Label(container, text=self.lm.tr("header_subtitle", "Hesabınıza giriş yapın"), 
                 font=('Segoe UI', 12), fg=self.theme['text_muted'], bg=self.theme['white']).pack(anchor='center', pady=(0, 20))

        # Hata Mesajı Alanı
        self.error_label = tk.Label(container, text="", font=('Segoe UI', 9, 'bold'), 
                                    fg=self.theme['danger'], bg=self.theme['white'], wraplength=300)
        self.error_label.pack(anchor='center', pady=(0, 10))

        # Dil Seçici
        lang_frame = tk.Frame(container, bg=self.theme['white'])
        lang_frame.pack(fill='x', pady=(0, 15))
        
        current_lang_name = self.lm.available_languages.get(self.lm.current_lang, "Türkçe")
        self.lang_var = tk.StringVar(value=current_lang_name)
        allowed_codes = ['tr', 'en']
        lang_values = [name for code, name in self.lm.available_languages.items() if code in allowed_codes]
        
        tk.Label(lang_frame, text=self.lm.tr("language", "Dil / Language"), 
                 font=('Segoe UI', 9, 'bold'), fg=self.theme['text_muted'], bg=self.theme['white']).pack(anchor='w')
        
        self.lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                      values=lang_values, state='readonly', width=30)
        self.lang_combo.pack(fill='x', pady=(2, 0))
        self.lang_combo.bind('<<ComboboxSelected>>', self.on_language_change)

        # Şirket Seçici
        company_frame = tk.Frame(container, bg=self.theme['white'])
        company_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(company_frame, text=self.lm.tr("company", "Şirket / Company"), 
                 font=('Segoe UI', 9, 'bold'), fg=self.theme['text_muted'], bg=self.theme['white']).pack(anchor='w')
        
        self.company_var = tk.StringVar()
        self.company_combo = ttk.Combobox(company_frame, textvariable=self.company_var, 
                                         state='readonly', width=30)
        self.company_combo.pack(fill='x', pady=(2, 0))
        self.load_companies()

        # Form Alanları
        form_frame = tk.Frame(container, bg=self.theme['white'])
        form_frame.pack(fill='x')

        # Kullanıcı Adı
        tk.Label(form_frame, text=self.lm.tr("username_label", "Kullanıcı Adı"), font=('Segoe UI', 10, 'bold'),
                 fg=self.theme['text_dark'], bg=self.theme['white']).pack(anchor='w', pady=(10, 5))
        
        username_entry_frame = tk.Frame(form_frame, bg='#f8f9fa', highlightbackground='#e9ecef', highlightthickness=1)
        username_entry_frame.pack(fill='x')
        
        self.username_entry = tk.Entry(username_entry_frame, font=('Segoe UI', 11), relief='flat', bg='#f8f9fa', width=30)
        self.username_entry.pack(fill='x', padx=10, pady=8)
        self.username_entry.bind('<Return>', self.handle_login)

        # Parola
        tk.Label(form_frame, text=self.lm.tr("password_label", "Parola"), font=('Segoe UI', 10, 'bold'),
                 fg=self.theme['text_dark'], bg=self.theme['white']).pack(anchor='w', pady=(15, 5))
        
        password_entry_frame = tk.Frame(form_frame, bg='#f8f9fa', highlightbackground='#e9ecef', highlightthickness=1)
        password_entry_frame.pack(fill='x')
        
        self.password_entry = tk.Entry(password_entry_frame, font=('Segoe UI', 11), relief='flat', bg='#f8f9fa', show='*', width=30)
        self.password_entry.pack(fill='x', padx=10, pady=8)
        self.password_entry.bind('<Return>', self.handle_login)

        # Beni Hatırla & Şifremi Unuttum
        options_frame = tk.Frame(form_frame, bg=self.theme['white'])
        options_frame.pack(fill='x', pady=(15, 20))
        
        self.remember_var = tk.BooleanVar()
        tk.Checkbutton(options_frame, text=self.lm.tr("remember_me", "Beni Hatırla"), variable=self.remember_var,
                       bg=self.theme['white'], activebackground=self.theme['white'], font=('Segoe UI', 9)).pack(side='left')
        
        tk.Label(options_frame, text=self.lm.tr("forgot_password", "Şifremi Unuttum?"),
                 font=('Segoe UI', 9), fg=self.theme['primary'], bg=self.theme['white'], cursor='hand2').pack(side='right')

        # Giriş Butonu
        self.login_btn = tk.Button(form_frame, text=self.lm.tr("login_button", "Giriş Yap"),
                                   font=('Segoe UI', 11, 'bold'), fg='white', bg=self.theme['primary'],
                                   activebackground=self.theme['primary_hover'], activeforeground='white',
                                   relief='flat', cursor='hand2', command=self.handle_login)
        self.login_btn.pack(fill='x', ipady=5)

        # Footer
        footer_label = tk.Label(container, text="© 2024 Sustainage. All rights reserved.",
                                font=('Segoe UI', 8), fg=self.theme['text_muted'], bg=self.theme['white'])
        footer_label.pack(side='bottom', pady=(20, 0))


    def load_companies(self) -> None:
        """Aktif şirketleri yükle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Önce company_info tablosunu dene
            companies = []
            try:
                cursor.execute("SELECT id, name FROM company_info WHERE aktif = 1 ORDER BY name")
                companies = cursor.fetchall()
            except sqlite3.OperationalError:
                # Tablo yoksa companies tablosunu dene
                try:
                    cursor.execute("SELECT id, name FROM companies WHERE is_active = 1 ORDER BY name")
                    companies = cursor.fetchall()
                except Exception:
                    pass
            
            conn.close()
            
            company_names = [name for _, name in companies]
            self.company_combo['values'] = company_names
            
            # Varsayılan olarak ilk şirketi seç
            if company_names:
                self.company_combo.current(0)
                
        except Exception as e:
            logging.error(f"Şirket yükleme hatası: {e}")

    def focus_username(self) -> None:
        """Kullanıcı adı alanına focus ayarla"""
        try:
            self.username_entry.focus_force()
            self.username_entry.icursor(0)  # İmleci başa getir
            self.username_entry.selection_range(0, tk.END)  # Tüm metni seç
        except Exception as e:
            logging.error(f"Focus ayarlama hatası: {e}")

    def on_language_change(self, event=None):
        """Dil değiştiğinde çalışır"""
        selected_name = self.lang_var.get()
        # Find code
        lang_code = 'tr'
        for code, name in self.lm.available_languages.items():
            if name == selected_name:
                lang_code = code
                break
        
        if lang_code == self.lm.current_lang:
            return

        # Show loading indicator (change cursor)
        self.parent.config(cursor="watch")
        self.parent.update()
        
        try:
            # Load language (this might generate files if missing)
            # This triggers google translate if file is missing
            self.lm.load_language(lang_code)
            
            # Refresh UI
            self.parent.title(self.lm.tr("app_title", "Sustainage - Giriş"))
            
            # Remove old panel
            if hasattr(self, 'login_card_frame') and self.login_card_frame:
                self.login_card_frame.destroy()
            
            # Recreate panel
            self.setup_login_card()
            
            # Focus
            self.focus_username()
            
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("language_change_error", "Dil değişimi başarısız: {e}").format(e=e))
        finally:
            self.parent.config(cursor="")

    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius=16, fill='#ffffff', outline='#cccccc', width=1) -> None:
        """Basit bir oval köşeli dikdörtgen çizer (polygon smoothing ile)."""
        r = radius
        points = [
            x1+r, y1,
            x2-r, y1,
            x2,   y1,
            x2,   y1+r,
            x2,   y2-r,
            x2,   y2,
            x2-r, y2,
            x1+r, y2,
            x1,   y2,
            x1,   y2-r,
            x1,   y1+r,
            x1,   y1,
            x1+r, y1
        ]
        canvas.create_polygon(points, fill=fill, outline=outline, width=width, smooth=True)

    def _create_linear_gradient_photo(self, width, height, start="#667eea", end="#764ba2") -> None:
        """PIL ile dikey lineer gradient oluşturup PhotoImage döner (appkk/web login ile aynı palet)."""
        try:
            from PIL import Image, ImageTk
            base = Image.new('RGB', (width, height), start)
            top = Image.new('RGB', (width, height), end)
            # Dikey maske
            mask = Image.new('L', (width, height))
            grad_line = [int(255 * (y / max(1, height-1))) for y in range(height)]
            mask.putdata([grad_line[y] for y in range(height) for _ in range(width)])
            blended = Image.composite(top, base, mask)
            return ImageTk.PhotoImage(blended)
        except Exception:
            return None

    def _create_neumorphic_button(self, parent, text, bg_color, command):
        container = tk.Frame(parent, bg=self.theme['white'])
        canvas = tk.Canvas(container, height=44, bg=self.theme['white'], highlightthickness=0)
        canvas.pack(fill='x')
        w = 10
        h = 44
        r = 14
        def draw(normal=True):
            canvas.delete('all')
            fill = bg_color
            outline1 = '#dfe7e3'
            outline2 = '#93c5a6'
            if not normal:
                outline1, outline2 = outline2, outline1
            self._draw_rounded_rect(canvas, w, 2, canvas.winfo_width()-w, h-2, radius=r, fill=fill, outline=outline1, width=1)
            self._draw_rounded_rect(canvas, w+2, 4, canvas.winfo_width()-w-2, h-4, radius=r, fill=fill, outline=outline2, width=1)
            canvas.create_text(canvas.winfo_width()//2, h//2, text=text, font=('Segoe UI', 12, 'bold'), fill='white')
        def on_enter(_):
            draw(False)
        def on_leave(_):
            draw(True)
        def on_click(_):
            try:
                if callable(command):
                    command()
            except Exception as e:
                logging.error(f"[Warning] on_click command failed: {e}")
        def on_resize(_):
            draw(True)
        canvas.bind('<Enter>', on_enter)
        canvas.bind('<Leave>', on_leave)
        canvas.bind('<Button-1>', on_click)
        canvas.bind('<Configure>', on_resize)
        draw(True)
        return container




    def toggle_password_visibility(self) -> None:
        """Şifre görünürlüğünü değiştir"""
        if str(self.password_entry.cget('show')) == '*':
            self.password_entry.config(show='')
            self.toggle_password_btn.config(text="")
        else:
            self.password_entry.config(show='*')
            self.toggle_password_btn.config(text="️")

    def forgot_password(self, event) -> None:
        """Şifremi unuttum - Güvenli OTP bazlı şifre sıfırlama"""
        try:
            # Şifre sıfırlama penceresini aç
            from app.password_reset_gui import show_password_reset_window
            show_password_reset_window(self.parent, db_path=self.db_path)
        except ImportError as ie:
            logging.error(f"[WARN] Password reset GUI import hatası: {ie}")
            # Basit alternatif
            messagebox.showinfo(self.lm.tr("forgot_password_title", "Şifremi Unuttum"),
                               self.lm.tr("password_reset_disabled_msg",
                               "Şifre sıfırlama özelliği aktif değil.\n"
                               "Şifrenizi sıfırlamak için sistem yöneticinizle iletişime geçin.\n\n"
                               "İletişim: admin@sustainage.tr"))
        except Exception as e:
            logging.error(f"[ERROR] Şifre sıfırlama hatası: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("password_reset_error", "Şifre sıfırlama penceresi açılamadı: {e}").format(e=e))

    def handle_login(self, event=None) -> None:
        """Giriş işlemi - Yeni Argon2 güvenlik sistemi ile"""
        # Global sqlite3 erişimi için
        import sqlite3

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        try:
            logging.debug(f"[DEBUG] LOGIN_START db={self.db_path} user={username} lenpwd={len(password)}")
        except Exception as e:
            logging.error(f"[Warning] Debug log failed: {e}")

        if not username or not password:
            self.show_error(self.lm.tr("login_error_empty", "Kullanıcı adı ve şifre gereklidir"))
            self.parent.after(100, self.focus_username)
            return

        try:
            # Basit güvenlik fonksiyonları (geçici)
            def lockout_check(db_path, username):
                """Basit kilit kontrolü"""
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("SELECT failed_attempts, locked_until FROM users WHERE username = ?", (username,))
                    result = cur.fetchone()
                    conn.close()

                    if result:
                        failed_attempts, locked_until = result
                        if locked_until:
                            import datetime
                            try:
                                lock_time = datetime.datetime.fromisoformat(locked_until)
                                if datetime.datetime.now() < lock_time:
                                    wait_seconds = int((lock_time - datetime.datetime.now()).total_seconds())
                                    return False, wait_seconds
                            except Exception as e:
                                logging.error(f"[Error] lockout_check date parsing failed: {e}")
                        if failed_attempts >= 5:  # 5 başarısız deneme sonrası kilit
                            return False, 300  # 5 dakika kilit
                    return True, 0
                except Exception as e:
                    logging.error(f"[Error] lockout_check db failed: {e}")
                    return True, 0

            def twofa_lockout_check(db_path, username):
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("PRAGMA table_info(users)")
                    cols = [c[1] for c in cur.fetchall()]
                    has_cols = ('twofa_failed_attempts' in cols) and ('twofa_locked_until' in cols)
                    if not has_cols:
                        conn.close()
                        return True, 0
                    cur.execute("SELECT twofa_failed_attempts, twofa_locked_until FROM users WHERE username=?", (username,))
                    row = cur.fetchone()
                    conn.close()
                    if not row:
                        return True, 0
                    attempts, locked_until = row
                    if locked_until:
                        try:
                            import datetime as _dt
                            lock_time = _dt.datetime.fromisoformat(str(locked_until))
                            now = _dt.datetime.now()
                            if lock_time > now:
                                return False, int((lock_time - now).total_seconds())
                        except Exception as e:
                            logging.error(f"[Error] twofa_lockout_check date parsing failed: {e}")
                    return True, 0
                except Exception as e:
                    logging.error(f"[Error] twofa_lockout_check db failed: {e}")
                    return True, 0

            def reset_twofa_attempts(db_path, username):
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("PRAGMA table_info(users)")
                    cols = [c[1] for c in cur.fetchall()]
                    if ('twofa_failed_attempts' in cols) and ('twofa_locked_until' in cols):
                        cur.execute("UPDATE users SET twofa_failed_attempts=0, twofa_locked_until=NULL WHERE username=?", (username,))
                        conn.commit()
                    conn.close()
                except Exception as e:
                    logging.error(f"[Error] reset_twofa_attempts failed: {e}")

            def record_failed_2fa(db_path, username):
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("PRAGMA table_info(users)")
                    cols = [c[1] for c in cur.fetchall()]
                    if ('twofa_failed_attempts' in cols) and ('twofa_locked_until' in cols):
                        cur.execute("SELECT twofa_failed_attempts FROM users WHERE username=?", (username,))
                        row = cur.fetchone()
                        current = int(row[0] or 0) if row else 0
                        new_fail = current + 1
                        lock_until = None
                        if new_fail >= 3:
                            try:
                                import datetime as _dt
                                lock_until = (_dt.datetime.now() + _dt.timedelta(minutes=5)).isoformat()
                            except Exception as e:
                                logging.error(f"[Error] Date calculation failed: {e}")
                                lock_until = None
                        cur.execute("UPDATE users SET twofa_failed_attempts=?, twofa_locked_until=? WHERE username=?", (new_fail, lock_until, username))
                        conn.commit()
                    conn.close()
                except Exception as e:
                    logging.error(f"[Error] record_failed_2fa failed: {e}")

            def verify_password(db_path, username, password):
                """Basit şifre doğrulama"""
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("SELECT password_hash, pw_hash_version FROM users WHERE username = ?", (username,))
                    result = cur.fetchone()
                    conn.close()

                    if not result:
                        return False

                    stored_hash, version = result

                    #  GÜVENLİK: Merkezi güvenlik modülü kullanılıyor
                    # Geriye dönük uyumlu: Argon2, PBKDF2, SHA-256
                    try:
                        from yonetim.security.core.crypto import verify_password_compat
                        ok = verify_password_compat(stored_hash or "", password or "")
                        if ok:
                            return True
                    except Exception as e:
                        logging.error(f"[Warning] crypto verify failed, falling back: {e}")
                        try:
                            from security.core.secure_password import verify_password as _sp_verify
                            ok, _ = _sp_verify(stored_hash or "", password or "")
                            return ok
                        except Exception as e2:
                            logging.error(f"[Warning] secure_password verify failed: {e2}")
                        # Fallback: Manuel kontrol
                        if stored_hash.startswith('$argon2'):
                            try:
                                from argon2 import PasswordHasher
                                ph = PasswordHasher()
                                ph.verify(stored_hash, password)
                                return True
                            except Exception as e3:
                                logging.error(f"[Warning] argon2 manual verify failed: {e3}")

                        # SHA-256 fallback (sadece eski veriler için)
                        import hashlib
                        if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
                            return True

                        return False
                    # Eğer compat False dönerse, ek fallback'ları dene
                    try:
                        from security.core.secure_password import verify_password as _sp_verify
                        ok, _ = _sp_verify(stored_hash or "", password or "")
                        if ok:
                            return True
                    except Exception as e:
                        logging.error(f"[Warning] secondary secure_password verify failed: {e}")
                    # PBKDF2 doğrudan doğrulama
                    try:
                        payload = stored_hash or ""
                        if payload.startswith('pbkdf2$'):
                            payload = payload.split('pbkdf2$', 1)[1]
                        if ':' in payload:
                            salt, h = payload.split(':', 1)
                            import hashlib
                            calc = hashlib.pbkdf2_hmac('sha256', (password or '').encode('utf-8'), salt.encode('utf-8'), 100000).hex()
                            if calc == h:
                                return True
                    except Exception as e:
                        logging.error(f"[Warning] pbkdf2 verify failed: {e}")
                    if (stored_hash or '').startswith('$argon2'):
                        try:
                            from argon2 import PasswordHasher
                            ph = PasswordHasher()
                            ph.verify(stored_hash, password)
                            return True
                        except Exception as e:
                            logging.error(f"[Warning] secondary argon2 verify failed: {e}")
                    import hashlib
                    if hashlib.sha256(password.encode()).hexdigest() == (stored_hash or ''):
                        return True
                    return False
                except Exception:
                    return False

            def record_failed_login(db_path, username):
                """Başarısız giriş kaydet"""
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE users 
                        SET failed_attempts = failed_attempts + 1,
                            locked_until = CASE 
                                WHEN failed_attempts >= 4 THEN datetime('now', '+5 minutes')
                                ELSE NULL 
                            END
                        WHERE username = ?
                    """, (username,))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logging.error(f"[Error] Failed to close connection in record_failed_login: {e}")

            def reset_failed_attempts(db_path, username):
                """Başarısız deneme sayısını sıfırla"""
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = ?", (username,))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logging.error(f"[Error] reset_failed_attempts failed: {e}")

            def must_change_password(db_path, username):
                """Şifre değiştirme zorunluluğu kontrolü"""
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("SELECT must_change_password FROM users WHERE username = ?", (username,))
                    result = cur.fetchone()
                    conn.close()
                    return result and result[0] == 1
                except Exception:
                    return False

            def audit_log(db_path, event_type, username=None, user_id=None, success=False, metadata=None):
                """Basit audit log"""
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    try:
                        cur.execute("""
                            INSERT INTO audit_logs (user_id, username, event_type, success, metadata, created_at)
                            VALUES (?, ?, ?, ?, ?, datetime('now'))
                        """, (user_id, username, event_type, success, str(metadata) if metadata else None))
                    except sqlite3.OperationalError as e:
                        if 'no column named event_type' in str(e):
                            # Eski DB şeması, event_type yoksa basit insert dene
                            try:
                                cur.execute("""
                                    INSERT INTO audit_logs (user_id, username, success, metadata, created_at)
                                    VALUES (?, ?, ?, ?, datetime('now'))
                                """, (user_id, username, success, str(metadata) if metadata else None))
                            except Exception as e:
                                logging.error(f"Silent error caught: {str(e)}")
                        else:
                            logging.error(f"[Error] audit_log insert failed: {e}")
                    
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logging.error(f"[Error] audit_log failed: {e}")

            # 1. Brute-force kilit kontrolü
            can_login, wait_seconds = lockout_check(self.db_path, username)
            if not can_login:
                minutes = wait_seconds // 60
                seconds = wait_seconds % 60
                self.show_error(self.lm.tr("login_error_locked", "Hesap kilitli. {minutes} dakika {seconds} saniye sonra tekrar deneyin.").format(minutes=minutes, seconds=seconds))
                audit_log(self.db_path, "LOGIN_FAIL", username=username, success=False,
                         metadata={"reason": "account_locked", "wait_seconds": wait_seconds})
                return

            # 2. Kullanıcı bilgilerini al
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cur.execute("""
                SELECT id, username, password_hash, role, is_active, must_change_password,
                       display_name, email
                FROM users
                WHERE LOWER(username) = LOWER(?)
            """, (username,))

            user_row = cur.fetchone()
            conn.close()

            if not user_row:
                # Kullanıcı bulunamadı (ama bunu söyleme - güvenlik)
                self.show_error(self.lm.tr("login_error_invalid", "Kullanıcı adı veya şifre hatalı."))
                record_failed_login(self.db_path, username)
                audit_log(self.db_path, "LOGIN_FAIL", username=username, success=False,
                         metadata={"reason": "user_not_found"})
                return

            user_id, db_username, password_hash, role, is_active, must_change, display_name, email = user_row
            try:
                logging.debug(f"[DEBUG] USER_ROW id={user_id} role={role} active={is_active} hash_prefix={(password_hash or '')[:15]}")
            except Exception as e:
                logging.error(f"[Warning] Debug log failed: {e}")

            # 3. Hesap aktif mi?
            if not is_active:
                self.show_error(self.lm.tr("login_error_inactive", "Hesabınız pasif. Lütfen yöneticiye başvurun."))
                audit_log(self.db_path, "LOGIN_FAIL", user_id=user_id, username=username,
                         success=False, metadata={"reason": "account_inactive"})
                return

            # 4. Şifre doğrulama
            is_valid = verify_password(self.db_path, username, password)
            needs_rehash = False  # Basit modda rehash yapmıyoruz

            if not is_valid:
                # Hatalı şifre
                self.show_error(self.lm.tr("login_error_invalid", "Kullanıcı adı veya şifre hatalı."))
                record_failed_login(self.db_path, username)
                audit_log(self.db_path, "LOGIN_FAIL", user_id=user_id, username=username,
                         success=False, metadata={"reason": "invalid_password"})
                try:
                    from yonetim.security.core.crypto import verify_password_compat
                    compat_ok = verify_password_compat(password_hash or "", password or "")
                    logging.debug(f"[DEBUG] COMPAT_VERIFY={compat_ok}")
                except Exception as e:
                    logging.error(f"[Warning] Compat verify check failed: {e}")
                return

            # 5. Başarılı giriş - failed_attempts sıfırla
            reset_failed_attempts(self.db_path, username)

            # 6. Rehash gerekirse yap (arka planda)
            if needs_rehash:
                def hash_password(password):
                    """Basit şifre hash'leme"""
                #  GÜVENLİK: Argon2 kullanılıyor
                try:
                    from yonetim.security.core.crypto import hash_password as secure_hash
                    return secure_hash(password)
                except Exception:
                    # Fallback: Argon2 doğrudan
                    try:
                        from argon2 import PasswordHasher
                        ph = PasswordHasher()
                        return ph.hash(password)
                    except Exception:
                        # Son çare: SHA-256 (sadece Argon2 yoksa)
                        import hashlib
                        return hashlib.sha256(password.encode()).hexdigest()

                new_hash = hash_password(password)
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("""
                    UPDATE users 
                    SET password_hash = ?, pw_hash_version = ?
                    WHERE id = ?
                """, (new_hash, 'argon2' if new_hash.startswith('argon2$') else 'pbkdf2', user_id))
                conn.commit()
                conn.close()
                logging.info(f"[INFO] Şifre rehash edildi: {username}")

            # 7. İlk giriş kontrolü - Sadece normal kullanıcılar için
            conn_check = sqlite3.connect(self.db_path)
            cur_check = conn_check.cursor()
            cur_check.execute("SELECT first_login, role FROM users WHERE id = ?", (user_id,))
            first_login_result = cur_check.fetchone()
            conn_check.close()

            first_login = first_login_result[0] if first_login_result else 1
            user_role = first_login_result[1] if first_login_result else "user"

            # Sadece normal kullanıcılar için ilk giriş şifre değiştirme (admin ve super_admin hariç)
            if first_login == 1 and user_role not in ['super_admin', 'admin']:
                audit_log(self.db_path, "LOGIN_SUCCESS_FIRST_LOGIN",
                         user_id=user_id, username=username, success=True,
                         metadata={"first_login": True})

                # İlk giriş şifre değiştirme ekranını aç
                from app.first_login_password_change import show_first_login_password_change

                def on_password_changed() -> None:
                    """Şifre değiştirildikten sonra normal giriş yap"""
                    # Kullanıcı bilgilerini yeniden al
                    self.complete_login(user_id, username, role, display_name, email)

                # İlk giriş şifre değiştirme ekranını göster
                show_first_login_password_change(self.parent, self.db_path, user_id, username)
                return

            # 8. Zorunlu şifre değişimi kontrolü (eski sistem)
            if must_change:
                audit_log(self.db_path, "LOGIN_SUCCESS_REQUIRES_PWD_CHANGE",
                         user_id=user_id, username=username, success=True,
                         metadata={"must_change_password": True})

                # İlk giriş şifre değiştirme ekranını aç
                from app.first_login_password_change import show_first_login_password_change

                def on_password_changed() -> None:
                    """Şifre değiştirildikten sonra normal giriş yap"""
                    # Kullanıcı bilgilerini yeniden al
                    self.complete_login(user_id, username, role, display_name, email)

                # Zorunlu şifre değiştirme ekranını göster
                show_first_login_password_change(self.parent, self.db_path, user_id, username)
                return

            # 8. 2FA kontrolü (opsiyonel - eğer kolonlar varsa)
            try:
                conn2 = sqlite3.connect(self.db_path)
                cur2 = conn2.cursor()

                # totp_enabled kolonu var mı kontrol et
                cur2.execute("PRAGMA table_info(users)")
                cols = [c[1] for c in cur2.fetchall()]

                if 'totp_enabled' in cols and 'totp_secret' in cols:
                    cur2.execute("""
                        SELECT totp_enabled, totp_secret FROM users WHERE id = ?
                    """, (user_id,))
                    totp_row = cur2.fetchone()

                    if totp_row and totp_row[0]:  # totp_enabled
                        totp_secret = totp_row[1]

                        # 2FA kilit durumu kontrol
                        can_2fa, wait_seconds = twofa_lockout_check(self.db_path, username)
                        if not can_2fa:
                            minutes = wait_seconds // 60
                            seconds = wait_seconds % 60
                            self.show_error(self.lm.tr("twofa_locked", "2FA doğrulama kilitli. {minutes} dk {seconds} sn sonra tekrar deneyin.").format(minutes=minutes, seconds=seconds))
                            audit_log(self.db_path, "LOGIN_2FA_LOCKED", user_id=user_id, username=username,
                                     success=False, metadata={"wait_seconds": wait_seconds})
                            conn2.close()
                            return

                        # Audit: 2FA kodu istendi
                        audit_log(self.db_path, "LOGIN_2FA_PROMPT", user_id=user_id, username=username,
                                 success=True, metadata={"method": "TOTP_or_backup"})

                        # 2FA kodu iste
                        code = simpledialog.askstring(
                            self.lm.tr("twofa_prompt_title", "2FA Doğrulama"),
                            self.lm.tr("twofa_prompt_msg", "TOTP kodunuzu veya yedek kodu girin:"),
                            show='*', parent=self.parent
                        )
                        if not code:
                            self.show_error(self.lm.tr("twofa_cancelled", "2FA doğrulama iptal edildi."))
                            audit_log(self.db_path, "LOGIN_2FA_FAIL", user_id=user_id, username=username,
                                     success=False, metadata={"reason": "cancelled"})
                            conn2.close()
                            return

                        # TOTP doğrulama
                        if totp_secret and self._verify_totp_simple(totp_secret, code):
                            logging.info("[OK] TOTP doğrulama başarılı")
                            reset_twofa_attempts(self.db_path, username)
                            audit_log(self.db_path, "LOGIN_2FA_SUCCESS", user_id=user_id, username=username,
                                     success=True, metadata={"method": "TOTP"})
                        elif self._verify_backup_code_simple(username, code):
                            logging.info("[OK] Yedek kod doğrulama başarılı")
                            reset_twofa_attempts(self.db_path, username)
                            audit_log(self.db_path, "LOGIN_2FA_SUCCESS", user_id=user_id, username=username,
                                     success=True, metadata={"method": "BACKUP_CODE"})
                        else:
                            record_failed_2fa(self.db_path, username)
                            self.show_error(self.lm.tr("twofa_failed", "2FA doğrulama başarısız."))
                            audit_log(self.db_path, "LOGIN_2FA_FAIL", user_id=user_id, username=username,
                                     success=False, metadata={"method": "TOTP_or_backup"})
                            conn2.close()
                            return
                else:
                    logging.info("[INFO] 2FA kolonları mevcut değil - atlandı")

                conn2.close()
            except Exception as e:
                logging.info(f"[WARN] 2FA kontrolü atlandı: {e}")

            # 9. Başarılı giriş - audit log
            audit_log(self.db_path, "LOGIN_SUCCESS", user_id=user_id, username=username,
                     success=True, metadata={"role": role})

            # 10. Ana uygulamayı aç
            self.show_error("")
            self.start_main_app({
                'user_id': user_id,
                'username': username,
                'role': role,
                'display_name': display_name,
                'email': email
            })
        except Exception as e:
            error_msg = self.lm.tr("login_error_generic", "Giriş sırasında hata oluştu: {e}").format(e=str(e))
            logging.error(f"[LOGIN ERROR] {error_msg}")
            import traceback
            traceback.print_exc()
            self.show_error(error_msg)

    def show_error(self, message) -> None:
        """Hata mesajını göster"""
        try:
            if hasattr(self, 'error_label') and self.error_label.winfo_exists():
                self.error_label['text'] = message
            else:
                # Login UI temizlenmişse veya label yoksa modal uyarı göster
                messagebox.showerror(self.lm.tr("error", "Hata"), message)
        except Exception:
            # Label yapılandırılamazsa yedek olarak mesaj kutusu kullan
            try:
                messagebox.showerror(self.lm.tr("error", "Hata"), message)
            except Exception:
                # Son çare: konsola yaz
                logging.error(f"Hata: {message}")

    def complete_login(self, user_id, username, role, display_name, email) -> None:
        """Helper to complete login process"""
        self.start_main_app({
            'user_id': user_id,
            'username': username,
            'role': role,
            'display_name': display_name,
            'email': email
        })

    def start_main_app(self, user_info) -> None:
        """Ana uygulamayı başlat"""
        try:
            # Login UI öğelerini temizle
            for child in self.parent.winfo_children():
                try:
                    child.destroy()
                except Exception as e:
                    logging.error(f"[Warning] Failed to destroy child widget: {e}")

            # Kullanıcı bilgilerini tuple formatına dönüştür (eski sistem uyumluluğu için)
            user_tuple = (
                user_info['user_id'],
                user_info['username'],
                user_info['display_name']
            )

            # Güvenlik log kaydet
            self._log_security_event_simple(
                user_info['user_id'],
                user_info['username'],
                "LOGIN_SUCCESS",
                True,
                "Başarılı giriş yapıldı"
            )

            # Firma seçimini giriş ekranından al
            # company_id = self.get_selected_company_id()
            # Yeni tasarımda combo yok, dialog açıyoruz:
            company_id = self.select_company()
            
            current_lang = self.lm.current_lang
            logging.debug(f"[DEBUG] Login successful. Passing current_lang={current_lang} to MainApp")

            import importlib

            import app.main_app
            importlib.reload(app.main_app)
            from app.main_app import MainApp
            
            MainApp(self.parent, user_tuple, company_id=company_id, current_lang=current_lang)

            # İlk kullanım turu (onboarding wizard)
            try:
                from modules.user_experience.onboarding_wizard import show_onboarding
                user_id = user_tuple[0] if user_tuple and len(user_tuple) > 0 else 1
                show_onboarding(self.parent, self.db_path, user_id)
            except Exception as e:
                logging.info(f"Onboarding wizard başlatılamadı: {e}")

            # Pencereyi tekrar görünür yap
            try:
                self.parent.deiconify()
            except Exception as e:
                logging.error(f"[Warning] Failed to deiconify parent: {e}")

        except Exception as e:
            self.show_error(self.lm.tr("main_app_start_error", "Ana uygulama başlatılamadı: {e}").format(e=str(e)))
            self.parent.deiconify()  # Login ekranını tekrar göster

    def ensure_database(self) -> None:
        """Veritabanının varlığını kontrol et"""
        if not os.path.exists(self.db_path):
            logging.info("Veritabanı bulunamadı, oluşturuluyor...")
            try:
                # Veritabanı oluşturma scriptini çalıştır
                init_script = os.path.join(self.base_dir, "tools", "init_extended_db.py")
                if os.path.exists(init_script):
                    subprocess.run([sys.executable, init_script, "--db", self.db_path], check=True)  # nosec B603
                    logging.info("Veritabanı oluşturuldu")
                else:
                    logging.info("Veritabanı oluşturulamadı: init_extended_db.py bulunamadı")
            except Exception as e:
                logging.info(f"Veritabanı oluşturulamadı: {e}")

    def get_companies_list(self) -> None:
        """Login formu için firma listesini getir."""
        companies = []
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT company_id, COALESCE(ticari_unvan, sirket_adi, 'Firma') FROM company_info ORDER BY company_id")
            companies = cur.fetchall() or []
            conn.close()
        except Exception as e:
            logging.info(f"Firma listesi alınamadı: {e}")
        if not companies:
            companies = [(1, "Varsayılan Firma")]
        return companies

    def get_selected_company_id(self) -> int:
        """Combobox'tan seçilen firma ID'sini döndür."""
        try:
            sel = self.company_var.get()
            if sel and " - " in sel:
                return int(sel.split(" - ")[0])
        except Exception as e:
            logging.error(f"[Warning] Failed to parse company selection: {e}")
        return 1

    def select_company(self) -> None:
        """Kullanıcı girişinden sonra firma seçimi diyalogu"""
        # company_info tablosundan şirketleri al
        companies = []
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT company_id, COALESCE(ticari_unvan, sirket_adi, 'Firma') FROM company_info ORDER BY company_id")
            companies = cur.fetchall() or []
            conn.close()
        except Exception as e:
            logging.info(f"Firma listesi alınamadı: {e}")

        # Dialog penceresi
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr("company_selection_title", "Firma Seçimi"))
        dialog.configure(bg='white')
        dialog.grab_set()
        tk.Label(dialog, text=self.lm.tr("company_selection_label", "Lütfen çalışacağınız firmayı seçin:"), font=('Segoe UI', 11, 'bold'), bg='white').pack(padx=16, pady=(16,8))
        values = [f"{cid} - {name}" for cid, name in companies] if companies else [self.lm.tr("default_company_option", "1 - Varsayılan Firma")]
        var = tk.StringVar(value=values[0])
        cb = ttk.Combobox(dialog, state='readonly', values=values, textvariable=var, width=40)
        cb.pack(padx=16, pady=8)
        chosen = {'id': None}

        def _ok() -> None:
            try:
                sel = var.get()
                if sel and " - " in sel:
                    chosen['id'] = int(sel.split(" - ")[0])
            except Exception:
                chosen['id'] = 1
            dialog.destroy()

        tk.Button(dialog, text=self.lm.tr("continue_btn", "Devam"), command=_ok, bg='#2E8B57', fg='white', relief='flat', padx=12, pady=6).pack(pady=(8,16))
        dialog.wait_window()
        return chosen['id'] or 1

    def _verify_totp_simple(self, secret: str, code: str) -> bool:
        """Basit TOTP doğrulama (geçici)"""
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)
        except Exception:
            return False

    def _verify_backup_code_simple(self, username: str, code: str) -> bool:
        """Basit yedek kod doğrulama (geçici)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT backup_codes FROM users WHERE username = ?", (username,))
            result = cur.fetchone()
            conn.close()

            if result and result[0]:
                backup_codes = result[0].split(',')
                return code.strip() in backup_codes
            return False
        except Exception:
            return False

    def _log_security_event_simple(self, user_id: int, username: str, event_type: str, success: bool, details: str):
        """Basit güvenlik log (geçici)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            # action kolonu varsa ona da yaz (geriye dönük uyumluluk)
            try:
                cur.execute("""
                    INSERT INTO security_logs (user_id, username, event_type, action, success, details, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """, (user_id, username, event_type, event_type, success, details))
            except sqlite3.OperationalError:
                # action kolonu yoksa sadece event_type
                cur.execute("""
                    INSERT INTO security_logs (user_id, username, event_type, success, details, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (user_id, username, event_type, success, details))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error logging security event: {e}")

    def setup_super_admin_access(self) -> None:
        """Süper admin gizli erişim sistemini kur (geçici olarak devre dışı)"""
        pass

def main() -> None:
    """Ana fonksiyon"""
    root = tk.Tk()
    try:
        root.withdraw()
    except Exception as e:
        logging.debug(f"Error withdrawing root: {e}")
    win = tk.Toplevel(root)
    try:
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), root.destroy()))
    except Exception as e:
        logging.debug(f"Error setting protocol: {e}")
    LoginScreen(win)
    root.mainloop()

if __name__ == "__main__":
    main()
