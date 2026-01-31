#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Doğrulama GUI
Veri kalitesi kontrol ve doğrulama sistemi
"""

import tkinter as tk
from tkinter import ttk
from utils.language_manager import LanguageManager
from config.icons import Icons


class ValidationGUI:
    """Veri Doğrulama GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()

        self.setup_ui()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text=f"{Icons.SUCCESS} Veri Doğrulama Merkezi",
                              font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=(0, 20))

        # Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)

        # Veri Kalitesi Sekmesi
        quality_frame = tk.Frame(notebook, bg='white')
        notebook.add(quality_frame, text=f"{Icons.REPORT} Veri Kalitesi")

        tk.Label(quality_frame, text=f"{Icons.REPORT} Veri Kalitesi Kontrol Araçları",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=(20,10))
        btn = ttk.Button(quality_frame, text="Dosya Seç ve Validasyon Çalıştır", command=self.run_basic_validation)
        btn.pack(pady=(0,10))
        from tkinter import scrolledtext
        self.validation_output = scrolledtext.ScrolledText(quality_frame, height=12, font=('Consolas', 10))
        self.validation_output.pack(fill='both', expand=True, padx=10, pady=10)
        ttk.Button(quality_frame, text="Raporu Kaydet", command=self.save_validation_report).pack(pady=(0,10))

        # Validasyon Kuralları
        rules_frame = tk.Frame(notebook, bg='white')
        notebook.add(rules_frame, text=f"{Icons.CLIPBOARD} Validasyon Kuralları")

        tk.Label(rules_frame, text=f"{Icons.CLIPBOARD} Validasyon Kuralları Yönetimi",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=30)

        # Raporlar
        reports_frame = tk.Frame(notebook, bg='white')
        notebook.add(reports_frame, text=f"{Icons.CHART_UP} Kalite Raporları")

        tk.Label(reports_frame, text=f"{Icons.CHART_UP} Veri Kalitesi Raporları",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=30)

        # Geliştirme mesajı
        for frame in [rules_frame, reports_frame]:
            tk.Label(frame, text="🚧 Bu özellik geliştiriliyor...",
                    font=('Segoe UI', 12), fg='#e67e22', bg='white').pack(pady=20)

    def run_basic_validation(self) -> None:
        try:
            import os
            from tkinter import filedialog
            path = filedialog.askopenfilename(
                title=self.lm.tr("select_data_file", "Veri Dosyası Seç"),
                filetypes=[
                    (self.lm.tr("data_files", "Veri dosyaları"), "*.xlsx *.xls *.csv *.json"),
                    (self.lm.tr("all_files", "Tüm dosyalar"), "*.*"),
                ]
            )
            if not path:
                return
            summary = []
            ext = os.path.splitext(path)[1].lower()
            if ext in [".xlsx", ".xls"]:
                import pandas as pd
                df = pd.read_excel(path)
            elif ext == ".csv":
                import pandas as pd
                df = pd.read_csv(path)
            elif ext == ".json":
                import json
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    import pandas as pd
                    df = pd.DataFrame(data)
                else:
                    import pandas as pd
                    df = pd.json_normalize(data)
            else:
                return
            rows, cols = df.shape
            summary.append(f"Dosya: {path}")
            summary.append(f"Satır: {rows} | Sütun: {cols}")
            empty_counts = df.isna().sum()
            summary.append("Boş Değer Sayıları:")
            for col, cnt in empty_counts.items():
                summary.append(f"- {col}: {cnt}")
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                out_of_range = {}
                for col in numeric_cols:
                    s = df[col].dropna()
                    out_of_range[col] = int(((s < 0) | (s > 100)).sum())
                summary.append("0-100 aralığı dışında kalan değer sayıları:")
                for col, cnt in out_of_range.items():
                    summary.append(f"- {col}: {cnt}")
            preview = df.head(5).to_string(index=False)
            summary.append("Önizleme (ilk 5 satır):")
            summary.append(preview)
            self.validation_output.config(state='normal')
            self.validation_output.delete('1.0', tk.END)
            self.validation_output.insert('1.0', "\n".join(summary))
            self.validation_output.config(state='disabled')
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Hata", str(e))

    def save_validation_report(self) -> None:
        try:
            from tkinter import filedialog, messagebox
            content = self.validation_output.get('1.0', 'end-1c')
            if not content.strip():
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("no_content_to_save", "Kaydedilecek rapor içeriği yok."))
                return
            path = filedialog.asksaveasfilename(
                defaultextension='.txt',
                filetypes=[(self.lm.tr("file_text", "Metin Dosyası"), '*.txt'), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                title=self.lm.tr("save_report", "Raporu Kaydet")
            )
            if not path:
                return
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("report_saved_success", "Rapor kaydedildi:\n{path}").format(path=path))
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror(self.lm.tr("error", "Hata"), str(e))
