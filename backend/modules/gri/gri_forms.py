import json
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager
from modules.standards.gri_standards import GRIStandardsManager

from .gri_sector_workflows import GRISectorWorkflows
from config.database import DB_PATH


class GRI1FoundationForm(tk.Toplevel):
    def __init__(self, parent, company_id: int, db_path: str = None) -> None:
        super().__init__(parent)
        self.lm = LanguageManager()
        self.title(self.lm.tr('gri_1_foundation_title', "GRI 1: Foundation 2021"))
        self.geometry("600x520")
        self.configure(bg='white')
        self.company_id = company_id
        self.manager = GRIStandardsManager(db_path or DB_PATH)

        tk.Label(self, text=self.lm.tr('gri_1_foundation_header', "GRI 1: Temel Prensipler ve Raporlama Bilgileri"),
                 font=('Segoe UI', 14, 'bold'), bg='white', fg='#2c3e50').pack(pady=(12, 8))

        form = tk.Frame(self, bg='white')
        form.pack(fill='both', expand=True, padx=16, pady=8)

        # Raporlama dönemi
        tk.Label(form, text=self.lm.tr('reporting_period_label', "Raporlama Dönemi (örn. 2024-01-2024-12)"), bg='white').grid(row=0, column=0, sticky='w')
        self.period_var = tk.StringVar()
        tk.Entry(form, textvariable=self.period_var).grid(row=0, column=1, sticky='ew', padx=8, pady=4)

        # Sıklık
        tk.Label(form, text=self.lm.tr('reporting_frequency', "Raporlama Sıklığı"), bg='white').grid(row=1, column=0, sticky='w')
        self.freq_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.freq_var, values=[
            self.lm.tr('annual', "Yıllık"),
            self.lm.tr('semi_annual', "Altı Aylık"),
            self.lm.tr('quarterly', "Çeyreklik")
        ], state='readonly').grid(row=1, column=1, sticky='ew', padx=8, pady=4)

        # Sınır
        tk.Label(form, text=self.lm.tr('reporting_boundary', "Raporlama Sınırı (Boundary)"), bg='white').grid(row=2, column=0, sticky='w')
        self.boundary_var = tk.StringVar()
        tk.Entry(form, textvariable=self.boundary_var).grid(row=2, column=1, sticky='ew', padx=8, pady=4)

        # İletişim
        tk.Label(form, text=self.lm.tr('contact_info', "İletişim Bilgileri"), bg='white').grid(row=3, column=0, sticky='w')
        self.contact_var = tk.StringVar()
        tk.Entry(form, textvariable=self.contact_var).grid(row=3, column=1, sticky='ew', padx=8, pady=4)

        # Dış doğrulama
        tk.Label(form, text=self.lm.tr('external_assurance', "Harici Güvence (External Assurance)"), bg='white').grid(row=4, column=0, sticky='w')
        self.assurance_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.assurance_var, values=[
            self.lm.tr('exists', "Var"),
            self.lm.tr('none', "Yok"),
            self.lm.tr('planned', "Planlanıyor")
        ], state='readonly').grid(row=4, column=1, sticky='ew', padx=8, pady=4)

        tk.Label(form, text=self.lm.tr('statement_of_use', "Statement of Use"), bg='white').grid(row=5, column=0, sticky='w')
        self.statement_var = tk.StringVar()
        tk.Entry(form, textvariable=self.statement_var).grid(row=5, column=1, sticky='ew', padx=8, pady=4)

        tk.Label(form, text=self.lm.tr('assurance_provider', "Güvence Sağlayıcı"), bg='white').grid(row=6, column=0, sticky='w')
        self.assurance_provider_var = tk.StringVar()
        tk.Entry(form, textvariable=self.assurance_provider_var).grid(row=6, column=1, sticky='ew', padx=8, pady=4)

        tk.Label(form, text=self.lm.tr('assurance_standard', "Güvence Standardı"), bg='white').grid(row=7, column=0, sticky='w')
        self.assurance_standard_var = tk.StringVar()
        tk.Entry(form, textvariable=self.assurance_standard_var).grid(row=7, column=1, sticky='ew', padx=8, pady=4)

        tk.Label(form, text=self.lm.tr('assurance_scope', "Güvence Kapsamı"), bg='white').grid(row=8, column=0, sticky='w')
        self.assurance_scope_var = tk.StringVar()
        tk.Entry(form, textvariable=self.assurance_scope_var).grid(row=8, column=1, sticky='ew', padx=8, pady=4)

        tk.Label(form, text=self.lm.tr('assurance_date', "Güvence Tarihi"), bg='white').grid(row=9, column=0, sticky='w')
        self.assurance_date_var = tk.StringVar()
        tk.Entry(form, textvariable=self.assurance_date_var).grid(row=9, column=1, sticky='ew', padx=8, pady=4)

        # Paydaş katılımı
        tk.Label(form, text=self.lm.tr('stakeholder_engagement', "Paydaş Katılımı"), bg='white').grid(row=10, column=0, sticky='w')
        self.stakeholder_text = tk.Text(form, height=4)
        self.stakeholder_text.grid(row=10, column=1, sticky='ew', padx=8, pady=4)

        # Materyal konular
        tk.Label(form, text=self.lm.tr('material_topics_summary', "Materyal Konular (özet)"), bg='white').grid(row=11, column=0, sticky='w')
        self.material_text = tk.Text(form, height=6)
        self.material_text.grid(row=11, column=1, sticky='ew', padx=8, pady=4)

        form.grid_columnconfigure(1, weight=1)

        tk.Button(self, text=self.lm.tr('btn_save', "Kaydet"), bg='#27ae60', fg='white', relief='flat',
                  command=self.save_foundation).pack(pady=12)

    def save_foundation(self) -> None:
        ok = self.manager.add_gri_1_foundation(
            self.company_id,
            self.period_var.get().strip(),
            self.freq_var.get().strip(),
            self.boundary_var.get().strip(),
            self.contact_var.get().strip(),
            self.assurance_var.get().strip(),
            self.stakeholder_text.get('1.0', tk.END).strip(),
            self.material_text.get('1.0', tk.END).strip(),
            self.statement_var.get().strip(),
            self.assurance_provider_var.get().strip(),
            self.assurance_standard_var.get().strip(),
            self.assurance_scope_var.get().strip(),
            self.assurance_date_var.get().strip()
        )
        if ok:
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('gri_1_saved', "GRI 1 temel bilgileri kaydedildi."))
            self.destroy()
        else:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('save_error', "Kayıt sırasında bir hata oluştu."))


