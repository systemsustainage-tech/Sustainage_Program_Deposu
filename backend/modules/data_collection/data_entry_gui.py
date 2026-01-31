#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Giriş Ana GUI
Görevlere göre doğru formu açar
"""

import logging
import os
import sys
from tkinter import messagebox

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import sqlite3

from sdg.data_forms.sdg_form_collection import get_sdg_form_fields, get_sdg_form_title

from .form_builder import FormBuilder
from config.database import DB_PATH


class DataEntryGUI:
    """
    Veri giriş ana arayüzü
    
    Görevin modülüne göre ilgili formu açar.
    """

    def __init__(self, parent, task_id: int, user_id: int) -> None:
        """
        DataEntryGUI başlat
        
        Args:
            parent: Ana widget
            task_id: Görev ID
            user_id: Kullanıcı ID
        """
        self.parent = parent
        self.task_id = task_id
        self.user_id = user_id

        # Görev bilgilerini al
        self.load_task_info()

        # Uygun formu aç
        self.open_appropriate_form()

    def load_task_info(self) -> None:
        """Görev bilgilerini yükle"""
        from tasks.task_manager import TaskManager

        tm = TaskManager()
        self.task = tm.get_task(self.task_id)

        if not self.task:
            messagebox.showerror("Hata", "Görev bulunamadı")
            return

    def open_appropriate_form(self) -> None:
        """Görevin modülüne göre uygun formu aç"""

        if not self.task:
            return

        module = self.task.get('related_module', '')
        item = self.task.get('related_item', '')

        # SDG formu
        if module == 'SDG' and item:
            # SDG numarasını çıkar (örn: "SDG 7" → 7)
            try:
                sdg_num = int(item.replace('SDG', '').strip())
                self.open_sdg_form(sdg_num)
            except Exception:
                messagebox.showerror("Hata", f"Geçersiz SDG numarası: {item}")

        # GRI formu
        elif module == 'GRI':
            messagebox.showinfo("Bilgi", "GRI veri formu kullanım için:\nSol menü → GRI Standartları")

        # TSRS formu
        elif module == 'TSRS':
            messagebox.showinfo("Bilgi", "TSRS veri formu kullanım için:\nSol menü → TSRS Standartları")

        else:
            messagebox.showwarning("Uyarı", f"Bu modül için form tanımlı değil: {module}")

    def open_sdg_form(self, sdg_number: int) -> None:
        """SDG formu aç"""

        # Form field'larını al
        fields = get_sdg_form_fields(sdg_number)
        title = get_sdg_form_title(sdg_number)

        if not fields:
            messagebox.showwarning("Uyarı", f"SDG {sdg_number} için form tanımlı değil")
            return

        # Kaydetme fonksiyonu
        def on_save(form_data, is_draft) -> None:
            success = self.save_sdg_data(sdg_number, form_data, is_draft)

            if success:
                if is_draft:
                    messagebox.showinfo("Başarılı", "Taslak kaydedildi")
                else:
                    messagebox.showinfo("Başarılı", "Veriler kaydedildi ve görev tamamlandı!")
                    # Pencereyi kapat
                    for widget in self.parent.winfo_children():
                        widget.destroy()
            else:
                messagebox.showerror("Hata", "Veriler kaydedilemedi")

        # Formu oluştur
        FormBuilder(self.parent, title, fields, on_save)

    def save_sdg_data(self, sdg_number: int, form_data: dict, is_draft: bool) -> bool:
        """SDG verisini kaydet"""

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            # Tablo adı
            table_name = f"sdg{sdg_number}_data" if sdg_number != 7 else "sdg7_energy_data"
            import re
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
                raise ValueError("Geçersiz tablo adı")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone() is None:
                raise ValueError("Tablo bulunamadı")

            # Dinamik olarak INSERT oluştur
            columns = list(form_data.keys())
            columns.extend(['company_id', 'task_id', 'is_draft'])

            placeholders = ', '.join(['?' for _ in columns])
            # Kolon doğrulaması
            cursor.execute("PRAGMA table_info(" + table_name + ")")
            valid_cols = [c[1] for c in cursor.fetchall()]
            safe_cols = [c for c in columns if c in valid_cols and c.isidentifier()]
            column_names = ', '.join(safe_cols)

            values = [form_data.get(c) for c in list(form_data.keys())]
            values.extend([self.task.get('company_id', 1), self.task_id, 1 if is_draft else 0])
            # değerleri safe_cols sırasına göre yeniden sırala
            value_map = dict(zip(columns, values))
            values_ordered = [value_map[c] for c in safe_cols]

            sql = "INSERT INTO " + table_name + " (" + column_names + ") VALUES (" + placeholders + ")"
            cursor.execute(sql, values_ordered)

            # Görev ilerlemesini güncelle
            if not is_draft:
                cursor.execute("""
                    UPDATE tasks 
                    SET progress = 100,
                        status = 'Tamamlandı',
                        completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (self.task_id,))

                # Bildirim gönder
                from tasks.notification_manager import NotificationManager
                nm = NotificationManager()
                nm.send_task_notification(self.task_id, 'task_completed')

            conn.commit()
            logging.info(f"[OK] SDG {sdg_number} verisi kaydedildi")
            return True

        except Exception as e:
            logging.error(f"[HATA] SDG {sdg_number} kaydetme hatası: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return False

        finally:
            conn.close()

