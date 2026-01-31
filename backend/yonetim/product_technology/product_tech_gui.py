import logging
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from .product_tech_manager import ProductTechManager
from config.icons import Icons


class ProductTechGUI:
    """Ürün ve Teknoloji Modülü GUI - AR-GE, Kalite, Güvenlik, Acil Durum"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.product_tech_manager = ProductTechManager()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f'Silent error in product_tech_gui.py: {str(e)}')

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Ürün ve Teknoloji modülü arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#e67e22', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="Ürün ve Teknoloji Modülü",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#e67e22')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Sol panel - Modül seçimi
        left_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Modül başlığı
        module_title = tk.Label(left_frame, text="Modüller", font=('Segoe UI', 12, 'bold'),
                               bg='white', fg='#e67e22')
        module_title.pack(pady=10)

        # Modül butonları
        button_frame = tk.Frame(left_frame, bg='white')
        button_frame.pack(fill='x', padx=10, pady=10)

        modules = [
            ("", "AR-GE ve İnovasyon", self.show_innovation),
            (Icons.STAR, "Kalite Yönetimi", self.show_quality),
            ("", "Dijital Güvenlik", self.show_security),
            ("", "Acil Durum Yönetimi", self.show_emergency)
        ]

        for icon, text, command in modules:
            btn = tk.Button(button_frame, text=f"{icon}  {text}",
                           font=('Segoe UI', 11), fg='white', bg='#e67e22',
                           relief='flat', bd=0, cursor='hand2', anchor='w',
                           command=command, padx=20, pady=8)
            btn.pack(fill='x', pady=2)

            # Hover efekti
            btn.bind('<Enter>', lambda e, b=btn: self.on_button_hover(b, True))
            btn.bind('<Leave>', lambda e, b=btn: self.on_button_hover(b, False))

        # Sağ panel - Detaylar
        right_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        # Detay başlığı
        self.detail_title = tk.Label(right_frame, text="Detaylar", font=('Segoe UI', 12, 'bold'),
                                    bg='white', fg='#e67e22')
        self.detail_title.pack(pady=10)

        # Detay içeriği
        self.detail_frame = tk.Frame(right_frame, bg='white')
        self.detail_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Ana Dashboard butonu kaldırıldı

    def on_button_hover(self, button, is_entering) -> None:
        """Buton hover efekti"""
        if is_entering:
            button.configure(bg='#f39c12')
        else:
            button.configure(bg='#e67e22')

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            self.show_summary()
        except Exception as e:
            logging.error(f"ProductTechGUI load_data hatası: {e}")
            import traceback
            traceback.print_exc()

    def show_summary(self) -> None:
        """Özet bilgileri göster"""
        # Mevcut detayları temizle
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        self.detail_title.config(text="Modül Özeti")

        # Özet bilgilerini al
        summary = self.product_tech_manager.get_all_metrics_summary(self.company_id)

        if not summary['has_data']:
            info_label = tk.Label(self.detail_frame,
                                 text="Henüz veri girilmemiş. Sol menüden bir modül seçerek veri girebilirsiniz.",
                                 font=('Segoe UI', 12), fg='#7f8c8d', bg='white')
            info_label.pack(expand=True)
            return

        # Özet kartları
        summary_frame = tk.Frame(self.detail_frame, bg='white')
        summary_frame.pack(fill='both', expand=True)

        # Modül durumları
        modules = [
            ("AR-GE ve İnovasyon", summary['innovation'], '#3498db'),
            ("Kalite Yönetimi", summary['quality'], '#2ecc71'),
            ("Dijital Güvenlik", summary['security'], '#9b59b6'),
            ("Acil Durum Yönetimi", summary['emergency'], '#e74c3c')
        ]

        for i, (name, data, color) in enumerate(modules):
            if data:
                card = tk.Frame(summary_frame, bg=color, relief='raised', bd=1)
                card.pack(fill='x', pady=5)

                title_label = tk.Label(card, text=name, font=('Segoe UI', 12, 'bold'),
                                     fg='white', bg=color)
                title_label.pack(pady=5)

                status_label = tk.Label(card, text="Veri Mevcut", font=('Segoe UI', 10),
                                      fg='white', bg=color)
                status_label.pack(pady=(0, 5))

    def show_innovation(self) -> None:
        """AR-GE ve İnovasyon modülünü göster"""
        self.clear_detail()
        self.detail_title.config(text="AR-GE ve İnovasyon")

        # Form oluştur
        form_frame = tk.Frame(self.detail_frame, bg='white')
        form_frame.pack(fill='both', expand=True)

        # Başlık
        title_label = tk.Label(form_frame, text="AR-GE ve İnovasyon Metrikleri",
                              font=('Segoe UI', 14, 'bold'), bg='white', fg='#e67e22')
        title_label.pack(pady=(0, 20))

        # Form alanları
        fields = [
            ("Ar-Ge Yatırım Oranı (%)", "rd_investment_ratio", "float"),
            ("Patent Başvuru Sayısı", "patent_applications", "int"),
            ("Eko-Tasarım Entegrasyonu", "ecodesign_integration", "bool"),
            ("LCA Uygulaması", "lca_implementation", "bool"),
            ("İnovasyon Bütçesi (TL)", "innovation_budget", "float"),
            ("Raporlama Dönemi", "reporting_period", "str")
        ]

        self.innovation_vars = {}

        for label_text, var_name, var_type in fields:
            field_frame = tk.Frame(form_frame, bg='white')
            field_frame.pack(fill='x', pady=5)

            tk.Label(field_frame, text=label_text, font=('Segoe UI', 11),
                    bg='white', fg='#2c3e50').pack(side='left', padx=(0, 10))

            if var_type == "bool":
                var = tk.BooleanVar()
                tk.Checkbutton(field_frame, variable=var, bg='white').pack(side='left')
            elif var_type == "str":
                var = tk.StringVar(value=datetime.now().year)
                tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11), width=20).pack(side='left')
            else:
                var = tk.StringVar()
                tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11), width=20).pack(side='left')

            self.innovation_vars[var_name] = var

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), font=('Segoe UI', 12, 'bold'),
                           bg='#27ae60', fg='white', relief='flat', bd=0,
                           command=self.save_innovation_metrics)
        save_btn.pack(pady=20)

    def save_innovation_metrics(self) -> None:
        """İnovasyon metriklerini kaydet"""
        try:
            rd_investment_ratio = float(self.innovation_vars['rd_investment_ratio'].get() or 0)
            patent_applications = int(self.innovation_vars['patent_applications'].get() or 0)
            ecodesign_integration = self.innovation_vars['ecodesign_integration'].get()
            lca_implementation = self.innovation_vars['lca_implementation'].get()
            innovation_budget = float(self.innovation_vars['innovation_budget'].get() or 0)
            reporting_period = self.innovation_vars['reporting_period'].get()

            success = self.product_tech_manager.save_innovation_metrics(
                self.company_id, rd_investment_ratio, patent_applications, ecodesign_integration,
                lca_implementation, innovation_budget, reporting_period
            )

            if success:
                messagebox.showinfo("Başarılı", "AR-GE metrikleri kaydedildi")
            else:
                messagebox.showerror("Hata", "AR-GE metrikleri kaydedilemedi")

        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri: {str(e)}")

    def show_quality(self) -> None:
        """Kalite Yönetimi modülünü göster"""
        self.clear_detail()
        self.detail_title.config(text="Kalite Yönetimi")

        # Form oluştur
        form_frame = tk.Frame(self.detail_frame, bg='white')
        form_frame.pack(fill='both', expand=True)

        # Başlık
        title_label = tk.Label(form_frame, text="Kalite Yönetimi Metrikleri",
                              font=('Segoe UI', 14, 'bold'), bg='white', fg='#e67e22')
        title_label.pack(pady=(0, 20))

        # Form alanları
        fields = [
            ("ISO 9001 Sertifikası", "iso9001_certified", "bool"),
            ("Müşteri Şikayet Oranı (%)", "customer_complaint_rate", "float"),
            ("Ürün Geri Çağırma Sayısı", "product_recall_count", "int"),
            ("NPS Skoru", "nps_score", "float"),
            ("Kalite Hata Oranı (%)", "quality_error_rate", "float"),
            ("Raporlama Dönemi", "reporting_period", "str")
        ]

        self.quality_vars = {}

        for label_text, var_name, var_type in fields:
            field_frame = tk.Frame(form_frame, bg='white')
            field_frame.pack(fill='x', pady=5)

            tk.Label(field_frame, text=label_text, font=('Segoe UI', 11),
                    bg='white', fg='#2c3e50').pack(side='left', padx=(0, 10))

            if var_type == "bool":
                var = tk.BooleanVar()
                tk.Checkbutton(field_frame, variable=var, bg='white').pack(side='left')
            elif var_type == "str":
                var = tk.StringVar(value=datetime.now().year)
                tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11), width=20).pack(side='left')
            else:
                var = tk.StringVar()
                tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11), width=20).pack(side='left')

            self.quality_vars[var_name] = var

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), font=('Segoe UI', 12, 'bold'),
                           bg='#27ae60', fg='white', relief='flat', bd=0,
                           command=self.save_quality_metrics)
        save_btn.pack(pady=20)

    def save_quality_metrics(self) -> None:
        """Kalite metriklerini kaydet"""
        try:
            iso9001_certified = self.quality_vars['iso9001_certified'].get()
            customer_complaint_rate = float(self.quality_vars['customer_complaint_rate'].get() or 0)
            product_recall_count = int(self.quality_vars['product_recall_count'].get() or 0)
            nps_score = float(self.quality_vars['nps_score'].get() or 0)
            quality_error_rate = float(self.quality_vars['quality_error_rate'].get() or 0)
            reporting_period = self.quality_vars['reporting_period'].get()

            success = self.product_tech_manager.save_quality_metrics(
                self.company_id, iso9001_certified, customer_complaint_rate, product_recall_count,
                nps_score, quality_error_rate, reporting_period
            )

            if success:
                messagebox.showinfo("Başarılı", "Kalite metrikleri kaydedildi")
            else:
                messagebox.showerror("Hata", "Kalite metrikleri kaydedilemedi")

        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri: {str(e)}")

    def show_security(self) -> None:
        """Dijital Güvenlik modülünü göster"""
        self.clear_detail()
        self.detail_title.config(text="Dijital Güvenlik")

        # Form oluştur
        form_frame = tk.Frame(self.detail_frame, bg='white')
        form_frame.pack(fill='both', expand=True)

        # Başlık
        title_label = tk.Label(form_frame, text="Dijital Güvenlik Metrikleri",
                              font=('Segoe UI', 14, 'bold'), bg='white', fg='#e67e22')
        title_label.pack(pady=(0, 20))

        # Form alanları
        fields = [
            ("ISO 27001 Sertifikası", "iso27001_certified", "bool"),
            ("Siber Güvenlik Eğitim Saati", "cybersecurity_training_hours", "int"),
            ("Veri İhlali Sayısı", "data_breach_count", "int"),
            ("Dijital Dönüşüm Skoru", "digital_transformation_score", "float"),
            ("AI Uygulama Sayısı", "ai_applications_count", "int"),
            ("Raporlama Dönemi", "reporting_period", "str")
        ]

        self.security_vars = {}

        for label_text, var_name, var_type in fields:
            field_frame = tk.Frame(form_frame, bg='white')
            field_frame.pack(fill='x', pady=5)

            tk.Label(field_frame, text=label_text, font=('Segoe UI', 11),
                    bg='white', fg='#2c3e50').pack(side='left', padx=(0, 10))

            if var_type == "bool":
                var = tk.BooleanVar()
                tk.Checkbutton(field_frame, variable=var, bg='white').pack(side='left')
            elif var_type == "str":
                var = tk.StringVar(value=datetime.now().year)
                tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11), width=20).pack(side='left')
            else:
                var = tk.StringVar()
                tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11), width=20).pack(side='left')

            self.security_vars[var_name] = var

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), font=('Segoe UI', 12, 'bold'),
                           bg='#27ae60', fg='white', relief='flat', bd=0,
                           command=self.save_security_metrics)
        save_btn.pack(pady=20)

    def save_security_metrics(self) -> None:
        """Dijital güvenlik metriklerini kaydet"""
        try:
            iso27001_certified = self.security_vars['iso27001_certified'].get()
            cybersecurity_training_hours = int(self.security_vars['cybersecurity_training_hours'].get() or 0)
            data_breach_count = int(self.security_vars['data_breach_count'].get() or 0)
            digital_transformation_score = float(self.security_vars['digital_transformation_score'].get() or 0)
            ai_applications_count = int(self.security_vars['ai_applications_count'].get() or 0)
            reporting_period = self.security_vars['reporting_period'].get()

            success = self.product_tech_manager.save_digital_security_metrics(
                self.company_id, iso27001_certified, cybersecurity_training_hours, data_breach_count,
                digital_transformation_score, ai_applications_count, reporting_period
            )

            if success:
                messagebox.showinfo("Başarılı", "Dijital güvenlik metrikleri kaydedildi")
            else:
                messagebox.showerror("Hata", "Dijital güvenlik metrikleri kaydedilemedi")

        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri: {str(e)}")

    def show_emergency(self) -> None:
        """Acil Durum Yönetimi modülünü göster"""
        self.clear_detail()
        self.detail_title.config(text="Acil Durum Yönetimi")

        # Form oluştur
        form_frame = tk.Frame(self.detail_frame, bg='white')
        form_frame.pack(fill='both', expand=True)

        # Başlık
        title_label = tk.Label(form_frame, text="Acil Durum Yönetimi Metrikleri",
                              font=('Segoe UI', 14, 'bold'), bg='white', fg='#e67e22')
        title_label.pack(pady=(0, 20))

        # Form alanları
        fields = [
            ("İş Sürekliliği Planı", "business_continuity_plan", "bool"),
            ("Acil Durum Tatbikat Sıklığı", "emergency_drill_frequency", "int"),
            ("Risk Değerlendirme Skoru", "risk_assessment_score", "float"),
            ("Kriz Yönetim Ekibi", "crisis_management_team", "bool"),
            ("Sigorta Kapsam Skoru", "insurance_coverage_score", "float"),
            ("Raporlama Dönemi", "reporting_period", "str")
        ]

        self.emergency_vars = {}

        for label_text, var_name, var_type in fields:
            field_frame = tk.Frame(form_frame, bg='white')
            field_frame.pack(fill='x', pady=5)

            tk.Label(field_frame, text=label_text, font=('Segoe UI', 11),
                    bg='white', fg='#2c3e50').pack(side='left', padx=(0, 10))

            if var_type == "bool":
                var = tk.BooleanVar()
                tk.Checkbutton(field_frame, variable=var, bg='white').pack(side='left')
            elif var_type == "str":
                var = tk.StringVar(value=datetime.now().year)
                tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11), width=20).pack(side='left')
            else:
                var = tk.StringVar()
                tk.Entry(field_frame, textvariable=var, font=('Segoe UI', 11), width=20).pack(side='left')

            self.emergency_vars[var_name] = var

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("btn_save", "Kaydet"), font=('Segoe UI', 12, 'bold'),
                           bg='#27ae60', fg='white', relief='flat', bd=0,
                           command=self.save_emergency_metrics)
        save_btn.pack(pady=20)

    def save_emergency_metrics(self) -> None:
        """Acil durum metriklerini kaydet"""
        try:
            business_continuity_plan = self.emergency_vars['business_continuity_plan'].get()
            emergency_drill_frequency = int(self.emergency_vars['emergency_drill_frequency'].get() or 0)
            risk_assessment_score = float(self.emergency_vars['risk_assessment_score'].get() or 0)
            crisis_management_team = self.emergency_vars['crisis_management_team'].get()
            insurance_coverage_score = float(self.emergency_vars['insurance_coverage_score'].get() or 0)
            reporting_period = self.emergency_vars['reporting_period'].get()

            success = self.product_tech_manager.save_emergency_metrics(
                self.company_id, business_continuity_plan, emergency_drill_frequency, risk_assessment_score,
                crisis_management_team, insurance_coverage_score, reporting_period
            )

            if success:
                messagebox.showinfo("Başarılı", "Acil durum metrikleri kaydedildi")
            else:
                messagebox.showerror("Hata", "Acil durum metrikleri kaydedilemedi")

        except ValueError as e:
            messagebox.showerror("Hata", f"Geçersiz veri: {str(e)}")

    def clear_detail(self) -> None:
        """Detay alanını temizle"""
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

    # go_to_dashboard fonksiyonu kaldırıldı
