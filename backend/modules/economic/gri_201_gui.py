#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI 201-1 Ekonomik Değer Dağılımı GUI
Direct Economic Value Generated and Distributed
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from utils.language_manager import LanguageManager
from .gri_201_calculator import GRI201Calculator


class GRI201GUI:
    """GRI 201-1 arayüzü"""

    def __init__(self, parent, db_path: str, company_id: int, year: int = 2024) -> None:
        self.parent = parent
        self.db_path = db_path
        self.company_id = company_id
        self.year = year
        self.lm = LanguageManager()
        self.calculator = GRI201Calculator(db_path)

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Başlık
        header = tk.Frame(self.parent, bg='#27ae60', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text=self.lm.tr('gri201_title', " GRI 201-1: Ekonomik Değer Dağılımı"),
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#27ae60').pack(side='left', padx=20, pady=20)

        tk.Label(header, text=self.lm.tr('gri201_subtitle', "Doğrudan Ekonomik Değer Üretimi ve Dağıtımı"),
                font=('Segoe UI', 10), fg='#ecf0f1', bg='#27ae60').pack(side='left')

        # Notebook
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)

        # Veri Girişi sekmesi
        self.data_entry_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.data_entry_frame, text=self.lm.tr('gri201_tab_data_entry', " Veri Girişi"))

        # Hesaplama sekmesi
        self.calculation_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.calculation_frame, text=self.lm.tr('gri201_tab_calculation_report', " Hesaplama ve Rapor"))

        self.build_data_entry_tab()
        self.build_calculation_tab()

    def build_data_entry_tab(self) -> None:
        """Veri girişi sekmesi"""
        # Sol panel - Veri listesi
        left_panel = tk.LabelFrame(self.data_entry_frame, text=self.lm.tr('gri201_grp_saved_data', " Kayıtlı Veriler"),
                                   bg='#ecf0f1', font=('Segoe UI', 11, 'bold'))
        left_panel.pack(side='left', fill='both', expand=True, padx=(10, 5), pady=10)

        # Sağ panel - Veri girişi
        right_panel = tk.LabelFrame(self.data_entry_frame, text=self.lm.tr('gri201_grp_add_new_data', " Yeni Veri Ekle"),
                                    bg='white', font=('Segoe UI', 11, 'bold'))
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

        self.build_data_list(left_panel)
        self.build_data_form(right_panel)

    def build_data_list(self, parent) -> None:
        """Veri listesi"""
        # Treeview
        columns = ('Kategori', 'Alt Kategori', 'Tutar', 'Para Birimi', 'Not')
        self.data_tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)

        self.data_tree.heading('Kategori', text=self.lm.tr('gri201_col_category', 'Kategori'))
        self.data_tree.heading('Alt Kategori', text=self.lm.tr('gri201_col_subcategory', 'Alt Kategori'))
        self.data_tree.heading('Tutar', text=self.lm.tr('gri201_col_amount', 'Tutar'))
        self.data_tree.heading('Para Birimi', text=self.lm.tr('gri201_col_currency', 'Para Birimi'))
        self.data_tree.heading('Not', text=self.lm.tr('gri201_col_notes', 'Notlar'))

        self.data_tree.column('Kategori', width=120)
        self.data_tree.column('Alt Kategori', width=180)
        self.data_tree.column('Tutar', width=120, anchor='e')
        self.data_tree.column('Para Birimi', width=50)
        self.data_tree.column('Not', width=200)

        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=scrollbar.set)

        self.data_tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side='right', fill='y', pady=10, padx=(0, 10))

        # Butonlar
        button_frame = tk.Frame(parent, bg='#ecf0f1')
        button_frame.pack(fill='x', padx=10, pady=(0, 10))

        tk.Button(button_frame, text=self.lm.tr('gri201_btn_delete', "️ Sil"), font=('Segoe UI', 9, 'bold'),
                 bg='#e74c3c', fg='white', relief='flat', cursor='hand2',
                 padx=15, pady=5, command=self.delete_data).pack(side='left', padx=5)

        tk.Button(button_frame, text=self.lm.tr('gri201_btn_refresh', " Yenile"), font=('Segoe UI', 9, 'bold'),
                 bg='#3498db', fg='white', relief='flat', cursor='hand2',
                 padx=15, pady=5, command=self.load_data).pack(side='left', padx=5)

        tk.Button(button_frame, text=self.lm.tr('gri201_btn_sample_data', "Örnek Veri"), font=('Segoe UI', 9, 'bold'),
                 bg='#9b59b6', fg='white', relief='flat', cursor='hand2',
                 padx=15, pady=5, command=self.create_sample_data).pack(side='left', padx=5)

    def build_data_form(self, parent) -> None:
        """Veri girişi formu"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Kategori
        tk.Label(form_frame, text=self.lm.tr('gri201_lbl_category', "Kategori:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var,
                                     state='readonly', width=37)
        category_combo['values'] = [
            self.lm.tr('gri201_cat_generated', 'Generated (Üretilen)'),
            self.lm.tr('gri201_cat_distributed', 'Distributed_Operating (Dağıtılan)')
        ]
        category_combo.pack(fill='x', pady=(0, 15))
        category_combo.bind('<<ComboboxSelected>>', self.on_category_change)

        # Alt Kategori
        tk.Label(form_frame, text=self.lm.tr('gri201_lbl_subcategory', "Alt Kategori:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(form_frame, textvariable=self.subcategory_var,
                                             state='readonly', width=37)
        self.subcategory_combo.pack(fill='x', pady=(0, 15))

        # Tutar
        tk.Label(form_frame, text=self.lm.tr('gri201_lbl_amount', "Tutar (TRY):"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        self.amount_var = tk.StringVar()
        amount_entry = tk.Entry(form_frame, textvariable=self.amount_var, font=('Segoe UI', 10), width=40)
        amount_entry.pack(fill='x', pady=(0, 15))

        # Notlar
        tk.Label(form_frame, text=self.lm.tr('gri201_lbl_notes', "Notlar:"), font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(0, 5))
        self.notes_text = tk.Text(form_frame, height=4, font=('Segoe UI', 9), wrap='word')
        self.notes_text.pack(fill='x', pady=(0, 15))

        # Veri Kaynağı
        tk.Label(form_frame, text=self.lm.tr('gri201_lbl_data_source', "Veri Kaynağı:"), font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(0, 5))
        self.source_var = tk.StringVar()
        source_entry = tk.Entry(form_frame, textvariable=self.source_var, font=('Segoe UI', 9), width=40)
        source_entry.pack(fill='x', pady=(0, 20))

        # Kaydet butonu
        tk.Button(form_frame, text=self.lm.tr('gri201_btn_save', " Kaydet"), font=('Segoe UI', 11, 'bold'),
                 bg='#27ae60', fg='white', relief='flat', cursor='hand2',
                 padx=30, pady=10, command=self.save_data).pack()

    def build_calculation_tab(self) -> None:
        """Hesaplama sekmesi"""
        # Kontrol paneli
        control_frame = tk.Frame(self.calculation_frame, bg='white')
        control_frame.pack(fill='x', padx=20, pady=15)

        tk.Button(control_frame, text=self.lm.tr('gri201_btn_calculate', " Hesapla"), font=('Segoe UI', 11, 'bold'),
                 bg='#27ae60', fg='white', relief='flat', cursor='hand2',
                 padx=20, pady=8, command=self.calculate).pack(side='left', padx=5)

        tk.Button(control_frame, text=self.lm.tr('gri201_btn_generate_report', " Rapor Oluştur"), font=('Segoe UI', 11, 'bold'),
                 bg='#3498db', fg='white', relief='flat', cursor='hand2',
                 padx=20, pady=8, command=self.generate_report).pack(side='left', padx=5)

        # Sonuç kartları
        cards_frame = tk.Frame(self.calculation_frame, bg='white')
        cards_frame.pack(fill='x', padx=20, pady=(0, 15))

        self.result_labels = {}

        # Üretilen Değer kartı
        generated_card = tk.Frame(cards_frame, bg='#27ae60', relief='raised', bd=2)
        generated_card.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(generated_card, text=self.lm.tr('gri201_card_generated', "Üretilen Ekonomik Değer"), font=('Segoe UI', 10, 'bold'),
                bg='#27ae60', fg='white').pack(pady=(10, 5))
        self.result_labels['generated'] = tk.Label(generated_card, text="0 TRY",
                                                   font=('Segoe UI', 16, 'bold'),
                                                   bg='#27ae60', fg='white')
        self.result_labels['generated'].pack(pady=(0, 10))

        # Dağıtılan Değer kartı
        distributed_card = tk.Frame(cards_frame, bg='#e67e22', relief='raised', bd=2)
        distributed_card.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(distributed_card, text=self.lm.tr('gri201_card_distributed', "Dağıtılan Ekonomik Değer"), font=('Segoe UI', 10, 'bold'),
                bg='#e67e22', fg='white').pack(pady=(10, 5))
        self.result_labels['distributed'] = tk.Label(distributed_card, text="0 TRY",
                                                     font=('Segoe UI', 16, 'bold'),
                                                     bg='#e67e22', fg='white')
        self.result_labels['distributed'].pack(pady=(0, 10))

        # Tutulan Değer kartı
        retained_card = tk.Frame(cards_frame, bg='#3498db', relief='raised', bd=2)
        retained_card.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(retained_card, text=self.lm.tr('gri201_card_retained', "İşletmede Tutulan Değer"), font=('Segoe UI', 10, 'bold'),
                bg='#3498db', fg='white').pack(pady=(10, 5))
        self.result_labels['retained'] = tk.Label(retained_card, text="0 TRY",
                                                  font=('Segoe UI', 16, 'bold'),
                                                  bg='#3498db', fg='white')
        self.result_labels['retained'].pack(pady=(0, 10))

        # Detaylı dağılım
        detail_frame = tk.LabelFrame(self.calculation_frame, text=self.lm.tr('gri201_grp_detailed_distribution', " Detaylı Dağılım"),
                                     bg='white', font=('Segoe UI', 11, 'bold'))
        detail_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        self.detail_tree = ttk.Treeview(detail_frame, columns=('Kategori', 'Tutar', 'Oran'),
                                       show='headings', height=12)

        self.detail_tree.heading('Kategori', text=self.lm.tr('gri201_col_category', 'Kategori'))
        self.detail_tree.heading('Tutar', text=self.lm.tr('gri201_col_amount', 'Tutar (TRY)'))
        self.detail_tree.heading('Oran', text=self.lm.tr('gri201_col_ratio', 'Oran (%)'))

        self.detail_tree.column('Kategori', width=300)
        self.detail_tree.column('Tutar', width=150, anchor='e')
        self.detail_tree.column('Oran', width=100, anchor='e')

        scrollbar = ttk.Scrollbar(detail_frame, orient='vertical', command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=scrollbar.set)

        self.detail_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)

    def on_category_change(self, event) -> None:
        """Kategori değiştiğinde alt kategorileri güncelle"""
        category = self.category_var.get()

        if 'Generated' in category:
            subcategories = [self.lm.tr('gri201_subcat_revenues', 'revenues (Gelirler)')]
        else:
            subcategories = [
                self.lm.tr('gri201_subcat_operating_costs', 'operating_costs (İşletme Maliyetleri)'),
                self.lm.tr('gri201_subcat_employee_wages', 'employee_wages (Çalışan Ücretleri)'),
                self.lm.tr('gri201_subcat_payments_capital', 'payments_capital_providers (Sermaye Sağlayıcılara Ödemeler)'),
                self.lm.tr('gri201_subcat_payments_govt', 'payments_government (Devlete Ödemeler)'),
                self.lm.tr('gri201_subcat_community', 'community_investments (Topluma Yatırımlar)')
            ]

        self.subcategory_combo['values'] = subcategories
        if subcategories:
            self.subcategory_combo.current(0)

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            data = self.calculator.get_economic_data(self.company_id, self.year)

            # Ağacı temizle
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)

            # Verileri ekle
            for item in data:
                self.data_tree.insert('', 'end', values=(
                    item['category'],
                    item['subcategory'],
                    f"{item['amount']:,.2f}",
                    item['currency'],
                    item['notes'] or ''
                ))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('data_load_error', 'Veri yükleme hatası')}: {e}")

    def save_data(self) -> None:
        """Veri kaydet"""
        try:
            category = self.category_var.get()
            if not category:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_category', "Lütfen kategori seçin"))
                return

            subcategory = self.subcategory_var.get()
            if not subcategory:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_subcategory', "Lütfen alt kategori seçin"))
                return

            amount_str = self.amount_var.get().strip()
            if not amount_str:
                messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('enter_amount', "Lütfen tutar girin"))
                return

            try:
                amount = float(amount_str.replace(',', ''))
            except ValueError:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('invalid_amount_format', "Geçersiz tutar formatı"))
                return

            # Kategori ve alt kategori kodlarını al
            category_code = category.split('(')[0].strip()
            subcategory_code = subcategory.split('(')[0].strip()

            notes = self.notes_text.get('1.0', 'end').strip()
            source = self.source_var.get().strip()

            success = self.calculator.add_economic_data(
                self.company_id, self.year, category_code, subcategory_code,
                amount, notes=notes, data_source=source
            )

            if success:
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('gri201_msg_data_saved', "Veri kaydedildi"))
                self.load_data()
                # Formu temizle
                self.amount_var.set("")
                self.notes_text.delete('1.0', 'end')
                self.source_var.set("")
            else:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('gri201_msg_save_fail', "Veri kaydedilemedi"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('gri201_msg_save_error', 'Kaydetme hatası')}: {e}")

    def delete_data(self) -> None:
        """Seçili veriyi sil"""
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr('warning', "Uyarı"), self.lm.tr('select_record_delete', "Lütfen silinecek kaydı seçin"))
            return

        # Seçili item'ın değerlerini al
        item = self.data_tree.item(selection[0])
        values = item['values']
        record_id = values[0] if values else None

        if not record_id:
            messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('error_id_not_found', "Kayıt ID'si bulunamadı!"))
            return

        if messagebox.askyesno(self.lm.tr('confirm', "Onay"), self.lm.tr('confirm_delete_irreversible', "Seçili kaydı silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!")):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM gri_201_data WHERE id = ?", (record_id,))
                conn.commit()
                conn.close()

                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('record_deleted', "Kayıt silindi!"))
                self.load_data()  # Listeyi yenile

            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('error_delete', 'Silme hatası')}: {e}")

    def calculate(self) -> None:
        """GRI 201-1 hesapla"""
        try:
            result = self.calculator.calculate_gri_201(self.company_id, self.year)

            if not result:
                messagebox.showerror(self.lm.tr('error', "Hata"), self.lm.tr('gri201_msg_calc_fail', "Hesaplama yapılamadı"))
                return

            # Kartları güncelle
            self.result_labels['generated'].config(text=f"{result['total_generated']:,.2f} TRY")
            self.result_labels['distributed'].config(text=f"{result['total_distributed']:,.2f} TRY")
            self.result_labels['retained'].config(text=f"{result['retained']:,.2f} TRY")

            # Detay ağacını güncelle
            for item in self.detail_tree.get_children():
                self.detail_tree.delete(item)

            # Dağıtılan değerler
            distributed_labels = {
                'operating_costs': self.lm.tr('gri201_lbl_operating_costs', 'İşletme Maliyetleri'),
                'employee_wages': self.lm.tr('gri201_lbl_employee_wages', 'Çalışan Ücretleri ve Yan Haklar'),
                'payments_capital_providers': self.lm.tr('gri201_lbl_payments_capital', 'Sermaye Sağlayıcılara Ödemeler'),
                'payments_government': self.lm.tr('gri201_lbl_payments_govt', 'Devlete Ödemeler (Vergi)'),
                'community_investments': self.lm.tr('gri201_lbl_community_investments', 'Topluma Yatırımlar')
            }

            for key, value in result['distributed'].items():
                percentage = (value / result['total_generated'] * 100) if result['total_generated'] > 0 else 0
                label = distributed_labels.get(key, key)
                self.detail_tree.insert('', 'end', values=(
                    label,
                    f"{value:,.2f}",
                    f"{percentage:.2f}%"
                ))

            # Tutulan değer
            retained_pct = (result['retained'] / result['total_generated'] * 100) if result['total_generated'] > 0 else 0
            self.detail_tree.insert('', 'end', values=(
                self.lm.tr('gri201_card_retained', "İşletmede Tutulan Değer"),
                f"{result['retained']:,.2f}",
                f"{retained_pct:.2f}%"
            ))

            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('gri201_msg_calc_success', "GRI 201-1 hesaplandı"))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('gri201_msg_calc_error', 'Hesaplama hatası')}: {e}")

    def generate_report(self) -> None:
        """Rapor oluştur"""
        try:
            report = self.calculator.generate_report(self.company_id, self.year)

            # Rapor penceresi
            report_window = tk.Toplevel(self.parent)
            report_window.title(f"GRI 201-1 Raporu - {self.year}")
            report_window.geometry("800x600")

            # Rapor metni
            report_text = scrolledtext.ScrolledText(report_window, font=('Courier', 10), wrap='word')
            report_text.pack(fill='both', expand=True, padx=10, pady=10)
            report_text.insert('1.0', report)
            report_text.config(state='disabled')

            # Kapat butonu
            tk.Button(report_window, text=self.lm.tr('btn_close', "Kapat"), font=('Segoe UI', 10, 'bold'),
                     bg='#95a5a6', fg='white', relief='flat', cursor='hand2',
                     padx=20, pady=8, command=report_window.destroy).pack(pady=(0, 10))

        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('report_error', 'Rapor oluşturma hatası')}: {e}")

    def create_sample_data(self) -> None:
        """Örnek veri oluştur"""
        if messagebox.askyesno(self.lm.tr('confirm', "Onay"), self.lm.tr('gri201_msg_sample_confirm', "Örnek veri oluşturulsun mu?")):
            self.calculator.create_sample_data(self.company_id, self.year)
            self.load_data()
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('gri201_msg_sample_success', "Örnek veri oluşturuldu"))

