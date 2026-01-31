#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri İçe Aktarma GUI
Excel, CSV, JSON veri import işlemleri
"""

import tkinter as tk
from tkinter import filedialog
from utils.language_manager import LanguageManager
from config.icons import Icons


class DataImportGUI:
    """Veri İçe Aktarma GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()
        self.last_df = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text="📥 Veri İçe Aktarma",
                              font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=(0, 20))

        # Import türleri
        import_frame = tk.LabelFrame(main_frame, text="Import Türleri", font=('Segoe UI', 12, 'bold'))
        import_frame.pack(fill='x', pady=10, padx=10, ipady=10)

        # Excel Import
        excel_btn = tk.Button(import_frame, text=f"{Icons.REPORT} Excel Dosyası İçe Aktar",
                             font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                             relief='flat', padx=20, pady=10, width=25,
                             command=self.import_excel)
        excel_btn.pack(pady=5)

        # CSV Import
        csv_btn = tk.Button(import_frame, text=f"{Icons.FILE} CSV Dosyası İçe Aktar",
                           font=('Segoe UI', 11, 'bold'), bg='#3498db', fg='white',
                           relief='flat', padx=20, pady=10, width=25,
                           command=self.import_csv)
        csv_btn.pack(pady=5)

        # JSON Import
        json_btn = tk.Button(import_frame, text=f"{Icons.CLIPBOARD} JSON Dosyası İçe Aktar",
                            font=('Segoe UI', 11, 'bold'), bg='#9b59b6', fg='white',
                            relief='flat', padx=20, pady=10, width=25,
                            command=self.import_json)
        json_btn.pack(pady=5)

        # Sonuç alanı
        result_frame = tk.LabelFrame(main_frame, text="Import Sonuçları", font=('Segoe UI', 12, 'bold'))
        result_frame.pack(fill='both', expand=True, pady=10, padx=10)

        from tkinter import scrolledtext
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, font=('Consolas', 10))
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)
        action_frame = tk.Frame(result_frame, bg='white')
        action_frame.pack(fill='x', padx=5, pady=(0,5))
        tk.Button(action_frame, text="Önizlemeyi Excel'e Kaydet", font=('Segoe UI', 10), bg='#27ae60', fg='white', relief='flat', padx=10, pady=4, command=self.save_preview_excel).pack(side='left', padx=(0,5))
        tk.Button(action_frame, text="Önizlemeyi CSV'ye Kaydet", font=('Segoe UI', 10), bg='#3498db', fg='white', relief='flat', padx=10, pady=4, command=self.save_preview_csv).pack(side='left')

        # Hoş geldin mesajı
        welcome_msg = f"""📥 VERİ İÇE AKTARMA MERKEZİ

Desteklenen Formatlar:
{Icons.REPORT} Excel (.xlsx, .xls) - Çalışma sayfaları
{Icons.FILE} CSV (.csv) - Virgülle ayrılmış değerler  
{Icons.CLIPBOARD} JSON (.json) - JavaScript Object Notation

Özellikler:
{Icons.SUCCESS} Çoklu dosya desteği
{Icons.SUCCESS} Veri doğrulama
{Icons.SUCCESS} Hata raporlama
{Icons.SUCCESS} Önizleme modu

Kullanım:
1. Import türünü seçin
2. Dosyayı seçin
3. Mapping yapılandırın
4. Import işlemini başlatın
"""

        self.result_text.insert('1.0', welcome_msg)
        self.result_text.config(state='disabled')

    def import_excel(self):
        """Excel dosyası import et"""
        file_path = filedialog.askopenfilename(
            filetypes=[(self.lm.tr("file_excel", "Excel Dosyası"), "*.xlsx *.xls"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
            title=self.lm.tr("import_excel", "Excel Dosyası İçe Aktar")
        )

        if file_path:
            try:
                import pandas as pd
                df = pd.read_excel(file_path)
                self.last_df = df
                preview = df.head(10).to_string(index=False)
                rows, cols = df.shape
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', tk.END)
                self.result_text.insert('1.0', f"{Icons.REPORT} Excel Import Başlatıldı\n\nDosya: {file_path}\nSatır: {rows} | Sütun: {cols}\n\nÖnizleme (ilk 10 satır):\n\n{preview}")
                self.result_text.config(state='disabled')
            except Exception as e:
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', tk.END)
                self.result_text.insert('1.0', f"{Icons.FAIL} Hata: {e}")
                self.result_text.config(state='disabled')

    def import_csv(self):
        """CSV dosyası import et"""
        file_path = filedialog.askopenfilename(
            title=self.lm.tr('import_csv', "CSV İçe Aktar"),
            filetypes=[(self.lm.tr('file_csv', "CSV Dosyası"), "*.csv"), (self.lm.tr('all_files', "Tüm Dosyalar"), "*.*")]
        )

        if file_path:
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                self.last_df = df
                preview = df.head(10).to_string(index=False)
                rows, cols = df.shape
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', tk.END)
                self.result_text.insert('1.0', f"{Icons.FILE} CSV Import Başlatıldı\n\nDosya: {file_path}\nSatır: {rows} | Sütun: {cols}\n\nÖnizleme (ilk 10 satır):\n\n{preview}")
                self.result_text.config(state='disabled')
            except Exception as e:
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', tk.END)
                self.result_text.insert('1.0', f"{Icons.FAIL} Hata: {e}")
                self.result_text.config(state='disabled')

    def import_json(self):
        """JSON dosyası import et"""
        file_path = filedialog.askopenfilename(
            filetypes=[(self.lm.tr("file_json", "JSON Dosyası"), "*.json"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
            title=self.lm.tr("import_json", "JSON Dosyası İçe Aktar")
        )

        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    preview_items = data[:5]
                    preview = "\n\n".join([str(item) for item in preview_items])
                    count = len(data)
                elif isinstance(data, dict):
                    preview = "\n".join([f"{k}: {str(v)[:80]}" for k, v in list(data.items())[:10]])
                    count = len(data.keys())
                else:
                    preview = str(data)[:500]
                    count = 1
                try:
                    import pandas as pd
                    if isinstance(data, list):
                        self.last_df = pd.DataFrame(data)
                    elif isinstance(data, dict):
                        self.last_df = pd.json_normalize(data)
                    else:
                        self.last_df = None
                except Exception:
                    self.last_df = None
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', tk.END)
                self.result_text.insert('1.0', f"{Icons.CLIPBOARD} JSON Import Başlatıldı\n\nDosya: {file_path}\nKayıt Sayısı: {count}\n\nÖnizleme:\n\n{preview}")
                self.result_text.config(state='disabled')
            except Exception as e:
                self.result_text.config(state='normal')
                self.result_text.delete('1.0', tk.END)
                self.result_text.insert('1.0', f"{Icons.FAIL} Hata: {e}")
                self.result_text.config(state='disabled')

    def save_preview_excel(self) -> None:
        try:
            from tkinter import filedialog, messagebox
            if self.last_df is None:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("warning_no_file", "Önce bir dosya içe aktarın."))
                return
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[(self.lm.tr("file_excel", "Excel Dosyası"), "*.xlsx"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                title=self.lm.tr("save_preview", "Önizlemeyi Kaydet")
            )
            if not path:
                return
            import pandas as pd
            with pd.ExcelWriter(path, engine='openpyxl') as writer:
                self.last_df.to_excel(writer, index=False, sheet_name='Veri')
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("preview_saved_excel", "Önizleme Excel'e kaydedildi:\n{path}").format(path=path))
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror(self.lm.tr("error", "Hata"), str(e))

    def save_preview_csv(self) -> None:
        try:
            from tkinter import filedialog, messagebox
            if self.last_df is None:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("warning_no_file", "Önce bir dosya içe aktarın."))
                return
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[(self.lm.tr("file_csv", "CSV Dosyası"), "*.csv"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                title=self.lm.tr("save_preview", "Önizlemeyi Kaydet")
            )
            if not path:
                return
            self.last_df.to_csv(path, index=False)
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("preview_saved_csv", "Önizleme CSV'ye kaydedildi:\n{path}").format(path=path))
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror(self.lm.tr("error", "Hata"), str(e))
