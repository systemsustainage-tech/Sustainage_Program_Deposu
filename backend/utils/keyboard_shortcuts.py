import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Klavye Kısayolları Modülü
Global ve modül-spesifik klavye kısayolları
"""

import tkinter as tk
from typing import Callable


class KeyboardShortcuts:
    """Klavye kısayolları yöneticisi"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.shortcuts = {}
        self.disabled = False

    def register(self, key_combination: str, callback: Callable, description: str = "") -> None:
        """
        Klavye kısayolu kaydet
        
        Args:
            key_combination: "<Control-s>", "<F5>", "<Escape>", vb.
            callback: Çağrılacak fonksiyon
            description: Kısayol açıklaması
        """
        self.shortcuts[key_combination] = {
            'callback': callback,
            'description': description
        }

        # Kısayolu bağla
        self.root.bind(key_combination, lambda e: self._handle_shortcut(key_combination, e))

    def _handle_shortcut(self, key_combination: str, event) -> None:
        """Kısayol işleyici"""
        if self.disabled:
            return

        if key_combination in self.shortcuts:
            try:
                self.shortcuts[key_combination]['callback']()
            except Exception as e:
                logging.error(f"Kısayol hatası ({key_combination}): {e}")

    def unregister(self, key_combination: str) -> None:
        """Kısayolu kaldır"""
        if key_combination in self.shortcuts:
            self.root.unbind(key_combination)
            del self.shortcuts[key_combination]

    def disable_all(self) -> None:
        """Tüm kısayolları geçici olarak devre dışı bırak"""
        self.disabled = True

    def enable_all(self) -> None:
        """Tüm kısayolları aktifleştir"""
        self.disabled = False

    def get_shortcuts_help(self) -> str:
        """Tüm kısayolların yardım metnini döndür"""
        help_text = "Klavye Kısayolları:\n\n"

        for key, data in self.shortcuts.items():
            description = data['description'] or "Açıklama yok"
            # Key'i kullanıcı dostu hale getir
            user_friendly_key = key.replace("<Control-", "Ctrl+").replace("<", "").replace(">", "").upper()
            help_text += f"{user_friendly_key:15} - {description}\n"

        return help_text

    def show_shortcuts_window(self) -> None:
        """Kısayollar penceresi göster"""
        window = tk.Toplevel(self.root)
        window.title("Klavye Kısayolları")
        window.geometry("500x600")
        window.configure(bg='white')

        # Başlık
        title = tk.Label(window, text="⌨️ Klavye Kısayolları",
                        font=('Segoe UI', 16, 'bold'), fg='#2c3e50', bg='white')
        title.pack(pady=20)

        # Kısayollar listesi
        frame = tk.Frame(window, bg='white')
        frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Başlıklar
        header_frame = tk.Frame(frame, bg='#f8f9fa')
        header_frame.pack(fill='x', pady=(0, 10))

        tk.Label(header_frame, text="Kısayol", font=('Segoe UI', 11, 'bold'),
                bg='#f8f9fa', width=20).pack(side='left', padx=10, pady=5)
        tk.Label(header_frame, text="Açıklama", font=('Segoe UI', 11, 'bold'),
                bg='#f8f9fa').pack(side='left', padx=10, pady=5)

        # Kısayollar
        for key, data in sorted(self.shortcuts.items()):
            row = tk.Frame(frame, bg='white', relief='solid', bd=1)
            row.pack(fill='x', pady=2)

            user_friendly_key = (key.replace("<Control-", "Ctrl+")
                                   .replace("<Alt-", "Alt+")
                                   .replace("<Shift-", "Shift+")
                                   .replace("<", "")
                                   .replace(">", "")
                                   .upper())

            tk.Label(row, text=user_friendly_key, font=('Courier', 10, 'bold'),
                    bg='white', width=20).pack(side='left', padx=10, pady=5)
            tk.Label(row, text=data['description'], font=('Segoe UI', 10),
                    bg='white', fg='#666').pack(side='left', padx=10, pady=5)

        # Kapat butonu
        close_btn = tk.Button(window, text="Kapat", font=('Segoe UI', 10),
                            bg='#95a5a6', fg='white', relief='flat',
                            command=window.destroy)
        close_btn.pack(pady=20)


