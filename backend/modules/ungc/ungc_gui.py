import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNGC (UN Global Compact) GUI
BM Küresel İlkeler Sözleşmesi - Ten Principles
"""

import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Dict, List

from backend.core.language_manager import LanguageManager
from backend.utils.ui_theme import apply_theme

from .ungc_manager import UNGCManager
from config.icons import Icons


class UNGCGUI:
    """UNGC GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()

        # Base directory
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
        self.db_path = db_path
        config_path = os.path.join(base_dir, 'config', 'ungc_config.json')

        self.manager = UNGCManager(db_path, config_path)
        self.compliance_all: List[Dict] = []
        self.compliance_filtered: List[Dict] = []
        self.compliance_selection_states: Dict[str, bool] = {}

        # Tabloları oluştur
        self.manager.create_ungc_tables()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        apply_theme(self.parent)
        main_frame = tk.Frame(self.parent, bg='#DDEAFB')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#2F6DB2', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text=f"{Icons.WORLD} {self.lm.tr('ungc_title', 'UN Global Compact - Ten Principles')}",
                font=('Segoe UI', 14, 'bold'), fg='white', bg='#2F6DB2').pack(side='left', padx=16)
        toolbar = ttk.Frame(main_frame, style='Toolbar.TFrame')
        toolbar.pack(fill='x', pady=(10, 10))
        ttk.Button(toolbar, text=f"{Icons.ADD} {self.lm.tr('btn_new', 'Yeni')}", style='Primary.TButton').pack(side='left', padx=6)
        ttk.Button(toolbar, text=f"{Icons.SAVE} {self.lm.tr('btn_save', 'Kaydet')}", style='Primary.TButton').pack(side='left', padx=6)
        ttk.Button(toolbar, text=f"{Icons.DELETE} {self.lm.tr('btn_delete', 'Sil')}", style='Accent.TButton').pack(side='left', padx=6)
        ttk.Button(toolbar, text=f"{Icons.LOADING} {self.lm.tr('btn_refresh', 'Yenile')}", style='Primary.TButton', command=self.load_data).pack(side='left', padx=6)
        ttk.Button(toolbar, text=f"{Icons.FOLDER_OPEN} {self.lm.tr('btn_report_center', 'Rapor Merkezi')}", style='Primary.TButton', command=self.open_report_center_ungc).pack(side='left', padx=6)
        tk.Label(toolbar, text=self.lm.tr('period', "Dönem:")).pack(side='left')
        self.ungc_period_var = tk.StringVar(value=str(datetime.now().year))
        years = [str(y) for y in range(datetime.now().year - 5, datetime.now().year + 1)]
        period_combo = ttk.Combobox(toolbar, textvariable=self.ungc_period_var, values=years, width=8, state='readonly')
        period_combo.pack(side='left', padx=6)
        self.search_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.search_var, width=24).pack(side='right', padx=6)
        try:
            self.search_var.trace_add('write', lambda *args: self.apply_compliance_filter())
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        ttk.Label(toolbar, text=self.lm.tr('search', "Ara:")).pack(side='right')
        ttk.Button(toolbar, text=f"{Icons.EDIT} {self.lm.tr('kpi_entry', 'KPI Veri Girişi')}", style='Primary.TButton', command=self.open_kpi_entry).pack(side='right', padx=6)
        def _validate_year(y: str) -> bool:
            try:
                y = (y or '').strip()
                return y.isdigit() and len(y) == 4 and 1990 <= int(y) <= 2100
            except Exception:
                return False
        def _on_period_change(*args):
            if not _validate_year(self.ungc_period_var.get()):
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('select_valid_year', 'Geçerli bir yıl seçin'))
                return
            try:
                self.load_data()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        try:
            self.ungc_period_var.trace_add('write', _on_period_change)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # İçerik
        content_frame = tk.Frame(main_frame, bg='#DDEAFB')
        content_frame.pack(fill='both', expand=True)

        # Skor kartları
        self.create_score_cards(content_frame)

        # Notebook
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, pady=(20, 0))

        # Sekmeler
        self.create_principles_tab()
        self.create_compliance_tab()
        self.create_mapping_tab()

    def open_report_center_ungc(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('ungc')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for ungc: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_center_error', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def create_score_cards(self, parent) -> None:
        cards_frame = tk.Frame(parent, bg='#DDEAFB')
        cards_frame.pack(fill='x')

        self.score_vars = {}
        categories = [
            ('Human Rights', self.lm.tr('human_rights', 'İnsan Hakları'), '#ef4444'),
            ('Labour', self.lm.tr('labour', 'Çalışma'), '#f59e0b'),
            ('Environment', self.lm.tr('environment', 'Çevre'), '#10b981'),
            ('Anti-Corruption', self.lm.tr('anti_corruption', 'Yolsuzlukla Mücadele'), '#3b82f6')
        ]

        for key, title, color in categories:
            card = tk.Frame(cards_frame, bg=color, relief='raised', bd=1)
            card.pack(side='left', fill='both', expand=True, padx=(0, 10) if key != 'Anti-Corruption' else 0)

            tk.Label(card, text=title, font=('Segoe UI', 11, 'bold'),
                    fg='white', bg=color).pack(pady=(15, 5))

            self.score_vars[key] = tk.StringVar(value="-%")
            tk.Label(card, textvariable=self.score_vars[key],
                    font=('Segoe UI', 24, 'bold'), fg='white', bg=color).pack(pady=(5, 15))

    def create_principles_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg='#FFFFFF')
        self.notebook.add(tab, text=self.lm.tr('ten_principles', " 10 İlke"))
        table_frame = tk.Frame(tab, bg='#FFFFFF')
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)

        columns = (
            self.lm.tr('principle', 'İlke'),
            self.lm.tr('category', 'Kategori'),
            self.lm.tr('title', 'Başlık'),
            self.lm.tr('status', 'Durum'),
            self.lm.tr('score', 'Skor'),
            'SDG', 'GRI', 'TSRS'
        )
        self.principles_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12, style='Custom.Treeview')

        for col in columns:
            self.principles_tree.heading(col, text=col)
            self.principles_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.principles_tree.yview)
        self.principles_tree.configure(yscrollcommand=scrollbar.set)

        self.principles_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.principles_tree.tag_configure('odd', background='#F7FAFF')
        self.principles_tree.tag_configure('even', background='#FFFFFF')

    def create_compliance_tab(self) -> None:
        tab = tk.Frame(self.notebook, bg='#FFFFFF')
        self.notebook.add(tab, text=self.lm.tr('compliance_status', " Uyum Durumu"))
        tk.Label(tab, text=self.lm.tr('ungc_compliance_desc', "UNGC uyum durumu ve kanıtlar"),
                font=('Segoe UI', 12), fg='#2C3E50', bg='#FFFFFF').pack(pady=10)
        container = tk.Frame(tab, bg='#FFFFFF')
        container.pack(fill='both', expand=True)
        left = tk.Frame(container, bg='#FFFFFF', width=280)
        left.pack(side='left', fill='y', padx=20, pady=10)
        right = tk.Frame(container, bg='#FFFFFF')
        right.pack(side='left', fill='both', expand=True, padx=(0,20), pady=10)
        ttk.Label(left, text=self.lm.tr('level', 'Düzey'), font=('Segoe UI', 10)).pack(anchor='w')
        self.filter_level = ttk.Combobox(left, values=['', 'None', 'Partial', 'Full'], width=20)
        self.filter_level.pack(anchor='w', pady=4)
        ttk.Label(left, text=self.lm.tr('min_score', 'Min Skor (%)'), font=('Segoe UI', 10)).pack(anchor='w', pady=(10,0))
        self.filter_score = ttk.Spinbox(left, from_=0, to=100, increment=5, width=8)
        self.filter_score.pack(anchor='w', pady=4)
        ttk.Button(left, text=self.lm.tr('apply_filter', 'Filtre Uygula'), style='Primary.TButton', command=self.apply_compliance_filter).pack(anchor='w', pady=8)
        columns = (
            self.lm.tr('select', 'Seç'),
            self.lm.tr('principle', 'İlke'),
            self.lm.tr('level', 'Seviye'),
            self.lm.tr('score', 'Skor'),
            self.lm.tr('evidence', 'Kanıt'),
            self.lm.tr('last_assessment', 'Son Değerlendirme')
        )
        self.compliance_tree = ttk.Treeview(right, columns=columns, show='headings', height=12, style='Custom.Treeview')
        self.compliance_tree.heading(columns[0], text=columns[0])
        for col in columns[1:]:
            self.compliance_tree.heading(col, text=col)
        self.compliance_tree.column(columns[0], width=60, anchor='center')
        for col in columns[1:]:
            self.compliance_tree.column(col, width=140)
        self.compliance_tree.pack(fill='both', expand=True)
        self.compliance_tree.tag_configure('odd', background='#F7FAFF')
        self.compliance_tree.tag_configure('even', background='#FFFFFF')
        self.compliance_tree.bind('<Button-1>', self.on_compliance_click)
        actions = tk.Frame(tab, bg='#FFFFFF')
        actions.pack(fill='x', padx=20, pady=(0, 10))
        ttk.Button(actions, text=self.lm.tr('edit_level', "Düzey Düzenle"), style='Primary.TButton', command=self.edit_compliance_level).pack(side='left', padx=6)
        ttk.Button(actions, text=self.lm.tr('add_evidence', "Kanıt Ekle"), style='Primary.TButton', command=self.add_compliance_evidence).pack(side='left', padx=6)
        footer = tk.Frame(right, bg='#FFFFFF')
        footer.pack(fill='x', padx=20, pady=(0,10))
        self.compliance_total_label = tk.Label(footer, text=f"{self.lm.tr('total', 'Toplam')}: 0", font=('Segoe UI', 10), bg='#FFFFFF', fg='#6B7A90')
        self.compliance_total_label.pack(side='left')
        self.compliance_page_label = tk.Label(footer, text=f"{self.lm.tr('page', 'Sayfa')}: 1/1", font=('Segoe UI', 10), bg='#FFFFFF', fg='#6B7A90')
        self.compliance_page_label.pack(side='right')
        self.compliance_next_btn = ttk.Button(footer, text=self.lm.tr('btn_next', 'Sonraki ▶'), style='Primary.TButton', command=self.next_page_compliance)
        self.compliance_next_btn.pack(side='right', padx=4)
        self.compliance_prev_btn = ttk.Button(footer, text=self.lm.tr('prev', '◀ Önceki'), style='Primary.TButton', command=self.prev_page_compliance)
        self.compliance_prev_btn.pack(side='right', padx=4)
        self.compliance_page_size = 20
        self.compliance_current_page = 0
        self.compliance_all = []
        self.compliance_filtered = []
        self.compliance_selection_states = {}

    def create_mapping_tab(self) -> None:
        """Eşleştirme sekmesi"""
        tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(tab, text=self.lm.tr('framework_mapping', " Framework Eşleştirme"))

        tk.Label(tab, text=self.lm.tr('mapping_desc', "UNGC ↔ SDG/GRI/TSRS eşleştirmeleri"),
                font=('Segoe UI', 12), fg='#2c3e50', bg='white').pack(pady=20)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            from .ungc_manager_enhanced import UNGCManagerEnhanced
            enh = UNGCManagerEnhanced(self.db_path, os.path.join(os.path.dirname(self.db_path), '..', 'config', 'ungc_config.json'))
            enh.create_tables()
            period = getattr(self, 'ungc_period_var', tk.StringVar(value=str(datetime.now().year))).get()
            if not period or not period.isdigit():
                period = str(datetime.now().year)
            enh.update_compliance_from_kpis(self.company_id, period=period)
            # İlke durumlarını hesapla
            status = self.manager.compute_principle_status(self.company_id, period=period)

            # Kategori skorlarını güncelle
            category_scores = status.get('category_scores', {})
            for category, score in category_scores.items():
                if category in self.score_vars:
                    self.score_vars[category].set(f"{score:.1f}%")

            # İlkeleri tabloya ekle
            self.load_principles(status)
            self.load_compliance_data()

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('load_error', 'Veriler yüklenirken hata')}: {e}")
            logging.error(f"UNGC veri yükleme hatası: {e}")

    def open_kpi_entry(self) -> None:
        try:
            from .ungc_kpi_forms import UNGCKPIDataEntry
            win = tk.Toplevel(self.parent)
            p = getattr(self, 'ungc_period_var', tk.StringVar(value=str(datetime.now().year))).get()
            if not p or not p.isdigit():
                p = str(datetime.now().year)
            UNGCKPIDataEntry(win, db_path=self.db_path, company_id=self.company_id, period=p)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('kpi_entry_error', 'KPI veri girişi açılamadı')}: {e}")

    def load_principles(self, status: Dict) -> None:
        try:
            for item in self.principles_tree.get_children():
                self.principles_tree.delete(item)
            principles = status.get('principles', [])
            mappings = self.manager.config.get('mappings', {})
            idx = 0
            for principle in principles:
                principle_id = principle.get('principle_id', '')
                mapping = mappings.get(principle_id, {})
                tag = 'odd' if idx % 2 == 0 else 'even'
                self.principles_tree.insert('', 'end', values=(
                    principle_id,
                    principle.get('category', ''),
                    principle.get('title', '')[:40],
                    principle.get('status', ''),
                    f"{principle.get('score', 0):.1f}%",
                    ', '.join(mapping.get('sdg', [])[:2]),
                    ', '.join(mapping.get('gri', [])[:2]),
                    ', '.join(mapping.get('tsrs', [])[:2])
                ), tags=(tag,))
                idx += 1
        except Exception as e:
            logging.error(f"İlkeler yükleme hatası: {e}")

    def load_compliance_data(self) -> None:
        try:
            for i in self.compliance_tree.get_children():
                self.compliance_tree.delete(i)
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            rows = cur.execute("SELECT principle_id, compliance_level, score, evidence_count, last_assessed FROM ungc_compliance WHERE company_id=? ORDER BY principle_id", (self.company_id,)).fetchall()
            conn.close()
            self.compliance_all = []
            for r in rows:
                pid = r[0] or ''
                try:
                    c2 = sqlite3.connect(self.db_path)
                    evc = c2.cursor().execute("SELECT COUNT(*) FROM ungc_evidence WHERE company_id=? AND principle_id=?", (self.company_id, pid)).fetchone()[0]
                    c2.close()
                except Exception:
                    evc = r[3] or 0
                self.compliance_all.append({'principle_id': pid, 'level': r[1] or '', 'score': float(r[2] or 0.0), 'evidence': evc, 'last': r[4] or ''})
                if pid not in self.compliance_selection_states:
                    self.compliance_selection_states[pid] = False
            self.compliance_filtered = self.compliance_all
            self.compliance_current_page = 0
            self.populate_compliance_tree(self._current_page_compliance())
            self._update_pagination_compliance()
        except Exception as e:
            logging.error(f"Uyum verisi yükleme hatası: {e}")

    def populate_compliance_tree(self, items) -> None:
        for i in self.compliance_tree.get_children():
            self.compliance_tree.delete(i)
        idx = 0
        for it in items:
            pid = it['principle_id']
            mark = Icons.PASS if self.compliance_selection_states.get(pid) else '—'
            tag = 'odd' if idx % 2 == 0 else 'even'
            self.compliance_tree.insert('', 'end', values=(mark, pid, it['level'], f"{it['score']*100:.1f}%", it['evidence'], it['last']), tags=(tag,))
            idx += 1
        total = len(self.compliance_filtered) if self.compliance_filtered else len(self.compliance_all)
        self.compliance_total_label.config(text=f"{self.lm.tr('total', 'Toplam')}: {total}")

    def on_compliance_click(self, event=None) -> None:
        region = self.compliance_tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
        col = self.compliance_tree.identify_column(event.x)
        if col != '#1':
            return
        row_id = self.compliance_tree.identify_row(event.y)
        if not row_id:
            return
        values = self.compliance_tree.item(row_id, 'values')
        pid = values[1]
        state = not self.compliance_selection_states.get(pid, False)
        self.compliance_selection_states[pid] = state
        self.compliance_tree.set(row_id, 'Seç', Icons.PASS if state else '—')

    def _current_page_compliance(self):
        data = self.compliance_filtered if self.compliance_filtered else self.compliance_all
        start = self.compliance_current_page * self.compliance_page_size
        end = start + self.compliance_page_size
        return data[start:end]

    def _update_pagination_compliance(self) -> None:
        data = self.compliance_filtered if self.compliance_filtered else self.compliance_all
        total = len(data)
        pages = max(1, (total + self.compliance_page_size - 1) // self.compliance_page_size)
        self.compliance_page_label.config(text=f"Sayfa: {self.compliance_current_page + 1}/{pages}")
        self.compliance_prev_btn.config(state='normal' if self.compliance_current_page > 0 else 'disabled')
        self.compliance_next_btn.config(state='normal' if self.compliance_current_page < pages - 1 else 'disabled')

    def next_page_compliance(self) -> None:
        data = self.compliance_filtered if self.compliance_filtered else self.compliance_all
        pages = max(1, (len(data) + self.compliance_page_size - 1) // self.compliance_page_size)
        if self.compliance_current_page < pages - 1:
            self.compliance_current_page += 1
            self.populate_compliance_tree(self._current_page_compliance())
            self._update_pagination_compliance()

    def prev_page_compliance(self) -> None:
        if self.compliance_current_page > 0:
            self.compliance_current_page -= 1
            self.populate_compliance_tree(self._current_page_compliance())
            self._update_pagination_compliance()

    def apply_compliance_filter(self) -> None:
        text = (self.search_var.get() or '').lower().strip() if hasattr(self, 'search_var') else ''
        level = (self.filter_level.get() or '').strip() if hasattr(self, 'filter_level') else ''
        try:
            min_score = float(self.filter_score.get())/100.0 if hasattr(self, 'filter_score') and self.filter_score.get() != '' else 0.0
        except Exception:
            min_score = 0.0
        data = []
        for it in self.compliance_all:
            if level and it['level'] != level:
                continue
            if it['score'] < min_score:
                continue
            if text and text not in it['principle_id'].lower():
                continue
            data.append(it)
        self.compliance_filtered = data
        self.compliance_current_page = 0
        self.populate_compliance_tree(self._current_page_compliance())
        self._update_pagination_compliance()

    def edit_compliance_level(self) -> None:
        sel = self.compliance_tree.selection()
        if not sel:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_principle', "Lütfen bir ilke seçin"))
            return
        vals = self.compliance_tree.item(sel[0], 'values')
        pid = vals[0]
        dialog = tk.Toplevel(self.parent)
        dialog.title("Uyum Düzeyi Düzenle")
        tk.Label(dialog, text="Düzey").pack(pady=6)
        level_var = tk.StringVar(value=str(vals[1]))
        ttk.Combobox(dialog, textvariable=level_var, values=["None","Partial","Full"], width=16).pack(pady=4)
        tk.Label(dialog, text="Notlar").pack(pady=6)
        notes = tk.Text(dialog, height=4, width=40)
        notes.pack(pady=4)
        def save():
            try:
                from .ungc_manager_enhanced import UNGCManagerEnhanced
                enh = UNGCManagerEnhanced(self.db_path)
                ok = enh.save_compliance_edit(self.company_id, pid, level_var.get(), notes.get('1.0', tk.END).strip())
                if ok:
                    dialog.destroy()
                    self.load_compliance_data()
                else:
                    messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('level_save_error', "Düzey kaydedilemedi"))
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), str(e))
        ttk.Button(dialog, text=self.lm.tr("btn_save", "Kaydet"), style='Primary.TButton', command=save).pack(pady=8)

    def add_compliance_evidence(self) -> None:
        sel = self.compliance_tree.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen bir ilke seçin")
            return
        vals = self.compliance_tree.item(sel[0], 'values')
        pid = vals[0]
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('add_evidence', "Kanıt Ekle"))
        tk.Label(dialog, text=self.lm.tr('file', "Dosya")).pack(pady=6)
        file_var = tk.StringVar()
        row = tk.Frame(dialog)
        row.pack(fill='x', padx=10)
        tk.Entry(row, textvariable=file_var, width=40).pack(side='left')
        def choose():
            from tkinter import filedialog as fd
            p = fd.askopenfilename(
                title=self.lm.tr('select_file', "Dosya Seç"),
                filetypes=[(self.lm.tr('all_files', "Tüm Dosyalar"), "*.*")]
            )
            if p:
                file_var.set(p)
        ttk.Button(row, text=self.lm.tr('select', "Seç"), style='Primary.TButton', command=choose).pack(side='left', padx=6)
        tk.Label(dialog, text="URL").pack(pady=6)
        url_var = tk.StringVar()
        tk.Entry(dialog, textvariable=url_var, width=48).pack()
        tk.Label(dialog, text=self.lm.tr('notes', "Notlar")).pack(pady=6)
        notes = tk.Text(dialog, height=3, width=48)
        notes.pack()
        def save():
            try:
                from .ungc_manager_enhanced import UNGCManagerEnhanced
                enh = UNGCManagerEnhanced(self.db_path)
                ok = enh.add_evidence(self.company_id, pid, 'file' if file_var.get() else 'url', file_var.get() or None, url_var.get() or None, notes.get('1.0', tk.END).strip())
                if not ok:
                    conn = sqlite3.connect(self.db_path)
                    cur = conn.cursor()
                    cur.execute("CREATE TABLE IF NOT EXISTS ungc_evidence (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id INTEGER NOT NULL, principle_id VARCHAR(10) NOT NULL, evidence_type TEXT, file_path TEXT, url TEXT, notes TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                    cur.execute("PRAGMA table_info(ungc_evidence)")
                    cols = [r[1] for r in cur.fetchall()]
                    if 'url' not in cols:
                        cur.execute("ALTER TABLE ungc_evidence ADD COLUMN url TEXT")
                    if 'file_path' not in cols:
                        cur.execute("ALTER TABLE ungc_evidence ADD COLUMN file_path TEXT")
                    cur.execute("INSERT INTO ungc_evidence(company_id, principle_id, evidence_type, file_path, url, notes) VALUES (?, ?, ?, ?, ?, ?)", (self.company_id, pid, 'file' if file_var.get() else 'url', file_var.get() or None, url_var.get() or None, notes.get('1.0', tk.END).strip()))
                    conn.commit()
                    conn.close()
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), str(e))
        ttk.Button(dialog, text=self.lm.tr("btn_save", "Kaydet"), style='Primary.TButton', command=save).pack(pady=8)

# Test
def test_ungc_gui() -> None:
    """UNGC GUI test"""
    root = tk.Tk()
    root.title("UNGC Test")
    root.geometry("1200x800")

    UNGCGUI(root, company_id=1)

    root.mainloop()

if __name__ == "__main__":
    test_ungc_gui()
