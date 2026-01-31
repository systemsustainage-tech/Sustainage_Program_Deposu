#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Form Yönetimi GUI
Dinamik formları yönetmek için arayüz
"""

import logging
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List

from utils.ui_theme import apply_theme

from .dynamic_form_builder import DynamicFormBuilder
from .form_templates import FormTemplateManager


class FormManagementGUI:
    """Form yönetimi ana GUI"""

    def __init__(self, parent, db_path: str, company_id: int = 1) -> None:
        """
        Args:
            parent: Ana pencere
            db_path: Veritabanı yolu
            company_id: Şirket ID
        """
        self.parent = parent
        self.db_path = db_path
        self.company_id = company_id
        self.template_manager = FormTemplateManager(db_path)

        self.setup_gui()

    def setup_gui(self) -> None:
        """GUI bileşenlerini oluştur"""
        apply_theme(self.parent)
        # Ana başlık
        title_frame = tk.Frame(self.parent, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text=" Form Yönetimi ve Veri Toplama",
            font=('Segoe UI', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)

        # İçerik alanı
        content_frame = tk.Frame(self.parent, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        toolbar = ttk.Frame(content_frame)
        toolbar.pack(fill='x', pady=(0, 10))
        ttk.Button(toolbar, text=" Rapor Merkezi", style='Primary.TButton', command=self.open_report_center).pack(side='left', padx=6)
        ttk.Button(toolbar, text=" Yenile", style='Primary.TButton', command=self.load_templates).pack(side='left', padx=6)

        # Sol panel: Form şablonları listesi
        left_frame = tk.Frame(content_frame, bg='white', width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # Şablon listesi başlık
        list_header = tk.Frame(left_frame, bg='#34495e', height=40)
        list_header.pack(fill=tk.X)
        list_header.pack_propagate(False)

        tk.Label(
            list_header,
            text="Form Şablonları",
            font=('Segoe UI', 12, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack(pady=10)

        # Kategori filtresi
        filter_frame = tk.Frame(left_frame, bg='white')
        filter_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            filter_frame,
            text="Kategori:",
            font=('Segoe UI', 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.category_var = tk.StringVar(value="Tümü")
        category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=["Tümü", "GRI", "TSRS", "SDG", "Çevre", "Sosyal", "Ekonomik"],
            state='readonly',
            width=15
        )
        category_combo.pack(side=tk.LEFT)
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.load_templates())

        # Şablon listesi (Treeview)
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.templates_tree = ttk.Treeview(
            tree_frame,
            columns=('form_id',),
            show='tree',
            yscrollcommand=scrollbar.set
        )
        self.templates_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.templates_tree.yview)

        self.templates_tree.bind('<Double-Button-1>', self.on_template_double_click)

        # Butonlar
        button_frame = tk.Frame(left_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text=" Form Doldur",
            style='Primary.TButton',
            command=self.open_selected_form
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            button_frame,
            text=" Kayıtlı Formlar",
            style='Primary.TButton',
            command=self.show_saved_forms
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            button_frame,
            text=" Varsayılan Şablonları Yükle",
            style='Primary.TButton',
            command=self.install_default_templates
        ).pack(fill=tk.X, pady=2)

        # Sağ panel: Form gösterimi
        self.right_frame = tk.Frame(content_frame, bg='white')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Başlangıç mesajı
        welcome_label = tk.Label(
            self.right_frame,
            text=" Soldaki listeden bir form şablonu seçin",
            font=('Segoe UI', 12),
            fg='#95a5a6',
            bg='white'
        )
        welcome_label.pack(expand=True)

        # Şablonları yükle
        self.load_templates()

    def open_report_center(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('genel')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for genel: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor Merkezi açılamadı:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def load_templates(self) -> None:
        """Form şablonlarını yükle"""
        # Ağacı temizle
        for item in self.templates_tree.get_children():
            self.templates_tree.delete(item)

        # Kategori filtresi
        try:
            category = str(self.category_var.get())
        except Exception:
            category = "Tümü"

        if category == "Tümü":
            templates = self.template_manager.list_templates()
        else:
            templates = self.template_manager.list_templates(category=category)

        # Kategoriye göre grupla
        categories: Dict[str, List[Dict[str, Any]]] = {}
        for template in templates:
            cat = template['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(template)

        # Ağaca ekle
        for cat, items in sorted(categories.items()):
            cat_node = self.templates_tree.insert('', tk.END, text=f" {cat}", open=True)

            for template in items:
                self.templates_tree.insert(
                    cat_node,
                    tk.END,
                    text=f"    {template['title']}",
                    values=(template['form_id'],)
                )

    def on_template_double_click(self, event) -> None:
        """Şablona çift tıklandığında formu aç"""
        self.open_selected_form()

    def open_selected_form(self) -> None:
        """Seçilen şablonu aç"""
        selected = self.templates_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir form şablonu seçin")
            return

        # Form ID'yi al
        values = self.templates_tree.item(selected[0], 'values')
        if not values or not values[0]:
            messagebox.showwarning("Uyarı", "Lütfen bir form şablonu seçin (kategori değil)")
            return

        form_id = values[0]

        # Şemayı al
        schema = self.template_manager.get_template(form_id)
        if not schema:
            messagebox.showerror("Hata", "Form şeması yüklenemedi")
            return

        # Sağ paneli temizle
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Form oluştur
        form_builder = DynamicFormBuilder(self.right_frame, self.db_path, self.company_id)
        form_builder.create_form_from_schema(self.right_frame, schema)

    def show_saved_forms(self) -> None:
        """Kayıtlı formları göster"""
        # Yeni pencere
        window = tk.Toplevel(self.parent)
        window.title("Kayıtlı Formlar")
        window.geometry("900x600")

        # Başlık
        title_frame = tk.Frame(window, bg='#34495e', height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text=" Kayıtlı Form Yanıtları",
            font=('Segoe UI', 14, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack(pady=12)

        # Treeview
        tree_frame = tk.Frame(window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'form', 'date'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)

        # Sütunlar
        tree.heading('id', text='ID')
        tree.heading('form', text='Form')
        tree.heading('date', text='Tarih')

        tree.column('id', width=50, anchor='center')
        tree.column('form', width=400, anchor='w')
        tree.column('date', width=150, anchor='center')

        # Verileri yükle
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT fr.id, fr.form_id, fr.created_at, ft.title
                FROM form_responses fr
                LEFT JOIN form_templates ft ON fr.form_id = ft.form_id
                WHERE fr.company_id = ?
                ORDER BY fr.created_at DESC
            """, (self.company_id,))

            for row in cursor.fetchall():
                tree.insert('', tk.END, values=(
                    row[0],
                    row[3] or row[1],
                    row[2][:10] if row[2] else ''
                ))

            conn.close()

        except Exception as e:
            messagebox.showerror("Hata", f"Veriler yüklenemedi:\n{e}")

        # Butonlar
        button_frame = tk.Frame(window)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        def view_response() -> None:
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Uyarı", "Lütfen bir kayıt seçin")
                return

            tree.item(selected[0])['values'][0]
            messagebox.showinfo("Bilgi", "Form goruntuleniyor")

        def delete_response() -> None:
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Uyarı", "Lütfen bir kayıt seçin")
                return

            if messagebox.askyesno("Onay", "Bu kaydı silmek istediğinizden emin misiniz?"):
                response_id = tree.item(selected[0])['values'][0]
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM form_responses WHERE id = ?", (response_id,))
                    conn.commit()
                    conn.close()

                    tree.delete(selected[0])
                    messagebox.showinfo("Başarılı", "Kayıt silindi")
                except Exception as e:
                    messagebox.showerror("Hata", f"Kayıt silinemedi:\n{e}")

        ttk.Button(
            button_frame,
            text="️ Görüntüle",
            style='Primary.TButton',
            command=view_response
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="️ Sil",
            style='Accent.TButton',
            command=delete_response
        ).pack(side=tk.LEFT, padx=5)

    def install_default_templates(self) -> None:
        """Varsayılan şablonları yükle"""
        if messagebox.askyesno(
            "Onay",
            "Varsayılan form şablonlarını yüklemek istediğinizden emin misiniz?\n\n" +
            "Bu işlem aşağıdaki şablonları ekleyecek:\n" +
            "• GRI Standartları (2-1, 2-6, 201-1, 302-1)\n" +
            "• TSRS/ESRS (E1, S1)\n" +
            "• SDG Göstergeleri (7, 13)\n" +
            "• Çevresel Formlar (Su, Atık)\n" +
            "• Sosyal Formlar (İSG, Eğitim)\n" +
            "• Ekonomik Formlar (Tedarik Zinciri)"
        ):
            try:
                self.template_manager.install_default_templates()
                self.load_templates()
                messagebox.showinfo("Başarılı", "Varsayılan şablonlar başarıyla yüklendi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Şablonlar yüklenemedi:\n{e}")

