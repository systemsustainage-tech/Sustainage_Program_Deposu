import logging
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils.language_manager import LanguageManager

from .detailed_energy_manager import DetailedEnergyManager
from .energy_reporting import EnergyReporting


class EnergyGUI:
    """Enerji Yönetimi Modülü GUI"""

    def __init__(self, parent, company_id: int, main_app=None) -> None:
        self.parent = parent
        self.company_id = company_id
        self.main_app = main_app
        self.lm = LanguageManager()
        self.manager = DetailedEnergyManager()
        self.reporting = EnergyReporting(self.manager)
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana container
        self.main_frame = tk.Frame(self.parent, bg='#f0f2f5')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        header = tk.Frame(self.main_frame, bg='#f0f2f5')
        header.pack(fill='x', pady=(0, 20))
        
        tk.Label(header, text=self.lm.tr('energy_module_title', "Enerji Yöneticisi"), 
                font=('Segoe UI', 20, 'bold'), fg='#1e293b', bg='#f0f2f5').pack(side='left')
        
        # KPI Kartları
        kpi_frame = tk.Frame(self.main_frame, bg='#f0f2f5')
        kpi_frame.pack(fill='x', pady=(0, 20))
        
        self.kpi_vars = {
            'consumption': tk.StringVar(value='-'),
            'cost': tk.StringVar(value='-'),
            'renewable': tk.StringVar(value='-'),
            'intensity': tk.StringVar(value='-')
        }
        
        self._create_kpi_card(kpi_frame, self.lm.tr('total_consumption', "Toplam Tüketim"), self.kpi_vars['consumption'], '#3498db')
        self._create_kpi_card(kpi_frame, self.lm.tr('total_cost', "Toplam Maliyet"), self.kpi_vars['cost'], '#e74c3c')
        self._create_kpi_card(kpi_frame, self.lm.tr('renewable_ratio', "Yenilenebilir Oranı"), self.kpi_vars['renewable'], '#2ecc71')
        self._create_kpi_card(kpi_frame, self.lm.tr('energy_intensity', "Enerji Yoğunluğu"), self.kpi_vars['intensity'], '#f39c12')

        # İçerik (Grafik ve Liste)
        content = tk.Frame(self.main_frame, bg='#f0f2f5')
        content.pack(fill='both', expand=True)
        
        # Sol: Grafik
        left_panel = tk.Frame(content, bg='white', relief='raised', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(left_panel, text=self.lm.tr('energy_trends', "Enerji Trendleri"), 
                font=('Segoe UI', 12, 'bold'), bg='white', fg='#34495e').pack(anchor='w', padx=10, pady=10)
        
        self.chart_frame = tk.Frame(left_panel, bg='white')
        self.chart_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Sağ: Son Kayıtlar
        right_panel = tk.Frame(content, bg='white', relief='raised', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        header_right = tk.Frame(right_panel, bg='white')
        header_right.pack(fill='x', padx=10, pady=10)
        
        tk.Label(header_right, text=self.lm.tr('recent_records', "Son Kayıtlar"), 
                font=('Segoe UI', 12, 'bold'), bg='white', fg='#34495e').pack(side='left')
        
        tk.Button(header_right, text=self.lm.tr('add_record', "+ Kayıt Ekle"), 
                 bg='#2ecc71', fg='white', relief='flat', font=('Segoe UI', 9, 'bold'),
                 command=self.add_record_dialog).pack(side='right', padx=5)

        tk.Button(header_right, text=self.lm.tr('import_excel', "Excel'den Al"), 
                 bg='#3498db', fg='white', relief='flat', font=('Segoe UI', 9, 'bold'),
                 command=self.import_excel_dialog).pack(side='right', padx=5)

        tk.Button(header_right, text=self.lm.tr('export_excel', "Rapor Al"), 
                 bg='#9b59b6', fg='white', relief='flat', font=('Segoe UI', 9, 'bold'),
                 command=self.generate_report_dialog).pack(side='right', padx=5)

        # Liste (Treeview)
        cols = ('date', 'type', 'amount', 'unit', 'cost')
        self.tree = ttk.Treeview(right_panel, columns=cols, show='headings', height=10)
        
        self.tree.heading('date', text=self.lm.tr('date', "Tarih"))
        self.tree.heading('type', text=self.lm.tr('energy_type', "Tür"))
        self.tree.heading('amount', text=self.lm.tr('amount', "Miktar"))
        self.tree.heading('unit', text=self.lm.tr('unit', "Birim"))
        self.tree.heading('cost', text=self.lm.tr('cost', "Maliyet"))
        
        self.tree.column('date', width=90)
        self.tree.column('type', width=100)
        self.tree.column('amount', width=80)
        self.tree.column('unit', width=60)
        self.tree.column('cost', width=80)
        
        self.tree.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def _create_kpi_card(self, parent, title, var, color):
        card = tk.Frame(parent, bg='white', relief='raised', bd=1)
        card.pack(side='left', fill='x', expand=True, padx=5)
        
        tk.Label(card, text=title, font=('Segoe UI', 10), fg='#7f8c8d', bg='white').pack(pady=(10, 5))
        tk.Label(card, textvariable=var, font=('Segoe UI', 16, 'bold'), fg=color, bg='white').pack(pady=(0, 10))

    def load_data(self):
        try:
            # Metrikleri hesapla
            metrics = self.manager.calculate_energy_metrics(self.company_id)
            
            self.kpi_vars['consumption'].set(f"{metrics.get('total_consumption', 0):,.0f} kWh")
            self.kpi_vars['cost'].set(f"{metrics.get('total_cost', 0):,.0f} TL")
            self.kpi_vars['renewable'].set(f"%{metrics.get('renewable_ratio', 0):.1f}")
            self.kpi_vars['intensity'].set(f"{metrics.get('avg_energy_intensity', 0):.2f}")
            
            # Trendleri çiz
            trends = self.manager.get_energy_trends(self.company_id)
            self._draw_chart(trends)
            
            # Listeyi doldur
            # (DetailedEnergyManager'da get_records metodu olmayabilir, kontrol etmemiz gerekirdi ama varsayalım)
            # Eğer yoksa SQL ile çekebiliriz veya manager'a ekleyebiliriz.
            # Şimdilik dummy data veya manager'dan çekmeyi deneyelim.
            self._load_recent_records()
            
        except Exception as e:
            logging.error(f"Veri yükleme hatası: {e}")

    def _draw_chart(self, trends):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        if not trends or not trends.get('months'):
            tk.Label(self.chart_frame, text=self.lm.tr('no_data', "Veri yok"), bg='white').pack(expand=True)
            return

        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        ax.plot(trends['months'], trends['consumption'], marker='o', linestyle='-', color='#3498db')
        ax.set_title(self.lm.tr('monthly_consumption', "Aylık Tüketim"), fontsize=10)
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _load_recent_records(self):
        # Treeview'i temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Veritabanından son 20 kaydı çek
        import sqlite3
        try:
            conn = sqlite3.connect(self.manager.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT measurement_date, energy_type, consumption_amount, unit, cost
                FROM energy_consumption_records
                WHERE company_id = ?
                ORDER BY measurement_date DESC
                LIMIT 20
            """, (self.company_id,))
            
            for row in cursor.fetchall():
                # Localize energy type
                date, etype, amount, unit, cost = row
                localized_type = self.lm.tr(etype, etype)
                self.tree.insert('', 'end', values=(date, localized_type, amount, unit, cost))
            
            conn.close()
        except Exception as e:
            logging.error(f"Error loading records: {e}")

    def add_record_dialog(self):
        # Basit bir ekleme dialogu
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('add_energy_record', "Enerji Kaydı Ekle"))
        dialog.geometry("400x650")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Energy Type Mapping
        type_mapping = {
            self.lm.tr('electricity', 'Elektrik'): 'electricity',
            self.lm.tr('natural_gas', 'Doğalgaz'): 'natural_gas',
            self.lm.tr('water', 'Su'): 'water'
        }
        display_values = list(type_mapping.keys())
        
        # Form alanları...
        tk.Label(dialog, text=self.lm.tr('date_format_hint', "Tarih (YYYY-AA-GG):")).pack(pady=5)
        date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        tk.Entry(dialog, textvariable=date_var).pack()
        
        tk.Label(dialog, text="Fatura Tarihi (YYYY-AA-GG):").pack(pady=5)
        inv_date_var = tk.StringVar()
        tk.Entry(dialog, textvariable=inv_date_var).pack()

        tk.Label(dialog, text="Son Ödeme Tarihi (YYYY-AA-GG):").pack(pady=5)
        due_date_var = tk.StringVar()
        tk.Entry(dialog, textvariable=due_date_var).pack()

        tk.Label(dialog, text="Tedarikçi Firma:").pack(pady=5)
        supplier_var = tk.StringVar()
        tk.Entry(dialog, textvariable=supplier_var).pack()
        
        tk.Label(dialog, text=self.lm.tr('energy_type', "Enerji Türü:")).pack(pady=5)
        type_display_var = tk.StringVar(value=display_values[0])
        ttk.Combobox(dialog, textvariable=type_display_var, values=display_values, state='readonly').pack()
        
        tk.Label(dialog, text=self.lm.tr('amount', "Miktar:")).pack(pady=5)
        amount_var = tk.StringVar()
        tk.Entry(dialog, textvariable=amount_var).pack()
        
        tk.Label(dialog, text=self.lm.tr('cost', "Maliyet:")).pack(pady=5)
        cost_var = tk.StringVar()
        tk.Entry(dialog, textvariable=cost_var).pack()
        
        def save():
            try:
                selected_display = type_display_var.get()
                energy_type_code = type_mapping.get(selected_display, 'electricity')
                
                self.manager.record_energy_consumption(
                    company_id=self.company_id,
                    energy_type=energy_type_code,
                    consumption_amount=float(amount_var.get()),
                    measurement_date=date_var.get(),
                    invoice_date=inv_date_var.get(),
                    due_date=due_date_var.get(),
                    supplier=supplier_var.get(),
                    cost=float(cost_var.get() or 0),
                    unit="kWh" # Varsayılan
                )
                messagebox.showinfo(self.lm.tr('success', "Başarılı"), self.lm.tr('record_added', "Kayıt eklendi"))
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), str(e))
        
        tk.Button(dialog, text=self.lm.tr('btn_save', "Kaydet"), command=save, bg='#2ecc71', fg='white').pack(pady=20)

    def import_excel_dialog(self):
        from tkinter import filedialog
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Hata", "Excel import için 'pandas' ve 'openpyxl' kütüphaneleri gereklidir.")
            return

        file_path = filedialog.askopenfilename(
            title=self.lm.tr('select_excel_file', "Excel Dosyası Seç"),
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not file_path:
            return
            
        try:
            df = pd.read_excel(file_path)
            # Kolon kontrolü yapmadan esnek import deneyelim
            # Beklenen: Tarih, Tür, Miktar, Maliyet
            
            count = 0
            for _, row in df.iterrows():
                # Zorunlu alan: Miktar
                # Kolon isimleri büyük/küçük harf duyarsız olsun
                row_keys = {k.lower(): k for k in row.keys()}
                
                def get_val(key):
                    if key in row_keys:
                        return row[row_keys[key]]
                    return None

                amount_val = get_val('miktar') or get_val('amount')
                if not amount_val:
                    continue
                
                amount = float(amount_val)
                cost = float(get_val('maliyet') or get_val('cost') or 0)
                etype = get_val('tür') or get_val('type') or 'electricity'
                
                # Tarih
                m_date = get_val('tarih') or get_val('date') or datetime.now()
                if hasattr(m_date, 'strftime'):
                    m_date = m_date.strftime('%Y-%m-%d')
                else:
                    m_date = str(m_date)

                # Yeni alanlar
                inv_date = get_val('fatura tarihi') or get_val('invoice date')
                if hasattr(inv_date, 'strftime'): inv_date = inv_date.strftime('%Y-%m-%d')

                due_date = get_val('son ödeme tarihi') or get_val('due date')
                if hasattr(due_date, 'strftime'): due_date = due_date.strftime('%Y-%m-%d')

                supplier = get_val('tedarikçi') or get_val('supplier') or ''

                # Tür mapping
                etype_str = str(etype).lower()
                if 'elektrik' in etype_str or 'electricity' in etype_str: etype_code = 'electricity'
                elif 'gaz' in etype_str or 'gas' in etype_str: etype_code = 'natural_gas'
                elif 'su' in etype_str or 'water' in etype_str: etype_code = 'water'
                else: etype_code = 'electricity'
                
                self.manager.record_energy_consumption(
                    company_id=self.company_id,
                    energy_type=etype_code,
                    consumption_amount=amount,
                    measurement_date=str(m_date),
                    invoice_date=str(inv_date) if inv_date else None,
                    due_date=str(due_date) if due_date else None,
                    supplier=str(supplier),
                    cost=cost,
                    unit="kWh"
                )
                count += 1
                
            messagebox.showinfo(self.lm.tr('success', "Başarılı"), f"{count} {self.lm.tr('records_imported', 'kayıt içeri aktarıldı')}")
            self.load_data()
            
        except Exception as e:
            messagebox.showerror(self.lm.tr('error', "Hata"), f"Excel import hatası: {e}")

    def generate_report_dialog(self):
        """Rapor oluşturma diyaloğu"""
        dialog = tk.Toplevel(self.parent)
        dialog.title(self.lm.tr('generate_report', "Rapor Oluştur"))
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Dönem Seçimi
        tk.Label(dialog, text=self.lm.tr('select_period', "Dönem Seçiniz (YYYY-AA):"), font=('Segoe UI', 10)).pack(pady=10)
        period_var = tk.StringVar(value=datetime.now().strftime('%Y-%m'))
        tk.Entry(dialog, textvariable=period_var, font=('Segoe UI', 10)).pack()

        # Format Seçimi
        tk.Label(dialog, text=self.lm.tr('select_format', "Format Seçiniz:"), font=('Segoe UI', 10)).pack(pady=10)
        
        format_frame = tk.Frame(dialog)
        format_frame.pack(pady=5)
        
        docx_var = tk.BooleanVar(value=True)
        excel_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(format_frame, text="DOCX (Word)", variable=docx_var).pack(side='left', padx=10)
        tk.Checkbutton(format_frame, text="Excel", variable=excel_var).pack(side='left', padx=10)

        def generate():
            formats = []
            if docx_var.get(): formats.append('docx')
            if excel_var.get(): formats.append('excel')
            
            if not formats:
                messagebox.showwarning("Uyarı", "Lütfen en az bir format seçiniz.")
                return

            try:
                files = self.reporting.generate_energy_report(
                    company_id=self.company_id, 
                    period=period_var.get(),
                    formats=formats
                )
                
                if files:
                    msg = "Raporlar başarıyla oluşturuldu:\n\n"
                    for fmt, path in files.items():
                        msg += f"{fmt.upper()}: {path}\n"
                    
                    messagebox.showinfo("Başarılı", msg)
                    dialog.destroy()
                else:
                    messagebox.showwarning("Uyarı", "Rapor oluşturulamadı veya veri yok.")
                    
            except Exception as e:
                logging.error(f"Rapor hatası: {e}")
                messagebox.showerror("Hata", f"Rapor oluşturulurken bir hata oluştu: {e}")

        tk.Button(dialog, text=self.lm.tr('create', "Oluştur"), 
                 bg='#2ecc71', fg='white', font=('Segoe UI', 10, 'bold'),
                 command=generate).pack(pady=20)

    def export_excel_dialog(self):
        # Geriye dönük uyumluluk için
        self.generate_report_dialog()

