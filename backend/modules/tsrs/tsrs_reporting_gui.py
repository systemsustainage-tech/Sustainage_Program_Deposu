import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS Raporlama GUI
TSRS raporları oluşturma ve yönetme arayüzü
"""

import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from modules.reporting.universal_exporter import UniversalExporter
from utils.language_manager import LanguageManager

from .tsrs_reporting import TSRSReporting


class TSRSReportingGUI:
    """TSRS Raporlama GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.tsrs_reporting = TSRSReporting()

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """TSRS raporlama arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr('tsrs_report_center_title', "TSRS Raporlama Merkezi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        actions = tk.Frame(title_frame, bg='#2c3e50')
        actions.pack(side='right', padx=10)
        ttk.Button(actions, text=self.lm.tr('report_center', "Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center_tsrs).pack(side='right')

        # Ana içerik - İki panel yan yana
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Sol panel - Rapor Oluşturma
        left_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        self.create_report_creation_panel(left_panel)

        # Sağ panel - Rapor Geçmişi
        right_panel = tk.Frame(content_frame, bg='white', relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True)

        self.create_report_history_panel(right_panel)

    def create_report_creation_panel(self, parent) -> None:
        """Rapor oluşturma panelini oluştur"""
        # Panel başlığı
        header_frame = tk.Frame(parent, bg='#34495e', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        header_label = tk.Label(header_frame, text=self.lm.tr('tsrs_new_report', "Yeni Rapor Oluştur"),
                               font=('Segoe UI', 14, 'bold'), fg='white', bg='#34495e')
        header_label.pack(expand=True)

        # İçerik
        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Raporlama dönemi
        period_frame = tk.Frame(content_frame, bg='white')
        period_frame.pack(fill='x', pady=(0, 15))

        tk.Label(period_frame, text=self.lm.tr('tsrs_reporting_period', "Raporlama Dönemi:"),
                font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')

        period_options = [f"{year}" for year in range(2020, 2030)]
        self.period_var = tk.StringVar(value=str(datetime.now().year))

        period_combo = ttk.Combobox(period_frame, textvariable=self.period_var,
                                   values=period_options, state='readonly', width=20)
        period_combo.pack(anchor='w', pady=(5, 0))

        # Rapor türü seçimi
        type_frame = tk.Frame(content_frame, bg='white')
        type_frame.pack(fill='x', pady=(0, 15))

        tk.Label(type_frame, text=self.lm.tr('tsrs_report_type', "Rapor Türü:"),
                font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')

        self.report_types = {
            'PDF': tk.BooleanVar(value=True),
            'Word': tk.BooleanVar(value=True),
            'Excel': tk.BooleanVar(value=True)
        }

        for report_type, var in self.report_types.items():
            checkbox = tk.Checkbutton(type_frame, text=report_type, variable=var,
                                     font=('Segoe UI', 11), bg='white')
            checkbox.pack(anchor='w', padx=20)

        # Çıktı dizini
        output_frame = tk.Frame(content_frame, bg='white')
        output_frame.pack(fill='x', pady=(0, 15))

        tk.Label(output_frame, text=self.lm.tr('tsrs_output_dir', "Çıktı Dizini:"),
                font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')

        output_path_frame = tk.Frame(output_frame, bg='white')
        output_path_frame.pack(fill='x', pady=(5, 0))

        self.output_path_var = tk.StringVar(value=os.path.join(os.getcwd(), 'data', 'exports'))
        output_entry = tk.Entry(output_path_frame, textvariable=self.output_path_var,
                               font=('Segoe UI', 10), width=40)
        output_entry.pack(side='left', fill='x', expand=True)

        browse_btn = tk.Button(output_path_frame, text=self.lm.tr('tsrs_browse', "Gözat"),
                              font=('Segoe UI', 10), bg='#3498db', fg='white',
                              relief='flat', bd=0, cursor='hand2', padx=15,
                              command=self.browse_output_directory)
        browse_btn.pack(side='right', padx=(10, 0))

        # Rapor oluştur butonu
        create_btn = tk.Button(content_frame, text=self.lm.tr('tsrs_create_report', "Rapor Oluştur"),
                              font=('Segoe UI', 12, 'bold'), bg='#27ae60', fg='white',
                              relief='flat', bd=0, cursor='hand2', padx=30, pady=10,
                              command=self.create_report)
        create_btn.pack(pady=20)
        preview_open_frame = tk.Frame(content_frame, bg='white')
        preview_open_frame.pack(fill='x')
        tk.Button(preview_open_frame, text=self.lm.tr('tsrs_preview_and_exports', 'Önizleme ve Çıkışlar'), command=self.open_preview_window,
                  font=('Segoe UI', 10), bg='#0ea5e9', fg='white', relief='flat').pack(side='left')

        # İlerleme çubuğu
        self.progress_var = tk.StringVar(value="Hazır")
        progress_label = tk.Label(content_frame, textvariable=self.progress_var,
                                 font=('Segoe UI', 10), fg='#7f8c8d', bg='white')
        progress_label.pack()

        self.progress_bar = ttk.Progressbar(content_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=(5, 0))

    def create_report_history_panel(self, parent) -> None:
        """Rapor geçmişi panelini oluştur"""
        # Panel başlığı
        header_frame = tk.Frame(parent, bg='#34495e', height=50)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        header_label = tk.Label(header_frame, text=self.lm.tr('tsrs_report_history', "Rapor Geçmişi"),
                               font=('Segoe UI', 14, 'bold'), fg='white', bg='#34495e')
        header_label.pack(expand=True)

        # İçerik
        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Rapor listesi
        columns = (self.lm.tr('period', 'Dönem'), self.lm.tr('type', 'Tür'), self.lm.tr('created_at', 'Oluşturma Tarihi'), self.lm.tr('status', 'Durum'))
        self.report_tree = ttk.Treeview(content_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=120)

        # Scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=scrollbar.set)

        self.report_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Çift tıklama olayı
        self.report_tree.bind('<Double-1>', self.open_report)

        tools = tk.Frame(parent, bg='white')
        tools.pack(fill='x', padx=20, pady=(10, 0))
        tk.Label(tools, text=self.lm.tr('tsrs_search', "Ara:"), bg='white').pack(side='left')
        self.history_search_var = tk.StringVar()
        ttk.Entry(tools, textvariable=self.history_search_var, width=24).pack(side='left', padx=8)
        try:
            self.history_search_var.trace_add('write', lambda *args: self.filter_history())
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        ttk.Button(tools, text=self.lm.tr('file_csv_label', "CSV"), style='Primary.TButton', command=self.export_history_csv).pack(side='right', padx=6)
        ttk.Button(tools, text=self.lm.tr('file_excel_label', "Excel"), style='Primary.TButton', command=self.export_history_excel).pack(side='right', padx=6)
        ttk.Button(tools, text=self.lm.tr('tsrs_copy_path', "Yol Kopyala"), style='Primary.TButton', command=self.copy_selected_report_path).pack(side='right', padx=6)
        ttk.Button(tools, text=self.lm.tr('tsrs_open_folder', "Klasörü Aç"), style='Primary.TButton', command=self.open_report_folder).pack(side='right', padx=6)

        # Sağ tık menüsü
        self.create_context_menu()

    def create_context_menu(self) -> None:
        """Bağlam menüsü oluştur"""
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label=self.lm.tr("ctx_open_report", "Raporu Aç"), command=self.open_report)
        self.context_menu.add_command(label=self.lm.tr("ctx_open_folder", "Klasörü Aç"), command=self.open_report_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=self.lm.tr("ctx_delete_report", "Raporu Sil"), command=self.delete_report)

        # Sağ tık olayı
        self.report_tree.bind('<Button-3>', self.show_context_menu)

    def show_context_menu(self, event) -> None:
        """Bağlam menüsünü göster"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def browse_output_directory(self) -> None:
        """Çıktı dizini seç"""
        directory = filedialog.askdirectory(
            title=self.lm.tr('tsrs_select_output_dir', "Çıktı Dizini Seçin"),
            initialdir=self.output_path_var.get()
        )
        if directory:
            self.output_path_var.set(directory)

    def open_report_center_tsrs(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('tsrs')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for tsrs: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"Rapor Merkezi açılamadı:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def _collect_history_rows(self) -> list[tuple]:
        rows = []
        for iid in self.report_tree.get_children():
            vals = self.report_tree.item(iid).get('values', [])
            rows.append(tuple(vals))
        return rows

    def filter_history(self) -> None:
        try:
            term = (self.history_search_var.get() or '').strip().lower()
            items = self._collect_history_rows()
            for iid in self.report_tree.get_children():
                self.report_tree.delete(iid)
            for r in items:
                s = ' '.join([str(x).lower() for x in r])
                if term and term not in s:
                    continue
                self.report_tree.insert('', 'end', values=r)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def export_history_csv(self) -> None:
        try:
            default_name = f"tsrs_history_{self.company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            path = filedialog.asksaveasfilename(
                title=self.lm.tr('export_csv', 'CSV Dışa Aktar'),
                defaultextension='.csv', 
                filetypes=[(self.lm.tr('file_csv', 'CSV Dosyaları'),'*.csv')], 
                initialfile=default_name
            )
            if not path:
                return
            cols = (self.lm.tr('period', 'Dönem'), self.lm.tr('type', 'Tür'), self.lm.tr('created_at', 'Oluşturma Tarihi'), self.lm.tr('status', 'Durum'))
            data_dicts = []
            for r in self._collect_history_rows():
                d = {}
                for i, c in enumerate(cols):
                    d[c] = r[i] if i < len(r) else ''
                data_dicts.append(d)
            try:
                ue = UniversalExporter(export_dir=os.path.dirname(path) or 'exports')
                ue.export_to_csv(data_dicts, os.path.basename(path))
            except Exception:
                import pandas as pd
                pd.DataFrame(data_dicts).to_csv(path, index=False, encoding='utf-8-sig')
            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), f'Dışa aktarıldı:\n{path}')
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Dışa aktarma hatası: {e}')

    def export_history_excel(self) -> None:
        try:
            default_name = f"tsrs_history_{self.company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            path = filedialog.asksaveasfilename(
                title=self.lm.tr('export_excel', 'Excel Dışa Aktar'),
                defaultextension='.xlsx', 
                filetypes=[(self.lm.tr('file_excel', 'Excel Dosyaları'),'*.xlsx')], 
                initialfile=default_name
            )
            if not path:
                return
            cols = (self.lm.tr('period', 'Dönem'), self.lm.tr('type', 'Tür'), self.lm.tr('created_at', 'Oluşturma Tarihi'), self.lm.tr('status', 'Durum'))
            data_dicts = []
            for r in self._collect_history_rows():
                d = {}
                for i, c in enumerate(cols):
                    d[c] = r[i] if i < len(r) else ''
                data_dicts.append(d)
            try:
                ue = UniversalExporter(export_dir=os.path.dirname(path) or 'exports')
                ue.export_to_excel(data_dicts, os.path.basename(path))
            except Exception:
                import pandas as pd
                with pd.ExcelWriter(path, engine='openpyxl') as writer:
                    pd.DataFrame(data_dicts).to_excel(writer, sheet_name='Veri', index=False)
            messagebox.showinfo(self.lm.tr('success', 'Başarılı'), f'Dışa aktarıldı:\n{path}')
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Dışa aktarma hatası: {e}')

    def copy_selected_report_path(self) -> None:
        try:
            selection = self.report_tree.selection()
            if not selection:
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('msg_select_record', 'Lütfen bir kayıt seçin'))
                return
            item = self.report_tree.item(selection[0])
            period = item['values'][0]
            file_type = item['values'][1]
            output_dir = self.output_path_var.get()
            files = os.listdir(output_dir)
            matching_files = [f for f in files if f.startswith(f'TSRS_Raporu_{period}_') and f.endswith(f'.{file_type.lower()}')]
            if matching_files:
                fp = os.path.join(output_dir, matching_files[0])
                try:
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(fp)
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('msg_path_copied', 'Dosya yolu panoya kopyalandı'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Yol kopyalama hatası: {e}')

    def create_report(self) -> None:
        """Rapor oluştur"""
        try:
            # Parametreleri al
            reporting_period = self.period_var.get()
            if not self._validate_year(reporting_period):
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('msg_invalid_year', "Geçersiz yıl"))
                return
            output_dir = self.output_path_var.get()

            # En az bir rapor türü seçilmiş olmalı
            selected_types = [t for t, var in self.report_types.items() if var.get()]
            if not selected_types:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('msg_select_type', "En az bir rapor türü seçmelisiniz!"))
                return

            # Çıktı dizinini oluştur
            os.makedirs(output_dir, exist_ok=True)

            # İlerleme göster
            self.progress_var.set(self.lm.tr('tsrs_report_creating', "Rapor oluşturuluyor..."))
            self.progress_bar.start()
            self.parent.update()

            # Rapor oluştur
            results = {}

            if 'PDF' in selected_types:
                pdf_path = os.path.join(output_dir, f'TSRS_Raporu_{reporting_period}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
                results['pdf'] = self.tsrs_reporting.create_tsrs_pdf_report(
                    self.company_id, reporting_period, pdf_path)

            if 'Word' in selected_types:
                docx_path = os.path.join(output_dir, f'TSRS_Raporu_{reporting_period}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx')
                results['docx'] = self.tsrs_reporting.create_tsrs_docx_report(
                    self.company_id, reporting_period, docx_path)

            if 'Excel' in selected_types:
                excel_path = os.path.join(output_dir, f'TSRS_Raporu_{reporting_period}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
                results['excel'] = self.tsrs_reporting.create_tsrs_excel_report(
                    self.company_id, reporting_period, excel_path)

            # İlerleme durdur
            self.progress_bar.stop()

            # Sonuçları göster
            success_count = sum(results.values())
            total_count = len(results)

            if success_count == total_count:
                self.progress_var.set(self.lm.tr('tsrs_report_success_status', f"Başarılı! {success_count}/{total_count} rapor oluşturuldu").format(success_count=success_count, total_count=total_count))
                messagebox.showinfo(self.lm.tr('success', "Başarılı"),
                    self.lm.tr('tsrs_report_success_msg', f"TSRS raporları başarıyla oluşturuldu!\n\nOluşturulan raporlar: {success_count}/{total_count}\nÇıktı dizini: {output_dir}").format(success_count=success_count, total_count=total_count, output_dir=output_dir))
            else:
                self.progress_var.set(self.lm.tr('tsrs_report_partial_status', f"Kısmen başarılı: {success_count}/{total_count}").format(success_count=success_count, total_count=total_count))
                failed_types = [t for t, success in results.items() if not success]
                messagebox.showwarning(self.lm.tr('tsrs_report_partial_title', "Kısmen Başarılı"),
                    self.lm.tr('tsrs_report_partial_msg', f"Bazı raporlar oluşturulamadı!\n\nBaşarılı: {success_count}/{total_count}\nBaşarısız: {', '.join(failed_types)}").format(success_count=success_count, total_count=total_count, failed_types=', '.join(failed_types)))

            # Rapor listesini yenile
            self.load_report_history()

        except Exception as e:
            self.progress_bar.stop()
            self.progress_var.set(self.lm.tr('tsrs_report_error_status', "Hata oluştu"))
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('tsrs_report_error', f"Rapor oluşturulurken hata: {e}").format(e=e))

    def load_report_history(self) -> None:
        """Rapor geçmişini yükle"""
        try:
            # Mevcut raporları temizle
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)

            # Çıktı dizinindeki dosyaları tara
            output_dir = self.output_path_var.get()
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                tsrs_files = [f for f in files if f.startswith('TSRS_Raporu_')]

                for file in tsrs_files:
                    # Dosya bilgilerini çıkar
                    parts = file.replace('.pdf', '').replace('.docx', '').replace('.xlsx', '').split('_')
                    if len(parts) >= 4:
                        period = parts[2]
                        file_type = file.split('.')[-1].upper()
                        file_path = os.path.join(output_dir, file)

                        # Dosya tarihini al
                        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        file_date = file_time.strftime('%d.%m.%Y %H:%M')

                        # Durum
                        status = "Mevcut"

                        # Ağaca ekle
                        self.report_tree.insert('', 'end', values=(
                            period, file_type, file_date, status
                        ))

        except Exception as e:
            logging.error(f"Rapor geçmişi yüklenirken hata: {e}")

    def _validate_year(self, y: str):
        try:
            y = (y or "").strip()
            if not (y.isdigit() and len(y) == 4):
                return None
            val = int(y)
            if 1990 <= val <= 2100:
                return val
            return None
        except Exception:
            return None

    def open_report(self, event=None) -> None:
        """Raporu aç"""
        try:
            selection = self.report_tree.selection()
            if not selection:
                return

            item = self.report_tree.item(selection[0])
            period = item['values'][0]
            file_type = item['values'][1]

            # Dosya yolunu oluştur
            output_dir = self.output_path_var.get()
            f'TSRS_Raporu_{period}_*.{file_type.lower()}'

            # Dosyayı bul
            files = os.listdir(output_dir)
            matching_files = [f for f in files if f.startswith(f'TSRS_Raporu_{period}_') and f.endswith(f'.{file_type.lower()}')]

            if matching_files:
                file_path = os.path.join(output_dir, matching_files[0])
                os.startfile(file_path)
            else:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('msg_file_not_found', "Dosya bulunamadı!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"Dosya açılırken hata: {e}")

    def open_report_folder(self) -> None:
        """Rapor klasörünü aç"""
        try:
            output_dir = self.output_path_var.get()
            os.startfile(output_dir)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"Klasör açılırken hata: {e}")

    def delete_report(self) -> None:
        """Raporu sil"""
        try:
            selection = self.report_tree.selection()
            if not selection:
                return

            # Onay al
            result = messagebox.askyesno(self.lm.tr('confirm', "Onay"), self.lm.tr('msg_confirm_delete', "Seçili raporu silmek istediğinizden emin misiniz?"))
            if not result:
                return

            item = self.report_tree.item(selection[0])
            period = item['values'][0]
            file_type = item['values'][1]

            # Dosya yolunu oluştur
            output_dir = self.output_path_var.get()
            files = os.listdir(output_dir)
            matching_files = [f for f in files if f.startswith(f'TSRS_Raporu_{period}_') and f.endswith(f'.{file_type.lower()}')]

            if matching_files:
                file_path = os.path.join(output_dir, matching_files[0])
                os.remove(file_path)
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('msg_report_deleted', "Rapor başarıyla silindi!"))
                self.load_report_history()
            else:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('msg_file_not_found', "Dosya bulunamadı!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"Dosya silinirken hata: {e}")

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_report_history()

    def _save_preview_text(self) -> None:
        try:
            content = self.preview_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('msg_preview_empty', 'Önizleme içeriği boş'))
                return
            fp = filedialog.asksaveasfilename(
                title=self.lm.tr('save_preview', "Önizlemeyi Kaydet"),
                defaultextension='.txt',
                filetypes=[(self.lm.tr('file_text', 'Metin'),'*.txt')],
                initialfile=f"tsrs_preview_{self.company_id}_{datetime.now().strftime('%Y')}.txt"
            )
            if not fp:
                return
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            self._last_saved_preview_path = fp
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('msg_report_text_saved', 'Önizleme kaydedildi: {path}').format(path=fp))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), self.lm.tr('err_save_failed', 'Kaydetme hatası: {error}').format(error=e))

    def _open_last_report(self) -> None:
        try:
            path = getattr(self, '_last_saved_preview_path', None)
            if path and os.path.exists(path):
                os.startfile(path)
                return
            messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('msg_file_to_open_not_found', 'Açılacak dosya bulunamadı'))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Açma hatası: {e}')

    def _print_preview_text(self) -> None:
        try:
            import os
            import tempfile
            content = self.preview_text.get('1.0', tk.END)
            if not content.strip():
                messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('msg_preview_empty', 'Önizleme içeriği boş'))
                return
            tmp_dir = tempfile.gettempdir()
            tmp_path = os.path.join(tmp_dir, f"tsrs_preview_{self.company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            try:
                os.startfile(tmp_path, 'print')
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('msg_print_started', 'Yazdırma başlatıldı'))
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', 'Hata'), f'Yazdırma hatası: {e}')
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Yazdırmaya hazırlık hatası: {e}')

    def _copy_preview_to_clipboard(self) -> None:
        try:
            content = self.preview_text.get('1.0', tk.END)
            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)
            messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('msg_preview_copied', 'Önizleme metni panoya kopyalandı'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def _share_dialog(self) -> None:
        try:
            dialog = tk.Toplevel(self.parent)
            dialog.title(self.lm.tr('tsrs_share', 'Paylaş'))
            dialog.geometry('360x180')
            dialog.grab_set()
            tk.Label(dialog, text=self.lm.tr('tsrs_share_options', 'Paylaşım Seçenekleri'), font=('Segoe UI', 12, 'bold')).pack(pady=10)
            btns = tk.Frame(dialog)
            btns.pack(pady=10)
            def copy_path():
                path = getattr(self, '_last_saved_preview_path', None)
                if path and os.path.exists(path):
                    self.parent.clipboard_clear()
                    self.parent.clipboard_append(path)
                    messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('msg_path_copied', 'Dosya yolu panoya kopyalandı'))
                else:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('msg_file_to_share_not_found', 'Paylaşılacak dosya bulunamadı'))
            def open_folder():
                path = getattr(self, '_last_saved_preview_path', None)
                if path and os.path.exists(path):
                    os.startfile(os.path.dirname(path))
                else:
                    messagebox.showwarning(self.lm.tr('warning', 'Uyarı'), self.lm.tr('msg_folder_open_error', 'Klasör açılamadı'))
            def copy_text():
                content = self.preview_text.get('1.0', tk.END)
                self.parent.clipboard_clear()
                self.parent.clipboard_append(content)
                messagebox.showinfo(self.lm.tr('info', 'Bilgi'), self.lm.tr('msg_preview_copied', 'Önizleme metni panoya kopyalandı'))
            tk.Button(btns, text=self.lm.tr('tsrs_copy_file_path', 'Dosya Yolunu Kopyala'), command=copy_path, bg='#0ea5e9', fg='white').pack(side='left', padx=6)
            tk.Button(btns, text=self.lm.tr('tsrs_open_folder', 'Klasörü Aç'), command=open_folder, bg='#2563eb', fg='white').pack(side='left', padx=6)
            tk.Button(btns, text=self.lm.tr('tsrs_copy_preview_text', 'Önizleme Metnini Kopyala'), command=copy_text, bg='#6b7280', fg='white').pack(side='left', padx=6)
            tk.Button(dialog, text=self.lm.tr('btn_close', 'Kapat'), command=dialog.destroy).pack(pady=8)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Paylaşım hatası: {e}')

    def open_preview_window(self) -> None:
        try:
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr('tsrs_preview_title', 'TSRS Önizleme ve Çıkışlar'))
            win.geometry('900x600')
            top = tk.Frame(win, bg='white')
            top.pack(fill='x', padx=10, pady=6)
            tk.Button(top, text=self.lm.tr('btn_back', 'Geri'), command=win.destroy, bg='#6b7280', fg='white').pack(side='left')
            self.preview_text = tk.Text(win, height=20, wrap='word')
            self.preview_text.pack(fill='both', expand=True, padx=10, pady=10)
            tools = tk.Frame(win, bg='white')
            tools.pack(fill='x', padx=10, pady=(0,10))
            tk.Button(tools, text=self.lm.tr('tsrs_save_txt', 'Kaydet (.txt)'), command=self._save_preview_text, bg='#0ea5e9', fg='white').pack(side='left', padx=4)
            tk.Button(tools, text=self.lm.tr('open', 'Aç'), command=self._open_last_report, bg='#10b981', fg='white').pack(side='left', padx=4)
            tk.Button(tools, text=self.lm.tr('tsrs_print', 'Yazdır'), command=self._print_preview_text, bg='#7B1FA2', fg='white').pack(side='left', padx=4)
            tk.Button(tools, text=self.lm.tr('tsrs_copy_clipboard', 'Panoya Kopyala'), command=self._copy_preview_to_clipboard, bg='#6b7280', fg='white').pack(side='left', padx=4)
            tk.Button(tools, text=self.lm.tr('tsrs_share', 'Paylaş'), command=self._share_dialog, bg='#e67e22', fg='white').pack(side='left', padx=4)
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', 'Hata'), f'Önizleme penceresi hatası: {e}')
