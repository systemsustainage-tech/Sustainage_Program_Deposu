import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dinamik Form Oluşturucu
Her gösterge için özelleştirilmiş formlar oluşturur
"""

import json
import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional
from utils.language_manager import LanguageManager


class DynamicFormBuilder:
    """
    Dinamik form oluşturucu sınıfı
    JSON şema tabanlı form oluşturma
    """

    # Alan tipleri
    FIELD_TYPES = {
        'text': 'Metin',
        'number': 'Sayı',
        'decimal': 'Ondalık Sayı',
        'date': 'Tarih',
        'select': 'Seçim',
        'multiselect': 'Çoklu Seçim',
        'checkbox': 'Onay Kutusu',
        'textarea': 'Uzun Metin',
        'file': 'Dosya',
        'table': 'Tablo',
        'section': 'Bölüm',
        'calculated': 'Hesaplanmış'
    }

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
        self.lm = LanguageManager()
        self.form_widgets = {}  # Widget referansları
        self.form_data = {}  # Form verileri
        self.validation_rules = {}  # Validasyon kuralları
        self.calculations = {}  # Hesaplama formülleri

    def create_form_from_schema(self, frame: tk.Frame, schema: Dict[str, Any]) -> None:
        """
        JSON şema'dan form oluştur
        
        Args:
            frame: Form yerleştirileceği frame
            schema: Form şeması
            
        Schema örneği:
        {
            "title": "Form Başlığı",
            "description": "Form açıklaması",
            "fields": [
                {
                    "name": "field_name",
                    "type": "text",
                    "label": "Alan Etiketi",
                    "required": True,
                    "default": "",
                    "validation": {"min": 0, "max": 100},
                    "help": "Yardım metni"
                }
            ]
        }
        """
        # Başlık
        if 'title' in schema:
            title_label = tk.Label(
                frame,
                text=schema['title'],
                font=('Segoe UI', 14, 'bold'),
                fg='#2c3e50'
            )
            title_label.pack(pady=(0, 5))

        # Açıklama
        if 'description' in schema:
            desc_label = tk.Label(
                frame,
                text=schema['description'],
                font=('Segoe UI', 9),
                fg='#7f8c8d',
                wraplength=700,
                justify=tk.LEFT
            )
            desc_label.pack(pady=(0, 15))

        # Canvas ve scrollbar oluştur
        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Alanları oluştur
        for field in schema.get('fields', []):
            self._create_field(scrollable_frame, field)

        # Kaydet butonu
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(pady=20, fill=tk.X, padx=20)

        save_btn = tk.Button(
            button_frame,
            text=" Kaydet",
            command=lambda: self._save_form_data(schema.get('form_id')),
            bg='#27ae60',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            cursor='hand2',
            padx=20,
            pady=8
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            button_frame,
            text="️ Temizle",
            command=self._clear_form,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            cursor='hand2',
            padx=20,
            pady=8
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_field(self, parent: tk.Frame, field: Dict[str, Any]) -> None:
        """
        Tek bir alan oluştur
        
        Args:
            parent: Üst frame
            field: Alan tanımı
        """
        field_type = field.get('type', 'text')
        field_name = field.get('name')

        # Bölüm (section) için özel işlem
        if field_type == 'section':
            self._create_section(parent, field)
            return

        # Alan frame'i
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(fill=tk.X, padx=20, pady=8)

        # Etiket
        label_text = field.get('label', field_name)
        if field.get('required', False):
            label_text += " *"

        label = tk.Label(
            field_frame,
            text=label_text,
            font=('Segoe UI', 10, 'bold'),
            bg='white',
            anchor='w'
        )
        label.pack(anchor='w')

        # Yardım metni
        if 'help' in field:
            help_label = tk.Label(
                field_frame,
                text=field['help'],
                font=('Segoe UI', 8),
                fg='#95a5a6',
                bg='white',
                anchor='w',
                wraplength=650,
                justify=tk.LEFT
            )
            help_label.pack(anchor='w', pady=(0, 5))

        # Alan tipine göre widget oluştur
        widget = None

        if field_type == 'text':
            widget = self._create_text_field(field_frame, field)
        elif field_type == 'number':
            widget = self._create_number_field(field_frame, field)
        elif field_type == 'decimal':
            widget = self._create_decimal_field(field_frame, field)
        elif field_type == 'date':
            widget = self._create_date_field(field_frame, field)
        elif field_type == 'select':
            widget = self._create_select_field(field_frame, field)
        elif field_type == 'multiselect':
            widget = self._create_multiselect_field(field_frame, field)
        elif field_type == 'checkbox':
            widget = self._create_checkbox_field(field_frame, field)
        elif field_type == 'textarea':
            widget = self._create_textarea_field(field_frame, field)
        elif field_type == 'file':
            widget = self._create_file_field(field_frame, field)
        elif field_type == 'table':
            widget = self._create_table_field(field_frame, field)
        elif field_type == 'calculated':
            widget = self._create_calculated_field(field_frame, field)

        # Widget'ı kaydet
        if widget:
            self.form_widgets[field_name] = {
                'widget': widget,
                'type': field_type,
                'field': field
            }

            # Validasyon kurallarını kaydet
            if 'validation' in field:
                self.validation_rules[field_name] = field['validation']

            # Hesaplama formülünü kaydet
            if field_type == 'calculated' and 'formula' in field:
                self.calculations[field_name] = field['formula']

    def _create_section(self, parent: tk.Frame, field: Dict[str, Any]) -> None:
        """Bölüm başlığı oluştur"""
        section_frame = tk.Frame(parent, bg='#ecf0f1', relief=tk.RIDGE, bd=1)
        section_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        section_label = tk.Label(
            section_frame,
            text=field.get('label', ''),
            font=('Segoe UI', 12, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50',
            anchor='w'
        )
        section_label.pack(fill=tk.X, padx=15, pady=10)

        if 'description' in field:
            desc_label = tk.Label(
                section_frame,
                text=field['description'],
                font=('Segoe UI', 9),
                bg='#ecf0f1',
                fg='#7f8c8d',
                anchor='w',
                wraplength=650,
                justify=tk.LEFT
            )
            desc_label.pack(fill=tk.X, padx=15, pady=(0, 10))

    def _create_text_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Entry:
        """Metin alanı oluştur"""
        entry = tk.Entry(parent, font=('Segoe UI', 10), width=50)
        entry.pack(fill=tk.X, pady=5)

        # Varsayılan değer
        if 'default' in field:
            entry.insert(0, str(field['default']))

        return entry

    def _create_number_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Entry:
        """Sayı alanı oluştur"""
        vcmd = (parent.register(self._validate_number), '%P')
        entry = tk.Entry(parent, font=('Segoe UI', 10), width=20, validate='key', validatecommand=vcmd)
        entry.pack(anchor='w', pady=5)

        # Varsayılan değer
        if 'default' in field:
            entry.insert(0, str(field['default']))

        return entry

    def _create_decimal_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Entry:
        """Ondalık sayı alanı oluştur"""
        vcmd = (parent.register(self._validate_decimal), '%P')
        entry = tk.Entry(parent, font=('Segoe UI', 10), width=20, validate='key', validatecommand=vcmd)
        entry.pack(anchor='w', pady=5)

        # Varsayılan değer
        if 'default' in field:
            entry.insert(0, str(field['default']))

        return entry

    def _create_date_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Frame:
        """Tarih alanı oluştur"""
        date_frame = tk.Frame(parent, bg='white')
        date_frame.pack(anchor='w', pady=5)

        # Gün
        tk.Label(date_frame, text="Gün:", font=('Segoe UI', 9), bg='white').pack(side=tk.LEFT, padx=(0, 5))
        day_var = tk.StringVar()
        day_combo = ttk.Combobox(date_frame, textvariable=day_var, width=5, state='readonly')
        day_combo['values'] = [str(i) for i in range(1, 32)]
        day_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Ay
        tk.Label(date_frame, text="Ay:", font=('Segoe UI', 9), bg='white').pack(side=tk.LEFT, padx=(0, 5))
        month_var = tk.StringVar()
        month_combo = ttk.Combobox(date_frame, textvariable=month_var, width=5, state='readonly')
        month_combo['values'] = [str(i) for i in range(1, 13)]
        month_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Yıl
        tk.Label(date_frame, text="Yıl:", font=('Segoe UI', 9), bg='white').pack(side=tk.LEFT, padx=(0, 5))
        year_var = tk.StringVar()
        year_combo = ttk.Combobox(date_frame, textvariable=year_var, width=8, state='readonly')
        current_year = datetime.now().year
        year_combo['values'] = [str(i) for i in range(current_year - 10, current_year + 2)]
        year_combo.pack(side=tk.LEFT)

        # Varsayılan değer
        if 'default' in field:
            try:
                date_str = field['default']
                if date_str == 'today':
                    today = datetime.now()
                    day_combo.set(str(today.day))
                    month_combo.set(str(today.month))
                    year_combo.set(str(today.year))
                else:
                    parts = date_str.split('-')
                    if len(parts) == 3:
                        year_combo.set(parts[0])
                        month_combo.set(parts[1])
                        day_combo.set(parts[2])
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        # Frame'i özel obje olarak kaydet
        date_frame.day = day_var
        date_frame.month = month_var
        date_frame.year = year_var

        return date_frame

    def _create_select_field(self, parent: tk.Frame, field: Dict[str, Any]) -> ttk.Combobox:
        """Seçim alanı oluştur"""
        var = tk.StringVar()
        combo = ttk.Combobox(parent, textvariable=var, width=47, state='readonly')
        combo['values'] = field.get('options', [])
        combo.pack(anchor='w', pady=5)

        # Varsayılan değer
        if 'default' in field:
            combo.set(field['default'])

        return combo

    def _create_multiselect_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Frame:
        """Çoklu seçim alanı oluştur"""
        multi_frame = tk.Frame(parent, bg='white', relief=tk.SUNKEN, bd=1)
        multi_frame.pack(fill=tk.BOTH, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(multi_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox
        listbox = tk.Listbox(
            multi_frame,
            selectmode=tk.MULTIPLE,
            font=('Segoe UI', 10),
            height=6,
            yscrollcommand=scrollbar.set
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Seçenekleri ekle
        for option in field.get('options', []):
            listbox.insert(tk.END, option)

        # Varsayılan seçimler
        if 'default' in field:
            defaults = field['default'] if isinstance(field['default'], list) else [field['default']]
            for i, option in enumerate(field.get('options', [])):
                if option in defaults:
                    listbox.selection_set(i)

        return listbox

    def _create_checkbox_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Checkbutton:
        """Onay kutusu oluştur"""
        var = tk.BooleanVar()
        check = tk.Checkbutton(
            parent,
            text=field.get('checkbox_label', ''),
            variable=var,
            font=('Segoe UI', 10),
            bg='white',
            activebackground='white'
        )
        check.pack(anchor='w', pady=5)

        # Varsayılan değer
        if field.get('default', False):
            var.set(True)

        check.var = var
        return check

    def _create_textarea_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Text:
        """Uzun metin alanı oluştur"""
        text_frame = tk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, pady=5)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(
            text_frame,
            font=('Segoe UI', 10),
            height=field.get('rows', 5),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        # Varsayılan değer
        if 'default' in field:
            text_widget.insert('1.0', str(field['default']))

        return text_widget

    def _create_file_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Frame:
        """Dosya alanı oluştur"""
        file_frame = tk.Frame(parent, bg='white')
        file_frame.pack(fill=tk.X, pady=5)

        # Seçilen dosya gösterimi
        file_var = tk.StringVar(value="Dosya seçilmedi")
        file_label = tk.Label(
            file_frame,
            textvariable=file_var,
            font=('Segoe UI', 9),
            fg='#7f8c8d',
            bg='white',
            anchor='w'
        )
        file_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Dosya seç butonu
        def select_file() -> None:
            filename = filedialog.askopenfilename(
                title=field.get('label', self.lm.tr('select_file', 'Dosya Seç')),
                filetypes=field.get('filetypes', [(self.lm.tr('all_files', 'Tüm Dosyalar'), "*.*")])
            )
            if filename:
                file_var.set(os.path.basename(filename))
                file_frame.filepath = filename

        select_btn = tk.Button(
            file_frame,
            text=" Dosya Seç",
            command=select_file,
            bg='#3498db',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            cursor='hand2',
            padx=15,
            pady=5
        )
        select_btn.pack(side=tk.RIGHT)

        file_frame.filepath = None
        file_frame.file_var = file_var

        return file_frame

    def _create_table_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Frame:
        """Tablo alanı oluştur"""
        table_frame = tk.Frame(parent, bg='white')
        table_frame.pack(fill=tk.BOTH, pady=5)

        # Treeview
        columns = field.get('columns', [])
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=5)

        # Sütun başlıkları
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        # Butonlar
        button_frame = tk.Frame(parent, bg='white')
        button_frame.pack(fill=tk.X, pady=(5, 0))

        def add_row() -> None:
            # Satır ekleme dialogu
            dialog = tk.Toplevel(parent)
            dialog.title("Satır Ekle")
            dialog.geometry("400x300")

            entries = {}
            for i, col in enumerate(columns):
                tk.Label(dialog, text=f"{col}:", font=('Segoe UI', 10)).grid(row=i, column=0, sticky='w', padx=10, pady=5)
                entry = tk.Entry(dialog, font=('Segoe UI', 10), width=30)
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[col] = entry

            def save_row() -> None:
                values = [entries[col].get() for col in columns]
                tree.insert('', tk.END, values=values)
                dialog.destroy()

            tk.Button(dialog, text="Kaydet", command=save_row, bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'), padx=20, pady=5).grid(row=len(columns), column=0, columnspan=2, pady=20)

        def delete_row() -> None:
            selected = tree.selection()
            if selected:
                tree.delete(selected)

        tk.Button(button_frame, text=" Satır Ekle", command=add_row, bg='#3498db', fg='white', font=('Segoe UI', 9), cursor='hand2', padx=10, pady=3).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text=" Satır Sil", command=delete_row, bg='#e74c3c', fg='white', font=('Segoe UI', 9), cursor='hand2', padx=10, pady=3).pack(side=tk.LEFT, padx=5)

        table_frame.tree = tree
        return table_frame

    def _create_calculated_field(self, parent: tk.Frame, field: Dict[str, Any]) -> tk.Label:
        """Hesaplanmış alan oluştur (read-only)"""
        result_frame = tk.Frame(parent, bg='#e8f8f5', relief=tk.RIDGE, bd=1)
        result_frame.pack(fill=tk.X, pady=5)

        result_label = tk.Label(
            result_frame,
            text="Hesaplanıyor...",
            font=('Segoe UI', 12, 'bold'),
            bg='#e8f8f5',
            fg='#16a085',
            anchor='w'
        )
        result_label.pack(fill=tk.X, padx=10, pady=10)

        return result_label

    def _validate_number(self, value: str) -> bool:
        """Sayı validasyonu"""
        if value == "":
            return True
        try:
            int(value)
            return True
        except Exception:
            return False

    def _validate_decimal(self, value: str) -> bool:
        """Ondalık sayı validasyonu"""
        if value == "":
            return True
        try:
            float(value.replace(',', '.'))
            return True
        except Exception:
            return False

    def _get_field_value(self, field_name: str) -> Any:
        """Alan değerini al"""
        if field_name not in self.form_widgets:
            return None

        widget_info = self.form_widgets[field_name]
        widget = widget_info['widget']
        field_type = widget_info['type']

        try:
            if field_type in ['text', 'number', 'decimal']:
                val = widget.get()
                return str(val) if val is not None else ""
            elif field_type == 'date':
                # Safe get for StringVar
                day = str(widget.day.get()) if widget.day.get() else ""
                month = str(widget.month.get()) if widget.month.get() else ""
                year = str(widget.year.get()) if widget.year.get() else ""
                if day and month and year:
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                return None
            elif field_type == 'select':
                val = widget.get()
                return str(val) if val is not None else ""
            elif field_type == 'multiselect':
                selected = widget.curselection()
                return [str(widget.get(i)) for i in selected]
            elif field_type == 'checkbox':
                # BooleanVar.get() returns bool, but let's be safe
                return bool(widget.var.get())
            elif field_type == 'textarea':
                return str(widget.get('1.0', tk.END)).strip()
            elif field_type == 'file':
                return getattr(widget, 'filepath', None)
            elif field_type == 'table':
                rows = []
                for item in widget.tree.get_children():
                    # Ensure values are strings
                    vals = widget.tree.item(item)['values']
                    rows.append([str(v) for v in vals] if vals else [])
                return rows
        except Exception as e:
            logging.error(f"Error getting field value: {e}")
            return None

    def _validate_form(self) -> tuple[bool, List[str]]:
        """
        Form validasyonu
        
        Returns:
            (başarılı_mı, hata_mesajları)
        """
        errors = []

        for field_name, widget_info in self.form_widgets.items():
            field = widget_info['field']
            value = self._get_field_value(field_name)

            # Zorunlu alan kontrolü
            if field.get('required', False):
                if value is None or value == '' or (isinstance(value, list) and len(value) == 0):
                    errors.append(f"'{field.get('label', field_name)}' alanı zorunludur")

            # Validasyon kuralları
            if field_name in self.validation_rules and value:
                rules = self.validation_rules[field_name]

                # Min değer
                if 'min' in rules:
                    try:
                        if float(value) < rules['min']:
                            errors.append(f"'{field.get('label', field_name)}' minimum {rules['min']} olmalıdır")
                    except Exception as e:
                        logging.error(f"Silent error caught: {str(e)}")

                # Max değer
                if 'max' in rules:
                    try:
                        if float(value) > rules['max']:
                            errors.append(f"'{field.get('label', field_name)}' maksimum {rules['max']} olmalıdır")
                    except Exception as e:
                        logging.error(f"Silent error caught: {str(e)}")

                # Min uzunluk
                if 'minLength' in rules:
                    if len(str(value)) < rules['minLength']:
                        errors.append(f"'{field.get('label', field_name)}' en az {rules['minLength']} karakter olmalıdır")

                # Max uzunluk
                if 'maxLength' in rules:
                    if len(str(value)) > rules['maxLength']:
                        errors.append(f"'{field.get('label', field_name)}' en fazla {rules['maxLength']} karakter olmalıdır")

                # Pattern (regex)
                if 'pattern' in rules:
                    import re
                    if not re.match(rules['pattern'], str(value)):
                        error_msg = rules.get('patternMessage', f"'{field.get('label', field_name)}' geçersiz format")
                        errors.append(error_msg)

        return (len(errors) == 0, errors)

    def _calculate_fields(self) -> None:
        """Hesaplanmış alanları güncelle"""
        for field_name, formula in self.calculations.items():
            if field_name in self.form_widgets:
                widget = self.form_widgets[field_name]['widget']

                try:
                    # Formüldeki değişkenleri değerlerle değiştir
                    calc_formula = formula
                    for var_name in self.form_widgets:
                        value = self._get_field_value(var_name)
                        if value and isinstance(value, (int, float, str)):
                            try:
                                num_value = float(value)
                                calc_formula = calc_formula.replace(f"{{{var_name}}}", str(num_value))
                            except Exception as e:
                                logging.error(f"Silent error caught: {str(e)}")

                    # Hesapla
                    result = eval(calc_formula)
                    widget.config(text=f"{result:.2f}")
                except Exception as e:
                    widget.config(text=f"Hesaplama hatası: {e}")

    def _save_form_data(self, form_id: Optional[str] = None) -> None:
        """Form verilerini kaydet"""
        # Validasyon
        is_valid, errors = self._validate_form()
        if not is_valid:
            messagebox.showerror(
                "Validasyon Hatası",
                "Lütfen aşağıdaki hataları düzeltin:\n\n" + "\n".join(f"• {e}" for e in errors)
            )
            return

        # Veriyi topla
        form_data = {}
        for field_name in self.form_widgets:
            form_data[field_name] = self._get_field_value(field_name)

        # Veritabanına kaydet
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Form responses tablosuna kaydet
            cursor.execute("""
                INSERT INTO form_responses 
                (form_id, company_id, response_data, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                form_id or 'dynamic_form',
                self.company_id,
                json.dumps(form_data, ensure_ascii=False),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Form başarıyla kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Form kaydedilemedi:\n{e}")

    def _clear_form(self) -> None:
        """Formu temizle"""
        if messagebox.askyesno("Onay", "Formu temizlemek istediğinizden emin misiniz?"):
            for field_name, widget_info in self.form_widgets.items():
                widget = widget_info['widget']
                field_type = widget_info['type']

                try:
                    if field_type in ['text', 'number', 'decimal']:
                        widget.delete(0, tk.END)
                    elif field_type == 'date':
                        widget.day.set('')
                        widget.month.set('')
                        widget.year.set('')
                    elif field_type in ['select']:
                        widget.set('')
                    elif field_type == 'multiselect':
                        widget.selection_clear(0, tk.END)
                    elif field_type == 'checkbox':
                        widget.var.set(False)
                    elif field_type == 'textarea':
                        widget.delete('1.0', tk.END)
                    elif field_type == 'file':
                        widget.filepath = None
                        widget.file_var.set("Dosya seçilmedi")
                    elif field_type == 'table':
                        for item in widget.tree.get_children():
                            widget.tree.delete(item)
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

    def load_form_data(self, form_id: str, response_id: int) -> None:
        """Kayıtlı form verilerini yükle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT response_data 
                FROM form_responses 
                WHERE id = ? AND form_id = ? AND company_id = ?
            """, (response_id, form_id, self.company_id))

            result = cursor.fetchone()
            conn.close()

            if result:
                data = json.loads(result[0])

                # Alanları doldur
                for field_name, value in data.items():
                    if field_name in self.form_widgets:
                        widget_info = self.form_widgets[field_name]
                        widget = widget_info['widget']
                        field_type = widget_info['type']

                        try:
                            if field_type in ['text', 'number', 'decimal']:
                                widget.delete(0, tk.END)
                                widget.insert(0, str(value))
                            elif field_type == 'date' and value:
                                parts = value.split('-')
                                if len(parts) == 3:
                                    widget.year.set(parts[0])
                                    widget.month.set(parts[1])
                                    widget.day.set(parts[2])
                            elif field_type == 'select':
                                widget.set(value)
                            elif field_type == 'multiselect' and isinstance(value, list):
                                options = widget_info['field'].get('options', [])
                                for i, opt in enumerate(options):
                                    if opt in value:
                                        widget.selection_set(i)
                            elif field_type == 'checkbox':
                                widget.var.set(bool(value))
                            elif field_type == 'textarea':
                                widget.delete('1.0', tk.END)
                                widget.insert('1.0', str(value))
                        except Exception as e:
                            logging.error(f"Silent error caught: {str(e)}")

        except Exception as e:
            messagebox.showerror("Hata", f"Form verileri yüklenemedi:\n{e}")

