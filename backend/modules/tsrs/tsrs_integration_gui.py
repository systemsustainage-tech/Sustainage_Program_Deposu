import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS-GRI-SDG Entegrasyon GUI
Üç standart arasında eşleştirme yönetimi
"""

import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from utils.tooltip import bind_treeview_header_tooltips

from .tsrs_manager import TSRSManager


class TSRSIntegrationGUI:
    """TSRS-GRI-SDG Entegrasyon GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.tsrs_manager = TSRSManager()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Entegrasyon arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="TSRS-GRI-SDG Entegrasyon Merkezi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # Ana içerik - Notebook (Sekmeler)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # TSRS-GRI Eşleştirmeleri sekmesi
        self.tsrs_gri_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.tsrs_gri_frame, text=" TSRS-GRI Eşleştirmeleri")

        # TSRS-SDG Eşleştirmeleri sekmesi
        self.tsrs_sdg_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.tsrs_sdg_frame, text=" TSRS-SDG Eşleştirmeleri")

        # Entegre Raporlar sekmesi
        self.integrated_reports_frame = tk.Frame(self.notebook, bg='#f5f5f5')
        self.notebook.add(self.integrated_reports_frame, text=" Entegre Raporlar")

        # TSRS-GRI sekmesi içeriği
        self.create_tsrs_gri_tab()

        # TSRS-SDG sekmesi içeriği
        self.create_tsrs_sdg_tab()

        # Entegre raporlar sekmesi içeriği
        self.create_integrated_reports_tab()

    def create_tsrs_gri_tab(self) -> None:
        """TSRS-GRI eşleştirmeleri sekmesi"""
        # Sol panel - TSRS Standartları
        left_panel = tk.Frame(self.tsrs_gri_frame, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # TSRS başlığı
        tsrs_header = tk.Frame(left_panel, bg='#3498db', height=40)
        tsrs_header.pack(fill='x')
        tsrs_header.pack_propagate(False)

        tk.Label(tsrs_header, text="TSRS Standartları",
                font=('Segoe UI', 12, 'bold'), fg='white', bg='#3498db').pack(expand=True)

        # TSRS listesi
        tsrs_frame = tk.Frame(left_panel, bg='white')
        tsrs_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.tsrs_tree = ttk.Treeview(tsrs_frame, columns=('code', 'title', 'category'), show='headings', height=15)
        self.tsrs_tree.heading('code', text='Kod')
        self.tsrs_tree.heading('title', text='Başlık')
        self.tsrs_tree.heading('category', text='Kategori')

        self.tsrs_tree.column('code', width=100)
        self.tsrs_tree.column('title', width=200)
        self.tsrs_tree.column('category', width=120)

        # TSRS header tooltips
        try:
            bind_treeview_header_tooltips(self.tsrs_tree, {
                'Kod': 'TSRS standardı kodu; tekil tanımlayıcıdır.',
                'Başlık': 'Standart başlığı; eşleştirme ve raporlamada referans.',
                'Kategori': 'Ana kategori; yönetim, risk, metrik, hedef vb.'
            })
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # TSRS scrollbar
        tsrs_scrollbar = ttk.Scrollbar(tsrs_frame, orient="vertical", command=self.tsrs_tree.yview)
        self.tsrs_tree.configure(yscrollcommand=tsrs_scrollbar.set)

        self.tsrs_tree.pack(side='left', fill='both', expand=True)
        tsrs_scrollbar.pack(side='right', fill='y')

        # TSRS seçim olayı
        self.tsrs_tree.bind('<Button-1>', self.on_tsrs_select)

        # Sağ panel - GRI Eşleştirmeleri
        right_panel = tk.Frame(self.tsrs_gri_frame, bg='white', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True)

        # GRI başlığı
        gri_header = tk.Frame(right_panel, bg='#e74c3c', height=40)
        gri_header.pack(fill='x')
        gri_header.pack_propagate(False)

        tk.Label(gri_header, text="GRI Eşleştirmeleri",
                font=('Segoe UI', 12, 'bold'), fg='white', bg='#e74c3c').pack(expand=True)

        # GRI listesi
        gri_frame = tk.Frame(right_panel, bg='white')
        gri_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.gri_tree = ttk.Treeview(gri_frame, columns=('gri_standard', 'gri_disclosure', 'relationship'), show='headings', height=15)
        self.gri_tree.heading('gri_standard', text='GRI Standard')
        self.gri_tree.heading('gri_disclosure', text='GRI Disclosure')
        self.gri_tree.heading('relationship', text='İlişki Türü')

        self.gri_tree.column('gri_standard', width=120)
        self.gri_tree.column('gri_disclosure', width=120)
        self.gri_tree.column('relationship', width=100)

        # GRI header tooltips
        try:
            bind_treeview_header_tooltips(self.gri_tree, {
                'GRI Standard': 'GRI standard seti; konu alanı başlığı.',
                'GRI Disclosure': 'GRI açıklama kodu; raporlanacak gereksinim.',
                'İlişki Türü': 'TSRS-GRI ilişkisi: Birebir, Kısmi, İlgili.'
            })
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # GRI scrollbar
        gri_scrollbar = ttk.Scrollbar(gri_frame, orient="vertical", command=self.gri_tree.yview)
        self.gri_tree.configure(yscrollcommand=gri_scrollbar.set)

        self.gri_tree.pack(side='left', fill='both', expand=True)
        gri_scrollbar.pack(side='right', fill='y')

        # İstatistikler
        stats_frame = tk.Frame(self.tsrs_gri_frame, bg='#f8f9fa', relief='solid', bd=1)
        stats_frame.pack(fill='x', pady=(10, 0))

        tk.Label(stats_frame, text="TSRS-GRI Eşleştirme İstatistikleri",
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(pady=10)

        self.tsrs_gri_stats = tk.Label(stats_frame, text="Yükleniyor...",
                                      font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa')
        self.tsrs_gri_stats.pack(pady=(0, 10))

    def create_tsrs_sdg_tab(self) -> None:
        """TSRS-SDG eşleştirmeleri sekmesi"""
        # Sol panel - TSRS Standartları
        left_panel = tk.Frame(self.tsrs_sdg_frame, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # TSRS başlığı
        tsrs_header = tk.Frame(left_panel, bg='#3498db', height=40)
        tsrs_header.pack(fill='x')
        tsrs_header.pack_propagate(False)

        tk.Label(tsrs_header, text="TSRS Standartları",
                font=('Segoe UI', 12, 'bold'), fg='white', bg='#3498db').pack(expand=True)

        # TSRS listesi
        tsrs_frame = tk.Frame(left_panel, bg='white')
        tsrs_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.tsrs_sdg_tree = ttk.Treeview(tsrs_frame, columns=('code', 'title', 'category'), show='headings', height=15)
        self.tsrs_sdg_tree.heading('code', text='Kod')
        self.tsrs_sdg_tree.heading('title', text='Başlık')
        self.tsrs_sdg_tree.heading('category', text='Kategori')

        self.tsrs_sdg_tree.column('code', width=100)
        self.tsrs_sdg_tree.column('title', width=200)
        self.tsrs_sdg_tree.column('category', width=120)

        # TSRS scrollbar
        tsrs_scrollbar = ttk.Scrollbar(tsrs_frame, orient="vertical", command=self.tsrs_sdg_tree.yview)
        self.tsrs_sdg_tree.configure(yscrollcommand=tsrs_scrollbar.set)

        self.tsrs_sdg_tree.pack(side='left', fill='both', expand=True)
        tsrs_scrollbar.pack(side='right', fill='y')

        # TSRS seçim olayı
        self.tsrs_sdg_tree.bind('<Button-1>', self.on_tsrs_sdg_select)

        # Sağ panel - SDG Eşleştirmeleri
        right_panel = tk.Frame(self.tsrs_sdg_frame, bg='white', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True)

        # SDG başlığı
        sdg_header = tk.Frame(right_panel, bg='#27ae60', height=40)
        sdg_header.pack(fill='x')
        sdg_header.pack_propagate(False)

        tk.Label(sdg_header, text="SDG Eşleştirmeleri",
                font=('Segoe UI', 12, 'bold'), fg='white', bg='#27ae60').pack(expand=True)

        # SDG listesi
        sdg_frame = tk.Frame(right_panel, bg='white')
        sdg_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.sdg_tree = ttk.Treeview(sdg_frame, columns=('sdg_goal', 'sdg_target', 'relationship'), show='headings', height=15)
        self.sdg_tree.heading('sdg_goal', text='SDG Hedef')
        self.sdg_tree.heading('sdg_target', text='SDG Alt Hedef')
        self.sdg_tree.heading('relationship', text='İlişki Türü')

        self.sdg_tree.column('sdg_goal', width=120)
        self.sdg_tree.column('sdg_target', width=120)
        self.sdg_tree.column('relationship', width=100)

        # SDG header tooltips
        try:
            bind_treeview_header_tooltips(self.sdg_tree, {
                'SDG Hedef': 'Sürdürülebilir Kalkınma Amacı; ana hedef.',
                'SDG Alt Hedef': 'Hedefin alt kırılımı; spesifik sonuç.',
                'İlişki Türü': 'TSRS-SDG ilişkisi: Doğrudan, Dolaylı, Kapsamlı.'
            })
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # SDG scrollbar
        sdg_scrollbar = ttk.Scrollbar(sdg_frame, orient="vertical", command=self.sdg_tree.yview)
        self.sdg_tree.configure(yscrollcommand=sdg_scrollbar.set)

        self.sdg_tree.pack(side='left', fill='both', expand=True)
        sdg_scrollbar.pack(side='right', fill='y')

        # İstatistikler
        stats_frame = tk.Frame(self.tsrs_sdg_frame, bg='#f8f9fa', relief='solid', bd=1)
        stats_frame.pack(fill='x', pady=(10, 0))

        tk.Label(stats_frame, text="TSRS-SDG Eşleştirme İstatistikleri",
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(pady=10)

        self.tsrs_sdg_stats = tk.Label(stats_frame, text="Yükleniyor...",
                                      font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa')
        self.tsrs_sdg_stats.pack(pady=(0, 10))

    def create_integrated_reports_tab(self) -> None:
        """Entegre raporlar sekmesi"""
        content_frame = tk.Frame(self.integrated_reports_frame, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        tk.Label(content_frame, text="TSRS-GRI-SDG Entegre Raporları",
                font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Rapor kartları
        reports_frame = tk.Frame(content_frame, bg='white')
        reports_frame.pack(fill='both', expand=True)

        # Kart 1: Sürdürülebilirlik Dashboard
        card1 = tk.Frame(reports_frame, bg='#f8f9fa', relief='solid', bd=1)
        card1.pack(fill='x', pady=10)

        card1_content = tk.Frame(card1, bg='#f8f9fa')
        card1_content.pack(fill='x', padx=20, pady=15)

        tk.Label(card1_content, text=" Sürdürülebilirlik Dashboard",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')
        tk.Label(card1_content, text="TSRS, GRI ve SDG performansını tek ekranda görüntüleyin",
                font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa').pack(anchor='w')

        tk.Button(card1_content, text="Dashboard Oluştur",
                 font=('Segoe UI', 10), bg='#3498db', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.create_sustainability_dashboard).pack(anchor='w', pady=(10, 0))

        # Kart 2: Eşleştirme Matrisi
        card2 = tk.Frame(reports_frame, bg='#f8f9fa', relief='solid', bd=1)
        card2.pack(fill='x', pady=10)

        card2_content = tk.Frame(card2, bg='#f8f9fa')
        card2_content.pack(fill='x', padx=20, pady=15)

        tk.Label(card2_content, text=" Eşleştirme Matrisi",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')
        tk.Label(card2_content, text="TSRS-GRI-SDG eşleştirmelerini matris formatında görüntüleyin",
                font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa').pack(anchor='w')

        tk.Button(card2_content, text="Matris Oluştur",
                 font=('Segoe UI', 10), bg='#e74c3c', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.create_mapping_matrix).pack(anchor='w', pady=(10, 0))

        # Kart 3: Kapsamlı Rapor
        card3 = tk.Frame(reports_frame, bg='#f8f9fa', relief='solid', bd=1)
        card3.pack(fill='x', pady=10)

        card3_content = tk.Frame(card3, bg='#f8f9fa')
        card3_content.pack(fill='x', padx=20, pady=15)

        tk.Label(card3_content, text=" Kapsamlı Sürdürülebilirlik Raporu",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(anchor='w')
        tk.Label(card3_content, text="TSRS, GRI ve SDG verilerini içeren kapsamlı rapor oluşturun",
                font=('Segoe UI', 10), fg='#7f8c8d', bg='#f8f9fa').pack(anchor='w')

        tk.Button(card3_content, text="Rapor Oluştur",
                 font=('Segoe UI', 10), bg='#27ae60', fg='white',
                 relief='flat', bd=0, cursor='hand2', padx=20, pady=5,
                 command=self.create_comprehensive_report).pack(anchor='w', pady=(10, 0))

    def on_tsrs_select(self, event) -> None:
        """TSRS seçildiğinde GRI eşleştirmelerini göster"""
        selection = self.tsrs_tree.selection()
        if not selection:
            return

        item = self.tsrs_tree.item(selection[0])
        tsrs_code = item['values'][0]

        # GRI eşleştirmelerini yükle
        self.load_gri_mappings(tsrs_code)

    def on_tsrs_sdg_select(self, event) -> None:
        """TSRS seçildiğinde SDG eşleştirmelerini göster"""
        selection = self.tsrs_sdg_tree.selection()
        if not selection:
            return

        item = self.tsrs_sdg_tree.item(selection[0])
        tsrs_code = item['values'][0]

        # SDG eşleştirmelerini yükle
        self.load_sdg_mappings(tsrs_code)

    def load_gri_mappings(self, tsrs_code) -> None:
        """GRI eşleştirmelerini yükle"""
        # Mevcut eşleştirmeleri temizle
        for item in self.gri_tree.get_children():
            self.gri_tree.delete(item)

        try:
            conn = sqlite3.connect(self.tsrs_manager.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT gri_standard, gri_disclosure, relationship_type, notes
                FROM map_tsrs_gri
                WHERE tsrs_standard_code = ?
                ORDER BY gri_standard, gri_disclosure
            """, (tsrs_code,))

            for row in cursor.fetchall():
                self.gri_tree.insert('', 'end', values=(
                    row[0], row[1] or '', row[2], row[3] or ''
                ))

            conn.close()

        except Exception as e:
            logging.error(f"GRI eşleştirmeleri yüklenirken hata: {e}")

    def load_sdg_mappings(self, tsrs_code) -> None:
        """SDG eşleştirmelerini yükle"""
        # Mevcut eşleştirmeleri temizle
        for item in self.sdg_tree.get_children():
            self.sdg_tree.delete(item)

        try:
            conn = sqlite3.connect(self.tsrs_manager.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT tsd.sdg_goal_id, tsd.sdg_target_id, tsd.relationship_type, tsd.notes,
                       sg.title as goal_title, st.title as target_title
                FROM map_tsrs_sdg tsd
                LEFT JOIN sdg_goals sg ON tsd.sdg_goal_id = sg.id
                LEFT JOIN sdg_targets st ON tsd.sdg_target_id = st.id
                WHERE tsd.tsrs_standard_code = ?
                ORDER BY tsd.sdg_goal_id, tsd.sdg_target_id
            """, (tsrs_code,))

            for row in cursor.fetchall():
                goal_text = f"SDG {row[0]}" + (f": {row[4]}" if row[4] else "")
                target_text = f"{row[1]}" + (f": {row[5]}" if row[5] else "") if row[1] else ""

                self.sdg_tree.insert('', 'end', values=(
                    goal_text, target_text, row[2], row[3] or ''
                ))

            conn.close()

        except Exception as e:
            logging.error(f"SDG eşleştirmeleri yüklenirken hata: {e}")

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_tsrs_standards()
        self.update_stats()

    def load_tsrs_standards(self) -> None:
        """TSRS standartlarını yükle"""
        # TSRS-GRI sekmesi için
        for item in self.tsrs_tree.get_children():
            self.tsrs_tree.delete(item)

        # TSRS-SDG sekmesi için
        for item in self.tsrs_sdg_tree.get_children():
            self.tsrs_sdg_tree.delete(item)

        try:
            standards = self.tsrs_manager.get_tsrs_standards()

            for standard in standards:
                # TSRS-GRI sekmesi
                self.tsrs_tree.insert('', 'end', values=(
                    standard['code'], standard['title'], standard['category']
                ))

                # TSRS-SDG sekmesi
                self.tsrs_sdg_tree.insert('', 'end', values=(
                    standard['code'], standard['title'], standard['category']
                ))

        except Exception as e:
            logging.error(f"TSRS standartları yüklenirken hata: {e}")

    def update_stats(self) -> None:
        """İstatistikleri güncelle"""
        try:
            conn = sqlite3.connect(self.tsrs_manager.db_path)
            cursor = conn.cursor()

            # TSRS-GRI istatistikleri
            cursor.execute("SELECT COUNT(*) FROM map_tsrs_gri")
            tsrs_gri_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT tsrs_standard_code) FROM map_tsrs_gri")
            tsrs_gri_standards = cursor.fetchone()[0]

            self.tsrs_gri_stats.config(text=f"Toplam Eşleştirme: {tsrs_gri_count} | Eşleştirilen TSRS Standart: {tsrs_gri_standards}")

            # TSRS-SDG istatistikleri
            cursor.execute("SELECT COUNT(*) FROM map_tsrs_sdg")
            tsrs_sdg_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT tsrs_standard_code) FROM map_tsrs_sdg")
            tsrs_sdg_standards = cursor.fetchone()[0]

            self.tsrs_sdg_stats.config(text=f"Toplam Eşleştirme: {tsrs_sdg_count} | Eşleştirilen TSRS Standart: {tsrs_sdg_standards}")

            conn.close()

        except Exception as e:
            logging.error(f"İstatistikler güncellenirken hata: {e}")

    def create_sustainability_dashboard(self) -> None:
        try:
            win = tk.Toplevel(self.parent)
            win.title("Sürdürülebilirlik Dashboard")
            win.geometry("800x400")
            win.configure(bg='white')
            top = tk.Frame(win, bg='white')
            top.pack(fill='x', padx=15, pady=10)
            tk.Label(top, text="TSRS Eşleştirme İstatistikleri", font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w')
            grid = tk.Frame(win, bg='white')
            grid.pack(fill='both', expand=True, padx=15, pady=10)
            def query_stats():
                conn = sqlite3.connect(self.tsrs_manager.db_path)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM map_tsrs_gri")
                tsrs_gri_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(DISTINCT tsrs_standard_code) FROM map_tsrs_gri")
                tsrs_gri_standards = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM map_tsrs_sdg")
                tsrs_sdg_count = cur.fetchone()[0]
                cur.execute("SELECT COUNT(DISTINCT tsrs_standard_code) FROM map_tsrs_sdg")
                tsrs_sdg_standards = cur.fetchone()[0]
                conn.close()
                return [
                    ("TSRS-GRI Toplam Eşleştirme", tsrs_gri_count),
                    ("TSRS-GRI Eşleşen Standart", tsrs_gri_standards),
                    ("TSRS-SDG Toplam Eşleştirme", tsrs_sdg_count),
                    ("TSRS-SDG Eşleşen Standart", tsrs_sdg_standards),
                ]

            cards_data = query_stats()
            value_labels = []
            for i, (title, value) in enumerate(cards_data):
                frame = tk.Frame(grid, bg='#f7f9fc', relief='groove', bd=1)
                frame.grid(row=i//2, column=i%2, sticky='nsew', padx=10, pady=10)
                tk.Label(frame, text=title, font=('Segoe UI', 12, 'bold'), bg='#f7f9fc').pack(pady=(15,5))
                val_label = tk.Label(frame, text=str(value), font=('Segoe UI', 20, 'bold'), fg='#2c3e50', bg='#f7f9fc')
                val_label.pack(pady=(0,15))
                value_labels.append(val_label)
            grid.grid_columnconfigure(0, weight=1)
            grid.grid_columnconfigure(1, weight=1)

            def refresh():
                data = query_stats()
                for i, (_, value) in enumerate(data):
                    value_labels[i].config(text=str(value))

            tk.Button(top, text="Yenile", bg='#3498db', fg='white', relief='flat', padx=10, pady=5, command=refresh).pack(side='right')
        except Exception as e:
            messagebox.showerror("Hata", f"Dashboard oluşturulamadı: {e}")

    def create_mapping_matrix(self) -> None:
        """Eşleştirme matrisi oluştur"""
        try:
            win = tk.Toplevel(self.parent)
            win.title("TSRS-GRI-SDG Eşleştirme Matrisi")
            win.geometry("900x600")
            win.configure(bg='white')

            # Üst filtre barı
            filter_frame = tk.Frame(win, bg='white')
            filter_frame.pack(fill='x', padx=15, pady=10)

            tk.Label(filter_frame, text="TSRS Standart:", font=('Segoe UI', 10), bg='white').pack(side='left')
            standards = self.tsrs_manager.get_tsrs_standards()
            codes = ['(Tümü)'] + [s['code'] for s in standards]
            selected_code = tk.StringVar(value='(Tümü)')
            combo = ttk.Combobox(filter_frame, values=codes, textvariable=selected_code, state='readonly', width=20)
            combo.pack(side='left', padx=10)

            def refresh() -> None:
                code = None if selected_code.get() == '(Tümü)' else selected_code.get()
                # GRI
                for item in gri_tree.get_children():
                    gri_tree.delete(item)
                gri_mappings = self.tsrs_manager.get_tsrs_gri_mappings(code)
                for m in gri_mappings:
                    gri_tree.insert('', 'end', values=(
                        m.get('tsrs_standard_code',''), m.get('tsrs_indicator_code',''),
                        m.get('gri_standard',''), m.get('gri_disclosure') or '',
                        m.get('relationship_type',''), m.get('notes') or ''
                    ))
                # SDG
                for item in sdg_tree.get_children():
                    sdg_tree.delete(item)
                sdg_mappings = self.tsrs_manager.get_tsrs_sdg_mappings(code)
                for m in sdg_mappings:
                    sdg_tree.insert('', 'end', values=(
                        m.get('tsrs_standard_code',''), m.get('tsrs_indicator_code',''),
                        m.get('sdg_goal_id',''), m.get('sdg_target_id') or '',
                        m.get('relationship_type',''), m.get('notes') or ''
                    ))

            tk.Button(filter_frame, text="Yenile", font=('Segoe UI', 10), bg='#3498db', fg='white', relief='flat', padx=15, command=refresh).pack(side='left', padx=10)

            # Ana içerik: iki sütunlu matris
            content = tk.Frame(win, bg='white')
            content.pack(fill='both', expand=True, padx=15, pady=(0, 15))

            left = tk.Frame(content, bg='white')
            left.pack(side='left', fill='both', expand=True, padx=(0, 10))
            tk.Label(left, text="TSRS ↔ GRI", font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')
            gri_tree = ttk.Treeview(left, columns=('tsrs_code','tsrs_indicator','gri_standard','gri_disclosure','relationship','notes'), show='headings')
            for col, text, w in [
                ('tsrs_code','TSRS Standart',120), ('tsrs_indicator','TSRS Gösterge',140),
                ('gri_standard','GRI Standard',120), ('gri_disclosure','GRI Disclosure',120),
                ('relationship','İlişki Türü',100), ('notes','Notlar',160)
            ]:
                gri_tree.heading(col, text=text)
                gri_tree.column(col, width=w, anchor='w')
            gri_tree.pack(fill='both', expand=True, pady=(5,0))

            right = tk.Frame(content, bg='white')
            right.pack(side='right', fill='both', expand=True)
            tk.Label(right, text="TSRS ↔ SDG", font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')
            sdg_tree = ttk.Treeview(right, columns=('tsrs_code','tsrs_indicator','sdg_goal','sdg_target','relationship','notes'), show='headings')
            for col, text, w in [
                ('tsrs_code','TSRS Standart',120), ('tsrs_indicator','TSRS Gösterge',140),
                ('sdg_goal','SDG Hedef',100), ('sdg_target','SDG Alt Hedef',120),
                ('relationship','İlişki Türü',100), ('notes','Notlar',160)
            ]:
                sdg_tree.heading(col, text=text)
                sdg_tree.column(col, width=w, anchor='w')
            sdg_tree.pack(fill='both', expand=True, pady=(5,0))

            # İlk yükleme
            refresh()
        except Exception as e:
            messagebox.showerror("Hata", f"Eşleştirme matrisi oluşturulamadı: {e}")

    def create_comprehensive_report(self) -> None:
        """Kapsamlı rapor oluştur"""
        try:
            # Özet verileri topla
            conn = sqlite3.connect(self.tsrs_manager.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM tsrs_standards")
            total_standards = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tsrs_indicators")
            total_indicators = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM map_tsrs_gri")
            gri_maps = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM map_tsrs_sdg")
            sdg_maps = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(DISTINCT indicator_id)
                FROM tsrs_responses
                WHERE company_id = ? AND response_value IS NOT NULL
            """, (self.company_id,))
            answered = cursor.fetchone()[0]
            conn.close()

            # Rapor penceresi
            win = tk.Toplevel(self.parent)
            win.title("Kapsamlı Sürdürülebilirlik Raporu")
            win.geometry("700x500")
            win.configure(bg='white')

            tk.Label(win, text="TSRS-GRI-SDG Kapsamlı Özet", font=('Segoe UI', 16, 'bold'), bg='white').pack(pady=15)
            info = tk.Frame(win, bg='white')
            info.pack(fill='x', padx=20)

            def row(label, value) -> None:
                r = tk.Frame(info, bg='white')
                r.pack(fill='x', pady=4)
                tk.Label(r, text=label, font=('Segoe UI', 11, 'bold'), bg='white', fg='#2c3e50').pack(side='left')
                tk.Label(r, text=value, font=('Segoe UI', 11), bg='white', fg='#7f8c8d').pack(side='right')

            row("Toplam TSRS Standart", str(total_standards))
            row("Toplam TSRS Gösterge", str(total_indicators))
            row("GRI Eşleştirme Sayısı", str(gri_maps))
            row("SDG Eşleştirme Sayısı", str(sdg_maps))
            row("Yanıtlanan Gösterge (Şirket)", str(answered))

            # Dışa aktar (HTML)
            def export_html() -> None:
                html = f"""
                <html><head><meta charset='utf-8'><title>TSRS Entegre Rapor</title></head>
                <body>
                <h1>TSRS-GRI-SDG Kapsamlı Özet</h1>
                <ul>
                  <li>Toplam TSRS Standart: {total_standards}</li>
                  <li>Toplam TSRS Gösterge: {total_indicators}</li>
                  <li>GRI Eşleştirme Sayısı: {gri_maps}</li>
                  <li>SDG Eşleştirme Sayısı: {sdg_maps}</li>
                  <li>Yanıtlanan Gösterge (Şirket): {answered}</li>
                </ul>
                <p>Oluşturulma: {datetime.now().isoformat()}</p>
                </body></html>
                """
                out_dir = os.path.join(os.path.dirname(self.tsrs_manager.db_path), 'reports')
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, 'tsrs_integrated_report.html')
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                messagebox.showinfo("Rapor Kaydedildi", f"Rapor kaydedildi:\n{out_path}")

            btns = tk.Frame(win, bg='white')
            btns.pack(pady=20)
            tk.Button(btns, text="HTML Olarak Dışa Aktar", font=('Segoe UI', 10), bg='#27ae60', fg='white', relief='flat', padx=15, command=export_html).pack()
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulamadı: {e}")