class GRI2DisclosuresForm(tk.Toplevel):
    def __init__(self, parent, company_id: int, db_path: str = None) -> None:
        super().__init__(parent)
        self.lm = LanguageManager()
        self.title(self.lm.tr('gri_2_disclosures_title', "GRI 2: General Disclosures 2021"))
        self.geometry("800x560")
        self.configure(bg='white')
        self.company_id = company_id
        self.manager = GRIStandardsManager(db_path or DB_PATH)

        top = tk.Frame(self, bg='white')
        top.pack(fill='x', padx=12, pady=8)
        tk.Label(top, text=self.lm.tr('reporting_period_label', "Raporlama Dönemi"), bg='white').pack(side='left')
        self.period_var = tk.StringVar()
        tk.Entry(top, textvariable=self.period_var, width=24).pack(side='left', padx=8)

        form = tk.Frame(self, bg='#f8f9fa')
        form.pack(fill='x', padx=12, pady=8)
        tk.Label(form, text=self.lm.tr('disclosure_no', "Açıklama No"), bg='#f8f9fa').grid(row=0, column=0, sticky='w')
        tk.Label(form, text=self.lm.tr('title', "Başlık"), bg='#f8f9fa').grid(row=0, column=1, sticky='w')
        tk.Label(form, text=self.lm.tr('content', "İçerik"), bg='#f8f9fa').grid(row=0, column=2, sticky='w')
        tk.Label(form, text=self.lm.tr('status', "Durum"), bg='#f8f9fa').grid(row=0, column=3, sticky='w')
        tk.Label(form, text=self.lm.tr('page', "Sayfa"), bg='#f8f9fa').grid(row=0, column=4, sticky='w')
        tk.Label(form, text=self.lm.tr('omission_reason', "Eksiklik Nedeni"), bg='#f8f9fa').grid(row=0, column=5, sticky='w')

        self.disc_no = tk.StringVar()
        tk.Entry(form, textvariable=self.disc_no, width=12).grid(row=1, column=0, padx=4, pady=4)
        self.disc_title = tk.StringVar()
        tk.Entry(form, textvariable=self.disc_title, width=24).grid(row=1, column=1, padx=4, pady=4)
        self.disc_content = tk.Text(form, height=4, width=36)
        self.disc_content.grid(row=1, column=2, padx=4, pady=4)
        self.disc_status = tk.StringVar()
        ttk.Combobox(
            form,
            textvariable=self.disc_status,
            values=[
                self.lm.tr('reported', "Reported"),
                self.lm.tr('partially_reported', "Partially Reported"),
                self.lm.tr('omitted', "Omitted")
            ],
            state='readonly',
            width=22,
        ).grid(row=1, column=3, padx=4, pady=4)
        self.page_var = tk.StringVar()
        tk.Entry(form, textvariable=self.page_var, width=8).grid(row=1, column=4, padx=4, pady=4)
        self.omission_var = tk.StringVar()
        tk.Entry(form, textvariable=self.omission_var, width=24).grid(row=1, column=5, padx=4, pady=4)

        tk.Button(form, text=self.lm.tr('btn_add', "Ekle"), bg='#27ae60', fg='white', relief='flat', command=self.add_disclosure).grid(row=2, column=5, sticky='e', padx=4, pady=6)
        form.grid_columnconfigure(2, weight=1)

        # Liste
        list_frame = tk.Frame(self, bg='white')
        list_frame.pack(fill='both', expand=True, padx=12, pady=8)
        self.tree = ttk.Treeview(list_frame, columns=("no", "title", "status"), show='headings')
        self.tree.heading("no", text=self.lm.tr('disclosure_no', "Açıklama No"))
        self.tree.heading("title", text=self.lm.tr('title', "Başlık"))
        self.tree.heading("status", text=self.lm.tr('status', "Durum"))
        self.tree.column("no", width=120)
        self.tree.column("title", width=400)
        self.tree.column("status", width=160)
        self.tree.pack(fill='both', expand=True)

    def add_disclosure(self) -> None:
        # Ön doğrulama: durum-temelli zorunluluklar
        status = self.disc_status.get().strip()
        page_val = self.page_var.get().strip()
        omission_val = self.omission_var.get().strip()

        if status == 'Omitted' and not omission_val:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('omitted_reason_required', "Eksiklik nedeni girilmesi gerekiyor çünkü durum 'Omitted' seçilmiş."))
            return

        if status != 'Omitted' and not page_val:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('page_number_required', "Lütfen sayfa numarası/konumu girin (örn. raporda hangi sayfada yer aldığı)."))
            return

        ok = self.manager.add_gri_2_disclosure(
            self.company_id,
            self.period_var.get().strip(),
            self.disc_no.get().strip(),
            self.disc_title.get().strip(),
            self.disc_content.get('1.0', tk.END).strip(),
            self.disc_status.get().strip(),
            int(page_val) if page_val.isdigit() else None,
            omission_val or None
        )
        if ok:
            self.tree.insert(
                '',
                'end',
                values=(
                    self.disc_no.get().strip(),
                    self.disc_title.get().strip(),
                    self.disc_status.get().strip(),
                ),
            )
            self.disc_no.set("")
            self.disc_title.set("")
            self.disc_status.set("")
            self.disc_content.delete('1.0', tk.END)
            self.page_var.set("")
            self.omission_var.set("")
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('disclosure_added', "Açıklama eklendi."))
        else:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('save_error', "Kayıt sırasında bir hata oluştu."))


