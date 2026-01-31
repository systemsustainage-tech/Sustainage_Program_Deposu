import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Raporlama GUI
PDF ve DOCX formatlarında rapor oluşturma arayüzü
"""

import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from utils.language_manager import LanguageManager

from .sdg_reporting import SDGReporting


class SDGReportingGUI:
    """SDG Raporlama GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.reporting = SDGReporting()
        self.lm = LanguageManager()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Raporlama arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#2c3e50', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        # Geri butonu
        back_btn = tk.Button(header_frame, text=f" {self.lm.tr('btn_back', 'Geri')}",
                             font=('Segoe UI', 10, 'bold'), bg='#1f2a36', fg='white',
                             relief='flat', bd=0, padx=15, pady=8,
                             command=self.back_to_sdg)
        back_btn.pack(side='left', padx=15, pady=15)

        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        title_frame.pack(side='left', padx=20, pady=15)

        title_label = tk.Label(title_frame, text=self.lm.tr("sdg_reporting_title", "SDG Raporlama Sistemi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(side='left')

        subtitle_label = tk.Label(title_frame, text=self.lm.tr("sdg_reporting_subtitle", "PDF ve DOCX formatlarında rapor oluşturma"),
                                 font=('Segoe UI', 11), fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(side='left', padx=(10, 0))

        # Ana içerik - Tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Rapor Oluşturma sekmesi
        self.create_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.create_frame, text=f" {self.lm.tr('tab_create_report', 'Rapor Oluştur')}")
        self.setup_create_tab()

        # Rapor Şablonları sekmesi
        self.templates_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.templates_frame, text=f" {self.lm.tr('tab_templates', 'Şablonlar')}")
        self.setup_templates_tab()

        # Rapor Geçmişi sekmesi
        self.history_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.notebook.add(self.history_frame, text=f" {self.lm.tr('tab_history', 'Geçmiş')}")
        self.setup_history_tab()

    def back_to_sdg(self) -> None:
        """SDG ana ekranına geri dön"""
        try:
            for widget in self.parent.winfo_children():
                widget.destroy()
            from .sdg_gui import SDGGUI
            SDGGUI(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), 
                               f"{self.lm.tr('err_back_nav', 'Geri dönme işleminde hata')}: {str(e)}")

    def setup_create_tab(self) -> None:
        """Rapor oluşturma sekmesini oluştur"""
        # Sol panel - Rapor ayarları
        left_panel = tk.Frame(self.create_frame, bg='white', relief='raised', bd=1)
        left_panel.pack(side='left', fill='y', padx=(0, 10), pady=10, ipadx=10, ipady=10)

        # Rapor türü seçimi
        tk.Label(left_panel, text=self.lm.tr("lbl_report_type", "Rapor Türü:"), font=('Segoe UI', 12, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 5))

        self.report_type_var = tk.StringVar(value='basic')
        report_types = [
            (self.lm.tr("report_type_basic", "Temel Rapor"), 'basic'),
            (self.lm.tr("report_type_detailed", "Detaylı Rapor"), 'detailed'),
            (self.lm.tr("report_type_executive", "Yönetici Özeti"), 'executive')
        ]

        for text, value in report_types:
            rb = tk.Radiobutton(left_panel, text=text, variable=self.report_type_var,
                               value=value, bg='white', font=('Segoe UI', 10))
            rb.pack(anchor='w', pady=2)

        # Format seçimi
        tk.Label(left_panel, text=f"\n{self.lm.tr('lbl_output_format', 'Çıktı Formatı:')}", font=('Segoe UI', 12, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(10, 5))

        self.format_var = tk.StringVar(value='PDF')
        format_frame = tk.Frame(left_panel, bg='white')
        format_frame.pack(anchor='w', pady=(0, 10))

        pdf_rb = tk.Radiobutton(format_frame, text="PDF", variable=self.format_var,
                               value='PDF', bg='white', font=('Segoe UI', 10))
        pdf_rb.pack(side='left', padx=(0, 10))

        docx_rb = tk.Radiobutton(format_frame, text="DOCX", variable=self.format_var,
                                value='DOCX', bg='white', font=('Segoe UI', 10))
        docx_rb.pack(side='left')

        # Dosya yolu seçimi
        tk.Label(left_panel, text=f"\n{self.lm.tr('lbl_save_location', 'Kayıt Konumu:')}", font=('Segoe UI', 12, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(10, 5))

        path_frame = tk.Frame(left_panel, bg='white')
        path_frame.pack(fill='x', pady=(0, 10))

        self.file_path_var = tk.StringVar()
        self.file_path_entry = tk.Entry(path_frame, textvariable=self.file_path_var,
                                       font=('Segoe UI', 10), width=30)
        self.file_path_entry.pack(side='left', fill='x', expand=True)

        ttk.Button(path_frame, text=self.lm.tr("btn_browse", "Gözat"), style='Primary.TButton', command=self.browse_file_path).pack(side='right', padx=(5, 0))

        # Rapor oluştur butonu
        ttk.Button(left_panel, text=f" {self.lm.tr('btn_create_report', 'Rapor Oluştur')}", style='Primary.TButton',
                   command=self.create_report).pack(pady=20)

        right_panel = tk.Frame(self.create_frame, bg='white', relief='raised', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0), pady=10, ipadx=10, ipady=10)
        tk.Label(right_panel, text=self.lm.tr("lbl_report_preview", "Rapor Önizlemesi"), font=('Segoe UI', 12, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 10))
        preview_open_frame = tk.Frame(right_panel, bg='white')
        preview_open_frame.pack(fill='x')
        ttk.Button(preview_open_frame, text=f" {self.lm.tr('btn_preview_outputs', 'Önizleme ve Çıkışlar')} ", style='Primary.TButton',
                   command=self.open_preview_window).pack(side='left')

    def setup_templates_tab(self) -> None:
        """Rapor şablonları sekmesini oluştur"""
        # Şablon listesi
        templates_frame = tk.Frame(self.templates_frame, bg='white', relief='raised', bd=1)
        templates_frame.pack(fill='both', expand=True, padx=10, pady=10, ipadx=10, ipady=10)

        tk.Label(templates_frame, text=self.lm.tr("title_report_templates", "Rapor Şablonları"), font=('Segoe UI', 14, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 15))

        # Şablon listesi
        self.templates_tree = ttk.Treeview(templates_frame, columns=('name', 'description', 'formats'),
                                          show='headings', height=10)

        self.templates_tree.heading('name', text=self.lm.tr("col_template_name", "Şablon Adı"))
        self.templates_tree.heading('description', text=self.lm.tr("col_description", "Açıklama"))
        self.templates_tree.heading('formats', text=self.lm.tr("col_supported_formats", "Desteklenen Formatlar"))

        self.templates_tree.column('name', width=150)
        self.templates_tree.column('description', width=300)
        self.templates_tree.column('formats', width=150)

        self.templates_tree.pack(fill='both', expand=True, pady=(0, 10))

        # Scrollbar
        templates_scrollbar = ttk.Scrollbar(templates_frame, orient="vertical", command=self.templates_tree.yview)
        self.templates_tree.configure(yscrollcommand=templates_scrollbar.set)
        templates_scrollbar.pack(side='right', fill='y')

        # Şablon yönetimi butonları
        button_frame = tk.Frame(templates_frame, bg='white')
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text=f" {self.lm.tr('btn_edit_template', 'Şablon Düzenle')}", style='Primary.TButton', command=self.edit_template).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text=f" {self.lm.tr('btn_new_template', 'Yeni Şablon')}", style='Primary.TButton', command=self.create_template).pack(side='left', padx=5)
        ttk.Button(button_frame, text=f" {self.lm.tr('btn_delete_template', 'Şablon Sil')}", style='Accent.TButton', command=self.delete_template).pack(side='left', padx=5)

    def setup_history_tab(self) -> None:
        """Rapor geçmişi sekmesini oluştur"""
        # Geçmiş listesi
        history_frame = tk.Frame(self.history_frame, bg='white', relief='raised', bd=1)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10, ipadx=10, ipady=10)

        tk.Label(history_frame, text=self.lm.tr("title_report_history", "Rapor Geçmişi"), font=('Segoe UI', 14, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 15))

        # Geçmiş listesi
        self.history_tree = ttk.Treeview(history_frame, columns=('date', 'type', 'format', 'file'),
                                        show='headings', height=15)

        self.history_tree.heading('date', text=self.lm.tr("col_date", "Tarih"))
        self.history_tree.heading('type', text=self.lm.tr("col_report_type", "Rapor Türü"))
        self.history_tree.heading('format', text=self.lm.tr("col_format", "Format"))
        self.history_tree.heading('file', text=self.lm.tr("col_filename", "Dosya Adı"))

        self.history_tree.column('date', width=120)
        self.history_tree.column('type', width=150)
        self.history_tree.column('format', width=80)
        self.history_tree.column('file', width=200)

        self.history_tree.pack(fill='both', expand=True, pady=(0, 10))

        # Scrollbar
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        history_scrollbar.pack(side='right', fill='y')

        # Geçmiş yönetimi butonları
        button_frame = tk.Frame(history_frame, bg='white')
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text=f" {self.lm.tr('btn_open_folder', 'Klasörü Aç')}", style='Primary.TButton', command=self.open_folder).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text=f" {self.lm.tr('btn_delete_selected', 'Seçiliyi Sil')}", style='Accent.TButton', command=self.delete_history).pack(side='left', padx=5)
        ttk.Button(button_frame, text=f" {self.lm.tr('btn_refresh', 'Yenile')}", command=self.refresh_history).pack(side='right')

    def _save_preview_text(self) -> None:
        try:
            content = self.preview_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_preview_empty", "Önizleme içeriği boş"))
                return
            from datetime import datetime
            fp = filedialog.asksaveasfilename(
                defaultextension='.txt',
                filetypes=[(self.lm.tr("file_text", "Metin"),'*.txt')],
                initialfile=f"sdg_report_{datetime.now().strftime('%Y')}.txt",
                title=self.lm.tr('save_report', "Raporu Kaydet")
            )
            if not fp:
                return
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            self._last_saved_preview_path = fp
            messagebox.showinfo(self.lm.tr("title_info", "Bilgi"), f"{self.lm.tr('msg_report_saved', 'Rapor metni kaydedildi')}: {fp}")
        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_save', 'Kaydetme hatası')}: {e}")

    def _print_preview_text(self) -> None:
        try:
            import os
            import tempfile
            content = self.preview_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_preview_empty", "Önizleme içeriği boş"))
                return
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"sdg_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            try:
                os.startfile(tmp_path, 'print')
                messagebox.showinfo(self.lm.tr("title_info", "Bilgi"), self.lm.tr("msg_print_started", "Yazdırma başlatıldı"))
            except Exception as e:
                messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_print', 'Yazdırma hatası')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_print_prep', 'Yazdırmaya hazırlık hatası')}: {e}")

    def _copy_preview_to_clipboard(self) -> None:
        try:
            content = self.preview_text.get('1.0', tk.END)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)
            messagebox.showinfo(self.lm.tr("title_info", "Bilgi"), self.lm.tr("msg_preview_copied", "Önizleme metni panoya kopyalandı"))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _share_dialog(self) -> None:
        try:
            dialog = tk.Toplevel(self.parent)
            dialog.title(self.lm.tr("title_share", "Paylaş"))
            dialog.geometry('360x180')
            dialog.grab_set()
            tk.Label(dialog, text=self.lm.tr("lbl_share_options", "Paylaşım Seçenekleri"), font=('Segoe UI', 12, 'bold')).pack(pady=10)
            btns = tk.Frame(dialog)
            btns.pack(pady=10)
            def copy_path():
                path = getattr(self, '_last_saved_preview_path', None)
                if path and os.path.exists(path):
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(path)
                    messagebox.showinfo(self.lm.tr("title_info", "Bilgi"), self.lm.tr("msg_path_copied", "Dosya yolu panoya kopyalandı"))
                else:
                    messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_file_not_found", "Paylaşılacak dosya bulunamadı"))
            def open_folder():
                path = getattr(self, '_last_saved_preview_path', None)
                if path and os.path.exists(path):
                    os.startfile(os.path.dirname(path))
                else:
                    messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_folder_open_error", "Klasör açılamadı"))
            def copy_text():
                content = self.preview_text.get('1.0', tk.END)
                self.parent.clipboard_clear()
                self.parent.clipboard_append(content)
                messagebox.showinfo(self.lm.tr("title_info", "Bilgi"), self.lm.tr("msg_preview_copied", "Önizleme metni panoya kopyalandı"))
            tk.Button(btns, text=self.lm.tr("btn_copy_path", "Dosya Yolunu Kopyala"), command=copy_path, bg='#0ea5e9', fg='white').pack(side='left', padx=6)
            tk.Button(btns, text=self.lm.tr("btn_open_folder", "Klasörü Aç"), command=open_folder, bg='#2563eb', fg='white').pack(side='left', padx=6)
            tk.Button(btns, text=self.lm.tr("btn_copy_preview", "Önizleme Metnini Kopyala"), command=copy_text, bg='#6b7280', fg='white').pack(side='left', padx=6)
            tk.Button(dialog, text=self.lm.tr("btn_close", "Kapat"), command=dialog.destroy).pack(pady=8)
        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_share', 'Paylaşım hatası')}: {e}")

    def _open_last_report(self) -> None:
        try:
            path = getattr(self, '_last_saved_preview_path', None)
            if path and os.path.exists(path):
                os.startfile(path)
                return
            messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_no_report_to_open", "Açılacak rapor bulunamadı"))
        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_open', 'Açma hatası')}: {e}")

    def open_preview_window(self) -> None:
        try:
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr("title_preview_window", "SDG Önizleme ve Çıkışlar"))
            win.geometry('900x600')
            top = tk.Frame(win, bg='white')
            top.pack(fill='x', padx=10, pady=6)
            tk.Button(top, text=self.lm.tr("btn_back", "Geri"), command=win.destroy, bg='#6b7280', fg='white').pack(side='left')
            self.preview_text = tk.Text(win, height=20, width=60, font=('Courier', 9), bg='#f8f9fa', wrap='word')
            self.preview_text.pack(fill='both', expand=True, pady=(0, 10))
            preview_scrollbar = ttk.Scrollbar(win, orient="vertical", command=self.preview_text.yview)
            self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
            preview_scrollbar.pack(side='right', fill='y')
            tools = tk.Frame(win, bg='white')
            tools.pack(fill='x', pady=6)
            tk.Button(tools, text=f" {self.lm.tr('btn_save_txt', 'Kaydet (.txt)')} ", command=self._save_preview_text, font=('Segoe UI', 10), bg='#0ea5e9', fg='white', relief='flat').pack(side='left', padx=4)
            tk.Button(tools, text=f" {self.lm.tr('btn_open', 'Aç')} ", command=self._open_last_report, font=('Segoe UI', 10), bg='#10b981', fg='white', relief='flat').pack(side='left', padx=4)
            tk.Button(tools, text=f" {self.lm.tr('btn_print', 'Yazdır')} ", command=self._print_preview_text, font=('Segoe UI', 10), bg='#7B1FA2', fg='white', relief='flat').pack(side='left', padx=4)
            tk.Button(tools, text=f" {self.lm.tr('btn_copy_clipboard', 'Panoya Kopyala')} ", command=self._copy_preview_to_clipboard, font=('Segoe UI', 10), bg='#6b7280', fg='white', relief='flat').pack(side='left', padx=4)
            tk.Button(tools, text=f" {self.lm.tr('btn_share', 'Paylaş')} ", command=self._share_dialog, font=('Segoe UI', 10), bg='#e67e22', fg='white', relief='flat').pack(side='left', padx=4)
        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_preview_window', 'Önizleme penceresi hatası')}: {e}")

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            # Şablonları yükle
            self.load_templates()

            # Geçmişi yükle
            self.load_history()

        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_data_load', 'Veriler yüklenirken hata oluştu')}: {str(e)}")

    def load_templates(self) -> None:
        """Şablonları yükle"""
        try:
            templates = self.reporting.get_report_templates()

            # Mevcut verileri temizle
            for item in self.templates_tree.get_children():
                self.templates_tree.delete(item)

            # Şablonları ekle
            for template in templates:
                formats_str = ', '.join(template['formats'])
                self.templates_tree.insert('', 'end', values=(
                    template['name'],
                    template['description'],
                    formats_str
                ))

        except Exception as e:
            logging.error(f"Şablonlar yüklenirken hata: {e}")

    def load_history(self) -> None:
        """Geçmişi yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            # Veritabanından geçmiş verilerini getir
            self.history_item_to_id = {}
            rows = self.reporting.get_report_history(self.company_id)
            for h in rows:
                fname = os.path.basename(h['output_path']) if h['output_path'] else ''
                item_id = self.history_tree.insert('', 'end', values=(h['created_at'], h['template_key'], h['output_format'], fname))
                self.history_item_to_id[item_id] = h['id']

        except Exception as e:
            logging.error(f"Geçmiş yüklenirken hata: {e}")

    def browse_file_path(self) -> None:
        """Dosya yolu seç"""
        file_type = self.format_var.get()
        if file_type == 'PDF':
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[(self.lm.tr("pdf_files", "PDF Dosyaları"), "*.pdf"), (self.lm.tr("filetype_all", "Tüm dosyalar"), "*.*")],
                title=self.lm.tr("title_save_report", "Raporu Kaydet")
            )
        else:  # DOCX
            file_path = filedialog.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[(self.lm.tr("word_files", "Word Dosyaları"), "*.docx"), (self.lm.tr("filetype_all", "Tüm dosyalar"), "*.*")],
                title=self.lm.tr("title_save_report", "Raporu Kaydet")
            )

        if file_path:
            self.file_path_var.set(file_path)

    def generate_preview(self) -> None:
        """Önizleme oluştur"""
        try:
            # Verileri al
            data = self.reporting.get_company_data(self.company_id)
            if 'error' in data:
                self.preview_text.delete('1.0', tk.END)
                self.preview_text.insert('1.0', f"{self.lm.tr('title_error', 'Hata')}: {data['error']}")
                return

            # Önizleme metnini oluştur
            preview_text = f"""
{self.lm.tr("sdg_progress_report_title", "SDG İLERLEME RAPORU")}
==================

