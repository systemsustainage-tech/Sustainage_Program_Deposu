#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Widget Sistemi
Özelleştirilebilir, sürüklenebilir widget kütüphanesi
"""

import logging
import json
import sqlite3
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional

from utils.language_manager import LanguageManager


class DashboardWidget:
    """Temel widget sınıfı"""

    def __init__(self, parent, widget_config: Dict) -> None:
        """
        Args:
            parent: Ana frame
            widget_config: Widget yapılandırması
        """
        self.lm = LanguageManager()
        self.parent = parent
        self.config = widget_config
        self.widget_frame = None
        self.create_widget()

    def create_widget(self) -> None:
        """Widget'ı oluştur"""
        self.widget_frame = tk.Frame(self.parent, bg='white', relief='raised', bd=2)

        # Başlık
        header = tk.Frame(self.widget_frame, bg=self.config.get('color', '#3498db'), height=40)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text=self.config.get('title', 'Widget'),
                font=('Segoe UI', 11, 'bold'), fg='white',
                bg=self.config.get('color', '#3498db')).pack(side='left', padx=15, pady=10)

        # İçerik alanı
        self.content_frame = tk.Frame(self.widget_frame, bg='white')
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def update_content(self, data: any) -> None:
        """İçeriği güncelle (override edilmeli)"""
        pass


class MetricCardWidget(DashboardWidget):
    """Metrik kartı widget"""

    def __init__(self, parent, widget_config: Dict) -> None:
        super().__init__(parent, widget_config)

    def create_widget(self) -> None:
        """Metrik kartı oluştur"""
        super().create_widget()

        # Değer
        self.value_label = tk.Label(self.content_frame, text="0",
                                    font=('Segoe UI', 32, 'bold'), bg='white',
                                    fg=self.config.get('color', '#3498db'))
        self.value_label.pack(pady=(20, 5))

        # Alt metin
        self.subtitle_label = tk.Label(self.content_frame,
                                       text=self.config.get('subtitle', ''),
                                       font=('Segoe UI', 9), bg='white', fg='#666')
        self.subtitle_label.pack(pady=(0, 20))

    def update_content(self, value: any) -> None:
        """Değeri güncelle"""
        self.value_label.config(text=str(value))


class ChartWidget(DashboardWidget):
    """Grafik widget"""

    def __init__(self, parent, widget_config: Dict) -> None:
        super().__init__(parent, widget_config)

    def create_widget(self) -> None:
        """Grafik widget oluştur"""
        super().create_widget()

        # Matplotlib için yer tutucu
        self.chart_frame = tk.Frame(self.content_frame, bg='white')
        self.chart_frame.pack(fill='both', expand=True)

        tk.Label(self.chart_frame, text=self.lm.tr("widget_chart_placeholder", " Grafik Alanı"),
                font=('Segoe UI', 12), bg='white', fg='#999').pack(expand=True)

    def update_content(self, chart_data: Dict) -> None:
        """Grafiği güncelle"""
        # Matplotlib chart oluşturma
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
            import matplotlib.pyplot as plt
        except ImportError:
            logging.warning("Matplotlib bulunamadı, grafik çizilemiyor.")
            return

        # Mevcut içeriği temizle
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if not chart_data:
             tk.Label(self.chart_frame, text=self.lm.tr("no_data", "Veri Yok"),
                     font=('Segoe UI', 12), bg='white', fg='#999').pack(expand=True)
             return

        try:
            # Basit bir bar chart örneği
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)

            labels = list(chart_data.keys())
            values = list(chart_data.values())

            ax.bar(labels, values, color=self.config.get('color', '#3498db'))
            ax.set_title(self.config.get('title', ''))
            
            # X ekseni etiketlerini döndür
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        except Exception as e:
            logging.error(f"Grafik oluşturma hatası: {e}")
            tk.Label(self.chart_frame, text=f"Grafik Hatası: {str(e)}",
                    font=('Segoe UI', 10), bg='white', fg='red').pack(expand=True)


