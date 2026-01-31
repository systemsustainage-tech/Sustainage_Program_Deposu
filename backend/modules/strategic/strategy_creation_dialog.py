#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strateji Oluşturma Dialog'u
Yeni sürdürülebilirlik stratejisi oluşturma arayüzü
"""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, scrolledtext, ttk
from typing import Callable, List


class StrategyCreationDialog:
    """Strateji oluşturma dialog'u"""

    def __init__(self, parent, company_id: int, user_id: int,
                 strategy_manager, on_save: Callable = None):
        self.parent = parent
        self.company_id = company_id
        self.user_id = user_id
        self.strategy_manager = strategy_manager
        self.on_save = on_save

        self.dialog = None
        self.setup_ui()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana dialog penceresi
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(" Yeni Sürdürülebilirlik Stratejisi")
        self.dialog.geometry("800x700")
        self.dialog.resizable(True, True)
        self.dialog.configure(bg='#f8f9fa')

        # Pencereyi merkeze al
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Ana frame
        main_frame = tk.Frame(self.dialog, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text=" Yeni Sürdürülebilirlik Stratejisi",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=15)

        # Form alanları
        self.create_form_fields(main_frame)

        # Butonlar
        self.create_buttons(main_frame)

    def create_form_fields(self, parent) -> None:
        """Form alanlarını oluştur"""
        # Notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, pady=(0, 20))

        # Temel Bilgiler sekmesi
        basic_frame = tk.Frame(notebook, bg='white')
        notebook.add(basic_frame, text=" Temel Bilgiler")

        # Strateji Adı
        tk.Label(basic_frame, text="Strateji Adı *", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(20, 5))
        self.strategy_name_var = tk.StringVar()
        strategy_name_entry = tk.Entry(basic_frame, textvariable=self.strategy_name_var,
                                     font=('Segoe UI', 10), width=60)
        strategy_name_entry.pack(anchor='w', padx=20, pady=(0, 15))

        # Açıklama
        tk.Label(basic_frame, text="Açıklama", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(0, 5))
        self.description_text = scrolledtext.ScrolledText(basic_frame, height=4,
                                                         font=('Segoe UI', 10), wrap='word')
        self.description_text.pack(anchor='w', padx=20, pady=(0, 15), fill='x')

        # Vizyon
        tk.Label(basic_frame, text="Vizyon", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(0, 5))
        self.vision_text = scrolledtext.ScrolledText(basic_frame, height=3,
                                                    font=('Segoe UI', 10), wrap='word')
        self.vision_text.pack(anchor='w', padx=20, pady=(0, 15), fill='x')

        # Misyon
        tk.Label(basic_frame, text="Misyon", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(0, 5))
        self.mission_text = scrolledtext.ScrolledText(basic_frame, height=3,
                                                     font=('Segoe UI', 10), wrap='word')
        self.mission_text.pack(anchor='w', padx=20, pady=(0, 15), fill='x')

        # Zaman Ufku
        time_frame = tk.Frame(basic_frame, bg='white')
        time_frame.pack(anchor='w', padx=20, pady=(0, 15), fill='x')

        tk.Label(time_frame, text="Zaman Ufku (Yıl)", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(side='left')

        self.time_horizon_var = tk.StringVar(value="5")
        time_horizon_combo = ttk.Combobox(time_frame, textvariable=self.time_horizon_var,
                                         values=["3", "5", "7", "10"], width=10)
        time_horizon_combo.pack(side='left', padx=(10, 0))

        # Başlangıç Yılı
        tk.Label(time_frame, text="Başlangıç Yılı", font=('Segoe UI', 10, 'bold'),
                fg='#2c3e50', bg='white').pack(side='left', padx=(30, 0))

        current_year = datetime.now().year
        self.start_year_var = tk.StringVar(value=str(current_year))
        start_year_combo = ttk.Combobox(time_frame, textvariable=self.start_year_var,
                                       values=[str(year) for year in range(current_year, current_year + 6)],
                                       width=10)
        start_year_combo.pack(side='left', padx=(10, 0))

        # Değerler ve Sütunlar sekmesi
        values_frame = tk.Frame(notebook, bg='white')
        notebook.add(values_frame, text=" Değerler & Sütunlar")

        # Temel Değerler
        tk.Label(values_frame, text="Temel Değerler", font=('Segoe UI', 12, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(20, 10))

        values_help = tk.Label(values_frame, text="Her satıra bir değer yazın:",
                              font=('Segoe UI', 9), fg='#7f8c8d', bg='white')
        values_help.pack(anchor='w', padx=20, pady=(0, 5))

        self.core_values_text = scrolledtext.ScrolledText(values_frame, height=6,
                                                         font=('Segoe UI', 10), wrap='word')
        self.core_values_text.pack(anchor='w', padx=20, pady=(0, 20), fill='x')

        # Örnek değerler
        sample_values = """Çevresel Sorumluluk
Sosyal Adalet
Şeffaflık
İnovasyon
İş Birliği
Sürdürülebilirlik"""
        self.core_values_text.insert(1.0, sample_values)

        # Stratejik Sütunlar
        tk.Label(values_frame, text="Stratejik Sütunlar", font=('Segoe UI', 12, 'bold'),
                fg='#2c3e50', bg='white').pack(anchor='w', padx=20, pady=(0, 10))

        pillars_help = tk.Label(values_frame, text="Her satıra bir sütun yazın:",
                               font=('Segoe UI', 9), fg='#7f8c8d', bg='white')
        pillars_help.pack(anchor='w', padx=20, pady=(0, 5))

        self.strategic_pillars_text = scrolledtext.ScrolledText(values_frame, height=6,
                                                               font=('Segoe UI', 10), wrap='word')
        self.strategic_pillars_text.pack(anchor='w', padx=20, pady=(0, 20), fill='x')

        # Örnek sütunlar
        sample_pillars = """Çevresel Sürdürülebilirlik
Sosyal Sorumluluk
Ekonomik Değer
Kurumsal Yönetişim"""
        self.strategic_pillars_text.insert(1.0, sample_pillars)

    def create_buttons(self, parent) -> None:
        """Butonları oluştur"""
        button_frame = tk.Frame(parent, bg='#f8f9fa')
        button_frame.pack(fill='x', pady=(0, 10))

        # İptal butonu
        cancel_btn = tk.Button(button_frame, text=" İptal", font=('Segoe UI', 10, 'bold'),
                              fg='white', bg='#e74c3c', relief='flat', cursor='hand2',
                              command=self.cancel)
        cancel_btn.pack(side='right', padx=(10, 0))

        # Kaydet butonu
        save_btn = tk.Button(button_frame, text=" Kaydet", font=('Segoe UI', 10, 'bold'),
                            fg='white', bg='#27ae60', relief='flat', cursor='hand2',
                            command=self.save_strategy)
        save_btn.pack(side='right')

    def get_core_values(self) -> List[str]:
        """Temel değerleri al"""
        text = self.core_values_text.get(1.0, tk.END).strip()
        if not text:
            return []

        values = [line.strip() for line in text.split('\n') if line.strip()]
        return values

    def get_strategic_pillars(self) -> List[str]:
        """Stratejik sütunları al"""
        text = self.strategic_pillars_text.get(1.0, tk.END).strip()
        if not text:
            return []

        pillars = [line.strip() for line in text.split('\n') if line.strip()]
        return pillars

    def validate_form(self) -> bool:
        """Form doğrulama"""
        if not self.strategy_name_var.get().strip():
            messagebox.showerror("Hata", "Strateji adı zorunludur!")
            return False

        try:
            int(self.time_horizon_var.get())
            int(self.start_year_var.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz yıl değeri!")
            return False

        return True

    def save_strategy(self) -> None:
        """Stratejiyi kaydet"""
        try:
            if not self.validate_form():
                return

            # Form verilerini al
            strategy_name = self.strategy_name_var.get().strip()
            description = self.description_text.get(1.0, tk.END).strip()
            vision = self.vision_text.get(1.0, tk.END).strip()
            mission = self.mission_text.get(1.0, tk.END).strip()
            time_horizon = int(self.time_horizon_var.get())
            start_year = int(self.start_year_var.get())
            end_year = start_year + time_horizon - 1
            core_values = self.get_core_values()
            strategic_pillars = self.get_strategic_pillars()

            # Stratejiyi oluştur
            strategy_id = self.strategy_manager.create_strategy(
                company_id=self.company_id,
                strategy_name=strategy_name,
                description=description,
                vision=vision,
                mission=mission,
                core_values=core_values,
                strategic_pillars=strategic_pillars,
                time_horizon=time_horizon,
                start_year=start_year,
                end_year=end_year,
                created_by=self.user_id
            )

            if strategy_id:
                messagebox.showinfo("Başarılı", f"Strateji başarıyla oluşturuldu!\nID: {strategy_id}")

                # Callback çağır
                if self.on_save:
                    self.on_save()

                # Dialog'u kapat
                self.dialog.destroy()
            else:
                messagebox.showerror("Hata", "Strateji oluşturulamadı!")

        except Exception as e:
            messagebox.showerror("Hata", f"Strateji kaydetme hatası: {e}")

    def cancel(self) -> None:
        """İptal et"""
        self.dialog.destroy()

    def show(self) -> None:
        """Dialog'u göster"""
        if self.dialog:
            self.dialog.focus_set()
            self.dialog.wait_window()


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.withdraw()

    dialog = StrategyCreationDialog(
        parent=root,
        company_id=1,
        user_id=1,
        strategy_manager=None,
        on_save=None
    )
    dialog.show()

    root.mainloop()
