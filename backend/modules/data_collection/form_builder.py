#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Form Builder - Dinamik Form Oluşturma Sistemi
Farklı veri tipleri için standart formlar oluşturur.
"""

import logging
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, List, Optional


class FormField:
    """
    Form alanı tanımı
    
    Her form alanının özelliklerini tutar.
    """

    def __init__(
        self,
        name: str,
        label: str,
        field_type: str = 'text',
        required: bool = False,
        default_value: Any = None,
        options: Optional[List] = None,
        validation: Optional[Callable] = None,
        help_text: Optional[str] = None,
        placeholder: Optional[str] = None,
        unit: Optional[str] = None
    ):
        """
        Form alanı oluştur
        
        Args:
            name: Alan adı (veritabanı kolonu)
            label: Görünen etiket
            field_type: Alan tipi
                - 'text': Tek satır metin
                - 'number': Sayı (int/float)
                - 'textarea': Çok satır metin
                - 'date': Tarih seçici
                - 'dropdown': Açılır liste
                - 'checkbox': Onay kutusu
                - 'radio': Radyo butonlar
            required: Zorunlu mu?
            default_value: Varsayılan değer
            options: Dropdown/radio için seçenekler
            validation: Doğrulama fonksiyonu
            help_text: Yardım metni (? butonu)
            placeholder: Örnek değer
            unit: Birim (kg, kWh, m³, vb.)
        
        Example:
            >>> field = FormField(
            ...     name='electricity_kwh',
            ...     label='Elektrik Tüketimi',
            ...     field_type='number',
            ...     required=True,
            ...     unit='kWh',
            ...     help_text='Yıllık toplam elektrik tüketimi',
            ...     placeholder='Örn: 150000'
            ... )
        """
        self.name = name
        self.label = label
        self.field_type = field_type
        self.required = required
        self.default_value = default_value
        self.options = options or []
        self.validation = validation
        self.help_text = help_text
        self.placeholder = placeholder
        self.unit = unit


class FormBuilder:
    """
    Dinamik form oluşturucu
    
    FormField tanımlarından otomatik GUI formu oluşturur.
    """

    def __init__(self, parent, title: str, fields: List[FormField], on_save: Optional[Callable] = None) -> None:
        """
        Form builder başlat
        
        Args:
            parent: Ana widget
            title: Form başlığı
            fields: Form alanları listesi (FormField nesneleri)
            on_save: Kaydet butonuna tıklandığında çağrılacak fonksiyon
        """
        self.parent = parent
        self.title = title
        self.fields = fields
        self.on_save_callback = on_save

        # Widgets sözlüğü (alan adı → widget)
        self.widgets = {}

        # Hata labels
        self.error_labels = {}

        # Form oluştur
        self.build_form()

    def build_form(self) -> None:
        """Formu oluştur"""

        # Ana frame
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#3498db', height=50)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text=self.title,
            font=('Segoe UI', 14, 'bold'),
            fg='white',
            bg='#3498db'
        )
        title_label.pack(expand=True)

        # Scrollable form alanı
        canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        form_frame = tk.Frame(canvas, bg='white')

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        canvas_window = canvas.create_window((0, 0), window=form_frame, anchor='nw')

        def configure_canvas(event) -> None:
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfig(canvas_window, width=event.width)

        form_frame.bind('<Configure>', configure_canvas)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        # Form içeriği
        content = tk.Frame(form_frame, bg='white')
        content.pack(fill='both', expand=True, padx=30, pady=20)

        # Her alan için widget oluştur
        for field in self.fields:
            self.create_field_widget(content, field)

        # Butonlar
        button_frame = tk.Frame(content, bg='white')
        button_frame.pack(fill='x', pady=20)

        # Kaydet butonu
        save_btn = tk.Button(
            button_frame,
            text=" Kaydet",
            font=('Segoe UI', 11, 'bold'),
            bg='#27ae60',
            fg='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=30,
            pady=10,
            command=self.save_form
        )
        save_btn.pack(side='left', padx=(0, 10))

        # Taslak kaydet butonu
        draft_btn = tk.Button(
            button_frame,
            text=" Taslak Kaydet",
            font=('Segoe UI', 11, 'bold'),
            bg='#3498db',
            fg='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=30,
            pady=10,
            command=self.save_draft
        )
        draft_btn.pack(side='left', padx=(0, 10))

        # İptal butonu
        cancel_btn = tk.Button(
            button_frame,
            text=" İptal",
            font=('Segoe UI', 11, 'bold'),
            bg='#95a5a6',
            fg='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=30,
            pady=10,
            command=self.cancel_form
        )
        cancel_btn.pack(side='left')

    def create_field_widget(self, parent, field: FormField) -> None:
        """
        Bir form alanı widget'ı oluştur
        
        Args:
            parent: Ana widget
            field: FormField nesnesi
        """
        # Alan frame
        field_frame = tk.Frame(parent, bg='white')
        field_frame.pack(fill='x', pady=10)

        # Etiket frame (label + yardım butonu)
        label_frame = tk.Frame(field_frame, bg='white')
        label_frame.pack(fill='x')

        # Etiket
        label_text = field.label
        if field.required:
            label_text += " *"

        label_widget = tk.Label(
            label_frame,
            text=label_text,
            font=('Segoe UI', 10, 'bold'),
            fg='#e74c3c' if field.required else '#2c3e50',
            bg='white',
            anchor='w'
        )
        label_widget.pack(side='left')

        # Birim (varsa)
        if field.unit:
            unit_label = tk.Label(
                label_frame,
                text=f"({field.unit})",
                font=('Segoe UI', 9),
                fg='#7f8c8d',
                bg='white'
            )
            unit_label.pack(side='left', padx=(5, 0))

        # Yardım butonu (varsa)
        if field.help_text:
            help_btn = tk.Button(
                label_frame,
                text="?",
                font=('Segoe UI', 8, 'bold'),
                bg='#3498db',
                fg='white',
                relief='flat',
                bd=0,
                cursor='hand2',
                width=2,
                height=1,
                command=lambda: self.show_help(field.label, field.help_text)
            )
            help_btn.pack(side='left', padx=(10, 0))

        # Widget oluştur (tipine göre)
        widget = None

        if field.field_type == 'text':
            # Tek satır metin
            widget = tk.Entry(
                field_frame,
                font=('Segoe UI', 10),
                relief='solid',
                bd=1
            )
            if field.placeholder:
                widget.insert(0, field.placeholder)
                widget.config(fg='#95a5a6')

                # Placeholder temizleme
                def on_focus_in(e, w=widget, ph=field.placeholder) -> None:
                    if w.get() == ph:
                        w.delete(0, 'end')
                        w.config(fg='#2c3e50')

                def on_focus_out(e, w=widget, ph=field.placeholder) -> None:
                    if not w.get():
                        w.insert(0, ph)
                        w.config(fg='#95a5a6')

                widget.bind('<FocusIn>', on_focus_in)
                widget.bind('<FocusOut>', on_focus_out)

            widget.pack(fill='x', pady=(5, 0))

        elif field.field_type == 'number':
            # Sayı girişi
            widget = tk.Entry(
                field_frame,
                font=('Segoe UI', 10),
                relief='solid',
                bd=1
            )

            # Sadece sayı girişine izin ver
            def validate_number(P) -> None:
                if P == "":
                    return True
                try:
                    float(P.replace(',', '.'))
                    return True
                except Exception:
                    return False

            vcmd = (widget.register(validate_number), '%P')
            widget.config(validate='key', validatecommand=vcmd)

            if field.placeholder:
                widget.insert(0, field.placeholder)
                widget.config(fg='#95a5a6')

            widget.pack(fill='x', pady=(5, 0))

        elif field.field_type == 'textarea':
            # Çok satır metin
            widget = tk.Text(
                field_frame,
                font=('Segoe UI', 10),
                relief='solid',
                bd=1,
                height=4,
                wrap='word'
            )
            if field.placeholder:
                widget.insert('1.0', field.placeholder)
                widget.config(fg='#95a5a6')

            widget.pack(fill='x', pady=(5, 0))

        elif field.field_type == 'date':
            # Tarih seçici (basit)
            date_frame = tk.Frame(field_frame, bg='white')
            date_frame.pack(fill='x', pady=(5, 0))

            # Yıl
            tk.Label(date_frame, text="Yıl:", bg='white', font=('Segoe UI', 9)).pack(side='left', padx=(0, 5))
            year_var = tk.StringVar(value=str(datetime.now().year))
            year_spin = ttk.Spinbox(
                date_frame,
                from_=2000,
                to=2030,
                textvariable=year_var,
                width=8,
                font=('Segoe UI', 10)
            )
            year_spin.pack(side='left', padx=(0, 15))

            # Ay
            tk.Label(date_frame, text="Ay:", bg='white', font=('Segoe UI', 9)).pack(side='left', padx=(0, 5))
            month_var = tk.StringVar(value=str(datetime.now().month))
            month_combo = ttk.Combobox(
                date_frame,
                textvariable=month_var,
                values=[str(i) for i in range(1, 13)],
                width=5,
                state='readonly',
                font=('Segoe UI', 10)
            )
            month_combo.pack(side='left', padx=(0, 15))

            # Gün
            tk.Label(date_frame, text="Gün:", bg='white', font=('Segoe UI', 9)).pack(side='left', padx=(0, 5))
            day_var = tk.StringVar(value=str(datetime.now().day))
            day_combo = ttk.Combobox(
                date_frame,
                textvariable=day_var,
                values=[str(i) for i in range(1, 32)],
                width=5,
                state='readonly',
                font=('Segoe UI', 10)
            )
            day_combo.pack(side='left')

            # Kombine widget (özel)
            widget = {'year': year_var, 'month': month_var, 'day': day_var}

        elif field.field_type == 'dropdown':
            # Açılır liste
            widget = ttk.Combobox(
                field_frame,
                values=field.options,
                state='readonly',
                font=('Segoe UI', 10)
            )
            if field.default_value:
                widget.set(field.default_value)

            widget.pack(fill='x', pady=(5, 0))

        elif field.field_type == 'checkbox':
            # Onay kutusu
            var = tk.BooleanVar(value=field.default_value or False)
            widget = tk.Checkbutton(
                field_frame,
                text=field.label,
                variable=var,
                font=('Segoe UI', 10),
                bg='white'
            )
            widget.var = var  # Değişkeni widget'a ekle
            widget.pack(anchor='w', pady=(5, 0))

        elif field.field_type == 'radio':
            # Radyo butonlar
            var = tk.StringVar(value=field.default_value or '')
            radio_frame = tk.Frame(field_frame, bg='white')
            radio_frame.pack(fill='x', pady=(5, 0))

            for option in field.options:
                radio = tk.Radiobutton(
                    radio_frame,
                    text=option,
                    variable=var,
                    value=option,
                    font=('Segoe UI', 10),
                    bg='white'
                )
                radio.pack(anchor='w')

            widget = radio_frame
            widget.var = var

        # Widget'ı sakla
        self.widgets[field.name] = widget

        # Hata label (başlangıçta gizli)
        error_label = tk.Label(
            field_frame,
            text="",
            font=('Segoe UI', 8),
            fg='#e74c3c',
            bg='white',
            anchor='w'
        )
        error_label.pack(fill='x', pady=(2, 0))
        self.error_labels[field.name] = error_label

    def show_help(self, label: str, help_text: str) -> None:
        """Yardım mesajı göster"""
        messagebox.showinfo(
            f"Yardım: {label}",
            help_text
        )

    def get_field_value(self, field: FormField) -> Any:
        """
        Alan değerini al
        
        Args:
            field: FormField nesnesi
        
        Returns:
            Alan değeri (tiplerine göre)
        """
        widget = self.widgets.get(field.name)
        if not widget:
            return None

        try:
            if field.field_type == 'text' or field.field_type == 'number':
                value = widget.get().strip()
                # Placeholder ise boş say
                if value == field.placeholder:
                    return ""
                # Sayı ise float'a çevir
                if field.field_type == 'number' and value:
                    return float(value.replace(',', '.'))
                return value

            elif field.field_type == 'textarea':
                value = widget.get('1.0', 'end-1c').strip()
                if value == field.placeholder:
                    return ""
                return value

            elif field.field_type == 'date':
                # Tarih formatla (YYYY-MM-DD)
                year = widget['year'].get()
                month = widget['month'].get().zfill(2)
                day = widget['day'].get().zfill(2)
                return f"{year}-{month}-{day}"

            elif field.field_type == 'dropdown':
                return widget.get()

            elif field.field_type == 'checkbox':
                return widget.var.get()

            elif field.field_type == 'radio':
                return widget.var.get()

        except Exception as e:
            logging.info(f"Alan değeri alınamadı ({field.name}): {e}")
            return None

    def validate_form(self) -> bool:
        """
        Formu doğrula
        
        Returns:
            bool: Tüm alanlar geçerli mi?
        """
        is_valid = True

        # Hata mesajlarını temizle
        for error_label in self.error_labels.values():
            error_label.config(text="")

        # Her alanı kontrol et
        for field in self.fields:
            value = self.get_field_value(field)
            error_msg = ""

            # Zorunlu alan kontrolü
            if field.required:
                if value is None or value == "" or value == []:
                    error_msg = "Bu alan zorunludur"
                    is_valid = False

            # Özel validasyon fonksiyonu varsa
            if field.validation and value:
                try:
                    is_field_valid = field.validation(value)
                    if not is_field_valid:
                        error_msg = "Geçersiz değer"
                        is_valid = False
                except Exception as e:
                    error_msg = f"Doğrulama hatası: {e}"
                    is_valid = False

            # Hata mesajını göster
            if error_msg and field.name in self.error_labels:
                self.error_labels[field.name].config(text=error_msg)

        return is_valid

    def get_form_data(self) -> Dict:
        """
        Form verilerini dictionary olarak al
        
        Returns:
            Dict: {alan_adı: değer, ...}
        """
        data = {}

        for field in self.fields:
            value = self.get_field_value(field)
            data[field.name] = value

        return data

    def save_form(self) -> None:
        """Formu kaydet (validasyon ile)"""
        # Validasyon
        if not self.validate_form():
            messagebox.showerror(
                "Hata",
                "Lütfen tüm zorunlu alanları doldurun ve hataları düzeltin."
            )
            return

        # Form verilerini al
        form_data = self.get_form_data()

        # Callback fonksiyonu çağır
        if self.on_save_callback:
            try:
                self.on_save_callback(form_data, is_draft=False)
            except Exception as e:
                messagebox.showerror("Hata", f"Kaydetme hatası: {e}")
        else:
            messagebox.showinfo("Başarılı", "Form kaydedildi!")

    def save_draft(self) -> None:
        """Formu taslak olarak kaydet (validasyon yok)"""
        # Form verilerini al (boş alanlar dahil)
        form_data = self.get_form_data()

        # Callback fonksiyonu çağır
        if self.on_save_callback:
            try:
                self.on_save_callback(form_data, is_draft=True)
            except Exception as e:
                messagebox.showerror("Hata", f"Taslak kaydetme hatası: {e}")
        else:
            messagebox.showinfo("Başarılı", "Taslak kaydedildi!")

    def cancel_form(self) -> None:
        """Formu iptal et"""
        result = messagebox.askyesno(
            "Onay",
            "Değişiklikler kaydedilmeyecek. Devam etmek istiyor musunuz?"
        )

        if result:
            # Ana frame'i kapat veya temizle
            for widget in self.parent.winfo_children():
                widget.destroy()

    def load_data(self, data: Dict) -> None:
        """
        Mevcut verileri forma yükle
        
        Args:
            data: {alan_adı: değer, ...}
        """
        for field in self.fields:
            if field.name not in data:
                continue

            value = data[field.name]
            widget = self.widgets.get(field.name)

            if not widget:
                continue

            try:
                if field.field_type == 'text' or field.field_type == 'number':
                    widget.delete(0, 'end')
                    widget.insert(0, str(value))
                    widget.config(fg='#2c3e50')

                elif field.field_type == 'textarea':
                    widget.delete('1.0', 'end')
                    widget.insert('1.0', str(value))
                    widget.config(fg='#2c3e50')

                elif field.field_type == 'date':
                    # YYYY-MM-DD formatından ayır
                    if isinstance(value, str) and '-' in value:
                        parts = value.split('-')
                        if len(parts) == 3:
                            widget['year'].set(parts[0])
                            widget['month'].set(parts[1])
                            widget['day'].set(parts[2])

                elif field.field_type == 'dropdown':
                    widget.set(value)

                elif field.field_type == 'checkbox':
                    widget.var.set(bool(value))

                elif field.field_type == 'radio':
                    widget.var.set(value)

            except Exception as e:
                logging.error(f"Veri yükleme hatası ({field.name}): {e}")

