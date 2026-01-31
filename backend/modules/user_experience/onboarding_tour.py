#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İlk Kullanım Turu
Yeni kullanıcılar için rehberli tur
"""

import logging
import sqlite3
import tkinter as tk
from typing import Optional, Tuple

from utils.language_manager import LanguageManager
from config.icons import Icons


class TourStep:
    """Tek bir tur adımı"""

    def __init__(self, title_key: str, title_default: str, message_key: str, message_default: str,
                 position: Tuple[int, int], highlight_widget: Optional[tk.Widget] = None):
        self.title_key = title_key
        self.title_default = title_default
        self.message_key = message_key
        self.message_default = message_default
        self.position = position  # (x, y)
        self.highlight_widget = highlight_widget


class OnboardingTour:
    """İlk kullanım turu yöneticisi"""

    def __init__(self, parent, db_path: str, user_id: int) -> None:
        self.parent = parent
        self.db_path = db_path
        self.user_id = user_id
        self.lm = LanguageManager()
        self.steps = []
        self.current_step = 0
        self.tour_window = None
        self.highlight_overlay = None

    def add_step(self, title_key: str, title_default: str, message_key: str, message_default: str, x: int, y: int,
                widget: Optional[tk.Widget] = None):
        """Tur adımı ekle"""
        self.steps.append(TourStep(title_key, title_default, message_key, message_default, (x, y), widget))

    def should_show_tour(self) -> bool:
        """Tur gösterilmeli mi?"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT tour_completed FROM users WHERE id = ?
            """, (self.user_id,))

            result = cursor.fetchone()
            conn.close()

            return result is None or not result[0]

        except Exception:
            return True

    def mark_tour_completed(self) -> None:
        """Turu tamamlandı olarak işaretle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE users SET tour_completed = 1 WHERE id = ?
            """, (self.user_id,))

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"Tur tamamlama hatası: {e}")

    def start_tour(self) -> None:
        """Turu başlat"""
        if not self.steps:
            return

        self.current_step = 0
        self.show_step(0)

    def show_step(self, index: int) -> None:
        """Adımı göster"""
        if index < 0 or index >= len(self.steps):
            return

        self.current_step = index
        step = self.steps[index]

        # Önceki pencereyi kapat
        if self.tour_window:
            self.tour_window.destroy()

        if self.highlight_overlay:
            self.highlight_overlay.destroy()

        # Highlight overlay (yarı saydam arka plan)
        self.highlight_overlay = tk.Toplevel(self.parent)
        self.highlight_overlay.attributes('-alpha', 0.3)
        self.highlight_overlay.attributes('-topmost', True)
        self.highlight_overlay.overrideredirect(True)

        # Tam ekran
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        self.highlight_overlay.geometry(f"{screen_width}x{screen_height}+0+0")
        self.highlight_overlay.configure(bg='black')

        # İpucu penceresi
        self.tour_window = tk.Toplevel(self.parent)
        self.tour_window.overrideredirect(True)
        self.tour_window.attributes('-topmost', True)

        # Pozisyon
        x, y = step.position
        self.tour_window.geometry(f"400x250+{x}+{y}")

        # Stil
        main_frame = tk.Frame(self.tour_window, bg='white', relief=tk.RAISED, bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#3498db', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text=f" {self.lm.tr(step.title_key, step.title_default)}",
            font=('Segoe UI', 12, 'bold'),
            bg='#3498db',
            fg='white'
        ).pack(side=tk.LEFT, padx=15, pady=15)

        # Adım sayacı
        tk.Label(
            header_frame,
            text=f"{index + 1}/{len(self.steps)}",
            font=('Segoe UI', 10),
            bg='#3498db',
            fg='white'
        ).pack(side=tk.RIGHT, padx=15, pady=15)

        # İçerik
        content_frame = tk.Frame(main_frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            content_frame,
            text=self.lm.tr(step.message_key, step.message_default),
            font=('Segoe UI', 10),
            bg='white',
            wraplength=350,
            justify=tk.LEFT
        ).pack(anchor='w')

        # Butonlar
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        if index > 0:
            tk.Button(
                button_frame,
                text=f"{Icons.LEFT} {self.lm.tr('btn_back', 'Geri')}",
                command=lambda: self.show_step(index - 1),
                bg='#95a5a6',
                fg='white',
                font=('Segoe UI', 9),
                cursor='hand2',
                padx=15,
                pady=5
            ).pack(side=tk.LEFT)

        if index < len(self.steps) - 1:
            tk.Button(
                button_frame,
                text=f"{self.lm.tr('btn_next', 'İleri')} ️",
                command=lambda: self.show_step(index + 1),
                bg='#27ae60',
                fg='white',
                font=('Segoe UI', 9, 'bold'),
                cursor='hand2',
                padx=15,
                pady=5
            ).pack(side=tk.RIGHT)
        else:
            tk.Button(
                button_frame,
                text=f" {self.lm.tr('btn_finish', 'Bitir')}",
                command=self.finish_tour,
                bg='#27ae60',
                fg='white',
                font=('Segoe UI', 9, 'bold'),
                cursor='hand2',
                padx=20,
                pady=5
            ).pack(side=tk.RIGHT)

        tk.Button(
            button_frame,
            text=self.lm.tr('skip', 'Atla'),
            command=self.skip_tour,
            bg='#ecf0f1',
            fg='#7f8c8d',
            font=('Segoe UI', 8),
            cursor='hand2',
            padx=10,
            pady=3,
            relief=tk.FLAT
        ).pack(side=tk.RIGHT, padx=(0, 10))

    def finish_tour(self) -> None:
        """Turu bitir"""
        self.mark_tour_completed()
        self.close_tour()

        # Tebrik mesajı
        from tkinter import messagebox
        messagebox.showinfo(
            f"{self.lm.tr('congratulations', 'Tebrikler!')} ",
            self.lm.tr('tour_completed_msg', "İlk kullanım turunu tamamladınız!\n\nArtık sistemi kullanmaya başlayabilirsiniz.")
        )

    def skip_tour(self) -> None:
        """Turu atla"""
        from tkinter import messagebox
        if messagebox.askyesno(self.lm.tr('confirmation', "Onay"), self.lm.tr('skip_tour_confirm', "Turu atlamak istediğinizden emin misiniz?")):
            self.mark_tour_completed()
            self.close_tour()

    def close_tour(self) -> None:
        """Tur pencerelerini kapat"""
        if self.tour_window:
            self.tour_window.destroy()
            self.tour_window = None

        if self.highlight_overlay:
            self.highlight_overlay.destroy()
            self.highlight_overlay = None


# Varsayılan tur oluşturucu
def create_default_tour(parent, db_path: str, user_id: int) -> OnboardingTour:
    """Varsayılan tur oluştur"""
    tour = OnboardingTour(parent, db_path, user_id)
    from utils.language_manager import LanguageManager
    lm = LanguageManager()

    # Adımlar
    tour.add_step(
        'welcome', lm.tr('tour_welcome_title', 'Hoş Geldiniz!'),
        'tour_welcome_msg', lm.tr('tour_welcome_msg', "SUSTAINAGE sistemine hoş geldiniz!\n\nBu kısa tur, sistemin temel özelliklerini tanıtacak."),
        400, 300
    )

    tour.add_step(
        'main_menu', lm.tr('tour_main_menu_title', 'Ana Menü'),
        'tour_main_menu_msg', lm.tr('tour_main_menu_msg', "Sol taraftaki menüden tüm modüllere erişebilirsiniz.\n\n• SDG Göstergeleri\n• GRI Standartları\n• TSRS Raporlaması\n• Karbon Yönetimi\n• ve daha fazlası..."),
        100, 150
    )

    tour.add_step(
        'data_entry', lm.tr('tour_data_entry_title', 'Veri Girişi'),
        'tour_data_entry_msg', lm.tr('tour_data_entry_msg', "Her modülde kolay veri giriş formları bulunur.\n\nVerilerinizi girin, sistem otomatik olarak hesaplamalar yapar ve raporlar oluşturur."),
        350, 200
    )

    tour.add_step(
        'reporting', lm.tr('tour_reporting_title', 'Raporlama'),
        'tour_reporting_msg', lm.tr('tour_reporting_msg', "Raporlama menüsünden profesyonel sürdürülebilirlik raporları oluşturabilirsiniz.\n\n• PDF Export\n• Excel Export\n• Özelleştirilebilir şablonlar"),
        350, 200
    )

    tour.add_step(
        'help', lm.tr('tour_help_title', 'Yardım'),
        'tour_help_msg', lm.tr('tour_help_msg', "Herhangi bir ekranda  simgesine tıklayarak yardım alabilirsiniz.\n\nBaşarılar dileriz! "),
        400, 300
    )

    return tour

