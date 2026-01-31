#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Anket Dağıtım GUI
Anketleri email ile dağıtma sistemi
"""

import logging
import csv
import os
import sys
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox, ttk

from utils.language_manager import LanguageManager

# Email manager'ı import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from services.email_service import EmailService
except ImportError:
    EmailService = None
    logging.info("️ Email Service yüklenemedi. Email özellikleri devre dışı.")

class SurveyDistributionGUI:
    def __init__(self, parent) -> None:
        self.parent = parent
        self.lm = LanguageManager()
        self.email_service = EmailService() if EmailService else None
        self.recipients = []
        self.setup_ui()

        # Email service yoksa kullanıcıyı uyar
        if not self.email_service:
            messagebox.showwarning("Uyarı",
                "Email sistemi yapılandırılmamış.\n"
                "Email gönderme özellikleri kullanılamayacak.\n\n"
                "Lütfen config/email_config.py dosyasını yapılandırın.")

    def setup_ui(self) -> None:
        """Anket dağıtım arayüzünü oluştur"""
        self.parent.title("Anket Dağıtım Sistemi")
        self.parent.geometry("800x700")
        self.parent.configure(bg='#f0f0f0')

        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text=" Anket Dağıtım Sistemi",
                              font=('Segoe UI', 20, 'bold'), fg='#2E8B57', bg='#f0f0f0')
        title_label.pack(pady=(0, 20))

        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Anket Bilgileri sekmesi
        self.create_survey_info_tab()

        # Alıcılar sekmesi
        self.create_recipients_tab()

        # Gönderim sekmesi
        self.create_sending_tab()

    def create_survey_info_tab(self) -> None:
        """Anket bilgileri sekmesi"""
        survey_frame = ttk.Frame(self.notebook)
        self.notebook.add(survey_frame, text=" Anket Bilgileri")

        # Anket bilgileri formu
        form_frame = tk.Frame(survey_frame, bg='white', relief='solid', bd=1)
        form_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(form_frame, text="Anket Bilgileri",
                font=('Segoe UI', 14, 'bold'), fg='#2E8B57', bg='white').pack(pady=20)

        # Anket başlığı
        tk.Label(form_frame, text="Anket Başlığı:",
                font=('Segoe UI', 10, 'bold'), fg='#333333', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        self.survey_title = tk.Entry(form_frame, font=('Segoe UI', 11), width=60)
        self.survey_title.pack(padx=20, pady=(0, 15))

        # Anket açıklaması
        tk.Label(form_frame, text="Açıklama:",
                font=('Segoe UI', 10, 'bold'), fg='#333333', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        self.survey_description = tk.Text(form_frame, font=('Segoe UI', 10), width=60, height=4)
        self.survey_description.pack(padx=20, pady=(0, 15))

        # Tahmini süre
        time_frame = tk.Frame(form_frame, bg='white')
        time_frame.pack(fill='x', padx=20, pady=(0, 15))
        tk.Label(time_frame, text="Tahmini Süre (dakika):",
                font=('Segoe UI', 10, 'bold'), fg='#333333', bg='white').pack(side='left')
        self.estimated_time = tk.Entry(time_frame, font=('Segoe UI', 11), width=10)
        self.estimated_time.insert(0, "10")
        self.estimated_time.pack(side='left', padx=(10, 0))

        # Son tarih
        deadline_frame = tk.Frame(form_frame, bg='white')
        deadline_frame.pack(fill='x', padx=20, pady=(0, 15))
        tk.Label(deadline_frame, text="Son Tarih:",
                font=('Segoe UI', 10, 'bold'), fg='#333333', bg='white').pack(side='left')
        self.deadline = tk.Entry(deadline_frame, font=('Segoe UI', 11), width=15)
        self.deadline.insert(0, (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))
        self.deadline.pack(side='left', padx=(10, 0))

        # Anket URL'si
        tk.Label(form_frame, text="Anket URL'si:",
                font=('Segoe UI', 10, 'bold'), fg='#333333', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        self.survey_url = tk.Entry(form_frame, font=('Segoe UI', 11), width=60)
        self.survey_url.insert(0, "http://localhost:8080/survey")
        self.survey_url.pack(padx=20, pady=(0, 15))

        # Anket kodu
        tk.Label(form_frame, text="Anket Kodu (opsiyonel):",
                font=('Segoe UI', 10, 'bold'), fg='#333333', bg='white').pack(anchor='w', padx=20, pady=(10, 5))
        self.survey_code = tk.Entry(form_frame, font=('Segoe UI', 11), width=20)
        self.survey_code.pack(padx=20, pady=(0, 20))

    def create_recipients_tab(self) -> None:
        """Alıcılar sekmesi"""
        recipients_frame = ttk.Frame(self.notebook)
        self.notebook.add(recipients_frame, text=" Alıcılar")

        # Alıcı ekleme paneli
        add_frame = tk.Frame(recipients_frame, bg='white', relief='solid', bd=1)
        add_frame.pack(fill='x', padx=20, pady=(20, 10))

        tk.Label(add_frame, text="Alıcı Ekle",
                font=('Segoe UI', 12, 'bold'), fg='#2E8B57', bg='white').pack(pady=15)

        # Alıcı bilgileri
        info_frame = tk.Frame(add_frame, bg='white')
        info_frame.pack(fill='x', padx=20, pady=(0, 15))

        tk.Label(info_frame, text="Ad Soyad:", font=('Segoe UI', 10), bg='white').pack(side='left')
        self.recipient_name = tk.Entry(info_frame, font=('Segoe UI', 10), width=20)
        self.recipient_name.pack(side='left', padx=(5, 20))

        tk.Label(info_frame, text="Email:", font=('Segoe UI', 10), bg='white').pack(side='left')
        self.recipient_email = tk.Entry(info_frame, font=('Segoe UI', 10), width=25)
        self.recipient_email.pack(side='left', padx=(5, 10))

        add_btn = tk.Button(info_frame, text="Ekle", font=('Segoe UI', 10), bg='#27ae60',
                           fg='white', relief='flat', command=self.add_recipient)
        add_btn.pack(side='left', padx=(10, 0))

        # CSV import butonu
        csv_btn = tk.Button(add_frame, text="CSV'den Alıcıları İçe Aktar",
                           font=('Segoe UI', 10), bg='#3498db', fg='white', relief='flat',
                           command=self.import_recipients_from_csv)
        csv_btn.pack(pady=(0, 15))

        # Alıcı listesi
        list_frame = tk.Frame(recipients_frame, bg='white', relief='solid', bd=1)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        tk.Label(list_frame, text="Alıcı Listesi",
                font=('Segoe UI', 12, 'bold'), fg='#2E8B57', bg='white').pack(pady=15)

        # Treeview
        columns = ('name', 'email')
        self.recipients_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        self.recipients_tree.heading('name', text='Ad Soyad')
        self.recipients_tree.heading('email', text='Email')

        self.recipients_tree.column('name', width=200)
        self.recipients_tree.column('email', width=300)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.recipients_tree.yview)
        self.recipients_tree.configure(yscrollcommand=scrollbar.set)

        self.recipients_tree.pack(side='left', fill='both', expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side='right', fill='y', pady=(0, 20))

        # Sil butonu
        delete_btn = tk.Button(list_frame, text="Seçili Alıcıyı Sil",
                              font=('Segoe UI', 10), bg='#e74c3c', fg='white', relief='flat',
                              command=self.delete_recipient)
        delete_btn.pack(pady=(0, 15))

    def create_sending_tab(self) -> None:
        """Gönderim sekmesi"""
        sending_frame = ttk.Frame(self.notebook)
        self.notebook.add(sending_frame, text=" Gönderim")

        # Gönderim paneli
        send_frame = tk.Frame(sending_frame, bg='white', relief='solid', bd=1)
        send_frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(send_frame, text="Email Gönderimi",
                font=('Segoe UI', 14, 'bold'), fg='#2E8B57', bg='white').pack(pady=20)

        # Özet bilgiler
        summary_frame = tk.Frame(send_frame, bg='#f8f9fa', relief='solid', bd=1)
        summary_frame.pack(fill='x', padx=20, pady=(0, 20))

        self.summary_label = tk.Label(summary_frame, text="Henüz alıcı eklenmedi",
                                    font=('Segoe UI', 10), fg='#666666', bg='#f8f9fa')
        self.summary_label.pack(pady=15)

        # Gönderim seçenekleri
        options_frame = tk.Frame(send_frame, bg='white')
        options_frame.pack(fill='x', padx=20, pady=(0, 20))

        # Test emaili
        test_frame = tk.Frame(options_frame, bg='white')
        test_frame.pack(fill='x', pady=(0, 15))
        tk.Label(test_frame, text="Test Emaili:", font=('Segoe UI', 10, 'bold'), bg='white').pack(side='left')
        self.test_email = tk.Entry(test_frame, font=('Segoe UI', 10), width=30)
        self.test_email.pack(side='left', padx=(10, 10))

        test_btn = tk.Button(test_frame, text="Test Gönder", font=('Segoe UI', 10), bg='#f39c12',
                            fg='white', relief='flat', command=self.send_test_email)
        test_btn.pack(side='left')

        # Toplu gönderim
        bulk_frame = tk.Frame(options_frame, bg='white')
        bulk_frame.pack(fill='x')

        self.send_all_btn = tk.Button(bulk_frame, text="Tüm Alıcılara Gönder",
                                     font=('Segoe UI', 12, 'bold'), bg='#27ae60', fg='white',
                                     relief='flat', bd=0, cursor='hand2', padx=30, pady=10,
                                     command=self.send_all_emails, state='disabled')
        self.send_all_btn.pack(pady=10)

        # Durum mesajı
        self.status_label = tk.Label(send_frame, text="",
                                   font=('Segoe UI', 10), fg='#666666', bg='white')
        self.status_label.pack(pady=(0, 20))

        # İlerleme çubuğu
        self.progress = ttk.Progressbar(send_frame, mode='determinate')
        self.progress.pack(fill='x', padx=20, pady=(0, 20))

    def add_recipient(self) -> None:
        """Alıcı ekle"""
        name = self.recipient_name.get().strip()
        email = self.recipient_email.get().strip()

        if not name or not email:
            messagebox.showwarning("Uyarı", "Lütfen ad soyad ve email adresini girin.")
            return

        if "@" not in email:
            messagebox.showwarning("Uyarı", "Geçerli bir email adresi girin.")
            return

        # Alıcıyı listeye ekle
        self.recipients.append({"name": name, "email": email})

        # Treeview'a ekle
        self.recipients_tree.insert('', 'end', values=(name, email))

        # Formu temizle
        self.recipient_name.delete(0, tk.END)
        self.recipient_email.delete(0, tk.END)

        # Özeti güncelle
        self.update_summary()

    def delete_recipient(self) -> None:
        """Seçili alıcıyı sil"""
        selection = self.recipients_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz alıcıyı seçin.")
            return

        # Seçili öğeyi al
        item = selection[0]
        values = self.recipients_tree.item(item, 'values')

        # Listeden kaldır
        self.recipients = [r for r in self.recipients if r["email"] != values[1]]

        # Treeview'dan kaldır
        self.recipients_tree.delete(item)

        # Özeti güncelle
        self.update_summary()

    def import_recipients_from_csv(self) -> None:
        """CSV'den alıcıları içe aktar"""
        file_path = filedialog.askopenfilename(
            title=self.lm.tr("select_csv_file", "CSV Dosyası Seç"),
            filetypes=[(self.lm.tr("file_csv", "CSV Dosyaları"), "*.csv"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    name = row.get('name', row.get('ad_soyad', row.get('Ad Soyad', '')))
                    email = row.get('email', row.get('email_adresi', row.get('Email', '')))

                    if name and email and "@" in email:
                        self.recipients.append({"name": name, "email": email})
                        self.recipients_tree.insert('', 'end', values=(name, email))

                messagebox.showinfo("Başarılı", f"{len(self.recipients)} alıcı içe aktarıldı.")
                self.update_summary()

        except Exception as e:
            messagebox.showerror("Hata", f"CSV dosyası okunamadı: {e}")

    def update_summary(self) -> None:
        """Özet bilgileri güncelle"""
        count = len(self.recipients)
        if count > 0:
            self.summary_label.config(text=f"Toplam {count} alıcı eklendi")
            self.send_all_btn.config(state='normal')
        else:
            self.summary_label.config(text="Henüz alıcı eklenmedi")
            self.send_all_btn.config(state='disabled')

    def send_test_email(self) -> None:
        """Test emaili gönder"""
        if not self.email_service:
            messagebox.showerror("Hata",
                "Email Service yapılandırılmamış.\n"
                "Lütfen config/email_config.py dosyasını düzenleyin.")
            return

        test_email = self.test_email.get().strip()
        if not test_email:
            messagebox.showwarning("Uyarı", "Test email adresini girin.")
            return

        if "@" not in test_email:
            messagebox.showwarning("Uyarı", "Geçerli bir email adresi girin.")
            return

        # Anket bilgilerini topla
        survey_data = self.get_survey_data()
        
        # Test emaili gönder
        try:
            result = self.email_service.send_template_email_with_result(
                to_email=test_email,
                template_key='survey_invitation',
                variables={
                    'stakeholder_name': "Test Kullanıcı",
                    'company_name': "Sustainage SDG",
                    'survey_name': survey_data.get('title', ''),
                    'survey_description': survey_data.get('description', ''),
                    'survey_url': survey_data.get('url', ''),
                    'deadline_date': survey_data.get('deadline', '')
                }
            )

            if result.get('success'):
                messagebox.showinfo("Başarılı", "Test emaili gönderildi!")
            else:
                messagebox.showerror("Hata", f"Test emaili gönderilemedi: {result.get('error')}")
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen hata: {e}")

    def send_all_emails(self) -> None:
        """Tüm alıcılara email gönder"""
        if not self.email_service:
            messagebox.showerror("Hata",
                "Email Service yapılandırılmamış.\n"
                "Lütfen config/email_config.py dosyasını düzenleyin.")
            return

        if not self.recipients:
            messagebox.showwarning("Uyarı", "Gönderilecek alıcı bulunmuyor.")
            return

        # Anket bilgilerini topla
        survey_data = self.get_survey_data()

        # Onay al
        if not messagebox.askyesno("Onay",
                                  f"{len(self.recipients)} alıcıya anket daveti gönderilecek.\n"
                                  "Devam etmek istiyor musunuz?"):
            return

        # İlerleme çubuğunu ayarla
        self.progress['maximum'] = len(self.recipients)
        self.progress['value'] = 0

        # Email gönderim işlemi
        success_count = 0
        error_count = 0

        for i, recipient in enumerate(self.recipients):
            try:
                result = self.email_service.send_template_email_with_result(
                    to_email=recipient['email'],
                    template_key='survey_invitation',
                    variables={
                        'stakeholder_name': recipient['name'],
                        'company_name': "Sustainage SDG",
                        'survey_name': survey_data.get('title', ''),
                        'survey_description': survey_data.get('description', ''),
                        'survey_url': survey_data.get('url', ''),
                        'deadline_date': survey_data.get('deadline', '')
                    }
                )

                if result.get('success'):
                    success_count += 1
                else:
                    error_count += 1
                    logging.error(f"Email gönderme hatası ({recipient['email']}): {result.get('error')}")

            except Exception as e:
                error_count += 1
                logging.error(f"Email loop error: {e}")
            
            # İlerleme güncelle
            self.progress['value'] = i + 1
            self.parent.update()
        
        # Sonuç mesajı
        if error_count == 0:
            messagebox.showinfo("Tamamlandı", f"{success_count} email başarıyla gönderildi.")
        else:
            messagebox.showwarning("Tamamlandı", 
                f"İşlem tamamlandı.\n\n"
                f"Başarılı: {success_count}\n"
                f"Hatalı: {error_count}")
        
        self.status_label.config(text=f"Son gönderim: {success_count} başarılı, {error_count} hatalı")

    def get_survey_data(self) -> None:
        """Anket verilerini topla"""
        return {
            "title": self.survey_title.get().strip() or "Sürdürülebilirlik Anketi",
            "description": self.survey_description.get('1.0', tk.END).strip(),
            "estimated_time": self.estimated_time.get().strip() or "10",
            "deadline": self.deadline.get().strip() or "Belirtilmemiş",
            "url": self.survey_url.get().strip() or "http://localhost:8080/survey",
            "code": self.survey_code.get().strip() or "N/A"
        }

def show_survey_distribution_window(parent) -> None:
    """Anket dağıtım penceresini göster"""
    distribution_window = tk.Toplevel(parent)
    distribution_window.grab_set()  # Modal pencere
    distribution_window.transient(parent)  # Ana pencereye bağlı

    SurveyDistributionGUI(distribution_window)

if __name__ == "__main__":
    root = tk.Tk()
    show_survey_distribution_window(root)
    root.mainloop()
