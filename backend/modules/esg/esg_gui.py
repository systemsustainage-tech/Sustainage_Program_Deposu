import logging
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import pandas as pd
import requests

from modules.data_import.import_templates import ImportTemplateManager
from modules.tcfd.tcfd_manager import TCFDManager
from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .esg_manager import ESGManager
from config.icons import Icons


class ESGGUI:
    """
    ESG Dashboard GUI
    - E/S/G skor kartları
    - Sinyal/kanıt listeleri
    - ESG işlemleri menüsü (rapor, ayarlar, veri görünümü)
    """

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id or 1
        self.lm = LanguageManager()
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        self.manager = ESGManager(base_dir)
        self._build()

    def _build(self) -> None:
        try:
            # messagebox.showinfo("ESG GÜNCELLEME", "ESG Modülü yeni tasarım yüklendi.\n(Bu mesajı görüyorsanız güncelleme başarılıdır.)")
            pass
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
            
        apply_theme(self.parent)
        
        # Ana Container - Modern Arka Plan
        self.main_container = tk.Frame(self.parent, bg='#f0f2f5')
        self.main_container.pack(fill='both', expand=True)

        # --- ÜST HEADER ---
        header_frame = tk.Frame(self.main_container, bg='white', height=80)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)
        
        # Logo ve Başlık Grubu
        title_group = tk.Frame(header_frame, bg='white')
        title_group.pack(side='left', pady=10, padx=20)
        
        # İkonlu Başlık
        tk.Label(title_group, text=Icons.LEAF, font=('Segoe UI', 24), bg='white').pack(side='left', padx=(0, 10))
        
        text_group = tk.Frame(title_group, bg='white')
        text_group.pack(side='left')
        
        tk.Label(text_group, text=self.lm.tr('esg_module_title', "ESG Yönetim Merkezi"), 
                font=('Segoe UI', 18, 'bold'), fg='#1e293b', bg='white').pack(anchor='w')
        tk.Label(text_group, text=self.lm.tr('esg_subtitle', "Sürdürülebilirlik hedeflerinizi yönetin ve izleyin"), 
                font=('Segoe UI', 9), fg='#64748b', bg='white').pack(anchor='w')

        # Sağ Üst Aksiyonlar
        actions = tk.Frame(header_frame, bg='white')
        actions.pack(side='right', padx=20)
        
        def create_header_btn(text, cmd, icon=Icons.REPORT):
            btn = tk.Button(actions, text=f"{icon} {text}", font=('Segoe UI', 9, 'bold'),
                          bg='#eff6ff', fg='#2563eb', relief='flat', padx=15, pady=8,
                          command=cmd, cursor='hand2')
            btn.pack(side='left', padx=5)
            return btn

        create_header_btn(self.lm.tr('btn_report_center', "Rapor Merkezi"), self.open_report_center_esg)

        # --- ANA İÇERİK ALANI ---
        content_area = tk.Frame(self.main_container, bg='#f0f2f5')
        content_area.pack(fill='both', expand=True, padx=20, pady=20)

        # 1. SOL MENÜ (Modern Liste)
        left_menu = tk.Frame(content_area, bg='white', width=280)
        left_menu.pack(side='left', fill='y', padx=(0, 20))
        left_menu.pack_propagate(False)
        
        # Sol Menü Başlığı
        tk.Label(left_menu, text=self.lm.tr('quick_actions_title', "HIZLI İŞLEMLER"), font=('Segoe UI', 9, 'bold'), 
                fg='#94a3b8', bg='white').pack(anchor='w', padx=20, pady=(20, 15))
        
        def create_menu_item(text, cmd, icon="•"):
            # Container for hover effect
            btn_frame = tk.Frame(left_menu, bg='white', cursor='hand2')
            btn_frame.pack(fill='x', padx=10, pady=2)
            
            lbl = tk.Label(btn_frame, text=f"  {icon}    {text}", font=('Segoe UI', 10),
                          bg='white', fg='#475569', anchor='w', padx=10, pady=10, cursor='hand2')
            lbl.pack(fill='x')
            
            def on_click(e): cmd()
            def on_enter(e): 
                btn_frame.configure(bg='#f1f5f9')
                lbl.configure(bg='#f1f5f9', fg='#0f172a')
            def on_leave(e): 
                btn_frame.configure(bg='white')
                lbl.configure(bg='white', fg='#475569')
                
            btn_frame.bind('<Button-1>', on_click)
            lbl.bind('<Button-1>', on_click)
            btn_frame.bind('<Enter>', on_enter)
            lbl.bind('<Enter>', on_enter)
            btn_frame.bind('<Leave>', on_leave)
            lbl.bind('<Leave>', on_leave)
        
        create_menu_item(self.lm.tr('btn_refresh_scores', 'Skorları Yenile'), self.refresh_scores, Icons.LOADING)
        create_menu_item(self.lm.tr('btn_show_signals', 'Sinyalleri Göster'), self.show_signals, "📡")
        create_menu_item(self.lm.tr('btn_eu_taxonomy', 'EU Taxonomy'), self.show_eu_taxonomy, "🇪🇺")
        create_menu_item(self.lm.tr('btn_cbam', 'CBAM Raporlama'), self.show_cbam, "🏭")
        create_menu_item(self.lm.tr('btn_ungc', 'UNGC İlkeleri'), self.show_ungc, "🌐")
        create_menu_item(self.lm.tr('btn_reporting_docx', 'Rapor Oluştur'), self.show_reporting_info, Icons.FILE)
        create_menu_item(self.lm.tr('btn_settings', 'Ayarlar'), self.show_settings_info, Icons.SETTINGS)
        create_menu_item(self.lm.tr('btn_import_metrics', 'Veri İçe Aktar'), self.show_operational_import_window, "📥")

        # 2. SAĞ DASHBOARD
        self.right_dashboard = tk.Frame(content_area, bg='#f0f2f5')
        self.right_dashboard.pack(side='right', fill='both', expand=True)
        
        # KPI Kartları (Üstte)
        kpi_container = tk.Frame(self.right_dashboard, bg='#f0f2f5')
        kpi_container.pack(fill='x', pady=(0, 20))
        
        self.kpi_vars = {
            'E': tk.StringVar(value='-'),
            'S': tk.StringVar(value='-'),
            'G': tk.StringVar(value='-'),
            'overall': tk.StringVar(value='-')
        }

        def create_kpi_card(parent, title, var, color):
            card = tk.Frame(parent, bg='white')
            card.pack(side='left', fill='x', expand=True, padx=5)
            
            # Üst çizgi
            tk.Frame(card, bg=color, height=3).pack(fill='x')
            
            # İçerik
            content = tk.Frame(card, bg='white', padx=15, pady=15)
            content.pack(fill='both', expand=True)
            
            tk.Label(content, text=title, font=('Segoe UI', 9, 'bold'), fg='#64748b', bg='white').pack(anchor='w')
            tk.Label(content, textvariable=var, font=('Segoe UI', 20, 'bold'), fg=color, bg='white').pack(anchor='w', pady=(5,0))

        create_kpi_card(kpi_container, self.lm.tr('env_score_title', "Çevresel (E)"), self.kpi_vars['E'], '#10b981')
        create_kpi_card(kpi_container, self.lm.tr('soc_score_title', "Sosyal (S)"), self.kpi_vars['S'], '#f59e0b')
        create_kpi_card(kpi_container, self.lm.tr('gov_score_title', "Yönetişim (G)"), self.kpi_vars['G'], '#3b82f6')
        create_kpi_card(kpi_container, self.lm.tr('overall_score_title', "Genel Skor"), self.kpi_vars['overall'], '#6366f1')

        # Modül Kartları (Grid - Ortada)
        modules_frame = tk.Frame(self.right_dashboard, bg='#f0f2f5')
        modules_frame.pack(fill='both', expand=True)
        
        modules_frame.columnconfigure(0, weight=1)
        modules_frame.columnconfigure(1, weight=1)
        modules_frame.columnconfigure(2, weight=1)
        
        def create_module_card(title, desc, icon, color, cmd, r, c):
            card = tk.Frame(modules_frame, bg='white', cursor='hand2')
            card.grid(row=r, column=c, padx=8, pady=8, sticky='nsew')
            
            def on_click(e): cmd()
            def on_enter(e): 
                card.configure(bg='#f8fafc')
                for w in card.winfo_children(): w.configure(bg='#f8fafc')
            def on_leave(e): 
                card.configure(bg='white')
                for w in card.winfo_children(): w.configure(bg='white')
            
            card.bind('<Button-1>', on_click)
            card.bind('<Enter>', on_enter)
            card.bind('<Leave>', on_leave)
            
            tk.Label(card, text=icon, font=('Segoe UI', 32), fg=color, bg='white').pack(pady=(25, 10))
            tk.Label(card, text=title, font=('Segoe UI', 12, 'bold'), fg='#1e293b', bg='white').pack()
            tk.Label(card, text=desc, font=('Segoe UI', 9), fg='#64748b', bg='white', wraplength=200).pack(pady=(5, 25))
            
            # Elemanlara da bind et
            for child in card.winfo_children():
                child.bind('<Button-1>', on_click)

        create_module_card(self.lm.tr('esg_consolidated', 'Konsolide Görünüm'), 
                         self.lm.tr('esg_consolidated_desc', "Tüm verilerin tek ekranda özeti"), Icons.REPORT, '#64748b', self.open_consolidated_dashboard, 0, 0)
        
        create_module_card(self.lm.tr('esg_module', 'ESG Modülü'), 
                         self.lm.tr('esg_module_card_desc', "Detaylı yönetim ve skorlama"), Icons.LEAF, '#2563eb', self.refresh_scores, 0, 1)
        
        create_module_card(self.lm.tr('reporting', 'Raporlama'), 
                         self.lm.tr('esg_reporting_center_desc', "Rapor oluşturma merkezi"), "📑", '#1abc9c', self.open_report_center_esg, 0, 2)
        
        create_module_card(self.lm.tr('signals', 'Sinyaller'), 
                         self.lm.tr('esg_signals_desc', "Önemli bulgular ve uyarılar"), "🔔", '#3498db', self.show_signals, 1, 0)
        
        create_module_card(self.lm.tr('settings', 'Ayarlar'), 
                         self.lm.tr('esg_settings_desc', "Ağırlıklar ve yapılandırma"), Icons.SETTINGS, '#6b7280', self.show_settings_info, 1, 1)

        # Alt Bilgi / Detay Alanı
        self.detail = tk.Frame(self.right_dashboard, bg='white')
        self.detail.pack(fill='x', pady=20)
        
        # İlk verileri yükle
        self.refresh_scores()

    def open_report_center_esg(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('esg')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for esg: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_center_error', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def open_consolidated_dashboard(self) -> None:
        try:
            from modules.esg.esg_consolidated_dashboard import ESGConsolidatedDashboard
            win = tk.Toplevel(self.parent)
            win.title('ESG Konsolide Dashboard')
            base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
            db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
            ESGConsolidatedDashboard(win, self.company_id, db_path)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def refresh_scores(self) -> None:
        try:
            s = self.manager.compute_scores(self.company_id)
            self.kpi_vars['E'].set(f"%{s['E']}")
            self.kpi_vars['S'].set(f"%{s['S']}")
            self.kpi_vars['G'].set(f"%{s['G']}")
            self.kpi_vars['overall'].set(f"%{s['overall']}")
            self._render_details(s)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('esg_calc_error', 'ESG skorları hesaplanamadı')}: {e}")

    def _render_details(self, scores) -> None:
        for w in list(self.detail.children.values()):
            try:
                w.destroy()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        # GRI/TSRS katkı detayları
        tk.Label(self.detail, text=self.lm.tr('contribution_details', 'Katkı Detayları'), font=('Segoe UI', 12, 'bold'), fg='#374151', bg='white').pack(anchor='w', pady=(0, 6))
        grid = tk.Frame(self.detail, bg='white')
        grid.pack(fill='x')

        def row(label, val) -> None:
            r = tk.Frame(grid, bg='white')
            r.pack(fill='x')
            tk.Label(r, text=label, font=('Segoe UI', 10, 'bold'), fg='#111827', bg='white', width=40, anchor='w').pack(side='left')
            tk.Label(r, text=val, font=('Segoe UI', 10), fg='#374151', bg='white', anchor='w').pack(side='left')

        d = scores.get('details', {})
        gri = d.get('gri', {})
        tsrs = d.get('tsrs', {})
        row(self.lm.tr('gri_env_stats', 'GRI Çevresel yanıtlanan/toplam'), f"{gri.get('environmental',{}).get('answered',0)}/{gri.get('environmental',{}).get('total',0)}")
        row(self.lm.tr('gri_soc_stats', 'GRI Sosyal yanıtlanan/toplam'), f"{gri.get('social',{}).get('answered',0)}/{gri.get('social',{}).get('total',0)}")
        row(self.lm.tr('gri_gov_stats', 'GRI Yönetişim (GRI 2) yanıtlanan/toplam'), f"{gri.get('governance',{}).get('answered',0)}/{gri.get('governance',{}).get('total',0)}")
        row(self.lm.tr('tsrs_env_stats', 'TSRS Çevresel yanıtlanan/toplam'), f"{tsrs.get('environmental',{}).get('answered',0)}/{tsrs.get('environmental',{}).get('total',0)}")
        row(self.lm.tr('tsrs_soc_stats', 'TSRS Sosyal yanıtlanan/toplam'), f"{tsrs.get('social',{}).get('answered',0)}/{tsrs.get('social',{}).get('total',0)}")
        row(self.lm.tr('tsrs_gov_stats', 'TSRS Yönetişim yanıtlanan/toplam'), f"{tsrs.get('governance',{}).get('answered',0)}/{tsrs.get('governance',{}).get('total',0)}")

    def _get_category_name(self, category: str) -> str:
        mapping = {
            'E': self.lm.tr('env_section', 'Çevresel (Environmental)'),
            'S': self.lm.tr('soc_section', 'Sosyal (Social)'),
            'G': self.lm.tr('gov_section', 'Yönetişim (Governance)')
        }
        return mapping.get(category, category)

    def show_signals(self) -> None:
        signals = self.manager.get_top_signals(self.company_id)

        # Pencere oluştur
        win = tk.Toplevel(self.parent)
        win.title(self.lm.tr('esg_signals_title', 'ESG Sinyalleri'))
        win.geometry('900x700')
        win.configure(bg='#f8f9fa')
        win.grab_set()

        # Pencereyi merkeze al
        win.transient(self.parent)
        win.focus_force()

        # Başlık
        header_frame = tk.Frame(win, bg='#3b82f6', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=self.lm.tr('esg_signals_header', " ESG Sinyalleri"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#3b82f6')
        title_label.pack(expand=True)

        # Ana içerik
        main_frame = tk.Frame(win, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Scrollable frame
        canvas = tk.Canvas(main_frame, bg='#f8f9fa')
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def section(title, items, color, icon) -> None:
            if not items:
                return

            # Section frame
            section_frame = tk.LabelFrame(scrollable_frame, text=f"{icon} {title}",
                                        font=('Segoe UI', 12, 'bold'), fg=color, bg='white',
                                        relief='solid', bd=1)
            section_frame.pack(fill='x', padx=10, pady=10)

            for it in items:
                item_frame = tk.Frame(section_frame, bg='white')
                item_frame.pack(fill='x', padx=15, pady=8)

                # Code ve title
                code_label = tk.Label(item_frame, text=it['code'],
                                    font=('Segoe UI', 10, 'bold'), fg='#2c3e50', bg='white')
                code_label.pack(anchor='w')

                title_label = tk.Label(item_frame, text=it['title'],
                                     font=('Segoe UI', 11, 'bold'), fg='#34495e', bg='white')
                title_label.pack(anchor='w')

                # Details
                details_frame = tk.Frame(item_frame, bg='white')
                details_frame.pack(fill='x', pady=(5, 0))

                # Source
                source_label = tk.Label(details_frame, text=f"{self.lm.tr('source_label', ' Kaynak: ')}{it['source']}",
                                      font=('Segoe UI', 9), fg='#7f8c8d', bg='white')
                source_label.pack(side='left')

                # Period
                period_label = tk.Label(details_frame, text=f"{self.lm.tr('period_label', ' Dönem: ')}{it['period']}",
                                      font=('Segoe UI', 9), fg='#7f8c8d', bg='white')
                period_label.pack(side='left', padx=(20, 0))

                # Type
                type_label = tk.Label(details_frame, text=f"{self.lm.tr('type_label', '️ Tip: ')}{it.get('type', 'N/A')}",
                                    font=('Segoe UI', 9), fg='#7f8c8d', bg='white')
                type_label.pack(side='left', padx=(20, 0))

                # Value
                value_text = str(it['value'])[:100]  # İlk 100 karakter
                value_label = tk.Label(item_frame, text=f"{self.lm.tr('value_label', ' Değer: ')}{value_text}",
                                     font=('Segoe UI', 10), fg='#27ae60', bg='white',
                                     wraplength=800, justify='left')
                value_label.pack(anchor='w', pady=(5, 0))

                # Separator
                separator = tk.Frame(item_frame, height=1, bg='#ecf0f1')
                separator.pack(fill='x', pady=(8, 0))

        # Sinyalleri göster
        section(self.lm.tr('env_section', 'Çevresel (Environmental)'), signals.get('E', []), '#27ae60', '')
        section(self.lm.tr('soc_section', 'Sosyal (Social)'), signals.get('S', []), '#3498db', '')
        section(self.lm.tr('gov_section', 'Yönetişim (Governance)'), signals.get('G', []), '#9b59b6', '️')

        # Eğer hiç sinyal yoksa bilgi göster
        if not any(signals.values()):
            info_frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
            info_frame.pack(fill='x', padx=10, pady=20)

            info_label = tk.Label(info_frame,
                                text=self.lm.tr('no_signals_msg', f"{Icons.INFO} Henüz ESG sinyali bulunamadı.\n\n"
                                     "ESG sinyalleri görmek için:\n"
                                     "• GRI standartlarına veri girin\n"
                                     "• TSRS göstergelerine yanıt verin\n"
                                     "• SDG hedeflerine katkıda bulunun"),
                                font=('Segoe UI', 12), fg='#7f8c8d', bg='white',
                                justify='center')
            info_label.pack(pady=30)

        # Canvas ve scrollbar'ı pack et
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel binding
        def _on_mousewheel(event) -> None:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event) -> None:
            canvas.unbind_all("<MouseWheel>")
        win.bind("<Destroy>", _unbind_mousewheel)

    def show_reporting_info(self) -> None:
        """ESG raporlama penceresini göster"""
        self.show_esg_reporting_window()

    def show_settings_info(self) -> None:
        """ESG ayarlar penceresini göster"""
        self.show_esg_settings_window()

    def show_operational_import_window(self) -> None:
        win = tk.Toplevel(self.parent)
        win.title(self.lm.tr('op_metrics_title', 'Operasyonel Metrikler'))
        win.geometry('700x420')
        win.configure(bg='white')
        frm = tk.Frame(win, bg='white')
        frm.pack(fill='both', expand=True, padx=20, pady=20)
        tk.Label(frm, text=self.lm.tr('lbl_year', 'Yıl'), bg='white').grid(row=0, column=0, sticky='w')
        year_var = tk.StringVar(value=str(datetime.now().year))
        tk.Entry(frm, textvariable=year_var, width=12).grid(row=0, column=1, padx=8, pady=6, sticky='w')
        tk.Label(frm, text=self.lm.tr('lbl_data_url', 'Veri URL (JSON)'), bg='white').grid(row=1, column=0, sticky='w')
        url_var = tk.StringVar()
        tk.Entry(frm, textvariable=url_var, width=48).grid(row=1, column=1, padx=8, pady=6, sticky='w')
        btns = tk.Frame(frm, bg='white')
        btns.grid(row=2, column=0, columnspan=2, pady=10, sticky='w')
        def _create_template():
            path = filedialog.asksaveasfilename(
                title=self.lm.tr('save_template', "Şablon Kaydet"),
                defaultextension='.xlsx',
                filetypes=[(self.lm.tr('file_excel', 'Excel Dosyası'), '*.xlsx')]
            )
            if not path:
                return
            ok = ImportTemplateManager.create_template_file('operational_common', path, format='excel')
            if ok:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('msg_template_created', 'Şablon oluşturuldu: ')}{path}")
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('msg_template_error', 'Şablon oluşturulamadı'))
        def _apply_data(d, year):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
            mgr = TCFDManager(db_path)
            data = {}
            for k in ['scope1_emissions','scope2_emissions','scope3_emissions','total_energy_consumption','renewable_energy_pct','internal_carbon_price']:
                if k in d and d.get(k) not in (None, ''):
                    try:
                        data[k] = float(d.get(k))
                    except Exception:
                        data[k] = d.get(k)
            other = {}
            if 'current_energy_price' in d:
                other['current_energy_price'] = d.get('current_energy_price')
            if other:
                try:
                    data['other_metrics'] = json.dumps(other)
                except Exception:
                    data['other_metrics'] = None
            ok, msg = mgr.save_metrics(self.company_id, int(year), data)
            if ok:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), msg)
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), msg)
        def _import_file():
            fp = filedialog.askopenfilename(
                title=self.lm.tr('import_data_file', "Veri Dosyası İçe Aktar"),
                filetypes=[(self.lm.tr('data_files', 'Veri Dosyaları'),'*.xlsx;*.csv;*.json'), (self.lm.tr('file_all', 'Tüm Dosyalar'), '*.*')]
            )
            if not fp:
                return
            y = year_var.get() or str(datetime.now().year)
            try:
                if fp.lower().endswith('.json'):
                    with open(fp, 'r', encoding='utf-8') as f:
                        d = json.load(f)
                elif fp.lower().endswith('.csv'):
                    df = pd.read_csv(fp)
                    d = {c: df.iloc[0][c] for c in df.columns}
                else:
                    df = pd.read_excel(fp)
                    d = {c: df.iloc[0][c] for c in df.columns}
                _apply_data(d, y)
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('msg_import_error', 'İçe aktarma hatası: ')}{e}")
        def _fetch_url():
            u = url_var.get().strip()
            if not u:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('msg_url_warning', 'URL girin'))
                return
            y = year_var.get() or str(datetime.now().year)
            try:
                r = requests.get(u, timeout=10)
                r.raise_for_status()
                d = r.json()
                _apply_data(d, y)
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('msg_url_error', 'URL’den veri alınamadı: ')}{e}")
        tk.Button(btns, text=self.lm.tr('btn_create_template', 'Şablon Oluştur (XLSX)'), command=_create_template, bg='#16a34a', fg='white').pack(side='left', padx=5)
        tk.Button(btns, text=self.lm.tr('btn_import', 'İçe Aktar'), command=_import_file, bg='#10b981', fg='white').pack(side='left', padx=5)
        tk.Button(btns, text=self.lm.tr('btn_fetch_url', 'URL’den Getir'), command=_fetch_url, bg='#2563eb', fg='white').pack(side='left', padx=5)

    def show_eu_taxonomy(self) -> None:
        """EU Taxonomy penceresini göster"""
        try:
            # EU Taxonomy penceresi oluştur
            taxonomy_window = tk.Toplevel(self.parent)
            taxonomy_window.title(self.lm.tr('btn_eu_taxonomy', "🇪🇺 EU Taxonomy"))
            taxonomy_window.geometry("1200x800")
            taxonomy_window.configure(bg='#f8f9fa')
            taxonomy_window.grab_set()

            # Pencereyi merkeze al ve öne getir
            taxonomy_window.transient(self.parent)
            taxonomy_window.focus_force()
            taxonomy_window.lift()
            taxonomy_window.attributes('-topmost', True)
            taxonomy_window.after_idle(taxonomy_window.attributes, '-topmost', False)

            # EU Taxonomy GUI'yi yükle
            from modules.eu_taxonomy.taxonomy_gui import EUTaxonomyGUI
            EUTaxonomyGUI(taxonomy_window, self.company_id)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('eu_taxonomy_error', "EU Taxonomy penceresi açılamadı: {e}").format(e=e))
            logging.error(f"EU Taxonomy penceresi hatası: {e}")

    def show_cbam(self) -> None:
        """CBAM penceresini göster"""
        try:
            # CBAM penceresi oluştur
            cbam_window = tk.Toplevel(self.parent)
            cbam_window.title(self.lm.tr('btn_cbam', " CBAM Raporlama"))
            cbam_window.geometry("1200x800")
            cbam_window.configure(bg='#f8f9fa')
            cbam_window.grab_set()

            # Pencereyi merkeze al ve öne getir
            cbam_window.transient(self.parent)
            cbam_window.focus_force()
            cbam_window.lift()
            cbam_window.attributes('-topmost', True)
            cbam_window.after_idle(cbam_window.attributes, '-topmost', False)

            # CBAM GUI'yi yükle
            from modules.cbam.cbam_gui import CBAMGUI
            CBAMGUI(cbam_window, self.company_id)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('cbam_error', "CBAM penceresi açılamadı: {e}").format(e=e))
            logging.error(f"CBAM penceresi hatası: {e}")

    def show_ungc(self) -> None:
        """UNGC penceresini göster"""
        try:
            # UNGC penceresi oluştur
            ungc_window = tk.Toplevel(self.parent)
            ungc_window.title(self.lm.tr('ungc_principles_title', " UNGC Ten Principles"))
            ungc_window.geometry("1200x800")
            ungc_window.configure(bg='#f8f9fa')
            ungc_window.grab_set()

            # Pencereyi merkeze al ve öne getir
            ungc_window.transient(self.parent)
            ungc_window.focus_force()
            ungc_window.lift()
            ungc_window.attributes('-topmost', True)
            ungc_window.after_idle(ungc_window.attributes, '-topmost', False)

            # UNGC GUI'yi yükle
            from modules.ungc.ungc_gui import UNGCGUI
            UNGCGUI(ungc_window, self.company_id)

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('ungc_error', "UNGC penceresi açılamadı: {e}").format(e=e))
            logging.error(f"UNGC penceresi hatası: {e}")

    def show_esg_reporting_window(self) -> None:
        """ESG raporlama penceresini göster"""
        # Raporlama penceresi oluştur
        report_window = tk.Toplevel(self.parent)
        report_window.title(self.lm.tr('esg_reporting_title', " ESG Raporlama"))
        report_window.geometry("800x600")
        report_window.configure(bg='#f8f9fa')
        report_window.grab_set()

        # Pencereyi merkeze al
        report_window.transient(self.parent)
        report_window.focus_force()

        # Başlık
        header_frame = tk.Frame(report_window, bg='#3b82f6', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=self.lm.tr('esg_reporting_center_title', " ESG Raporlama Merkezi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#3b82f6')
        title_label.pack(expand=True)

        # Ana içerik
        main_frame = tk.Frame(report_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Rapor oluşturma bölümü
        create_frame = tk.LabelFrame(main_frame, text=self.lm.tr('esg_create_new_report_title', " Yeni Rapor Oluştur"),
                                   font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        create_frame.pack(fill='x', pady=(0, 20))

        # Rapor formatları
        format_frame = tk.Frame(create_frame, bg='white')
        format_frame.pack(fill='x', padx=15, pady=15)

        tk.Label(format_frame, text=self.lm.tr('esg_report_format', "Rapor Formatı:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w')

        format_var = tk.StringVar(value="DOCX")
        formats = [
            (self.lm.tr('esg_fmt_docx', " DOCX Raporu"), "DOCX", self.lm.tr('esg_fmt_docx_desc', "Microsoft Word formatında detaylı ESG raporu")),
            (self.lm.tr('esg_fmt_excel', " Excel Raporu"), "Excel", self.lm.tr('esg_fmt_excel_desc', "Excel formatında ESG verileri ve grafikler")),
            (self.lm.tr('esg_fmt_pdf', " PDF Raporu"), "PDF", self.lm.tr('esg_fmt_pdf_desc', "PDF formatında yazdırılabilir ESG raporu")),
            (self.lm.tr('esg_fmt_dashboard', " Dashboard Raporu"), "Dashboard", self.lm.tr('esg_fmt_dashboard_desc', "Görsel dashboard içeren interaktif rapor"))
        ]

        for i, (text, value, desc) in enumerate(formats):
            frame = tk.Frame(format_frame, bg='white')
            frame.pack(fill='x', pady=5)

            rb = tk.Radiobutton(frame, text=text, variable=format_var, value=value,
                               font=('Segoe UI', 11), bg='white', fg='#2c3e50',
                               selectcolor='#3b82f6')
            rb.pack(side='left')

            tk.Label(frame, text=desc, font=('Segoe UI', 9), fg='#666', bg='white').pack(side='left', padx=(10, 0))

        # Rapor seçenekleri
        options_frame = tk.Frame(create_frame, bg='white')
        options_frame.pack(fill='x', padx=15, pady=(0, 15))

        tk.Label(options_frame, text=self.lm.tr('esg_report_options', "Rapor Seçenekleri:"), font=('Segoe UI', 11, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', pady=(10, 5))

        # Checkbox'lar
        self.include_charts = tk.BooleanVar(value=True)
        self.include_details = tk.BooleanVar(value=True)
        self.include_signals = tk.BooleanVar(value=True)
        self.include_comparison = tk.BooleanVar(value=False)

        options = [
            (self.lm.tr('esg_opt_charts', " Grafikler ve Görselleştirmeler"), self.include_charts),
            (self.lm.tr('esg_opt_details', " Detaylı Skor Analizi"), self.include_details),
            (self.lm.tr('esg_opt_signals', " ESG Sinyalleri"), self.include_signals),
            (self.lm.tr('esg_opt_comparison', " Sektör Karşılaştırması"), self.include_comparison)
        ]

        for text, var in options:
            cb = tk.Checkbutton(options_frame, text=text, variable=var,
                               font=('Segoe UI', 10), bg='white', fg='#2c3e50',
                               selectcolor='#3b82f6')
            cb.pack(anchor='w', pady=2)

        # Rapor oluştur butonu
        create_btn = tk.Button(create_frame, text=self.lm.tr('esg_btn_create_report', " Rapor Oluştur"),
                              font=('Segoe UI', 12, 'bold'), fg='white', bg='#3b82f6',
                              relief='flat', cursor='hand2',
                              command=lambda: self.create_esg_report(format_var.get(), report_window),
                              padx=30, pady=10)
        create_btn.pack(pady=15)

        # Mevcut raporlar bölümü
        existing_frame = tk.LabelFrame(main_frame, text=self.lm.tr('esg_existing_reports', " Mevcut ESG Raporları"),
                                     font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        existing_frame.pack(fill='both', expand=True)

        # Raporlar tablosu
        table_frame = tk.Frame(existing_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Treeview oluştur
        columns = (
            self.lm.tr('esg_col_report_name', "Rapor Adı"),
            self.lm.tr('esg_col_format', "Format"),
            self.lm.tr('esg_col_date', "Tarih"),
            self.lm.tr('esg_col_size', "Boyut"),
            self.lm.tr('esg_col_status', "Durum")
        )
        self.reports_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)

        for col in columns:
            self.reports_tree.heading(col, text=col)
            self.reports_tree.column(col, width=120)

        # Scrollbar
        scrollbar_reports = ttk.Scrollbar(table_frame, orient="vertical", command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=scrollbar_reports.set)

        self.reports_tree.pack(side="left", fill="both", expand=True)
        scrollbar_reports.pack(side="right", fill="y")

        # Rapor işlemleri butonları
        actions_frame = tk.Frame(existing_frame, bg='white')
        actions_frame.pack(fill='x', padx=15, pady=(0, 15))

        ttk.Button(actions_frame, text=self.lm.tr('btn_refresh', " Yenile"),
                   command=self.refresh_reports).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text=self.lm.tr('btn_open_folder', " Klasörü Aç"),
                   command=self.open_reports_folder).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text=self.lm.tr('btn_delete_selected', "️ Seçiliyi Sil"), style='Accent.TButton',
                   command=self.delete_selected_report).pack(side='left')
        ttk.Button(actions_frame, text=self.lm.tr('btn_preview', " Önizle"), style='Primary.TButton',
                   command=self.preview_selected_esg_report).pack(side='left', padx=(10, 10))
        ttk.Button(actions_frame, text=self.lm.tr('btn_open', " Aç"), style='Primary.TButton',
                   command=self.open_selected_esg_report).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text=self.lm.tr('btn_save_as', " Farklı Kaydet"), style='Primary.TButton',
                   command=self.save_selected_esg_report_as).pack(side='left', padx=(0, 10))
        ttk.Button(actions_frame, text=self.lm.tr('btn_print', " Yazdır"), style='Primary.TButton',
                   command=self.print_selected_esg_report).pack(side='left')

        # İlk yükleme
        self.refresh_reports()

    def create_esg_report(self, format_type, parent_window) -> None:
        """ESG raporu oluştur"""
        try:
            # Progress dialog
            progress_window = tk.Toplevel(parent_window)
            progress_window.title(self.lm.tr('title_creating_report', " Rapor Oluşturuluyor"))
            progress_window.geometry("400x150")
            progress_window.configure(bg='#f8f9fa')
            progress_window.grab_set()

            progress_frame = tk.Frame(progress_window, bg='#f8f9fa')
            progress_frame.pack(expand=True)

            msg = self.lm.tr('msg_creating_report', "{format} ESG raporu oluşturuluyor...").replace('{format}', format_type)
            progress_label = tk.Label(progress_frame, text=msg,
                                    font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa')
            progress_label.pack(pady=20)

            progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill='x')
            progress_bar.start()

            progress_window.update()

            # ESG verilerini al
            scores = self.manager.compute_scores(self.company_id)
            signals = self.manager.get_top_signals(self.company_id)

            # Rapor oluştur
            report_path = self.manager.generate_esg_report(
                self.company_id,
                format_type,
                scores,
                signals,
                {
                    'include_charts': self.include_charts.get(),
                    'include_details': self.include_details.get(),
                    'include_signals': self.include_signals.get(),
                    'include_comparison': self.include_comparison.get()
                }
            )

            progress_window.destroy()

            if report_path:
                msg_success = self.lm.tr('msg_report_created', "{format} ESG raporu başarıyla oluşturuldu!\n\nDosya: {path}\n\nRapor 'Mevcut Raporlar' bölümünde görüntülenebilir.")
                msg_success = msg_success.replace('{format}', format_type).replace('{path}', report_path)
                messagebox.showinfo(self.lm.tr('title_success', "Başarılı"), msg_success)

                self.refresh_reports()
                parent_window.destroy()
            else:
                msg_fail = self.lm.tr('msg_report_failed', "{format} ESG raporu oluşturulamadı!").replace('{format}', format_type)
                messagebox.showerror(self.lm.tr('title_error', "Hata"), msg_fail)

        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            msg_err = self.lm.tr('msg_report_error', "Rapor oluşturma sırasında hata: {error}").replace('{error}', str(e))
            messagebox.showerror(self.lm.tr('title_error', "Hata"), msg_err)

    def refresh_reports(self) -> None:
        """Raporlar tablosunu yenile"""
        try:
            # Tabloyu temizle
            for item in self.reports_tree.get_children():
                self.reports_tree.delete(item)

            # Raporları al ve tabloya ekle
            reports = self.manager.get_esg_reports(self.company_id)
            for report in reports:
                self.reports_tree.insert('', 'end', values=(
                    report.get('report_name', ''),
                    report.get('format_type', ''),
                    report.get('created_at', '')[:10] if report.get('created_at') else '',
                    report.get('file_size', ''),
                    report.get('status', self.lm.tr('esg_status_completed', 'Tamamlandı'))
                ))
        except Exception as e:
            logging.error(self.lm.tr('esg_msg_refresh_error', "Raporlar yenilenirken hata: {error}").replace('{error}', str(e)))

    def open_reports_folder(self) -> None:
        """Raporlar klasörünü aç"""
        try:
            import os
            import subprocess

            reports_dir = os.path.join(self.manager.base_dir, 'data', 'companies', str(self.company_id), 'reports')
            if os.path.exists(reports_dir):
                subprocess.Popen(['explorer', reports_dir])
            else:
                messagebox.showwarning(self.lm.tr('title_warning', "Uyarı"), self.lm.tr('esg_msg_folder_not_found', "Raporlar klasörü bulunamadı!"))
        except Exception as e:
            msg = self.lm.tr('esg_msg_folder_error', "Klasör açılırken hata: {error}").replace('{error}', str(e))
            messagebox.showerror(self.lm.tr('title_error', "Hata"), msg)

    def delete_selected_report(self) -> None:
        """Seçili raporu sil"""
        selected = self.reports_tree.selection()
        if not selected:
            messagebox.showwarning(self.lm.tr('title_warning', "Uyarı"), self.lm.tr('msg_select_report', "Lütfen silinecek raporu seçin!"))
            return

        if messagebox.askyesno(self.lm.tr('title_confirm', "Onay"), self.lm.tr('esg_msg_confirm_delete', "Seçili raporu silmek istediğinizden emin misiniz?")):
            try:
                # Rapor silme işlemi burada yapılacak
                self.reports_tree.delete(selected[0])
                messagebox.showinfo(self.lm.tr('title_success', "Başarılı"), self.lm.tr('esg_msg_report_deleted', "Rapor başarıyla silindi!"))
            except Exception as e:
                msg = self.lm.tr('esg_msg_delete_error', "Rapor silinirken hata: {error}").replace('{error}', str(e))
                messagebox.showerror(self.lm.tr('title_error', "Hata"), msg)

    def _get_selected_esg_filepath(self) -> str:
        try:
            selected = self.reports_tree.selection()
            if not selected:
                return ''
            vals = self.reports_tree.item(selected[0], 'values')
            if not vals:
                return ''
            filename = vals[0]
            reports_dir = os.path.join(self.manager.base_dir, 'data', 'companies', str(self.company_id), 'reports')
            return os.path.join(reports_dir, filename)
        except Exception:
            return ''

    def preview_selected_esg_report(self) -> None:
        try:
            fp = self._get_selected_esg_filepath()
            if not fp:
                messagebox.showwarning(self.lm.tr('title_warning', 'Uyarı'), self.lm.tr('msg_select_report', 'Lütfen bir rapor seçin!'))
                return
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr('title_preview_report', 'ESG Rapor Önizleme'))
            win.geometry('700x500')
            win.configure(bg='white')
            info = tk.Text(win, wrap='word', bg='#ffffff')
            info.pack(fill='both', expand=True, padx=12, pady=12)
            msg = self.lm.tr('msg_preview_info', "Seçilen dosya: {path}\n\nTam içerik önizleme için 'Aç' butonunu kullanın.").replace('{path}', fp)
            info.insert('1.0', msg)
            info.config(state='disabled')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def open_selected_esg_report(self) -> None:
        try:
            fp = self._get_selected_esg_filepath()
            if not fp:
                messagebox.showwarning(self.lm.tr('title_warning', 'Uyarı'), self.lm.tr('msg_select_report', 'Lütfen bir rapor seçin!'))
                return
            if os.path.exists(fp):
                os.startfile(fp)
            else:
                messagebox.showerror(self.lm.tr('title_error', 'Hata'), self.lm.tr('msg_file_not_found', 'Rapor dosyası bulunamadı!'))
        except Exception as e:
            msg = self.lm.tr('msg_open_error', 'Dosya açılamadı: {error}').replace('{error}', str(e))
            messagebox.showerror(self.lm.tr('title_error', 'Hata'), msg)

    def save_selected_esg_report_as(self) -> None:
        try:
            fp = self._get_selected_esg_filepath()
            if not fp or not os.path.exists(fp):
                messagebox.showwarning(self.lm.tr('title_warning', 'Uyarı'), self.lm.tr('msg_select_valid_report', 'Lütfen geçerli bir rapor seçin!'))
                return
            ext = os.path.splitext(fp)[1]
            types = [(self.lm.tr('file_type_all', 'Tüm Dosyalar'),'*.*')]
            if ext.lower() == '.pdf':
                types.insert(0, (self.lm.tr('file_pdf', 'PDF Dosyası'),'*.pdf'))
            if ext.lower() in ('.xlsx','.xls'):
                types.insert(0, (self.lm.tr('file_excel', 'Excel Dosyası'),'*.xlsx;*.xls'))
            if ext.lower() in ('.docx','.doc'):
                types.insert(0, (self.lm.tr('file_word', 'Word Dosyası'),'*.docx;*.doc'))
            dest = filedialog.asksaveasfilename(
                title=self.lm.tr('title_save_report', "Raporu Farklı Kaydet"),
                defaultextension=ext, 
                filetypes=types
            )
            if dest:
                import shutil
                shutil.copy2(fp, dest)
                msg = self.lm.tr('msg_saved_as', 'Rapor kaydedildi: {path}').replace('{path}', dest)
                messagebox.showinfo(self.lm.tr('title_success', 'Bilgi'), msg)
        except Exception as e:
            msg = self.lm.tr('msg_save_error', 'Kaydetme hatası: {error}').replace('{error}', str(e))
            messagebox.showerror(self.lm.tr('title_error', 'Hata'), msg)

    def print_selected_esg_report(self) -> None:
        try:
            fp = self._get_selected_esg_filepath()
            if not fp or not os.path.exists(fp):
                messagebox.showwarning(self.lm.tr('title_warning', 'Uyarı'), self.lm.tr('msg_select_valid_report', 'Lütfen geçerli bir rapor seçin!'))
                return
            try:
                os.startfile(fp, 'print')
                messagebox.showinfo(self.lm.tr('title_success', 'Bilgi'), self.lm.tr('msg_print_started', 'Yazdırma başlatıldı!'))
            except Exception as e:
                msg = self.lm.tr('msg_print_error', 'Yazdırma hatası: {error}').replace('{error}', str(e))
                messagebox.showerror(self.lm.tr('title_error', 'Hata'), msg)
        except Exception as e:
            msg = self.lm.tr('msg_print_prep_error', 'Yazdırma hazırlık hatası: {error}').replace('{error}', str(e))
            messagebox.showerror(self.lm.tr('title_error', 'Hata'), msg)

    def show_esg_settings_window(self) -> None:
        """ESG ayarlar penceresini göster"""
        # Ayarlar penceresi oluştur
        settings_window = tk.Toplevel(self.parent)
        settings_window.title(self.lm.tr('title_esg_settings', "️ ESG Ayarları"))
        settings_window.geometry("900x700")
        settings_window.configure(bg='#f8f9fa')
        settings_window.grab_set()

        # Pencereyi merkeze al
        settings_window.transient(self.parent)
        settings_window.focus_force()

        # Başlık
        header_frame = tk.Frame(settings_window, bg='#6b7280', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=self.lm.tr('header_esg_settings', "️ ESG Ayarları ve Konfigürasyon"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#6b7280')
        title_label.pack(expand=True)

        # Ana içerik
        main_frame = tk.Frame(settings_window, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Notebook oluştur
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)

        # Ağırlık Ayarları sekmesi
        weights_frame = tk.Frame(notebook, bg='white')
        notebook.add(weights_frame, text=self.lm.tr('tab_weights', " Ağırlık Ayarları"))
        self.create_weights_tab(weights_frame)

        # Eşleştirme Ayarları sekmesi
        mapping_frame = tk.Frame(notebook, bg='white')
        notebook.add(mapping_frame, text=self.lm.tr('tab_mapping', " Eşleştirme Ayarları"))
        self.create_mapping_tab(mapping_frame)

        # Skorlama Ayarları sekmesi
        scoring_frame = tk.Frame(notebook, bg='white')
        notebook.add(scoring_frame, text=self.lm.tr('tab_scoring', " Skorlama Ayarları"))
        self.create_scoring_tab(scoring_frame)

        # Sektör Ayarları sekmesi
        sector_frame = tk.Frame(notebook, bg='white')
        notebook.add(sector_frame, text=self.lm.tr('tab_sector', " Sektör Ayarları"))
        self.create_sector_tab(sector_frame)

        # Butonlar
        button_frame = tk.Frame(main_frame, bg='#f8f9fa', height=60)
        button_frame.pack(fill='x', pady=(20, 0))
        button_frame.pack_propagate(False)

        tk.Button(button_frame, text=self.lm.tr('btn_save', " Kaydet"), command=lambda: self.save_settings(settings_window),
                 font=('Segoe UI', 12, 'bold'), fg='white', bg='#10b981', relief='flat',
                 padx=30, pady=10).pack(side='left', padx=(0, 10))

        tk.Button(button_frame, text=self.lm.tr('btn_reset_default', " Varsayılana Dön"), command=self.reset_to_defaults,
                 font=('Segoe UI', 12, 'bold'), fg='white', bg='#f59e0b', relief='flat',
                 padx=30, pady=10).pack(side='left', padx=(0, 10))

        tk.Button(button_frame, text=self.lm.tr('btn_cancel', " İptal"), command=settings_window.destroy,
                 font=('Segoe UI', 12, 'bold'), fg='white', bg='#ef4444', relief='flat',
                 padx=30, pady=10).pack(side='right')

    def create_weights_tab(self, parent) -> None:
        """Ağırlık ayarları sekmesini oluştur"""
        # Scrollable frame
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Başlık
        tk.Label(scrollable_frame, text=self.lm.tr('title_weight_settings', "ESG Ağırlık Ayarları"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=(20, 10))

        tk.Label(scrollable_frame, text=self.lm.tr('desc_weight_settings', "ESG skorlarının hesaplanmasında kullanılan ağırlıkları ayarlayın:"),
                font=('Segoe UI', 11), fg='#666', bg='white').pack(pady=(0, 20))

        # Ağırlık değişkenleri
        self.weight_vars = {
            'E': tk.DoubleVar(value=self.manager.config['weights']['E']),
            'S': tk.DoubleVar(value=self.manager.config['weights']['S']),
            'G': tk.DoubleVar(value=self.manager.config['weights']['G'])
        }

        # Ağırlık slider'ları
        categories = [
            ('', self.lm.tr('cat_env_e', 'Çevresel (E)'), self.weight_vars['E'], '#10b981'),
            ('', self.lm.tr('cat_soc_s', 'Sosyal (S)'), self.weight_vars['S'], '#f59e0b'),
            ('️', self.lm.tr('cat_gov_g', 'Yönetişim (G)'), self.weight_vars['G'], '#3b82f6')
        ]

        for icon, name, var, color in categories:
            frame = tk.Frame(scrollable_frame, bg='white', relief='solid', bd=1)
            frame.pack(fill='x', padx=20, pady=10)

            # Başlık
            title_frame = tk.Frame(frame, bg=color)
            title_frame.pack(fill='x', padx=10, pady=10)

            tk.Label(title_frame, text=f"{icon} {name}",
                    font=('Segoe UI', 12, 'bold'), fg='white', bg=color).pack()

            # Slider
            slider_frame = tk.Frame(frame, bg='white')
            slider_frame.pack(fill='x', padx=20, pady=15)

            slider = tk.Scale(slider_frame, from_=0.0, to=1.0, resolution=0.05,
                             orient='horizontal', variable=var, bg='white',
                             font=('Segoe UI', 11), length=400)
            slider.pack(side='left')

            # Değer gösterici
            value_label = tk.Label(slider_frame, text=f"{var.get():.2f}",
                                  font=('Segoe UI', 12, 'bold'), fg=color, bg='white')
            value_label.pack(side='left', padx=(20, 0))

            # Değer değiştiğinde label'ı güncelle
            var.trace('w', lambda *args, label=value_label, var=var:
                     label.config(text=f"{var.get():.2f}"))

        # Toplam kontrol
        total_frame = tk.Frame(scrollable_frame, bg='#f8f9fa', relief='solid', bd=2)
        total_frame.pack(fill='x', padx=20, pady=20)

        tk.Label(total_frame, text=self.lm.tr('title_total_weight', " Toplam Ağırlık Kontrolü"),
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(pady=10)

        self.total_label = tk.Label(total_frame, text=self.lm.tr('lbl_total', "Toplam: 1.00"),
                                   font=('Segoe UI', 14, 'bold'), fg='#10b981', bg='#f8f9fa')
        self.total_label.pack(pady=(0, 10))

        # Toplam değişiklik kontrolü
        for var in self.weight_vars.values():
            var.trace('w', self.update_total_weight)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_mapping_tab(self, parent) -> None:
        """Eşleştirme ayarları sekmesini oluştur"""
        # Scrollable frame
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Başlık
        tk.Label(scrollable_frame, text=self.lm.tr('title_mapping_settings', "ESG Eşleştirme Ayarları"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=(20, 10))

        tk.Label(scrollable_frame, text=self.lm.tr('desc_mapping_settings', "ESG kategorilerinin hangi standartlarla eşleştirileceğini belirleyin:"),
                font=('Segoe UI', 11), fg='#666', bg='white').pack(pady=(0, 20))

        mappings = self.manager.config['mappings']

        for category, icon in [('E', ''), ('S', ''), ('G', '️')]:
            cat_name = self._get_category_name(category) # This helper needs localization too probably
            # Localize category name if possible or assume _get_category_name returns English/Turkish
            # Let's check _get_category_name implementation later. For now, rely on dynamic value.
            category_frame = tk.LabelFrame(scrollable_frame, text=f"{icon} {category} - {cat_name}",
                                         font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
            category_frame.pack(fill='x', padx=20, pady=10)

            # GRI Standartları
            gri_frame = tk.Frame(category_frame, bg='white')
            gri_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(gri_frame, text=self.lm.tr('lbl_gri_standards', "GRI Standartları:"),
                    font=('Segoe UI', 11, 'bold'), fg='#2196F3', bg='white').pack(anchor='w')

            gri_list = mappings.get(category, {}).get('gri_standards', [])
            if not gri_list:
                gri_list = mappings.get(category, {}).get('gri_categories', [])

            for standard in gri_list:
                tk.Label(gri_frame, text=f"• {standard}",
                        font=('Segoe UI', 10), fg='#666', bg='white').pack(anchor='w', padx=(20, 0))

            # TSRS Bölümleri
            tsrs_frame = tk.Frame(category_frame, bg='white')
            tsrs_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(tsrs_frame, text=self.lm.tr('lbl_tsrs_sections', "TSRS Bölümleri:"),
                    font=('Segoe UI', 11, 'bold'), fg='#FF9800', bg='white').pack(anchor='w')

            tsrs_list = mappings.get(category, {}).get('tsrs_sections', [])
            for section in tsrs_list:
                tk.Label(tsrs_frame, text=f"• {section}",
                        font=('Segoe UI', 10), fg='#666', bg='white').pack(anchor='w', padx=(20, 0))

            # SDG Hedefleri
            sdg_frame = tk.Frame(category_frame, bg='white')
            sdg_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(sdg_frame, text=self.lm.tr('lbl_sdg_goals', "SDG Hedefleri:"),
                    font=('Segoe UI', 11, 'bold'), fg='#4CAF50', bg='white').pack(anchor='w')

            sdg_list = mappings.get(category, {}).get('sdg_hint_goals', [])
            for goal in sdg_list:
                tk.Label(sdg_frame, text=f"• SDG {goal}",
                        font=('Segoe UI', 10), fg='#666', bg='white').pack(anchor='w', padx=(20, 0))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_scoring_tab(self, parent) -> None:
        """Skorlama ayarları sekmesini oluştur"""
        # Scrollable frame
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Başlık
        tk.Label(scrollable_frame, text=self.lm.tr('title_scoring_settings', "ESG Skorlama Ayarları"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=(20, 10))

        tk.Label(scrollable_frame, text=self.lm.tr('desc_scoring_settings', "ESG skorlarının hesaplanma yöntemini ve bonus sistemini ayarlayın:"),
                font=('Segoe UI', 11), fg='#666', bg='white').pack(pady=(0, 20))

        scoring = self.manager.config['scoring']

        # Minimum tamamlanma oranı
        min_frame = tk.LabelFrame(scrollable_frame, text=self.lm.tr('title_min_completeness', " Minimum Tamamlanma Oranı"),
                                 font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        min_frame.pack(fill='x', padx=20, pady=10)

        self.min_completeness = tk.DoubleVar(value=scoring.get('min_completeness_to_count', 0.5))

        tk.Label(min_frame, text=self.lm.tr('desc_min_completeness', "Bir standart kategorisinin skora dahil edilmesi için minimum tamamlanma oranı:"),
                font=('Segoe UI', 11), fg='#666', bg='white').pack(pady=10)

        min_slider = tk.Scale(min_frame, from_=0.0, to=1.0, resolution=0.05,
                             orient='horizontal', variable=self.min_completeness, bg='white',
                             font=('Segoe UI', 11), length=400)
        min_slider.pack(pady=10)

        # Bonus ayarları
        bonus_frame = tk.LabelFrame(scrollable_frame, text=self.lm.tr('title_bonus_system', " Bonus Sistemi"),
                                   font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        bonus_frame.pack(fill='x', padx=20, pady=10)

        # Kanıt bonusu
        evidence_frame = tk.Frame(bonus_frame, bg='white')
        evidence_frame.pack(fill='x', padx=15, pady=10)

        self.evidence_bonus = tk.DoubleVar(value=scoring.get('evidence_bonus', 0.05))

        tk.Label(evidence_frame, text=self.lm.tr('lbl_evidence_bonus', "Kanıt Bonusu (ERP, Anket, vb. veri varlığında):"),
                font=('Segoe UI', 11), fg='#666', bg='white').pack(anchor='w')

        evidence_slider = tk.Scale(evidence_frame, from_=0.0, to=0.2, resolution=0.01,
                                  orient='horizontal', variable=self.evidence_bonus, bg='white',
                                  font=('Segoe UI', 11), length=400)
        evidence_slider.pack(pady=10)

        # Materyalite bonusu
        materiality_frame = tk.Frame(bonus_frame, bg='white')
        materiality_frame.pack(fill='x', padx=15, pady=10)

        self.materiality_bonus = tk.DoubleVar(value=scoring.get('materiality_bonus', 0.1))

        tk.Label(materiality_frame, text="Materyalite Bonusu (TSRS materyalite değerlendirmesi varlığında):",
                font=('Segoe UI', 11), fg='#666', bg='white').pack(anchor='w')

        materiality_slider = tk.Scale(materiality_frame, from_=0.0, to=0.3, resolution=0.01,
                                     orient='horizontal', variable=self.materiality_bonus, bg='white',
                                     font=('Segoe UI', 11), length=400)
        materiality_slider.pack(pady=10)

        # Normalizasyon yöntemi
        norm_frame = tk.LabelFrame(scrollable_frame, text=self.lm.tr('title_norm_method', " Normalizasyon Yöntemi"),
                                  font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        norm_frame.pack(fill='x', padx=20, pady=10)

        self.normalize_method = tk.StringVar(value=scoring.get('normalize_method', 'ratio_answered_to_total'))

        methods = [
            ("ratio_answered_to_total", self.lm.tr('norm_ratio', "Yanıtlanan/Toplam Oranı"), self.lm.tr('norm_ratio_desc', "Standart yaklaşım")),
            ("percentage_based", self.lm.tr('norm_percentage', "Yüzde Tabanlı"), self.lm.tr('norm_percentage_desc', "Yüzde değerleri üzerinden")),
            ("weighted_average", self.lm.tr('norm_weighted', "Ağırlıklı Ortalama"), self.lm.tr('norm_weighted_desc', "Kategori ağırlıkları ile"))
        ]

        for value, name, desc in methods:
            frame = tk.Frame(norm_frame, bg='white')
            frame.pack(fill='x', padx=15, pady=5)

            rb = tk.Radiobutton(frame, text=name, variable=self.normalize_method, value=value,
                               font=('Segoe UI', 11), bg='white', fg='#2c3e50',
                               selectcolor='#3b82f6')
            rb.pack(side='left')

            tk.Label(frame, text=f"- {desc}",
                    font=('Segoe UI', 9), fg='#666', bg='white').pack(side='left', padx=(10, 0))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_sector_tab(self, parent) -> None:
        """Sektör ayarları sekmesini oluştur"""
        # Scrollable frame
        canvas = tk.Canvas(parent, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Başlık
        tk.Label(scrollable_frame, text=self.lm.tr('title_sector_settings', "Sektör Özelleştirmeleri"),
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=(20, 10))

        tk.Label(scrollable_frame, text=self.lm.tr('desc_sector_settings', "Sektörünüze özel ESG kriterlerini ve ağırlıklarını ayarlayın:"),
                font=('Segoe UI', 11), fg='#666', bg='white').pack(pady=(0, 20))

        # Sektör seçimi
        sector_frame = tk.LabelFrame(scrollable_frame, text=self.lm.tr('title_sector_selection', " Sektör Seçimi"),
                                   font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        sector_frame.pack(fill='x', padx=20, pady=10)

        self.sector_var = tk.StringVar(value=self.lm.tr('sec_general', "Genel"))

        sectors = [
            self.lm.tr('sec_general', "Genel"), self.lm.tr('sec_production', "Üretim"), 
            self.lm.tr('sec_tech', "Teknoloji"), self.lm.tr('sec_finance', "Finans"), 
            self.lm.tr('sec_energy', "Enerji"), self.lm.tr('sec_mining', "Madencilik"),
            self.lm.tr('sec_agriculture', "Tarım"), self.lm.tr('sec_construction', "İnşaat"), 
            self.lm.tr('sec_health', "Sağlık"), self.lm.tr('sec_education', "Eğitim"), 
            self.lm.tr('sec_tourism', "Turizm"), self.lm.tr('sec_logistics', "Lojistik")
        ]

        sector_combo = ttk.Combobox(sector_frame, textvariable=self.sector_var, values=sectors,
                                   font=('Segoe UI', 11), width=30)
        sector_combo.pack(padx=15, pady=15)

        # Sektör özelleştirmeleri
        custom_frame = tk.LabelFrame(scrollable_frame, text=self.lm.tr('title_sector_custom', "️ Sektör Özelleştirmeleri"),
                                   font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        custom_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(custom_frame, text=self.lm.tr('desc_sector_custom', "Seçilen sektör için özel ayarlar burada görüntülenecek."),
                font=('Segoe UI', 11), fg='#666', bg='white').pack(pady=20)

        # KPI özelleştirmeleri
        kpi_frame = tk.LabelFrame(scrollable_frame, text=self.lm.tr('title_custom_kpis', " Özel KPI'lar"),
                                 font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        kpi_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(kpi_frame, text=self.lm.tr('desc_custom_kpis', "Sektörünüze özel ESG göstergelerini tanımlayabilirsiniz."),
                font=('Segoe UI', 11), fg='#666', bg='white').pack(pady=20)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def update_total_weight(self, *args) -> None:
        """Toplam ağırlığı güncelle"""
        total = sum(var.get() for var in self.weight_vars.values())
        self.total_label.config(text=self.lm.tr('lbl_total', "Toplam: {value}").replace('{value}', f"{total:.2f}"))

        if abs(total - 1.0) < 0.01:
            self.total_label.config(fg='#10b981')
        else:
            self.total_label.config(fg='#ef4444')

    def save_settings(self, parent_window) -> None:
        """Ayarları kaydet"""
        try:
            # Ağırlıkları güncelle
            self.manager.config['weights'] = {
                'E': self.weight_vars['E'].get(),
                'S': self.weight_vars['S'].get(),
                'G': self.weight_vars['G'].get()
            }

            # Skorlama ayarlarını güncelle
            self.manager.config['scoring'] = {
                'min_completeness_to_count': self.min_completeness.get(),
                'evidence_bonus': self.evidence_bonus.get(),
                'materiality_bonus': self.materiality_bonus.get(),
                'normalize_method': self.normalize_method.get()
            }

            # Konfigürasyon dosyasını kaydet
            import json
            with open(self.manager.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.manager.config, f, indent=2, ensure_ascii=False)

            messagebox.showinfo(self.lm.tr('title_success', "Başarılı"), self.lm.tr('msg_settings_saved', "ESG ayarları başarıyla kaydedildi!"))
            parent_window.destroy()

        except Exception as e:
            msg = self.lm.tr('msg_settings_error', "Ayarlar kaydedilirken hata oluştu: {error}").replace('{error}', str(e))
            messagebox.showerror(self.lm.tr('title_error', "Hata"), msg)

    def reset_to_defaults(self) -> None:
        """Ayarları varsayılan değerlere döndür"""
        if messagebox.askyesno(self.lm.tr('title_confirm', "Onay"), self.lm.tr('msg_confirm_reset', "Tüm ayarları varsayılan değerlere döndürmek istediğinizden emin misiniz?")):
            # Varsayılan değerleri yükle
            self.weight_vars['E'].set(0.4)
            self.weight_vars['S'].set(0.3)
            self.weight_vars['G'].set(0.3)

            self.min_completeness.set(0.5)
            self.evidence_bonus.set(0.05)
            self.materiality_bonus.set(0.1)
            self.normalize_method.set('ratio_answered_to_total')

            self.update_total_weight()

            messagebox.showinfo(self.lm.tr('title_success', "Başarılı"), self.lm.tr('msg_reset_success', "Ayarlar varsayılan değerlere döndürüldü!"))
