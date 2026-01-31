"""
Veri Giriş Format Kontrol Modülü
Para birimi ve tarih formatları için yardımcı fonksiyonlar
"""
import re
import tkinter as tk
from datetime import datetime


class InputFormatters:
    """Veri giriş format kontrol sınıfı"""

    def __init__(self):
        """Utility class, başlatılmasına gerek yok"""
        pass

    @staticmethod
    def create_currency_entry(parent, **kwargs):
        """Para birimi girişi için formatlı Entry oluştur (###.###.###)"""
        var = kwargs.get('textvariable', tk.StringVar())

        # Entry oluştur
        entry = tk.Entry(parent, textvariable=var, **{k: v for k, v in kwargs.items() if k != 'textvariable'})

        # Format kontrolü için event binding
        def format_currency(event=None):
            value = var.get()
            if value:
                # Sadece rakamları al
                digits = re.sub(r'[^\d]', '', value)
                if digits:
                    # Binlik ayırıcı ekle
                    formatted = InputFormatters._format_currency_value(digits)
                    if formatted != value:
                        var.set(formatted)

        # Event binding
        entry.bind('<KeyRelease>', format_currency)
        entry.bind('<FocusOut>', format_currency)

        return entry

    @staticmethod
    def create_date_entry(parent, **kwargs):
        """Tarih girişi için formatlı Entry oluştur (##.##.####)"""
        var = kwargs.get('textvariable', tk.StringVar())

        # Entry oluştur
        entry = tk.Entry(parent, textvariable=var, **{k: v for k, v in kwargs.items() if k != 'textvariable'})

        # Format kontrolü için event binding
        def format_date(event=None):
            value = var.get()
            if value:
                # Sadece rakamları al
                digits = re.sub(r'[^\d]', '', value)
                if digits:
                    # Tarih formatına çevir
                    formatted = InputFormatters._format_date_value(digits)
                    if formatted != value:
                        var.set(formatted)

        # Event binding
        entry.bind('<KeyRelease>', format_date)
        entry.bind('<FocusOut>', format_date)

        return entry

    @staticmethod
    def _format_currency_value(digits):
        """Para birimi değerini formatla (###.###.###)"""
        if not digits:
            return ""

        # Baştan itibaren 3'erli gruplar halinde ayır
        formatted = ""
        for i, digit in enumerate(reversed(digits)):
            if i > 0 and i % 3 == 0:
                formatted = "." + formatted
            formatted = digit + formatted

        return formatted

    @staticmethod
    def _format_date_value(digits):
        """Tarih değerini formatla (##.##.####)"""
        if not digits:
            return ""

        # Maksimum 8 rakam (gg.aa.yyyy)
        digits = digits[:8]

        if len(digits) <= 2:
            return digits
        elif len(digits) <= 4:
            return f"{digits[:2]}.{digits[2:]}"
        else:
            return f"{digits[:2]}.{digits[2:4]}.{digits[4:]}"

    @staticmethod
    def validate_currency(value):
        """Para birimi değerini doğrula"""
        if not value:
            return True, ""

        # Format kontrolü: ###.###.###
        pattern = r'^\d{1,3}(\.\d{3})*$'
        if re.match(pattern, value):
            return True, ""
        else:
            return False, "Para birimi formatı: ###.###.### (örn: 1.000.000)"

    @staticmethod
    def validate_date(value):
        """Tarih değerini doğrula"""
        if not value:
            return True, ""

        # Format kontrolü: ##.##.####
        pattern = r'^\d{2}\.\d{2}\.\d{4}$'
        if not re.match(pattern, value):
            return False, "Tarih formatı: ##.##.#### (örn: 15.03.2024)"

        try:
            # Geçerli tarih kontrolü
            datetime.strptime(value, '%d.%m.%Y')
            return True, ""
        except ValueError:
            return False, "Geçersiz tarih (örn: 15.03.2024)"

    @staticmethod
    def get_currency_numeric_value(formatted_value):
        """Formatlı para birimi değerinden sayısal değer al"""
        if not formatted_value:
            return 0
        return int(re.sub(r'[^\d]', '', formatted_value))

    @staticmethod
    def get_date_datetime_value(formatted_value):
        """Formatlı tarih değerinden datetime objesi al"""
        if not formatted_value:
            return None
        try:
            # Format kontrolü: ##.##.####
            if len(formatted_value) == 10 and formatted_value.count('.') == 2:
                return datetime.strptime(formatted_value, '%d.%m.%Y')
            else:
                return None
        except ValueError:
            return None


