import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, ttk

from utils.ui_theme import apply_theme

from .ai_manager import AIManager
from utils.language_manager import LanguageManager


class AIModuleGUI:
    """AI Modulu kullanici arayuzu"""

    def __init__(self, parent, company_id: int = 1):
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id

        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.base_dir = base_dir
        self.db_path = os.path.join(base_dir, "data", "sdg_desktop.sqlite")

        self.manager = AIManager(self.db_path)

        # Tema
        self.theme = {
            'primary': '#2E8B57',
            'secondary': '#4169E1',
            'success': '#32CD32',
            'warning': '#FFA500',
            'danger': '#DC143C',
            'bg_light': '#F0F0F0',
            'white': '#FFFFFF',
            'text_dark': '#333333'
        }

        self.setup_ui()

    def setup_ui(self):
        """Ana UI olustur"""
        apply_theme(self.parent)
        main_frame = ttk.Frame(self.parent, style='Content.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Baslik
        title_frame = ttk.Frame(main_frame, style='Toolbar.TFrame')
        title_frame.pack(fill='x')

        ttk.Label(title_frame, text=" AI Modulu - Yapay Zeka Destekli Analiz", style='Header.TLabel').pack(side='left', padx=12)

        # Durum gostergesi
        status_text = "Aktif" if self.manager.is_available() else "Pasif"
        self.theme['success'] if self.manager.is_available() else self.theme['danger']

        status_label = ttk.Label(title_frame, text=f"Durum: {status_text}")
        status_label.pack(side='right', padx=12)

        if not self.manager.is_available():
            warning_label = ttk.Label(
                title_frame,
                text="(OpenAI API key gerekli - .env dosyasina ekleyin)",
                font=('Segoe UI', 9),
                foreground=self.theme['warning']
            )
            warning_label.pack(side='right', padx=(0, 10))

        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(10, 10))
        ttk.Button(toolbar, text=self.lm.tr("btn_report_center", "Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center).pack(side='left', padx=6)
        ttk.Button(toolbar, text=self.lm.tr("btn_refresh", "Yenile"), style='Primary.TButton', command=self.refresh_view).pack(side='left', padx=6)
        ttk.Label(toolbar, text="Yıl:").pack(side='left', padx=(10,0))
        self.period_var = tk.StringVar(value=datetime.now().strftime('%Y'))
        years = [str(y) for y in range(datetime.now().year - 5, datetime.now().year + 1)]
        period_combo = ttk.Combobox(toolbar, textvariable=self.period_var, values=years, width=8, state='readonly')
        period_combo.pack(side='left', padx=6)
        def _validate_year(y: str):
            try:
                y = (y or '').strip()
                return y.isdigit() and len(y) == 4 and 1990 <= int(y) <= 2100
            except Exception:
                return False
        def _on_period_change(*args):
            if not _validate_year(self.period_var.get()):
                messagebox.showwarning('Uyarı', 'Geçerli bir yıl seçin (1990-2100)')
                return
            try:
                self.refresh_view()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        try:
            self.period_var.trace_add('write', _on_period_change)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(0, 20))

        ttk.Button(
            btn_frame,
            text="Veri Ozetleme",
            style='Primary.TButton',
            command=self.show_summary_tool
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text="Performans Analizi",
            style='Primary.TButton',
            command=self.show_analysis_tool
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text="Akilli Oneriler",
            style='Primary.TButton',
            command=self.show_recommendations_tool
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text="API Ayarlari",
            style='Primary.TButton',
            command=self.show_api_settings
        ).pack(side='left', padx=5)

        # Icerik alani
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill='both', expand=True)

        # Baslangic mesaji
        self.show_welcome()

    def clear_content(self):
        """Icerik alanini temizle"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        """Hosgeldin mesaji"""
        self.clear_content()

        welcome_text = """
AI MODULU HOSGELDINIZ

Bu modul, yapay zeka destekli analiz ve raporlama yetenekleri sunar:

1. VERI OZETLEME
   - SDG, GRI, TSRS verilerinizi ozetleyin
   - Hizli ve anlasilir raporlar olusturun

