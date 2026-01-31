#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grafik Performans Optimizasyon Utilities
Matplotlib performans iyileştirmeleri
"""

import logging
import matplotlib

# Performans için Agg backend kullan (GUI olmayan)
matplotlib.use('Agg')

import io
import threading
from typing import Callable, Optional

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk


class ChartOptimizer:
    """Matplotlib grafik optimizasyonu"""

    def __init__(self) -> None:
        self.figure_cache = {}
        self.canvas_cache = {}

        # Performans ayarları
        plt.style.use('fast')  # Hızlı render modu
        matplotlib.rcParams['path.simplify'] = True
        matplotlib.rcParams['path.simplify_threshold'] = 1.0
        matplotlib.rcParams['agg.path.chunksize'] = 10000

    def create_optimized_figure(self, figsize=(8, 6), dpi=100, cache_key=None) -> None:
        """Optimize edilmiş figure oluştur"""
        # Cache varsa kullan
        if cache_key and cache_key in self.figure_cache:
            fig = self.figure_cache[cache_key]
            fig.clear()  # Clear previous content
            return fig

        # Yeni figure oluştur
        fig = plt.figure(figsize=figsize, dpi=dpi)

        # Cache'le
        if cache_key:
            self.figure_cache[cache_key] = fig

        return fig

    def create_tkinter_canvas(self, parent, fig, cache_key=None) -> None:
        """Tkinter canvas oluştur (optimize edilmiş)"""
        # Cache varsa güncelle
        if cache_key and cache_key in self.canvas_cache:
            canvas = self.canvas_cache[cache_key]
            canvas.draw()
            return canvas

        # Yeni canvas oluştur
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()

        # Cache'le
        if cache_key:
            self.canvas_cache[cache_key] = canvas

        return canvas

    def create_static_image(self, fig, width=800, height=600) -> None:
        """Figure'ı statik resme dönüştür (daha hızlı)"""
        # Memory buffer'a kaydet
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)

        # PIL Image'e dönüştür
        img = Image.open(buf)
        img = img.resize((width, height), Image.Resampling.LANCZOS)

        buf.close()

        return img

    def create_photoimage(self, fig, width=800, height=600) -> None:
        """Figure'ı PhotoImage'e dönüştür (Tkinter için)"""
        img = self.create_static_image(fig, width, height)
        return ImageTk.PhotoImage(img)

    def async_render_chart(self, render_func: Callable, callback: Callable) -> None:
        """Asenkron grafik render (UI donmasını önler)"""
        def worker() -> None:
            try:
                result = render_func()
                callback(result)
            except Exception as e:
                logging.error(f"Async chart render hatası: {e}")

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def clear_cache(self, cache_key: Optional[str] = None) -> None:
        """Cache'i temizle"""
        if cache_key:
            if cache_key in self.figure_cache:
                plt.close(self.figure_cache[cache_key])
                del self.figure_cache[cache_key]
            if cache_key in self.canvas_cache:
                del self.canvas_cache[cache_key]
        else:
            # Tüm cache'i temizle
            for fig in self.figure_cache.values():
                plt.close(fig)
            self.figure_cache.clear()
            self.canvas_cache.clear()

            # Matplotlib memory cleanup
            plt.close('all')

    def optimize_pie_chart(self, ax, labels, sizes, colors=None, explode=None) -> None:
        """Optimize edilmiş pasta grafik"""
        ax.pie(sizes, labels=labels, colors=colors, explode=explode,
               autopct='%1.1f%%', startangle=90,
               pctdistance=0.85,  # Metin konumu
               textprops={'size': 9})  # Küçük font
        ax.axis('equal')

    def optimize_bar_chart(self, ax, x_data, y_data, color='skyblue') -> None:
        """Optimize edilmiş bar grafik"""
        ax.bar(x_data, y_data, color=color, edgecolor='none')  # Edge yok = hızlı
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)

    def optimize_line_chart(self, ax, x_data, y_data, color='blue', linewidth=2) -> None:
        """Optimize edilmiş çizgi grafik"""
        ax.plot(x_data, y_data, color=color, linewidth=linewidth,
               marker='o', markersize=4, markerfacecolor='white',
               markeredgewidth=1.5)
        ax.grid(alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)


