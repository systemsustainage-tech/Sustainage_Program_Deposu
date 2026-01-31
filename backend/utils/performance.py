#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performans Optimizasyon Utilities
Tkinter uygulaması için performans iyileştirmeleri
"""

import logging
import threading
import time
import tkinter as tk
from functools import wraps
from tkinter import ttk
from typing import Callable


class PerformanceOptimizer:
    """Performans optimizasyonu yöneticisi"""

    def __init__(self) -> None:
        self.cache = {}
        self.debounce_timers = {}

    def debounce(self, delay: int = 300) -> None:
        """
        Debounce decorator - Hızlı tekrarlanan çağrıları geciktirir
        
        Args:
            delay: Gecikme süresi (ms)
        
        Kullanım:
            @optimizer.debounce(500)
            def on_search_change(self, text) -> None:
                # Kullanıcı yazmayı bitirdikten 500ms sonra çalışır
                self.perform_search(text)
        """
        def decorator(func) -> None:
            @wraps(func)
            def wrapper(*args, **kwargs) -> None:
                # Önceki timer'ı iptal et
                func_id = id(func)
                if func_id in self.debounce_timers:
                    args[0].parent.after_cancel(self.debounce_timers[func_id])

                # Yeni timer ayarla
                self.debounce_timers[func_id] = args[0].parent.after(
                    delay,
                    lambda: func(*args, **kwargs)
                )

            return wrapper
        return decorator

    def throttle(self, delay: int = 100) -> None:
        """
        Throttle decorator - Fonksiyonu belirli aralıklarla çağırır
        
        Args:
            delay: Minimum çağrı aralığı (ms)
        
        Kullanım:
            @optimizer.throttle(200)
            def on_scroll(self, event) -> None:
                # 200ms'de bir çalışır
                self.update_visible_items()
        """
        def decorator(func) -> None:
            last_call = [0]  # Mutable list to store last call time

            @wraps(func)
            def wrapper(*args, **kwargs) -> None:
                now = time.time() * 1000  # ms
                if now - last_call[0] >= delay:
                    last_call[0] = now
                    return func(*args, **kwargs)

            return wrapper
        return decorator

    def memoize(self, func: Callable) -> Callable:
        """
        Memoization decorator - Fonksiyon sonuçlarını önbelleğe alır
        
        Kullanım:
            @optimizer.memoize
            def expensive_calculation(self, value) -> None:
                # Ağır hesaplama
                return result
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            # Cache key oluştur
            cache_key = str(args) + str(kwargs)

            if cache_key in self.cache:
                return self.cache[cache_key]

            result = func(*args, **kwargs)
            self.cache[cache_key] = result
            return result

        return wrapper

    def clear_cache(self) -> None:
        """Önbelleği temizle"""
        self.cache.clear()


class VirtualScrollbar:
    """
    Sanal kaydırma çubuğu - Büyük listeler için
    Sadece görünür öğeleri render eder
    """

    def __init__(self, parent: tk.Frame, items: list, item_height: int = 30) -> None:
        self.parent = parent
        self.items = items
        self.item_height = item_height
        self.visible_items = []
        self.canvas = None
        self.scrollbar = None
        self.container = None

    def setup(self) -> None:
        """Sanal scrollbar'ı kur"""
        # Canvas ve scrollbar
        self.canvas = tk.Canvas(self.parent, bg='white', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.parent, orient='vertical',
                                       command=self._on_scroll)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Layout
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

        # Container frame
        self.container = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0, 0), window=self.container, anchor='nw')

        # Scroll event
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)

        # İlk render
        self._render_visible_items()

    def _on_scroll(self, *args) -> None:
        """Scroll eventi"""
        self.canvas.yview(*args)
        self._render_visible_items()

    def _on_canvas_configure(self, event) -> None:
        """Canvas boyut değişimi"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self._render_visible_items()

    def _on_mousewheel(self, event) -> None:
        """Fare tekerleği"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._render_visible_items()

    def _render_visible_items(self) -> None:
        """Sadece görünür öğeleri render et"""
        # Görünür alan hesapla
        canvas_top = self.canvas.canvasy(0)
        canvas_bottom = self.canvas.canvasy(self.canvas.winfo_height())

        # Mevcut widget'ları temizle
        for widget in self.container.winfo_children():
            widget.destroy()

        # Görünür öğeleri render et
        for i, item in enumerate(self.items):
            item_top = i * self.item_height
            item_bottom = item_top + self.item_height

            # Görünür alanda mı?
            if item_bottom >= canvas_top and item_top <= canvas_bottom:
                self._create_item_widget(item, i)


