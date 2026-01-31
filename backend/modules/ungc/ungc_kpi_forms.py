#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UN Global Compact - KPI Data Collection Forms
Kullanıcı dostu form widgetları ile KPI veri girişi
"""
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Dict, List, Optional, Tuple

from modules.forms.input_formatters import InputFormatters
from modules.ungc.ungc_manager_enhanced import UNGCManagerEnhanced
from config.database import DB_PATH


class KPIFormWidget(ttk.Frame):
    """Single KPI input widget"""

    def __init__(self, parent, kpi: Dict, **kwargs):
        super().__init__(parent, **kwargs)
        self.kpi = kpi
        self.value_var = tk.StringVar()
        self._create_widget()

    def _create_widget(self):
        """Create form widget based on KPI type"""
        kpi_type = self.kpi.get('type', 'number')
        kpi_name = self.kpi.get('name_tr', self.kpi.get('name_en', ''))
        target = self.kpi.get('target')
        unit = self.kpi.get('unit', '')

        # KPI label
        label_frame = ttk.Frame(self)
        label_frame.pack(fill='x', pady=5)

        label_text = f"{kpi_name}"
        if target is not None:
            label_text += f" (Hedef: {target}{' ' + unit if unit else ''})"

        ttk.Label(label_frame, text=label_text, wraplength=400).pack(side='left')

        # Input widget based on type
        input_frame = ttk.Frame(self)
        input_frame.pack(fill='x', pady=5)

        if kpi_type == 'boolean':
            self._create_boolean_widget(input_frame)
        elif kpi_type == 'percentage':
            self._create_percentage_widget(input_frame)
        elif kpi_type == 'number':
            self._create_number_widget(input_frame)

    def _create_boolean_widget(self, parent):
        """Boolean checkbox"""
        var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(
            parent,
            text="Evet",
            variable=var,
            command=lambda: self.value_var.set("1" if var.get() else "0")
        )
        checkbox.pack(side='left')
        self.input_widget = checkbox
        self.bool_var = var

    def _create_percentage_widget(self, parent):
        """Percentage slider + entry"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x')

        # Entry
        entry = ttk.Entry(frame, textvariable=self.value_var, width=10)
        entry.pack(side='left', padx=5)

        ttk.Label(frame, text="%").pack(side='left')

        # Slider
        slider = ttk.Scale(
            frame,
            from_=0,
            to=100,
            orient='horizontal',
            length=200,
            command=lambda v: self.value_var.set(f"{float(v):.1f}")
        )
        slider.pack(side='left', padx=10)

        self.input_widget = entry
        self.slider = slider

    def _create_number_widget(self, parent):
        """Number entry - Para birimi formatı ile"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x')

        unit = self.kpi.get('unit', '')

        # Para birimi birimi varsa formatlı giriş kullan
        if unit and any(currency in unit.lower() for currency in ['tl', 'lira', '₺', 'euro', '€', 'dollar', '$', 'usd', 'eur']):
            entry = InputFormatters.create_currency_entry(frame, textvariable=self.value_var, width=15)
        else:
            entry = ttk.Entry(frame, textvariable=self.value_var, width=15)

        entry.pack(side='left', padx=5)

        if unit:
            ttk.Label(frame, text=unit).pack(side='left')

        self.input_widget = entry

    def get_value(self) -> Optional[float]:
        """Get current value"""
        try:
            if self.kpi.get('type') == 'boolean':
                return float(self.bool_var.get())
            else:
                val = self.value_var.get()
                return float(val) if val else None
        except ValueError:
            return None

    def set_value(self, value: float):
        """Set value"""
        if self.kpi.get('type') == 'boolean':
            self.bool_var.set(value > 0)
            self.value_var.set("1" if value > 0 else "0")
        else:
            self.value_var.set(str(value))
            if hasattr(self, 'slider'):
                self.slider.set(value)

    def validate(self) -> bool:
        """Validate input"""
        value = self.get_value()
        if value is None:
            return False

        kpi_type = self.kpi.get('type')
        if kpi_type == 'percentage' and (value < 0 or value > 100):
            return False

        return True


class PrincipleKPIForm(ttk.Frame):
    """Form for all KPIs of a principle"""

    def __init__(self, parent, principle_id: str, manager: UNGCManagerEnhanced,
                 company_id: int, period: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.principle_id = principle_id
        self.manager = manager
        self.company_id = company_id
        self.period = period

        self.kpi_widgets: List[Tuple[str, KPIFormWidget]] = []
        self._create_form()

    def _create_form(self):
        """Create form for principle"""
        # Principle info
        principle_info = self.manager.get_principle_info(self.principle_id)
        if not principle_info:
            return

        # Header
        header = ttk.Label(
            self,
            text=f"Principle {self.principle_id}: {principle_info['title']}",
            font=('Helvetica', 12, 'bold')
        )
        header.pack(pady=10)

        # Description
        desc = ttk.Label(
            self,
            text=principle_info['description'],
            wraplength=600,
            justify='left'
        )
        desc.pack(pady=5)

        # Separator
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=10)

        # KPI forms in scrollable frame
        canvas = tk.Canvas(self, height=400)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Get KPIs for this principle
        kpis = self.manager.get_principle_kpis(self.principle_id)

        for kpi in kpis:
            # Create KPI widget
            kpi_widget = KPIFormWidget(scrollable_frame, kpi)
            kpi_widget.pack(fill='x', padx=20, pady=10)

            # Load existing value
            kpi_id = kpi['kpi_id']
            current_value = self.manager.get_kpi_data(
                self.company_id, kpi_id, self.period
            )
            if current_value is not None:
                kpi_widget.set_value(current_value)

            self.kpi_widgets.append((kpi_id, kpi_widget))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Save button
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Kaydet",
            command=self.save_data
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="İptal",
            command=self.clear_form
        ).pack(side='left', padx=5)

    def save_data(self):
        """Save all KPI data"""
        saved_count = 0
        errors = []

        for kpi_id, widget in self.kpi_widgets:
            if not widget.validate():
                errors.append(f"{kpi_id}: Geçersiz değer")
                continue

            value = widget.get_value()
            if value is not None:
                success = self.manager.save_kpi_data(
                    self.company_id,
                    kpi_id,
                    value,
                    self.period
                )
                if success:
                    saved_count += 1
                else:
                    errors.append(f"{kpi_id}: Kayıt hatası")

        if errors:
            messagebox.showwarning(
                "Uyarı",
                f"{saved_count} KPI kaydedildi.\n\nHatalar:\n" + "\n".join(errors)
            )
        else:
            messagebox.showinfo(
                "Başarılı",
                f"{saved_count} KPI başarıyla kaydedildi!"
            )

    def clear_form(self):
        """Clear form"""
        for _, widget in self.kpi_widgets:
            widget.value_var.set("")
            if hasattr(widget, 'bool_var'):
                widget.bool_var.set(False)


class UNGCKPIDataEntry(tk.Toplevel):
    """Main KPI data entry window"""

    def __init__(self, parent, db_path: str, company_id: int, period: Optional[str] = None):
        super().__init__(parent)
        self.db_path = db_path
        self.company_id = company_id
        self.period = period or str(datetime.now().year)

        self.manager = UNGCManagerEnhanced(db_path)

        self.title(f"UNGC KPI Data Entry - Period: {self.period}")
        self.geometry("900x700")

        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        # Top frame - principle selector
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(top_frame, text="İlke Seçin:", font=('Helvetica', 10, 'bold')).pack(side='left', padx=5)

        # Principle dropdown
        principles = self.manager.config.get('principles', [])
        principle_options = [f"P{p['number']}: {p['title_tr']}" for p in principles]

        self.principle_var = tk.StringVar()
        principle_combo = ttk.Combobox(
            top_frame,
            textvariable=self.principle_var,
            values=principle_options,
            state='readonly',
            width=60
        )
        principle_combo.pack(side='left', padx=5)
        principle_combo.bind('<<ComboboxSelected>>', self._on_principle_selected)

        # Main content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Initial message
        ttk.Label(
            self.content_frame,
            text="Lütfen bir ilke seçin",
            font=('Helvetica', 12)
        ).pack(pady=50)

        # Bottom frame - overall score
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(
            bottom_frame,
            text="Genel Uyum Skorunu Göster",
            command=self._show_overall_score
        ).pack(side='left', padx=5)

        ttk.Button(
            bottom_frame,
            text="Kapat",
            command=self.destroy
        ).pack(side='right', padx=5)

    def _on_principle_selected(self, event=None):
        """When principle is selected"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Get selected principle
        selection = self.principle_var.get()
        if not selection:
            return

        # Extract principle ID (P1, P2, etc.)
        principle_id = selection.split(':')[0]

        # Create form
        form = PrincipleKPIForm(
            self.content_frame,
            principle_id,
            self.manager,
            self.company_id,
            self.period
        )
        form.pack(fill='both', expand=True)

    def _show_overall_score(self):
        """Show overall compliance score"""
        result = self.manager.calculate_overall_score(self.company_id, self.period)

        message = "UNGC Genel Uyum Skoru\n\n"
        message += f"Toplam Skor: {result['overall_score']}%\n"
        message += f"Seviye: {result['level']} {result['level_info']['badge']}\n\n"
        message += "Kategori Skorları:\n"

        for category, score in result['category_scores'].items():
            message += f"  {category}: {score}%\n"

        messagebox.showinfo("UNGC Uyum Skoru", message)


if __name__ == '__main__':
    # Test
    root = tk.Tk()
    root.withdraw()

    db_path = DB_PATH
    window = UNGCKPIDataEntry(root, db_path, company_id=1)

    root.mainloop()