class MaterialityForm(tk.Toplevel):
    def __init__(self, parent, company_id: int, db_path: str = None) -> None:
        super().__init__(parent)
        self.lm = LanguageManager()
        self.title(self.lm.tr('materiality_title', "GRI 3: Material Topics - Materyalite"))
        self.geometry("820x560")
        self.configure(bg='white')
        self.company_id = company_id
        self.manager = GRIStandardsManager(db_path or DB_PATH)

        top = tk.Frame(self, bg='white')
        top.pack(fill='x', padx=12, pady=8)
        tk.Label(top, text=self.lm.tr('assessment_year', "Değerlendirme Yılı"), bg='white').pack(side='left')
        self.year_var = tk.StringVar()
        tk.Entry(top, textvariable=self.year_var, width=10).pack(side='left', padx=6)

        form = tk.Frame(self, bg='#f8f9fa')
        form.pack(fill='x', padx=12, pady=8)
        labels = [
            self.lm.tr('topic_name', "Konu Adı"),
            self.lm.tr('category', "Kategori"),
            self.lm.tr('stakeholder_importance', "Paydaş Önemi (0-5)"),
            self.lm.tr('business_impact', "İş Etkisi (0-5)"),
            self.lm.tr('materiality_level', "Materyalite Seviyesi"),
            self.lm.tr('boundary', "Sınır"),
            self.lm.tr('management_approach', "Yönetim Yaklaşımı"),
        ]
        for i, label in enumerate(labels):
            tk.Label(form, text=label, bg='#f8f9fa').grid(row=0, column=i, sticky='w')
        self.topic = tk.StringVar()
        tk.Entry(form, textvariable=self.topic, width=18).grid(row=1, column=0, padx=3, pady=4)
        self.cat = tk.StringVar()
        tk.Entry(form, textvariable=self.cat, width=16).grid(row=1, column=1, padx=3, pady=4)
        self.stake = tk.StringVar()
        tk.Entry(form, textvariable=self.stake, width=10).grid(row=1, column=2, padx=3, pady=4)
        self.business = tk.StringVar()
        tk.Entry(form, textvariable=self.business, width=10).grid(row=1, column=3, padx=3, pady=4)
        self.level = tk.StringVar()
        ttk.Combobox(form, textvariable=self.level, values=[
            self.lm.tr('critical', "Kritik"),
            self.lm.tr('high', "Yüksek"),
            self.lm.tr('medium', "Orta"),
            self.lm.tr('low', "Düşük")
        ], state='readonly', width=14).grid(row=1, column=4, padx=3, pady=4)
        self.boundary = tk.StringVar()
        tk.Entry(form, textvariable=self.boundary, width=16).grid(row=1, column=5, padx=3, pady=4)
        self.approach = tk.StringVar()
        tk.Entry(form, textvariable=self.approach, width=22).grid(row=1, column=6, padx=3, pady=4)

        tk.Button(form, text=self.lm.tr('btn_add', "Ekle"), bg='#27ae60', fg='white', relief='flat', command=self.add_topic).grid(row=2, column=6, sticky='e', padx=4, pady=6)

        listf = tk.Frame(self, bg='white')
        listf.pack(fill='both', expand=True, padx=12, pady=8)
        self.tree = ttk.Treeview(listf, columns=("topic","cat","stake","biz","level"), show='headings')
        headers = [
            self.lm.tr('topic', "Konu"),
            self.lm.tr('category', "Kategori"),
            self.lm.tr('stakeholder', "Paydaş"),
            self.lm.tr('business_impact', "İş Etkisi"),
            self.lm.tr('level', "Seviye")
        ]
        for i, h in enumerate(headers):
            self.tree.heading(self.tree['columns'][i], text=h)
        self.tree.pack(fill='both', expand=True)

    def add_topic(self) -> None:
        try:
            ok = self.manager.add_materiality_assessment(
                self.company_id,
                int(self.year_var.get().strip()),
                self.topic.get().strip(),
                self.cat.get().strip(),
                float(self.stake.get().strip()),
                float(self.business.get().strip()),
                self.level.get().strip(),
                self.boundary.get().strip(),
                self.approach.get().strip()
            )
        except Exception:
            ok = False
        if ok:
            self.tree.insert('', 'end', values=(
                self.topic.get().strip(),
                self.cat.get().strip(),
                self.stake.get().strip(),
                self.business.get().strip(),
                self.level.get().strip()
            ))
            self.topic.set("")
            self.cat.set("")
            self.stake.set("")
            self.business.set("")
            self.level.set("")
            self.boundary.set("")
            self.approach.set("")
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('materiality_added', "Materyalite kaydı eklendi."))
        else:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('save_error', "Kayıt sırasında bir hata oluştu."))


