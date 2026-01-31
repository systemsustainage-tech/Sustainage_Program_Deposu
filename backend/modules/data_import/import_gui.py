#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Import GUI
Excel ve CSV import arayüzü
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from utils.language_manager import LanguageManager
from .data_importer import DataImporter
from .import_templates import ImportTemplateManager
from config.icons import Icons


class DataImportGUI:
    """Veri import arayüzü"""

    def __init__(self, parent, db_path: str, company_id: int = 1, user_id: Optional[int] = None) -> None:
        self.parent = parent
        self.db_path = db_path
        self.company_id = company_id
        self.user_id = user_id
        self.lm = LanguageManager()
        self.importer = DataImporter(db_path)

        self.setup_gui()

    def setup_gui(self) -> None:
        """GUI bileşenlerini oluştur"""
        # Ana başlık
        title_frame = tk.Frame(self.parent, bg='#2c3e50', height=32)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text=self.lm.tr("data_import_title", "Veri Import (Excel / CSV)"),
            font=('Segoe UI', 12, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=6)

        # İçerik
        content_frame = tk.Frame(self.parent, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # 1. Şablon Seçimi
        section1 = tk.LabelFrame(
            content_frame,
            text=self.lm.tr("select_template_step", "1️⃣ Şablon Seçin"),
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=12,
            pady=10
        )
        section1.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        canvas = tk.Canvas(section1, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(section1, orient='vertical', command=canvas.yview)
        inner = tk.Frame(canvas, bg='white')
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        window_id = canvas.create_window((0, 0), window=inner, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        templates_grid = tk.Frame(inner, bg='white')
        templates_grid.pack(fill='both', expand=True)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(window_id, width=e.width))

        self.selected_template = tk.StringVar()

        for i, template in enumerate(ImportTemplateManager.get_all_templates()):
            row = i // 2
            col = i % 2

            card = tk.Frame(templates_grid, bg='#ecf0f1', relief=tk.RAISED, bd=1)
            card.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')

            radio = tk.Radiobutton(
                card,
                text=template['name'],
                variable=self.selected_template,
                value=template['id'],
                font=('Segoe UI', 10, 'bold'),
                bg='#ecf0f1',
                activebackground='#ecf0f1',
                cursor='hand2'
            )
            radio.pack(anchor='w', padx=8, pady=(8, 4))

            tk.Label(
                card,
                text=template['description'],
                font=('Segoe UI', 9),
                bg='#ecf0f1',
                fg='#7f8c8d',
                wraplength=220,
                justify=tk.LEFT
            ).pack(anchor='w', padx=8, pady=(0, 8))

        templates_grid.columnconfigure(0, weight=1)
        templates_grid.columnconfigure(1, weight=1)

        # Şablon indirme
        download_btn = tk.Button(
            section1,
            text=self.lm.tr("download_empty_template", "Boş Şablon İndir"),
            command=self.download_template,
            bg='#3498db',
            fg='white',
            font=('Segoe UI', 10),
            cursor='hand2',
            padx=12,
            pady=4
        )
        download_btn.pack(pady=(8, 0))

        # 2. Dosya Seçimi
        section2 = tk.LabelFrame(
            content_frame,
            text=self.lm.tr("select_file_step", "2️⃣ Dosya Seçin"),
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=12,
            pady=10
        )
        section2.pack(fill=tk.X, pady=(0, 12))

        file_frame = tk.Frame(section2, bg='white')
        file_frame.pack(fill=tk.X)

        self.file_path_var = tk.StringVar(value=self.lm.tr("no_file_selected", "Dosya seçilmedi"))
        tk.Label(
            file_frame,
            textvariable=self.file_path_var,
            font=('Segoe UI', 10),
            bg='white',
            fg='#7f8c8d',
            anchor='w'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            file_frame,
            text=self.lm.tr("select_file", "Dosya Seç"),
            command=self.select_file,
            bg='#27ae60',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            cursor='hand2',
            padx=14,
            pady=6
        ).pack(side=tk.RIGHT)

        # 3. Import
        section3 = tk.LabelFrame(
            content_frame,
            text=self.lm.tr("import_step", "3️⃣ İmport"),
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=12,
            pady=10
        )
        section3.pack(fill=tk.X, pady=(0, 12))

        tk.Button(
            section3,
            text=self.lm.tr("start_import", "Import Başlat"),
            command=self.start_import,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            cursor='hand2',
            padx=20,
            pady=8
        ).pack()

        # 4. Geçmiş
        section4 = tk.LabelFrame(
            content_frame,
            text=" " + self.lm.tr("import_history", "Import Geçmişi"),
            font=('Segoe UI', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            padx=12,
            pady=10
        )
        section4.pack(fill=tk.BOTH, expand=True)

        # Treeview
        tree_frame = tk.Frame(section4)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_tree = ttk.Treeview(
            tree_frame,
            columns=('date', 'type', 'file', 'status', 'rows'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_tree.yview)

        self.history_tree.heading('date', text=self.lm.tr("col_date", "Tarih"))
        self.history_tree.heading('type', text=self.lm.tr("col_type", "Tip"))
        self.history_tree.heading('file', text=self.lm.tr("col_file", "Dosya"))
        self.history_tree.heading('status', text=self.lm.tr("col_status", "Durum"))
        self.history_tree.heading('rows', text=self.lm.tr("col_rows", "Satırlar"))

        self.history_tree.column('date', width=150, anchor='center')
        self.history_tree.column('type', width=100, anchor='center')
        self.history_tree.column('file', width=200, anchor='w')
        self.history_tree.column('status', width=120, anchor='center')
        self.history_tree.column('rows', width=150, anchor='center')

        self.load_history()

    def download_template(self) -> None:
        """Boş şablon indir"""
        template_id = self.selected_template.get()
        if not template_id:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_template_warning", "Lütfen bir şablon seçin"))
            return

        # Kayıt yeri seç
        file_path = filedialog.asksaveasfilename(
            title=self.lm.tr("save_template", "Şablonu Kaydet"),
            defaultextension=".xlsx",
            filetypes=[(self.lm.tr("file_excel", "Excel"), "*.xlsx"), (self.lm.tr("file_csv", "CSV"), "*.csv")]
        )

        if not file_path:
            return

        # Format
        format_type = 'excel' if file_path.endswith('.xlsx') else 'csv'

        # Şablonu oluştur
        success = ImportTemplateManager.create_template_file(
            template_name=template_id,
            output_path=file_path,
            format=format_type
        )

        if success:
            messagebox.showinfo(
                self.lm.tr("success", "Başarılı"),
                f"{self.lm.tr('template_saved_success', 'Şablon başarıyla kaydedildi')}:\n{file_path}\n\n{self.lm.tr('fill_template_info', 'Şimdi bu şablonu doldurup import edebilirsiniz.')}"
            )
        else:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("template_create_error", "Şablon oluşturulamadı"))

    def select_file(self) -> None:
        """Dosya seç"""
        file_path = filedialog.askopenfilename(
            title=self.lm.tr('select_import_file', "Import Dosyası Seç"),
            filetypes=[
                (self.lm.tr('file_excel', "Excel Dosyası"), "*.xlsx *.xls"),
                (self.lm.tr('file_csv', "CSV Dosyası"), "*.csv"),
                (self.lm.tr('all_files', "Tüm Dosyalar"), "*.*")
            ]
        )

        if file_path:
            self.file_path_var.set(file_path)

    def start_import(self) -> None:
        """Import başlat"""
        # Kontroller
        template_id = self.selected_template.get()
        if not template_id:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_template_warning", "Lütfen bir şablon seçin"))
            return

        file_path = self.file_path_var.get()
        if not file_path or file_path == "Dosya seçilmedi":
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_file_warning", "Lütfen bir dosya seçin"))
            return

        if not os.path.exists(file_path):
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("file_not_found", "Dosya bulunamadı"))
            return

        # Şablon bilgilerini al
        template = ImportTemplateManager.get_template(template_id)
        if not template:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("template_info_error", "Şablon bilgileri alınamadı"))
            return

        # Onay
        if not messagebox.askyesno(
            self.lm.tr("confirmation", "Onay"),
            self.lm.tr("import_confirm", "Aşağıdaki dosya import edilecek:") + "\n\n" +
            f"{self.lm.tr('file', 'Dosya')}: {os.path.basename(file_path)}\n" +
            f"{self.lm.tr('template', 'Şablon')}: {template['name']}\n" +
            f"{self.lm.tr('target_table', 'Hedef Tablo')}: {template['target_table']}\n\n" +
            self.lm.tr("continue_question", "Devam etmek istiyor musunuz?")
        ):
            return

        # Progress dialog
        progress_window = tk.Toplevel(self.parent)
        progress_window.title(self.lm.tr("import_in_progress", "Import Devam Ediyor"))
        progress_window.geometry("500x200")
        progress_window.transient(self.parent)
        progress_window.grab_set()

        tk.Label(
            progress_window,
            text=f"{Icons.WAIT} " + self.lm.tr("importing_data", "Veri import ediliyor..."),
            font=('Segoe UI', 14, 'bold')
        ).pack(pady=20)

        progress_bar = ttk.Progressbar(
            progress_window,
            mode='indeterminate',
            length=400
        )
        progress_bar.pack(pady=10)
        progress_bar.start()

        status_label = tk.Label(
            progress_window,
            text=self.lm.tr("process_started", "İşlem başladı..."),
            font=('Segoe UI', 10)
        )
        status_label.pack(pady=10)

        progress_window.update()

        # Import işlemi
        try:
            result = self.importer.import_data(
                company_id=self.company_id,
                file_path=file_path,
                import_type=template_id,
                column_mapping=template['column_mapping'],
                target_table=template['target_table'],
                transformation_rules=template.get('transformation_rules'),
                imported_by=self.user_id
            )

            progress_bar.stop()
            progress_window.destroy()

            # Sonuç
            if result['failed'] == 0:
                messagebox.showinfo(
                    self.lm.tr("success", "Başarılı"),
                    " " + self.lm.tr("import_success", "Import başarıyla tamamlandı!") + "\n\n" +
                    f"{self.lm.tr('total', 'Toplam')}: {result['total_rows']} {self.lm.tr('rows', 'satır')}\n" +
                    f"{self.lm.tr('successful', 'Başarılı')}: {result['successful']} {self.lm.tr('rows', 'satır')}\n" +
                    f"{self.lm.tr('failed', 'Başarısız')}: {result['failed']} {self.lm.tr('rows', 'satır')}"
                )
            else:
                # Hata detayları göster
                error_msg = self.lm.tr("import_completed_with_errors", "Import tamamlandı ancak bazı hatalar oluştu:") + "\n\n" + \
                           f"{self.lm.tr('total', 'Toplam')}: {result['total_rows']} {self.lm.tr('rows', 'satır')}\n" + \
                           f"{self.lm.tr('successful', 'Başarılı')}: {result['successful']} {self.lm.tr('rows', 'satır')}\n" + \
                           f"{self.lm.tr('failed', 'Başarısız')}: {result['failed']} {self.lm.tr('rows', 'satır')}\n\n" + \
                           self.lm.tr("first_5_errors", "İlk 5 hata:") + "\n" + \
                           "\n".join(result['errors'][:5])

                if len(result['errors']) > 5:
                    error_msg += f"\n\n... {self.lm.tr('and_more_errors', 've {count} hata daha').format(count=len(result['errors']) - 5)}"

                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), error_msg)

            # Geçmişi yenile
            self.load_history()

        except Exception as e:
            progress_bar.stop()
            progress_window.destroy()
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('import_error', 'Import hatası')}:\n\n{str(e)}")

    def load_history(self) -> None:
        """Import geçmişini yükle"""
        # Temizle
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Geçmişi al
        history = self.importer.get_import_history(self.company_id, limit=20)

        # Göster
        for record in history:
            status_text = {
                'pending': f"{Icons.WAIT} {self.lm.tr('status_pending', 'Bekliyor')}",
                'in_progress': f"{Icons.PLAY} {self.lm.tr('status_in_progress', 'Devam Ediyor')}",
                'completed': self.lm.tr('status_completed', ' Tamamlandı'),
                'completed_with_errors': self.lm.tr('status_completed_errors', '️ Hatalarla Tamamlandı'),
                'failed': self.lm.tr('status_failed', ' Başarısız')
            }.get(record['status'], record['status'])

            rows_text = f"{record['successful_rows']}/{record['total_rows']}"

            self.history_tree.insert('', tk.END, values=(
                record['imported_at'][:19] if record['imported_at'] else '',
                record['type'].upper(),
                record['file_name'],
                status_text,
                rows_text
            ))