{self.lm.tr("preview_header_company", "Şirket Bilgileri:")}
- {self.lm.tr("lbl_company_name", "Şirket Adı")}: {data['company']['name']}
- {self.lm.tr("lbl_description", "Açıklama")}: {data['company']['description'] or self.lm.tr("lbl_not_specified", "Belirtilmemiş")}
- {self.lm.tr("lbl_report_date", "Rapor Tarihi")}: {data['report_date']} {data['report_time']}

{self.lm.tr("preview_header_goals", "Seçilen SDG Hedefleri:")}
"""

            if data['selected_goals']:
                for goal in data['selected_goals']:
                    preview_text += f"- SDG {goal[0]}: {goal[1]}\n"
            else:
                preview_text += f"- {self.lm.tr('msg_no_goals_selected', 'Seçilen SDG hedefi bulunmamaktadır.')}\n"

            preview_text += f"\n{self.lm.tr('preview_header_progress', 'İlerleme Durumu:')}\n"
            if data['progress_data']:
                for progress in data['progress_data']:
                    preview_text += f"- SDG {progress[0]}: %{progress[4]} {self.lm.tr('lbl_completed', 'tamamlandı')} ({progress[2]}/{progress[3]} {self.lm.tr('lbl_questions', 'soru')})\n"
            else:
                preview_text += f"- {self.lm.tr('msg_no_progress_data', 'İlerleme verisi bulunmamaktadır.')}\n"

            preview_text += f"\n{self.lm.tr('preview_header_gri', 'GRI Eşleştirmeleri:')}\n"
            if data['gri_mappings']:
                for gri in data['gri_mappings']:
                    preview_text += f"- SDG {gri[0]}: {gri[1]} GRI standardı\n"
            else:
                preview_text += "- GRI eşleştirme verisi bulunmamaktadır.\n"

            # Özet
            total_goals = len(data['selected_goals'])
            total_questions = sum(p[3] for p in data['progress_data']) if data['progress_data'] else 0
            answered_questions = sum(p[2] for p in data['progress_data']) if data['progress_data'] else 0
            overall_completion = round((answered_questions / total_questions * 100) if total_questions > 0 else 0, 2)

            preview_text += f"""
