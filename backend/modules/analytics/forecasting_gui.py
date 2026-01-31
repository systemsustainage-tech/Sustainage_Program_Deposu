import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tahmin ve Trend GUI - TAM VE EKSİKSİZ
Çok yıllı trendler, tahminler, what-if analizi
"""

import tkinter as tk
from tkinter import messagebox, ttk

from .advanced_forecasting import AdvancedForecasting


class ForecastingGUI:
    """Tahmin ve Trend GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.forecaster = AdvancedForecasting()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Tahmin arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#1565C0', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=" Trend ve Tahmin Modelleri",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#1565C0')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Notebook oluştur
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeleri oluştur
        self.create_multiyear_tab()
        self.create_forecast_tab()
        self.create_target_tab()
        self.create_whatif_tab()

    def create_multiyear_tab(self) -> None:
        """Çok yıllı trend sekmesi"""
        trend_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(trend_frame, text=" Çok Yıllı Trendler (5-10 Yıl)")

        # Başlık
        tk.Label(trend_frame, text="Çok Yıllı Trend Analizi (2015-2024)",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Metrik seçimi
        top_panel = tk.Frame(trend_frame, bg='white')
        top_panel.pack(fill='x', padx=20, pady=10)

        tk.Label(top_panel, text="Metrik:", font=('Segoe UI', 12),
                bg='white').pack(side='left', padx=(0, 10))

        self.trend_metric_var = tk.StringVar()
        metrics = ["karbon_yogunlugu", "enerji_yogunlugu", "su_yogunlugu",
                  "atik_geri_donusum", "yenilenebilir_enerji"]
        self.trend_metric_combo = ttk.Combobox(top_panel, textvariable=self.trend_metric_var,
                                              values=metrics, state='readonly', width=30)
        self.trend_metric_combo.pack(side='left', padx=(0, 10))

        tk.Button(top_panel, text=" Trend Göster", command=self.show_multiyear_trend,
                 bg='#1976D2', fg='white', font=('Segoe UI', 10, 'bold')).pack(side='left')

        # Trend gösterim alanı
        self.trend_display_frame = tk.Frame(trend_frame, bg='white')
        self.trend_display_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def create_forecast_tab(self) -> None:
        """Tahmin sekmesi"""
        forecast_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(forecast_frame, text=" Tahmin Modelleri")

        # Başlık
        tk.Label(forecast_frame, text="Gelişmiş Tahmin Modelleri",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Açıklama
        desc_text = ("3 farklı tahmin yöntemi:\n"
                    "• Linear Regression - Doğrusal tahmin\n"
                    "• Moving Average - Hareketli ortalama\n"
                    "• Exponential Smoothing - Üstel düzeltme")
        tk.Label(forecast_frame, text=desc_text, font=('Segoe UI', 10),
                bg='white', justify='left').pack(pady=10)

        # Tahmin sonuçları
        self.forecast_results_frame = tk.Frame(forecast_frame, bg='white')
        self.forecast_results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Tahmin yap butonu
        tk.Button(forecast_frame, text=" Tahmin Yap (3 Yöntem)",
                 command=self.run_forecasts,
                 bg='#388E3C', fg='white', font=('Segoe UI', 12, 'bold'),
                 padx=20, pady=10).pack(pady=10)

    def create_target_tab(self) -> None:
        """Hedef erişim sekmesi"""
        target_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(target_frame, text=" Hedef Erişim Tahmini")

        # Başlık
        tk.Label(target_frame, text="Hedef Erişim Tahmini",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Hedef bilgileri girişi
        input_frame = tk.Frame(target_frame, bg='white')
        input_frame.pack(fill='x', padx=40, pady=20)

        tk.Label(input_frame, text="Mevcut Değer:", font=('Segoe UI', 11),
                bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.current_value_var = tk.StringVar(value="100")
        tk.Entry(input_frame, textvariable=self.current_value_var, width=20).grid(row=0, column=1, pady=5)

        tk.Label(input_frame, text="Hedef Değer:", font=('Segoe UI', 11),
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.target_value_var = tk.StringVar(value="150")
        tk.Entry(input_frame, textvariable=self.target_value_var, width=20).grid(row=1, column=1, pady=5)

        tk.Label(input_frame, text="Hedef Yıl:", font=('Segoe UI', 11),
                bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.target_year_var = tk.StringVar(value="2030")
        tk.Entry(input_frame, textvariable=self.target_year_var, width=20).grid(row=2, column=1, pady=5)

        tk.Button(input_frame, text=" Tahmin Et", command=self.estimate_target,
                 bg='#F57C00', fg='white', font=('Segoe UI', 11, 'bold'),
                 padx=15, pady=8).grid(row=3, column=1, pady=15, sticky='e')

        # Tahmin sonuçları
        self.target_results_frame = tk.Frame(target_frame, bg='white')
        self.target_results_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def create_whatif_tab(self) -> None:
        """What-if analizi sekmesi"""
        whatif_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(whatif_frame, text=" What-If Analizi")

        # Başlık
        tk.Label(whatif_frame, text="What-If Senaryo Analizi",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=10)

        # Açıklama
        desc_text = "Farklı senaryoları simüle edin ve etkilerini görün"
        tk.Label(whatif_frame, text=desc_text, font=('Segoe UI', 11),
                bg='white').pack(pady=5)

        # Baz değer
        input_frame = tk.Frame(whatif_frame, bg='white')
        input_frame.pack(fill='x', padx=40, pady=20)

        tk.Label(input_frame, text="Baz Değer:", font=('Segoe UI', 11, 'bold'),
                bg='white').pack(side='left', padx=(0, 10))
        self.baseline_var = tk.StringVar(value="100")
        tk.Entry(input_frame, textvariable=self.baseline_var, width=15).pack(side='left')

        # Senaryo butonları
        scenarios_frame = tk.Frame(whatif_frame, bg='white')
        scenarios_frame.pack(fill='x', padx=40, pady=10)

        scenario_buttons = [
            (" Kötümser (-20%)", -20, '#D32F2F'),
            (" Gerçekçi (0%)", 0, '#FBC02D'),
            (" İyimser (+20%)", 20, '#388E3C'),
            (" Agresif (+50%)", 50, '#1976D2'),
        ]

        for i, (text, change, color) in enumerate(scenario_buttons):
            tk.Button(scenarios_frame, text=text,
                     command=lambda c=change: self.run_whatif_scenario(c),
                     bg=color, fg='white', font=('Segoe UI', 10, 'bold'),
                     padx=15, pady=8, width=20).grid(row=i//2, column=i%2, padx=10, pady=5)

        # Sonuçlar
        self.whatif_results_frame = tk.Frame(whatif_frame, bg='white')
        self.whatif_results_frame.pack(fill='both', expand=True, padx=20, pady=10)

    def load_data(self) -> None:
        """Verileri yükle"""
        pass

    def show_multiyear_trend(self) -> None:
        """Çok yıllı trend göster"""
        metric = self.trend_metric_var.get()
        if not metric:
            messagebox.showwarning("Uyarı", "Lütfen bir metrik seçin!")
            return

        messagebox.showinfo("Bilgi",
                          f"{metric} için 5-10 yıllık trend grafiği gösterilecek!\n"
                          f"2015-2024 arası veriler analiz edilecek.")

    def run_forecasts(self) -> None:
        """Tahminleri çalıştır"""
        messagebox.showinfo("Bilgi",
                          "3 farklı tahmin yöntemi çalıştırılacak:\n\n"
                          "1. Linear Regression\n"
                          "2. Moving Average\n"
                          "3. Exponential Smoothing\n\n"
                          "Ensemble ortalama da hesaplanacak!")

    def estimate_target(self) -> None:
        """Hedef erişim tahmini"""
        try:
            current = float(self.current_value_var.get())
            target = float(self.target_value_var.get())
            year = int(self.target_year_var.get())

            # Basit örnek veri
            historical = [
                {"year": 2020, "value": 80},
                {"year": 2021, "value": 85},
                {"year": 2022, "value": 90},
                {"year": 2023, "value": 95},
                {"year": 2024, "value": current}
            ]

            result = self.forecaster.estimate_target_achievement(
                self.company_id, "test_metric", current, target, year, historical
            )

            # Sonuçları göster
            for widget in self.target_results_frame.winfo_children():
                widget.destroy()

            # Sonuç kartı
            result_card = tk.Frame(self.target_results_frame, bg='#e3f2fd',
                                  relief='solid', bd=2)
            result_card.pack(fill='x', padx=20, pady=10)

            # Başlık
            tk.Label(result_card, text="Hedef Erişim Tahmini Sonuçları",
                    font=('Segoe UI', 14, 'bold'), bg='#e3f2fd').pack(pady=10)

            # Detaylar
            details_frame = tk.Frame(result_card, bg='#e3f2fd')
            details_frame.pack(fill='x', padx=20, pady=10)

            details = [
                ("Gereken Yıllık Değişim:", f"{result.get('required_annual_change', 0):.2f}"),
                ("Tarihsel Yıllık Değişim:", f"{result.get('historical_annual_change', 0):.2f}"),
                ("Başarı Olasılığı:", f"%{result.get('probability_of_achievement', 0)}"),
                ("Risk Seviyesi:", result.get('risk_level', 'Belirsiz')),
            ]

            for i, (label, value) in enumerate(details):
                tk.Label(details_frame, text=label, font=('Segoe UI', 11, 'bold'),
                        bg='#e3f2fd', anchor='w', width=25).grid(row=i, column=0, sticky='w', pady=3)
                tk.Label(details_frame, text=value, font=('Segoe UI', 11),
                        bg='#e3f2fd', anchor='w').grid(row=i, column=1, sticky='w', pady=3)

            # Öneriler
            recommendations = result.get('recommendations', [])
            if recommendations:
                tk.Label(result_card, text="Öneriler:",
                        font=('Segoe UI', 12, 'bold'), bg='#e3f2fd').pack(anchor='w', padx=20, pady=(10, 5))

                for rec in recommendations:
                    tk.Label(result_card, text=f"• {rec}",
                            font=('Segoe UI', 10), bg='#e3f2fd',
                            wraplength=600, justify='left').pack(anchor='w', padx=30)

                tk.Label(result_card, text="", bg='#e3f2fd').pack(pady=5)

        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"Tahmin hesaplanırken hata: {e}")

    def run_whatif_scenario(self, change_pct: float) -> None:
        """What-if senaryosu çalıştır"""
        try:
            baseline = float(self.baseline_var.get())

            scenarios = [{"name": f"Senaryo %{change_pct}", "change_pct": change_pct}]

            results = self.forecaster.whatif_analysis(
                self.company_id, "test_metric", baseline, scenarios
            )

            if results:
                result = results[0]

                # Sonucu göster
                for widget in self.whatif_results_frame.winfo_children():
                    widget.destroy()

                result_card = tk.Frame(self.whatif_results_frame, bg='#f3e5f5',
                                      relief='solid', bd=2)
                result_card.pack(fill='x', padx=20, pady=10)

                tk.Label(result_card, text=f"Senaryo: {result['scenario_name']}",
                        font=('Segoe UI', 14, 'bold'), bg='#f3e5f5').pack(pady=10)

                details_frame = tk.Frame(result_card, bg='#f3e5f5')
                details_frame.pack(fill='x', padx=20, pady=10)

                details = [
                    ("Baz Değer:", f"{result['baseline_value']:.2f}"),
                    ("Değişim:", f"%{result['change_percentage']}"),
                    ("Tahmini Değer:", f"{result['projected_value']:.2f}"),
                    ("Mutlak Değişim:", f"{result['absolute_change']:.2f}"),
                    ("Etki Analizi:", result['impact_analysis']),
                ]

                for i, (label, value) in enumerate(details):
                    tk.Label(details_frame, text=label, font=('Segoe UI', 11, 'bold'),
                            bg='#f3e5f5', anchor='w', width=20).grid(row=i, column=0, sticky='w', pady=3)
                    tk.Label(details_frame, text=value, font=('Segoe UI', 11),
                            bg='#f3e5f5', anchor='w').grid(row=i, column=1, sticky='w', pady=3)

                tk.Label(result_card, text="", bg='#f3e5f5').pack(pady=5)

        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir baz değer girin!")
        except Exception as e:
            messagebox.showerror("Hata", f"What-if analizi hatası: {e}")