class ContentIndexWindow(tk.Toplevel):
    def __init__(self, parent, company_id: int, db_path: str = None) -> None:
        super().__init__(parent)
        self.lm = LanguageManager()
        self.title(self.lm.tr('gri_content_index_title', "GRI İçerik İndeksi"))
        self.geometry("900x600")
        self.configure(bg='white')
        self.company_id = company_id
        self.manager = GRIStandardsManager(db_path or DB_PATH)
        self.db_path = db_path or DB_PATH

        top = tk.Frame(self, bg='white')
        top.pack(fill='x', padx=12, pady=8)
        tk.Label(top, text=self.lm.tr('reporting_period_label', "Raporlama Dönemi"), bg='white').pack(side='left')
        self.period_var = tk.StringVar()
        tk.Entry(top, textvariable=self.period_var, width=24).pack(side='left', padx=8)
        tk.Button(top, text=self.lm.tr('auto_generate', "Otomatik Oluştur"), bg='#3498db', fg='white', relief='flat', command=self.generate_index).pack(side='left', padx=8)

        # YENİ: Excel Export Butonları
        tk.Button(top, text=self.lm.tr('excel_export_standard', " Excel Export (Standart)"), bg='#27ae60', fg='white', relief='flat', command=self.export_excel_standard).pack(side='left', padx=8)
        tk.Button(top, text=self.lm.tr('excel_export_enhanced', " Excel Export (Gelişmiş)"), bg='#e74c3c', fg='white', relief='flat', command=self.export_excel_enhanced).pack(side='left', padx=8)

        self.text = tk.Text(self, font=('Consolas', 10))
        self.text.pack(fill='both', expand=True, padx=12, pady=8)

    def generate_index(self) -> None:
        content = self.manager.generate_gri_content_index(self.company_id, self.period_var.get().strip())
        if not content:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('content_index_error', "İçerik indeksi oluşturulamadı veya veri bulunamadı."))
            return
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', content)

    def export_excel_standard(self) -> None:
        """Standart Excel export"""
        import os
        from tkinter import filedialog

        # Dosya kaydetme dialogu
        file_path = filedialog.asksaveasfilename(
            title=self.lm.tr('save_excel_standard', "Standart Excel Kaydet"),
            defaultextension=".xlsx",
            filetypes=[(self.lm.tr('excel_file', "Excel dosyası"), "*.xlsx")],
            initialfile=f"GRI_Content_Index_Standard_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )

        if not file_path:
            return

        try:
            # Standart export (eski versiyon)
            from gri.gri_content_index import GRIContentIndex
            content_index = GRIContentIndex(self.db_path)

            if content_index.export_to_excel(file_path, self.company_id):
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{self.lm.tr('excel_export_success', 'Standart Excel dosyası oluşturuldu')}:\n{file_path}")

                # Dosyayı aç
                if messagebox.askyesno(self.lm.tr('open_file', "Dosyayı Aç"), self.lm.tr('open_excel_confirm', "Excel dosyasını açmak ister misiniz?")):
                    os.startfile(file_path)
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('excel_export_fail', "Excel dosyası oluşturulamadı!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('excel_export_error', 'Excel export hatası')}:\n{str(e)}")

    def export_excel_enhanced(self) -> None:
        """Gelişmiş Excel export - YENİ!"""
        import os
        from tkinter import filedialog

        # Dosya kaydetme dialogu
        file_path = filedialog.asksaveasfilename(
            title=self.lm.tr('save_excel_enhanced', "Gelişmiş Excel Kaydet"),
            defaultextension=".xlsx",
            filetypes=[(self.lm.tr('excel_file', "Excel dosyası"), "*.xlsx")],
            initialfile=f"GRI_Content_Index_Enhanced_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )

        if not file_path:
            return

        try:
            # Gelişmiş export (yeni versiyon)
            from gri.gri_content_index_enhanced import GRIContentIndexEnhanced
            content_index_enhanced = GRIContentIndexEnhanced(self.db_path)

            if content_index_enhanced.export_to_excel(file_path, self.company_id):
                msg = (f"{self.lm.tr('enhanced_excel_created', 'Gelişmiş Excel dosyası oluşturuldu!')}\n\n"
                       f"{self.lm.tr('dashboard_page', 'Dashboard sayfası')}\n"
                       f"{self.lm.tr('color_coded_indicators', 'Renk kodlamalı göstergeler')}\n"
                       f"{self.lm.tr('stats_and_charts', 'İstatistikler ve grafikler')}\n\n"
                       f"{self.lm.tr('file', 'Dosya')}: {file_path}")
                
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), msg)

                # Dosyayı aç
                if messagebox.askyesno(self.lm.tr('open_file', "Dosyayı Aç"), self.lm.tr('open_excel_confirm', "Excel dosyasını açmak ister misiniz?")):
                    os.startfile(file_path)
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('enhanced_excel_fail', "Gelişmiş Excel dosyası oluşturulamadı!"))

        except Exception as e:
            import traceback
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('enhanced_excel_error', 'Gelişmiş Excel export hatası')}:\n{str(e)}\n\n{traceback.format_exc()}")