Özet:
- Toplam Seçilen SDG Hedefi: {total_goals}
- Toplam Soru Sayısı: {total_questions}
- Cevaplanan Soru Sayısı: {answered_questions}
- Genel Tamamlanma Oranı: %{overall_completion}
"""

            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', preview_text)

        except Exception as e:
            messagebox.showerror("Hata", f"Önizleme oluşturulurken hata: {str(e)}")

    def create_report(self) -> None:
        """Rapor oluştur"""
        try:
            file_path = self.file_path_var.get().strip()
            if not file_path:
                messagebox.showwarning("Uyarı", "Lütfen dosya yolu seçin")
                return

            report_type = self.report_type_var.get()
            format_type = self.format_var.get()

            # Rapor oluştur
            if format_type == 'PDF':
                success = self.reporting.create_pdf_report(self.company_id, file_path)
            else:  # DOCX
                success = self.reporting.create_docx_report(self.company_id, file_path)

            if success:
                # Geçmişe kaydet
                self.reporting.add_report_history(self.company_id, report_type, format_type, file_path, meta={'source': 'gui'})
                messagebox.showinfo("Başarılı", f"{format_type} raporu başarıyla oluşturuldu:\n{file_path}")
                self.refresh_history()
            else:
                messagebox.showerror("Hata", "Rapor oluşturulamadı")

        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulurken hata: {str(e)}")

    def edit_template(self) -> None:
        """Şablon düzenle"""
        try:
            selection = self.templates_tree.selection()
            if not selection:
                messagebox.showwarning("Uyarı", "Lütfen bir şablon seçin")
                return
            item_id = selection[0]
            values = self.templates_tree.item(item_id, 'values')
            name = values[0] if values else ''
            description = values[1] if values and len(values) > 1 else ''
            formats_str = values[2] if values and len(values) > 2 else ''
            from tkinter import simpledialog
            new_name = simpledialog.askstring("Şablon Adı", "Yeni adı girin", initialvalue=name) or name
            new_desc = simpledialog.askstring("Açıklama", "Açıklamayı girin", initialvalue=description) or description
            fmt_in = simpledialog.askstring("Formatlar", "Virgülle ayırın (PDF,DOCX)", initialvalue=formats_str) or formats_str
            new_formats = [f.strip().upper() for f in fmt_in.split(',') if f.strip()]
            # Şablon anahtarını bul
            templates = self.reporting.get_report_templates()
            tkey = None
            for t in templates:
                if t['name'] == name:
                    tkey = t['id']
                    break
            if not tkey:
                messagebox.showerror("Hata", "Şablon anahtarı bulunamadı")
                return
            ok = self.reporting.update_report_template(tkey, name=new_name, description=new_desc, formats=new_formats)
            if ok:
                messagebox.showinfo("Başarılı", "Şablon güncellendi")
                self.load_templates()
            else:
                messagebox.showerror("Hata", "Şablon güncellenemedi")
        except Exception as e:
            messagebox.showerror("Hata", f"Şablon düzenlenirken hata: {str(e)}")

    def create_template(self) -> None:
        """Yeni şablon oluştur"""
        try:
            from tkinter import simpledialog
            tkey = simpledialog.askstring("Şablon Anahtarı", "Benzersiz anahtar (ör. custom1)")
            if not tkey:
                return
            name = simpledialog.askstring("Şablon Adı", "Adı girin")
            if not name:
                return
            desc = simpledialog.askstring("Açıklama", "Açıklama girin") or ''
            fmt_in = simpledialog.askstring("Formatlar", "Virgülle ayırın (PDF,DOCX)", initialvalue='PDF,DOCX') or 'PDF'
            formats = [f.strip().upper() for f in fmt_in.split(',') if f.strip()]
            rid = self.reporting.add_report_template(tkey, name, desc, formats)
            if rid:
                messagebox.showinfo("Başarılı", "Şablon eklendi")
                self.load_templates()
            else:
                messagebox.showerror("Hata", "Şablon eklenemedi; anahtar benzersiz olmalı")
        except Exception as e:
            messagebox.showerror("Hata", f"Şablon eklenirken hata: {str(e)}")

    def delete_template(self) -> None:
        """Şablon sil"""
        try:
            selection = self.templates_tree.selection()
            if not selection:
                messagebox.showwarning("Uyarı", "Lütfen bir şablon seçin")
                return
            item_id = selection[0]
            values = self.templates_tree.item(item_id, 'values')
            name = values[0] if values else ''
            # Şablon anahtarını bul
            templates = self.reporting.get_report_templates()
            tkey = None
            for t in templates:
                if t['name'] == name:
                    tkey = t['id']
                    break
            if not tkey:
                messagebox.showerror("Hata", "Şablon anahtarı bulunamadı")
                return
            if messagebox.askyesno("Onay", f"'{name}' şablonu silinsin mi?"):
                ok = self.reporting.delete_report_template(tkey)
                if ok:
                    messagebox.showinfo("Başarılı", "Şablon silindi")
                    self.load_templates()
                else:
                    messagebox.showerror("Hata", "Şablon silinemedi")
        except Exception as e:
            messagebox.showerror("Hata", f"Şablon silinirken hata: {str(e)}")

    def open_folder(self) -> None:
        """Klasörü aç"""
        try:
            import platform
            import subprocess

            if platform.system() == "Windows":
                subprocess.run(["explorer", "."])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "."])
            else:  # Linux
                subprocess.run(["xdg-open", "."])

        except Exception as e:
            messagebox.showerror("Hata", f"Klasör açılırken hata: {str(e)}")

    def delete_history(self) -> None:
        """Geçmişi sil"""
        try:
            selection = self.history_tree.selection()
            if not selection:
                messagebox.showwarning("Uyarı", "Lütfen bir kayıt seçin")
                return
            item_id = selection[0]
            hid = getattr(self, 'history_item_to_id', {}).get(item_id)
            if not hid:
                messagebox.showerror("Hata", "Kayıt ID bulunamadı")
                return
            if messagebox.askyesno("Onay", "Seçili geçmiş kaydı silinsin mi?"):
                ok = self.reporting.delete_report_history(hid)
                if ok:
                    messagebox.showinfo("Başarılı", "Geçmiş kaydı silindi")
                    self.refresh_history()
                else:
                    messagebox.showerror("Hata", "Geçmiş kaydı silinemedi")
        except Exception as e:
            messagebox.showerror("Hata", f"Geçmiş silinirken hata: {str(e)}")

    def refresh_history(self) -> None:
        """Geçmişi yenile"""
        self.load_history()

if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("SDG Raporlama Sistemi")
    app = SDGReportingGUI(root, 1)
    root.mainloop()
