#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Veri Yükleme
GUI donmasını önlemek için arka planda veri yükleme
"""

import logging
import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable


class AsyncLoader:
    """Asenkron veri yükleme yardımcısı"""

    def __init__(self):
        """Utility class, başlatılmasına gerek yok"""
        pass

    @staticmethod
    def load_with_progress(parent, load_function: Callable,
                          on_complete: Callable, title: str = "Yükleniyor..."):
        """
        Veriyi arka planda yükle, progress bar göster
        
        Args:
            parent: Tkinter parent
            load_function: Veri yükleme fonksiyonu (return data)
            on_complete: Tamamlandığında çağrılacak fonksiyon (data parametresi ile)
            title: Progress dialog başlığı
        """

        # Progress dialog
        progress_window = tk.Toplevel(parent)
        progress_window.title(title)
        progress_window.geometry("400x150")
        progress_window.transient(parent)
        progress_window.grab_set()

        # Center window
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
        progress_window.geometry(f"400x150+{x}+{y}")

        # İçerik
        tk.Label(progress_window, text=title,
                font=('Segoe UI', 12, 'bold')).pack(pady=20)

        progress = ttk.Progressbar(progress_window, mode='indeterminate', length=300)
        progress.pack(pady=10)
        progress.start(10)

        status_label = tk.Label(progress_window, text="Veri yükleniyor...",
                               font=('Segoe UI', 9), fg='#666')
        status_label.pack(pady=5)

        # Arka plan thread
        result = {'data': None, 'error': None}

        def load_thread() -> None:
            """Arka planda yükle"""
            try:
                result['data'] = load_function()
            except Exception as e:
                result['error'] = e
            finally:
                # Ana thread'e geri dön
                progress_window.after(100, finish_loading)

        def finish_loading() -> None:
            """Yükleme bitti"""
            progress.stop()
            progress_window.destroy()

            if result['error']:
                from tkinter import messagebox
                messagebox.showerror("Hata", f"Veri yüklenemedi:\n{result['error']}")
            elif result['data'] is not None:
                on_complete(result['data'])

        # Thread başlat
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    @staticmethod
    def execute_async(function: Callable, on_complete: Callable = None) -> None:
        """
        Basit async execution
        
        Args:
            function: Çalıştırılacak fonksiyon
            on_complete: Tamamlandığında çağrılacak (sonuç parametresi ile)
        """
        def thread_func() -> None:
            try:
                result = function()
                if on_complete:
                    on_complete(result)
            except Exception as e:
                logging.error(f"[HATA] Async execution: {e}")

        thread = threading.Thread(target=thread_func, daemon=True)
        thread.start()


# Decorator kullanımı
def async_task(on_complete: Callable = None) -> None:
    """
    Fonksiyonu async yapan decorator
    
    Kullanım:
        @async_task(on_complete=lambda result: print(result))
        def load_data() -> None:
            # Ağır işlem
            return data
    """
    def decorator(func) -> None:
        def wrapper(*args, **kwargs) -> None:
            def thread_func() -> None:
                try:
                    result = func(*args, **kwargs)
                    if on_complete:
                        on_complete(result)
                except Exception as e:
                    logging.error(f"[HATA] {func.__name__}: {e}")

            thread = threading.Thread(target=thread_func, daemon=True)
            thread.start()

        return wrapper
    return decorator

