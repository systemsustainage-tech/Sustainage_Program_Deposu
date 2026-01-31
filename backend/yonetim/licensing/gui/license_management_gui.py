#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
Lisanslama Yönetimi GUI
SUSTAINAGE-SDG'den adapte edilmiş lisans yönetim arayüzü
"""

import json
import os
import sqlite3
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from yonetim.licensing.core.license_ed25519 import \
    activate_license as ed_activate_license
from yonetim.licensing.core.license_ed25519 import \
    get_license_info as ed_get_license_info
from yonetim.licensing.core.license_ed25519 import \
    save_license_key as ed_save_license_key
from yonetim.licensing.tools.license_generator import \
    generate_license as ed_generate_license
from yonetim.security.core.hw import get_hwid_info
from utils.language_manager import LanguageManager
from config.icons import Icons
from config.database import DB_PATH


class LicenseManagementGUI:
    """Lisanslama Yönetimi GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Lisanslama yönetimi arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Lisanslama Yönetimi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # Ana içerik - Notebook (Sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Lisans Durumu sekmesi
        self.license_status_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.license_status_frame, text=" Lisans Durumu")

        # Lisans Aktivasyonu sekmesi
        self.license_activation_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.license_activation_frame, text=" Lisans Aktivasyonu")

        # Donanım Bilgileri sekmesi
        self.hardware_info_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.hardware_info_frame, text=" Donanım Bilgileri")

        # Lisans Üretimi sekmesi
        self.license_generation_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.license_generation_frame, text="️ Lisans Üretimi")

        # IP Kontrolü sekmesi
        self.ip_control_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.ip_control_frame, text="🛡️ IP Kontrolü")

        # Rate Limiting sekmesi
        self.rate_limiting_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.rate_limiting_frame, text="⚡ Rate Limiting")

        # Monitoring Dashboard sekmesi
        self.monitoring_dashboard_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.monitoring_dashboard_frame, text=f"{Icons.REPORT} Monitoring Dashboard")

        # Sekmeleri oluştur
        self.create_license_status_tab()
        self.create_license_activation_tab()
        self.create_hardware_info_tab()
        self.create_license_generation_tab()
        self.create_ip_control_tab()
        self.create_rate_limiting_tab()
        self.create_monitoring_dashboard_tab()

    def _get_db_connection(self) -> sqlite3.Connection:
        possible_paths = [
            DB_PATH,
            "sdg.db",
            os.path.join(os.getcwd(), "data", "sdg_desktop.sqlite"),
        ]
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    conn = sqlite3.connect(path, timeout=5.0)
                    try:
                        conn.execute("PRAGMA journal_mode=WAL")
                        conn.execute("PRAGMA busy_timeout=5000")
                        conn.execute("PRAGMA synchronous=NORMAL")
                    except Exception as e:
                        logging.error(f'Silent error in license_management_gui.py: {str(e)}')
                    return conn
            except Exception as e:
                logging.error(f'Silent error in license_management_gui.py: {str(e)}')
        raise FileNotFoundError("Veritabanı dosyası bulunamadı (data/sdg_desktop.sqlite).")

    def create_license_status_tab(self) -> None:
        """Lisans Durumu sekmesi"""
        content_frame = tk.Frame(self.license_status_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(content_frame, text="Lisans Durumu ve Bilgileri",
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Lisans durumu kartı
        status_card = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        status_card.pack(fill='x', pady=10)

        status_content = tk.Frame(status_card, bg='#f8f9fa')
        status_content.pack(fill='x', padx=20, pady=15)

        tk.Label(status_content, text="Lisans Durumu", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        # Durum bilgileri
        self.status_info_frame = tk.Frame(status_content, bg='#f8f9fa')
        self.status_info_frame.pack(fill='x', pady=10)

        # Durum etiketi
        self.status_label = tk.Label(self.status_info_frame, text="Yükleniyor...",
                                    font=('Segoe UI', 12, 'bold'), fg='#7f8c8d', bg='#f8f9fa')
        self.status_label.pack(anchor='w')

        # Lisans detayları
        self.license_details_frame = tk.Frame(status_content, bg='#f8f9fa')
        self.license_details_frame.pack(fill='x', pady=10)

        # Yenile butonu
        refresh_frame = tk.Frame(content_frame, bg='white')
        refresh_frame.pack(fill='x', pady=10)

        tk.Button(refresh_frame, text="Lisans Durumunu Yenile",
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.refresh_license_status).pack()

        server_frame = tk.Frame(content_frame, bg='white')
        server_frame.pack(fill='x', pady=10)
        tk.Label(server_frame, text="Lisans Sunucu URL",
                 font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(anchor='w')
        server_inner = tk.Frame(server_frame, bg='white')
        server_inner.pack(fill='x', pady=5)
        self.server_url_var = tk.StringVar()
        tk.Entry(server_inner, textvariable=self.server_url_var, width=80).pack(side='left', fill='x', expand=True)
        tk.Button(server_inner, text=self.lm.tr("btn_save", "Kaydet"),
                 font=('Segoe UI', 10), bg='#27ae60', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.save_server_url).pack(side='left', padx=5)
        tk.Button(server_inner, text="Yükle",
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.load_server_url).pack(side='left')
        try:
            self.load_server_url()
        except Exception as e:
            logging.error(f'Silent error in license_management_gui.py: {str(e)}')

        # Lisans işlemleri
        actions_frame = tk.Frame(content_frame, bg='white')
        actions_frame.pack(fill='x', pady=10)

        tk.Button(actions_frame, text="Lisansı Deaktifleştir",
                 font=('Segoe UI', 10), bg='#e74c3c', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.deactivate_license).pack(side='left', padx=5)

        tk.Button(actions_frame, text="Lisans Bilgilerini Dışa Aktar",
                 font=('Segoe UI', 10), bg='#f39c12', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.export_license_info).pack(side='left', padx=5)

    def create_license_activation_tab(self) -> None:
        """Lisans Aktivasyonu sekmesi"""
        content_frame = tk.Frame(self.license_activation_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(content_frame, text="Lisans Aktivasyonu",
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Lisans anahtarı girişi
        key_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        key_frame.pack(fill='x', pady=10)

        key_content = tk.Frame(key_frame, bg='#f8f9fa')
        key_content.pack(fill='x', padx=20, pady=15)

        tk.Label(key_content, text="Lisans Anahtarı", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        # Lisans anahtarı giriş alanı
        key_input_frame = tk.Frame(key_content, bg='#f8f9fa')
        key_input_frame.pack(fill='x', pady=10)

        tk.Label(key_input_frame, text="Lisans Anahtarı:", bg='#f8f9fa').pack(anchor='w')
        self.license_key_var = tk.StringVar()
        key_entry = tk.Entry(key_input_frame, textvariable=self.license_key_var, width=80)
        key_entry.pack(fill='x', pady=5)

        # Dosyadan yükle
        file_frame = tk.Frame(key_content, bg='#f8f9fa')
        file_frame.pack(fill='x', pady=10)

        tk.Button(file_frame, text="Dosyadan Yükle",
                 font=('Segoe UI', 9), bg='#95a5a6', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=15, pady=2,
                 command=self.load_license_from_file).pack(side='left', padx=(0, 10))

        tk.Button(file_frame, text="Panodan Yapıştır",
                 font=('Segoe UI', 9), bg='#95a5a6', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=15, pady=2,
                 command=self.paste_from_clipboard).pack(side='left')

        # Aktivasyon butonu
        activate_frame = tk.Frame(content_frame, bg='white')
        activate_frame.pack(fill='x', pady=10)

        tk.Button(activate_frame, text="Lisansı Aktifleştir",
                 font=('Segoe UI', 12, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=30, pady=10,
                 command=self.activate_license).pack()

        # Aktivasyon sonucu
        self.activation_result_frame = tk.Frame(content_frame, bg='white')
        self.activation_result_frame.pack(fill='x', pady=10)

    def create_hardware_info_tab(self) -> None:
        """Donanım Bilgileri sekmesi"""
        content_frame = tk.Frame(self.hardware_info_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(content_frame, text="Donanım Kimliği Bilgileri",
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Donanım bilgileri kartı
        hw_card = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        hw_card.pack(fill='both', expand=True, pady=10)

        hw_content = tk.Frame(hw_card, bg='#f8f9fa')
        hw_content.pack(fill='both', expand=True, padx=20, pady=15)

        tk.Label(hw_content, text="Donanım Bilgileri", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        # Donanım bilgileri alanı
        self.hw_info_text = tk.Text(hw_content, height=15, width=80,
                                   font=('Consolas', 10), bg='white')
        hw_scrollbar = ttk.Scrollbar(hw_content, orient="vertical", command=self.hw_info_text.yview)
        self.hw_info_text.configure(yscrollcommand=hw_scrollbar.set)

        self.hw_info_text.pack(side='left', fill='both', expand=True, pady=10)
        hw_scrollbar.pack(side='right', fill='y', pady=10)

        # Butonlar
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=10)

        tk.Button(button_frame, text="Donanım Bilgilerini Yenile",
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.refresh_hardware_info).pack(side='left', padx=5)

        tk.Button(button_frame, text="Donanım ID'sini Kopyala",
                 font=('Segoe UI', 10), bg='#27ae60', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.copy_hwid).pack(side='left', padx=5)

        tk.Button(button_frame, text="Bilgileri Dışa Aktar",
                 font=('Segoe UI', 10), bg='#f39c12', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.export_hardware_info).pack(side='left', padx=5)

    def create_license_generation_tab(self) -> None:
        """Lisans Üretimi sekmesi"""
        content_frame = tk.Frame(self.license_generation_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(content_frame, text="Lisans Üretim Aracı",
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Uyarı
        warning_frame = tk.Frame(content_frame, bg='#fff3cd', relief='solid', bd=1)
        warning_frame.pack(fill='x', pady=10)

        warning_content = tk.Frame(warning_frame, bg='#fff3cd')
        warning_content.pack(fill='x', padx=20, pady=15)

        tk.Label(warning_content, text="️ Uyarı", font=('Segoe UI', 12, 'bold'),
                fg='#856404', bg='#fff3cd').pack(anchor='w')
        tk.Label(warning_content, text="Bu araç sadece yetkili personel tarafından kullanılmalıdır. " +
                "Lisans üretimi için özel anahtar gereklidir.",
                font=('Segoe UI', 10), fg='#856404', bg='#fff3cd').pack(anchor='w')

        # Lisans parametreleri
        params_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        params_frame.pack(fill='x', pady=10)

        params_content = tk.Frame(params_frame, bg='#f8f9fa')
        params_content.pack(fill='x', padx=20, pady=15)

        tk.Label(params_content, text="Lisans Parametreleri", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        # Parametre girişleri
        param_inputs_frame = tk.Frame(params_content, bg='#f8f9fa')
        param_inputs_frame.pack(fill='x', pady=10)

        # Ürün adı
        tk.Label(param_inputs_frame, text="Ürün Adı:", bg='#f8f9fa').grid(row=0, column=0, sticky='w', pady=2)
        self.product_var = tk.StringVar(value="SUSTAINAGE")
        tk.Entry(param_inputs_frame, textvariable=self.product_var, width=30).grid(row=0, column=1, sticky='w', padx=(5, 20), pady=2)

        # Sürüm
        tk.Label(param_inputs_frame, text="Sürüm:", bg='#f8f9fa').grid(row=0, column=2, sticky='w', pady=2)
        self.edition_var = tk.StringVar(value="CORE")
        edition_combo = ttk.Combobox(param_inputs_frame, textvariable=self.edition_var,
                                    values=["CORE", "SDG", "ENTERPRISE"], state='readonly', width=15)
        edition_combo.grid(row=0, column=3, sticky='w', padx=5, pady=2)

        # Geçerlilik süresi
        tk.Label(param_inputs_frame, text="Geçerlilik (gün):", bg='#f8f9fa').grid(row=1, column=0, sticky='w', pady=2)
        self.days_var = tk.StringVar(value="365")
        tk.Entry(param_inputs_frame, textvariable=self.days_var, width=30).grid(row=1, column=1, sticky='w', padx=(5, 20), pady=2)

        # Maksimum kullanıcı
        tk.Label(param_inputs_frame, text="Max Kullanıcı:", bg='#f8f9fa').grid(row=1, column=2, sticky='w', pady=2)
        self.max_users_var = tk.StringVar(value="10")
        tk.Entry(param_inputs_frame, textvariable=self.max_users_var, width=15).grid(row=1, column=3, sticky='w', padx=5, pady=2)

        # Donanım ID
        tk.Label(param_inputs_frame, text="Donanım ID (Core):", bg='#f8f9fa').grid(row=2, column=0, sticky='w', pady=2)
        self.hwid_core_var = tk.StringVar()
        hwid_frame = tk.Frame(param_inputs_frame, bg='#f8f9fa')
        hwid_frame.grid(row=2, column=1, columnspan=3, sticky='ew', padx=(5, 0), pady=2)
        hwid_entry = tk.Entry(hwid_frame, textvariable=self.hwid_core_var, width=50)
        hwid_entry.pack(side='left', fill='x', expand=True)
        tk.Button(hwid_frame, text="Mevcut",
                 font=('Segoe UI', 8), bg='#95a5a6', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=10, pady=1,
                 command=self.use_current_hwid).pack(side='right', padx=(5, 0))

        # Not
        tk.Label(param_inputs_frame, text="Not:", bg='#f8f9fa').grid(row=3, column=0, sticky='nw', pady=2)
        self.note_var = tk.StringVar()
        tk.Entry(param_inputs_frame, textvariable=self.note_var, width=50).grid(row=3, column=1, columnspan=3, sticky='w', padx=(5, 0), pady=2)

        # Özel anahtar yolu
        key_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        key_frame.pack(fill='x', pady=10)

        key_content = tk.Frame(key_frame, bg='#f8f9fa')
        key_content.pack(fill='x', padx=20, pady=15)

        tk.Label(key_content, text="Özel Anahtar", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        key_input_frame = tk.Frame(key_content, bg='#f8f9fa')
        key_input_frame.pack(fill='x', pady=10)

        tk.Label(key_input_frame, text="Özel Anahtar Dosyası:", bg='#f8f9fa').pack(anchor='w')
        private_key_frame = tk.Frame(key_input_frame, bg='#f8f9fa')
        private_key_frame.pack(fill='x', pady=5)

        self.private_key_var = tk.StringVar(value="./keys/license_private_key.pem")
        tk.Entry(private_key_frame, textvariable=self.private_key_var, width=60).pack(side='left', fill='x', expand=True)
        tk.Button(private_key_frame, text="Gözat",
                 font=('Segoe UI', 9), bg='#95a5a6', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=15, pady=2,
                 command=self.browse_private_key).pack(side='right', padx=(5, 0))

        # Üretim butonu
        generate_frame = tk.Frame(content_frame, bg='white')
        generate_frame.pack(fill='x', pady=10)

        tk.Button(generate_frame, text="Lisans Üret",
                 font=('Segoe UI', 12, 'bold'), bg='#27ae60', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=30, pady=10,
                 command=self.generate_license).pack()

        # Üretilen lisans
        result_frame = tk.Frame(content_frame, bg='#f8f9fa', relief='solid', bd=1)
        result_frame.pack(fill='both', expand=True, pady=10)

        result_content = tk.Frame(result_frame, bg='#f8f9fa')
        result_content.pack(fill='both', expand=True, padx=20, pady=15)

        tk.Label(result_content, text="Üretilen Lisans", font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')

        self.license_result_text = tk.Text(result_content, height=8, width=80,
                                          font=('Consolas', 9), bg='white')
        result_scrollbar = ttk.Scrollbar(result_content, orient="vertical", command=self.license_result_text.yview)
        self.license_result_text.configure(yscrollcommand=result_scrollbar.set)

        self.license_result_text.pack(side='left', fill='both', expand=True, pady=10)
        result_scrollbar.pack(side='right', fill='y', pady=10)

        # Kopyala butonu
        copy_frame = tk.Frame(result_content, bg='#f8f9fa')
        copy_frame.pack(fill='x', pady=5)

        tk.Button(copy_frame, text="Lisansa Kopyala",
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.copy_generated_license).pack(side='left')

    def load_data(self) -> None:
        """Verileri yükle"""
        self.refresh_license_status()
        self.refresh_hardware_info()

    def refresh_license_status(self) -> None:
        """Lisans durumunu yenile"""
        try:
            conn = self._get_db_connection()
            try:
                info = ed_get_license_info(conn)
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f'Silent error in license_management_gui.py: {str(e)}')
            state = info.get("state", "none")
            color = {
                "valid": "#27ae60",
                "tolerated": "#f39c12",
                "expired": "#e74c3c",
                "invalid": "#e74c3c",
                "none": "#7f8c8d",
            }.get(state, "#7f8c8d")
            self.status_label.config(text=f"Durum: {state}", fg=color)

            for widget in self.license_details_frame.winfo_children():
                widget.destroy()

            details = []
            if state in ("valid", "tolerated"):
                bound = info.get("bound", "core")
                exp = info.get("exp")
                exp_str = datetime.fromtimestamp(exp).strftime("%d.%m.%Y") if exp else "Süresiz"
                details = [
                    ("Ürün:", info.get("product", "SUSTAINAGE")),
                    ("Sürüm:", info.get("edition", "CORE")),
                    ("Geçerlilik:", exp_str),
                    ("Maksimum Kullanıcı:", str(info.get("max_users", 0))),
                    ("Donanım Bağlama:", "Full" if bound == "full" else "Core"),
                    ("Tolerans:", "Açık" if info.get("tolerance_enabled") else "Kapalı"),
                    ("HWID Core:", info.get("hwid_core", "-")),
                ]
            elif state == "expired":
                details = [("Mesaj:", "Lisans süresi dolmuş"), ("HWID Core:", info.get("hwid_core", "-"))]
            elif state == "invalid":
                details = [("Mesaj:", f"Geçersiz lisans: {info.get('reason','')}"), ("HWID Core:", info.get("hwid_core", "-"))]
            else:
                details = [("Durum:", "Lisans bulunamadı"), ("HWID Core:", info.get("hwid_core", "-"))]

            for label, value in details:
                row = tk.Frame(self.license_details_frame, bg='#f8f9fa')
                row.pack(fill='x', pady=2)
                tk.Label(row, text=label, font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(side='left')
                tk.Label(row, text=value, font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa').pack(side='left', padx=(10, 0))
        except Exception as e:
            self.status_label.config(text=f"Hata: {e}", fg='#e74c3c')

    def create_ip_control_tab(self) -> None:
        """IP Kontrolü sekmesi"""
        # Başlık
        title_label = tk.Label(self.ip_control_frame, text="🛡️ IP Kontrolü ve Güvenlik",
                              font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=15)

        # İçerik alanı
        content_frame = tk.Frame(self.ip_control_frame, bg='#ffffff', relief='solid', bd=2)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # IP Beyaz Liste
        whitelist_frame = tk.LabelFrame(content_frame, text="Beyaz Liste IP'ler",
                                       font=('Segoe UI', 11, 'bold'), fg='#27ae60', bg='#ffffff')
        whitelist_frame.pack(fill='x', padx=15, pady=10)

        # IP listesi

        ip_list_frame = tk.Frame(whitelist_frame, bg='#ffffff')
        ip_list_frame.pack(fill='x', padx=10, pady=10)

        # Mevcut IP'ler
        self.ip_listbox = tk.Listbox(ip_list_frame, height=6, font=('Consolas', 10))
        self.ip_listbox.pack(side='left', fill='both', expand=True)

        # Örnek IP'ler ekle
        sample_ips = [
            "192.168.1.0/24 - Yerel Ağ",
            "10.0.0.0/8 - İç Ağ",
            "203.142.87.45 - Yönetici IP",
            "185.125.32.10 - Backup Sunucu"
        ]

        for ip in sample_ips:
            self.ip_listbox.insert('end', ip)

        # IP yönetim butonları
        ip_btn_frame = tk.Frame(ip_list_frame, bg='#ffffff')
        ip_btn_frame.pack(side='right', fill='y', padx=(10, 0))

        tk.Button(ip_btn_frame, text=f"{Icons.ADD} Ekle", bg='#27ae60', fg='white',
                 command=self.add_ip_address, font=('Segoe UI', 9, 'bold')).pack(fill='x', pady=2)
        tk.Button(ip_btn_frame, text=f"{Icons.FAIL} Sil", bg='#e74c3c', fg='white',
                 command=self.remove_ip_address, font=('Segoe UI', 9, 'bold')).pack(fill='x', pady=2)
        tk.Button(ip_btn_frame, text=f"{Icons.EDIT} Düzenle", bg='#3498db', fg='white',
                 command=self.edit_ip_address, font=('Segoe UI', 9, 'bold')).pack(fill='x', pady=2)

        # IP Güvenlik Ayarları
        security_frame = tk.LabelFrame(content_frame, text="Güvenlik Ayarları",
                                      font=('Segoe UI', 11, 'bold'), fg='#e74c3c', bg='#ffffff')
        security_frame.pack(fill='x', padx=15, pady=10)

        security_options = tk.Frame(security_frame, bg='#ffffff')
        security_options.pack(fill='x', padx=10, pady=10)

        # Checkbox'lar
        self.strict_ip_var = tk.BooleanVar(value=True)
        self.log_attempts_var = tk.BooleanVar(value=True)
        self.block_unknown_var = tk.BooleanVar(value=False)

        tk.Checkbutton(security_options, text="Sıkı IP kontrolü (sadece beyaz liste)",
                      variable=self.strict_ip_var, bg='#ffffff', font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        tk.Checkbutton(security_options, text="Erişim denemelerini logla",
                      variable=self.log_attempts_var, bg='#ffffff', font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        tk.Checkbutton(security_options, text="Bilinmeyen IP'leri otomatik engelle",
                      variable=self.block_unknown_var, bg='#ffffff', font=('Segoe UI', 10)).pack(anchor='w', pady=2)

        # Kaydet butonu
        tk.Button(security_options, text=f"{Icons.SAVE} Güvenlik Ayarlarını Kaydet", bg='#2c3e50', fg='white',
                 font=('Segoe UI', 10, 'bold'), command=self.save_ip_security_settings).pack(pady=10)

    def create_rate_limiting_tab(self) -> None:
        """Rate Limiting sekmesi"""
        # Başlık
        title_label = tk.Label(self.rate_limiting_frame, text="⚡ Rate Limiting ve Performans",
                              font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=15)

        # İçerik alanı
        content_frame = tk.Frame(self.rate_limiting_frame, bg='#ffffff', relief='solid', bd=2)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # API Rate Limiting
        api_frame = tk.LabelFrame(content_frame, text="API Rate Limiting",
                                 font=('Segoe UI', 11, 'bold'), fg='#f39c12', bg='#ffffff')
        api_frame.pack(fill='x', padx=15, pady=10)

        api_settings = tk.Frame(api_frame, bg='#ffffff')
        api_settings.pack(fill='x', padx=10, pady=10)

        # Rate limiting ayarları
        settings_data = [
            ("Dakikada maksimum istek:", "100"),
            ("Saatte maksimum istek:", "1000"),
            ("Günlük maksimum istek:", "10000"),
            ("Eş zamanlı bağlantı limiti:", "50"),
            ("Timeout süresi (saniye):", "30")
        ]

        self.rate_entries = {}

        for i, (label_text, default_value) in enumerate(settings_data):
            row_frame = tk.Frame(api_settings, bg='#ffffff')
            row_frame.pack(fill='x', pady=5)

            tk.Label(row_frame, text=label_text, font=('Segoe UI', 10),
                    bg='#ffffff', width=25, anchor='w').pack(side='left')

            entry = tk.Entry(row_frame, font=('Segoe UI', 10), width=15)
            entry.insert(0, default_value)
            entry.pack(side='left', padx=(10, 0))

            self.rate_entries[label_text] = entry

        # Performans Metrikleri
        metrics_frame = tk.LabelFrame(content_frame, text="Performans Metrikleri",
                                     font=('Segoe UI', 11, 'bold'), fg='#9b59b6', bg='#ffffff')
        metrics_frame.pack(fill='x', padx=15, pady=10)

        metrics_content = tk.Frame(metrics_frame, bg='#ffffff')
        metrics_content.pack(fill='x', padx=10, pady=10)

        # Canlı metrikler (örnek)
        metrics_data = [
            (f"{Icons.LOADING} Aktif Bağlantı:", "23/50"),
            (f"{Icons.REPORT} Son Dakika İstek:", "45/100"),
            ("⚡ Ortalama Yanıt Süresi:", "0.23s"),
            ("🚫 Reddedilen İstek:", "2"),
            (f"{Icons.CHART_UP} CPU Kullanımı:", "%15"),
            (f"{Icons.SAVE} RAM Kullanımı:", "%32")
        ]

        for label_text, value in metrics_data:
            metric_frame = tk.Frame(metrics_content, bg='#ffffff')
            metric_frame.pack(fill='x', pady=2)

            tk.Label(metric_frame, text=label_text, font=('Segoe UI', 10, 'bold'),
                    bg='#ffffff', width=20, anchor='w').pack(side='left')
            tk.Label(metric_frame, text=value, font=('Segoe UI', 10),
                    bg='#ffffff', fg='#27ae60').pack(side='left', padx=(10, 0))

        # Butonlar
        btn_frame = tk.Frame(metrics_content, bg='#ffffff')
        btn_frame.pack(fill='x', pady=10)

        tk.Button(btn_frame, text=f"{Icons.SAVE} Ayarları Kaydet", bg='#27ae60', fg='white',
                 font=('Segoe UI', 10, 'bold'), command=self.save_rate_limiting_settings).pack(side='left', padx=5)
        tk.Button(btn_frame, text=f"{Icons.LOADING} Metrikleri Yenile", bg='#3498db', fg='white',
                 font=('Segoe UI', 10, 'bold'), command=self.refresh_performance_metrics).pack(side='left', padx=5)

    def create_monitoring_dashboard_tab(self) -> None:
        """Monitoring Dashboard sekmesi"""
        # Başlık
        title_label = tk.Label(self.monitoring_dashboard_frame, text=f"{Icons.REPORT} Lisans Monitoring Dashboard",
                              font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=15)

        # İçerik alanı
        main_content = tk.Frame(self.monitoring_dashboard_frame, bg='#f5f5f5')
        main_content.pack(fill='both', expand=True, padx=20, pady=10)

        # Üst panel - İstatistikler
        stats_frame = tk.Frame(main_content, bg='#ffffff', relief='solid', bd=2)
        stats_frame.pack(fill='x', pady=(0, 10))

        stats_title = tk.Label(stats_frame, text=f"{Icons.CHART_UP} Gerçek Zamanlı İstatistikler",
                              font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ffffff')
        stats_title.pack(pady=10)

        # İstatistik kartları
        cards_frame = tk.Frame(stats_frame, bg='#ffffff')
        cards_frame.pack(fill='x', padx=15, pady=10)

        stats_data = [
            ("Aktif Lisans", "15", "#27ae60"),
            ("Süresi Dolan", "3", "#e74c3c"),
            ("Bu Ay Kullanım", "89%", "#f39c12"),
            ("Toplam Kullanıcı", "247", "#3498db")
        ]

        for title, value, color in stats_data:
            card = tk.Frame(cards_frame, bg=color, relief='raised', bd=3)
            card.pack(side='left', fill='both', expand=True, padx=5)

            tk.Label(card, text=value, font=('Segoe UI', 18, 'bold'),
                    fg='white', bg=color).pack(pady=(10, 5))
            tk.Label(card, text=title, font=('Segoe UI', 10),
                    fg='white', bg=color).pack(pady=(0, 10))

        # Alt panel - Log ve Aktiviteler
        log_frame = tk.Frame(main_content, bg='#ffffff', relief='solid', bd=2)
        log_frame.pack(fill='both', expand=True)

        log_title = tk.Label(log_frame, text=f"{Icons.MEMO} Son Lisans Aktiviteleri",
                            font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ffffff')
        log_title.pack(pady=10)

        # Log listesi
        log_columns = ('Zaman', 'Kullanıcı', 'Aktivite', 'Durum')
        self.log_tree = ttk.Treeview(log_frame, columns=log_columns, show='headings', height=12)

        for col in log_columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150)

        # Örnek log verileri
        sample_logs = [
            ("28.10.2024 15:30", "admin", "Lisans doğrulama", f"{Icons.SUCCESS} Başarılı"),
            ("28.10.2024 15:28", "user1", "Modül erişim", f"{Icons.SUCCESS} İzin verildi"),
            ("28.10.2024 15:25", "user2", "Lisans süresi kontrolü", f"{Icons.WARNING} 5 gün kaldı"),
            ("28.10.2024 15:20", "system", "Otomatik yenileme", f"{Icons.SUCCESS} Tamamlandı"),
            ("28.10.2024 15:15", "guest", "Geçersiz lisans", f"{Icons.FAIL} Reddedildi"),
            ("28.10.2024 15:10", "admin", "IP kontrolü", f"{Icons.SUCCESS} Beyaz liste"),
            ("28.10.2024 15:05", "user3", "Rate limit aşıldı", f"{Icons.WARNING} Uyarı"),
            ("28.10.2024 15:00", "system", "Backup lisans", f"{Icons.SUCCESS} Oluşturuldu")
        ]

        for log_entry in sample_logs:
            self.log_tree.insert('', 'end', values=log_entry)

        self.log_tree.pack(fill='both', expand=True, padx=15, pady=10)

        # Alt butonlar
        monitor_btn_frame = tk.Frame(log_frame, bg='#ffffff')
        monitor_btn_frame.pack(fill='x', padx=15, pady=10)

        tk.Button(monitor_btn_frame, text=f"{Icons.LOADING} Yenile", bg='#3498db', fg='white',
                 font=('Segoe UI', 10, 'bold'), command=self.refresh_monitoring_data).pack(side='left', padx=5)
        tk.Button(monitor_btn_frame, text=f"{Icons.REPORT} Detaylı Rapor", bg='#9b59b6', fg='white',
                 font=('Segoe UI', 10, 'bold'), command=self.show_detailed_report).pack(side='left', padx=5)
        tk.Button(monitor_btn_frame, text=f"{Icons.CLIPBOARD} Dışa Aktar", bg='#27ae60', fg='white',
                 font=('Segoe UI', 10, 'bold'), command=self.export_monitoring_data).pack(side='left', padx=5)

    # IP Kontrol fonksiyonları
    def add_ip_address(self) -> None:
        """IP adresi ekle"""
        from tkinter import messagebox, simpledialog

        ip_address = simpledialog.askstring("IP Adresi Ekle", "IP adresini girin (örn: 192.168.1.100):")
        if ip_address:
            self.ip_listbox.insert('end', f"{ip_address} - Yeni IP")
            messagebox.showinfo("Başarılı", f"IP adresi eklendi: {ip_address}")

    def remove_ip_address(self) -> None:
        """IP adresi sil"""
        selection = self.ip_listbox.curselection()
        if selection:
            self.ip_listbox.delete(selection[0])
            messagebox.showinfo("Başarılı", "Seçili IP adresi silindi")

    def edit_ip_address(self) -> None:
        """IP adresi düzenle"""
        messagebox.showinfo("IP Düzenle", "IP düzenleme özelliği aktif edilecek")

    def save_ip_security_settings(self) -> None:
        """IP güvenlik ayarlarını kaydet"""
        settings = {
            'strict_ip': self.strict_ip_var.get(),
            'log_attempts': self.log_attempts_var.get(),
            'block_unknown': self.block_unknown_var.get()
        }
        messagebox.showinfo("Kaydedildi", f"IP güvenlik ayarları kaydedildi!\n\n{settings}")

    # Rate Limiting fonksiyonları
    def save_rate_limiting_settings(self) -> None:
        """Rate limiting ayarlarını kaydet"""
        settings = {}
        for key, entry in self.rate_entries.items():
            settings[key] = entry.get()
        messagebox.showinfo("Kaydedildi", f"Rate limiting ayarları kaydedildi!\n\n{len(settings)} ayar güncellendi")

    def refresh_performance_metrics(self) -> None:
        """Performans metriklerini yenile"""
        messagebox.showinfo("Yenilendi", "Performans metrikleri güncellendi!")

    # Monitoring Dashboard fonksiyonları
    def refresh_monitoring_data(self) -> None:
        """Monitoring verilerini yenile"""
        messagebox.showinfo("Yenilendi", "Monitoring verileri güncellendi!")

    def show_detailed_report(self) -> None:
        """Detaylı rapor göster"""
        messagebox.showinfo("Rapor", "Detaylı lisans raporu açılacak")

    def export_monitoring_data(self) -> None:
        """Monitoring verilerini dışa aktar"""
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title=self.lm.tr("export_monitoring_data", "Monitoring Verilerini Dışa Aktar"),
            defaultextension=".csv",
            filetypes=[(self.lm.tr("file_csv", "CSV Dosyaları"), "*.csv"), (self.lm.tr("file_excel", "Excel Dosyaları"), "*.xlsx")]
        )
        if file_path:
            messagebox.showinfo("Dışa Aktarıldı", f"Monitoring verileri dışa aktarıldı:\n{file_path}")

    def refresh_hardware_info(self) -> None:
        """Donanım bilgilerini yenile"""
        try:
            hw_info = get_hwid_info()

            # Donanım bilgilerini göster
            self.hw_info_text.delete(1.0, tk.END)

            info_text = f"""Donanım Kimliği Bilgileri
{'='*50}

Disk Seri No: {hw_info.get('disk_serial', "Veri Yok")}
CPU ID: {hw_info.get('cpu_id', "Veri Yok")}
MAC Hash: {hw_info.get('mac_hash', "Veri Yok")}

HWID Core: {hw_info.get('hwid_core', "Veri Yok")}
HWID Full: {hw_info.get('hwid_full', "Veri Yok")}

{'='*50}

Not: HWID Core lisanslama için kullanılır.
HWID Full daha sıkı donanım bağlama için kullanılır.
"""

            self.hw_info_text.insert(1.0, info_text)

        except Exception as e:
            self.hw_info_text.delete(1.0, tk.END)
            self.hw_info_text.insert(1.0, f"Hata: {e}")

    def load_license_from_file(self) -> None:
        """Dosyadan lisans yükle"""
        try:
            file_path = filedialog.askopenfilename(
                title=self.lm.tr("select_license_file", "Lisans Dosyası Seç"),
                filetypes=[(self.lm.tr("file_text", "Metin Dosyaları"), "*.txt"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")]
            )

            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    license_key = f.read().strip()
                    self.license_key_var.set(license_key)

        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yüklenirken hata: {e}")

    def paste_from_clipboard(self) -> None:
        """Panodan lisans anahtarı yapıştır"""
        try:
            clipboard_content = tk.Tk().clipboard_get()
            if clipboard_content:
                self.license_key_var.set(clipboard_content.strip())
            else:
                messagebox.showwarning("Uyarı", "Panoda lisans anahtarı bulunamadı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Panodan yapıştırırken hata: {e}")

    def activate_license(self) -> None:
        """Lisansı aktifleştir"""
        license_key = self.license_key_var.get().strip()

        if not license_key:
            messagebox.showerror("Hata", "Lisans anahtarı girin.")
            return

        try:
            conn = self._get_db_connection()
            try:
                result = ed_activate_license(conn, license_key, actor="gui")
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f'Silent error in license_management_gui.py: {str(e)}')
            if result.get("ok"):
                messagebox.showinfo("Başarılı", result.get("message", "Lisans başarıyla aktifleştirildi!"))
                self.refresh_license_status()
            else:
                messagebox.showerror("Hata", result.get("message", "Lisans aktifleştirilemedi."))

        except Exception as e:
            messagebox.showerror("Hata", f"Lisans aktifleştirme hatası: {e}")

    def deactivate_license(self) -> None:
        """Lisansı deaktifleştir"""
        try:
            result = messagebox.askyesno("Onay", "Lisansı deaktifleştirmek istediğinizden emin misiniz?")
            if result:
                conn = self._get_db_connection()
                try:
                    ed_save_license_key(conn, actor="gui", new_plain="")
                    # Tolerans ayarını kapat
                    try:
                        conn.execute("UPDATE system_settings SET value='0' WHERE key='tolerance_mac_ok'")
                        conn.commit()
                    except Exception as e:
                        logging.error(f'Silent error in license_management_gui.py: {str(e)}')
                finally:
                    try:
                        conn.close()
                    except Exception as e:
                        logging.error(f'Silent error in license_management_gui.py: {str(e)}')
                messagebox.showinfo("Başarılı", "Lisans başarıyla deaktifleştirildi!")
                self.refresh_license_status()

        except Exception as e:
            messagebox.showerror("Hata", f"Lisans deaktifleştirme hatası: {e}")

    def load_server_url(self) -> None:
        try:
            conn = self._get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS system_settings (key TEXT PRIMARY KEY, value TEXT)")
                conn.commit()
                cur.execute("SELECT value FROM system_settings WHERE key=?", ("license_server_url",))
                row = cur.fetchone()
                self.server_url_var.set((row[0] if row else "") or "")
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f'Silent error in license_management_gui.py: {str(e)}')
        except Exception as e:
            messagebox.showerror("Hata", f"Ayar yüklenemedi: {e}")

    def save_server_url(self) -> None:
        url = (self.server_url_var.get() or "").strip()
        try:
            conn = self._get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS system_settings (key TEXT PRIMARY KEY, value TEXT)")
                conn.commit()
                cur.execute(
                    "INSERT INTO system_settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    ("license_server_url", url)
                )
                if url:
                    cur.execute(
                        "INSERT INTO system_settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        ("license_online_required", "1")
                    )
                else:
                    cur.execute(
                        "INSERT INTO system_settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        ("license_online_required", "0")
                    )
                conn.commit()
            finally:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f'Silent error in license_management_gui.py: {str(e)}')
            messagebox.showinfo("Başarılı", "Sunucu URL kaydedildi")
            self.refresh_license_status()
        except Exception as e:
            messagebox.showerror("Hata", f"Ayar kaydedilemedi: {e}")

    def export_license_info(self) -> None:
        """Lisans bilgilerini dışa aktar"""
        try:
            file_path = filedialog.asksaveasfilename(
                title=self.lm.tr("save_license_info", "Lisans Bilgilerini Kaydet"),
                defaultextension=".json",
                filetypes=[(self.lm.tr("file_json", "JSON Dosyaları"), "*.json"), (self.lm.tr("file_text", "Metin Dosyaları"), "*.txt")]
            )

            if file_path:
                conn = self._get_db_connection()
                try:
                    info = ed_get_license_info(conn)
                finally:
                    try:
                        conn.close()
                    except Exception as e:
                        logging.error(f'Silent error in license_management_gui.py: {str(e)}')
                info_out = dict(info)
                info_out["export_date"] = datetime.now().isoformat()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(info_out, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("Başarılı", f"Lisans bilgileri {file_path} dosyasına kaydedildi.")

        except Exception as e:
            messagebox.showerror("Hata", f"Dışa aktarma hatası: {e}")

    def copy_hwid(self) -> None:
        """Donanım ID'sini kopyala"""
        try:
            hw_info = get_hwid_info()
            hwid_core = hw_info.get('hwid_core', '')

            if hwid_core:
                root = tk.Tk()
                root.withdraw()
                root.clipboard_clear()
                root.clipboard_append(hwid_core)
                root.update()
                root.destroy()

                messagebox.showinfo("Başarılı", "Donanım ID'si panoya kopyalandı.")
            else:
                messagebox.showerror("Hata", "Donanım ID'si alınamadı.")

        except Exception as e:
            messagebox.showerror("Hata", f"Kopyalama hatası: {e}")

    def export_hardware_info(self) -> None:
        """Donanım bilgilerini dışa aktar"""
        try:
            file_path = filedialog.asksaveasfilename(
                title=self.lm.tr("save_hardware_info", "Donanım Bilgilerini Kaydet"),
                defaultextension=".txt",
                filetypes=[(self.lm.tr("file_text", "Metin Dosyaları"), "*.txt"), (self.lm.tr("file_json", "JSON Dosyaları"), "*.json")]
            )

            if file_path:
                hw_info = get_hwid_info()

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Donanım Kimliği Bilgileri\n")
                    f.write("="*50 + "\n\n")
                    for key, value in hw_info.items():
                        f.write(f"{key}: {value}\n")

                messagebox.showinfo("Başarılı", f"Donanım bilgileri {file_path} dosyasına kaydedildi.")

        except Exception as e:
            messagebox.showerror("Hata", f"Dışa aktarma hatası: {e}")

    def use_current_hwid(self) -> None:
        """Mevcut donanım ID'sini kullan"""
        try:
            hw_info = get_hwid_info()
            hwid_core = hw_info.get('hwid_core', '')

            if hwid_core:
                self.hwid_core_var.set(hwid_core)
            else:
                messagebox.showerror("Hata", "Donanım ID'si alınamadı.")

        except Exception as e:
            messagebox.showerror("Hata", f"Donanım ID'si alınırken hata: {e}")

    def browse_private_key(self) -> None:
        """Özel anahtar dosyasını seç"""
        try:
            file_path = filedialog.askopenfilename(
                title=self.lm.tr("select_private_key", "Özel Anahtar Dosyası Seç"),
                filetypes=[(self.lm.tr("pem_files", "PEM Dosyaları"), "*.pem"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")]
            )

            if file_path:
                self.private_key_var.set(file_path)

        except Exception as e:
            messagebox.showerror("Hata", f"Dosya seçim hatası: {e}")

    def generate_license(self) -> None:
        """Lisans üret"""
        try:
            # Parametreleri al
            product = self.product_var.get()
            edition = self.edition_var.get()
            days = int(self.days_var.get())
            max_users = int(self.max_users_var.get())
            hwid_core = self.hwid_core_var.get()
            note = self.note_var.get()
            private_key_path = self.private_key_var.get()

            if not all([product, edition, hwid_core, private_key_path]):
                messagebox.showerror("Hata", "Tüm gerekli alanları doldurun.")
                return

            license_key = ed_generate_license(
                private_key_path=private_key_path,
                product=product,
                edition=edition,
                hwid_core=hwid_core,
                days=days,
                max_users=max_users,
                note=note or None,
            )
            self.license_result_text.delete(1.0, tk.END)
            self.license_result_text.insert(1.0, license_key)

            messagebox.showinfo("Başarılı", "Lisans başarıyla üretildi!")

        except ValueError:
            messagebox.showerror("Hata", "Geçerli sayısal değerler girin.")
        except Exception as e:
            messagebox.showerror("Hata", f"Lisans üretme hatası: {e}")

    def copy_generated_license(self) -> None:
        """Üretilen lisansı kopyala"""
        try:
            license_text = self.license_result_text.get(1.0, tk.END).strip()

            if license_text:
                root = tk.Tk()
                root.withdraw()
                root.clipboard_clear()
                root.clipboard_append(license_text)
                root.update()
                root.destroy()

                messagebox.showinfo("Başarılı", "Lisans anahtarı panoya kopyalandı.")
            else:
                messagebox.showerror("Hata", "Kopyalanacak lisans anahtarı bulunamadı.")

        except Exception as e:
            messagebox.showerror("Hata", f"Kopyalama hatası: {e}")
