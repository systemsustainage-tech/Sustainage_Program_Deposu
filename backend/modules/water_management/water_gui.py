#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
SU YÖNETİMİ MODÜLÜ GUI (Tam sürüm)
Su tüketimi kayıtları, su ayak izi hesaplamaları ve raporlama arayüzü.
"""

import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .water_manager import WaterManager
from .water_reporting import WaterReporting
from config.icons import Icons


class WaterGUI:
    """Su Yönetimi Modülü GUI (Yönetici, formlar, listeler ve metrikler ile)"""

    def __init__(self, parent, company_id: int, user_role: str = 'user', db_path: str | None = None) -> None:
        self.parent = parent
        self.company_id = company_id
        self.user_role = user_role  # user, admin, super_admin
        self.is_admin = user_role in ('admin', 'super_admin', '__super__')
        self.lm = LanguageManager()

        # Mappings
        self.type_map = {
            'industrial': self.lm.tr('industrial', 'Endüstriyel'),
            'agricultural': self.lm.tr('agricultural', 'Tarımsal'),
            'domestic': self.lm.tr('domestic', 'Evsel'),
            'process': self.lm.tr('process', 'Proses')
        }
        self.type_map_rev = {v: k for k, v in self.type_map.items()}

        self.source_map = {
            'groundwater': self.lm.tr('groundwater', 'Yeraltı Suyu'),
            'surface_water': self.lm.tr('surface_water', 'Yüzey Suyu'),
            'municipal': self.lm.tr('municipal', 'Şebeke Suyu'),
            'recycled': self.lm.tr('recycled', 'Geri Dönüştürülmüş')
        }
        self.source_map_rev = {v: k for k, v in self.source_map.items()}

        self.method_map = {
            'measurement': self.lm.tr('measurement', 'Ölçüm'),
            'estimate': self.lm.tr('estimate', 'Tahmin'),
            'calculation': self.lm.tr('calculation', 'Hesaplama')
        }
        self.method_map_rev = {v: k for k, v in self.method_map.items()}

        self.quality_map = {
            'high': self.lm.tr('high', 'Yüksek'),
            'medium': self.lm.tr('medium', 'Orta'),
            'low': self.lm.tr('low', 'Düşük')
        }
        self.quality_map_rev = {v: k for k, v in self.quality_map.items()}

        # db_path opsiyonel: verilirse kullan, yoksa mevcut varsayılanlara bırak
        if db_path:
            self.manager = WaterManager(db_path)
            self.reporting = WaterReporting(db_path)
        else:
            self.manager = WaterManager()
            self.reporting = WaterReporting()

        # Durum
        self.periods: list[str] = []
        self.records_tree: ttk.Treeview | None = None
        self.stats_cards: dict[str, Any] = {}
        self.current_view: str | None = None
        # Düzenleme durumları
        self.current_record_id: int | None = None
        self.current_target_id: int | None = None
        self.current_quality_id: int | None = None
        self.current_project_id: int | None = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Su yönetimi arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#f0f2f5')
        header_frame.pack(fill='x', pady=(0, 20))

        title_label = tk.Label(header_frame, text=self.lm.tr('water_title', "Su Yönetimi"),
                               font=('Segoe UI', 20, 'bold'), fg='#1e293b', bg='#f0f2f5')
        title_label.pack(side='left')

        subtitle_label = tk.Label(header_frame, text=self.lm.tr('water_subtitle', "Tüketim Takibi, Su Ayak İzi ve Raporlama"),
                                   font=('Segoe UI', 12), fg='#64748b', bg='#f0f2f5')
        subtitle_label.pack(side='left', padx=(10, 0), pady=(8, 0))

        # Aktif firma adını başlığa ekle (ticari_unvan veya sirket_adi)
        try:
            conn = sqlite3.connect(self.manager.db_path)
            cur = conn.cursor()
            cur.execute("SELECT ticari_unvan, sirket_adi FROM company_info WHERE company_id=?", (self.company_id,))
            row = cur.fetchone()
            conn.close()
            company_name = ''
            if row:
                company_name = (row[0] or '').strip() or (row[1] or '').strip()
            if company_name:
                subtitle_label.configure(text=f"{self.lm.tr('water_subtitle', 'Tüketim Takibi, Su Ayak İzi ve Raporlama')} — {company_name}")
        except Exception as e:
            logging.info(f"[WaterGUI] Firma adı alınamadı: {e}")

        # Geri butonu (sağ üst)
        toolbar = ttk.Frame(header_frame)
        toolbar.pack(side='right', padx=12, pady=12)
        ttk.Button(toolbar, text=self.lm.tr('report_center', ' Rapor Merkezi'), style='Primary.TButton', command=self.open_report_center_water).pack(side='right', padx=6)
        ttk.Button(toolbar, text=self.lm.tr('btn_back', ' ← Geri'), style='Primary.TButton', command=self._go_back).pack(side='right', padx=6)

        # Sol panel - Menü (üstte konumlandırıldı, içerik tam genişlikte)
        left_panel = tk.Frame(main_frame, bg='#ecf0f1')
        left_panel.pack(side='top', fill='x', padx=0, pady=(0, 10))
        left_panel.pack_propagate(False)

        menu_title = tk.Label(left_panel, text=self.lm.tr('water_menu', "Su Yönetimi Menüsü"),
                               font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        menu_title.pack(pady=15)

        menu_buttons = [
            ("", self.lm.tr('menu_dashboard', "Dashboard"), self.build_dashboard),
            ("", self.lm.tr('menu_records', "Kayıtlar"), self.build_records_view),
            ("", self.lm.tr('menu_metrics', "Metrikler"), self.build_metrics_view),
            ("", self.lm.tr('menu_targets', "Hedefler"), self.build_targets_view),
            ("", self.lm.tr('menu_quality', "Kalite İzleme"), self.build_quality_view),
            ("️", self.lm.tr('menu_projects', "Verimlilik Projeleri"), self.build_projects_view),
            ("", self.lm.tr('menu_sdg6', "SDG 6 İlerleme"), self.build_sdg6_view),
            ("", self.lm.tr('menu_reports', "Raporlar"), self.build_reports_view),
        ]

        for icon, text, cmd in menu_buttons:
            btn = ttk.Button(left_panel, text=f"{icon} {text}", style='Primary.TButton', command=cmd)
            btn.pack(fill='x', padx=10, pady=5)

        # İçerik alanı - scrollable
        content_outer = tk.Frame(main_frame, bg='white')
        content_outer.pack(side='top', fill='both', expand=True)
        content_canvas = tk.Canvas(content_outer, bg='white', highlightthickness=0)
        content_scroll = ttk.Scrollbar(content_outer, orient='vertical', command=content_canvas.yview)
        self.content_frame = tk.Frame(content_canvas, bg='white')
        self.content_frame.bind('<Configure>', lambda e: content_canvas.configure(scrollregion=content_canvas.bbox('all')))
        content_canvas.create_window((0, 0), window=self.content_frame, anchor='nw')
        content_canvas.configure(yscrollcommand=content_scroll.set)
        content_canvas.pack(side='left', fill='both', expand=True)
        content_scroll.pack(side='right', fill='y')

        self.content_title = tk.Label(self.content_frame, text=self.lm.tr('water_dashboard', "Su Dashboard"),
                                      font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        self.content_title.pack(pady=10)

        # İlk görünüm
        self.build_dashboard()

    def open_report_center_water(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('su')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for su: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_report_center', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def _clear_content(self) -> None:
        for w in self.content_frame.winfo_children():
            if w is not self.content_title:
                w.destroy()

    # ==================== DASHBOARD ====================
    def build_dashboard(self) -> None:
        self.current_view = 'dashboard'
        self.content_title['text'] = self.lm.tr('water_dashboard', 'Su Dashboard')
        self._clear_content()

        stats_frame = tk.Frame(self.content_frame, bg='white')
        stats_frame.pack(fill='x', padx=15, pady=10)

        cards = [
            (self.lm.tr('total_consumption', "Toplam Tüketim"), "m³", "#3498db", 'total_water'),
            (self.lm.tr('avg_recycling', "Ortalama Geri Dönüşüm"), "%", "#27ae60", 'avg_recycling'),
            (self.lm.tr('avg_efficiency', "Ortalama Verimlilik"), "%", "#16a085", 'avg_efficiency'),
            (self.lm.tr('record_count', "Kayıt Sayısı"), self.lm.tr('count_unit', "adet"), "#8e44ad", 'records_count'),
        ]

        self.stats_cards = {}
        for i, (title, unit, color, key) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=2)
            card.grid(row=0, column=i, padx=8, pady=5, sticky='ew')
            stats_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'), fg='white', bg=color).pack(pady=(10, 3))
            value_lbl = tk.Label(card, text='—', font=('Segoe UI', 16, 'bold'), fg='white', bg=color)
            value_lbl.pack(pady=(0, 10))
            self.stats_cards[key] = (value_lbl, unit)

        self._refresh_dashboard_stats()

        # Hızlı Kayıt Formu (kartların altında görünür veri girişi)
        quick_frame = tk.LabelFrame(self.content_frame, text=self.lm.tr('quick_add_record', 'Hızlı Kayıt Ekle'), bg='white')
        quick_frame.pack(fill='x', padx=15, pady=10)

        def q_add(parent, text, row, col=0, width=20) -> tk.Entry:
            tk.Label(parent, text=text, bg='white').grid(row=row, column=col, sticky='w', padx=5, pady=4)
            ent = tk.Entry(parent, width=width)
            ent.grid(row=row, column=col+1, sticky='w', padx=5, pady=4)
            return ent

        self.quick_period_ent = q_add(quick_frame, self.lm.tr('period_example', 'Dönem (örn. 2024-Q1)'), 0)
        self.quick_total_ent = q_add(quick_frame, self.lm.tr('total_water_m3', 'Toplam Su (m³)'), 0, col=2)
        self.quick_recycle_ent = q_add(quick_frame, self.lm.tr('recycling_rate_percent', 'Geri Dönüşüm Oranı (%)'), 1)
        self.quick_efficiency_ent = q_add(quick_frame, self.lm.tr('efficiency_ratio_percent', 'Verimlilik Oranı (%)'), 1, col=2)

        q_btns = tk.Frame(quick_frame, bg='white')
        q_btns.grid(row=2, column=0, columnspan=4, sticky='e', padx=5, pady=8)
        ttk.Button(q_btns, text=self.lm.tr('quick_save', 'Hızlı Kaydet'), style='Primary.TButton', command=self._quick_add_record).pack(side='left', padx=5)
        ttk.Button(q_btns, text=self.lm.tr('go_to_records', 'Kayıtlar Görünümüne Git'), style='Primary.TButton', command=self.build_records_view).pack(side='left', padx=5)

    def _refresh_dashboard_stats(self) -> None:
        try:
            records = self.manager.get_water_consumption(self.company_id)
            total_water = sum(r.get('total_water', 0) or 0 for r in records)
            avg_recycling = (sum(r.get('recycling_rate', 0) or 0 for r in records) / len(records)) if records else 0
            avg_efficiency = (sum(r.get('efficiency_ratio', 0) or 0 for r in records) / len(records)) if records else 0
            records_count = len(records)

            values = {
                'total_water': round(total_water, 2),
                'avg_recycling': round(avg_recycling * 100, 1),
                'avg_efficiency': round(avg_efficiency * 100, 1),
                'records_count': records_count,
            }

            for key, (lbl, unit) in self.stats_cards.items():
                val = values.get(key, '—')
                lbl['text'] = f"{val} {unit}" if isinstance(val, (int, float)) else val
        except Exception as e:
            logging.error(f"Dashboard istatistik hatası: {e}")

    def _go_back(self) -> None:
        """SKDM ana görünüme dön veya yoksa Dashboard'a geç."""
        try:
            master = getattr(self.parent, 'master', None)
            # SKDMGUI içinde ise ana modüle dön (varsayılan: Karbon)
            if master and hasattr(master, 'load_carbon'):
                master.load_carbon()
                return
        except Exception as e:
            logging.error(f"[WaterGUI] Geri dönüş sırasında hata: {e}")
        # Yedek: Su Dashboard'a dön
        self.build_dashboard()

    def get_water_statistics(self) -> dict:
        """Su yönetimi istatistiklerini al"""
        try:
            records = self.manager.get_water_consumption(self.company_id)
            total = sum((r.get('total_water') or 0) for r in records)
            return {'record_count': len(records), 'total_water': total}
        except Exception as e:
            logging.info(f"Su istatistikleri alınamadı: {e}")
            return {}

    def get_water_trends(self, period_months=12) -> list:
        """Su tüketim trendlerini al"""
        try:
            return []
        except Exception as e:
            logging.info(f"Su trendleri alınamadı: {e}")
            return []

    def validate_water_data(self, data) -> list[str]:
        """Su verisi validasyonu"""
        errors = []

        # Dönem kontrolü
        if not data.get('period'):
            errors.append(self.lm.tr('error_period_required', "Dönem alanı zorunludur"))

        # Su miktarı kontrolü
        if data.get('total_water') is not None:
            if data['total_water'] < 0:
                errors.append(self.lm.tr('error_negative_water', "Su miktarı negatif olamaz"))
            if data['total_water'] > 1000000:  # 1 milyon m³ üst limit
                errors.append(self.lm.tr('error_high_water', "Su miktarı çok yüksek (max: 1,000,000 m³)"))

        # Oran kontrolü
        if data.get('recycling_rate') is not None:
            if not (0 <= data['recycling_rate'] <= 1):
                errors.append(self.lm.tr('error_invalid_recycling_rate', "Geri dönüşüm oranı 0-1 arasında olmalıdır"))

        if data.get('efficiency_ratio') is not None:
            if not (0 <= data['efficiency_ratio'] <= 1):
                errors.append(self.lm.tr('error_invalid_efficiency_rate', "Verimlilik oranı 0-1 arasında olmalıdır"))

        return errors

    def _log_activity(self, message, level="INFO") -> None:
        """Su yönetimi aktivitelerini logla"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] [WaterGUI] {message}"
            logging.info(log_entry)

            # Gerçek log dosyasına yazma (opsiyonel)
            try:
                with open("logs/water_management.log", "a", encoding="utf-8") as f:
                    f.write(log_entry + "\n")
            except Exception as e:
                logging.error(f'Silent error in water_gui.py: {str(e)}')  # Log dosyası yazılamazsa sessizce devam et
        except Exception as e:
            logging.error(f"Log yazma hatası: {e}")

    def _update_water_statistics(self) -> None:
        """Su istatistiklerini güncelle"""
        try:
            stats = self.get_water_statistics()
            trends = self.get_water_trends()
            self._log_activity(f"İstatistikler güncellendi: {len(stats)} metrik, {len(trends)} trend")
        except Exception as e:
            self._log_activity(f"İstatistik güncelleme hatası: {e}", level="ERROR")

    def _quick_add_record(self) -> None:
        try:
            period = (self.quick_period_ent.get() or '').strip()
            total = self._to_float(self.quick_total_ent.get()) or 0.0
            recycling_pct = self._to_float(self.quick_recycle_ent.get()) or 0.0
            efficiency_pct = self._to_float(self.quick_efficiency_ent.get()) or 0.0

            # Veri validasyonu
            data = {
                'period': period,
                'total_water': total,
                'recycling_rate': recycling_pct/100.0,
                'efficiency_ratio': efficiency_pct/100.0
            }

            errors = self.validate_water_data(data)
            if errors:
                messagebox.showwarning(self.lm.tr('data_error', 'Veri Hatası'), '\n'.join(errors))
                return

            # Log kaydı
            self._log_activity(f"Hızlı kayıt eklendi: {period}, {total} m³")

            consumption_id = self.manager.add_water_consumption(
                company_id=self.company_id,
                period=period,
                consumption_type='industrial',
                water_source='municipal',
                blue_water=0.0,
                green_water=0.0,
                grey_water=0.0,
                total_water=total,
                unit='m3',
                water_quality_parameters=None,
                efficiency_ratio=efficiency_pct/100.0,
                recycling_rate=recycling_pct/100.0,
                location=None,
                process_description=None,
                responsible_person=None,
                measurement_method='measurement',
                data_quality='medium',
                source=self.lm.tr('quick_entry', 'Hızlı Giriş'),
                evidence_file=None,
                notes=f"{self.lm.tr('quick_record_note', 'Hızlı kayıt')} - {self.lm.tr('efficiency', 'Verimlilik')}: {efficiency_pct}%, {self.lm.tr('recycling', 'Geri Dönüşüm')}: {recycling_pct}%",
            )

            if consumption_id:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), f"{self.lm.tr('record_added', 'Kayıt eklendi')} (ID: {consumption_id}).")
                # Formu temizle
                self.quick_period_ent.delete(0, 'end')
                self.quick_total_ent.delete(0, 'end')
                self.quick_recycle_ent.delete(0, 'end')
                self.quick_efficiency_ent.delete(0, 'end')
                # Kartları güncelle
                self._refresh_dashboard_stats()
                # İstatistikleri güncelle
                self._update_water_statistics()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('record_add_error', 'Kayıt eklenemedi. Detaylar konsolda bulunabilir.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('quick_record_error', 'Hızlı kayıt eklenirken sorun oluştu')}: {e}")
            self._log_activity(f"Hızlı kayıt hatası: {e}", level="ERROR")

    # ==================== KAYITLAR ====================
    def build_records_view(self) -> None:
        self.current_view = 'records'
        self.content_title['text'] = self.lm.tr('water_records', 'Su Kayıtları')
        self._clear_content()

        # Form alanları
        form = tk.LabelFrame(self.content_frame, text=self.lm.tr('new_consumption_record', 'Yeni Tüketim Kaydı'), bg='white')
        form.pack(fill='x', padx=15, pady=10)

        def add_labeled_entry(parent, text, row, col=0, width=20) -> tk.Entry:
            tk.Label(parent, text=text, bg='white').grid(row=row, column=col, sticky='w', padx=5, pady=4)
            ent = tk.Entry(parent, width=width)
            ent.grid(row=row, column=col+1, sticky='w', padx=5, pady=4)
            return ent

        # Satır 0
        self.period_ent = add_labeled_entry(form, self.lm.tr('period_example', 'Dönem (örn. 2024-Q1)'), 0)
        tk.Label(form, text=self.lm.tr('consumption_type', 'Tüketim Türü'), bg='white').grid(row=0, column=2, sticky='w', padx=5, pady=4)
        self.type_cmb = ttk.Combobox(form, values=list(self.type_map.values()), width=18)
        self.type_cmb.grid(row=0, column=3, sticky='w', padx=5, pady=4)
        self.type_cmb.set(self.type_map.get('industrial', 'industrial'))

        tk.Label(form, text=self.lm.tr('water_source', 'Su Kaynağı'), bg='white').grid(row=0, column=4, sticky='w', padx=5, pady=4)
        self.source_cmb = ttk.Combobox(form, values=list(self.source_map.values()), width=18)
        self.source_cmb.grid(row=0, column=5, sticky='w', padx=5, pady=4)
        self.source_cmb.set(self.source_map.get('municipal', 'municipal'))

        # Satır 1
        self.blue_ent = add_labeled_entry(form, self.lm.tr('blue_water_m3', 'Mavi Su (m³)'), 1)
        self.green_ent = add_labeled_entry(form, self.lm.tr('green_water_m3', 'Yeşil Su (m³)'), 1, col=2)
        self.grey_ent = add_labeled_entry(form, self.lm.tr('grey_water_m3', 'Gri Su (m³)'), 1, col=4)

        # Satır 2
        self.total_ent = add_labeled_entry(form, self.lm.tr('total_water_m3', 'Toplam Su (m³)'), 2)
        tk.Label(form, text=self.lm.tr('recycling_rate_percent', 'Geri Dönüşüm Oranı (%)'), bg='white').grid(row=2, column=2, sticky='w', padx=5, pady=4)
        self.recycle_ent = tk.Entry(form, width=20)
        self.recycle_ent.grid(row=2, column=3, sticky='w', padx=5, pady=4)
        tk.Label(form, text=self.lm.tr('efficiency_ratio_percent', 'Verimlilik Oranı (%)'), bg='white').grid(row=2, column=4, sticky='w', padx=5, pady=4)
        self.efficiency_ent = tk.Entry(form, width=20)
        self.efficiency_ent.grid(row=2, column=5, sticky='w', padx=5, pady=4)

        # Satır 3
        self.location_ent = add_labeled_entry(form, self.lm.tr('location', 'Lokasyon'), 3)
        self.process_ent = add_labeled_entry(form, self.lm.tr('process_description', 'Süreç Açıklaması'), 3, col=2, width=30)
        self.responsible_ent = add_labeled_entry(form, self.lm.tr('responsible_person', 'Sorumlu Kişi'), 3, col=4)

        # Satır 4
        tk.Label(form, text=self.lm.tr('measurement_method', 'Ölçüm Yöntemi'), bg='white').grid(row=4, column=0, sticky='w', padx=5, pady=4)
        self.method_cmb = ttk.Combobox(form, values=list(self.method_map.values()), width=18)
        self.method_cmb.grid(row=4, column=1, sticky='w', padx=5, pady=4)
        self.method_cmb.set(self.method_map.get('measurement', 'measurement'))

        tk.Label(form, text=self.lm.tr('data_quality', 'Veri Kalitesi'), bg='white').grid(row=4, column=2, sticky='w', padx=5, pady=4)
        self.quality_cmb = ttk.Combobox(form, values=list(self.quality_map.values()), width=18)
        self.quality_cmb.grid(row=4, column=3, sticky='w', padx=5, pady=4)
        self.quality_cmb.set(self.quality_map.get('medium', 'medium'))

        self.source_ent = add_labeled_entry(form, self.lm.tr('data_source', 'Veri Kaynağı'), 4, col=4)

        # Satır 5 - Finansal alanlar
        self.supplier_ent = add_labeled_entry(form, self.lm.tr('supplier', 'Tedarikçi Firma'), 5)
        tk.Label(form, text=self.lm.tr('invoice_date', 'Fatura Tarihi (YYYY-MM-DD)'), bg='white').grid(row=5, column=2, sticky='w', padx=5, pady=4)
        self.invoice_ent = tk.Entry(form, width=20)
        self.invoice_ent.grid(row=5, column=3, sticky='w', padx=5, pady=4)
        tk.Label(form, text=self.lm.tr('due_date', 'Son Ödeme Tarihi (YYYY-MM-DD)'), bg='white').grid(row=5, column=4, sticky='w', padx=5, pady=4)
        self.due_ent = tk.Entry(form, width=20)
        self.due_ent.grid(row=5, column=5, sticky='w', padx=5, pady=4)

        # Satır 6
        tk.Label(form, text=self.lm.tr('notes', 'Notlar'), bg='white').grid(row=6, column=0, sticky='nw', padx=5, pady=4)
        self.notes_txt = tk.Text(form, height=3, width=88)
        self.notes_txt.grid(row=6, column=1, columnspan=5, sticky='ew', padx=5, pady=4)

        # İşlem butonları
        btns = tk.Frame(form, bg='white')
        btns.grid(row=7, column=0, columnspan=6, sticky='e', padx=5, pady=8)
        ttk.Button(btns, text=self.lm.tr('btn_save', 'Kaydet'), style='Primary.TButton', command=self._save_consumption_record).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('btn_update', 'Güncelle'), style='Primary.TButton', command=self._update_consumption_record).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('clear_form', 'Formu Temizle'), style='Primary.TButton', command=self._clear_form).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('refresh_list', 'Listeyi Yenile'), style='Primary.TButton', command=self._refresh_records_list).pack(side='left', padx=5)

        # Filtreleme ve arama
        filter_frame = tk.LabelFrame(self.content_frame, text=self.lm.tr('filtering_and_search', 'Filtreleme ve Arama'), bg='white')
        filter_frame.pack(fill='x', padx=15, pady=10)

        # Filtreleme alanları
        tk.Label(filter_frame, text=self.lm.tr('period', 'Dönem:'), bg='white').grid(row=0, column=0, padx=5, pady=5)
        self.filter_period_cmb = ttk.Combobox(filter_frame, width=15)
        self.filter_period_cmb.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text=self.lm.tr('consumption_type', 'Tüketim Türü:'), bg='white').grid(row=0, column=2, padx=5, pady=5)
        self.filter_type_cmb = ttk.Combobox(
            filter_frame,
            values=[self.lm.tr('all', 'Tümü')] + list(self.type_map.values()),
            width=15,
        )
        self.filter_type_cmb.set(self.lm.tr('all', 'Tümü'))
        self.filter_type_cmb.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text=self.lm.tr('water_source', 'Su Kaynağı:'), bg='white').grid(row=0, column=4, padx=5, pady=5)
        self.filter_source_cmb = ttk.Combobox(
            filter_frame,
            values=[self.lm.tr('all', 'Tümü')] + list(self.source_map.values()),
            width=15,
        )
        self.filter_source_cmb.set(self.lm.tr('all', 'Tümü'))
        self.filter_source_cmb.grid(row=0, column=5, padx=5, pady=5)

        # Arama alanı
        tk.Label(filter_frame, text=self.lm.tr('search', 'Arama:'), bg='white').grid(row=1, column=0, padx=5, pady=5)
        self.search_entry = tk.Entry(filter_frame, width=30)
        self.search_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self._filter_records())

        # Filtreleme butonları
        ttk.Button(filter_frame, text=self.lm.tr('filter', 'Filtrele'), style='Primary.TButton', command=self._filter_records).grid(row=1, column=4, padx=5, pady=5)
        ttk.Button(filter_frame, text=self.lm.tr('clear', 'Temizle'), style='Primary.TButton', command=self._clear_filters).grid(row=1, column=5, padx=5, pady=5)

        # Kayıt listesi
        list_frame = tk.LabelFrame(self.content_frame, text=self.lm.tr('consumption_records', 'Tüketim Kayıtları'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Treeview için frame ve scrollbar
        tree_frame = tk.Frame(list_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        cols = (
            'id',
            'period',
            'consumption_type',
            'water_source',
            'total_water',
            'unit',
            'recycling_rate',
            'efficiency_ratio',
            'location',
            'created_at',
        )
        self.records_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)

        # Sütun başlıkları
        headers = {
            'id': 'ID', 'period': self.lm.tr('period', 'Dönem'), 'consumption_type': self.lm.tr('type', 'Tür'), 'water_source': self.lm.tr('source', 'Kaynak'),
            'total_water': self.lm.tr('total_m3', 'Toplam (m³)'), 'unit': self.lm.tr('unit', 'Birim'), 'recycling_rate': self.lm.tr('recycling_percent', 'Geri Dönüşüm (%)'),
            'efficiency_ratio': self.lm.tr('efficiency_percent', 'Verimlilik (%)'), 'location': self.lm.tr('location', 'Lokasyon'), 'created_at': self.lm.tr('created_at', 'Oluşturulma')
        }

        for c in cols:
            self.records_tree.heading(c, text=headers.get(c, c))
            if c == 'id':
                self.records_tree.column(c, width=50, anchor='center')
            elif c in ['total_water', 'recycling_rate', 'efficiency_ratio']:
                self.records_tree.column(c, width=100, anchor='center')
            elif c == 'location':
                self.records_tree.column(c, width=150, anchor='w')
            else:
                self.records_tree.column(c, width=120, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.records_tree.yview)
        self.records_tree.configure(yscrollcommand=scrollbar.set)

        self.records_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Liste işlemleri
        action_frame = tk.Frame(list_frame, bg='white')
        action_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(action_frame, text=self.lm.tr('view_details', ' Detaylı Görüntüle'), style='Primary.TButton', command=self._view_record_details).pack(side='left', padx=2)
        ttk.Button(action_frame, text=self.lm.tr('btn_edit', '️ Düzenle'), style='Primary.TButton', command=self._edit_selected_record).pack(side='left', padx=2)
        ttk.Button(action_frame, text=self.lm.tr('copy', ' Kopyala'), style='Primary.TButton', command=self._copy_record).pack(side='left', padx=2)
        ttk.Button(action_frame, text=self.lm.tr('btn_delete', '️ Sil'), style='Primary.TButton', command=self._delete_selected_record).pack(side='left', padx=2)

        # İstatistikler
        self.records_stats_label = tk.Label(action_frame, text=self.lm.tr('total_records_count', 'Toplam: 0 kayıt'), bg='white', fg='#7f8c8d')
        self.records_stats_label.pack(side='right', padx=10)

        # Filtreleri güncelle
        self._update_filter_options()
        self._refresh_records_list()

    def _clear_form(self) -> None:
        for ent in [
            self.period_ent,
            self.blue_ent,
            self.green_ent,
            self.grey_ent,
            self.total_ent,
            self.recycle_ent,
            self.efficiency_ent,
            self.location_ent,
            self.process_ent,
            self.responsible_ent,
            self.source_ent,
        ]:
            ent.delete(0, 'end')
        self.type_cmb.set('industrial')
        self.source_cmb.set('municipal')
        self.method_cmb.set(self.method_map.get('measurement', 'measurement'))
        self.quality_cmb.set(self.quality_map.get('medium', 'medium'))
        self.notes_txt.delete('1.0', 'end')
        self.current_record_id = None

    def _to_float(self, val) -> float | None:
        try:
            if val is None or val == '':
                return None
            return float(str(val).replace(',', '.'))
        except Exception:
            return None

    def _save_consumption_record(self) -> None:
        try:
            period = self.period_ent.get().strip()
            if not period:
                messagebox.showwarning(self.lm.tr('missing_info', 'Eksik Bilgi'), self.lm.tr('error_period_required', 'Dönem alanı zorunludur.'))
                return

            blue = self._to_float(self.blue_ent.get()) or 0.0
            green = self._to_float(self.green_ent.get()) or 0.0
            grey = self._to_float(self.grey_ent.get()) or 0.0
            total = self._to_float(self.total_ent.get())
            if total is None:
                total = blue + green + grey

            recycling_pct = self._to_float(self.recycle_ent.get()) or 0.0
            efficiency_pct = self._to_float(self.efficiency_ent.get()) or 0.0

            consumption_id = self.manager.add_water_consumption(
                company_id=self.company_id,
                period=period,
                consumption_type=self.type_map_rev.get(self.type_cmb.get(), self.type_cmb.get()),
                water_source=self.source_map_rev.get(self.source_cmb.get(), self.source_cmb.get()),
                blue_water=blue,
                green_water=green,
                grey_water=grey,
                total_water=total,
                unit='m3',
                water_quality_parameters=None,
                efficiency_ratio=efficiency_pct/100.0,
                recycling_rate=recycling_pct/100.0,
                location=self.location_ent.get().strip() or None,
                process_description=self.process_ent.get().strip() or None,
                responsible_person=self.responsible_ent.get().strip() or None,
                measurement_method=self.method_map_rev.get(self.method_cmb.get(), self.method_cmb.get()),
                data_quality=self.quality_map_rev.get(self.quality_cmb.get(), self.quality_cmb.get()),
                source=self.source_ent.get().strip() or None,
                evidence_file=None,
                notes=self.notes_txt.get('1.0', 'end').strip() or None,
                supplier=self.supplier_ent.get().strip() or None,
                invoice_date=self.invoice_ent.get().strip() or None,
                due_date=self.due_ent.get().strip() or None,
            )

            if consumption_id:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), f"{self.lm.tr('record_added', 'Kayıt eklendi')} (ID: {consumption_id}).")
                self._refresh_records_list()
                self._refresh_dashboard_stats()
                self._refresh_periods()
                self._clear_form()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('record_add_error', 'Kayıt eklenemedi. Detaylar konsolda bulunabilir.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('record_add_error_detailed', 'Kayıt eklenirken sorun oluştu')}: {e}")

    def _edit_selected_record(self) -> None:
        try:
            if not self.records_tree:
                return
            sel = self.records_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('select_record_to_edit', 'Lütfen düzenlemek için bir kayıt seçin.'))
                return
            item = self.records_tree.item(sel[0])
            rec_id = item['values'][0]
            # Kayıt detayını bul ve forma bas
            records = self.manager.get_water_consumption(self.company_id)
            rec = next((r for r in records if r['id'] == rec_id), None)
            if not rec:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('record_details_error', 'Kayıt detayları getirilemedi.'))
                return
            self.current_record_id = int(rec_id)
            # Formu doldur
            self.period_ent.delete(0, 'end')
            self.period_ent.insert(0, rec.get('period') or '')
            self.type_cmb.set(rec.get('consumption_type') or 'industrial')
            self.source_cmb.set(rec.get('water_source') or 'municipal')
            self.blue_ent.delete(0, 'end')
            self.blue_ent.insert(0, str(rec.get('blue_water') or ''))
            self.green_ent.delete(0, 'end')
            self.green_ent.insert(0, str(rec.get('green_water') or ''))
            self.grey_ent.delete(0, 'end')
            self.grey_ent.insert(0, str(rec.get('grey_water') or ''))
            self.total_ent.delete(0, 'end')
            self.total_ent.insert(0, str(rec.get('total_water') or ''))
            self.recycle_ent.delete(0, 'end')
            self.recycle_ent.insert(0, str(((rec.get('recycling_rate') or 0) * 100)))
            self.efficiency_ent.delete(0, 'end')
            self.efficiency_ent.insert(0, str(((rec.get('efficiency_ratio') or 0) * 100)))
            self.location_ent.delete(0, 'end')
            self.location_ent.insert(0, rec.get('location') or '')
            self.process_ent.delete(0, 'end')
            self.process_ent.insert(0, rec.get('process_description') or '')
            self.responsible_ent.delete(0, 'end')
            self.responsible_ent.insert(0, rec.get('responsible_person') or '')
            self.method_cmb.set(self.method_map.get(rec.get('measurement_method'), rec.get('measurement_method')) or 'measurement')
            self.quality_cmb.set(self.quality_map.get(rec.get('data_quality'), rec.get('data_quality')) or 'medium')
            self.source_ent.delete(0, 'end')
            self.source_ent.insert(0, rec.get('source') or '')
            self.supplier_ent.delete(0, 'end')
            self.supplier_ent.insert(0, rec.get('supplier') or '')
            self.invoice_ent.delete(0, 'end')
            self.invoice_ent.insert(0, rec.get('invoice_date') or '')
            self.due_ent.delete(0, 'end')
            self.due_ent.insert(0, rec.get('due_date') or '')
            self.notes_txt.delete('1.0', 'end')
            self.notes_txt.insert('1.0', rec.get('notes') or '')
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('record_edit_mode', 'Kayıt #{rec_id} düzenleme modunda.').format(rec_id=rec_id)}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('edit_error', 'Düzenleme sırasında sorun')}: {e}")

    def _update_consumption_record(self) -> None:
        try:
            if not self.current_record_id:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('select_record_to_update', 'Güncellemek için önce bir kayıt seçip düzenleyin.'))
                return
            period = self.period_ent.get().strip()
            blue = self._to_float(self.blue_ent.get())
            green = self._to_float(self.green_ent.get())
            grey = self._to_float(self.grey_ent.get())
            total = self._to_float(self.total_ent.get())
            recycling_pct = self._to_float(self.recycle_ent.get())
            efficiency_pct = self._to_float(self.efficiency_ent.get())

            updates = {
                'period': period or None,
                'consumption_type': self.type_map_rev.get(self.type_cmb.get(), self.type_cmb.get()) or None,
                'water_source': self.source_map_rev.get(self.source_cmb.get(), self.source_cmb.get()) or None,
                'blue_water': blue,
                'green_water': green,
                'grey_water': grey,
                'total_water': total,
                'unit': 'm3',
                'efficiency_ratio': (efficiency_pct or 0)/100.0 if efficiency_pct is not None else None,
                'recycling_rate': (recycling_pct or 0)/100.0 if recycling_pct is not None else None,
                'location': self.location_ent.get().strip() or None,
                'process_description': self.process_ent.get().strip() or None,
                'responsible_person': self.responsible_ent.get().strip() or None,
                'measurement_method': self.method_map_rev.get(self.method_cmb.get(), self.method_cmb.get()) or None,
                'data_quality': self.quality_map_rev.get(self.quality_cmb.get(), self.quality_cmb.get()) or None,
                'source': self.source_ent.get().strip() or None,
                'supplier': self.supplier_ent.get().strip() or None,
                'invoice_date': self.invoice_ent.get().strip() or None,
                'due_date': self.due_ent.get().strip() or None,
                'notes': self.notes_txt.get('1.0', 'end').strip() or None,
            }
            filtered_updates = {k: v for k, v in updates.items() if v is not None}
            ok = self.manager.update_water_consumption(
                self.current_record_id,
                **filtered_updates,
            )
            if ok:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('record_updated', 'Kayıt güncellendi.'))
                self._refresh_records_list()
                self._refresh_dashboard_stats()
                self._refresh_periods()
                self._clear_form()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('record_update_error', 'Kayıt güncellenemedi.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('update_error', 'Güncelleme sırasında sorun')}: {e}")

    def _update_filter_options(self) -> None:
        """Filtre seçeneklerini güncelle"""
        try:
            records = self.manager.get_water_consumption(self.company_id)
            periods = sorted(set(r['period'] for r in records if r.get('period')))
            self.filter_period_cmb['values'] = [self.lm.tr('all', 'Tümü')] + periods
        except Exception as e:
            self._log_activity(f"Filtre seçenekleri güncellenemedi: {e}", level="ERROR")

    def _filter_records(self) -> None:
        """Kayıtları filtrele"""
        try:
            # Filtre kriterleri
            period_filter = self.filter_period_cmb.get()
            type_filter = self.filter_type_cmb.get()
            source_filter = self.filter_source_cmb.get()
            search_term = self.search_entry.get().lower()

            # Tüm kayıtları al
            all_records = self.manager.get_water_consumption(self.company_id)
            filtered_records = []

            for r in all_records:
                # Dönem filtresi
                if period_filter != self.lm.tr('all', 'Tümü') and r.get('period') != period_filter:
                    continue

                # Tür filtresi
                if type_filter != self.lm.tr('all', 'Tümü') and r.get('consumption_type') != type_filter:
                    continue

                # Kaynak filtresi
                if source_filter != self.lm.tr('all', 'Tümü') and r.get('water_source') != source_filter:
                    continue

                # Arama filtresi
                if search_term:
                    search_fields = [
                        str(r.get('period', '')),
                        str(r.get('consumption_type', '')),
                        str(r.get('water_source', '')),
                        str(r.get('location', '')),
                        str(r.get('responsible_person', '')),
                        str(r.get('notes', ''))
                    ]
                    if not any(search_term in field.lower() for field in search_fields):
                        continue

                filtered_records.append(r)

            # Listeyi güncelle
            self._populate_records_tree(filtered_records)
            self._log_activity(f"Kayıtlar filtrelendi: {len(filtered_records)}/{len(all_records)} kayıt")

        except Exception as e:
            self._log_activity(f"Filtreleme hatası: {e}", level="ERROR")

    def _clear_filters(self) -> None:
        """Filtreleri temizle"""
        self.filter_period_cmb.set(self.lm.tr('all', 'Tümü'))
        self.filter_type_cmb.set(self.lm.tr('all', 'Tümü'))
        self.filter_source_cmb.set(self.lm.tr('all', 'Tümü'))
        self.search_entry.delete(0, 'end')
        self._refresh_records_list()

    def _populate_records_tree(self, records) -> None:
        """Treeview'i kayıtlarla doldur"""
        try:
            if not self.records_tree:
                return
            # Mevcut kayıtları temizle
            for i in self.records_tree.get_children():
                self.records_tree.delete(i)

            # Yeni kayıtları ekle
            for r in records:
                created_at = r.get('created_at', '')
                if created_at:
                    try:
                        from datetime import datetime
                        iso_value = created_at.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(iso_value)
                        created_at = dt.strftime('%Y-%m-%d %H:%M')
                    except Exception:
                        created_at = str(created_at)[:16]
                else:
                    created_at = ''

                self.records_tree.insert('', 'end', values=(
                    r['id'],
                    r['period'],
                    r['consumption_type'],
                    r['water_source'],
                    round(r['total_water'] or 0, 2),
                    r['unit'] or 'm3',
                    round((r['recycling_rate'] or 0)*100, 1),
                    round((r['efficiency_ratio'] or 0)*100, 1),
                    r['location'] or '',
                    created_at
                ))

            # İstatistikleri güncelle
            self.records_stats_label['text'] = self.lm.tr('total_records_count', 'Toplam: {count} kayıt').format(count=len(records))

        except Exception as e:
            self._log_activity(f"Treeview doldurma hatası: {e}", level="ERROR")

    def _refresh_records_list(self) -> None:
        try:
            records = self.manager.get_water_consumption(self.company_id)
            self._populate_records_tree(records)
            self._update_filter_options()
        except Exception as e:
            self._log_activity(f"Kayıt listesi yenileme hatası: {e}", level="ERROR")

    def _view_record_details(self) -> None:
        """Seçili kaydın detaylarını göster"""
        try:
            if not self.records_tree:
                return
            sel = self.records_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('select_record_to_view', 'Lütfen detaylarını görmek için bir kayıt seçin.'))
                return

            item = self.records_tree.item(sel[0])
            rec_id = item['values'][0]

            # Kayıt detaylarını al
            records = self.manager.get_water_consumption(self.company_id)
            record = next((r for r in records if r['id'] == rec_id), None)

            if not record:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('record_details_not_found', 'Kayıt detayları bulunamadı.'))
                return

            # Detay penceresi
            detail_window = tk.Toplevel(self.parent)
            detail_window.title(f"{self.lm.tr('record_details', 'Kayıt Detayları')} - #{rec_id}")
            detail_window.geometry("600x500")
            detail_window.configure(bg='white')

            # Detay içeriği
            detail_text = f"""
 {self.lm.tr('water_consumption_details', 'SU TÜKETİM KAYDI DETAYLARI')}

🆔 {self.lm.tr('record_id', 'Kayıt ID')}: {record['id']}
 {self.lm.tr('period', 'Dönem')}: {record.get('period', self.lm.tr('no_data', 'Veri Yok'))}
 {self.lm.tr('consumption_type', 'Tüketim Türü')}: {record.get('consumption_type', self.lm.tr('no_data', 'Veri Yok'))}
 {self.lm.tr('water_source', 'Su Kaynağı')}: {record.get('water_source', self.lm.tr('no_data', 'Veri Yok'))}

 {self.lm.tr('water_amounts', 'SU MİKTARLARI')}:
   • {self.lm.tr('blue_water', 'Mavi Su')}: {record.get('blue_water', 0):.2f} m³
   • {self.lm.tr('green_water', 'Yeşil Su')}: {record.get('green_water', 0):.2f} m³
   • {self.lm.tr('grey_water', 'Gri Su')}: {record.get('grey_water', 0):.2f} m³
   • {self.lm.tr('total_water', 'Toplam Su')}: {record.get('total_water', 0):.2f} m³

 {self.lm.tr('efficiency_metrics', 'VERİMLİLİK METRİKLERİ')}:
   • {self.lm.tr('recycling_rate', 'Geri Dönüşüm Oranı')}: {(record.get('recycling_rate', 0) * 100):.1f}%
   • {self.lm.tr('efficiency_rate', 'Verimlilik Oranı')}: {(record.get('efficiency_ratio', 0) * 100):.1f}%

 {self.lm.tr('location_info', 'LOKASYON BİLGİLERİ')}:
   • {self.lm.tr('location', 'Lokasyon')}: {record.get('location', self.lm.tr('no_data', 'Veri Yok'))}
   • {self.lm.tr('process_description', 'Süreç Açıklaması')}: {record.get('process_description', self.lm.tr('no_data', 'Veri Yok'))}
   • {self.lm.tr('responsible_person', 'Sorumlu Kişi')}: {record.get('responsible_person', self.lm.tr('no_data', 'Veri Yok'))}

 {self.lm.tr('measurement_info', 'ÖLÇÜM BİLGİLERİ')}:
   • {self.lm.tr('measurement_method', 'Ölçüm Yöntemi')}: {record.get('measurement_method', self.lm.tr('no_data', 'Veri Yok'))}
   • {self.lm.tr('data_quality', 'Veri Kalitesi')}: {record.get('data_quality', self.lm.tr('no_data', 'Veri Yok'))}
   • {self.lm.tr('data_source', 'Veri Kaynağı')}: {record.get('source', self.lm.tr('no_data', 'Veri Yok'))}

 {self.lm.tr('notes', 'NOTLAR')}:
{record.get('notes', self.lm.tr('no_notes', 'Kayıt için not bulunmuyor.'))}

Icons.TIME {self.lm.tr('record_info', 'KAYIT BİLGİLERİ')}:
   • {self.lm.tr('created_at', 'Oluşturulma')}: {record.get('created_at', self.lm.tr('no_data', 'Veri Yok'))}
   • {self.lm.tr('updated_at', 'Güncellenme')}: {record.get('updated_at', self.lm.tr('no_data', 'Veri Yok'))}
            """

            # Text widget
            text_widget = tk.Text(detail_window, wrap='word', font=('Segoe UI', 10), bg='#f8f9fa', relief='flat')
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            text_widget.insert('1.0', detail_text.strip())
            text_widget.configure(state='disabled')

            # Kapatma butonu
            ttk.Button(detail_window, text=self.lm.tr('btn_close', 'Kapat'), style='Primary.TButton', command=detail_window.destroy).pack(pady=10)

            self._log_activity(f"Kayıt #{rec_id} detayları görüntülendi")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Detay görüntüleme hatası: {e}')
            self._log_activity(f"Detay görüntüleme hatası: {e}", level="ERROR")

    def _copy_record(self) -> None:
        """Seçili kaydı kopyala"""
        try:
            if not self.records_tree:
                return
            sel = self.records_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('msg_info', 'Bilgi'), self.lm.tr('msg_select_record_copy', 'Lütfen kopyalamak için bir kayıt seçin.'))
                return

            item = self.records_tree.item(sel[0])
            rec_id = item['values'][0]

            # Kayıt detaylarını al
            records = self.manager.get_water_consumption(self.company_id)
            record = next((r for r in records if r['id'] == rec_id), None)

            if not record:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('msg_record_not_found', 'Kayıt detayları bulunamadı.'))
                return

            # Formu doldur (kopyalama için)
            self.period_ent.delete(0, 'end')
            self.period_ent.insert(0, f"{record.get('period', '')} - Kopya")
            
            ctype = record.get('consumption_type', 'industrial')
            self.type_cmb.set(self.type_map.get(ctype, ctype))
            
            src = record.get('water_source', 'municipal')
            self.source_cmb.set(self.source_map.get(src, src))
            
            self.blue_ent.delete(0, 'end')
            self.blue_ent.insert(0, str(record.get('blue_water', 0)))
            self.green_ent.delete(0, 'end')
            self.green_ent.insert(0, str(record.get('green_water', 0)))
            self.grey_ent.delete(0, 'end')
            self.grey_ent.insert(0, str(record.get('grey_water', 0)))
            self.total_ent.delete(0, 'end')
            self.total_ent.insert(0, str(record.get('total_water', 0)))
            self.recycle_ent.delete(0, 'end')
            self.recycle_ent.insert(0, str((record.get('recycling_rate', 0) * 100)))
            self.efficiency_ent.delete(0, 'end')
            self.efficiency_ent.insert(0, str((record.get('efficiency_ratio', 0) * 100)))
            self.location_ent.delete(0, 'end')
            self.location_ent.insert(0, record.get('location', ''))
            self.process_ent.delete(0, 'end')
            self.process_ent.insert(0, record.get('process_description', ''))
            self.responsible_ent.delete(0, 'end')
            self.responsible_ent.insert(0, record.get('responsible_person', ''))
            self.method_cmb.set(record.get('measurement_method', 'measurement'))
            self.quality_cmb.set(record.get('data_quality', 'medium'))
            self.source_ent.delete(0, 'end')
            self.source_ent.insert(0, record.get('source', ''))
            self.notes_txt.delete('1.0', 'end')
            self.notes_txt.insert('1.0', f"Kopya - {record.get('notes', '')}")

            # Düzenleme modundan çık
            self.current_record_id = None

            messagebox.showinfo(
                self.lm.tr('success', 'Başarılı'),
                self.lm.tr('water_msg_copy_success', 'Kayıt #{rec_id} formuna kopyalandı. Gerekli değişiklikleri yapıp kaydedebilirsiniz.').format(rec_id=rec_id)
            )
            self._log_activity(f"Kayıt #{rec_id} formuna kopyalandı")

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('water_msg_copy_error', f'Kopyalama hatası: {e}').format(e=e))
            self._log_activity(f"Kopyalama hatası: {e}", level="ERROR")

    def _delete_selected_record(self) -> None:
        try:
            if not self.records_tree:
                return
            sel = self.records_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('water_msg_select_delete', 'Lütfen silmek için bir kayıt seçin.'))
                return
            item = self.records_tree.item(sel[0])
            rec_id = item['values'][0]
            if messagebox.askyesno(self.lm.tr('confirm', 'Onay'), self.lm.tr('water_msg_confirm_delete', f'Kayıt #{rec_id} silinsin mi?').format(rec_id=rec_id)):
                ok = self.manager.delete_water_consumption(int(rec_id))
                if ok:
                    messagebox.showinfo(self.lm.tr('deleted', 'Silindi'), self.lm.tr('water_msg_record_deleted', 'Kayıt silindi.'))
                    self._refresh_records_list()
                    self._refresh_dashboard_stats()
                    self._log_activity(f"Kayıt #{rec_id} silindi")
                else:
                    messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('water_msg_record_delete_error', 'Kayıt silinemedi.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('water_msg_delete_error', f'Silme sırasında sorun: {e}').format(e=e))
            self._log_activity(f"Silme hatası: {e}", level="ERROR")

    def _refresh_periods(self) -> None:
        records = self.manager.get_water_consumption(self.company_id)
        self.periods = sorted({r['period'] for r in records if r.get('period')})

    # ==================== METRİKLER ====================
    def build_metrics_view(self) -> None:
        self.current_view = 'metrics'
        self.content_title['text'] = self.lm.tr('water_metrics', 'Su Metrikleri')
        self._clear_content()

        # Dönem seçimi
        selector = tk.Frame(self.content_frame, bg='white')
        selector.pack(fill='x', padx=15, pady=10)
        tk.Label(selector, text=self.lm.tr('select_period', 'Dönem Seç'), bg='white').pack(side='left')
        self._refresh_periods()
        self.period_cmb = ttk.Combobox(selector, values=self.periods, width=20)
        self.period_cmb.pack(side='left', padx=8)
        if self.periods:
            self.period_cmb.set(self.periods[0])
        ttk.Button(selector, text=self.lm.tr('calculate', 'Hesapla'), style='Primary.TButton', command=self._calculate_footprint).pack(side='left', padx=8)

        # Sonuç kartları
        res_frame = tk.Frame(self.content_frame, bg='white')
        res_frame.pack(fill='x', padx=15, pady=5)

        self.metric_labels = {}
        metrics = [
            (self.lm.tr('blue_water', 'Mavi Su'), 'total_blue_water', 'm³', '#3498db'),
            (self.lm.tr('green_water', 'Yeşil Su'), 'total_green_water', 'm³', '#27ae60'),
            (self.lm.tr('grey_water', 'Gri Su'), 'total_grey_water', 'm³', '#8e44ad'),
            (self.lm.tr('total_footprint', 'Toplam Ayak İzi'), 'total_water_footprint', 'm³', '#34495e'),
        ]

        for i, (title, key, unit, color) in enumerate(metrics):
            card = tk.Frame(res_frame, bg=color, relief='raised', bd=2)
            card.grid(row=0, column=i, padx=8, pady=5, sticky='ew')
            res_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'), fg='white', bg=color).pack(pady=(10, 3))
            lbl = tk.Label(card, text='—', font=('Segoe UI', 16, 'bold'), fg='white', bg=color)
            lbl.pack(pady=(0, 10))
            self.metric_labels[key] = (lbl, unit)

        # Dağılım tabloları
        breakdown = tk.Frame(self.content_frame, bg='white')
        breakdown.pack(fill='both', expand=True, padx=15, pady=10)

        # Tür dağılımı
        type_frame = tk.LabelFrame(breakdown, text=self.lm.tr('distribution_by_type', 'Tüketim Türüne Göre Dağılım'), bg='white')
        type_frame.pack(side='left', fill='both', expand=True, padx=5)
        self.type_tree = ttk.Treeview(type_frame, columns=('type', 'blue', 'green', 'grey', 'total'), show='headings')
        for c, t in [('type', self.lm.tr('type', 'Tür')),
                     ('blue', self.lm.tr('blue', 'Mavi')),
                     ('green', self.lm.tr('green', 'Yeşil')),
                     ('grey', self.lm.tr('grey', 'Gri')),
                     ('total', self.lm.tr('total', 'Toplam'))]:
            self.type_tree.heading(c, text=t)
            self.type_tree.column(c, width=90, anchor='center')
        self.type_tree.pack(fill='both', expand=True)

        # Kaynak dağılımı
        source_frame = tk.LabelFrame(breakdown, text=self.lm.tr('distribution_by_source', 'Su Kaynağına Göre Dağılım'), bg='white')
        source_frame.pack(side='right', fill='both', expand=True, padx=5)
        self.source_tree = ttk.Treeview(
            source_frame,
            columns=('source', 'blue', 'green', 'grey', 'total'),
            show='headings',
        )
        for c, t in [('source', self.lm.tr('source', 'Kaynak')),
                     ('blue', self.lm.tr('blue', 'Mavi')),
                     ('green', self.lm.tr('green', 'Yeşil')),
                     ('grey', self.lm.tr('grey', 'Gri')),
                     ('total', self.lm.tr('total', 'Toplam'))]:
            self.source_tree.heading(c, text=t)
            self.source_tree.column(c, width=90, anchor='center')
        self.source_tree.pack(fill='both', expand=True)

    def _calculate_footprint(self) -> None:
        try:
            period = self.period_cmb.get().strip()
            if not period:
                messagebox.showwarning(self.lm.tr('select_period', 'Dönem Seçimi'), self.lm.tr('error_select_period', 'Lütfen dönem seçin.'))
                return

            # Log kaydı
            self._log_activity(f"Su ayak izi hesaplama başlatıldı: {period}")

            result = self.manager.calculate_water_footprint(self.company_id, period)
            if not result:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('no_data_for_period', 'Seçilen döneme ait veri bulunamadı.'))
                self._log_activity(f"Su ayak izi hesaplama: {period} için veri bulunamadı")
                return

            # Ana metrikleri güncelle
            for key, (lbl, unit) in self.metric_labels.items():
                val = result.get(key, 0)
                if isinstance(val, (int, float)):
                    lbl['text'] = f"{val:.2f} {unit}"
                else:
                    lbl['text'] = f"{val} {unit}"

            # Dağılım tablolarını güncelle
            for tree in (self.type_tree, self.source_tree):
                for i in tree.get_children():
                    tree.delete(i)

            # Tür bazlı dağılım
            breakdown_by_type = result.get('breakdown_by_type', {})
            if breakdown_by_type:
                for t, vals in breakdown_by_type.items():
                    self.type_tree.insert('', 'end', values=(
                        t,
                        f"{vals.get('blue_water', 0):.2f}",
                        f"{vals.get('green_water', 0):.2f}",
                        f"{vals.get('grey_water', 0):.2f}",
                        f"{vals.get('total', 0):.2f}"
                    ))
            else:
                self.type_tree.insert('', 'end', values=(self.lm.tr('no_data', 'Veri Yok'), '0.00', '0.00', '0.00', '0.00'))

            # Kaynak bazlı dağılım
            breakdown_by_source = result.get('breakdown_by_source', {})
            if breakdown_by_source:
                for s, vals in breakdown_by_source.items():
                    self.source_tree.insert('', 'end', values=(
                        s,
                        f"{vals.get('blue_water', 0):.2f}",
                        f"{vals.get('green_water', 0):.2f}",
                        f"{vals.get('grey_water', 0):.2f}",
                        f"{vals.get('total', 0):.2f}"
                    ))
            else:
                self.source_tree.insert('', 'end', values=(self.lm.tr('no_data', 'Veri Yok'), '0.00', '0.00', '0.00', '0.00'))

            # Hesaplama detaylarını göster
            self._show_calculation_details(result, period)

            total_fp = result.get('total_water_footprint', 0)
            self._log_activity(
                f"Su ayak izi hesaplama tamamlandı: {period} - Toplam: {total_fp:.2f} m³"
            )

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('calculation_error', 'Hesaplama sırasında sorun')}: {e}")
            self._log_activity(f"Su ayak izi hesaplama hatası: {e}", level="ERROR")

    def _show_calculation_details(self, result, period) -> None:
        """Hesaplama detaylarını göster"""
        try:
            # Detay penceresi
            detail_window = tk.Toplevel(self.parent)
            detail_window.title(f"{self.lm.tr('calc_details_title', 'Su Ayak İzi Hesaplama Detayları')} - {period}")
            detail_window.geometry("600x500")
            detail_window.configure(bg='white')

            # Detay içeriği
            detail_text = f"""
 {self.lm.tr('calc_details_header', 'SU AYAK İZİ HESAPLAMA DETAYLARI')} - {period}

 {self.lm.tr('main_metrics', 'ANA METRİKLER')}:
• {self.lm.tr('blue_water', 'Mavi Su')}: {result.get('total_blue_water', 0):.2f} m³
• {self.lm.tr('green_water', 'Yeşil Su')}: {result.get('total_green_water', 0):.2f} m³
• {self.lm.tr('grey_water', 'Gri Su')}: {result.get('total_grey_water', 0):.2f} m³
• {self.lm.tr('total_footprint', 'Toplam Su Ayak İzi')}: {result.get('total_water_footprint', 0):.2f} m³

 {self.lm.tr('distribution_by_type', 'TÜKETİM TÜRÜNE GÖRE DAĞILIM')}:
"""

            # Tür bazlı detaylar
            breakdown_by_type = result.get('breakdown_by_type', {})
            if breakdown_by_type:
                for t, vals in breakdown_by_type.items():
                    total_fp = result.get('total_water_footprint', 0)
                    total_val = vals.get('total', 0)
                    if total_fp > 0:
                        percentage = (total_val / total_fp) * 100
                    else:
                        percentage = 0
                    detail_text += f"• {t}: {vals.get('total', 0):.2f} m³ (%{percentage:.1f})\n"
            else:
                detail_text += f"• {self.lm.tr('no_data', 'Veri bulunamadı')}\n"

            detail_text += f"""
{self.lm.tr('distribution_by_source', 'SU KAYNAĞINA GÖRE DAĞILIM')}:
"""

            # Kaynak bazlı detaylar
            breakdown_by_source = result.get('breakdown_by_source', {})
            if breakdown_by_source:
                for s, vals in breakdown_by_source.items():
                    total_fp = result.get('total_water_footprint', 0)
                    total_val = vals.get('total', 0)
                    if total_fp > 0:
                        percentage = (total_val / total_fp) * 100
                    else:
                        percentage = 0
                    detail_text += f"• {s}: {vals.get('total', 0):.2f} m³ (%{percentage:.1f})\n"
            else:
                detail_text += f"• {self.lm.tr('no_data', 'Veri bulunamadı')}\n"

            detail_text += f"""

 {self.lm.tr('methodology', 'HESAPLAMA METODOLOJİSİ')}:
• {self.lm.tr('method_iso', 'Hesaplama Yöntemi: ISO 14046 Su Ayak İzi Standardı')}
• {self.lm.tr('blue_water_desc', 'Mavi Su: Doğrudan tüketilen tatlı su')}
• {self.lm.tr('green_water_desc', 'Yeşil Su: Yağmur suyu kullanımı')}
• {self.lm.tr('grey_water_desc', 'Gri Su: Kirlenmiş suyun temizlenmesi için gerekli su')}

 {self.lm.tr('recommendations', 'YORUM VE ÖNERİLER')}:
{self._generate_footprint_recommendations(result)}

═══════════════════════════════════════════════════

 {self.lm.tr('data_sources', 'VERİ KAYNAKLARI')}:
• {self.lm.tr('consumption_records', 'Tüketim Kayıtları')}: {result.get('consumption_records_count', 0)} {self.lm.tr('record', 'kayıt')}
• {self.lm.tr('quality_measurements', 'Kalite Ölçümleri')}: {result.get('quality_measurements_count', 0)} {self.lm.tr('measurement', 'ölçüm')}
• {self.lm.tr('calculation_date', 'Hesaplama Tarihi')}: {result.get('calculation_date', self.lm.tr('no_data', 'Veri Yok'))}
            """

            # Text widget
            text_widget = tk.Text(detail_window, wrap='word', font=('Segoe UI', 10), bg='#f8f9fa', relief='flat')
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            text_widget.insert('1.0', detail_text.strip())
            text_widget.configure(state='disabled')

            # Kapatma butonu
            ttk.Button(detail_window, text=self.lm.tr('btn_close', 'Kapat'), style='Primary.TButton', command=detail_window.destroy).pack(pady=10)

        except Exception as e:
            self._log_activity(f"Hesaplama detayları gösterim hatası: {e}", level="ERROR")

    def _generate_footprint_recommendations(self, result) -> str:
        """Su ayak izi önerileri oluştur"""
        recommendations = []

        total_footprint = result.get('total_water_footprint', 0)

        if total_footprint == 0:
            recommendations.append(f"• {self.lm.tr('no_water_data', 'Henüz su tüketim verisi girilmemiş')}")
            recommendations.append(f"• {self.lm.tr('add_water_records_hint', 'Su kayıtları ekleyerek ayak izi hesaplaması yapabilirsiniz')}")
            return '\n'.join(recommendations)

        # Mavi su analizi
        blue_water = result.get('total_blue_water', 0)
        blue_percentage = (blue_water / total_footprint) * 100 if total_footprint > 0 else 0

        if blue_percentage > 70:
            recommendations.append(f"• {self.lm.tr('high_blue_water', 'Mavi su kullanımı yüksek, verimlilik artırılabilir')}")
        elif blue_percentage < 30:
            recommendations.append(f"• {self.lm.tr('low_blue_water', 'Mavi su kullanımı düşük, iyi performans')}")

        # Gri su analizi
        grey_water = result.get('total_grey_water', 0)
        grey_percentage = (grey_water / total_footprint) * 100 if total_footprint > 0 else 0

        if grey_percentage > 50:
            recommendations.append(f"• {self.lm.tr('high_grey_water', 'Gri su oranı yüksek, arıtma sistemleri geliştirilebilir')}")

        # Genel öneriler
        if total_footprint > 10000:  # 10,000 m³ üst limit
            recommendations.append(f"• {self.lm.tr('high_footprint', 'Toplam su ayak izi yüksek, tasarruf önlemleri alınabilir')}")
        elif total_footprint < 1000:  # 1,000 m³ alt limit
            recommendations.append(f"• {self.lm.tr('low_footprint', 'Su ayak izi düşük, bu performansı sürdürün')}")

        # Kaynak çeşitliliği
        breakdown_by_source = result.get('breakdown_by_source', {})
        if len(breakdown_by_source) < 2:
            recommendations.append(f"• {self.lm.tr('diversify_sources', 'Su kaynakları çeşitlendirilebilir')}")

        # Tür çeşitliliği
        breakdown_by_type = result.get('breakdown_by_type', {})
        if len(breakdown_by_type) < 2:
            recommendations.append(f"• {self.lm.tr('collect_more_data', 'Farklı tüketim türlerinde veri toplanabilir')}")

        return '\n'.join(recommendations) if recommendations else f"• {self.lm.tr('good_performance', 'Su ayak izi performansınız iyi durumda!')}"

    # ==================== RAPORLAR ====================
    def build_reports_view(self) -> None:
        self.current_view = 'reports'
        self.content_title['text'] = self.lm.tr('water_reports', 'Su Raporları')
        self._clear_content()

        panel = tk.Frame(self.content_frame, bg='white')
        panel.pack(fill='x', padx=15, pady=10)

        tk.Label(panel, text=self.lm.tr('report_period', 'Rapor Dönemi'), bg='white').pack(side='left')
        self._refresh_periods()
        self.report_period_cmb = ttk.Combobox(panel, values=self.periods, width=20)
        self.report_period_cmb.pack(side='left', padx=8)
        if self.periods:
            self.report_period_cmb.set(self.periods[0])

        ttk.Button(panel, text=self.lm.tr('create_docx_report', 'DOCX Rapor Oluştur'), style='Primary.TButton', command=self._export_docx).pack(side='left', padx=5)
        ttk.Button(panel, text=self.lm.tr('create_excel_report', 'Excel Rapor Oluştur'), style='Primary.TButton', command=self._export_excel).pack(side='left', padx=5)
        ttk.Button(panel, text=self.lm.tr('preview_and_outputs', 'Önizleme ve Çıkışlar'), style='Primary.TButton', command=self._open_preview_window).pack(side='left', padx=5)
        ttk.Button(panel, text=self.lm.tr('open_report', 'Raporu Aç'), style='Primary.TButton', command=self._open_last_report).pack(side='left', padx=5)

        tk.Label(
            self.content_frame,
            text=(
                f"{self.lm.tr('report_note', 'Not: DOCX için python-docx, Excel için openpyxl gereklidir.')}"
            ),
            bg='white',
            fg='#7f8c8d',
        ).pack(padx=15, pady=10, anchor='w')

    def _export_docx(self) -> None:
        try:
            period = self.report_period_cmb.get().strip()
            if not period:
                messagebox.showwarning(self.lm.tr('select_period', 'Dönem Seçimi'), self.lm.tr('error_select_period', 'Lütfen dönem seçin.'))
                return
            path = self.reporting.generate_water_footprint_report(self.company_id, period)
            self.last_water_report_path = path
            messagebox.showinfo('Rapor', f'DOCX rapor oluşturuldu:\n{path}')
        except Exception as e:
            messagebox.showerror('Hata', f'DOCX rapor oluşturulamadı: {e}')

    def _export_excel(self) -> None:
        try:
            period = self.report_period_cmb.get().strip()
            if not period:
                messagebox.showwarning(self.lm.tr('select_period', 'Dönem Seçimi'), self.lm.tr('error_select_period', 'Lütfen dönem seçin.'))
                return
            path = self.reporting.generate_excel_report(self.company_id, period)
            self.last_water_report_path = path
            messagebox.showinfo(self.lm.tr('report', 'Rapor'), f"{self.lm.tr('excel_report_created', 'Excel rapor oluşturuldu')}:\n{path}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('excel_report_error', 'Excel rapor oluşturulamadı')}: {e}")

    def _open_preview_window(self) -> None:
        try:
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr('preview_title', 'Su Raporu Önizleme'))
            win.geometry('900x600')
            top = tk.Frame(win, bg='white')
            top.pack(fill='x', padx=10, pady=6)
            ttk.Button(top, text=self.lm.tr('btn_close', 'Kapat'), style='Primary.TButton', command=win.destroy).pack(side='left')
            controls = tk.Frame(win, bg='white')
            controls.pack(fill='x', padx=10, pady=6)
            tk.Label(controls, text=f"{self.lm.tr('period', 'Dönem')}:", bg='white').pack(side='left')
            self.preview_period_var = tk.StringVar(value=self.report_period_cmb.get().strip() if hasattr(self, 'report_period_cmb') else '')
            period_entry = tk.Entry(controls, textvariable=self.preview_period_var, width=12)
            period_entry.pack(side='left', padx=8)
            self.water_report_text = tk.Text(win, height=20, wrap='word')
            r_scroll = ttk.Scrollbar(win, orient='vertical', command=self.water_report_text.yview)
            self.water_report_text.configure(yscrollcommand=r_scroll.set)
            self.water_report_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            r_scroll.pack(side='right', fill='y', pady=10)
            tools = tk.Frame(win, bg='white')
            tools.pack(fill='x', padx=10, pady=(0,10))
            ttk.Button(tools, text=self.lm.tr('fill_preview', 'Önizlemeyi Doldur'), style='Primary.TButton', command=self._fill_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('open', 'Aç'), style='Primary.TButton', command=self._open_last_report).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('save_txt', 'Kaydet (.txt)'), style='Primary.TButton', command=self._save_preview_text).pack(side='left', padx=4)
            ttk.Button(tools, text=self.lm.tr('print', 'Yazdır'), style='Primary.TButton', command=self._print_preview_text).pack(side='left', padx=4)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('preview_error', 'Önizleme penceresi hatası')}: {e}")

    def _fill_preview_text(self) -> None:
        try:
            period = self.preview_period_var.get().strip()
            if not period:
                messagebox.showwarning(self.lm.tr('select_period', 'Dönem Seçimi'), self.lm.tr('error_enter_period', 'Lütfen dönem girin.'))
                return
            data = self.manager.calculate_water_footprint(self.company_id, period)
            if not data:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('no_water_data_found', 'Su ayak izi verisi bulunamadı'))
                return
            self.water_report_text.delete('1.0', tk.END)
            self.water_report_text.insert(tk.END, f"{self.lm.tr('water_footprint_report', 'SU AYAK İZİ RAPORU')}\n")
            self.water_report_text.insert(tk.END, f"{self.lm.tr('period', 'Dönem')}: {period}\n")
            self.water_report_text.insert(tk.END, f"{self.lm.tr('total', 'Toplam')}: {data.get('total_water_footprint',0):.2f} m³\n")
            self.water_report_text.insert(tk.END, f"{self.lm.tr('blue', 'Mavi')}: {data.get('total_blue_water',0):.2f} m³\n")
            self.water_report_text.insert(tk.END, f"{self.lm.tr('green', 'Yeşil')}: {data.get('total_green_water',0):.2f} m³\n")
            self.water_report_text.insert(tk.END, f"{self.lm.tr('grey', 'Gri')}: {data.get('total_grey_water',0):.2f} m³\n\n")
            by_type = data.get('breakdown_by_type', {})
            for t, vals in by_type.items():
                self.water_report_text.insert(tk.END, f'{t}: {vals.get("total",0):.2f} m³ ({self.lm.tr("blue", "Mavi")} {vals.get("blue_water",0):.2f}, {self.lm.tr("green", "Yeşil")} {vals.get("green_water",0):.2f}, {self.lm.tr("grey", "Gri")} {vals.get("grey_water",0):.2f})\n')
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('preview_error', 'Önizleme hatası')}: {e}")

    def _save_preview_text(self) -> None:
        try:
            from tkinter import filedialog
            content = self.water_report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('empty_preview', 'Önizleme içeriği boş'))
                return
            out = filedialog.asksaveasfilename(
                title=self.lm.tr('save_report', "Raporu Kaydet"),
                defaultextension='.txt',
                filetypes=[(self.lm.tr('file_text', 'Metin'), '*.txt')]
            )
            if not out:
                return
            with open(out, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('preview_saved', 'Önizleme kaydedildi')}: {out}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('save_error', 'Kaydetme hatası')}: {e}")

    def _print_preview_text(self) -> None:
        try:
            import tempfile
            content = self.water_report_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('empty_preview', 'Önizleme içeriği boş'))
                return
            tmp = os.path.join(tempfile.gettempdir(), 'water_preview.txt')
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(content)
            try:
                os.startfile(tmp, 'print')
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('print_started', 'Yazdırma başlatıldı'))
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('print_error', 'Yazdırma hatası')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('print_prep_error', 'Yazdırmaya hazırlık hatası')}: {e}")

    def _open_last_report(self) -> None:
        try:
            path = getattr(self, 'last_water_report_path', None)
            if path and os.path.exists(path):
                os.startfile(path)
            else:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('no_report_found', 'Açılacak rapor bulunamadı'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('open_error', 'Açma hatası')}: {e}")

    # ==================== HEDEFLER ====================
    def build_targets_view(self) -> None:
        self.current_view = 'targets'
        self.content_title['text'] = self.lm.tr('water_targets', 'Su Hedefleri')
        self._clear_content()

        # Hedef ekleme formu
        form = tk.LabelFrame(self.content_frame, text=self.lm.tr('add_new_target', 'Yeni Hedef Ekle'), bg='white')
        form.pack(fill='x', padx=15, pady=10)

        def add_labeled_entry(parent, text, row, col=0, width=20) -> tk.Entry:
            tk.Label(parent, text=text, bg='white').grid(row=row, column=col, sticky='w', padx=5, pady=4)
            ent = tk.Entry(parent, width=width)
            ent.grid(row=row, column=col+1, sticky='w', padx=5, pady=4)
            return ent

        # Satır 0
        tk.Label(form, text=self.lm.tr('target_type', 'Hedef Türü'), bg='white').grid(row=0, column=0, sticky='w', padx=5, pady=4)
        self.target_type_cmb = ttk.Combobox(
            form,
            values=[
                'consumption_reduction',
                'efficiency_improvement',
                'recycling_increase',
            ],
            width=18,
        )
        self.target_type_cmb.grid(row=0, column=1, sticky='w', padx=5, pady=4)
        self.target_type_cmb.set('consumption_reduction')

        self.target_name_ent = add_labeled_entry(form, self.lm.tr('target_name', 'Hedef Adı'), 0, col=2)

        # Satır 1
        self.base_year_ent = add_labeled_entry(form, self.lm.tr('base_year', 'Baz Yıl'), 1)
        self.target_year_ent = add_labeled_entry(form, self.lm.tr('target_year', 'Hedef Yıl'), 1, col=2)
        self.base_value_ent = add_labeled_entry(form, self.lm.tr('base_value', 'Başlangıç Değeri'), 1, col=4)

        # Satır 2
        self.target_value_ent = add_labeled_entry(form, self.lm.tr('target_value', 'Hedef Değer'), 2)
        tk.Label(form, text=self.lm.tr('unit', 'Birim'), bg='white').grid(row=2, column=2, sticky='w', padx=5, pady=4)
        self.target_unit_cmb = ttk.Combobox(form, values=['m3', 'percentage', 'ratio'], width=18)
        self.target_unit_cmb.grid(row=2, column=3, sticky='w', padx=5, pady=4)
        self.target_unit_cmb.set('m3')

        tk.Label(form, text=self.lm.tr('sdg_alignment', 'SDG 6 Uyum'), bg='white').grid(row=2, column=4, sticky='w', padx=5, pady=4)
        self.sdg_alignment_cmb = ttk.Combobox(
            form,
            values=[
                'SDG 6.1',
                'SDG 6.2',
                'SDG 6.3',
                'SDG 6.4',
                'SDG 6.5',
                'SDG 6.6',
            ],
            width=18,
        )
        self.sdg_alignment_cmb.grid(row=2, column=5, sticky='w', padx=5, pady=4)
        self.sdg_alignment_cmb.set('SDG 6.4')

        # Satır 3
        self.target_responsible_ent = add_labeled_entry(form, self.lm.tr('responsible_person', 'Sorumlu Kişi'), 3)
        tk.Label(form, text=self.lm.tr('description', 'Açıklama'), bg='white').grid(row=3, column=2, sticky='nw', padx=5, pady=4)
        self.target_desc_txt = tk.Text(form, height=3, width=40)
        self.target_desc_txt.grid(row=3, column=3, columnspan=3, sticky='ew', padx=5, pady=4)

        # Butonlar
        btns = tk.Frame(form, bg='white')
        btns.grid(row=4, column=0, columnspan=6, sticky='e', padx=5, pady=8)
        ttk.Button(btns, text=self.lm.tr('add_target', 'Hedef Ekle'), style='Primary.TButton', command=self._save_target).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('update_target', 'Hedefi Güncelle'), style='Primary.TButton', command=self._update_target).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('clear', 'Temizle'), style='Primary.TButton', command=self._clear_target_form).pack(side='left', padx=5)

        # Hedef ilerleme takibi
        progress_frame = tk.LabelFrame(self.content_frame, text=self.lm.tr('target_progress_tracking', 'Hedef İlerleme Takibi'), bg='white')
        progress_frame.pack(fill='x', padx=15, pady=10)

        # İlerleme kartları
        progress_cards = tk.Frame(progress_frame, bg='white')
        progress_cards.pack(fill='x', padx=10, pady=10)

        self.progress_cards = {}
        progress_types = [
            (self.lm.tr('active_targets', 'Aktif Hedefler'), 'active', '#27ae60'),
            (self.lm.tr('completed_targets', 'Tamamlanan Hedefler'), 'completed', '#3498db'),
            (self.lm.tr('overdue_targets', 'Geciken Hedefler'), 'overdue', '#e74c3c'),
            (self.lm.tr('total_targets', 'Toplam Hedef'), 'total', '#9b59b6')
        ]

        for i, (title, key, color) in enumerate(progress_types):
            card = tk.Frame(progress_cards, bg=color, relief='raised', bd=2)
            card.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            progress_cards.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'), fg='white', bg=color).pack(pady=(8, 2))
            count_lbl = tk.Label(card, text='0', font=('Segoe UI', 16, 'bold'), fg='white', bg=color)
            count_lbl.pack(pady=(0, 8))
            self.progress_cards[key] = count_lbl

        # Hedef listesi
        list_frame = tk.LabelFrame(self.content_frame, text=self.lm.tr('current_targets', 'Mevcut Hedefler'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Treeview için frame ve scrollbar
        tree_frame = tk.Frame(list_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        cols = (
            'id',
            'target_name',
            'target_type',
            'base_year',
            'target_year',
            'base_value',
            'target_value',
            'unit',
            'sdg_alignment',
            'status',
            'progress',
            'days_remaining',
        )
        self.targets_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', height=12)

        # Sütun başlıkları
        headers = {
            'id': 'ID',
            'target_name': self.lm.tr('target_name', 'Hedef Adı'),
            'target_type': self.lm.tr('type', 'Tür'),
            'base_year': self.lm.tr('base_year', 'Baz Yıl'),
            'target_year': self.lm.tr('target_year', 'Hedef Yıl'),
            'base_value': self.lm.tr('start_value', 'Başlangıç'),
            'target_value': self.lm.tr('target', 'Hedef'),
            'unit': self.lm.tr('unit', 'Birim'),
            'sdg_alignment': 'SDG',
            'status': self.lm.tr('status', 'Durum'),
            'progress': self.lm.tr('progress', 'İlerleme'),
            'days_remaining': self.lm.tr('days_remaining', 'Kalan Gün')
        }

        for c in cols:
            self.targets_tree.heading(c, text=headers.get(c, c))
            if c == 'id':
                self.targets_tree.column(c, width=50, anchor='center')
            elif c == 'target_name':
                self.targets_tree.column(c, width=200, anchor='w')
            elif c in ['base_value', 'target_value', 'progress']:
                self.targets_tree.column(c, width=80, anchor='center')
            elif c == 'days_remaining':
                self.targets_tree.column(c, width=100, anchor='center')
            else:
                self.targets_tree.column(c, width=100, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.targets_tree.yview)
        self.targets_tree.configure(yscrollcommand=scrollbar.set)

        self.targets_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Liste işlemleri
        action_frame = tk.Frame(list_frame, bg='white')
        action_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(action_frame, text=f" {self.lm.tr('progress_analysis', 'İlerleme Analizi')}", style='Primary.TButton', command=self._analyze_target_progress).pack(side='left', padx=2)
        ttk.Button(action_frame, text=f" {self.lm.tr('visualize', 'Görselleştir')}", style='Primary.TButton', command=self._visualize_targets).pack(side='left', padx=2)
        ttk.Button(action_frame, text=f"️ {self.lm.tr('btn_edit', 'Düzenle')}", style='Primary.TButton', command=self._edit_target).pack(side='left', padx=2)
        if self.is_admin:
            ttk.Button(action_frame, text=f"️ {self.lm.tr('btn_delete', 'Sil')}", style='Primary.TButton', command=self._delete_target).pack(side='left', padx=2)

        self._refresh_targets_list()

    def _clear_target_form(self) -> None:
        self.target_name_ent.delete(0, 'end')
        self.base_year_ent.delete(0, 'end')
        self.target_year_ent.delete(0, 'end')
        self.base_value_ent.delete(0, 'end')
        self.target_value_ent.delete(0, 'end')
        self.target_responsible_ent.delete(0, 'end')
        self.target_desc_txt.delete('1.0', 'end')
        self.current_target_id = None

    def _save_target(self) -> None:
        try:
            target_name = self.target_name_ent.get().strip()
            if not target_name:
                messagebox.showwarning(self.lm.tr('missing_info', 'Eksik Bilgi'), self.lm.tr('target_name_required', 'Hedef adı zorunludur.'))
                return

            target_id = self.manager.add_water_target(
                company_id=self.company_id,
                target_type=self.target_type_cmb.get(),
                target_name=target_name,
                base_year=int(self.base_year_ent.get() or 2024),
                target_year=int(self.target_year_ent.get() or 2025),
                base_value=float(self.base_value_ent.get() or 0),
                target_value=float(self.target_value_ent.get() or 0),
                target_unit=self.target_unit_cmb.get(),
                sdg_alignment=self.sdg_alignment_cmb.get(),
                responsible_person=self.target_responsible_ent.get().strip() or None,
                description=self.target_desc_txt.get('1.0', 'end').strip() or None
            )

            if target_id:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), f"{self.lm.tr('target_added', 'Hedef eklendi')} (ID: {target_id}).")
                self._refresh_targets_list()
                self._clear_target_form()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('target_add_error', 'Hedef eklenemedi.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('target_add_exception', 'Hedef eklenirken sorun')}: {e}")

    def _refresh_targets_list(self) -> None:
        try:
            for i in self.targets_tree.get_children():
                self.targets_tree.delete(i)
            targets = self.manager.get_water_targets(self.company_id)

            # İlerleme kartlarını güncelle
            active_count = 0
            completed_count = 0
            overdue_count = 0

            for t in targets:
                # Hedef durumunu kontrol et
                status = t.get('status', 'active')
                if status == 'completed':
                    completed_count += 1
                elif status == 'overdue':
                    overdue_count += 1
                else:
                    active_count += 1

                # Kalan günleri hesapla
                days_remaining = self._calculate_days_remaining(t.get('target_year'), t.get('status'))

                self.targets_tree.insert('', 'end', values=(
                    t['id'], t['target_name'], t['target_type'], t['base_year'], t['target_year'],
                    t['base_value'], t['target_value'], t['target_unit'], t['sdg_alignment'],
                    status, f"{t['progress_percentage']:.1f}%", days_remaining
                ))

            # İlerleme kartlarını güncelle
            self.progress_cards['active']['text'] = str(active_count)
            self.progress_cards['completed']['text'] = str(completed_count)
            self.progress_cards['overdue']['text'] = str(overdue_count)
            self.progress_cards['total']['text'] = str(len(targets))

            self._log_activity(f"{self.lm.tr('target_list_updated', 'Hedef listesi güncellendi')}: {len(targets)} {self.lm.tr('target', 'hedef')}")

        except Exception as e:
            self._log_activity(f"{self.lm.tr('target_list_error', 'Hedef listesi hatası')}: {e}", level="ERROR")

    def _calculate_days_remaining(self, target_year, status) -> str:
        """Hedef yılına kalan günleri hesapla"""
        try:
            if status == 'completed':
                return self.lm.tr('completed', 'Tamamlandı')

            from datetime import datetime
            current_year = datetime.now().year

            if target_year and target_year > current_year:
                # Gelecek yıl için tahmini gün sayısı
                days_left = (target_year - current_year) * 365
                return f"{days_left} {self.lm.tr('days', 'gün')}"
            elif target_year and target_year < current_year:
                return self.lm.tr('overdue', 'Gecikti')
            else:
                return self.lm.tr('this_year', 'Bu yıl')
        except Exception:
            return self.lm.tr('no_data', 'Veri Yok')

    def _analyze_target_progress(self) -> None:
        """Hedef ilerleme analizi göster"""
        try:
            targets = self.manager.get_water_targets(self.company_id)
            if not targets:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('no_targets_to_analyze', 'Analiz edilecek hedef bulunamadı.'))
                return

            # Analiz penceresi
            analysis_window = tk.Toplevel(self.parent)
            analysis_window.title(self.lm.tr('target_progress_analysis', "Hedef İlerleme Analizi"))
            analysis_window.geometry("700x600")
            analysis_window.configure(bg='white')

            # Analiz içeriği
            analysis_text = f"""
 {self.lm.tr('target_progress_analysis_title', 'HEDEF İLERLEME ANALİZİ')}

 {self.lm.tr('general_status', 'GENEL DURUM')}:
• {self.lm.tr('total_targets', 'Toplam Hedef')}: {len(targets)}
• {self.lm.tr('active_targets', 'Aktif Hedef')}: {len([t for t in targets if t.get('status') == 'active'])}
• {self.lm.tr('completed', 'Tamamlanan')}: {len([t for t in targets if t.get('status') == 'completed'])}
• {self.lm.tr('overdue', 'Geciken')}: {len([t for t in targets if t.get('status') == 'overdue'])}

 {self.lm.tr('target_type_distribution', 'HEDEF TÜRÜ DAĞILIMI')}:
"""

            # Hedef türü analizi
            target_types: dict[str, int] = {}
            for t in targets:
                target_type = t.get('target_type', 'unknown')
                target_types[target_type] = target_types.get(target_type, 0) + 1

            for target_type, count in target_types.items():
                percentage = (count / len(targets)) * 100
                analysis_text += f"• {target_type}: {count} {self.lm.tr('target', 'hedef')} ({percentage:.1f}%)\n"

            analysis_text += f"""
 {self.lm.tr('year_based_distribution', 'YIL BAZLI DAĞILIM')}:
 """

            # Yıl bazlı analiz
            year_analysis: dict[str, int] = {}
            for t in targets:
                year = t.get('target_year', self.lm.tr('no_data', 'Veri Yok'))
                year_analysis[year] = year_analysis.get(year, 0) + 1

            for year, count in sorted(year_analysis.items()):
                analysis_text += f"• {year}: {count} {self.lm.tr('target', 'hedef')}\n"

            analysis_text += f"""
 {self.lm.tr('sdg_alignment_analysis', 'SDG UYUM ANALİZİ')}:
 """

            # SDG analizi
            sdg_analysis: dict[str, int] = {}
            for t in targets:
                sdg = t.get('sdg_alignment', self.lm.tr('no_data', 'Veri Yok'))
                sdg_analysis[sdg] = sdg_analysis.get(sdg, 0) + 1

            for sdg, count in sorted(sdg_analysis.items()):
                analysis_text += f"• {sdg}: {count} {self.lm.tr('target', 'hedef')}\n"

            analysis_text += f"""
 {self.lm.tr('average_progress_title', 'ORTALAMA İLERLEME')}:
 """

            # İlerleme analizi
            total_progress = sum(t.get('progress_percentage', 0) for t in targets)
            avg_progress = total_progress / len(targets) if targets else 0
            analysis_text += f"• {self.lm.tr('average_progress', 'Ortalama İlerleme')}: {avg_progress:.1f}%\n"

            # En iyi ve en kötü performans
            if targets:
                best_target = max(targets, key=lambda t: t.get('progress_percentage', 0))
                worst_target = min(targets, key=lambda t: t.get('progress_percentage', 0))

                best_name = best_target.get('target_name', self.lm.tr('no_data', 'Veri Yok'))
                best_val = best_target.get('progress_percentage', 0)
                worst_name = worst_target.get('target_name', self.lm.tr('no_data', 'Veri Yok'))
                worst_val = worst_target.get('progress_percentage', 0)
                analysis_text += f"• {self.lm.tr('best_performance', 'En İyi Performans')}: {best_name} ({best_val:.1f}%)\n"
                analysis_text += f"• {self.lm.tr('worst_performance', 'En Düşük Performans')}: {worst_name} ({worst_val:.1f}%)\n"

            analysis_text += f"""

 {self.lm.tr('recommendations_title', 'ÖNERİLER')}:
{self._generate_target_recommendations(targets)}

═══════════════════════════════════════════════════

 {self.lm.tr('detailed_target_list', 'DETAYLI HEDEF LİSTESİ')}:
"""

            # Detaylı hedef listesi
            for i, t in enumerate(targets, 1):
                status_emoji = {
                    'active': '',
                    'completed': '',
                    'overdue': ''
                }.get(t.get('status', 'active'), '')

                analysis_text += f"""
{i}. {status_emoji} {t.get('target_name', self.lm.tr('no_data', 'Veri Yok'))}
   {self.lm.tr('type', 'Tür')}: {t.get('target_type', self.lm.tr('no_data', 'Veri Yok'))}
   {self.lm.tr('status', 'Durum')}: {t.get('status', self.lm.tr('no_data', 'Veri Yok'))}
   {self.lm.tr('progress', 'İlerleme')}: {t.get('progress_percentage', 0):.1f}%
   SDG: {t.get('sdg_alignment', self.lm.tr('no_data', 'Veri Yok'))}
   {self.lm.tr('target_year', 'Hedef Yıl')}: {t.get('target_year', self.lm.tr('no_data', 'Veri Yok'))}
"""

            # Text widget
            text_widget = tk.Text(analysis_window, wrap='word', font=('Segoe UI', 10), bg='#f8f9fa', relief='flat')
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            text_widget.insert('1.0', analysis_text.strip())
            text_widget.configure(state='disabled')

            # Kapatma butonu
            ttk.Button(analysis_window, text=self.lm.tr('btn_close', 'Kapat'), style='Primary.TButton', command=analysis_window.destroy).pack(pady=10)

            self._log_activity(self.lm.tr('target_analysis_viewed', "Hedef ilerleme analizi görüntülendi"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('analysis_error', 'Analiz hatası')}: {e}")
            self._log_activity(f"{self.lm.tr('analysis_exception', 'Hedef analizi hatası')}: {e}", level="ERROR")

    def _visualize_targets(self) -> None:
        """Hedef görselleştirmesi (basit metin tabanlı)"""
        try:
            targets = self.manager.get_water_targets(self.company_id)
            if not targets:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('no_targets_to_visualize', 'Görselleştirilecek hedef bulunamadı.'))
                return

            # Görselleştirme penceresi
            viz_window = tk.Toplevel(self.parent)
            viz_window.title(self.lm.tr('target_visualization', "Hedef Görselleştirmesi"))
            viz_window.geometry("800x500")
            viz_window.configure(bg='white')

            # Görselleştirme içeriği
            viz_text = f"""
 {self.lm.tr('target_visualization_title', 'HEDEF GÖRSELLEŞTİRMESİ')}
 
 {self.lm.tr('progress_bars', 'İLERLEME ÇUBUKLARI')}:
 """

            for t in targets:
                progress = t.get('progress_percentage', 0)
                status = t.get('status', 'active')

                # İlerleme çubuğu oluştur
                bar_length = 30
                filled_length = int((progress / 100) * bar_length)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)

                # Durum emojisi
                status_emoji = {
                    'active': '',
                    'completed': '',
                    'overdue': ''
                }.get(status, '')

                viz_text += f"""
{status_emoji} {t.get('target_name', self.lm.tr('no_data', 'Veri Yok'))[:30]:<30}
   [{bar}] {progress:5.1f}%
   SDG: {t.get('sdg_alignment', self.lm.tr('no_data', 'Veri Yok'))} | {self.lm.tr('year', 'Yıl')}: {t.get('target_year', self.lm.tr('no_data', 'Veri Yok'))}
"""

            viz_text += f"""
 
 {self.lm.tr('statistics', 'İSTATİSTİKLER')}:
 """

            # İstatistikler
            total_targets = len(targets)
            completed = len([t for t in targets if t.get('status') == 'completed'])
            active = len([t for t in targets if t.get('status') == 'active'])
            overdue = len([t for t in targets if t.get('status') == 'overdue'])

            completion_rate = (completed / total_targets * 100) if total_targets > 0 else 0

            viz_text += f"""
• {self.lm.tr('completion_rate', 'Tamamlanma Oranı')}: {completion_rate:.1f}% ({completed}/{total_targets})
• {self.lm.tr('active_targets', 'Aktif Hedefler')}: {active}
• {self.lm.tr('overdue_targets', 'Geciken Hedefler')}: {overdue}

 {self.lm.tr('year_based_distribution', 'YIL BAZLI DAĞILIM')}:
"""

            # Yıl bazlı görselleştirme
            year_targets: dict[str, list] = {}
            for t in targets:
                year = t.get('target_year', self.lm.tr('no_data', 'Veri Yok'))
                if year not in year_targets:
                    year_targets[year] = []
                year_targets[year].append(t)

            for year in sorted(year_targets.keys()):
                year_target_list = year_targets[year]
                viz_text += f"\n {year} ({len(year_target_list)} {self.lm.tr('target', 'hedef')}):\n"
                for t in year_target_list:
                    progress = t.get('progress_percentage', 0)
                    bar = '█' * int(progress / 5) + '░' * (20 - int(progress / 5))
                    viz_text += f"   {t.get('target_name', self.lm.tr('no_data', 'Veri Yok'))[:25]:<25} [{bar}] {progress:5.1f}%\n"

            # Text widget
            text_widget = tk.Text(viz_window, wrap='word', font=('Consolas', 9), bg='#f8f9fa', relief='flat')
            text_widget.pack(fill='both', expand=True, padx=20, pady=20)
            text_widget.insert('1.0', viz_text.strip())
            text_widget.configure(state='disabled')

            # Kapatma butonu
            ttk.Button(viz_window, text=self.lm.tr('btn_close', 'Kapat'), style='Primary.TButton', command=viz_window.destroy).pack(pady=10)

            self._log_activity(self.lm.tr('target_visualization_created', "Hedef görselleştirmesi oluşturuldu"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('visualization_error', 'Görselleştirme hatası')}: {e}")
            self._log_activity(f"{self.lm.tr('visualization_exception', 'Hedef görselleştirme hatası')}: {e}", level="ERROR")

    def _generate_target_recommendations(self, targets) -> str:
        """Hedef önerileri oluştur"""
        recommendations = []

        # Genel öneriler
        if not targets:
            recommendations.append(f"• {self.lm.tr('rec_set_first_targets', 'İlk hedeflerinizi belirleyin')}")
            return '\n'.join(recommendations)

        # İlerleme analizi
        avg_progress = sum(t.get('progress_percentage', 0) for t in targets) / len(targets)

        if avg_progress < 30:
            recommendations.append(f"• {self.lm.tr('rec_low_progress', 'Genel ilerleme düşük, hedefleri gözden geçirin')}")
        elif avg_progress < 60:
            recommendations.append(f"• {self.lm.tr('rec_medium_progress', 'İlerleme orta seviyede, motivasyonu artırın')}")
        else:
            recommendations.append(f"• {self.lm.tr('rec_good_progress', 'İlerleme iyi durumda, bu performansı sürdürün')}")

        # Durum analizi
        overdue_count = len([t for t in targets if t.get('status') == 'overdue'])
        if overdue_count > 0:
            recommendations.append(f"• {self.lm.tr('rec_overdue_targets', '{count} geciken hedef var, öncelik verin').format(count=overdue_count)}")

        # Yıl analizi
        current_year = 2024  # Varsayılan
        this_year_targets = [t for t in targets if t.get('target_year') == current_year]
        if this_year_targets:
            low_progress = [t for t in this_year_targets if t.get('progress_percentage', 0) < 50]
            if low_progress:
                recommendations.append(f"• {self.lm.tr('rec_low_progress_this_year', 'Bu yıl için {count} hedef düşük ilerlemede').format(count=len(low_progress))}")

        # SDG analizi
        sdg_targets = [t for t in targets if t.get('sdg_alignment')]
        if len(sdg_targets) < len(targets) * 0.7:
            recommendations.append(f"• {self.lm.tr('rec_more_sdg_targets', 'Daha fazla SDG uyumlu hedef belirleyin')}")

        return '\n'.join(recommendations) if recommendations else f"• {self.lm.tr('rec_targets_good', 'Hedefleriniz iyi durumda!')}"

    def _edit_target(self) -> None:
        try:
            sel = self.targets_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('select_target_to_edit', 'Lütfen düzenlemek için bir hedef seçin.'))
                return
            item = self.targets_tree.item(sel[0])
            target_id = item['values'][0]
            targets = self.manager.get_water_targets(self.company_id)
            t = next((x for x in targets if x['id'] == target_id), None)
            if not t:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('target_details_error', 'Hedef detayları getirilemedi.'))
                return
            self.current_target_id = int(target_id)
            self.target_type_cmb.set(t.get('target_type') or 'consumption_reduction')
            self.target_name_ent.delete(0, 'end')
            self.target_name_ent.insert(0, t.get('target_name') or '')
            self.base_year_ent.delete(0, 'end')
            self.base_year_ent.insert(0, str(t.get('base_year') or ''))
            self.target_year_ent.delete(0, 'end')
            self.target_year_ent.insert(0, str(t.get('target_year') or ''))
            self.base_value_ent.delete(0, 'end')
            self.base_value_ent.insert(0, str(t.get('base_value') or ''))
            self.target_value_ent.delete(0, 'end')
            self.target_value_ent.insert(0, str(t.get('target_value') or ''))
            self.target_unit_cmb.set(t.get('target_unit') or 'm3')
            self.sdg_alignment_cmb.set(t.get('sdg_alignment') or 'SDG 6.4')
            self.target_responsible_ent.delete(0, 'end')
            self.target_responsible_ent.insert(0, t.get('responsible_person') or '')
            self.target_desc_txt.delete('1.0', 'end')
            self.target_desc_txt.insert('1.0', t.get('description') or '')
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), f"{self.lm.tr('target_edit_mode', 'Hedef #{id} düzenleme modunda.').format(id=target_id)}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('edit_error', 'Düzenleme sırasında sorun')}: {e}")

    def _update_target(self) -> None:
        try:
            if not self.current_target_id:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('select_target_to_update', 'Güncellemek için önce bir hedef seçip düzenleyin.'))
                return
            updates = {
                'target_type': self.target_type_cmb.get() or None,
                'target_name': self.target_name_ent.get().strip() or None,
                'base_year': int(self.base_year_ent.get()) if self.base_year_ent.get() else None,
                'target_year': int(self.target_year_ent.get()) if self.target_year_ent.get() else None,
                'base_value': self._to_float(self.base_value_ent.get()),
                'target_value': self._to_float(self.target_value_ent.get()),
                'target_unit': self.target_unit_cmb.get() or None,
                'sdg_alignment': self.sdg_alignment_cmb.get() or None,
                'responsible_person': self.target_responsible_ent.get().strip() or None,
                'description': self.target_desc_txt.get('1.0', 'end').strip() or None,
            }
            ok = self.manager.update_water_target(
                self.current_target_id,
                **{k: v for k, v in updates.items() if v is not None},
            )
            if ok:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('target_updated', 'Hedef güncellendi.'))
                self._refresh_targets_list()
                self._clear_target_form()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('target_update_error', 'Hedef güncellenemedi.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('update_error', 'Güncelleme sırasında sorun')}: {e}")

    def _delete_target(self) -> None:
        try:
            # Admin kontrolü
            if not self.is_admin:
                messagebox.showwarning(self.lm.tr('permission_error', 'Yetki Hatası'), self.lm.tr('admin_required', 'Bu işlem için admin veya super_admin yetkisi gereklidir.'))
                return

            sel = self.targets_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('select_target_to_delete', 'Lütfen silmek için bir hedef seçin.'))
                return
            item = self.targets_tree.item(sel[0])
            target_id = item['values'][0]
            if messagebox.askyesno(self.lm.tr('confirmation', 'Onay'), f"{self.lm.tr('delete_target_confirm', 'Hedef #{id} silinsin mi?').format(id=target_id)}"):
                try:
                    self.manager.delete_water_target(int(target_id))
                    messagebox.showinfo(self.lm.tr('success', 'Başarılı'), f"{self.lm.tr('target_deleted', 'Hedef #{id} silindi.').format(id=target_id)}")
                except Exception as e:
                    messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('target_delete_error', 'Hedef silinemedi')}: {e}")
                self._refresh_targets_list()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('delete_error', 'Silme sırasında sorun')}: {e}")

    # ==================== KALİTE İZLEME ====================
    def build_quality_view(self) -> None:
        self.current_view = 'quality'
        self.content_title['text'] = self.lm.tr('water_quality_monitoring', 'Su Kalitesi İzleme')
        self._clear_content()

        # Kalite ölçümü formu
        form = tk.LabelFrame(self.content_frame, text=self.lm.tr('new_quality_measurement', 'Yeni Kalite Ölçümü'), bg='white')
        form.pack(fill='x', padx=15, pady=10)

        def add_labeled_entry(parent, text, row, col=0, width=20) -> tk.Entry:
            tk.Label(parent, text=text, bg='white').grid(row=row, column=col, sticky='w', padx=5, pady=4)
            ent = tk.Entry(parent, width=width)
            ent.grid(row=row, column=col+1, sticky='w', padx=5, pady=4)
            return ent

        # Satır 0
        self.q_date_ent = add_labeled_entry(form, self.lm.tr('measurement_date_format', 'Ölçüm Tarihi (YYYY-MM-DD)'), 0)
        tk.Label(form, text=self.lm.tr('water_source', 'Su Kaynağı'), bg='white').grid(row=0, column=2, sticky='w', padx=5, pady=4)
        self.q_source_cmb = ttk.Combobox(form, values=['intake', 'discharge', 'process', 'recycled'], width=18)
        self.q_source_cmb.grid(row=0, column=3, sticky='w', padx=5, pady=4)
        self.q_source_cmb.set('intake')

        self.q_location_ent = add_labeled_entry(form, self.lm.tr('location', 'Lokasyon'), 0, col=4)

        # Satır 1
        tk.Label(form, text=self.lm.tr('parameter', 'Parametre'), bg='white').grid(row=1, column=0, sticky='w', padx=5, pady=4)
        self.q_param_cmb = ttk.Combobox(
            form,
            values=['pH', 'TDS', 'BOD', 'COD', 'TSS', 'Chloride', 'Nitrogen', 'Phosphorus'],
            width=18,
        )
        self.q_param_cmb.grid(row=1, column=1, sticky='w', padx=5, pady=4)
        self.q_param_cmb.set('pH')

        self.q_value_ent = add_labeled_entry(form, self.lm.tr('value', 'Değer'), 1, col=2)
        self.q_unit_ent = add_labeled_entry(form, self.lm.tr('unit', 'Birim'), 1, col=4)

        # Satır 2
        self.q_limit_ent = add_labeled_entry(form, self.lm.tr('standard_limit', 'Standart Limit'), 2)
        tk.Label(form, text=self.lm.tr('compliance', 'Uyumluluk'), bg='white').grid(row=2, column=2, sticky='w', padx=5, pady=4)
        self.q_compliance_cmb = ttk.Combobox(form, values=['compliant', 'non_compliant', 'warning'], width=18)
        self.q_compliance_cmb.grid(row=2, column=3, sticky='w', padx=5, pady=4)
        self.q_compliance_cmb.set('compliant')

        self.q_lab_ent = add_labeled_entry(form, self.lm.tr('laboratory', 'Laboratuvar'), 2, col=4)

        # Butonlar
        btns = tk.Frame(form, bg='white')
        btns.grid(row=3, column=0, columnspan=6, sticky='e', padx=5, pady=8)
        ttk.Button(btns, text=self.lm.tr('add_measurement', 'Ölçüm Ekle'), style='Primary.TButton', command=self._save_quality).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('update_measurement', 'Ölçümü Güncelle'), style='Primary.TButton', command=self._update_quality).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('clear', 'Temizle'), style='Primary.TButton', command=self._clear_quality_form).pack(side='left', padx=5)

        # Kalite ölçüm listesi
        list_frame = tk.LabelFrame(self.content_frame, text=self.lm.tr('quality_measurements', 'Kalite Ölçümleri'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=15, pady=10)

        cols = (
            'id', 'monitoring_date', 'water_source', 'location',
            'parameter_name', 'parameter_value', 'unit', 'standard_limit',
            'compliance_status', 'responsible_lab'
        )
        self.quality_tree = ttk.Treeview(list_frame, columns=cols, show='headings')
        for c in cols:
            self.quality_tree.heading(c, text=c)
            self.quality_tree.column(c, width=100, anchor='center')
        self.quality_tree.pack(fill='both', expand=True)

        # Liste işlemleri
        ttk.Button(list_frame, text=self.lm.tr('edit_selected_measurement', 'Seçili Ölçümü Düzenle'), style='Primary.TButton', command=self._edit_quality).pack(side='right', padx=5, pady=5)
        if self.is_admin:
            ttk.Button(list_frame, text=self.lm.tr('delete_selected_measurement', 'Seçili Ölçümü Sil'), style='Primary.TButton', command=self._delete_quality).pack(side='right', padx=5, pady=5)

        self._refresh_quality_list()

    def _clear_quality_form(self) -> None:
        self.q_date_ent.delete(0, 'end')
        self.q_location_ent.delete(0, 'end')
        self.q_value_ent.delete(0, 'end')
        self.q_unit_ent.delete(0, 'end')
        self.q_limit_ent.delete(0, 'end')
        self.q_lab_ent.delete(0, 'end')
        self.current_quality_id = None

    def _save_quality(self) -> None:
        try:
            monitoring_date = self.q_date_ent.get().strip()
            if not monitoring_date:
                messagebox.showwarning(self.lm.tr('missing_info', 'Eksik Bilgi'), self.lm.tr('measurement_date_required', 'Ölçüm tarihi zorunludur.'))
                return

            from datetime import datetime
            md = datetime.strptime(monitoring_date, "%Y-%m-%d").date()

            quality_id = self.manager.add_quality_measurement(
                company_id=self.company_id,
                monitoring_date=md,
                water_source=self.q_source_cmb.get(),
                location=self.q_location_ent.get().strip(),
                parameter_name=self.q_param_cmb.get(),
                parameter_value=float(self.q_value_ent.get() or 0),
                parameter_unit=self.q_unit_ent.get().strip() or "",
                standard_limit=float(self.q_limit_ent.get() or 0) if self.q_limit_ent.get() else None,
                compliance_status=self.q_compliance_cmb.get(),
                responsible_lab=self.q_lab_ent.get().strip() or ""
            )

            if quality_id:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('quality_measurement_added', 'Kalite ölçümü eklendi (ID: {quality_id}).').format(quality_id=quality_id))
                self._refresh_quality_list()
                self._clear_quality_form()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('quality_measurement_add_error', 'Kalite ölçümü eklenemedi.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('quality_measurement_add_exception', 'Kalite ölçümü eklenirken sorun')}: {e}")

    def _edit_quality(self) -> None:
        try:
            sel = self.quality_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('select_measurement_to_edit', 'Lütfen düzenlemek için bir ölçüm seçin.'))
                return
            item = self.quality_tree.item(sel[0])
            q_id = item['values'][0]
            measurements = self.manager.get_quality_measurements(self.company_id)
            m = next((x for x in measurements if x['id'] == q_id), None)
            if not m:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('measurement_details_error', 'Ölçüm detayları getirilemedi.'))
                return
            self.current_quality_id = int(q_id)
            self.q_date_ent.delete(0, 'end')
            self.q_date_ent.insert(0, m.get('monitoring_date') or '')
            self.q_source_cmb.set(m.get('water_source') or 'intake')
            self.q_location_ent.delete(0, 'end')
            self.q_location_ent.insert(0, m.get('location') or '')
            self.q_param_cmb.set(m.get('parameter_name') or 'pH')
            self.q_value_ent.delete(0, 'end')
            self.q_value_ent.insert(0, str(m.get('parameter_value') or ''))
            self.q_unit_ent.delete(0, 'end')
            self.q_unit_ent.insert(0, m.get('parameter_unit') or '')
            self.q_limit_ent.delete(0, 'end')
            self.q_limit_ent.insert(0, str(m.get('standard_limit') or ''))
            self.q_compliance_cmb.set(m.get('compliance_status') or 'compliant')
            self.q_lab_ent.delete(0, 'end')
            self.q_lab_ent.insert(0, m.get('responsible_lab') or '')
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('measurement_edit_mode', 'Ölçüm #{q_id} düzenleme modunda.').format(q_id=q_id))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('edit_error', 'Düzenleme sırasında sorun')}: {e}")

    def _update_quality(self) -> None:
        try:
            if not self.current_quality_id:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('select_measurement_first', 'Güncellemek için önce bir ölçüm seçip düzenleyin.'))
                return
            updates = {
                'monitoring_date': self.q_date_ent.get().strip() or None,
                'water_source': self.q_source_cmb.get() or None,
                'location': self.q_location_ent.get().strip() or None,
                'parameter_name': self.q_param_cmb.get() or None,
                'parameter_value': self._to_float(self.q_value_ent.get()),
                'parameter_unit': self.q_unit_ent.get().strip() or None,
                'standard_limit': self._to_float(self.q_limit_ent.get()),
                'compliance_status': self.q_compliance_cmb.get() or None,
                'responsible_lab': self.q_lab_ent.get().strip() or None,
            }
            ok = self.manager.update_quality_measurement(
                self.current_quality_id,
                **{k: v for k, v in updates.items() if v is not None},
            )
            if ok:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('measurement_updated', 'Ölçüm güncellendi.'))
                self._refresh_quality_list()
                self._clear_quality_form()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('measurement_update_error', 'Ölçüm güncellenemedi.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('update_error', 'Güncelleme sırasında sorun')}: {e}")

    def _refresh_quality_list(self) -> None:
        try:
            for i in self.quality_tree.get_children():
                self.quality_tree.delete(i)
            measurements = self.manager.get_quality_measurements(self.company_id)
            for m in measurements:
                self.quality_tree.insert('', 'end', values=(
                    m['id'], m['monitoring_date'], m['water_source'], m['location'],
                    m['parameter_name'], m['parameter_value'], m['parameter_unit'],
                    m['standard_limit'], m['compliance_status'], m['responsible_lab']
                ))
        except Exception as e:
            logging.error(f"{self.lm.tr('quality_list_error', 'Kalite listesi hatası')}: {e}")

    def _delete_quality(self) -> None:
        try:
            # Admin kontrolü
            if not self.is_admin:
                messagebox.showwarning(self.lm.tr('permission_error', 'Yetki Hatası'), self.lm.tr('admin_required', 'Bu işlem için admin veya super_admin yetkisi gereklidir.'))
                return

            sel = self.quality_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('select_measurement_to_delete', 'Lütfen silmek için bir ölçüm seçin.'))
                return
            item = self.quality_tree.item(sel[0])
            quality_id = item['values'][0]
            if messagebox.askyesno(self.lm.tr('confirmation', 'Onay'), self.lm.tr('delete_measurement_confirm', 'Ölçüm #{quality_id} silinsin mi?').format(quality_id=quality_id)):
                try:
                    self.manager.delete_quality_measurement(int(quality_id))
                    messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('measurement_deleted', 'Ölçüm #{quality_id} silindi.').format(quality_id=quality_id))
                except Exception as e:
                    messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('delete_error', 'Ölçüm silinemedi')}: {e}")
                self._refresh_quality_list()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('delete_exception', 'Silme sırasında sorun')}: {e}")

    # ==================== VERİMLİLİK PROJELERİ ====================
    def build_projects_view(self) -> None:
        self.current_view = 'projects'
        self.content_title['text'] = self.lm.tr('efficiency_projects', 'Verimlilik Projeleri')
        self._clear_content()

        # Proje formu
        form = tk.LabelFrame(self.content_frame, text=self.lm.tr('new_project', 'Yeni Proje Ekle'), bg='white')
        form.pack(fill='x', padx=15, pady=10)

        def add_labeled_entry(parent, text, row, col=0, width=20) -> tk.Entry:
            tk.Label(parent, text=text, bg='white').grid(row=row, column=col, sticky='w', padx=5, pady=4)
            ent = tk.Entry(parent, width=width)
            ent.grid(row=row, column=col+1, sticky='w', padx=5, pady=4)
            return ent

        # Satır 0
        self.p_name_ent = add_labeled_entry(form, self.lm.tr('project_name', 'Proje Adı'), 0)
        tk.Label(form, text=self.lm.tr('project_type', 'Proje Türü'), bg='white').grid(row=0, column=2, sticky='w', padx=5, pady=4)
        self.p_type_cmb = ttk.Combobox(
            form,
            values=['recycling', 'reuse', 'reduction', 'treatment', 'efficiency'],
            width=18,
        )
        self.p_type_cmb.grid(row=0, column=3, sticky='w', padx=5, pady=4)
        self.p_type_cmb.set('recycling')

        tk.Label(form, text=self.lm.tr('status', 'Durum'), bg='white').grid(row=0, column=4, sticky='w', padx=5, pady=4)
        self.p_status_cmb = ttk.Combobox(
            form,
            values=['planned', 'ongoing', 'completed', 'cancelled'],
            width=18,
        )
        self.p_status_cmb.grid(row=0, column=5, sticky='w', padx=5, pady=4)
        self.p_status_cmb.set('planned')

        # Satır 1
        self.p_investment_ent = add_labeled_entry(form, self.lm.tr('investment_amount', 'Yatırım Tutarı (TL)'), 1)
        self.p_savings_ent = add_labeled_entry(form, self.lm.tr('expected_savings', 'Beklenen Tasarruf (m³)'), 1, col=2)
        self.p_efficiency_ent = add_labeled_entry(form, self.lm.tr('expected_efficiency', 'Beklenen Verimlilik (%)'), 1, col=4)

        # Satır 2
        self.p_start_ent = add_labeled_entry(form, self.lm.tr('start_date', 'Başlangıç Tarihi'), 2)
        self.p_end_ent = add_labeled_entry(form, self.lm.tr('end_date', 'Bitiş Tarihi'), 2, col=2)
        self.p_responsible_ent = add_labeled_entry(form, self.lm.tr('responsible_person', 'Sorumlu Kişi'), 2, col=4)

        # Satır 3
        tk.Label(form, text=self.lm.tr('description', 'Açıklama'), bg='white').grid(row=3, column=0, sticky='nw', padx=5, pady=4)
        self.p_desc_txt = tk.Text(form, height=3, width=70)
        self.p_desc_txt.grid(row=3, column=1, columnspan=5, sticky='ew', padx=5, pady=4)

        # Butonlar
        btns = tk.Frame(form, bg='white')
        btns.grid(row=4, column=0, columnspan=6, sticky='e', padx=5, pady=8)
        ttk.Button(btns, text=self.lm.tr('add_project', 'Proje Ekle'), style='Primary.TButton', command=self._save_project).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('update_project', 'Projeyi Güncelle'), style='Primary.TButton', command=self._update_project).pack(side='left', padx=5)
        ttk.Button(btns, text=self.lm.tr('clear', 'Temizle'), style='Primary.TButton', command=self._clear_project_form).pack(side='left', padx=5)

        # Proje listesi
        list_frame = tk.LabelFrame(self.content_frame, text=self.lm.tr('existing_projects', 'Mevcut Projeler'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=15, pady=10)

        cols = (
            'id',
            'project_name',
            'project_type',
            'investment_amount',
            'expected_savings_m3',
            'expected_efficiency_gain',
            'status',
            'start_date',
            'end_date',
        )
        self.projects_tree = ttk.Treeview(list_frame, columns=cols, show='headings')
        for c in cols:
            self.projects_tree.heading(c, text=c)
            self.projects_tree.column(c, width=100, anchor='center')
        self.projects_tree.pack(fill='both', expand=True)

        # Liste işlemleri
        ttk.Button(list_frame, text=self.lm.tr('edit_selected_project', 'Seçili Projeyi Düzenle'), style='Primary.TButton', command=self._edit_project).pack(side='right', padx=5, pady=5)
        if self.is_admin:
            ttk.Button(list_frame, text=self.lm.tr('delete_selected_project', 'Seçili Projeyi Sil'), style='Primary.TButton', command=self._delete_project).pack(side='right', padx=5, pady=5)

        self._refresh_projects_list()

    def _clear_project_form(self) -> None:
        self.p_name_ent.delete(0, 'end')
        self.p_investment_ent.delete(0, 'end')
        self.p_savings_ent.delete(0, 'end')
        self.p_efficiency_ent.delete(0, 'end')
        self.p_start_ent.delete(0, 'end')
        self.p_end_ent.delete(0, 'end')
        self.p_responsible_ent.delete(0, 'end')
        self.p_desc_txt.delete('1.0', 'end')
        self.current_project_id = None

    def _save_project(self) -> None:
        try:
            project_name = self.p_name_ent.get().strip()
            if not project_name:
                messagebox.showwarning(self.lm.tr('msg_missing_info', 'Eksik Bilgi'), self.lm.tr('msg_project_name_required', 'Proje adı zorunludur.'))
                return

            from datetime import datetime
            impl_date = None
            comp_date = None
            if self.p_start_ent.get().strip():
                impl_date = datetime.strptime(self.p_start_ent.get().strip(), "%Y-%m-%d").date()
            if self.p_end_ent.get().strip():
                comp_date = datetime.strptime(self.p_end_ent.get().strip(), "%Y-%m-%d").date()

            project_id = self.manager.add_efficiency_project(
                company_id=self.company_id,
                project_name=project_name,
                project_type=self.p_type_cmb.get(),
                project_description=self.p_desc_txt.get('1.0', 'end').strip() or "",
                implementation_date=impl_date,
                completion_date=comp_date,
                investment_amount=float(self.p_investment_ent.get() or 0),
                expected_savings_m3=float(self.p_savings_ent.get() or 0),
                expected_efficiency_gain=float(self.p_efficiency_ent.get() or 0) / 100.0,
                responsible_person=self.p_responsible_ent.get().strip() or ""
            )

            if project_id:
                messagebox.showinfo(self.lm.tr('msg_success', 'Başarılı'), f'Proje eklendi (ID: {project_id}).')
                self._refresh_projects_list()
                self._clear_project_form()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('msg_project_add_error', 'Proje eklenemedi.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Proje eklenirken sorun: {e}')

    def _edit_project(self) -> None:
        try:
            sel = self.projects_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('msg_info', 'Bilgi'), self.lm.tr('msg_select_project_edit', 'Lütfen düzenlemek için bir proje seçin.'))
                return
            item = self.projects_tree.item(sel[0])
            p_id = item['values'][0]
            projects = self.manager.get_efficiency_projects(self.company_id)
            p = next((x for x in projects if x['id'] == p_id), None)
            if not p:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('msg_project_details_error', 'Proje detayları getirilemedi.'))
                return
            self.current_project_id = int(p_id)
            self.p_name_ent.delete(0, 'end')
            self.p_name_ent.insert(0, p.get('project_name') or '')
            self.p_type_cmb.set(p.get('project_type') or 'recycling')
            self.p_status_cmb.set(p.get('status') or 'planned')
            self.p_investment_ent.delete(0, 'end')
            self.p_investment_ent.insert(0, str(p.get('investment_amount') or ''))
            self.p_savings_ent.delete(0, 'end')
            self.p_savings_ent.insert(0, str(p.get('expected_savings_m3') or ''))
            self.p_efficiency_ent.delete(0, 'end')
            self.p_efficiency_ent.insert(0, str(((p.get('expected_efficiency_gain') or 0) * 100)))
            self.p_start_ent.delete(0, 'end')
            self.p_start_ent.insert(0, p.get('implementation_date') or '')
            self.p_end_ent.delete(0, 'end')
            self.p_end_ent.insert(0, p.get('completion_date') or '')
            self.p_responsible_ent.delete(0, 'end')
            self.p_responsible_ent.insert(0, p.get('responsible_person') or '')
            self.p_desc_txt.delete('1.0', 'end')
            self.p_desc_txt.insert('1.0', p.get('project_description') or '')
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('water_msg_project_edit_mode', f'Proje #{p_id} düzenleme modunda.').format(p_id=p_id))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('water_msg_edit_error', f'Düzenleme sırasında sorun: {e}').format(e=e))

    def _update_project(self) -> None:
        try:
            if not self.current_project_id:
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('water_msg_select_project_update', 'Güncellemek için önce bir proje seçip düzenleyin.'))
                return
            from datetime import datetime
            impl_date = None
            comp_date = None
            if self.p_start_ent.get().strip():
                impl_date = datetime.strptime(self.p_start_ent.get().strip(), "%Y-%m-%d").date()
            if self.p_end_ent.get().strip():
                comp_date = datetime.strptime(self.p_end_ent.get().strip(), "%Y-%m-%d").date()

            updates = {
                'project_name': self.p_name_ent.get().strip() or None,
                'project_type': self.p_type_cmb.get() or None,
                'status': self.p_status_cmb.get() or None,
                'investment_amount': self._to_float(self.p_investment_ent.get()),
                'expected_savings_m3': self._to_float(self.p_savings_ent.get()),
                'expected_efficiency_gain': (self._to_float(self.p_efficiency_ent.get()) or 0)/100.0,
                'implementation_date': impl_date,
                'completion_date': comp_date,
                'responsible_person': self.p_responsible_ent.get().strip() or None,
                'project_description': self.p_desc_txt.get('1.0', 'end').strip() or None,
            }
            ok = self.manager.update_efficiency_project(
                self.current_project_id,
                **{k: v for k, v in updates.items() if v is not None}
            )
            if ok:
                messagebox.showinfo(self.lm.tr('success', 'Başarılı'), self.lm.tr('water_msg_project_updated', 'Proje güncellendi.'))
                self._refresh_projects_list()
                self._clear_project_form()
            else:
                messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('water_msg_project_update_error', 'Proje güncellenemedi.'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('water_msg_update_error', f'Güncelleme sırasında sorun: {e}').format(e=e))

    def _refresh_projects_list(self) -> None:
        try:
            for i in self.projects_tree.get_children():
                self.projects_tree.delete(i)
            projects = self.manager.get_efficiency_projects(self.company_id)
            for p in projects:
                self.projects_tree.insert('', 'end', values=(
                    p['id'], p['project_name'], p['project_type'], p['investment_amount'],
                    p['expected_savings_m3'], f"{(p['expected_efficiency_gain'] or 0) * 100:.1f}%",
                    p['status'], p['implementation_date'], p['completion_date']
                ))
        except Exception as e:
            logging.error(f"Proje listesi hatası: {e}")

    def _delete_project(self) -> None:
        try:
            # Admin kontrolü
            if not self.is_admin:
                messagebox.showwarning(self.lm.tr('msg_permission_error', 'Yetki Hatası'), self.lm.tr('msg_admin_required', 'Bu işlem için admin veya super_admin yetkisi gereklidir.'))
                return

            sel = self.projects_tree.selection()
            if not sel:
                messagebox.showinfo(self.lm.tr('msg_info', 'Bilgi'), self.lm.tr('msg_select_project_delete', 'Lütfen silmek için bir proje seçin.'))
                return
            item = self.projects_tree.item(sel[0])
            project_id = item['values'][0]
            if messagebox.askyesno(self.lm.tr('confirm', 'Onay'), f'Proje #{project_id} silinsin mi?'):
                try:
                    self.manager.delete_efficiency_project(int(project_id))
                    messagebox.showinfo(self.lm.tr('msg_success', 'Başarılı'), f'Proje #{project_id} silindi.')
                except Exception as e:
                    messagebox.showerror(self.lm.tr('error', 'Hata'), f'Proje silinemedi: {e}')
                self._refresh_projects_list()
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Silme sırasında sorun: {e}')

    # ==================== SDG 6 İLERLEME ====================
    def build_sdg6_view(self) -> None:
        self.current_view = 'sdg6'
        self.content_title['text'] = self.lm.tr('sdg6_tracking', 'SDG 6 İlerleme Takibi')
        self._clear_content()

        # Dönem seçimi
        selector = tk.Frame(self.content_frame, bg='white')
        selector.pack(fill='x', padx=15, pady=10)
        tk.Label(selector, text=self.lm.tr('select_period', 'Dönem Seç'), bg='white').pack(side='left')
        self._refresh_periods()
        self.sdg6_period_cmb = ttk.Combobox(selector, values=self.periods, width=20)
        self.sdg6_period_cmb.pack(side='left', padx=8)
        if self.periods:
            self.sdg6_period_cmb.set(self.periods[0])
        ttk.Button(selector, text=self.lm.tr('calculate_progress', 'İlerleme Hesapla'), style='Primary.TButton', command=self._calculate_sdg6).pack(side='left', padx=8)

        # SDG 6 alt hedefleri kartları
        sdg6_frame = tk.Frame(self.content_frame, bg='white')
        sdg6_frame.pack(fill='both', expand=True, padx=15, pady=10)

        sdg6_targets = [
            ('SDG 6.1', self.lm.tr('sdg6_1_desc', 'İçme Suyu Erişimi'), '#3498db'),
            ('SDG 6.2', self.lm.tr('sdg6_2_desc', 'Sanitasyon ve Hijyen'), '#27ae60'),
            ('SDG 6.3', self.lm.tr('sdg6_3_desc', 'Su Kalitesi'), '#f39c12'),
            ('SDG 6.4', self.lm.tr('sdg6_4_desc', 'Su Verimliliği'), '#9b59b6'),
            ('SDG 6.5', self.lm.tr('sdg6_5_desc', 'Su Yönetişimi'), '#e74c3c'),
            ('SDG 6.6', self.lm.tr('sdg6_6_desc', 'Ekosistem Koruması'), '#16a085'),
        ]

        self.sdg6_labels = {}
        for i, (target, desc, color) in enumerate(sdg6_targets):
            row = i // 3
            col = i % 3

            card = tk.Frame(sdg6_frame, bg=color, relief='raised', bd=2)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='ew')
            sdg6_frame.grid_columnconfigure(col, weight=1)

            tk.Label(card, text=target, font=('Segoe UI', 12, 'bold'), fg='white', bg=color).pack(pady=(15, 5))
            tk.Label(card, text=desc, font=('Segoe UI', 9), fg='white', bg=color).pack(pady=(0, 5))

            progress_lbl = tk.Label(card, text=self.lm.tr('lbl_percentage_placeholder', '—%'), font=('Segoe UI', 20, 'bold'), fg='white', bg=color)
            progress_lbl.pack(pady=(10, 15))
            self.sdg6_labels[target] = progress_lbl

        # Detaylı bilgi alanı
        info_frame = tk.LabelFrame(self.content_frame, text=self.lm.tr('sdg6_detailed_info', 'SDG 6 Detaylı Bilgi'), bg='white')
        info_frame.pack(fill='both', expand=True, padx=15, pady=10)

        self.sdg6_info_text = tk.Text(info_frame, height=10, width=80, bg='#f8f9fa', relief='flat')
        self.sdg6_info_text.pack(fill='both', expand=True, padx=10, pady=10)

    def _calculate_sdg6(self) -> None:
        try:
            period = self.sdg6_period_cmb.get().strip()
            if not period:
                messagebox.showwarning(self.lm.tr('period_selection', 'Dönem Seçimi'), self.lm.tr('select_period_warning', 'Lütfen dönem seçin.'))
                return

            # Gerçek verilerden SDG 6 ilerleme hesaplama
            try:
                # Su tüketim verileri
                consumption_records = self.manager.get_water_consumption(self.company_id, period=period)

                # Kalite ölçümleri
                quality_records = self.manager.get_quality_measurements(self.company_id)

                # Hedefler
                targets = self.manager.get_water_targets(self.company_id)

                # Projeler
                projects = self.manager.get_efficiency_projects(self.company_id)

                # SDG 6 alt hedeflerini hesapla
                sdg6_progress: dict[str, float] = {}

                # SDG 6.1 - İçme Suyu Erişimi (Municipal water kullanımına göre)
                municipal_usage = [r for r in consumption_records if r.get('water_source') == 'municipal']
                sdg6_progress['SDG 6.1'] = 90 if municipal_usage else 0

                # SDG 6.2 - Sanitasyon (Sanitation için proxy olarak recycled water kullanımı)
                recycled_usage = [r for r in consumption_records if r.get('water_source') == 'recycled']
                sdg6_progress['SDG 6.2'] = min(100, len(recycled_usage) * 20) if consumption_records else 0

                # SDG 6.3 - Su Kalitesi (Kalite ölçümlerinin uyumluluğuna göre)
                if quality_records:
                    compliant = [q for q in quality_records if q.get('compliance_status') == 'compliant']
                    compliant_count = len(compliant)
                    sdg6_progress['SDG 6.3'] = round((compliant_count / len(quality_records)) * 100, 1)
                else:
                    sdg6_progress['SDG 6.3'] = 0

                # SDG 6.4 - Su Verimliliği (Ortalama verimlilik oranı ve geri dönüşüm)
                if consumption_records:
                    avg_efficiency = (
                        sum(
                            r.get('efficiency_ratio', 0) or 0
                            for r in consumption_records
                        ) / len(consumption_records)
                    )
                    avg_recycling = (
                        sum(
                            r.get('recycling_rate', 0) or 0
                            for r in consumption_records
                        ) / len(consumption_records)
                    )
                    sdg6_progress['SDG 6.4'] = round(((avg_efficiency + avg_recycling) / 2) * 100, 1)
                else:
                    sdg6_progress['SDG 6.4'] = 0

                # SDG 6.5 - Su Yönetişimi (Hedef ve proje sayısına göre)
                active_targets = [t for t in targets if t.get('status') == 'active']
                active_projects = [p for p in projects if p.get('status') in ('ongoing', 'planned')]
                management_score = min(100, (len(active_targets) + len(active_projects)) * 15)
                sdg6_progress['SDG 6.5'] = management_score

                # SDG 6.6 - Ekosistem Koruması (Toplam tüketim azalma hedefi ve projelere göre)
                eco_projects = [p for p in projects if p.get('project_type') in ('reduction', 'treatment')]
                sdg6_progress['SDG 6.6'] = min(100, len(eco_projects) * 25)

                # Kartları güncelle
                for target, progress in sdg6_progress.items():
                    if target in self.sdg6_labels:
                        if progress > 0:
                            self.sdg6_labels[target]['text'] = f'{progress:.0f}%'
                        else:
                            self.sdg6_labels[target]['text'] = '—'

                # Genel ortalama
                valid_scores = [v for v in sdg6_progress.values() if v > 0]
                avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

                # Detaylı bilgi
                if not consumption_records and not quality_records and not targets and not projects:
                    info_text = f"""{self.lm.tr('sdg6_report_title', 'SDG 6 İlerleme Raporu')} - {period}

️ {self.lm.tr('no_data_found', 'VERİ BULUNAMADI')}

{self.lm.tr('no_data_sdg6_desc', 'Henüz bu dönem için veri girilmemiş. SDG 6 ilerleme hesaplaması yapabilmek için:')}

1.  {self.lm.tr('add_consumption_records', 'Su Tüketimi Kayıtları Ekleyin')}
   - {self.lm.tr('enter_consumption_data', 'Kayıtlar sekmesinden su tüketim verilerini girin')}
   - {self.lm.tr('record_efficiency_recycling', 'Verimlilik ve geri dönüşüm oranlarını kaydedin')}

2.  {self.lm.tr('make_quality_measurements', 'Kalite Ölçümleri Yapın')}
   - {self.lm.tr('enter_quality_params', 'Kalite İzleme sekmesinden su kalitesi parametrelerini girin')}
   - {self.lm.tr('measure_ph_bod_cod', 'pH, BOD, COD gibi parametreleri ölçün')}

3.  {self.lm.tr('set_targets', 'Hedefler Belirleyin')}
   - {self.lm.tr('define_water_targets', 'Hedefler sekmesinden su yönetimi hedeflerinizi tanımlayın')}
   - {self.lm.tr('create_sdg6_targets', 'SDG 6 uyumlu hedefler oluşturun')}

4. ️ {self.lm.tr('start_projects', 'Projeler Başlatın')}
   - {self.lm.tr('add_efficiency_projects', 'Verimlilik Projeleri sekmesinden su tasarrufu projelerinizi ekleyin')}
   - {self.lm.tr('record_recycling_treatment', 'Geri dönüşüm ve arıtma projelerini kaydedin')}

{self.lm.tr('sdg6_auto_calculation', 'Veri girildikçe gerçek SDG 6 ilerlemeniz otomatik olarak hesaplanacaktır.')}
"""
                else:
                    info_text = f"""{self.lm.tr('sdg6_report_title', 'SDG 6 İlerleme Raporu')} - {period}

{self.lm.tr('general_average', 'Genel Ortalama')}: {avg_score:.1f}%

{self.lm.tr('sdg6_1_title', 'SDG 6.1 - İçme Suyu Erişimi')} ({sdg6_progress['SDG 6.1']:.0f}%)
{'' if sdg6_progress['SDG 6.1'] > 0 else '️'} {self.lm.tr('municipal_water_records', 'Municipal su kaynaklarından {} kayıt mevcut').format(len(municipal_usage))}

{self.lm.tr('sdg6_2_title', 'SDG 6.2 - Sanitasyon ve Hijyen')} ({sdg6_progress['SDG 6.2']:.0f}%)
{'' if sdg6_progress['SDG 6.2'] > 0 else '️'} {self.lm.tr('recycled_water_usage', 'Geri dönüştürülmüş su kullanımı: {} kayıt').format(len(recycled_usage))}

{self.lm.tr('sdg6_3_title', 'SDG 6.3 - Su Kalitesi')} ({sdg6_progress['SDG 6.3']:.1f}%)
{'' if sdg6_progress['SDG 6.3'] > 70 else '️' if sdg6_progress['SDG 6.3'] > 0 else ''} {compliant_count} /
{len(quality_records)} {self.lm.tr('measurements_compliant', 'ölçüm standartlara uygun')}

{self.lm.tr('sdg6_4_title', 'SDG 6.4 - Su Verimliliği')} ({sdg6_progress['SDG 6.4']:.1f}%)
{'' if sdg6_progress['SDG 6.4'] > 50 else '️' if sdg6_progress['SDG 6.4'] > 0 else ''}
{self.lm.tr('avg_efficiency_recycling', 'Ortalama verimlilik ve geri dönüşüm oranları')}

{self.lm.tr('sdg6_5_title', 'SDG 6.5 - Su Yönetişimi')} ({sdg6_progress['SDG 6.5']:.0f}%)
{'' if sdg6_progress['SDG 6.5'] > 50 else '️' if sdg6_progress['SDG 6.5'] > 0 else ''}
{self.lm.tr('active_targets_projects', '{} aktif hedef, {} aktif proje').format(len(active_targets), len(active_projects))}

{self.lm.tr('sdg6_6_title', 'SDG 6.6 - Ekosistem Koruması')} ({sdg6_progress['SDG 6.6']:.0f}%)
{'' if sdg6_progress['SDG 6.6'] > 50 else '️' if sdg6_progress['SDG 6.6'] > 0 else ''}
{self.lm.tr('eco_protection_projects', '{} çevre koruma projesi').format(len(eco_projects))}

═══════════════════════════════════════════════════

 {self.lm.tr('data_summary', 'Veri Özeti')}:
• {self.lm.tr('total_consumption_records', 'Toplam Tüketim Kaydı')}: {len(consumption_records)}
• {self.lm.tr('total_quality_measurements', 'Toplam Kalite Ölçümü')}: {len(quality_records)}
• {self.lm.tr('total_targets', 'Toplam Hedef')}: {len(targets)}
• {self.lm.tr('total_projects', 'Toplam Proje')}: {len(projects)}

 {self.lm.tr('recommendations', 'Öneriler')}:
{self._generate_sdg6_recommendations(sdg6_progress, consumption_records, quality_records, targets, projects)}
"""

                self.sdg6_info_text.delete('1.0', 'end')
                self.sdg6_info_text.insert('1.0', info_text)

            except Exception as calc_error:
                messagebox.showerror(self.lm.tr('calculation_error', 'Hesaplama Hatası'), f"{self.lm.tr('sdg6_calculation_error', 'SDG 6 hesaplama hatası')}: {calc_error}")
                for target in self.sdg6_labels:
                    self.sdg6_labels[target]['text'] = '—'

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f"{self.lm.tr('sdg6_calculation_problem', 'SDG 6 hesaplama sırasında sorun')}: {e}")

    def _generate_sdg6_recommendations(self, progress, consumption, quality, targets, projects) -> str:
        """SDG 6 iyileştirme önerileri oluştur"""
        recommendations = []

        if progress.get('SDG 6.1', 0) < 50:
            recommendations.append(f"• {self.lm.tr('rec_sdg6_1', 'İçme suyu erişimini artırmak için municipal su kaynaklarını çeşitlendirin')}")

        if progress.get('SDG 6.2', 0) < 50:
            recommendations.append(f"• {self.lm.tr('rec_sdg6_2', 'Sanitasyon için geri dönüştürülmüş su kullanımını artırın')}")

        if progress.get('SDG 6.3', 0) < 70:
            recommendations.append(f"• {self.lm.tr('rec_sdg6_3', 'Su kalitesi ölçümlerini artırın ve standartlara uygunluğu sağlayın')}")

        if progress.get('SDG 6.4', 0) < 60:
            recommendations.append(f"• {self.lm.tr('rec_sdg6_4', 'Verimlilik ve geri dönüşüm oranlarını artırmak için projeler başlatın')}")

        if progress.get('SDG 6.5', 0) < 50:
            recommendations.append(f"• {self.lm.tr('rec_sdg6_5', 'Daha fazla hedef belirleyin ve su yönetim projelerini genişletin')}")

        if progress.get('SDG 6.6', 0) < 50:
            recommendations.append(f"• {self.lm.tr('rec_sdg6_6', 'Ekosistem koruması için arıtma ve azaltma projeleri ekleyin')}")

        if not consumption:
            recommendations.append(f"• {self.lm.tr('rec_add_consumption', 'Su tüketim kayıtları eklemeye başlayın')}")

        if not quality:
            recommendations.append(f"• {self.lm.tr('rec_start_quality', 'Su kalitesi izleme programı başlatın')}")

        if not targets:
            recommendations.append(f"• {self.lm.tr('rec_set_targets', 'SDG 6 uyumlu hedefler belirleyin')}")

        if not projects:
            recommendations.append(f"• {self.lm.tr('rec_create_projects', 'Su verimliliği projeleri oluşturun')}")

        return '\n'.join(recommendations) if recommendations else f"• {self.lm.tr('rec_all_good', 'Tüm alanlar iyi durumda, bu performansı sürdürün!')}"