2. PERFORMANS ANALIZI
   - Metriklerinizi analiz edin
   - Guclu ve zayif yonleri belirleyin
   - Iyilestirme onerileri alin

3. AKILLI ONERILER
   - Surdurulebilirlik hedefleriniz icin oneriler
   - En iyi uygulamalar
   - Sektore ozel tavsieler

KULLANIM:
- OpenAI API key gereklidir (.env dosyasina ekleyin)
- Ust taraftaki butonlardan istediginiz araci secin
- Sonuclar otomatik olarak kaydedilir

NOTLAR:
- AI sonuclari tavsiye niteligindedir
- Her zaman uzman gorusu alinmalidir
- Veri guvenligi sizin sorumlulugunuzdadir
"""

        text_widget = scrolledtext.ScrolledText(
            self.content_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=20
        )
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', welcome_text)
        text_widget.config(state='disabled')

    def show_summary_tool(self):
        """Veri ozetleme araci"""
        self.clear_content()

        ttk.Label(
            self.content_frame,
            text="Veri Ozetleme Araci",
            font=('Segoe UI', 14, 'bold')
        ).pack(pady=(0, 10))

        # Rapor tipi secimi
        type_frame = ttk.LabelFrame(self.content_frame, text="Rapor Tipi")
        type_frame.pack(fill='x', pady=(0, 10))

        self.report_type_var = tk.StringVar(value="genel")

        ttk.Radiobutton(
            type_frame,
            text="Genel Ozet",
            variable=self.report_type_var,
            value="genel"
        ).pack(anchor='w', padx=10, pady=5)

        ttk.Radiobutton(
            type_frame,
            text="SDG Raporu",
            variable=self.report_type_var,
            value="sdg"
        ).pack(anchor='w', padx=10, pady=5)

        ttk.Radiobutton(
            type_frame,
            text="GRI Raporu",
            variable=self.report_type_var,
            value="gri"
        ).pack(anchor='w', padx=10, pady=5)

        ttk.Radiobutton(
            type_frame,
            text="Birlesik Rapor (KPI Snapshot)",
            variable=self.report_type_var,
            value="unified"
        ).pack(anchor='w', padx=10, pady=5)

        # Veri girisi
        data_frame = ttk.LabelFrame(self.content_frame, text="Veri (JSON formatinda)")
        data_frame.pack(fill='both', expand=True, pady=(0, 10))

        self.data_text = scrolledtext.ScrolledText(
            data_frame,
            wrap=tk.WORD,
            height=8,
            font=('Consolas', 9)
        )
        self.data_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Sonuc alani
        result_frame = ttk.LabelFrame(self.content_frame, text="AI Ozet")
        result_frame.pack(fill='both', expand=True, pady=(0, 10))

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            height=8,
            font=('Segoe UI', 10)
        )
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(fill='x')

        ttk.Button(
            btn_frame,
            text="Snapshot Yukle",
            style='Primary.TButton',
            command=self.load_snapshot
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text="Ozetle",
            style='Primary.TButton',
            command=self.generate_summary
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text=self.lm.tr("btn_save", "Kaydet"),
            style='Primary.TButton',
            command=self.save_summary
        ).pack(side='left', padx=5)

        ttk.Button(
            btn_frame,
            text="Temizle",
            style='Primary.TButton',
            command=lambda: self.result_text.delete('1.0', tk.END)
        ).pack(side='left', padx=5)

    def load_snapshot(self):
        import json
        import os

        try:
            snapshot_dir = os.path.join(self.base_dir, "ai_snapshots")
            initial_dir = snapshot_dir if os.path.isdir(snapshot_dir) else self.base_dir
            file_path = filedialog.askopenfilename(
                title="AI Snapshot dosyasi sec",
                initialdir=initial_dir,
                filetypes=[("JSON Dosyalari", "*.json"), ("Tum Dosyalar", "*.*")],
            )
            if not file_path:
                return
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()
            try:
                snapshot = json.loads(raw)
            except Exception:
                self.data_text.delete('1.0', tk.END)
                self.data_text.insert('1.0', raw)
                self.report_type_var.set("genel")
                return
            company = snapshot.get("company") or {}
            period = snapshot.get("period") or {}
            context = {
                "company_id": company.get("id") or self.company_id,
                "reporting_period": period.get("label") or period.get("year"),
                "modules": [],
                "module_reports": [],
                "metrics": {},
                "kpi_snapshot": snapshot,
                "kpis": snapshot.get("kpis") or [],
                "alignments": snapshot.get("alignments") or {},
            }
            text = json.dumps(context, ensure_ascii=False, indent=2)
            self.data_text.delete('1.0', tk.END)
            self.data_text.insert('1.0', text)
            if hasattr(self, "result_text"):
                self.result_text.delete('1.0', tk.END)
            self.report_type_var.set("unified")
        except Exception as e:
            messagebox.showerror("Hata", f"Snapshot dosyasi yuklenemedi:\n{e}")

    def generate_summary(self):
        """Ozet olustur"""
        if not self.manager.is_available():
            messagebox.showwarning(
                "AI Kullanılamıyor",
                "AI ozellikleri kullanilabilir degil.\nLutfen OpenAI API key ekleyin (.env dosyasina)."
            )
            return

        # Veriyi al
        data_json = self.data_text.get('1.0', tk.END).strip()

        if not data_json:
            messagebox.showwarning("Uyari", "Lutfen veri girin!")
            return

        # JSON parse et
        try:
            import json
            data = json.loads(data_json)
        except json.JSONDecodeError as e:
            messagebox.showerror("Hata", f"Gecersiz JSON format:\n{e}")
            return

        # Loading mesaji
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', "AI analiz ediyor, lutfen bekleyin...\n\n")
        self.result_text.update()

        # AI cagrisi
        report_type = self.report_type_var.get()
        summary = self.manager.generate_summary(data, report_type)

        # Sonucu goster
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', summary)

    def save_summary(self):
        """Ozeti kaydet"""
        content = self.result_text.get('1.0', tk.END).strip()

        if not content:
            messagebox.showwarning("Uyari", "Kaydedilecek icerik yok!")
            return

        if self.manager.save_report(content, "ai_ozet"):
            messagebox.showinfo("Basarili", "AI ozet kaydedildi!")
        else:
            messagebox.showerror("Hata", "Ozet kaydedilemedi!")

    def show_analysis_tool(self):
        """Performans analizi araci"""
        self.clear_content()

        ttk.Label(
            self.content_frame,
            text="Performans Analizi (Yakinda...)",
            font=('Segoe UI', 14, 'bold')
        ).pack(pady=20)

    def show_recommendations_tool(self):
        """Akilli oneriler araci"""
        self.clear_content()

        ttk.Label(
            self.content_frame,
            text="Akilli Oneriler (Yakinda...)",
            font=('Segoe UI', 14, 'bold')
        ).pack(pady=20)

    def show_api_settings(self):
        """API ayarlari"""
        self.clear_content()

        ttk.Label(
            self.content_frame,
            text="OpenAI API Ayarlari",
            font=('Segoe UI', 14, 'bold')
        ).pack(pady=(0, 20))

        info_text = """
OPENAI API KEY NASIL EKLENIR?

1. .env dosyasini acin (proje ana dizininde)
2. Asagidaki satiri ekleyin:
   OPENAI_API_KEY=your-api-key-here
3. 'your-api-key-here' yerine gercek API key'inizi yazin
4. Dosyayi kaydedin
5. Programi yeniden baslatın

API KEY NASIL ALINIR?

1. https://platform.openai.com adresine gidin
2. Hesap olusturun veya giris yapin
3. API Keys bolumune gidin
4. "Create new secret key" butonuna tiklayin
5. Key'i kopyalayin ve yukardaki adımlari takip edin

NOT: API kullanimi ucretlidir. OpenAI fiyatlandirmasi icin:
https://openai.com/pricing

GUCLU NOT: API key'inizi kimseyle paylasmayin!
"""

        text_widget = scrolledtext.ScrolledText(
            self.content_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            height=20
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')

    def open_report_center(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('ai')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for ai: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor Merkezi açılamadı:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def refresh_view(self) -> None:
        try:
            _ = self.period_var.get()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