def setup_global_shortcuts(root: tk.Tk, app_instance) -> KeyboardShortcuts:
    """
    Global klavye kısayollarını ayarla
    
    Args:
        root: Ana Tk penceresi
        app_instance: MainApp instance (callback'ler için)
    
    Returns:
        KeyboardShortcuts instance
    """
    shortcuts = KeyboardShortcuts(root)

    # F1 - Yardım
    shortcuts.register("<F1>",
        lambda: shortcuts.show_shortcuts_window(),
        "Klavye kısayolları yardımı")

    # F5 - Yenile
    shortcuts.register("<F5>",
        lambda: refresh_current_view(app_instance),
        "Mevcut görünümü yenile")

    # Escape - Kapat/İptal
    shortcuts.register("<Escape>",
        lambda: handle_escape(app_instance),
        "İptal/Geri")

    # Ctrl+S - Kaydet
    shortcuts.register("<Control-s>",
        lambda: handle_save(app_instance),
        "Kaydet")

    # Ctrl+F - Ara
    shortcuts.register("<Control-f>",
        lambda: handle_search(app_instance),
        "Ara")

    # Ctrl+N - Yeni
    shortcuts.register("<Control-n>",
        lambda: handle_new(app_instance),
        "Yeni kayıt")

    # Ctrl+E - Düzenle
    shortcuts.register("<Control-e>",
        lambda: handle_edit(app_instance),
        "Düzenle")

    # Delete - Sil
    shortcuts.register("<Delete>",
        lambda: handle_delete(app_instance),
        "Sil")

    # Ctrl+Q - Çıkış
    shortcuts.register("<Control-q>",
        lambda: app_instance.exit_application() if hasattr(app_instance, 'exit_application') else None,
        "Çıkış")

    # Ctrl+H - Ana Sayfa
    shortcuts.register("<Control-h>",
        lambda: app_instance.show_dashboard() if hasattr(app_instance, 'show_dashboard') else None,
        "Ana Sayfa")

    return shortcuts


def refresh_current_view(app_instance) -> None:
    """Mevcut görünümü yenile (F5)"""
    try:
        # Mevcut modülü yeniden yükle
        if hasattr(app_instance, 'current_module'):
            module_name = app_instance.current_module
            if hasattr(app_instance, f'show_{module_name}'):
                getattr(app_instance, f'show_{module_name}')()
        logging.info(" Görünüm yenilendi (F5)")
    except Exception as e:
        logging.error(f"Yenileme hatası: {e}")


def handle_escape(app_instance) -> None:
    """Escape tuşu işleyici"""
    try:
        # Açık modal pencere varsa kapat
        for widget in app_instance.parent.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
                logging.info(" Modal pencere kapatıldı (Escape)")
                return

        # Modal yoksa ana sayfaya dön
        if hasattr(app_instance, 'show_dashboard'):
            app_instance.show_dashboard()
            logging.info(" Ana sayfaya dönüldü (Escape)")
    except Exception as e:
        logging.error(f"Escape hatası: {e}")


def handle_save(app_instance) -> None:
    """Ctrl+S - Kaydetme işleyici"""
    try:
        # Aktif pencerede kaydet fonksiyonu varsa çağır
        focused = app_instance.parent.focus_get()

        # Fokustaki widget'ın parent'ını bul
        current_widget = focused
        while current_widget:
            if hasattr(current_widget, 'save_data'):
                current_widget.save_data()
                logging.info(" Veri kaydedildi (Ctrl+S)")
                return
            current_widget = current_widget.master if hasattr(current_widget, 'master') else None

        logging.info("️ Kaydetme fonksiyonu bulunamadı")
    except Exception as e:
        logging.error(f"Kaydetme hatası: {e}")


def handle_search(app_instance) -> None:
    """Ctrl+F - Arama işleyici"""
    try:
        # Arama kutusu varsa focus yap
        for widget in app_instance.parent.winfo_children():
            if isinstance(widget, (tk.Entry, tk.Text)):
                # "Ara" veya "Search" kelimesi geçen widget'ları bul
                try:
                    if hasattr(widget, 'master'):
                        for child in widget.master.winfo_children():
                            if isinstance(child, tk.Label):
                                label_text = str(child.cget('text')).lower()
                                if 'ara' in label_text or 'search' in label_text:
                                    widget.focus_set()
                                    logging.info(" Arama kutusuna odaklandı (Ctrl+F)")
                                    return
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

        logging.info("️ Arama kutusu bulunamadı")
    except Exception as e:
        logging.error(f"Arama hatası: {e}")


def handle_new(app_instance) -> None:
    """Ctrl+N - Yeni kayıt işleyici"""
    try:
        # Mevcut modüle göre yeni kayıt fonksiyonu çağır
        logging.info(" Yeni kayıt (Ctrl+N)")
    except Exception as e:
        logging.error(f"Yeni kayıt hatası: {e}")


def handle_edit(app_instance) -> None:
    """Ctrl+E - Düzenleme işleyici"""
    try:
        logging.info(" Düzenleme (Ctrl+E)")
    except Exception as e:
        logging.error(f"Düzenleme hatası: {e}")


def handle_delete(app_instance) -> None:
    """Delete - Silme işleyici"""
    try:
        # Seçili öğeyi sil
        logging.info(" Silme (Delete)")
    except Exception as e:
        logging.error(f"Silme hatası: {e}")

