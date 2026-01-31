#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESG Konsolide Dashboard
Su, karbon, atık, enerji, biyoçeşitlilik, İK/İSG, etik-uyum metriklerini 
E/S/G sütunlarına toplayan konsolide görünüm
"""

import logging
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from config.database import DB_PATH


class ESGConsolidatedDashboard:
    """ESG Konsolide Dashboard"""

    def __init__(self, parent, company_id: int, db_path: str) -> None:
        self.parent = parent
        self.company_id = company_id
        self.db_path = db_path

        # Tema renkleri
        self.colors = {
            'E': '#10b981',  # Yeşil - Çevre
            'S': '#f59e0b',  # Turuncu - Sosyal
            'G': '#3b82f6',  # Mavi - Yönetişim
            'overall': '#6366f1',  # Mor - Genel
            'bg': '#f0f2f5', # Standart arka plan
            'card_bg': 'white',
            'text': '#2c3e50',
            'border': '#e2e8f0'
        }

        self.setup_ui()
        self.load_consolidated_data()

    def setup_ui(self) -> None:
        """UI oluştur"""
        # Ana container (scrollable)
        outer = tk.Frame(self.parent, bg=self.colors['bg'])
        outer.pack(fill='both', expand=True)
        canvas = tk.Canvas(outer, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient='vertical', command=canvas.yview)
        main_frame = tk.Frame(canvas, bg=self.colors['bg'])
        main_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=main_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Başlık
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill='x', padx=20, pady=(0, 20))

        tk.Label(header_frame, text="ESG Konsolide Dashboard",
                font=('Segoe UI', 20, 'bold'), fg='#1e293b',
                bg=self.colors['bg']).pack(side='left')

        # Filtreler
        filter_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        filter_frame.pack(side='right', padx=10)

        # Yıl
        tk.Label(filter_frame, text="Yıl:", font=('Segoe UI', 10),
                bg=self.colors['bg']).pack(side='left', padx=5)

        current_year = datetime.now().year
        years = ['Tümü'] + [str(y) for y in range(current_year, current_year - 5, -1)]
        self.period_var = tk.StringVar(value='Tümü') # Varsayılan Tümü olsun
        
        period_combo = ttk.Combobox(filter_frame, textvariable=self.period_var,
                                   values=years, width=10, state='readonly')
        period_combo.pack(side='left', padx=5)
        period_combo.bind('<<ComboboxSelected>>', lambda e: self.load_consolidated_data())

        # Tedarikçi
        tk.Label(filter_frame, text="Tedarikçi:", font=('Segoe UI', 10),
                bg=self.colors['bg']).pack(side='left', padx=5)
        
        self.supplier_var = tk.StringVar(value='Tümü')
        self.supplier_cb = ttk.Combobox(filter_frame, textvariable=self.supplier_var, width=20)
        self.supplier_cb.pack(side='left', padx=5)
        self.supplier_cb.set('Tümü')
        self.supplier_cb.bind('<<ComboboxSelected>>', lambda e: self.load_consolidated_data())
        
        # Filtreleri Temizle
        tk.Button(filter_frame, text="Temizle", command=self._reset_filters,
                 font=('Segoe UI', 9), bg='#64748b', fg='white').pack(side='left', padx=5)

        # Yenile butonu
        refresh_btn = tk.Button(header_frame, text="Yenile",
                               font=('Segoe UI', 10, 'bold'), fg='white',
                               bg='#10b981', relief='flat', cursor='hand2',
                               command=self.load_consolidated_data, padx=15, pady=8)
        refresh_btn.pack(side='right')

        # Skor kartları
        self.create_score_cards(main_frame)

        # Detay tablosu
        self.create_detail_table(main_frame)

        # Trend grafiği
        self.create_trend_chart(main_frame)

        # Risk göstergeleri
        self.create_risk_indicators(main_frame)

    def create_score_cards(self, parent) -> None:
        """Skor kartları oluştur"""
        cards_frame = tk.Frame(parent, bg=self.colors['bg'])
        cards_frame.pack(fill='x', padx=20, pady=(0, 20))

        self.score_vars = {}
        self.trend_vars = {}

        # E, S, G ve Genel skor kartları
        scores = [
            ('E', 'Çevresel', 'E'),
            ('S', 'Sosyal', 'S'),
            ('G', 'Yönetişim', 'G'),
            ('overall', 'Genel ESG', 'overall')
        ]

        for i, (key, title, color_key) in enumerate(scores):
            card = self.create_score_card(cards_frame, key, title, color_key)
            card.pack(side='left', fill='x', expand=True, padx=(0, 8) if i < len(scores) - 1 else 0)

    def create_score_card(self, parent, key: str, title: str, color_key: str) -> None:
        """Tek bir skor kartı oluştur"""
        card = tk.Frame(parent, bg=self.colors[color_key], relief='raised', bd=2)

        # İkon ve başlık
        header_frame = tk.Frame(card, bg=self.colors[color_key])
        header_frame.pack(fill='x', padx=10, pady=(10, 4))

        icons = {'E': '', 'S': '', 'G': '️', 'overall': ''}
        icon = icons.get(key, '')

        tk.Label(header_frame, text=icon, font=('Segoe UI', 20),
                bg=self.colors[color_key]).pack(side='left')

        tk.Label(header_frame, text=title, font=('Segoe UI', 11, 'bold'),
                fg='white', bg=self.colors[color_key]).pack(side='left', padx=(10, 0))

        # Skor
        self.score_vars[key] = tk.StringVar(value="-")
        score_label = tk.Label(card, textvariable=self.score_vars[key],
                              font=('Segoe UI', 24, 'bold'), fg='white',
                              bg=self.colors[color_key])
        score_label.pack(pady=(4, 4))

        # Trend
        self.trend_vars[key] = tk.StringVar(value="")
        trend_label = tk.Label(card, textvariable=self.trend_vars[key],
                              font=('Segoe UI', 9), fg='white',
                              bg=self.colors[color_key])
        trend_label.pack(pady=(0, 8))

        return card

    def create_detail_table(self, parent) -> None:
        """Detay tablosu oluştur"""
        table_frame = tk.LabelFrame(parent, text=" Modül Bazlı Detaylar",
                                   font=('Segoe UI', 12, 'bold'), fg=self.colors['text'],
                                   bg=self.colors['card_bg'])
        table_frame.pack(fill='both', expand=True, padx=12, pady=(0, 12))

        # Treeview
        columns = ('Modül', 'Kategori', 'Skor', 'Durum', 'Katkı', 'Son Güncelleme')
        self.detail_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)

        # Kolon başlıkları
        for col in columns:
            self.detail_tree.heading(col, text=col)
            self.detail_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=scrollbar.set)

        self.detail_tree.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        scrollbar.pack(side='right', fill='y', pady=8)

    def create_trend_chart(self, parent) -> None:
        """Trend grafiği oluştur"""
        chart_frame = tk.LabelFrame(parent, text=" ESG Trend Analizi",
                                   font=('Segoe UI', 12, 'bold'), fg=self.colors['text'],
                                   bg=self.colors['card_bg'])
        chart_frame.pack(fill='x', padx=12, pady=(0, 12))

        # Basit trend gösterimi (gerçek grafik için matplotlib kullanılabilir)
        trend_canvas = tk.Canvas(chart_frame, height=160, bg='white', highlightthickness=0)
        trend_canvas.pack(fill='x', padx=8, pady=8)

        self.trend_canvas = trend_canvas

    def create_risk_indicators(self, parent) -> None:
        """Risk göstergeleri oluştur"""
        risk_frame = tk.LabelFrame(parent, text="️ Risk Göstergeleri",
                                  font=('Segoe UI', 12, 'bold'), fg=self.colors['text'],
                                  bg=self.colors['card_bg'])
        risk_frame.pack(fill='x', padx=12, pady=(0, 8))

        # Risk kartları
        risks_container = tk.Frame(risk_frame, bg='white')
        risks_container.pack(fill='x', padx=8, pady=8)

        self.risk_labels = {}
        risk_types = [
            ('Yüksek Risk', '#ef4444'),
            ('Orta Risk', '#f59e0b'),
            ('Düşük Risk', '#10b981'),
            ('İzleme Gerekli', '#6b7280')
        ]

        for risk_type, color in risk_types:
            risk_card = tk.Frame(risks_container, bg=color, relief='solid', bd=1)
            risk_card.pack(side='left', fill='x', expand=True, padx=8)

            tk.Label(risk_card, text=risk_type, font=('Segoe UI', 10, 'bold'),
                    fg='white', bg=color).pack(pady=(8, 4))

            self.risk_labels[risk_type] = tk.StringVar(value="0")
            tk.Label(risk_card, textvariable=self.risk_labels[risk_type],
                    font=('Segoe UI', 18, 'bold'), fg='white', bg=color).pack(pady=(0, 8))

    def load_consolidated_data(self) -> None:
        """Konsolide verileri yükle"""
        try:
            # Tedarikçi listesini güncelle (ilk açılışta veya boşsa)
            if hasattr(self, 'supplier_cb'):
                current_values = self.supplier_cb['values']
                if not current_values or len(current_values) <= 1: # Sadece Tümü varsa veya boşsa
                    suppliers = self._get_all_suppliers()
                    self.supplier_cb['values'] = ['Tümü'] + suppliers

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Dönem filtresi
            year = None
            if hasattr(self, 'period_var'):
                val = self.period_var.get()
                if val != 'Tümü':
                    year = val

            # Tedarikçi filtresi
            supplier = None
            if hasattr(self, 'supplier_var'):
                val = self.supplier_var.get()
                if val != 'Tümü':
                    supplier = val

            # E (Çevresel) skorları topla
            e_score = self.calculate_environmental_score(cursor, year, supplier)

            # S (Sosyal) skorları topla
            s_score = self.calculate_social_score(cursor, year, supplier)

            # G (Yönetişim) skorları topla
            g_score = self.calculate_governance_score(cursor, year, supplier)

            # Genel ESG skoru
            overall_score = (e_score + s_score + g_score) / 3

            # Skorları güncelle
            self.score_vars['E'].set(f"{e_score:.1f}")
            self.score_vars['S'].set(f"{s_score:.1f}")
            self.score_vars['G'].set(f"{g_score:.1f}")
            self.score_vars['overall'].set(f"{overall_score:.1f}")



            # Trend göstergeleri (örnek)
            self.trend_vars['E'].set("↑ +2.3% (son ay)")
            self.trend_vars['S'].set("↑ +1.5% (son ay)")
            self.trend_vars['G'].set("→ 0.0% (son ay)")
            self.trend_vars['overall'].set("↑ +1.3% (son ay)")

            # Detay tablosunu doldur
            self.populate_detail_table(cursor, e_score, s_score, g_score, year, supplier)

            # Risk göstergelerini güncelle
            self.update_risk_indicators(cursor)

            # Trend grafiğini çiz
            self.draw_trend_chart()

            conn.close()

        except Exception as e:
            messagebox.showerror("Hata", f"Konsolide veriler yüklenirken hata: {e}")
            logging.error(f"Konsolide veri yükleme hatası: {e}")

    def calculate_environmental_score(self, cursor, year: str = None, supplier: str = None) -> float:
        """Çevresel skor hesapla"""
        try:
            # Karbon modülü
            carbon_score = self.get_module_score(cursor, 'carbon', year, supplier)

            # Su modülü
            water_score = self.get_module_score(cursor, 'water', year, supplier)

            # Atık modülü
            waste_score = self.get_module_score(cursor, 'waste', year, supplier)

            # Enerji modülü
            energy_score = self.get_module_score(cursor, 'energy', year, supplier)

            # Biyoçeşitlilik (varsa)
            biodiversity_score = self.get_module_score(cursor, 'biodiversity', year, supplier)

            # Ortalama hesapla
            scores = [s for s in [carbon_score, water_score, waste_score, energy_score, biodiversity_score] if s > 0]
            return sum(scores) / len(scores) if scores else 0.0

        except Exception as e:
            logging.error(f"Çevresel skor hesaplama hatası: {e}")
            return 0.0

    def calculate_social_score(self, cursor, year: str = None, supplier: str = None) -> float:
        """Sosyal skor hesapla"""
        try:
            # İK/İSG modülü
            hr_score = self.get_module_score(cursor, 'human_resources', year, supplier)

            # Tedarik zinciri
            supply_chain_score = self.get_module_score(cursor, 'supply_chain', year, supplier)

            # Toplum katılımı
            community_score = self.get_module_score(cursor, 'community', year, supplier)

            # Ortalama hesapla
            scores = [s for s in [hr_score, supply_chain_score, community_score] if s > 0]
            return sum(scores) / len(scores) if scores else 0.0

        except Exception as e:
            logging.error(f"Sosyal skor hesaplama hatası: {e}")
            return 0.0

    def calculate_governance_score(self, cursor, year: str = None, supplier: str = None) -> float:
        """Yönetişim skoru hesapla"""
        try:
            # Etik ve uyum
            ethics_score = self.get_module_score(cursor, 'ethics', year, supplier)

            # Risk yönetimi
            risk_score = self.get_module_score(cursor, 'risk_management', year, supplier)

            # Kurumsal yönetim
            corporate_gov_score = self.get_module_score(cursor, 'corporate_governance', year, supplier)

            # Ortalama hesapla
            scores = [s for s in [ethics_score, risk_score, corporate_gov_score] if s > 0]
            return sum(scores) / len(scores) if scores else 0.0

        except Exception as e:
            logging.error(f"Yönetişim skoru hesaplama hatası: {e}")
            return 0.0

    def get_module_score(self, cursor, module_name: str, year: str = None, supplier: str = None) -> float:
        """Modül skorunu al"""
        try:
            # Modüle göre farklı tablolardan skor hesapla
            if module_name == 'carbon':
                # Karbon modülü skorlaması - Scope 1 emisyonlarını baz al
                try:
                    query = """
                        SELECT COUNT(*) as total, 
                               SUM(CASE WHEN total_emissions > 0 THEN 1 ELSE 0 END) as completed
                        FROM scope1_emissions 
                        WHERE company_id = ?
                    """
                    params = [self.company_id]
                    if year:
                        query += " AND year = ?"
                        params.append(year)
                    if supplier:
                        query += " AND supplier = ?"
                        params.append(supplier)
                        
                    cursor.execute(query, params)
                    row = cursor.fetchone()
                    if row and row[0] > 0:
                        return (row[1] / row[0]) * 100
                except sqlite3.OperationalError:
                     # Tablo yoksa 0 dön
                     return 0.0

            elif module_name == 'water':
                # Su modülü skorlaması
                query = """
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN total_water > 0 THEN 1 ELSE 0 END) as completed
                    FROM water_consumption 
                    WHERE company_id = ?
                """
                params = [self.company_id]
                if year:
                    query += " AND period LIKE ?"
                    params.append(f"{year}%")
                if supplier:
                    query += " AND supplier = ?"
                    params.append(supplier)
                    
                cursor.execute(query, params)
                row = cursor.fetchone()
                if row and row[0] > 0:
                    return (row[1] / row[0]) * 100

            elif module_name == 'waste':
                # Atık modülü skorlaması
                query = """
                    SELECT COUNT(*) as total,
                           SUM(CASE WHEN quantity > 0 THEN 1 ELSE 0 END) as completed
                    FROM waste_records 
                    WHERE company_id = ?
                """
                params = [self.company_id]
                if year:
                    query += " AND period LIKE ?"
                    params.append(f"{year}%")
                if supplier:
                    query += " AND supplier = ?"
                    params.append(supplier)
                    
                cursor.execute(query, params)
                row = cursor.fetchone()
                if row and row[0] > 0:
                    return (row[1] / row[0]) * 100

            elif module_name == 'supply_chain':
                # Tedarik zinciri skorlaması
                cursor.execute("""
                    SELECT AVG(total_score) 
                    FROM supplier_assessments 
                    WHERE company_id = ?
                """, (self.company_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    return float(row[0])

            # Diğer modüller için
            elif module_name == 'energy':
                # Enerji tüketimi
                try:
                    # Önce detaylı tabloyu kontrol et
                    query = "SELECT COUNT(*) FROM energy_consumption_records WHERE company_id = ?"
                    params = [self.company_id]
                    
                    if year:
                        query += " AND measurement_date LIKE ?"
                        params.append(f"{year}%")
                    
                    if supplier:
                        query += " AND supplier = ?"
                        params.append(supplier)
                        
                    cursor.execute(query, params)
                    row = cursor.fetchone()
                    if row and row[0] > 0:
                        return 100.0
                        
                    # Kayıt yoksa veya filtre sonucu boşsa, eski tabloya bak (sadece filtre yoksa)
                    if not year and not supplier:
                        cursor.execute("SELECT COUNT(*) FROM energy_consumption WHERE company_id = ?", (self.company_id,))
                        row = cursor.fetchone()
                        return 100.0 if row and row[0] > 0 else 0.0
                    
                    return 0.0
                    
                except sqlite3.OperationalError:
                    # Detaylı tablo yoksa eski tabloya bak
                    try:
                        cursor.execute("SELECT COUNT(*) FROM energy_consumption WHERE company_id = ?", (self.company_id,))
                        row = cursor.fetchone()
                        return 100.0 if row and row[0] > 0 else 0.0
                    except sqlite3.OperationalError:
                        return 0.0

            elif module_name == 'human_resources':
                # İK istatistikleri
                try:
                    cursor.execute("SELECT COUNT(*) FROM employee_statistics WHERE company_id = ?", (self.company_id,))
                    row = cursor.fetchone()
                    return 100.0 if row and row[0] > 0 else 0.0
                except sqlite3.OperationalError:
                    return 0.0

            elif module_name == 'ethics':
                # Etik ihlalleri (takip ediliyorsa tam puan varsayalım)
                try:
                    cursor.execute("SELECT COUNT(*) FROM ethics_violations WHERE company_id = ?", (self.company_id,))
                    row = cursor.fetchone()
                    return 100.0 if row and row[0] > 0 else 0.0 # Veya ihlal sayısına göre düşebilir
                except sqlite3.OperationalError:
                    return 0.0

            elif module_name == 'risk_management':
                # Risk yönetimi
                try:
                    cursor.execute("SELECT COUNT(*) FROM sustainability_risks WHERE company_id = ?", (self.company_id,))
                    row = cursor.fetchone()
                    return 100.0 if row and row[0] > 0 else 0.0
                except sqlite3.OperationalError:
                    return 0.0

            # Bilinmeyen modül
            return 0.0

        except Exception as e:
            # Hata durumunda logla ama 0 dön (program çökmesin)
            logging.error(f"Modül skoru alma hatası ({module_name}): {e}")
            return 0.0

    def _get_module_status(self, cursor, table_name: str) -> str:
        """Modül durumunu kontrol et"""
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                return "Yüklü Değil"
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE company_id = ?", (self.company_id,))
            count = cursor.fetchone()[0]
            return "Aktif" if count > 0 else "Veri Yok"
        except Exception:
            return "Hata"

    def populate_detail_table(self, cursor, e_score: float, s_score: float, g_score: float, year: str = None, supplier: str = None) -> None:
        """Detay tablosunu doldur"""
        # Tabloyu temizle
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

        # Modül detayları
        # (Ad, Kategori, Skor, Durum, Katkı, Tarih)
        modules = [
            ('Karbon Ayak İzi', 'E', self.get_module_score(cursor, 'carbon', year, supplier), 
             self._get_module_status(cursor, 'scope1_emissions'), f'{e_score * 0.3:.1f}%', datetime.now().strftime('%Y-%m-%d')),
            
            ('Su Yönetimi', 'E', self.get_module_score(cursor, 'water', year, supplier), 
             self._get_module_status(cursor, 'water_consumption'), f'{e_score * 0.25:.1f}%', datetime.now().strftime('%Y-%m-%d')),
            
            ('Atık Yönetimi', 'E', self.get_module_score(cursor, 'waste', year, supplier), 
             self._get_module_status(cursor, 'waste_records'), f'{e_score * 0.25:.1f}%', datetime.now().strftime('%Y-%m-%d')),
            
            ('Enerji Yönetimi', 'E', self.get_module_score(cursor, 'energy', year, supplier), 
             self._get_module_status(cursor, 'energy_consumption'), f'{e_score * 0.2:.1f}%', '-'),
            
            ('İK/İSG', 'S', self.get_module_score(cursor, 'human_resources', year, supplier), 
             self._get_module_status(cursor, 'employee_statistics'), f'{s_score * 0.4:.1f}%', '-'),
            
            ('Tedarik Zinciri', 'S', self.get_module_score(cursor, 'supply_chain', year, supplier), 
             self._get_module_status(cursor, 'supplier_assessments'), f'{s_score * 0.6:.1f}%', datetime.now().strftime('%Y-%m-%d')),
            
            ('Etik ve Uyum', 'G', self.get_module_score(cursor, 'ethics', year, supplier), 
             self._get_module_status(cursor, 'ethics_violations'), f'{g_score * 0.5:.1f}%', '-'),
            
            ('Risk Yönetimi', 'G', self.get_module_score(cursor, 'risk_management', year, supplier), 
             self._get_module_status(cursor, 'sustainability_risks'), f'{g_score * 0.5:.1f}%', '-'),
        ]

        for module in modules:
            self.detail_tree.insert('', 'end', values=module)

    def _reset_filters(self) -> None:
        """Filtreleri temizle"""
        if hasattr(self, 'period_var'):
            self.period_var.set('Tümü')
        if hasattr(self, 'supplier_var'):
            self.supplier_var.set('Tümü')
        self.load_consolidated_data()

    def _get_all_suppliers(self) -> list:
        """Tüm tedarikçileri getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            suppliers = set()
            
            # Waste
            try:
                cursor.execute("SELECT DISTINCT supplier FROM waste_records WHERE supplier IS NOT NULL AND supplier != ''")
                suppliers.update(row[0] for row in cursor.fetchall())
            except: pass

            # Water
            try:
                cursor.execute("SELECT DISTINCT supplier FROM water_consumption WHERE supplier IS NOT NULL AND supplier != ''")
                suppliers.update(row[0] for row in cursor.fetchall())
            except: pass
            
            # Energy
            try:
                cursor.execute("SELECT DISTINCT supplier FROM energy_consumption WHERE supplier IS NOT NULL AND supplier != ''")
                suppliers.update(row[0] for row in cursor.fetchall())
            except: pass

            # Detailed Energy
            try:
                cursor.execute("SELECT DISTINCT supplier FROM energy_consumption_records WHERE supplier IS NOT NULL AND supplier != ''")
                suppliers.update(row[0] for row in cursor.fetchall())
            except: pass
            
            conn.close()
            return sorted(list(suppliers))
        except:
            return []

    def update_risk_indicators(self, cursor) -> None:
        """Risk göstergelerini güncelle"""
        try:
            # Risk sayılarını hesapla (örnek)
            self.risk_labels['Yüksek Risk'].set("2")
            self.risk_labels['Orta Risk'].set("5")
            self.risk_labels['Düşük Risk'].set("12")
            self.risk_labels['İzleme Gerekli'].set("3")

        except Exception as e:
            logging.error(f"Risk göstergeleri güncelleme hatası: {e}")

    def draw_trend_chart(self) -> None:
        """Trend grafiği çiz"""
        try:
            canvas = self.trend_canvas
            canvas.delete('all')

            # Basit çizgi grafiği
            width = canvas.winfo_width() if canvas.winfo_width() > 1 else 800
            height = 200
            padding = 40

            # Örnek veri noktaları
            months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz']
            e_data = [65, 68, 70, 72, 74, 76]
            s_data = [60, 62, 64, 65, 66, 67]
            g_data = [70, 70, 71, 71, 72, 72]

            # Eksen çizgileri
            canvas.create_line(padding, height - padding, width - padding, height - padding, fill='#e5e7eb', width=2)
            canvas.create_line(padding, padding, padding, height - padding, fill='#e5e7eb', width=2)

            # Veri çizgileri
            self.draw_line_series(canvas, e_data, months, width, height, padding, self.colors['E'], 'E')
            self.draw_line_series(canvas, s_data, months, width, height, padding, self.colors['S'], 'S')
            self.draw_line_series(canvas, g_data, months, width, height, padding, self.colors['G'], 'G')

            # Ay etiketleri
            for i, month in enumerate(months):
                x = padding + (i * (width - 2 * padding) / (len(months) - 1))
                canvas.create_text(x, height - padding + 20, text=month, font=('Segoe UI', 9))

        except Exception as e:
            logging.error(f"Trend grafiği çizme hatası: {e}")

    def draw_line_series(self, canvas, data, labels, width, height, padding, color, label) -> None:
        """Çizgi serisi çiz"""
        try:
            if not data or len(data) < 2:
                return

            # Veri noktalarını normalize et
            max_val = 100
            min_val = 0

            points = []
            for i, value in enumerate(data):
                x = padding + (i * (width - 2 * padding) / (len(data) - 1))
                y = height - padding - ((value - min_val) / (max_val - min_val) * (height - 2 * padding))
                points.extend([x, y])

            # Çizgi çiz
            if len(points) >= 4:
                canvas.create_line(*points, fill=color, width=3, smooth=True)

            # Veri noktaları
            for i in range(0, len(points), 2):
                canvas.create_oval(points[i]-4, points[i+1]-4, points[i]+4, points[i+1]+4,
                                 fill=color, outline='white', width=2)

        except Exception as e:
            logging.error(f"Çizgi serisi çizme hatası: {e}")

# Test fonksiyonu
def test_consolidated_dashboard() -> None:
    """Konsolide dashboard'u test et"""
    root = tk.Tk()
    root.title("ESG Konsolide Dashboard Test")
    root.geometry("1200x800")

    db_path = DB_PATH
    ESGConsolidatedDashboard(root, company_id=1, db_path=db_path)

    root.mainloop()

if __name__ == "__main__":
    test_consolidated_dashboard()