class FormattedEntry(tk.Frame):
    """Formatlı Entry widget'ı"""

    def __init__(self, parent, entry_type='text', **kwargs):
        super().__init__(parent)

        self.entry_type = entry_type
        self.var = kwargs.get('textvariable', tk.StringVar())
        self.error_var = tk.StringVar()

        # Entry oluştur
        if entry_type == 'currency':
            self.entry = InputFormatters.create_currency_entry(self, textvariable=self.var, **kwargs)
        elif entry_type == 'date':
            self.entry = InputFormatters.create_date_entry(self, textvariable=self.var, **kwargs)
        else:
            self.entry = tk.Entry(self, textvariable=self.var, **kwargs)

        self.entry.pack(fill='x')

        # Hata mesajı label'ı
        self.error_label = tk.Label(self, textvariable=self.error_var, fg='red', font=('Segoe UI', 8))
        self.error_label.pack(fill='x')

        # Validation binding
        self.entry.bind('<FocusOut>', self._validate)

    def _validate(self, event=None):
        """Değeri doğrula"""
        value = self.var.get()

        if self.entry_type == 'currency':
            is_valid, error_msg = InputFormatters.validate_currency(value)
        elif self.entry_type == 'date':
            is_valid, error_msg = InputFormatters.validate_date(value)
        else:
            is_valid, error_msg = True, ""

        if is_valid:
            self.error_var.set("")
            self.entry.config(bg='white')
        else:
            self.error_var.set(error_msg)
            self.entry.config(bg='#ffebee')

    def get_value(self):
        """Değeri al"""
        if self.entry_type == 'currency':
            return InputFormatters.get_currency_numeric_value(self.var.get())
        elif self.entry_type == 'date':
            return InputFormatters.get_date_datetime_value(self.var.get())
        else:
            return self.var.get()

    def set_value(self, value):
        """Değeri ayarla"""
        if self.entry_type == 'currency' and isinstance(value, (int, float)):
            self.var.set(InputFormatters._format_currency_value(str(int(value))))
        elif self.entry_type == 'date':
            if isinstance(value, datetime):
                self.var.set(value.strftime('%d.%m.%Y'))
            elif isinstance(value, str) and len(value) == 10 and value.count('.') == 2:
                # Zaten formatlı tarih
                self.var.set(value)
            else:
                # String tarih formatını dene
                try:
                    if '-' in value:
                        dt = datetime.strptime(value, '%Y-%m-%d')
                        self.var.set(dt.strftime('%d.%m.%Y'))
                    else:
                        self.var.set(str(value) if value else "")
                except Exception:
                    self.var.set(str(value) if value else "")
        else:
            self.var.set(str(value) if value else "")


# Kullanım örnekleri
def create_formatted_form(parent):
    """Formatlı form örneği"""
    frame = tk.Frame(parent)
    frame.pack(fill='x', padx=10, pady=5)

    # Para birimi girişi
    tk.Label(frame, text="Para Birimi:").pack(anchor='w')
    currency_entry = FormattedEntry(frame, entry_type='currency', width=20)
    currency_entry.pack(fill='x', pady=(0, 10))

    # Tarih girişi
    tk.Label(frame, text="Tarih:").pack(anchor='w')
    date_entry = FormattedEntry(frame, entry_type='date', width=20)
    date_entry.pack(fill='x', pady=(0, 10))

    # Normal giriş
    tk.Label(frame, text="Normal Metin:").pack(anchor='w')
    normal_entry = FormattedEntry(frame, entry_type='text', width=20)
    normal_entry.pack(fill='x')

    return currency_entry, date_entry, normal_entry