class SectorStandardsWindow(tk.Toplevel):
    def __init__(self, parent, company_id: int, db_path: str = None) -> None:
        super().__init__(parent)
        self.lm = LanguageManager()
        self.title(self.lm.tr('sector_standards_title', "GRI Sektör Standartları"))
        self.geometry("820x560")
        self.configure(bg='white')
        self.company_id = company_id
        self.workflows = GRISectorWorkflows(db_path or DB_PATH)

        top = tk.Frame(self, bg='white')
        top.pack(fill='x', padx=12, pady=8)
        tk.Button(top, text=self.lm.tr('create_templates', "Şablonları Oluştur (GRI 11–14)"), bg='#8e44ad', fg='white', relief='flat', command=self.create_templates).pack(side='left')

        mid = tk.Frame(self, bg='white')
        mid.pack(fill='x', padx=12, pady=8)
        tk.Label(mid, text=self.lm.tr('sector_code', "Sektör Kodu"), bg='white').pack(side='left')
        self.sector_var = tk.StringVar()
        ttk.Combobox(mid, textvariable=self.sector_var, values=["GRI 11","GRI 12","GRI 13","GRI 14"], state='readonly', width=18).pack(side='left', padx=8)
        tk.Button(mid, text=self.lm.tr('check_compliance', "Uyumluluk Durumunu Getir"), bg='#27ae60', fg='white', relief='flat', command=self.check_compliance).pack(side='left', padx=8)

        self.text = tk.Text(self, font=('Consolas', 10))
        self.text.pack(fill='both', expand=True, padx=12, pady=8)

    def create_templates(self) -> None:
        try:
            self.workflows.create_sector_workflow_templates()
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('sector_templates_created', "Sektör iş akışı şablonları oluşturuldu."))
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('template_error', 'Şablonlar oluşturulamadı')}: {e}")

    def check_compliance(self) -> None:
        code = self.sector_var.get().strip()
        if not code:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_sector_code', "Lütfen bir sektör kodu seçin."))
            return
        status = self.workflows.get_sector_compliance_status(self.company_id, code)
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', json.dumps(status, ensure_ascii=False, indent=2))