def lazy_load_treeview(tree: ttk.Treeview, data: list, chunk_size: int = 50) -> None:
    """
    Treeview'a tembel yükleme (lazy loading)
    
    Args:
        tree: Treeview widget
        data: Gösterilecek veri listesi
        chunk_size: Tek seferde yüklenecek öğe sayısı
    """
    def load_chunk(start_index: int = 0) -> None:
        end_index = min(start_index + chunk_size, len(data))

        for i in range(start_index, end_index):
            item = data[i]
            tree.insert('', 'end', values=item)

        # Daha fazla veri varsa, sonrakini yükle
        if end_index < len(data):
            tree.after(10, lambda: load_chunk(end_index))
        else:
            logging.info(f" Toplam {len(data)} öğe yüklendi")

    # İlk chunk'ı yükle
    load_chunk()


def async_load(func: Callable, callback: Callable, error_callback: Callable = None) -> None:
    """
    Asenkron veri yükleme
    
    Args:
        func: Arka planda çalışacak fonksiyon
        callback: Sonuç geldiğinde çağrılacak fonksiyon
        error_callback: Hata olduğunda çağrılacak fonksiyon
    
    Kullanım:
        def load_data() -> None:
            # Ağır işlem
            return data
        
        def on_data_loaded(data) -> None:
            # UI güncelle
            self.display_data(data)
        
        async_load(load_data, on_data_loaded)
    """
    def worker() -> None:
        try:
            result = func()
            callback(result)
        except Exception as e:
            if error_callback:
                error_callback(e)
            else:
                logging.error(f"Async load hatası: {e}")

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


def optimize_image_loading(image_path: str, max_size: tuple = (300, 300)) -> None:
    """
    Resim yüklemeyi optimize et
    
    Args:
        image_path: Resim dosya yolu
        max_size: Maksimum boyut (genişlik, yükseklik)
    
    Returns:
        PIL Image instance
    """
    try:
        from PIL import Image

        img = Image.open(image_path)

        # Boyutlandır (aspect ratio korunarak)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        return img
    except Exception as e:
        logging.error(f"Resim optimizasyon hatası: {e}")
        return None


def batch_update(widget: tk.Widget, update_func: Callable, items: list, batch_size: int = 10) -> None:
    """
    Widget güncellemelerini toplu yap (UI donmasını önler)
    
    Args:
        widget: Güncellenecek widget
        update_func: Her öğe için çağrılacak fonksiyon
        items: Öğe listesi
        batch_size: Tek seferde işlenecek öğe sayısı
    """
    def process_batch(start_index: int = 0) -> None:
        end_index = min(start_index + batch_size, len(items))

        for i in range(start_index, end_index):
            update_func(items[i])

        # Daha fazla öğe varsa, sonrakini işle
        if end_index < len(items):
            widget.after(1, lambda: process_batch(end_index))

    process_batch()


class ProgressiveRenderer:
    """
    Aşamalı render - Büyük UI'ları parça parça yükler
    """

    def __init__(self, parent: tk.Widget) -> None:
        self.parent = parent
        self.render_queue = []

    def add_to_queue(self, render_func: Callable) -> None:
        """Render kuyruğuna ekle"""
        self.render_queue.append(render_func)

    def start_rendering(self, delay: int = 10) -> None:
        """Aşamalı render başlat"""
        if self.render_queue:
            render_func = self.render_queue.pop(0)
            render_func()

            # Sonraki render
            self.parent.after(delay, lambda: self.start_rendering(delay))


def measure_performance(func: Callable) -> Callable:
    """
    Fonksiyon performansını ölç
    
    Kullanım:
        @measure_performance
        def slow_function(self) -> None:
            # Ağır işlem
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> None:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        elapsed = (end_time - start_time) * 1000  # ms
        logging.info(f"⏱️ {func.__name__}: {elapsed:.2f}ms")

        return result

    return wrapper


# Global optimizer instance
performance_optimizer = PerformanceOptimizer()

