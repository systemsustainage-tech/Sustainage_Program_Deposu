#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lisans Anahtarı Oluşturma GUI
Super Admin paneli için lisans yönetimi
"""

import logging
import json
import os
import shutil
import subprocess  # nosec B404
import sys
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, ttk
from utils.language_manager import LanguageManager

# Lisans generator modülünü import et
try:
    license_tools_path = os.path.join(os.path.dirname(__file__), '..', 'yonetim', 'licensing', 'tools')
    sys.path.append(license_tools_path)
    from license_generator import create_key_pair, generate_license
except ImportError as e:
    logging.info(f"Lisans generator modülü bulunamadı: {e}")
    logging.info(f"Aranan yol: {license_tools_path}")

    # Alternatif yol dene
    try:
        alt_path = os.path.join(os.path.dirname(__file__), '..')
        sys.path.append(alt_path)
        from yonetim.licensing.tools.license_generator import create_key_pair, generate_license
        logging.info("Alternatif yoldan import edildi")
    except ImportError as e2:
        logging.info(f"Alternatif yol da başarısız: {e2}")

class LicenseManagerGUI:
    """Lisans Anahtarı Oluşturma Arayüzü"""

    def __init__(self, parent, base_dir: str, db_path: str) -> None:
        self.lm = LanguageManager()
        self.parent = parent
        self.base_dir = base_dir
        self.db_path = db_path
        self.keys_dir = os.path.join(base_dir, "yonetim", "licensing", "tools", "keys")

        # Tema renkleri
        self.theme = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'white': '#ffffff'
        }

        self.setup_ui()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg=self.theme['light'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg=self.theme['primary'], height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Lisans Anahtarı Yönetimi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg=self.theme['primary'])
        title_label.pack(expand=True)

        # İçerik alanı
        content_frame = tk.Frame(main_frame, bg=self.theme['light'])
        content_frame.pack(fill='both', expand=True)

        # Sol panel - Lisans oluşturma
        left_panel = tk.Frame(content_frame, bg=self.theme['white'], relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Sağ panel - Lisans yönetimi
        right_panel = tk.Frame(content_frame, bg=self.theme['white'], relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

        self.create_license_creation_panel(left_panel)
        self.create_license_management_panel(right_panel)

    def create_license_creation_panel(self, parent) -> None:
        """Lisans oluşturma paneli"""
        # Panel başlığı
        header_frame = tk.Frame(parent, bg=self.theme['secondary'], height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="Yeni Lisans Anahtarı Oluştur",
                font=('Segoe UI', 12, 'bold'), fg='white', bg=self.theme['secondary']).pack(expand=True)

        # İçerik
        content = tk.Frame(parent, bg=self.theme['white'])
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # HWID alma bölümü
        hwid_frame = tk.LabelFrame(content, text="Cihaz Bilgileri",
                                  font=('Segoe UI', 10, 'bold'), bg=self.theme['white'])
        hwid_frame.pack(fill='x', pady=(0, 15))

        # Mevcut HWID
        tk.Label(hwid_frame, text="Mevcut HWID CORE:", font=('Segoe UI', 9), bg=self.theme['white']).pack(anchor='w', padx=10, pady=(10, 5))

        hwid_input_frame = tk.Frame(hwid_frame, bg=self.theme['white'])
        hwid_input_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.hwid_var = tk.StringVar()
        self.hwid_entry = tk.Entry(hwid_input_frame, textvariable=self.hwid_var,
                                  font=('Segoe UI', 9), width=50)
        self.hwid_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

        tk.Button(hwid_input_frame, text="Al", font=('Segoe UI', 9), bg=self.theme['secondary'],
                 fg='white', relief='flat', bd=0, cursor='hand2',
                 command=self.get_current_hwid).pack(side='right')

        # Manuel HWID girişi
        tk.Label(hwid_frame, text="Manuel HWID CORE girişi:", font=('Segoe UI', 9), bg=self.theme['white']).pack(anchor='w', padx=10, pady=(10, 5))

        manual_hwid_frame = tk.Frame(hwid_frame, bg=self.theme['white'])
        manual_hwid_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.manual_hwid_var = tk.StringVar()
        manual_hwid_entry = tk.Entry(manual_hwid_frame, textvariable=self.manual_hwid_var,
                                    font=('Segoe UI', 9), width=50)
        manual_hwid_entry.pack(side='left', fill='x', expand=True)

        # Lisans parametreleri
        params_frame = tk.LabelFrame(content, text="Lisans Parametreleri",
                                    font=('Segoe UI', 10, 'bold'), bg=self.theme['white'])
        params_frame.pack(fill='x', pady=(0, 15))

        # Ürün adı
        product_frame = tk.Frame(params_frame, bg=self.theme['white'])
        product_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(product_frame, text="Ürün:", font=('Segoe UI', 9), bg=self.theme['white'], width=15).pack(side='left')
        self.product_var = tk.StringVar(value="SUSTAINAGE")
        tk.Entry(product_frame, textvariable=self.product_var, font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True, padx=(5, 0))

        # Sürüm
        edition_frame = tk.Frame(params_frame, bg=self.theme['white'])
        edition_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(edition_frame, text="Sürüm:", font=('Segoe UI', 9), bg=self.theme['white'], width=15).pack(side='left')
        self.edition_var = tk.StringVar(value="CORE")
        edition_combo = ttk.Combobox(edition_frame, textvariable=self.edition_var,
                                    values=['CORE', 'SDG', 'ENTERPRISE'], state='readonly')
        edition_combo.pack(side='left', fill='x', expand=True, padx=(5, 0))

        # Geçerlilik süresi
        duration_frame = tk.Frame(params_frame, bg=self.theme['white'])
        duration_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(duration_frame, text="Süre:", font=('Segoe UI', 9), bg=self.theme['white'], width=15).pack(side='left')

        duration_type_frame = tk.Frame(duration_frame, bg=self.theme['white'])
        duration_type_frame.pack(side='left', fill='x', expand=True, padx=(5, 0))

        self.duration_type_var = tk.StringVar(value="days")
        tk.Radiobutton(duration_type_frame, text="Gün", variable=self.duration_type_var,
                      value="days", font=('Segoe UI', 9), bg=self.theme['white'],
                      command=self.toggle_duration_input).pack(side='left')

        tk.Radiobutton(duration_type_frame, text="Tarih", variable=self.duration_type_var,
                      value="date", font=('Segoe UI', 9), bg=self.theme['white'],
                      command=self.toggle_duration_input).pack(side='left', padx=(10, 0))

        # Süre girişi
        duration_input_frame = tk.Frame(params_frame, bg=self.theme['white'])
        duration_input_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(duration_input_frame, text="Değer:", font=('Segoe UI', 9), bg=self.theme['white'], width=15).pack(side='left')

        self.duration_var = tk.StringVar(value="365")
        self.duration_entry = tk.Entry(duration_input_frame, textvariable=self.duration_var,
                                      font=('Segoe UI', 9))
        self.duration_entry.pack(side='left', fill='x', expand=True, padx=(5, 5))

        self.duration_label = tk.Label(duration_input_frame, text="gün", font=('Segoe UI', 9), bg=self.theme['white'])
        self.duration_label.pack(side='left')

        # Maksimum kullanıcı sayısı
        users_frame = tk.Frame(params_frame, bg=self.theme['white'])
        users_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(users_frame, text="Max Kullanıcı:", font=('Segoe UI', 9), bg=self.theme['white'], width=15).pack(side='left')
        self.max_users_var = tk.StringVar()
        tk.Entry(users_frame, textvariable=self.max_users_var, font=('Segoe UI', 9)).pack(side='left', fill='x', expand=True, padx=(5, 0))

        # Not
        note_frame = tk.Frame(params_frame, bg=self.theme['white'])
        note_frame.pack(fill='x', padx=10, pady=(5, 10))

        tk.Label(note_frame, text="Not:", font=('Segoe UI', 9), bg=self.theme['white'], width=15).pack(anchor='nw', side='left')
        self.note_text = tk.Text(note_frame, font=('Segoe UI', 9), height=3, width=30)
        self.note_text.pack(side='left', fill='x', expand=True, padx=(5, 0))

        # Butonlar
        button_frame = tk.Frame(content, bg=self.theme['white'])
        button_frame.pack(fill='x', pady=(0, 10))

        tk.Button(button_frame, text=" Anahtar Çifti Oluştur", font=('Segoe UI', 9, 'bold'),
                 bg=self.theme['warning'], fg='white', relief='flat', bd=0, cursor='hand2',
                 command=self.create_key_pair).pack(side='left', padx=(0, 5))

        tk.Button(button_frame, text=" Lisans Anahtarı Oluştur", font=('Segoe UI', 9, 'bold'),
                 bg=self.theme['success'], fg='white', relief='flat', bd=0, cursor='hand2',
                 command=self.generate_license_key).pack(side='left', padx=5)

        tk.Button(button_frame, text=" Kopyala", font=('Segoe UI', 9, 'bold'),
                 bg=self.theme['secondary'], fg='white', relief='flat', bd=0, cursor='hand2',
                 command=self.copy_license_key).pack(side='right')

        # Sonuç alanı
        result_frame = tk.LabelFrame(content, text="Oluşturulan Lisans Anahtarı",
                                    font=('Segoe UI', 10, 'bold'), bg=self.theme['white'])
        result_frame.pack(fill='both', expand=True, pady=(10, 0))

        self.result_text = tk.Text(result_frame, font=('Consolas', 8), height=8,
                                  bg='#f8f9fa', relief='solid', bd=1, wrap='word')
        result_scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        self.result_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        result_scrollbar.pack(side='right', fill='y', pady=10)

        # Varsayılan mesaj
        self.result_text.insert('1.0', "Lisans anahtarı oluşturmak için yukarıdaki bilgileri doldurun ve 'Lisans Anahtarı Oluştur' butonuna tıklayın.")
        self.result_text.configure(state='disabled')

        self.current_license_key = ""

    def create_license_management_panel(self, parent) -> None:
        """Lisans yönetimi paneli"""
        # Panel başlığı
        header_frame = tk.Frame(parent, bg=self.theme['secondary'], height=40)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="Lisans Yönetimi",
                font=('Segoe UI', 12, 'bold'), fg='white', bg=self.theme['secondary']).pack(expand=True)

        # İçerik
        content = tk.Frame(parent, bg=self.theme['white'])
        content.pack(fill='both', expand=True, padx=20, pady=20)

        # Anahtar çifti durumu
        key_status_frame = tk.LabelFrame(content, text="Anahtar Çifti Durumu",
                                        font=('Segoe UI', 10, 'bold'), bg=self.theme['white'])
        key_status_frame.pack(fill='x', pady=(0, 15))

        self.key_status_label = tk.Label(key_status_frame, text="Kontrol ediliyor...",
                                        font=('Segoe UI', 9), bg=self.theme['white'], fg=self.theme['warning'])
        self.key_status_label.pack(pady=10)

        # Anahtar çifti işlemleri
        key_actions_frame = tk.Frame(key_status_frame, bg=self.theme['white'])
        key_actions_frame.pack(fill='x', padx=10, pady=(0, 10))

        tk.Button(key_actions_frame, text=" Durumu Kontrol Et", font=('Segoe UI', 9),
                 bg=self.theme['secondary'], fg='white', relief='flat', bd=0, cursor='hand2',
                 command=self.check_key_status).pack(side='left', padx=(0, 5))

        tk.Button(key_actions_frame, text=" Klasörü Aç", font=('Segoe UI', 9),
                 bg=self.theme['primary'], fg='white', relief='flat', bd=0, cursor='hand2',
                 command=self.open_keys_folder).pack(side='left', padx=5)

        # Lisans geçmişi
        history_frame = tk.LabelFrame(content, text="Lisans Geçmişi",
                                     font=('Segoe UI', 10, 'bold'), bg=self.theme['white'])
        history_frame.pack(fill='both', expand=True, pady=(0, 15))

        # Treeview
        tree_frame = tk.Frame(history_frame, bg=self.theme['white'])
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('Tarih', 'HWID', 'Süre', 'Durum')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)

        self.history_tree.heading('Tarih', text='Oluşturma Tarihi')
        self.history_tree.heading('HWID', text='HWID CORE')
        self.history_tree.heading('Süre', text='Geçerlilik')
        self.history_tree.heading('Durum', text='Durum')

        self.history_tree.column('Tarih', width=120)
        self.history_tree.column('HWID', width=200)
        self.history_tree.column('Süre', width=100)
        self.history_tree.column('Durum', width=80)

        history_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)

        self.history_tree.pack(side='left', fill='both', expand=True)
        history_scrollbar.pack(side='right', fill='y')

        # Lisans yönetimi butonları
        mgmt_button_frame = tk.Frame(content, bg=self.theme['white'])
        mgmt_button_frame.pack(fill='x', pady=(0, 10))

        tk.Button(mgmt_button_frame, text=" Lisans İstatistikleri", font=('Segoe UI', 9),
                 bg=self.theme['primary'], fg='white', relief='flat', bd=0, cursor='hand2',
                 command=self.show_license_stats).pack(side='left', padx=(0, 5))

        tk.Button(mgmt_button_frame, text=" Lisans Raporu", font=('Segoe UI', 9),
                 bg=self.theme['secondary'], fg='white', relief='flat', bd=0, cursor='hand2',
                 command=self.export_license_report).pack(side='left', padx=5)

        tk.Button(mgmt_button_frame, text="️ Temizle", font=('Segoe UI', 9),
                 bg=self.theme['danger'], fg='white', relief='flat', bd=0, cursor='hand2',
                 command=self.clear_license_history).pack(side='right')

        # İlk yükleme
        self.check_key_status()
        self.load_license_history()

    def toggle_duration_input(self) -> None:
        """Süre giriş tipini değiştir"""
        if self.duration_type_var.get() == "days":
            self.duration_label.config(text="gün")
            self.duration_var.set("365")
        else:
            self.duration_label.config(text="(YYYY-MM-DD)")
            self.duration_var.set("2025-12-31")

    def get_current_hwid(self) -> None:
        """Mevcut sistemin HWID'sini al"""
        try:
            # Doğrudan import et
            sys.path.append(os.path.join(self.base_dir, "yonetim", "security"))
            from core.hw import hwid_full_core

            # HWID'yi al
            s, full, core = hwid_full_core()

            if core:
                self.hwid_var.set(core)
                messagebox.showinfo("Başarılı", f"HWID CORE alındı: {core[:20]}...")
            else:
                messagebox.showerror("Hata", "HWID alınamadı!")

        except Exception as e:
            messagebox.showerror("Hata", f"HWID alınırken hata: {e}")

    def create_key_pair(self) -> None:
        """Anahtar çifti oluştur"""
        try:
            # Keys dizinini oluştur
            os.makedirs(self.keys_dir, exist_ok=True)

            # Anahtar çifti oluştur
            private_path, public_path = create_key_pair(self.keys_dir)

            messagebox.showinfo("Başarılı",
                              f"Anahtar çifti oluşturuldu!\n\n"
                              f"Özel anahtar: {private_path}\n"
                              f"Genel anahtar: {public_path}\n\n"
                              f"ÖNEMLİ: Özel anahtarı güvenli tutun!")

            self.check_key_status()

        except NameError:
            messagebox.showerror("Hata", "Lisans generator modülü yüklenemedi!\n\nLütfen yonetim/licensing/tools/license_generator.py dosyasının varlığını kontrol edin.")
        except Exception as e:
            messagebox.showerror("Hata", f"Anahtar çifti oluşturulamadı: {e}")

    def generate_license_key(self) -> None:
        """Lisans anahtarı oluştur"""
        try:
            # Parametreleri kontrol et
            hwid_core = self.hwid_var.get().strip() or self.manual_hwid_var.get().strip()

            if not hwid_core:
                messagebox.showerror("Hata", "HWID CORE girmelisiniz!")
                return

            # Anahtar çifti kontrolü
            private_key_path = os.path.join(self.keys_dir, "license_private_key.pem")
            if not os.path.exists(private_key_path):
                messagebox.showerror("Hata", "Önce anahtar çifti oluşturmalısınız!")
                return

            # Parametreleri al
            product = self.product_var.get().strip()
            edition = self.edition_var.get().strip()

            # Süre hesaplama
            if self.duration_type_var.get() == "days":
                days = int(self.duration_var.get())
                exp_date = None
            else:
                days = 0
                exp_date = self.duration_var.get()

            # Maksimum kullanıcı sayısı
            max_users = None
            if self.max_users_var.get().strip():
                max_users = int(self.max_users_var.get().strip())

            # Not
            note = self.note_text.get('1.0', 'end').strip()
            if not note:
                note = None

            # Lisans oluştur
            try:
                license_key = generate_license(
                    private_key_path=private_key_path,
                    product=product,
                    edition=edition,
                    hwid_core=hwid_core,
                    days=days,
                    max_users=max_users,
                    note=note,
                    exp_date=exp_date
                )
            except NameError:
                messagebox.showerror("Hata", "Lisans generator modülü yüklenemedi!\n\nLütfen yonetim/licensing/tools/license_generator.py dosyasının varlığını kontrol edin.")
                return

            # Sonucu göster
            self.result_text.configure(state='normal')
            self.result_text.delete('1.0', 'end')

            result_info = f"""Lisans Anahtarı Başarıyla Oluşturuldu!

Ürün: {product}
Sürüm: {edition}
HWID CORE: {hwid_core}
Geçerlilik: {self.duration_var.get()} {'gün' if self.duration_type_var.get() == 'days' else 'tarih'}
Max Kullanıcı: {max_users or 'Sınırsız'}
Not: {note or 'Yok'}

Lisans Anahtarı:
{license_key}

Bu anahtarı uygulamanın 'Lisans Anahtarı' alanına yapıştırın.
"""

            self.result_text.insert('1.0', result_info)
            self.result_text.configure(state='disabled')

            self.current_license_key = license_key

            # Geçmişe ekle
            self.add_to_license_history(hwid_core, self.duration_var.get(), "Aktif")

            messagebox.showinfo("Başarılı", "Lisans anahtarı oluşturuldu!")

        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz parametre: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Lisans oluşturulamadı: {e}")

    def copy_license_key(self) -> None:
        """Lisans anahtarını panoya kopyala"""
        if self.current_license_key:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(self.current_license_key)
            messagebox.showinfo("Başarılı", "Lisans anahtarı panoya kopyalandı!")
        else:
            messagebox.showwarning("Uyarı", "Kopyalanacak lisans anahtarı yok!")

    def check_key_status(self) -> None:
        """Anahtar çifti durumunu kontrol et"""
        try:
            private_key_path = os.path.join(self.keys_dir, "license_private_key.pem")
            public_key_path = os.path.join(self.keys_dir, "license_public_key.pem")

            if os.path.exists(private_key_path) and os.path.exists(public_key_path):
                self.key_status_label.config(
                    text=" Anahtar çifti mevcut",
                    fg=self.theme['success']
                )
            else:
                self.key_status_label.config(
                    text=" Anahtar çifti bulunamadı",
                    fg=self.theme['danger']
                )

        except Exception as e:
            self.key_status_label.config(
                text=f" Hata: {e}",
                fg=self.theme['danger']
            )

    def open_keys_folder(self) -> None:
        """Keys klasörünü aç"""
        try:
            os.makedirs(self.keys_dir, exist_ok=True)
            if sys.platform == 'win32':
                os.startfile(self.keys_dir)  # nosec B606
            elif sys.platform == 'darwin':
                opener = shutil.which('open') or 'open'
                subprocess.run([opener, self.keys_dir])  # nosec B603
            else:
                opener = shutil.which('xdg-open') or 'xdg-open'
                subprocess.run([opener, self.keys_dir])  # nosec B603
        except Exception as e:
            messagebox.showerror("Hata", f"Klasör açılamadı: {e}")

    def load_license_history(self) -> None:
        """Lisans geçmişini yükle"""
        try:
            # Geçmiş dosyası yolu
            history_file = os.path.join(self.base_dir, "data", "license_history.json")

            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)

                # Treeview'ı temizle
                for item in self.history_tree.get_children():
                    self.history_tree.delete(item)

                # Geçmişi ekle
                for entry in history:
                    self.history_tree.insert('', 'end', values=(
                        entry.get('date', ''),
                        entry.get('hwid', '')[:20] + '...' if len(entry.get('hwid', '')) > 20 else entry.get('hwid', ''),
                        entry.get('duration', ''),
                        entry.get('status', '')
                    ))
            else:
                # Boş geçmiş
                for item in self.history_tree.get_children():
                    self.history_tree.delete(item)

        except Exception as e:
            logging.error(f"Lisans geçmişi yüklenirken hata: {e}")

    def add_to_license_history(self, hwid: str, duration: str, status: str) -> None:
        """Lisans geçmişine ekle"""
        try:
            history_file = os.path.join(self.base_dir, "data", "license_history.json")

            # Geçmiş dosyasını oluştur veya yükle
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []

            # Yeni kayıt ekle
            new_entry = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hwid': hwid,
                'duration': duration,
                'status': status
            }

            history.insert(0, new_entry)  # En başa ekle

            # Maksimum 100 kayıt tut
            if len(history) > 100:
                history = history[:100]

            # Kaydet
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)

            # UI'yi güncelle
            self.load_license_history()

        except Exception as e:
            logging.error(f"Lisans geçmişine ekleme hatası: {e}")

    def show_license_stats(self) -> None:
        """Lisans istatistiklerini göster"""
        try:
            history_file = os.path.join(self.base_dir, "data", "license_history.json")

            if not os.path.exists(history_file):
                messagebox.showinfo("Bilgi", "Henüz lisans geçmişi yok!")
                return

            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # İstatistikleri hesapla
            total_licenses = len(history)
            active_licenses = len([h for h in history if h.get('status') == 'Aktif'])
            unique_hwids = len(set(h.get('hwid') for h in history))

            # Son 30 gün
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_licenses = len([
                h for h in history
                if datetime.strptime(h.get('date', ''), '%Y-%m-%d %H:%M:%S') >= thirty_days_ago
            ])

            stats_window = tk.Toplevel(self.parent)
            stats_window.title(" Lisans İstatistikleri")
            stats_window.geometry("400x300")
            stats_window.configure(bg=self.theme['light'])

            # Başlık
            tk.Label(stats_window, text=" Lisans İstatistikleri",
                    font=('Segoe UI', 14, 'bold'), bg=self.theme['primary'],
                    fg='white', pady=10).pack(fill='x')

            # İstatistikler
            content = tk.Frame(stats_window, bg=self.theme['light'])
            content.pack(fill='both', expand=True, padx=20, pady=20)

            stats = [
                ("Toplam Lisans", str(total_licenses)),
                ("Aktif Lisans", str(active_licenses)),
                ("Benzersiz HWID", str(unique_hwids)),
                ("Son 30 Gün", str(recent_licenses))
            ]

            for label, value in stats:
                frame = tk.Frame(content, bg=self.theme['white'], relief='solid', bd=1)
                frame.pack(fill='x', pady=5)

                tk.Label(frame, text=label, font=('Segoe UI', 11),
                        bg=self.theme['white'], anchor='w').pack(side='left', padx=15, pady=10)
                tk.Label(frame, text=value, font=('Segoe UI', 11, 'bold'),
                        bg=self.theme['white'], fg=self.theme['primary'],
                        anchor='e').pack(side='right', padx=15, pady=10)

        except Exception as e:
            messagebox.showerror("Hata", f"İstatistikler alınamadı: {e}")

    def export_license_report(self) -> None:
        """Lisans raporunu dışa aktar"""
        try:
            history_file = os.path.join(self.base_dir, "data", "license_history.json")

            if not os.path.exists(history_file):
                messagebox.showinfo("Bilgi", "Dışa aktarılacak veri yok!")
                return

            # Dosya seçimi
            file_path = filedialog.asksaveasfilename(
                title="Lisans Raporunu Kaydet",
                defaultextension=".csv",
                filetypes=[("CSV dosyaları", "*.csv"), ("JSON dosyaları", "*.json")]
            )

            if not file_path:
                return

            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            if file_path.endswith('.csv'):
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['date', 'hwid', 'duration', 'status']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(history)
            else:
                with open(file_path, 'w', encoding='utf-8') as jsonfile:
                    json.dump(history, jsonfile, indent=2, ensure_ascii=False)

            messagebox.showinfo("Başarılı", f"Rapor dışa aktarıldı: {file_path}")

        except Exception as e:
            messagebox.showerror("Hata", f"Rapor dışa aktarılamadı: {e}")

    def clear_license_history(self) -> None:
        """Lisans geçmişini temizle"""
        result = messagebox.askyesno("Onay", "Lisans geçmişini temizlemek istediğinizden emin misiniz?")
        if result:
            try:
                history_file = os.path.join(self.base_dir, "data", "license_history.json")
                if os.path.exists(history_file):
                    os.remove(history_file)

                self.load_license_history()
                messagebox.showinfo("Başarılı", "Lisans geçmişi temizlendi!")

            except Exception as e:
                messagebox.showerror("Hata", f"Geçmiş temizlenemedi: {e}")