# Global optimizer instance
chart_optimizer = ChartOptimizer()


def create_fast_chart(chart_type: str, data: dict, parent=None, cache_key=None) -> None:
    """
    Hızlı grafik oluştur
    
    Args:
        chart_type: 'pie', 'bar', 'line'
        data: Grafik verisi
        parent: Tkinter parent (None = sadece figure döndür)
        cache_key: Cache anahtarı
    
    Returns:
        Figure veya Canvas
    """
    # Figure oluştur
    fig = chart_optimizer.create_optimized_figure(
        figsize=data.get('figsize', (8, 6)),
        dpi=data.get('dpi', 100),
        cache_key=cache_key
    )

    ax = fig.add_subplot(111)

    # Grafik tipine göre çiz
    if chart_type == 'pie':
        chart_optimizer.optimize_pie_chart(
            ax,
            labels=data['labels'],
            sizes=data['sizes'],
            colors=data.get('colors'),
            explode=data.get('explode')
        )
    elif chart_type == 'bar':
        chart_optimizer.optimize_bar_chart(
            ax,
            x_data=data['x'],
            y_data=data['y'],
            color=data.get('color', 'skyblue')
        )
    elif chart_type == 'line':
        chart_optimizer.optimize_line_chart(
            ax,
            x_data=data['x'],
            y_data=data['y'],
            color=data.get('color', 'blue'),
            linewidth=data.get('linewidth', 2)
        )

    # Başlık ve label'lar
    if 'title' in data:
        ax.set_title(data['title'], fontsize=12, fontweight='bold')
    if 'xlabel' in data:
        ax.set_xlabel(data['xlabel'], fontsize=10)
    if 'ylabel' in data:
        ax.set_ylabel(data['ylabel'], fontsize=10)

    fig.tight_layout()

    # Parent varsa canvas döndür
    if parent:
        return chart_optimizer.create_tkinter_canvas(parent, fig, cache_key)
    else:
        return fig


def create_progress_gauge(parent, value: float, max_value: float = 100,
                         title: str = "İlerleme", cache_key=None):
    """
    İlerleme göstergesi oluştur (optimize)
    
    Args:
        parent: Tkinter parent
        value: Mevcut değer
        max_value: Maksimum değer
        title: Başlık
        cache_key: Cache anahtarı
    """
    # Normalize et
    percentage = (value / max_value) * 100 if max_value > 0 else 0

    # Figure oluştur
    fig = chart_optimizer.create_optimized_figure(
        figsize=(6, 4),
        dpi=80,
        cache_key=cache_key
    )

    ax = fig.add_subplot(111, projection='polar')

    # Gauge çiz (yarım daire)
    theta = np.linspace(0, np.pi, 100)
    radii = np.ones_like(theta)

    # Arka plan (gri)
    ax.plot(theta, radii, color='lightgray', linewidth=10)

    # İlerleme (renkli)
    progress_theta = np.linspace(0, np.pi * (percentage / 100), 100)
    progress_radii = np.ones_like(progress_theta)

    # Renk seçimi
    if percentage >= 80:
        color = 'green'
    elif percentage >= 50:
        color = 'orange'
    else:
        color = 'red'

    ax.plot(progress_theta, progress_radii, color=color, linewidth=10)

    # Ayarlar
    ax.set_ylim(0, 1.5)
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines['polar'].set_visible(False)

    # Metin
    ax.text(0, -0.3, f"{percentage:.1f}%",
           ha='center', va='center', fontsize=24, fontweight='bold')
    ax.text(0, -0.5, title,
           ha='center', va='center', fontsize=12)

    fig.tight_layout()

    return chart_optimizer.create_tkinter_canvas(parent, fig, cache_key)


# Numpy import (gauge için)
try:
    import numpy as np
except ImportError:
    np = None
    logging.info("️ NumPy yüklü değil. Gauge grafikleri kullanılamaz.")