class TableWidget(DashboardWidget):
    """Tablo widget"""

    def __init__(self, parent, widget_config: Dict) -> None:
        super().__init__(parent, widget_config)

    def create_widget(self) -> None:
        """Tablo widget oluştur"""
        super().create_widget()

        # Treeview
        self.tree = ttk.Treeview(self.content_frame, height=5)
        scrollbar = ttk.Scrollbar(self.content_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def update_content(self, table_data: Dict) -> None:
        """Tabloyu güncelle"""
        # Sütunları ayarla
        columns = table_data.get('columns', [])
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'

        for col in columns:
            self.tree.heading(col, text=col)

        # Verileri ekle
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in table_data.get('data', []):
            self.tree.insert('', 'end', values=row)


class ProgressWidget(DashboardWidget):
    """İlerleme widget"""

    def __init__(self, parent, widget_config: Dict) -> None:
        super().__init__(parent, widget_config)

    def create_widget(self) -> None:
        """İlerleme widget oluştur"""
        super().create_widget()

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(self.content_frame, variable=self.progress_var,
                                       maximum=100, length=200, mode='determinate')
        self.progress.pack(pady=20)

        # Yüzde metni
        self.percent_label = tk.Label(self.content_frame, text="0%",
                                      font=('Segoe UI', 16, 'bold'), bg='white',
                                      fg=self.config.get('color', '#27ae60'))
        self.percent_label.pack()

    def update_content(self, value: float) -> None:
        """İlerlemeyi güncelle"""
        self.progress_var.set(value)
        self.percent_label.config(text=f"{value:.1f}%")


class DashboardWidgetManager:
    """Dashboard widget yöneticisi"""

    # Widget tipleri
    WIDGET_TYPES = {
        'metric_card': MetricCardWidget,
        'chart': ChartWidget,
        'table': TableWidget,
        'progress': ProgressWidget
    }

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self) -> None:
        """Widget yapılandırma tablosu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_layouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    layout_name TEXT NOT NULL,
                    is_default INTEGER DEFAULT 0,
                    layout_config TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_widgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    layout_id INTEGER NOT NULL,
                    widget_type TEXT NOT NULL,
                    widget_title TEXT NOT NULL,
                    widget_config TEXT,
                    position_row INTEGER DEFAULT 0,
                    position_col INTEGER DEFAULT 0,
                    width INTEGER DEFAULT 1,
                    height INTEGER DEFAULT 1,
                    is_visible INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (layout_id) REFERENCES dashboard_layouts(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Dashboard widget tabloları hazır")

        except Exception as e:
            logging.error(f"[HATA] Widget tablo: {e}")
            conn.rollback()
        finally:
            conn.close()

    def save_layout(self, user_id: int, layout_name: str,
                   widgets: List[Dict], is_default: bool = False) -> int:
        """
        Dashboard layout'u kaydet
        
        Args:
            user_id: Kullanıcı ID
            layout_name: Layout adı
            widgets: Widget listesi
            is_default: Varsayılan layout mu
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            layout_config = json.dumps(widgets, ensure_ascii=False)

            cursor.execute("""
                INSERT INTO dashboard_layouts (user_id, layout_name, is_default, layout_config)
                VALUES (?, ?, ?, ?)
            """, (user_id, layout_name, 1 if is_default else 0, layout_config))

            layout_id = cursor.lastrowid

            # Eğer varsayılan ise diğerlerini güncelle
            if is_default:
                cursor.execute("""
                    UPDATE dashboard_layouts SET is_default = 0 
                    WHERE user_id = ? AND id != ?
                """, (user_id, layout_id))

            conn.commit()
            return layout_id

        except Exception as e:
            logging.error(f"Layout kaydetme hatası: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def get_user_layout(self, user_id: int, layout_id: int = None) -> Optional[Dict]:
        """Kullanıcının layout'unu getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if layout_id:
                cursor.execute("""
                    SELECT id, layout_name, layout_config FROM dashboard_layouts
                    WHERE id = ? AND user_id = ?
                """, (layout_id, user_id))
            else:
                # Varsayılan layout'u getir
                cursor.execute("""
                    SELECT id, layout_name, layout_config FROM dashboard_layouts
                    WHERE user_id = ? AND is_default = 1
                    LIMIT 1
                """, (user_id,))

            row = cursor.fetchone()

            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'widgets': json.loads(row[2])
                }

            return None

        finally:
            conn.close()

    def create_default_layout(self, user_id: int) -> int:
        """Varsayılan layout oluştur"""
        default_widgets = [
            {
                'type': 'metric_card',
                'title': self.lm.tr("widget_total_tasks", 'Toplam Görev'),
                'color': '#3498db',
                'subtitle': self.lm.tr("widget_active_tasks", 'Aktif görevler'),
                'position': {'row': 0, 'col': 0},
                'size': {'width': 1, 'height': 1}
            },
            {
                'type': 'metric_card',
                'title': self.lm.tr("widget_completed", 'Tamamlanan'),
                'color': '#27ae60',
                'subtitle': self.lm.tr("widget_this_month", 'Bu ay'),
                'position': {'row': 0, 'col': 1},
                'size': {'width': 1, 'height': 1}
            },
            {
                'type': 'progress',
                'title': self.lm.tr("widget_sdg_progress", 'SDG İlerleme'),
                'color': '#e67e22',
                'position': {'row': 0, 'col': 2},
                'size': {'width': 1, 'height': 1}
            },
            {
                'type': 'chart',
                'title': self.lm.tr("widget_monthly_trend", 'Aylık Trend'),
                'color': '#9b59b6',
                'position': {'row': 1, 'col': 0},
                'size': {'width': 3, 'height': 2}
            }
        ]

        return self.save_layout(user_id, self.lm.tr("default_dashboard_title", 'Varsayılan Dashboard'),
                               default_widgets, is_default=True)

