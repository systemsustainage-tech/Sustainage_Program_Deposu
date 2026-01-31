# -*- coding: utf-8 -*-
"""
WEB ANKET YÖNETİM GUI
Token-based web anket sistemi arayüzü
"""

import logging
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from modules.surveys.web_survey_integrator import WebSurveyIntegrator
from utils.ui_theme import apply_theme
from utils.language_manager import LanguageManager
from config.icons import Icons
from config.database import DB_PATH


class WebSurveyGUI:
    """Web anket yönetim arayüzü"""

    def __init__(self, parent, company_id: int, db_path: str):
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id
        self.db_path = db_path
        self.integrator = WebSurveyIntegrator(db_path)

        self.setup_ui()
        self.load_surveys()

    def setup_ui(self):
        """Arayüzü oluştur"""
        apply_theme(self.parent)
        main_frame = ttk.Frame(self.parent, style='Content.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        header = ttk.Frame(main_frame, style='Toolbar.TFrame')
        header.pack(fill='x')

        title = tk.Label(header, text="🌐 Web Anket Yönetimi",
                        font=('Segoe UI', 16, 'bold'), fg='#2c3e50')
        title.pack(side='left')

        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(10, 10))

        ttk.Button(toolbar, text=f"{Icons.ADD} Yeni Anket", style='Primary.TButton',
                   command=self.create_new_survey).pack(side='left', padx=5)
        ttk.Button(toolbar, text=f"{Icons.EMAIL} E-posta Gönder", style='Primary.TButton',
                   command=self.send_email).pack(side='left', padx=5)
        ttk.Button(toolbar, text=f"{Icons.LOADING} Yanıtları Çek", style='Primary.TButton',
                   command=self.fetch_responses).pack(side='left', padx=5)
        ttk.Button(toolbar, text=f"{Icons.REPORT} Yanıtları İşle", style='Primary.TButton',
                   command=self.process_responses).pack(side='left', padx=5)
        ttk.Button(toolbar, text=f"{Icons.PAUSE} Duraklat", style='Accent.TButton',
                   command=self.pause_survey).pack(side='left', padx=5)
        ttk.Button(toolbar, text=f"{Icons.SUCCESS} Aktifleştir", style='Primary.TButton',
                   command=self.activate_survey).pack(side='left', padx=5)
        ttk.Button(toolbar, text=f"{Icons.LOADING} Yenile", style='Primary.TButton',
                   command=self.load_surveys).pack(side='left', padx=5)
        ttk.Button(toolbar, text=self.lm.tr("btn_report_center", "Rapor Merkezi"), style='Primary.TButton',
                   command=self.open_report_center).pack(side='left', padx=5)

        # Liste frame
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Treeview
        columns = ('ID', 'Anket Adı', 'Modül', 'Token', 'Yanıt', 'Durum', 'Son Tarih')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Anket Adı':
                self.tree.column(col, width=250)
            elif col == 'Token':
                self.tree.column(col, width=200)
            else:
                self.tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Durum çubuğu
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', padx=20, pady=10)

        self.status_label = tk.Label(status_frame, text="Hazır",
                                     font=('Segoe UI', 9), fg='#666')
        self.status_label.pack(side='left')

    def load_surveys(self):
        """Anketleri yükle"""
        try:
            # Temizle
            for item in self.tree.get_children():
                self.tree.delete(item)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, survey_name, module_name, survey_token,
                       response_count, status, deadline_date
                FROM web_surveys
                WHERE company_id = ?
                ORDER BY created_at DESC
            """, (self.company_id,))

            surveys = cursor.fetchall()
            conn.close()

            for survey in surveys:
                self.tree.insert('', 'end', values=survey)

            self.status_label['text'] = f"{len(surveys)} anket listelendi"

        except Exception as e:
            messagebox.showerror("Hata", f"Anket yükleme hatası: {e}")

    def create_new_survey(self):
        """Yeni anket oluştur"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Yeni Web Anket Oluştur")
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Form
        form_frame = ttk.LabelFrame(dialog, text="Anket Bilgileri", padding=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Anket adı
        ttk.Label(form_frame, text="Anket Adı:").grid(row=0, column=0, sticky='w', pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=40).grid(row=0, column=1, pady=5)

        # Modül
        ttk.Label(form_frame, text="Modül:").grid(row=1, column=0, sticky='w', pady=5)
        module_var = tk.StringVar(value="materiality")
        module_combo = ttk.Combobox(form_frame, textvariable=module_var, width=38,
                                    values=["materiality", "gri", "sdg", "stakeholder", "ungc"],
                                    state='readonly')
        module_combo.grid(row=1, column=1, pady=5)

        # Açıklama
        ttk.Label(form_frame, text="Açıklama:").grid(row=2, column=0, sticky='nw', pady=5)
        description_text = tk.Text(form_frame, height=4, width=40)
        description_text.grid(row=2, column=1, pady=5)

        # Son tarih (gün)
        ttk.Label(form_frame, text="Son Tarih (gün):").grid(row=3, column=0, sticky='w', pady=5)
        days_var = tk.StringVar(value="30")
        ttk.Entry(form_frame, textvariable=days_var, width=40).grid(row=3, column=1, pady=5)

        # Konu sayısı bilgisi
        info_label = tk.Label(form_frame,
                             text=f"{Icons.LIGHTBULB} Konular: Double Materiality için 10 standart konu kullanılacak",
                             font=('Segoe UI', 9), fg='#666', wraplength=400, justify='left')
        info_label.grid(row=4, column=0, columnspan=2, pady=10)

        def create():
            """Anketi oluştur"""
            name = name_var.get().strip()
            module = module_var.get()
            description = description_text.get('1.0', tk.END).strip()
            days = int(days_var.get() or 30)

            if not name:
                messagebox.showerror("Hata", "Anket adı gereklidir!")
                return

            # Standart konular (Double Materiality)
            topics = [
                {'topic_code': 'CLIMATE_CHANGE', 'topic_name': 'İklim Değişikliği', 'topic_category': 'Çevresel'},
                {'topic_code': 'ENERGY_EFFICIENCY', 'topic_name': 'Enerji Verimliliği', 'topic_category': 'Çevresel'},
                {'topic_code': 'WATER_MANAGEMENT', 'topic_name': 'Su Yönetimi', 'topic_category': 'Çevresel'},
                {'topic_code': 'WASTE_CIRCULAR', 'topic_name': 'Atık Yönetimi', 'topic_category': 'Çevresel'},
                {'topic_code': 'BIODIVERSITY', 'topic_name': 'Biyoçeşitlilik', 'topic_category': 'Çevresel'},
                {'topic_code': 'EMPLOYEE_HEALTH', 'topic_name': 'Çalışan Sağlığı', 'topic_category': 'Sosyal'},
                {'topic_code': 'DIVERSITY_INCLUSION', 'topic_name': 'Çeşitlilik ve Eşitlik', 'topic_category': 'Sosyal'},
                {'topic_code': 'HUMAN_RIGHTS', 'topic_name': 'İnsan Hakları', 'topic_category': 'Sosyal'},
                {'topic_code': 'SUPPLY_CHAIN', 'topic_name': 'Tedarik Zinciri', 'topic_category': 'Ekonomik'},
                {'topic_code': 'ETHICS_COMPLIANCE', 'topic_name': 'Etik ve Uyum', 'topic_category': 'Yönetişim'}
            ]

            self.status_label['text'] = "Anket oluşturuluyor..."
            dialog.update()

            # Thread'de oluştur
            def create_thread():
                result = self.integrator.create_web_survey(
                    company_id=self.company_id,
                    module_name=module,
                    survey_name=name,
                    topics=topics,
                    description=description,
                    deadline_days=days
                )

                if result['success']:
                    messagebox.showinfo("Başarılı",
                                       f"Web anket oluşturuldu!\n\n"
                                       f"Token: {result['token']}\n"
                                       f"URL: {result['survey_url']}\n\n"
                                       f"Şimdi e-posta gönderebilirsiniz.")
                    dialog.destroy()
                    self.load_surveys()
                else:
                    messagebox.showerror("Hata", f"Anket oluşturulamadı:\n{result['message']}")

                self.status_label['text'] = "Hazır"

            threading.Thread(target=create_thread, daemon=True).start()

        # Butonlar
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill='x', padx=20, pady=10)

        ttk.Button(btn_frame, text="Oluştur", style='Primary.TButton', command=create).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.lm.tr("btn_cancel", "İptal"), style='Primary.TButton', command=dialog.destroy).pack(side='left', padx=5)

    def send_email(self):
        """Seçili anket için e-posta gönder"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir anket seçin!")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        survey_token = values[3]

        # E-posta dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Anket E-postası Gönder")
        dialog.geometry("500x300")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Form
        form_frame = ttk.LabelFrame(dialog, text="Alıcı Bilgileri", padding=20)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(form_frame, text="Alıcı E-posta:").grid(row=0, column=0, sticky='w', pady=5)
        email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=email_var, width=35).grid(row=0, column=1, pady=5)

        ttk.Label(form_frame, text="Alıcı Adı:").grid(row=1, column=0, sticky='w', pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=35).grid(row=1, column=1, pady=5)

        ttk.Label(form_frame, text="Özel Mesaj:").grid(row=2, column=0, sticky='nw', pady=5)
        message_text = tk.Text(form_frame, height=4, width=35)
        message_text.grid(row=2, column=1, pady=5)
        message_text.insert('1.0', "Anket davetimize katılımınızı bekliyoruz.")

        def send():
            email = email_var.get().strip()
            name = name_var.get().strip()
            message = message_text.get('1.0', tk.END).strip()

            if not email or not name:
                messagebox.showerror("Hata", "E-posta ve ad gereklidir!")
                return

            self.status_label['text'] = "E-posta gönderiliyor..."
            dialog.update()

            def send_thread():
                success = self.integrator.send_survey_email(
                    survey_token=survey_token,
                    recipient_email=email,
                    recipient_name=name,
                    custom_message=message
                )

                if success:
                    messagebox.showinfo("Başarılı", f"E-posta gönderildi!\n\nAlıcı: {email}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Hata", "E-posta gönderilemedi!")

                self.status_label['text'] = "Hazır"

            threading.Thread(target=send_thread, daemon=True).start()

        # Butonlar
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill='x', padx=20, pady=10)

        ttk.Button(btn_frame, text="Gönder", style='Primary.TButton', command=send).pack(side='left', padx=5)
        ttk.Button(btn_frame, text=self.lm.tr("btn_cancel", "İptal"), style='Primary.TButton', command=dialog.destroy).pack(side='left', padx=5)

    def open_report_center(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('genel')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for genel: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor Merkezi açılamadı:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def fetch_responses(self):
        """Yanıtları web'den çek"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir anket seçin!")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        survey_token = values[3]

        self.status_label['text'] = "Yanıtlar çekiliyor..."

        def fetch_thread():
            responses = self.integrator.fetch_responses(survey_token)

            messagebox.showinfo("Yanıtlar",
                               f"Çekilen yanıt sayısı: {len(responses)}\n\n"
                               f"Yanıtlar veritabanına kaydedildi.\n"
                               f"Şimdi 'Yanıtları İşle' butonuna tıklayarak\n"
                               f"ilgili modüle aktarabilirsiniz.")

            self.load_surveys()
            self.status_label['text'] = "Hazır"

        threading.Thread(target=fetch_thread, daemon=True).start()

    def process_responses(self):
        """Yanıtları ilgili modüle aktar"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir anket seçin!")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        survey_token = values[3]
        module_name = values[2]

        if messagebox.askyesno("Onay",
                               f"Yanıtlar '{module_name}' modülüne aktarılacak.\n\n"
                               f"Devam etmek istiyor musunuz?"):

            self.status_label['text'] = "Yanıtlar işleniyor..."

            def process_thread():
                result = self.integrator.process_responses_to_module(survey_token)

                if result['success']:
                    messagebox.showinfo("Başarılı",
                                       f"{result['message']}\n\n"
                                       f"İşlenen Yanıt: {result.get('processed_count', 0)}")
                else:
                    messagebox.showerror("Hata", f"İşleme hatası:\n{result['message']}")

                self.status_label['text'] = "Hazır"

            threading.Thread(target=process_thread, daemon=True).start()

    def pause_survey(self):
        """Anketi duraklat"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir anket seçin!")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        values[0]
        survey_name = values[1]
        survey_token = values[3]

        if messagebox.askyesno("Onay",
                               f"'{survey_name}' anketi duraklatılacak.\n\n"
                               f"Duraklatılan anketler yeni yanıt kabul etmez.\n\n"
                               f"Devam etmek istiyor musunuz?"):

            self.status_label['text'] = "Anket duraklatılıyor..."

            def pause_thread():
                result = self.integrator.update_survey_status(survey_token, 'paused')

                if result['success']:
                    messagebox.showinfo("Başarılı", "Anket duraklatıldı!")
                    self.load_surveys()
                else:
                    messagebox.showerror("Hata", f"Güncelleme başarısız: {result.get('message', 'Bilinmeyen hata')}")

                self.status_label['text'] = "Hazır"

            threading.Thread(target=pause_thread, daemon=True).start()

    def activate_survey(self):
        """Anketi aktifleştir"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir anket seçin!")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        values[0]
        survey_name = values[1]
        survey_token = values[3]

        if messagebox.askyesno("Onay",
                               f"'{survey_name}' anketi aktifleştirilecek.\n\n"
                               f"Aktif anketler yeni yanıt kabul eder.\n\n"
                               f"Devam etmek istiyor musunuz?"):

            self.status_label['text'] = "Anket aktifleştiriliyor..."

            def activate_thread():
                result = self.integrator.update_survey_status(survey_token, 'active')

                if result['success']:
                    messagebox.showinfo("Başarılı", "Anket aktifleştirildi!")
                    self.load_surveys()
                else:
                    messagebox.showerror("Hata", f"Güncelleme başarısız: {result.get('message', 'Bilinmeyen hata')}")

                self.status_label['text'] = "Hazır"

            threading.Thread(target=activate_thread, daemon=True).start()


# Test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Web Anket Sistemi Test")
    root.geometry("1000x600")

    WebSurveyGUI(root, company_id=1, db_path=DB_PATH)

    root.mainloop()

