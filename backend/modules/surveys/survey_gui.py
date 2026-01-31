import logging
"""
Sustainage Anket Sistemi - GUI
Anket oluşturma, yönetme ve sonuçları görüntüleme ekranı

Tarih: 2025-10-23
"""

import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Dict, Optional

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .hosting_survey_manager import HostingSurveyManager
from config.icons import Icons
from config.database import DB_PATH


class SurveyManagementGUI:
    """Anket yönetim GUI'si"""

    def __init__(self, parent: tk.Tk, db_path: str = None):
        """
        Args:
            parent: Ana pencere
            db_path: Veritabanı yolu
        """
        self.parent = parent
        self.lm = LanguageManager()
        if db_path is None:
            try:
                from config.settings import get_db_path
                self.db_path = get_db_path()
            except Exception:
                self.db_path = DB_PATH
        else:
            self.db_path = db_path
        self.manager = HostingSurveyManager(self.db_path)

        self.window: Optional[tk.Toplevel] = None
        self.current_survey_id: Optional[int] = None

    def _bring_to_front(self) -> None:
        """Pencereyi ön plana getir ve odağı ver.
        Windows/Tkinter'da bazen mesaj kutularından sonra pencere arka plana
        düşebildiği için kısa süreli '-topmost' ile öne çıkartılır.
        """
        try:
            if self.window and self.window.winfo_exists():
                # Önce kaldır ve odağı ver
                self.window.lift()
                self.window.focus_force()
                self.window.focus()
                # Kısa süre topmost yap, sonra kaldır
                self.window.attributes('-topmost', True)
                self.window.after(400, lambda: self.window.attributes('-topmost', False))
        except Exception as e:
            # Sessizce geç; UI odak işlemi başarısızsa uygulama akışını bozmayalım
            logging.error(f"Silent error caught: {str(e)}")

    def show(self) -> None:
        """Ana pencereyi göster"""
        # Eğer pencere zaten açıksa, öne getir
        if self.window and self.window.winfo_exists():
            self.window.state('normal')  # Minimize'dan çıkar
            self.window.state('zoomed')  # Maximize
            self.window.lift()
            self.window.focus_force()
            self.window.attributes('-topmost', True)
            self.window.after(200, lambda: self.window.attributes('-topmost', False))
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title(self.lm.tr("survey_mgmt_title", "Sustainage - Anket Yönetimi"))

        # Önce normal boyutta aç
        self.window.geometry("1200x700")

        # Pencereyi güncelle
        self.window.update_idletasks()

        # Pencereyi tam ekran yap ve öne çıkar - DAHA AGRESİF
        self.window.attributes('-topmost', True)  # İlk önce topmost yap
        self.window.state('zoomed')  # Sonra maximize
        self.window.lift()
        self.window.focus_force()
        self.window.focus()

        # 500ms sonra topmost kaldır (daha uzun süre)
        self.window.after(500, lambda: self.window.attributes('-topmost', False))
        # Ek güvence: idle sonrası tekrar öne getir
        self.window.after_idle(self._bring_to_front)

        apply_theme(self.window)
        # Ana frame
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Başlık
        title_label = ttk.Label(
            main_frame,
            text=self.lm.tr("online_survey_mgmt", "🌐 Online Anket Yönetimi"),
            font=('Segoe UI', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(0, 10))
        ttk.Button(toolbar, text=f" {self.lm.tr('btn_report_center', 'Rapor Merkezi')}", style='Primary.TButton', command=self.open_report_center_survey).pack(side='left', padx=6)

        # Notebook (sekmeler)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)

        # Sekmeler
        tab_create = ttk.Frame(notebook)
        tab_manage = ttk.Frame(notebook)
        tab_results = ttk.Frame(notebook)
        tab_stakeholders = ttk.Frame(notebook)

        notebook.add(tab_create, text=f" {self.lm.tr('tab_new_survey', 'Yeni Anket')}")
        notebook.add(tab_manage, text=f" {self.lm.tr('tab_surveys', 'Anketler')}")
        notebook.add(tab_results, text=f" {self.lm.tr('tab_results', 'Sonuçlar')}")
        notebook.add(tab_stakeholders, text=f" {self.lm.tr('tab_stakeholders', 'Paydaşlar')}")

        # Sekmele içeriğini doldur
        self._create_create_tab(tab_create)
        self._create_manage_tab(tab_manage)
        self._create_results_tab(tab_results)
        self._create_stakeholders_tab(tab_stakeholders)

    def open_report_center_survey(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.window)
            gui = ReportCenterGUI(win, getattr(self.parent, 'company_id', 1))
            try:
                gui.module_filter_var.set('genel')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for genel: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor Merkezi açılamadı:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def _create_create_tab(self, parent: ttk.Frame) -> None:
        """Yeni anket oluşturma sekmesi"""
        # Scroll frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Temel bilgiler
        info_frame = ttk.LabelFrame(scrollable_frame, text=self.lm.tr("grp_survey_info", "Anket Bilgileri"), padding=15)
        info_frame.pack(fill='x', padx=10, pady=10)

        # Anket adı
        ttk.Label(info_frame, text=self.lm.tr("lbl_survey_name", "Anket Adı:")).grid(row=0, column=0, sticky='w', pady=5)
        self.survey_name_entry = ttk.Entry(info_frame, width=50)
        self.survey_name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        self.survey_name_entry.insert(0, f"{self.lm.tr('default_survey_name', 'Materyalite Anketi')} {datetime.now().year}")

        # Şirket adı
        ttk.Label(info_frame, text=self.lm.tr("lbl_company_name", "Şirket Adı:")).grid(row=1, column=0, sticky='w', pady=5)
        self.company_name_entry = ttk.Entry(info_frame, width=50)
        self.company_name_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        self.company_name_entry.insert(0, "Sustainage")

        # Açıklama
        ttk.Label(info_frame, text=self.lm.tr("lbl_description", "Açıklama:")).grid(row=2, column=0, sticky='nw', pady=5)
        self.description_text = tk.Text(info_frame, width=50, height=3)
        self.description_text.grid(row=2, column=1, pady=5, padx=(10, 0))
        self.description_text.insert('1.0', self.lm.tr("default_survey_desc", "Paydaş görüşlerini almak için oluşturulmuş materyalite anketi."))

        # Süre
        ttk.Label(info_frame, text=self.lm.tr("lbl_duration", "Anket Süresi:")).grid(row=3, column=0, sticky='w', pady=5)
        duration_frame = ttk.Frame(info_frame)
        duration_frame.grid(row=3, column=1, pady=5, padx=(10, 0), sticky='w')
        self.duration_spinbox = ttk.Spinbox(duration_frame, from_=7, to=90, width=10)
        self.duration_spinbox.set(30)
        self.duration_spinbox.pack(side='left')
        ttk.Label(duration_frame, text=self.lm.tr("unit_days", " gün")).pack(side='left', padx=(5, 0))

        # Konular
        topics_frame = ttk.LabelFrame(scrollable_frame, text=self.lm.tr("grp_survey_topics", "Anket Konuları"), padding=15)
        topics_frame.pack(fill='both', expand=True, padx=10, pady=10)

        ttk.Label(
            topics_frame,
            text=self.lm.tr("lbl_select_topics", "Konuları seçin veya manuel ekleyin:"),
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 10))

        # Hızlı seçim butonları
        quick_frame = ttk.Frame(topics_frame)
        quick_frame.pack(fill='x', pady=(0, 10))

        ttk.Button(
            quick_frame,
            text=self.lm.tr("btn_add_gri", "GRI Konuları Ekle"),
            command=self._add_gri_topics
        ).pack(side='left', padx=(0, 5))

        ttk.Button(
            quick_frame,
            text=self.lm.tr("btn_add_esrs", "ESRS Konuları Ekle"),
            command=self._add_esrs_topics
        ).pack(side='left', padx=5)

        ttk.Button(
            quick_frame,
            text=self.lm.tr("btn_add_custom", "Özel Konu Ekle"),
            command=self._add_custom_topic
        ).pack(side='left', padx=5)

        ttk.Button(
            quick_frame,
            text=self.lm.tr("btn_clear_all", "Tümünü Temizle"),
            command=self._clear_topics
        ).pack(side='left', padx=5)

        # Konu listesi
        list_frame = ttk.Frame(topics_frame)
        list_frame.pack(fill='both', expand=True)

        self.topics_tree = ttk.Treeview(
            list_frame,
            columns=('code', 'name', 'category'),
            show='headings',
            height=8
        )
        self.topics_tree.heading('code', text=self.lm.tr("col_code", "Kod"))
        self.topics_tree.heading('name', text=self.lm.tr("col_topic_name", "Konu Adı"))
        self.topics_tree.heading('category', text=self.lm.tr("col_category", "Kategori"))

        self.topics_tree.column('code', width=100)
        self.topics_tree.column('name', width=350)
        self.topics_tree.column('category', width=150)

        topics_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.topics_tree.yview)
        self.topics_tree.configure(yscrollcommand=topics_scrollbar.set)

        self.topics_tree.pack(side='left', fill='both', expand=True)
        topics_scrollbar.pack(side='right', fill='y')

        # Butonlar
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(
            button_frame,
            text=f"{Icons.SUCCESS} {self.lm.tr('btn_create_send', 'Anketi Oluştur ve Email Gönder')}",
            command=self._create_and_send_survey,
            style='Accent.TButton'
        ).pack(side='left', padx=(0, 10))

        ttk.Button(
            button_frame,
            text=f"{Icons.SAVE} {self.lm.tr('btn_create_only', 'Sadece Oluştur (Email yok)')}",
            command=self._create_survey_only
        ).pack(side='left')

        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_manage_tab(self, parent: ttk.Frame) -> None:
        """Anket yönetim sekmesi"""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill='x', padx=10, pady=10)

        ttk.Button(
            toolbar,
            text=f"{Icons.LOADING} {self.lm.tr('btn_refresh', 'Yenile')}",
            command=self._refresh_surveys
        ).pack(side='left', padx=(0, 5))

        web_text = self.lm.tr('btn_open_web', "Web'de Aç")
        ttk.Button(
            toolbar,
            text=f"🌐 {web_text}",
            command=self._open_survey_in_browser
        ).pack(side='left', padx=5)

        ttk.Button(
            toolbar,
            text=f"{Icons.EMAIL} {self.lm.tr('btn_send_email', 'Email Gönder')}",
            command=self._send_survey_emails_dialog
        ).pack(side='left', padx=5)

        ttk.Button(
            toolbar,
            text=f"{Icons.PAUSE} {self.lm.tr('btn_pause', 'Duraklat')}",
            command=lambda: self._update_survey_status('closed')
        ).pack(side='left', padx=5)

        ttk.Button(
            toolbar,
            text=f"{Icons.PLAY} {self.lm.tr('btn_activate', 'Aktifleştir')}",
            command=lambda: self._update_survey_status('active')
        ).pack(side='left', padx=5)

        # Anket listesi
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.surveys_tree = ttk.Treeview(
            list_frame,
            columns=('id', 'name', 'company', 'deadline', 'responses', 'status'),
            show='headings',
            height=15
        )

        self.surveys_tree.heading('id', text=self.lm.tr('col_id', 'ID'))
        self.surveys_tree.heading('name', text=self.lm.tr('col_survey_name', 'Anket Adı'))
        self.surveys_tree.heading('company', text=self.lm.tr('col_company', 'Şirket'))
        self.surveys_tree.heading('deadline', text=self.lm.tr('col_deadline', 'Son Tarih'))
        self.surveys_tree.heading('responses', text=self.lm.tr('col_responses', 'Yanıt'))
        self.surveys_tree.heading('status', text=self.lm.tr('col_status', 'Durum'))

        self.surveys_tree.column('id', width=50)
        self.surveys_tree.column('name', width=300)
        self.surveys_tree.column('company', width=150)
        self.surveys_tree.column('deadline', width=100)
        self.surveys_tree.column('responses', width=80)
        self.surveys_tree.column('status', width=100)

        surveys_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.surveys_tree.yview)
        self.surveys_tree.configure(yscrollcommand=surveys_scrollbar.set)

        self.surveys_tree.pack(side='left', fill='both', expand=True)
        surveys_scrollbar.pack(side='right', fill='y')

        # İlk yükleme
        self._refresh_surveys()

    def _create_results_tab(self, parent: ttk.Frame) -> None:
        """Sonuçlar sekmesi"""
        # Anket seçimi
        select_frame = ttk.Frame(parent)
        select_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(select_frame, text=self.lm.tr('lbl_select_survey', "Anket Seçin:")).pack(side='left', padx=(0, 10))
        self.results_survey_combo = ttk.Combobox(select_frame, width=40, state='readonly')
        self.results_survey_combo.pack(side='left', padx=(0, 10))

        ttk.Button(
            select_frame,
            text=f"{Icons.REPORT} {self.lm.tr('btn_show_results', 'Sonuçları Göster')}",
            command=self._show_results
        ).pack(side='left')

        # Sonuçlar frame
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.results_text.pack(fill='both', expand=True)

    def _create_stakeholders_tab(self, parent: ttk.Frame) -> None:
        """Paydaşlar sekmesi"""
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill='x', padx=10, pady=10)

        ttk.Button(
            toolbar,
            text=f"{Icons.ADD} {self.lm.tr('btn_new_stakeholder', 'Yeni Paydaş')}",
            command=self._add_stakeholder_dialog
        ).pack(side='left', padx=(0, 5))

        import_text = self.lm.tr('btn_import_excel', "Excel'den İçe Aktar")
        ttk.Button(
            toolbar,
            text=f"📁 {import_text}",
            command=self._import_stakeholders_from_excel
        ).pack(side='left', padx=5)

        ttk.Button(
            toolbar,
            text=f"{Icons.LOADING} {self.lm.tr('btn_refresh', 'Yenile')}",
            command=self._refresh_stakeholders
        ).pack(side='left', padx=5)

        # Paydaş listesi
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.stakeholders_tree = ttk.Treeview(
            list_frame,
            columns=('name', 'email', 'organization', 'role', 'category'),
            show='headings',
            height=15
        )

        self.stakeholders_tree.heading('name', text=self.lm.tr('col_name', 'Ad Soyad'))
        self.stakeholders_tree.heading('email', text=self.lm.tr('col_email', 'Email'))
        self.stakeholders_tree.heading('organization', text=self.lm.tr('col_organization', 'Kuruluş'))
        self.stakeholders_tree.heading('role', text=self.lm.tr('col_role', 'Görev'))
        self.stakeholders_tree.heading('category', text=self.lm.tr('col_category', 'Kategori'))

        self.stakeholders_tree.column('name', width=150)
        self.stakeholders_tree.column('email', width=200)
        self.stakeholders_tree.column('organization', width=150)
        self.stakeholders_tree.column('role', width=120)
        self.stakeholders_tree.column('category', width=100)

        stakeholders_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.stakeholders_tree.yview)
        self.stakeholders_tree.configure(yscrollcommand=stakeholders_scrollbar.set)

        self.stakeholders_tree.pack(side='left', fill='both', expand=True)
        stakeholders_scrollbar.pack(side='right', fill='y')

        # İlk yükleme
        self._refresh_stakeholders()

    def _add_gri_topics(self) -> None:
        """GRI konularını ekle"""
        gri_topics = [
            {'code': 'GRI_201', 'name': self.lm.tr('gri_201', 'Ekonomik Performans'), 'category': self.lm.tr('cat_economic', 'Ekonomik')},
            {'code': 'GRI_301', 'name': self.lm.tr('gri_301', 'Malzemeler'), 'category': self.lm.tr('cat_environment', 'Çevre')},
            {'code': 'GRI_302', 'name': self.lm.tr('gri_302', 'Enerji'), 'category': self.lm.tr('cat_environment', 'Çevre')},
            {'code': 'GRI_303', 'name': self.lm.tr('gri_303', 'Su ve Atıksu'), 'category': self.lm.tr('cat_environment', 'Çevre')},
            {'code': 'GRI_305', 'name': self.lm.tr('gri_305', 'Emisyonlar'), 'category': self.lm.tr('cat_environment', 'Çevre')},
            {'code': 'GRI_306', 'name': self.lm.tr('gri_306', 'Atık'), 'category': self.lm.tr('cat_environment', 'Çevre')},
            {'code': 'GRI_401', 'name': self.lm.tr('gri_401', 'İstihdam'), 'category': self.lm.tr('cat_social', 'Sosyal')},
            {'code': 'GRI_403', 'name': self.lm.tr('gri_403', 'İş Sağlığı ve Güvenliği'), 'category': self.lm.tr('cat_social', 'Sosyal')},
            {'code': 'GRI_404', 'name': self.lm.tr('gri_404', 'Eğitim ve Öğretim'), 'category': self.lm.tr('cat_social', 'Sosyal')},
            {'code': 'GRI_405', 'name': self.lm.tr('gri_405', 'Çeşitlilik ve Fırsat Eşitliği'), 'category': self.lm.tr('cat_social', 'Sosyal')},
        ]

        for topic in gri_topics:
            self.topics_tree.insert('', 'end', values=(topic['code'], topic['name'], topic['category']))

        messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{len(gri_topics)} {self.lm.tr('msg_gri_added', 'GRI konusu eklendi.')}")
        # Mesaj kutusundan sonra pencereyi tekrar ön yüze getir
        self._bring_to_front()

    def _add_esrs_topics(self) -> None:
        """ESRS konularını ekle"""
        esrs_topics = [
            {'code': 'ESRS_E1', 'name': self.lm.tr('esrs_e1', 'İklim Değişikliği'), 'category': self.lm.tr('cat_environment', 'Çevre')},
            {'code': 'ESRS_E2', 'name': self.lm.tr('esrs_e2', 'Kirlilik'), 'category': self.lm.tr('cat_environment', 'Çevre')},
            {'code': 'ESRS_E3', 'name': self.lm.tr('esrs_e3', 'Su ve Deniz Kaynakları'), 'category': self.lm.tr('cat_environment', 'Çevre')},
            {'code': 'ESRS_E4', 'name': self.lm.tr('esrs_e4', 'Biyoçeşitlilik ve Ekosistemler'), 'category': self.lm.tr('cat_environment', 'Çevre')},
            {'code': 'ESRS_S1', 'name': self.lm.tr('esrs_s1', 'Kendi İş Gücü'), 'category': self.lm.tr('cat_social', 'Sosyal')},
            {'code': 'ESRS_S2', 'name': self.lm.tr('esrs_s2', 'Değer Zincirindeki Çalışanlar'), 'category': self.lm.tr('cat_social', 'Sosyal')},
            {'code': 'ESRS_S3', 'name': self.lm.tr('esrs_s3', 'Etkilenen Topluluklar'), 'category': self.lm.tr('cat_social', 'Sosyal')},
            {'code': 'ESRS_S4', 'name': self.lm.tr('esrs_s4', 'Tüketiciler ve Son Kullanıcılar'), 'category': self.lm.tr('cat_social', 'Sosyal')},
            {'code': 'ESRS_G1', 'name': self.lm.tr('esrs_g1', 'İş Davranışı'), 'category': self.lm.tr('cat_governance', 'Yönetişim')},
        ]

        for topic in esrs_topics:
            self.topics_tree.insert('', 'end', values=(topic['code'], topic['name'], topic['category']))

        messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{len(esrs_topics)} {self.lm.tr('msg_esrs_added', 'ESRS konusu eklendi.')}")
        # Mesaj kutusundan sonra pencereyi tekrar ön yüze getir
        self._bring_to_front()

    def _add_custom_topic(self) -> None:
        """Özel konu ekle"""
        dialog = tk.Toplevel(self.window)
        dialog.title(self.lm.tr("title_add_custom_topic", "Özel Konu Ekle"))
        dialog.geometry("500x250")

        # Pencereyi öne çıkar
        dialog.transient(self.window)  # Ana pencereye bağlı
        dialog.grab_set()  # Modal yap
        dialog.lift()
        dialog.focus_force()

        # Form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        ttk.Label(form_frame, text=self.lm.tr("lbl_topic_code", "Konu Kodu:")).grid(row=0, column=0, sticky='w', pady=5)
        code_entry = ttk.Entry(form_frame, width=40)
        code_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(form_frame, text=self.lm.tr("lbl_topic_name", "Konu Adı:")).grid(row=1, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(form_frame, text=self.lm.tr("lbl_category", "Kategori:")).grid(row=2, column=0, sticky='w', pady=5)
        category_entry = ttk.Entry(form_frame, width=40)
        category_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        category_entry.insert(0, self.lm.tr("cat_custom", "Özel"))

        def add_topic():
            code = code_entry.get().strip()
            name = name_entry.get().strip()
            category = category_entry.get().strip()

            if not code or not name:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_code_name_required", "Kod ve ad alanları zorunludur."))
                return

            self.topics_tree.insert('', 'end', values=(code, name, category))
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("msg_topic_added", "Konu eklendi."))
            dialog.destroy()
            # Dialog kapandıktan sonra ana pencereyi öne getir
            self._bring_to_front()

        ttk.Button(form_frame, text=self.lm.tr("btn_add", "Ekle"), command=add_topic).grid(row=3, column=1, pady=20, sticky='e')

    def _clear_topics(self) -> None:
        """Tüm konuları temizle"""
        if messagebox.askyesno(self.lm.tr("confirmation", "Onay"), self.lm.tr("msg_clear_all_confirm", "Tüm konular silinecek. Emin misiniz?")):
            for item in self.topics_tree.get_children():
                self.topics_tree.delete(item)

    def _create_and_send_survey(self) -> None:
        """Anket oluştur ve email gönder"""
        # Anket oluştur
        result = self._create_survey_only()

        if result and result.get('success'):
            # Email gönderme dialogunu aç
            self._send_survey_emails_dialog(survey_url=result['survey_url'])

    def _create_survey_only(self) -> Optional[Dict]:
        """Sadece anket oluştur (email yok)"""
        # Form verilerini al
        survey_name = self.survey_name_entry.get().strip()
        company_name = self.company_name_entry.get().strip()
        description = self.description_text.get('1.0', 'end').strip()
        deadline_days = int(self.duration_spinbox.get())

        # Validation
        if not survey_name or not company_name:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_survey_name_required", "Anket adı ve şirket adı zorunludur."))
            return None

        # Konuları al
        topics = []
        for item in self.topics_tree.get_children():
            values = self.topics_tree.item(item, 'values')
            topics.append({
                'code': values[0],
                'name': values[1],
                'category': values[2]
            })

        # DEBUG: Konuları yazdır
        logging.debug(f"[DEBUG] Toplanan topics sayısı: {len(topics)}")
        if topics:
            logging.debug(f"[DEBUG] İlk topic: {topics[0]}")

        if not topics:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_at_least_one_topic", "En az bir konu ekleyin."))
            return None

        # Anketi oluştur
        try:
            result = self.manager.create_survey(
                survey_name=survey_name,
                company_name=company_name,
                topics=topics,
                description=description,
                deadline_days=deadline_days
            )

            if result.get('success'):
                messagebox.showinfo(
                    self.lm.tr("success", "Başarılı"),
                    f"{self.lm.tr('msg_survey_created', 'Anket başarıyla oluşturuldu!')}\n\n"
                    f"{self.lm.tr('lbl_survey_url', 'Anket URL')}:\n{result['survey_url']}\n\n"
                    f"{self.lm.tr('msg_total_topics', 'Toplam {} konu eklendi.').format(len(topics))}"
                )

                # Anket listesini yenile
                self._refresh_surveys()

                return result
            else:
                messagebox.showerror(
                    self.lm.tr("error", "Hata"),
                    f"{self.lm.tr('msg_create_failed', 'Anket oluşturulamadı')}:\n{result.get('error', 'Bilinmeyen hata')}"
                )
                return None

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('msg_unexpected_error', 'Beklenmeyen hata')}:\n{str(e)}")
            return None

    def _refresh_surveys(self) -> None:
        """Anket listesini yenile"""
        # Tabloyu temizle
        for item in self.surveys_tree.get_children():
            self.surveys_tree.delete(item)

        # Lokal anketleri yükle
        surveys = self.manager.get_local_surveys()

        for survey in surveys:
            self.surveys_tree.insert('', 'end', values=(
                survey['hosting_survey_id'],
                survey['survey_name'],
                survey['company_name'],
                survey['deadline_date'],
                survey['response_count'],
                survey['status']
            ))

        # Combo için güncelle
        survey_names = [f"{s['hosting_survey_id']} - {s['survey_name']}" for s in surveys]
        if hasattr(self, 'results_survey_combo'):
            self.results_survey_combo['values'] = survey_names

    def _refresh_stakeholders(self) -> None:
        """Paydaş listesini yenile"""
        for item in self.stakeholders_tree.get_children():
            self.stakeholders_tree.delete(item)

        stakeholders = self.manager.get_stakeholders()

        for stakeholder in stakeholders:
            self.stakeholders_tree.insert('', 'end', values=(
                stakeholder['name'],
                stakeholder['email'],
                stakeholder['organization'],
                stakeholder['role'],
                stakeholder['category']
            ))

    def _open_survey_in_browser(self) -> None:
        """Seçili anketi tarayıcıda aç"""
        selected = self.surveys_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_survey_warning", "Lütfen bir anket seçin."))
            return

        survey_id = self.surveys_tree.item(selected[0], 'values')[0]

        # URL'i bul
        surveys = self.manager.get_local_surveys()
        survey = next((s for s in surveys if s['hosting_survey_id'] == int(survey_id)), None)

        if survey:
            webbrowser.open(survey['survey_url'])
        else:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_survey_url_not_found", "Anket URL'i bulunamadı."))

    def _send_survey_emails_dialog(self, survey_url: Optional[str] = None) -> None:
        """Email gönderme dialogu"""
        if not survey_url:
            selected = self.surveys_tree.selection()
            if not selected:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_survey_warning", "Lütfen bir anket seçin."))
                return

            survey_id = self.surveys_tree.item(selected[0], 'values')[0]
            surveys = self.manager.get_local_surveys()
            survey = next((s for s in surveys if s['hosting_survey_id'] == int(survey_id)), None)

            if not survey:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_survey_not_found", "Anket bulunamadı."))
                return

            survey_url = survey['survey_url']

        # Paydaş seçimi dialogu
        dialog = tk.Toplevel(self.window)
        dialog.title(self.lm.tr("title_send_email", "Email Gönder"))
        dialog.geometry("600x400")

        # Pencereyi öne çıkar
        dialog.transient(self.window)
        dialog.grab_set()
        dialog.lift()
        dialog.focus_force()

        ttk.Label(dialog, text=self.lm.tr("lbl_select_stakeholders", "Paydaşları Seçin:"), font=('Segoe UI', 11, 'bold')).pack(pady=10)

        # Paydaş listesi (checkbox)
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        stakeholder_vars = []
        stakeholders = self.manager.get_stakeholders()

        for stakeholder in stakeholders:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(
                list_frame,
                text=f"{stakeholder['name']} ({stakeholder['email']})",
                variable=var
            )
            cb.pack(anchor='w', pady=2)
            stakeholder_vars.append((var, stakeholder))

        def send_emails():
            selected_emails = [s['email'] for v, s in stakeholder_vars if v.get()]

            if not selected_emails:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_stakeholder_warning", "En az bir paydaş seçin."))
                return

            # Email gönder
            success_count, fail_count, last_error = self.manager.send_survey_emails(
                survey_url=survey_url,
                stakeholder_emails=selected_emails
            )

            if fail_count > 0 and last_error:
                messagebox.showwarning(
                    self.lm.tr("warning", "Uyarı"),
                    self.lm.tr("err_email_send_partial", f"Email gönderimi tamamlandı ancak hatalar var:\n\n{Icons.PASS} Başarılı: {{}}\n{Icons.REJECT} Başarısız: {{}}\n\nSon hata: {{}}").format(success_count, fail_count, last_error)
                )
            else:
                messagebox.showinfo(
                    self.lm.tr("success", "Başarılı"),
                    self.lm.tr("msg_email_send_complete", f"Email gönderimi tamamlandı:\n\n{Icons.PASS} Başarılı: {{}}\n{Icons.REJECT} Başarısız: {{}}").format(success_count, fail_count)
                )

            dialog.destroy()

        ttk.Button(dialog, text=f"{Icons.EMAIL} {self.lm.tr('btn_send_email_action', 'Email Gönder')}", command=send_emails).pack(pady=10)

    def _update_survey_status(self, status: str) -> None:
        """Anket durumunu güncelle"""
        selected = self.surveys_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_survey", "Lütfen bir anket seçin."))
            return

        survey_id = int(self.surveys_tree.item(selected[0], 'values')[0])

        result = self.manager.update_status(survey_id, status)

        if result.get('success'):
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), f"{self.lm.tr('msg_status_updated', 'Anket durumu güncellendi')}: '{status}'")
            self._refresh_surveys()
        else:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('msg_update_failed', 'Güncelleme başarısız')}: {result.get('error')}")

    def _show_results(self) -> None:
        """Anket sonuçlarını göster"""
        selected = self.results_survey_combo.get()
        if not selected:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_select_survey", "Lütfen bir anket seçin."))
            return

        survey_id = int(selected.split(' - ')[0])

        # Özet istatistikleri al
        result = self.manager.get_summary(survey_id)

        if not result.get('success'):
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('msg_results_failed', 'Sonuçlar alınamadı')}: {result.get('error')}")
            return

        # Sonuçları göster
        self.results_text.delete('1.0', 'end')

        self.results_text.insert('end', f"{'='*80}\n")
        self.results_text.insert('end', f"{self.lm.tr('title_survey_results', 'ANKET SONUÇLARI')} - #{survey_id}\n")
        self.results_text.insert('end', f"{'='*80}\n\n")

        self.results_text.insert('end', f"{self.lm.tr('lbl_total_stakeholders', 'Toplam Paydaş')}: {result['total_stakeholders']}\n")
        self.results_text.insert('end', f"{self.lm.tr('lbl_total_topics', 'Toplam Konu')}: {result['total_topics']}\n\n")

        self.results_text.insert('end', f"{self.lm.tr('col_topic', 'Konu'):<40} {self.lm.tr('col_importance', 'Önem'):<10} {self.lm.tr('col_impact', 'Etki'):<10} {self.lm.tr('col_materiality', 'Materyalite'):<12}\n")
        self.results_text.insert('end', f"{'-'*80}\n")

        for item in result['summary']:
            self.results_text.insert(
                'end',
                f"{item['topic_name'][:38]:<40} "
                f"{item['avg_importance']:<10.2f} "
                f"{item['avg_impact']:<10.2f} "
                f"{item['materiality_score']:<12.2f}\n"
            )

    def _add_stakeholder_dialog(self) -> None:
        """Yeni paydaş ekleme dialogu"""
        dialog = tk.Toplevel(self.window)
        dialog.title(self.lm.tr("title_add_stakeholder", "Yeni Paydaş Ekle"))
        dialog.geometry("500x300")

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        ttk.Label(form_frame, text=self.lm.tr("lbl_name", "Ad Soyad:")).grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(form_frame, text=self.lm.tr("lbl_email", "Email:")).grid(row=1, column=0, sticky='w', pady=5)
        email_entry = ttk.Entry(form_frame, width=40)
        email_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(form_frame, text=self.lm.tr("lbl_organization", "Kuruluş:")).grid(row=2, column=0, sticky='w', pady=5)
        org_entry = ttk.Entry(form_frame, width=40)
        org_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Label(form_frame, text=self.lm.tr("lbl_role", "Görev:")).grid(row=3, column=0, sticky='w', pady=5)
        role_entry = ttk.Entry(form_frame, width=40)
        role_entry.grid(row=3, column=1, pady=5, padx=(10, 0))

        ttk.Label(form_frame, text=self.lm.tr("lbl_category", "Kategori:")).grid(row=4, column=0, sticky='w', pady=5)
        category_combo = ttk.Combobox(form_frame, width=37, values=[
            self.lm.tr("cat_employee", "Çalışan"),
            self.lm.tr("cat_customer", "Müşteri"),
            self.lm.tr("cat_supplier", "Tedarikçi"),
            self.lm.tr("cat_investor", "Yatırımcı"),
            self.lm.tr("cat_ngo", "STK"),
            self.lm.tr("cat_other", "Diğer")
        ])
        category_combo.grid(row=4, column=1, pady=5, padx=(10, 0))

        def add():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            org = org_entry.get().strip()
            role = role_entry.get().strip()
            category = category_combo.get().strip()

            if not name or not email:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("msg_name_email_required", "Ad ve email alanları zorunludur."))
                return

            if self.manager.add_stakeholder(name, email, org, role, category):
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("msg_stakeholder_added", "Paydaş eklendi."))
                self._refresh_stakeholders()
                dialog.destroy()
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("msg_stakeholder_failed", "Paydaş eklenemedi. Email zaten kayıtlı olabilir."))

        ttk.Button(form_frame, text=self.lm.tr("btn_add", "Ekle"), style='Primary.TButton', command=add).grid(row=5, column=1, pady=20, sticky='e')

    def _import_stakeholders_from_excel(self) -> None:
        """Excel'den paydaş içe aktar"""
        filepath = filedialog.askopenfilename(
            title=self.lm.tr("title_select_excel", "Excel Dosyası Seç"),
            filetypes=[(self.lm.tr("file_excel", "Excel Dosyası"), "*.xlsx"), (self.lm.tr("file_all", "Tüm Dosyalar"), "*.*")]
        )

        if not filepath:
            return

        try:
            import openpyxl

            wb = openpyxl.load_workbook(filepath)
            ws = wb.active

            # Başlık satırını atla, verilerden başla
            imported = 0
            failed = 0

            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row or not row[0]:  # Boş satır
                    continue

                try:
                    name = str(row[0]) if row[0] else ""
                    email = str(row[1]) if len(row) > 1 and row[1] else ""
                    organization = str(row[2]) if len(row) > 2 and row[2] else ""
                    role = str(row[3]) if len(row) > 3 and row[3] else ""
                    category = str(row[4]) if len(row) > 4 and row[4] else "Diğer"

                    if name and email:
                        if self.manager.add_stakeholder(name, email, organization, role, category):
                            imported += 1
                        else:
                            failed += 1
                    else:
                        failed += 1

                except Exception:
                    failed += 1
                    continue

            wb.close()

            # Listeyi yenile
            self._refresh_stakeholders()

            # Sonuç mesajı
            message = f"{self.lm.tr('msg_import_complete', 'İçe aktarma tamamlandı!')}\n\n"
            message += f"{Icons.SUCCESS} {self.lm.tr('lbl_success', 'Başarılı')}: {imported} {self.lm.tr('lbl_stakeholder', 'paydaş')}\n"
            if failed > 0:
                message += f"{Icons.FAIL} {self.lm.tr('lbl_fail', 'Başarısız')}: {failed} {self.lm.tr('lbl_stakeholder', 'paydaş')}"

            messagebox.showinfo(self.lm.tr("title_import_result", "İçe Aktarma Sonucu"), message)

        except ImportError:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("err_openpyxl_missing", "openpyxl kütüphanesi bulunamadı!\n\nKurulum: pip install openpyxl"))
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('msg_excel_error', 'Excel dosyası okunamadı')}:\n{str(e)}")


# Test fonksiyonu
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    app = SurveyManagementGUI(root)
    app.show()

    root.mainloop()

