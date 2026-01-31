import logging
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

from .prioritization_manager import PrioritizationManager


class PrioritizationGUI:
    """Önceliklendirme Modülü GUI - Materyal konu analizi ve anket sistemi"""

    def __init__(self, parent, company_id: int) -> None:
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id
        self.prioritization_manager = PrioritizationManager()

        try:
            apply_theme(self.parent)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Önceliklendirme modülü arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#8e44ad', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr("prioritization_module_title", "Önceliklendirme Modülü - Materyal Konu Analizi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#8e44ad')
        title_label.pack(expand=True)

        # Ana içerik alanı
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Sol panel - Anket yönetimi
        left_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Anket yönetimi başlığı
        survey_title = tk.Label(left_frame, text=self.lm.tr("survey_management", "Anket Yönetimi"), font=('Segoe UI', 12, 'bold'),
                               bg='white', fg='#8e44ad')
        survey_title.pack(pady=10)

        # Anket butonları
        button_frame = tk.Frame(left_frame, bg='white')
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text=self.lm.tr("create_new_survey", "Yeni Anket Oluştur"), style='Primary.TButton',
                   command=self.create_survey).pack(fill='x', pady=2)
        ttk.Button(button_frame, text=self.lm.tr("create_default_survey", "Varsayılan Anket Oluştur"), style='Primary.TButton',
                   command=self.create_default_survey).pack(fill='x', pady=2)
        ttk.Button(button_frame, text=self.lm.tr("delete_selected_survey", "Seçili Anketi Sil"), style='Accent.TButton',
                   command=self.delete_survey).pack(fill='x', pady=2)

        # Anket listesi
        self.survey_listbox = tk.Listbox(left_frame, font=('Segoe UI', 10))
        self.survey_listbox.pack(fill='both', expand=True, padx=10, pady=10)
        self.survey_listbox.bind('<<ListboxSelect>>', self.on_survey_select)

        # Sağ panel - Anket detayları ve sonuçlar
        right_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

        # Detay başlığı
        self.detail_title = tk.Label(right_frame, text=self.lm.tr("survey_details", "Anket Detayları"), font=('Segoe UI', 12, 'bold'),
                                    bg='white', fg='#8e44ad')
        self.detail_title.pack(pady=10)

        # Detay içeriği
        self.detail_frame = tk.Frame(right_frame, bg='white')
        self.detail_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Notebook ekle - Sekmeli yapı
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Sekmeler
        self.create_survey_tab()
        self.create_stakeholder_matrix_tab()
        self.create_scoring_tab()
        self.create_results_tab()

    def create_survey_tab(self) -> None:
        """Anket sekmesi"""
        survey_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(survey_tab, text=f" {self.lm.tr('surveys_tab', 'Anketler')}")

        tk.Label(survey_tab, text=self.lm.tr("survey_management_desc", "Anket yönetimi ve analiz sistemi"),
                font=('Segoe UI', 10), bg='white').pack(pady=20)

    def create_stakeholder_matrix_tab(self) -> None:
        """Stakeholder öncelik matrisi sekmesi"""
        matrix_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(matrix_tab, text=f" {self.lm.tr('stakeholder_matrix_tab', 'Stakeholder Matrisi')}")

        # Başlık
        tk.Label(matrix_tab, text=f" {self.lm.tr('stakeholder_priority_matrix', 'Stakeholder Öncelik Matrisi')}",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        # Açıklama
        info_frame = tk.Frame(matrix_tab, bg='#e8f4f8', relief='solid', bd=1)
        info_frame.pack(fill='x', padx=20, pady=10)

        info_text = self.lm.tr("stakeholder_matrix_info", """
        Stakeholder öncelik matrisi, paydaşların önem ve etki düzeylerini 
        değerlendirerek materyal konuları belirlemenize yardımcı olur.
        """)
        tk.Label(info_frame, text=info_text, font=('Segoe UI', 10),
                bg='#e8f4f8', justify='left').pack(padx=10, pady=10)

        # Matris formu
        form_frame = tk.LabelFrame(matrix_tab, text=self.lm.tr("add_stakeholder_title", "Stakeholder Ekle"),
                                  font=('Segoe UI', 11, 'bold'), bg='white')
        form_frame.pack(fill='x', padx=20, pady=10)

        # Form alanları
        fields_frame = tk.Frame(form_frame, bg='white')
        fields_frame.pack(fill='x', padx=10, pady=10)

        # Stakeholder adı
        tk.Label(fields_frame, text=self.lm.tr("stakeholder_name_lbl", "Stakeholder Adı:"), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.stakeholder_name_entry = tk.Entry(fields_frame, width=30)
        self.stakeholder_name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Kategori
        tk.Label(fields_frame, text=self.lm.tr("category_lbl", "Kategori:"), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.stakeholder_category = ttk.Combobox(fields_frame, width=28, values=[
            "İç Paydaşlar", "Dış Paydaşlar", "Müşteriler", "Tedarikçiler",
            "Çalışanlar", "Yatırımcılar", "Sivil Toplum", "Kamu Otoriteleri"
        ])
        self.stakeholder_category.grid(row=1, column=1, padx=10, pady=5)

        # Etki Düzeyi
        tk.Label(fields_frame, text=self.lm.tr("impact_level_lbl", "Etki Düzeyi (1-5):"), bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.impact_level = ttk.Combobox(fields_frame, width=28, values=["1", "2", "3", "4", "5"])
        self.impact_level.grid(row=2, column=1, padx=10, pady=5)

        # Önem Düzeyi
        tk.Label(fields_frame, text=self.lm.tr("importance_level_lbl", "Önem Düzeyi (1-5):"), bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.importance_level = ttk.Combobox(fields_frame, width=28, values=["1", "2", "3", "4", "5"])
        self.importance_level.grid(row=3, column=1, padx=10, pady=5)

        # Ekle butonu
        add_btn = tk.Button(form_frame, text=f" {self.lm.tr('add_btn', 'Ekle')}", font=('Segoe UI', 10),
                          bg='#27ae60', fg='white', relief='flat',
                          command=self.add_stakeholder)
        add_btn.pack(pady=10)

        # Stakeholder listesi
        list_frame = tk.LabelFrame(matrix_tab, text=self.lm.tr("stakeholder_list_title", "Stakeholder Listesi"),
                                  font=('Segoe UI', 11, 'bold'), bg='white')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Treeview
        columns = ("Stakeholder", "Kategori", "Etki", "Önem", "Öncelik")
        self.stakeholder_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Localize headers
        headers = {
            "Stakeholder": self.lm.tr("col_stakeholder", "Stakeholder"),
            "Kategori": self.lm.tr("col_category", "Kategori"),
            "Etki": self.lm.tr("col_impact", "Etki"),
            "Önem": self.lm.tr("col_importance", "Önem"),
            "Öncelik": self.lm.tr("col_priority", "Öncelik")
        }

        for col in columns:
            self.stakeholder_tree.heading(col, text=headers.get(col, col))
            self.stakeholder_tree.column(col, width=120)

        self.stakeholder_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.stakeholder_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.stakeholder_tree.configure(yscrollcommand=scrollbar.set)

        # Butonlar
        btn_frame = tk.Frame(list_frame, bg='white')
        btn_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(btn_frame, text=f" {self.lm.tr('view_matrix_btn', 'Matrisi Görüntüle')}", bg='#3498db', fg='white',
                 command=self.show_matrix_visualization).pack(side='left', padx=5)
        tk.Button(btn_frame, text=f"️ {self.lm.tr('delete_selected_btn', 'Seçili Sil')}", bg='#e74c3c', fg='white',
                 command=self.delete_stakeholder).pack(side='left', padx=5)

    def create_scoring_tab(self) -> None:
        """Skorlama sistemi sekmesi"""
        scoring_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(scoring_tab, text=f" {self.lm.tr('scoring_tab', 'Skorlama')}")

        # Başlık
        tk.Label(scoring_tab, text=f" {self.lm.tr('material_topic_scoring_system', 'Materyal Konu Skorlama Sistemi')}",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        # Skorlama kriterleri
        criteria_frame = tk.LabelFrame(scoring_tab, text=self.lm.tr("scoring_criteria_title", "Skorlama Kriterleri"),
                                      font=('Segoe UI', 11, 'bold'), bg='white')
        criteria_frame.pack(fill='x', padx=20, pady=10)

        criteria_text = self.lm.tr("scoring_formula_info", """
         Skorlama Formülü:
        
        Öncelik Skoru = (Stakeholder Etkisi × 0.4) + (İş Etkisi × 0.3) + (Sürdürülebilirlik Etkisi × 0.3)
        
        1-5 Skala:
        • 1 = Çok Düşük
        • 2 = Düşük
        • 3 = Orta
        • 4 = Yüksek
        • 5 = Çok Yüksek
        
        Öncelik Sınıflandırması:
        • 4.0-5.0 = Kritik (Yüksek Öncelik)
        • 3.0-3.9 = Önemli (Orta Öncelik)
        • 2.0-2.9 = Takip Edilmeli (Düşük Öncelik)
        • 1.0-1.9 = İzlenebilir (Minimum Öncelik)
        """)

        tk.Label(criteria_frame, text=criteria_text, font=('Segoe UI', 9),
                bg='white', justify='left').pack(padx=15, pady=10)

        # Materyal konu ekleme
        topic_frame = tk.LabelFrame(scoring_tab, text=self.lm.tr("add_material_topic_title", "Materyal Konu Ekle"),
                                   font=('Segoe UI', 11, 'bold'), bg='white')
        topic_frame.pack(fill='x', padx=20, pady=10)

        input_frame = tk.Frame(topic_frame, bg='white')
        input_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(input_frame, text=self.lm.tr("topic_name_lbl", "Konu Adı:"), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.topic_name_entry = tk.Entry(input_frame, width=40)
        self.topic_name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(input_frame, text=self.lm.tr("stakeholder_impact_lbl", "Stakeholder Etkisi (1-5):"), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.topic_stakeholder_impact = ttk.Combobox(input_frame, width=38, values=["1", "2", "3", "4", "5"])
        self.topic_stakeholder_impact.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(input_frame, text=self.lm.tr("business_impact_lbl", "İş Etkisi (1-5):"), bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.topic_business_impact = ttk.Combobox(input_frame, width=38, values=["1", "2", "3", "4", "5"])
        self.topic_business_impact.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(input_frame, text=self.lm.tr("sustainability_impact_lbl", "Sürdürülebilirlik Etkisi (1-5):"), bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.topic_sustainability_impact = ttk.Combobox(input_frame, width=38, values=["1", "2", "3", "4", "5"])
        self.topic_sustainability_impact.grid(row=3, column=1, padx=10, pady=5)

        # Hesapla ve ekle butonu
        tk.Button(topic_frame, text=f" {self.lm.tr('calculate_add_btn', 'Hesapla ve Ekle')}", font=('Segoe UI', 10),
                 bg='#27ae60', fg='white', relief='flat',
                 command=self.calculate_and_add_topic).pack(pady=10)

        # Materyal konular listesi
        results_frame = tk.LabelFrame(scoring_tab, text=self.lm.tr("material_topics_priority_list", "Materyal Konular - Öncelik Sıralaması"),
                                     font=('Segoe UI', 11, 'bold'), bg='white')
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Treeview
        columns = ("Konu", "Stakeholder", "İş", "Sürdürülebilirlik", "Skor", "Öncelik")
        self.topics_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        # Localize headers
        headers = {
            "Konu": self.lm.tr("col_topic", "Konu"),
            "Stakeholder": self.lm.tr("col_stakeholder", "Stakeholder"),
            "İş": self.lm.tr("col_business", "İş"),
            "Sürdürülebilirlik": self.lm.tr("col_sustainability", "Sürdürülebilirlik"),
            "Skor": self.lm.tr("col_score", "Skor"),
            "Öncelik": self.lm.tr("col_priority", "Öncelik")
        }

        for col in columns:
            self.topics_tree.heading(col, text=headers.get(col, col))
            width = 150 if col == "Konu" else 100
            self.topics_tree.column(col, width=width)

        self.topics_tree.pack(fill='both', expand=True, padx=10, pady=10)

    def create_results_tab(self) -> None:
        """Sonuçlar ve raporlama sekmesi"""
        results_tab = tk.Frame(self.notebook, bg='white')
        self.notebook.add(results_tab, text=f" {self.lm.tr('results_tab', 'Sonuçlar')}")

        tk.Label(results_tab, text=f" {self.lm.tr('prioritization_results_reports', 'Önceliklendirme Sonuçları ve Raporlar')}",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        # Özet kartlar
        summary_frame = tk.Frame(results_tab, bg='white')
        summary_frame.pack(fill='x', padx=20, pady=10)

        # Kart oluştur
        self.create_summary_card(summary_frame, "Kritik Konular", "0", "#e74c3c")
        self.create_summary_card(summary_frame, "Önemli Konular", "0", "#f39c12")
        self.create_summary_card(summary_frame, "Takip Edilecek", "0", "#3498db")

        # Rapor butonları
        report_frame = tk.LabelFrame(results_tab, text=self.lm.tr("reports_section", "Raporlar"),
                                    font=('Segoe UI', 11, 'bold'), bg='white')
        report_frame.pack(fill='x', padx=20, pady=10)



        tk.Button(report_frame, text=f" {self.lm.tr('generate_materiality_report_btn', 'Materyal Konu Raporu Oluştur')}",
                bg='#3498db', fg='white', font=('Segoe UI', 10), relief='flat', width=30, pady=8,
                command=self.generate_materiality_report).pack(pady=5)

        tk.Button(report_frame, text=f" {self.lm.tr('stakeholder_analysis_report_btn', 'Stakeholder Analiz Raporu')}",
                bg='#27ae60', fg='white', font=('Segoe UI', 10), relief='flat', width=30, pady=8,
                command=self.generate_stakeholder_report).pack(pady=5)

        tk.Button(report_frame, text=f" {self.lm.tr('prioritization_matrix_excel_btn', 'Önceliklendirme Matrisi (Excel)')}",
                bg='#f39c12', fg='white', font=('Segoe UI', 10), relief='flat', width=30, pady=8,
                command=self.export_to_excel).pack(pady=5)

        # YENİ: Materialite Matrisi Görselleştirme
        matrix_frame = tk.LabelFrame(results_tab, text=f" {self.lm.tr('materiality_matrix_visualization', 'Materialite Matrisi Görselleştirme')}",
                                     font=('Segoe UI', 11, 'bold'), bg='white')
        matrix_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Butonlar
        matrix_btn_frame = tk.Frame(matrix_frame, bg='white')
        matrix_btn_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(matrix_btn_frame, text=f" {self.lm.tr('draw_matrix_btn', 'Matris Çiz')}",
                bg='#8e44ad', fg='white', font=('Segoe UI', 10), relief='flat', width=30, pady=8,
                command=self.draw_materiality_matrix).pack(side='left', padx=5)

        tk.Button(matrix_btn_frame, text=f" {self.lm.tr('excel_export_matrix_btn', 'Excel Export (Matris ile)')}",
                bg='#27ae60', fg='white', font=('Segoe UI', 10), relief='flat', width=30, pady=8,
                command=self.export_matrix_to_excel).pack(side='left', padx=5)

        tk.Button(matrix_btn_frame, text=f"️ {self.lm.tr('save_image_png_btn', 'Görsel Kaydet (PNG)')}",
                bg='#3498db', fg='white', font=('Segoe UI', 10), relief='flat', width=30, pady=8,
                command=self.save_matrix_image).pack(side='left', padx=5)

        # Canvas alanı (matris gösterilecek)
        self.matrix_canvas_frame = tk.Frame(matrix_frame, bg='white')
        self.matrix_canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def create_summary_card(self, parent, title, value, color) -> None:
        """Özet kartı oluştur"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=2)
        card.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        tk.Label(card, text=title, font=('Segoe UI', 10),
                fg='white', bg=color).pack(pady=(10, 5))
        tk.Label(card, text=value, font=('Segoe UI', 24, 'bold'),
                fg='white', bg=color).pack(pady=(0, 10))

    def add_stakeholder(self) -> None:
        """Stakeholder ekle"""
        try:
            name = self.stakeholder_name_entry.get().strip()
            category = self.stakeholder_category.get()
            impact = int(self.impact_level.get() or 0)
            importance = int(self.importance_level.get() or 0)

            if not name or not category:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("fill_all_fields_warning", "Lütfen tüm alanları doldurun!"))
                return

            if impact < 1 or importance < 1:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("impact_importance_range_warning", "Etki ve önem düzeyi 1-5 arası olmalı!"))
                return

            # Öncelik hesapla (ortalama)
            priority = (impact + importance) / 2
            priority_text = "Kritik" if priority >= 4 else "Yüksek" if priority >= 3 else "Orta"

            # Listeye ekle
            self.stakeholder_tree.insert('', 'end', values=(
                name, category, impact, importance, f"{priority:.1f}", priority_text
            ))

            # Formu temizle
            self.stakeholder_name_entry.delete(0, tk.END)
            self.stakeholder_category.set('')
            self.impact_level.set('')
            self.importance_level.set('')

            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("stakeholder_added_success", "Stakeholder eklendi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("stakeholder_add_error", "Stakeholder eklenemedi: {e}").format(e=e))

    def delete_stakeholder(self) -> None:
        """Seçili stakeholder'ı sil"""
        try:
            selected = self.stakeholder_tree.selection()
            if not selected:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_stakeholder_delete_warning", "Lütfen silmek için bir stakeholder seçin!"))
                return

            if messagebox.askyesno(self.lm.tr("confirm", "Onay"), self.lm.tr("delete_stakeholder_confirm", "Seçili stakeholder silinsin mi?")):
                for item in selected:
                    self.stakeholder_tree.delete(item)
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("stakeholder_deleted_success", "Stakeholder silindi!"))
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("delete_error", "Silme hatası: {e}").format(e=e))

    def calculate_and_add_topic(self) -> None:
        """Materyal konu skorunu hesapla ve ekle"""
        try:
            topic = self.topic_name_entry.get().strip()
            
            if not topic:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("topic_name_empty_warning", "Konu adı boş olamaz!"))
                return

            try:
                stakeholder = float(self.topic_stakeholder_impact.get() or 0)
                business = float(self.topic_business_impact.get() or 0)
                sustainability = float(self.topic_sustainability_impact.get() or 0)
            except ValueError:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("impact_levels_range_warning", "Tüm etki düzeyleri 1-5 arası olmalı!"))
                return

            if stakeholder < 1 or business < 1 or sustainability < 1:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("impact_levels_range_warning", "Tüm etki düzeyleri 1-5 arası olmalı!"))
                return

            # Öncelik skoru hesapla
            score = (stakeholder * 0.4) + (business * 0.3) + (sustainability * 0.3)

            # Öncelik sınıfı
            if score >= 4.0:
                priority = "Kritik"
                color_tag = "critical"
            elif score >= 3.0:
                priority = "Önemli"
                color_tag = "important"
            elif score >= 2.0:
                priority = "Takip"
                color_tag = "monitor"
            else:
                priority = "İzle"
                color_tag = "watch"

            # Listeye ekle
            self.topics_tree.insert('', 'end', values=(
                topic, f"{stakeholder:.1f}", f"{business:.1f}",
                f"{sustainability:.1f}", f"{score:.2f}", priority
            ), tags=(color_tag,))

            # Renklendirme
            self.topics_tree.tag_configure('critical', background='#ffcccc')
            self.topics_tree.tag_configure('important', background='#fff4cc')
            self.topics_tree.tag_configure('monitor', background='#ccf0ff')
            self.topics_tree.tag_configure('watch', background='#f0f0f0')

            # Formu temizle
            self.topic_name_entry.delete(0, tk.END)
            self.topic_stakeholder_impact.set('')
            self.topic_business_impact.set('')
            self.topic_sustainability_impact.set('')

            try:
                self.prioritization_manager.save_materiality_topic(
                    company_id=self.company_id,
                    topic_name=topic,
                    stakeholder_impact=stakeholder,
                    business_impact=business,
                    priority_score=score,
                )
            except Exception as ex:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("material_db_error", "Veritabanı kaydı başarısız: {e}").format(e=ex))

            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("material_topic_added_success", "Materyal konu eklendi! Öncelik Skoru: {score}").format(score=f"{score:.2f}"))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("results_calc_error", "Hesaplama hatası: {e}").format(e=e))

    def show_matrix_visualization(self) -> None:
        """Stakeholder matrisini görselleştir"""
        try:
            # Yeni pencere oluştur
            matrix_window = tk.Toplevel(self.parent)
            matrix_window.title(self.lm.tr("stakeholder_priority_matrix", "Stakeholder Öncelik Matrisi"))
            matrix_window.geometry("800x600")

            # Canvas oluştur
            canvas = tk.Canvas(matrix_window, bg='white')
            canvas.pack(fill='both', expand=True, padx=20, pady=20)

            # Matris çiz
            width = 600
            height = 500
            margin = 50

            # Eksenler
            canvas.create_line(margin, height-margin, width-margin, height-margin, width=2)  # X ekseni
            canvas.create_line(margin, margin, margin, height-margin, width=2)  # Y ekseni

            # Etiketler
            canvas.create_text(width/2, height-margin+30, text=self.lm.tr("impact_level_lbl", "Etki Düzeyi") + " →", font=('Segoe UI', 12, 'bold'))
            canvas.create_text(margin-30, height/2, text=self.lm.tr("importance_level_lbl", "Önem") + " ↑", font=('Segoe UI', 12, 'bold'), angle=90)

            # Grid çizgileri
            for i in range(6):
                x = margin + (width-2*margin) * i / 5
                y = margin + (height-2*margin) * i / 5
                canvas.create_line(x, margin, x, height-margin, fill='#ddd', dash=(2, 2))
                canvas.create_line(margin, y, width-margin, y, fill='#ddd', dash=(2, 2))
                canvas.create_text(x, height-margin+15, text=str(i+1), font=('Segoe UI', 9))
                canvas.create_text(margin-15, height-margin-y+margin, text=str(i+1), font=('Segoe UI', 9))

            # Stakeholder'ları çiz
            for item in self.stakeholder_tree.get_children():
                values = self.stakeholder_tree.item(item)['values']
                name, _category, impact, importance = values[0], values[1], float(values[2]), float(values[3])

                x = margin + (width-2*margin) * (impact-1) / 4
                y = height - margin - (height-2*margin) * (importance-1) / 4

                # Nokta rengi (önceliğe göre)
                priority = (impact + importance) / 2
                if priority >= 4:
                    color = '#e74c3c'
                elif priority >= 3:
                    color = '#f39c12'
                else:
                    color = '#3498db'

                # Nokta çiz
                canvas.create_oval(x-8, y-8, x+8, y+8, fill=color, outline='black', width=2)
                canvas.create_text(x, y-15, text=name, font=('Segoe UI', 8))

            messagebox.showinfo(self.lm.tr("info", "Bilgi"), self.lm.tr("matrix_drawn_success", "Stakeholder matrisi görüntülendi!"))

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("matrix_draw_error", "Görselleştirme hatası: {e}").format(e=e))

    def generate_materiality_report(self) -> None:
        """Materyal konu raporu oluştur"""
        try:
            # Konuları topla
            topics = []
            for item in self.topics_tree.get_children():
                values = self.topics_tree.item(item)['values']
                topics.append({
                    'topic': values[0],
                    'stakeholder_impact': float(values[1]),
                    'business_impact': float(values[2]),
                    'sustainability_impact': float(values[3]),
                    'score': float(values[4]),
                    'priority': values[5]
                })

            if not topics:
                messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("no_material_topics_warning", "Henüz materyal konu eklenmemiş!"))
                return

            # Rapor oluştur (basit text raporu)
            report_lines = [
                "=" * 80,
                self.lm.tr("material_topic_report_title", "MATERYAL KONU RAPORU"),
                "=" * 80,
                self.lm.tr("date_label", "Tarih: {date}").format(date=datetime.now().strftime('%Y-%m-%d %H:%M')),
                self.lm.tr("total_topic_count", "Toplam Konu Sayısı: {count}").format(count=len(topics)),
                "",
                self.lm.tr("material_topics_by_priority", "ÖNCELIK SIRALAMASINA GÖRE MATERYAL KONULAR:"),
                "-" * 80,
            ]

            # Önceliğe göre sırala
            sorted_topics = sorted(topics, key=lambda x: x['score'], reverse=True)

            for i, topic in enumerate(sorted_topics, 1):
                report_lines.append(f"\n{i}. {topic['topic']}")
                report_lines.append(f"   {self.lm.tr('stakeholder_impact_lbl', 'Stakeholder Etkisi')}: {topic['stakeholder_impact']:.1f}")
                report_lines.append(f"   {self.lm.tr('business_impact_lbl', 'İş Etkisi')}: {topic['business_impact']:.1f}")
                report_lines.append(f"   {self.lm.tr('sustainability_impact_lbl', 'Sürdürülebilirlik Etkisi')}: {topic['sustainability_impact']:.1f}")
                report_lines.append(f"    {self.lm.tr('total_score_lbl', 'TOPLAM SKOR: {score} - {priority}').format(score=f'{topic['score']:.2f}', priority=topic['priority'])}")

            report_lines.extend([
                "",
                "=" * 80,
                self.lm.tr("end_of_report", "RAPOR SONU")
            ])

            # Raporu göster
            report_window = tk.Toplevel(self.parent)
            report_window.title(self.lm.tr("material_topic_report_window_title", "Materyal Konu Raporu"))
            report_window.geometry("700x600")

            text_widget = tk.Text(report_window, wrap='word', font=('Courier', 10))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)

            text_widget.insert('1.0', '\n'.join(report_lines))
            text_widget.config(state='disabled')

            # Kaydet butonu
            tk.Button(report_window, text=self.lm.tr("save_report_btn", " Raporu Kaydet"), bg='#27ae60', fg='white',
                     command=lambda: self.save_report('\n'.join(report_lines))).pack(pady=10)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("report_create_error", "Rapor oluşturma hatası: {e}").format(e=e))

    def generate_stakeholder_report(self) -> None:
        try:
            from .materiality_matrix import MaterialityMatrix
            mm = MaterialityMatrix()
            topics = mm.get_materiality_topics(self.company_id)
            lines = []
            lines.append(self.lm.tr("stakeholder_analysis_report_title", "Stakeholder Analiz Raporu"))
            lines.append("="*26 + "\n")
            if not topics:
                lines.append(self.lm.tr("no_material_topics_found", "Kayıtlı materyal konu bulunamadı."))
            else:
                import statistics
                st_vals = [t.get('stakeholder_impact', 0) for t in topics]
                bs_vals = [t.get('business_impact', 0) for t in topics]
                pr_vals = [t.get('priority_score', 0) for t in topics]
                lines.append(self.lm.tr("total_topic_count_simple", "Toplam Konu: {count}").format(count=len(topics)))
                lines.append(self.lm.tr("avg_stakeholder_impact", "Paydaş Etkisi Ortalama: {val:.2f}").format(val=statistics.mean(st_vals)))
                lines.append(self.lm.tr("avg_business_impact", "İş Etkisi Ortalama: {val:.2f}").format(val=statistics.mean(bs_vals)))
                lines.append(self.lm.tr("avg_priority_score", "Öncelik Skoru Ortalama: {val:.2f}").format(val=statistics.mean(pr_vals)) + "\n")
                high = [t for t in topics if (t.get('priority_score',0) or 0) >= 75]
                medium = [t for t in topics if 50 <= (t.get('priority_score',0) or 0) < 75]
                low = [t for t in topics if (t.get('priority_score',0) or 0) < 50]
                lines.append(self.lm.tr("priority_counts_summary", "Yüksek Öncelik: {high} | Orta: {medium} | Düşük: {low}").format(high=len(high), medium=len(medium), low=len(low)) + "\n")
                lines.append(self.lm.tr("detailed_list", "Detaylı Liste:") + "\n")
                for t in topics[:50]:
                    lines.append(f"- {t.get('topic_name','')} | Paydaş: {t.get('stakeholder_impact',0)} | İş: {t.get('business_impact',0)} | Skor: {t.get('priority_score',0)}")
            report_window = tk.Toplevel(self.parent)
            report_window.title(self.lm.tr("stakeholder_analysis_report_title", "Stakeholder Analiz Raporu"))
            report_window.geometry("700x600")
            text_widget = tk.Text(report_window, wrap='word', font=('Courier', 10))
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', "\n".join(lines))
            text_widget.config(state='disabled')
            tk.Button(report_window, text=self.lm.tr("save_report_btn", " Raporu Kaydet"), bg='#27ae60', fg='white',
                     command=lambda: self.save_report("\n".join(lines))).pack(pady=10)
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("report_error", "Rapor hatası: {e}").format(e=e))

    def export_to_excel(self) -> None:
        try:
            import os
            from tkinter import filedialog

            from .materiality_matrix import MaterialityMatrix
            file_path = filedialog.asksaveasfilename(
                title=self.lm.tr('export_excel', "Excel'e Aktar"),
                defaultextension=".xlsx",
                filetypes=[(self.lm.tr("excel_file", "Excel dosyası"), "*.xlsx")],
                initialfile=f"Materialite_Analizi_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )
            if not file_path:
                return
            matrix = MaterialityMatrix()
            if matrix.export_to_excel(company_id=self.company_id, output_path=file_path):
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("excel_export_success_short", "Excel'e export edildi:\n{path}").format(path=file_path))
                if messagebox.askyesno(self.lm.tr("open_file", "Dosyayı Aç"), self.lm.tr("open_file_confirm", "Excel dosyasını açmak ister misiniz?")):
                    os.startfile(file_path)
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("excel_export_error", "Excel export başarısız!"))
        except Exception as e:
            import traceback
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("excel_export_exception", "Excel export hatası:\n{e}").format(e=str(e)))

    def save_report(self, report_content) -> None:
        """Raporu dosyaya kaydet"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[(self.lm.tr("file_text", "Metin Dosyası"), "*.txt"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                    title=self.lm.tr("save_report", "Raporu Kaydet")
                )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("report_saved_success", "Rapor kaydedildi:\n{path}").format(path=filename))
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("save_error", "Kaydetme hatası: {e}").format(e=e))

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_surveys()

    def load_surveys(self) -> None:
        """Anketleri yükle"""
        self.survey_listbox.delete(0, tk.END)
        surveys = self.prioritization_manager.get_survey_templates()

        for survey in surveys:
            # category alanı yoksa varsayılan değer kullan
            category = survey.get('category', 'Genel')
            self.survey_listbox.insert(tk.END, f"{survey['name']} ({category})")

    def on_survey_select(self, event) -> None:
        """Anket seçildiğinde"""
        selection = self.survey_listbox.curselection()
        if selection:
            survey_name = self.survey_listbox.get(selection[0])
            self.show_survey_details(survey_name)

    def show_survey_details(self, survey_name) -> None:
        """Anket detaylarını göster"""
        # Mevcut detayları temizle
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # Anket bilgilerini al
        surveys = self.prioritization_manager.get_survey_templates()
        selected_survey = None
        for survey in surveys:
            if f"{survey['name']} ({survey['category']})" == survey_name:
                selected_survey = survey
                break

        if not selected_survey:
            return

        # Anket başlığı
        title_label = tk.Label(self.detail_frame, text=selected_survey['name'],
                              font=('Segoe UI', 14, 'bold'), bg='white', fg='#8e44ad')
        title_label.pack(pady=(0, 10))

        # Anket açıklaması
        desc_label = tk.Label(self.detail_frame, text=selected_survey['description'],
                             font=('Segoe UI', 10), bg='white', fg='#7f8c8d', wraplength=400)
        desc_label.pack(pady=(0, 10))

        # Anketi doldur butonu
        fill_btn = tk.Button(self.detail_frame, text=self.lm.tr("fill_survey_btn", "Anketi Doldur"), font=('Segoe UI', 12, 'bold'),
                           bg='#e67e22', fg='white', relief='flat', bd=0,
                           command=lambda: self.fill_survey(selected_survey['id']))
        fill_btn.pack(pady=10)

        # Sonuçları görüntüle butonu
        ttk.Button(self.detail_frame, text=self.lm.tr("view_results_btn", "Sonuçları Görüntüle"), style='Primary.TButton',
                   command=lambda: self.show_results(selected_survey['id'])).pack(pady=5)

        # Standart sorular içe aktarma
        std_frame = tk.Frame(self.detail_frame, bg='white')
        std_frame.pack(fill='x', pady=(10, 5))
        tk.Label(std_frame, text=self.lm.tr("standard_questions_title", "Standart Sorular"), font=('Segoe UI', 11, 'bold'), bg='white', fg='#2c3e50').pack(anchor='w')
        std_inner = tk.Frame(std_frame, bg='white')
        std_inner.pack(fill='x', pady=5)
        framework_var = tk.StringVar(value=selected_survey.get('category', 'SDG'))
        framework_combo = ttk.Combobox(std_inner, textvariable=framework_var,
                                       values=["SDG", "GRI", "TSRS"], font=('Segoe UI', 10), width=10)
        framework_combo.pack(side='left')
        ttk.Button(std_inner, text=self.lm.tr("add_standard_questions_btn", "Standart Soruları Ekle"), style='Primary.TButton',
                   command=lambda: self.populate_standard_questions(selected_survey['id'], framework_var.get())).pack(side='left', padx=10)

        # Soruları düzenleme
        ttk.Button(self.detail_frame, text=self.lm.tr("edit_questions_btn", "Soruları Düzenle"), style='Primary.TButton',
                   command=lambda: self.edit_survey_questions(selected_survey['id'])).pack(pady=5)

    def create_survey(self) -> None:
        """Yeni anket oluştur"""
        # Anket oluşturma penceresi
        create_window = tk.Toplevel(self.parent)
        create_window.title(self.lm.tr("create_new_survey", "Yeni Anket Oluştur"))
        create_window.state('zoomed')  # Tam ekran
        create_window.configure(bg='#f5f5f5')

        # Form
        form_frame = tk.Frame(create_window, bg='#f5f5f5')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Anket adı
        tk.Label(form_frame, text=self.lm.tr("survey_name_lbl", "Anket Adı:"), font=('Segoe UI', 12, 'bold'),
                bg='#f5f5f5', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 12), width=50)
        name_entry.pack(fill='x', pady=(0, 10))

        # Açıklama
        tk.Label(form_frame, text=self.lm.tr("description_lbl", "Açıklama:"), font=('Segoe UI', 12, 'bold'),
                bg='#f5f5f5', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        desc_text = tk.Text(form_frame, height=3, font=('Segoe UI', 12))
        desc_text.pack(fill='x', pady=(0, 10))

        # Kategori
        tk.Label(form_frame, text=self.lm.tr("category_lbl", "Kategori:"), font=('Segoe UI', 12, 'bold'),
                bg='#f5f5f5', fg='#2c3e50').pack(anchor='w', pady=(0, 5))
        category_var = tk.StringVar(value="SDG")
        category_combo = ttk.Combobox(form_frame, textvariable=category_var,
                                     values=["SDG", "GRI", "TSRS", "Genel"], font=('Segoe UI', 12))
        category_combo.pack(fill='x', pady=(0, 20))

        # Kaydet butonu
        save_btn = tk.Button(form_frame, text=self.lm.tr("create_survey_btn", "Anket Oluştur"), font=('Segoe UI', 12, 'bold'),
                           bg='#27ae60', fg='white', relief='flat', bd=0,
                           command=lambda: self.save_survey(name_entry.get(), desc_text.get("1.0", tk.END).strip(),
                                                          category_var.get(), create_window))
        save_btn.pack(pady=10)

    def save_survey(self, name, description, category, window) -> None:
        """Anketi kaydet"""
        if not name:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("survey_name_required", "Anket adı gerekli"))
            return

        template_id = self.prioritization_manager.create_survey_template(name, description, category)

        if template_id:
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("survey_created_success", "Anket oluşturuldu"))
            window.destroy()
            self.load_surveys()
        else:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("survey_create_error", "Anket oluşturulamadı"))

    def create_default_survey(self) -> None:
        """Varsayılan anket oluştur"""
        template_id = self.prioritization_manager.create_default_survey_template()

        if template_id:
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("default_survey_created", "Varsayılan anket oluşturuldu"))
            self.load_surveys()
        else:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("default_survey_error", "Varsayılan anket oluşturulamadı"))

    def delete_survey(self) -> None:
        """Seçili anketi sil"""
        # Seçili anketi al
        selected_indices = self.survey_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("select_survey_delete_warning", "Lütfen silmek istediğiniz anketi seçin"))
            return

        # Anket bilgilerini al
        surveys = self.prioritization_manager.get_survey_templates()
        if not surveys or selected_indices[0] >= len(surveys):
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("survey_not_found", "Seçili anket bulunamadı"))
            return

        selected_survey = surveys[selected_indices[0]]

        # Onay iste
        result = messagebox.askyesno(self.lm.tr("confirm", "Onay"),
                                   self.lm.tr("delete_survey_confirm", "'{name}' anketini silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz ve tüm sorular da silinecektir.").format(name=selected_survey['name']))

        if result:
            # Anketi sil
            success = self.prioritization_manager.delete_survey_template(selected_survey['id'])

            if success:
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("survey_deleted_success", "Anket başarıyla silindi"))
                self.load_surveys()
                # Detay panelini temizle
                self.clear_detail_panel()
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("survey_delete_error", "Anket silinirken bir hata oluştu"))

    def populate_standard_questions(self, template_id: int, framework: str) -> None:
        """CSV'den framework (SDG/GRI/TSRS) standart soruları ekle."""
        added = self.prioritization_manager.populate_standard_questions(template_id, framework)
        if added > 0:
            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("standard_questions_added", "{framework} standart sorularından {added} adet eklendi.").format(framework=framework, added=added))
            # Listeyi tazele ve detayları yeniden göster
            self.load_surveys()
        else:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("standard_questions_warning", "Standart sorular eklenemedi ya da uygun soru bulunamadı."))

    def edit_survey_questions(self, template_id: int) -> None:
        """Soru düzenleme arayüzü: kaydırılabilir liste + çerçeve ve bölüm filtresi."""
        questions = self.prioritization_manager.get_survey_questions(template_id)
        if not questions:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("no_questions_found", "Bu anket için soru bulunamadı"))
            return

        # Yardımcı: soru için çerçeve (framework) belirle
        def detect_framework(q) -> str:
            mapping = (q.get('sdg_mapping') or '').upper()
            if 'GRI' in mapping:
                return 'GRI'
            if 'TSRS' in mapping:
                return 'TSRS'
            if 'SDG' in mapping:
                return 'SDG'
            return 'Genel'

        # Mevcut kategoriler ve çerçeveler
        categories = sorted({(q.get('category') or 'Genel') for q in questions})
        frameworks = sorted({detect_framework(q) for q in questions})

        win = tk.Toplevel(self.parent)
        win.title(self.lm.tr("edit_questions_btn", "Soruları Düzenle"))
        # Tam ekran (Windows)
        try:
            win.state('zoomed')
        except Exception:
            win.geometry("1200x800")
        win.configure(bg='#f5f5f5')

        # Filtre alanı
        filter_frame = tk.Frame(win, bg='#f5f5f5')
        filter_frame.pack(fill='x', padx=10, pady=(10, 0))

        tk.Label(filter_frame, text=self.lm.tr("framework_lbl", "Çerçeve:"), font=('Segoe UI', 10, 'bold'), bg='#f5f5f5').pack(side='left')
        framework_var = tk.StringVar(value=self.lm.tr("all_option", "Tümü"))
        framework_combo = ttk.Combobox(filter_frame, textvariable=framework_var,
                                       values=[self.lm.tr("all_option", "Tümü")] + frameworks, width=10)
        framework_combo.pack(side='left', padx=(5, 15))

        tk.Label(filter_frame, text=self.lm.tr("section_lbl", "Bölüm:"), font=('Segoe UI', 10, 'bold'), bg='#f5f5f5').pack(side='left')
        category_var = tk.StringVar(value=self.lm.tr("all_option", "Tümü"))
        category_combo = ttk.Combobox(filter_frame, textvariable=category_var,
                                      values=[self.lm.tr("all_option", "Tümü")] + categories, width=18)
        category_combo.pack(side='left', padx=(5, 15))

        # Kaydırılabilir liste konteyneri
        list_container = tk.Frame(win, bg='#f5f5f5')
        list_container.pack(fill='both', expand=True, padx=10, pady=10)

        canvas = tk.Canvas(list_container, bg='#f5f5f5', highlightthickness=0)
        vscroll = ttk.Scrollbar(list_container, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        list_frame = tk.Frame(canvas, bg='#f5f5f5')
        list_window = canvas.create_window((0, 0), window=list_frame, anchor='nw')
        # İçteki frame, canvas genişliğine otomatik sığsın
        canvas.bind('<Configure>', lambda e: canvas.itemconfigure(list_window, width=e.width))

        def on_configure(event) -> None:
            canvas.configure(scrollregion=canvas.bbox('all'))
        list_frame.bind('<Configure>', on_configure)

        from typing import Any, List, Tuple
        entries: List[Tuple[int, Any, Any, Any]] = []

        def render_rows() -> None:
            nonlocal entries
            # Temizle
            for w in list_frame.winfo_children():
                w.destroy()
            entries = []
            # Aktif filtreler
            f_sel = framework_var.get()
            c_sel = category_var.get()

            for q in questions:
                fw = detect_framework(q)
                cat_val = q.get('category') or 'Genel'
                if f_sel != self.lm.tr("all_option", "Tümü") and fw != f_sel:
                    continue
                if c_sel != self.lm.tr("all_option", "Tümü") and cat_val != c_sel:
                    continue

                row = tk.Frame(list_frame, bg='white', relief='raised', bd=1)
                row.pack(fill='x', pady=5)

                tk.Label(row, text=f"#{q['id']}", font=('Segoe UI', 9), bg='white').pack(side='left', padx=6)

                txt = tk.Entry(row, font=('Segoe UI', 10), width=120)
                txt.insert(0, q['question_text'])
                txt.pack(side='left', fill='x', expand=True, padx=6)

                wt = tk.Entry(row, font=('Segoe UI', 10), width=8)
                wt.insert(0, str(q['weight']))
                wt.pack(side='left', padx=6)

                cat = tk.Entry(row, font=('Segoe UI', 10), width=18)
                cat.insert(0, cat_val)
                cat.pack(side='left', padx=6)

                # Çerçeve rozeti (salt-okunur)
                tk.Label(row, text=fw, font=('Segoe UI', 9, 'bold'), bg='white', fg='#8e44ad', width=8,
                         relief='flat').pack(side='left', padx=6)

                # Sil butonu
                def delete_this_question(qid=q['id']) -> None:
                    if messagebox.askyesno(self.lm.tr("confirm", "Onay"), self.lm.tr("delete_question_confirm", "#{qid} numaralı soruyu silmek istediğinizden emin misiniz?").format(qid=qid)):
                        if self.prioritization_manager.delete_survey_question(qid):
                            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("question_deleted_success", "Soru silindi"))
                            # Soruları yeniden yükle ve render et
                            nonlocal questions
                            questions = self.prioritization_manager.get_survey_questions(template_id)
                            render_rows()
                        else:
                            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("question_delete_error", "Soru silinemedi"))

                tk.Button(row, text="️", font=('Segoe UI', 10), bg='#e74c3c', fg='white',
                         relief='flat', bd=0, cursor='hand2', width=3,
                         command=delete_this_question).pack(side='left', padx=6)

                entries.append((q['id'], txt, wt, cat))

        render_rows()
        framework_combo.bind('<<ComboboxSelected>>', lambda e: render_rows())
        category_combo.bind('<<ComboboxSelected>>', lambda e: render_rows())

        # Alt butonlar
        btn_frame = tk.Frame(win, bg='#f5f5f5')
        btn_frame.pack(fill='x', pady=10)

        def save_all() -> None:
            ok = 0
            for qid, txt, wt, cat in entries:
                try:
                    weight_val = float(wt.get())
                except Exception:
                    weight_val = 1.0
                if self.prioritization_manager.update_survey_question(
                        qid,
                        question_text=txt.get(),
                        weight=weight_val,
                        category=cat.get()):
                    ok += 1
            messagebox.showinfo(self.lm.tr("saved_title", "Kaydedildi"), self.lm.tr("questions_updated", "{ok} soru güncellendi").format(ok=ok))
            win.destroy()

        tk.Button(btn_frame, text=self.lm.tr("save_btn", "Kaydet"), font=('Segoe UI', 11, 'bold'), bg='#27ae60', fg='white',
                  relief='flat', bd=0, command=save_all).pack(side='right')
        tk.Button(btn_frame, text=self.lm.tr("cancel_btn", "İptal"), font=('Segoe UI', 11), bg='#95a5a6', fg='white',
                  relief='flat', bd=0, command=win.destroy).pack(side='right', padx=10)

    def fill_survey(self, template_id) -> None:
        """Anketi doldur"""
        # Anket doldurma penceresi
        survey_window = tk.Toplevel(self.parent)
        survey_window.title(self.lm.tr("fill_survey_title", "Anket Doldur"))
        survey_window.state('zoomed')  # Tam ekran
        survey_window.configure(bg='#f5f5f5')

        # Soruları getir
        questions = self.prioritization_manager.get_survey_questions(template_id)

        if not questions:
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("no_questions_found", "Bu anket için soru bulunamadı"))
            survey_window.destroy()
            return

        # Başlık
        title_frame = tk.Frame(survey_window, bg='#8e44ad', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr("fill_survey_title", "Anket Doldur"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#8e44ad')
        title_label.pack(expand=True)

        # Form içeriği (kaydırılabilir)
        container = tk.Frame(survey_window, bg='#f5f5f5')
        container.pack(fill='both', expand=True, padx=20, pady=10)
        canvas = tk.Canvas(container, bg='#f5f5f5', highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        form_holder = tk.Frame(canvas, bg='#f5f5f5')
        form_holder.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=form_holder, anchor='nw')
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Sorular
        from typing import Any, Dict
        self.question_vars: Dict[int, Any] = {}

        for i, question in enumerate(questions):
            question_frame = tk.Frame(form_holder, bg='white', relief='raised', bd=1)
            question_frame.pack(fill='x', pady=5, padx=10)

            # Soru metni
            question_label = tk.Label(question_frame, text=f"{i+1}. {question['question_text']}",
                                    font=('Segoe UI', 11, 'bold'), bg='white', fg='#2c3e50',
                                    wraplength=800, justify='left')
            question_label.pack(anchor='w', padx=10, pady=(10, 5))

            # Cevap alanı
            if question['question_type'] == 'scale':
                # 1-5 ölçek
                scale_var = tk.IntVar(value=3)
                scale_frame = tk.Frame(question_frame, bg='white')
                scale_frame.pack(fill='x', padx=10, pady=(0, 10))

                tk.Label(scale_frame, text="1", font=('Segoe UI', 10), bg='white').pack(side='left')
                scale = tk.Scale(scale_frame, from_=1, to=5, orient='horizontal',
                               variable=scale_var, bg='white')
                scale.pack(side='left', padx=10, fill='x', expand=True)
                tk.Label(scale_frame, text="5", font=('Segoe UI', 10), bg='white').pack(side='left')

                self.question_vars[question['id']] = scale_var
            else:
                # Metin cevabı
                text_var = tk.StringVar()
                text_entry = tk.Entry(question_frame, textvariable=text_var, font=('Segoe UI', 11))
                text_entry.pack(fill='x', padx=10, pady=(0, 10))

                self.question_vars[question['id']] = text_var

        # Kaydet butonu
        button_frame = tk.Frame(survey_window, bg='#f5f5f5')
        button_frame.pack(fill='x', padx=20, pady=10)

        save_btn = tk.Button(button_frame, text=self.lm.tr("save_survey_btn", "Anketi Kaydet"), font=('Segoe UI', 12, 'bold'),
                           bg='#27ae60', fg='white', relief='flat', bd=0,
                           command=lambda: self.save_survey_responses(template_id, survey_window))
        save_btn.pack(side='right')

        cancel_btn = tk.Button(button_frame, text=self.lm.tr("cancel_btn", "İptal"), font=('Segoe UI', 12),
                             bg='#95a5a6', fg='white', relief='flat', bd=0,
                             command=survey_window.destroy)
        cancel_btn.pack(side='right', padx=(0, 10))

    def save_survey_responses(self, template_id, window) -> None:
        """Anket cevaplarını kaydet"""
        questions = self.prioritization_manager.get_survey_questions(template_id)

        for question in questions:
            question_id = question['id']
            if question_id in self.question_vars:
                var = self.question_vars[question_id]

                if question['question_type'] == 'scale':
                    response_value = str(var.get())
                    score = float(var.get())
                else:
                    response_value = str(var.get())
                    score = 5.0 if response_value else 0.0

                self.prioritization_manager.save_survey_response(
                    self.company_id, question_id, response_value, score
                )

        # Skorları hesapla
        results = self.prioritization_manager.calculate_priority_scores(self.company_id, template_id)

        messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("survey_saved_success", "Anket kaydedildi!\nGenel Skor: {score}\nÖncelik: {priority}").format(score=f"{results['overall_score']:.1f}", priority=results['overall_priority']))

        window.destroy()

    def show_results(self, template_id) -> None:
        """Sonuçları göster"""
        # Sonuç penceresi
        results_window = tk.Toplevel(self.parent)
        results_window.title(self.lm.tr("survey_results_title", "Anket Sonuçları"))
        results_window.state('zoomed')  # Tam ekran
        results_window.configure(bg='#f5f5f5')

        # Başlık
        title_frame = tk.Frame(results_window, bg='#8e44ad', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr("survey_results_title", "Anket Sonuçları"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#8e44ad')
        title_label.pack(expand=True)

        # Sonuçları hesapla (hata yakalama ile güvenli)
        try:
            results = self.prioritization_manager.calculate_priority_scores(self.company_id, template_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("results_calc_error", "Sonuçlar hesaplanırken hata oluştu: {e}").format(e=e))
            results = {
                'overall_score': 0.0,
                'overall_priority': 'low',
                'category_scores': {}
            }

        # İçerik
        content_frame = tk.Frame(results_window, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Genel skor
        overall_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        overall_frame.pack(fill='x', pady=(0, 10))

        overall_label = tk.Label(overall_frame, text=self.lm.tr("overall_score_fmt", "Genel Skor: {score:.1f}%").format(score=results['overall_score']),
                               font=('Segoe UI', 14, 'bold'), bg='white', fg='#8e44ad')
        overall_label.pack(pady=10)

        priority_label = tk.Label(overall_frame, text=self.lm.tr("priority_level_fmt", "Öncelik Seviyesi: {priority}").format(priority=results['overall_priority'].upper()),
                                font=('Segoe UI', 12), bg='white', fg='#2c3e50')
        priority_label.pack(pady=(0, 10))

        # Kategori skorları
        categories_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        categories_frame.pack(fill='both', expand=True)

        tk.Label(categories_frame, text=self.lm.tr("category_scores_lbl", "Kategori Skorları"), font=('Segoe UI', 12, 'bold'),
                bg='white', fg='#8e44ad').pack(pady=10)

        # Tablo veya boş durum
        if results['category_scores']:
            columns = (self.lm.tr("col_category", "Kategori"), self.lm.tr("col_score", "Skor"), self.lm.tr("col_priority", "Öncelik"), self.lm.tr("col_question_count", "Soru Sayısı"))
            tree = ttk.Treeview(categories_frame, columns=columns, show='headings', height=10)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor='center')
            for category, data in results['category_scores'].items():
                tree.insert('', 'end', values=(
                    category,
                    f"{data['score']:.1f}%",
                    data['priority_level'].upper(),
                    data['question_count']
                ))
            tree.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        else:
            tk.Label(categories_frame,
                     text=self.lm.tr("no_responses_found", "Henüz kayıtlı cevap bulunamadı veya hesaplama yapılmadı"),
                     font=('Segoe UI', 11), bg='white', fg='#7f8c8d').pack(pady=10)

    def clear_detail_panel(self) -> None:
        """Detay panelini temizle"""
        # Detay panelindeki tüm widget'ları temizle
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        # Boş mesaj göster
        empty_label = tk.Label(self.detail_frame,
                              text=self.lm.tr("empty_panel_msg", "Anket seçin veya yeni anket oluşturun"),
                              font=('Segoe UI', 12), fg='#7f8c8d', bg='white')
        empty_label.pack(expand=True)

    # YENİ: Materialite Matrisi Fonksiyonları
    def draw_materiality_matrix(self) -> None:
        """Materialite matrisini çiz"""
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            from .materiality_matrix import MaterialityMatrix

            # Önceki canvas'ı temizle
            for widget in self.matrix_canvas_frame.winfo_children():
                widget.destroy()

            # Matris oluştur
            matrix = MaterialityMatrix()
            fig = matrix.create_matrix_plot(company_id=self.company_id, figsize=(10, 8))

            # Canvas'a yerleştir
            canvas = FigureCanvasTkAgg(fig, master=self.matrix_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

            messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("matrix_drawn_success", "Materialite matrisi çizildi!\n\n Kırmızı: Yüksek Öncelik\n Turuncu: Orta Öncelik\n Gri: Düşük Öncelik"))

        except Exception as e:
            import traceback
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("matrix_draw_error", "Matris çizim hatası:\n{e}").format(e=str(e)))

    def export_matrix_to_excel(self) -> None:
        """Materialite matrisini Excel'e export et"""
        try:
            import os
            from tkinter import filedialog

            from .materiality_matrix import MaterialityMatrix

            # Dosya kaydetme dialogu
            file_path = filedialog.asksaveasfilename(
                title=self.lm.tr('export_excel', "Excel'e Aktar"),
                defaultextension=".xlsx",
                filetypes=[(self.lm.tr("excel_file", "Excel dosyası"), "*.xlsx")],
                initialfile=f"Materialite_Analizi_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )

            if not file_path:
                return

            # Export et
            matrix = MaterialityMatrix()
            if matrix.export_to_excel(company_id=self.company_id, output_path=file_path):
                messagebox.showinfo(self.lm.tr("success", "Başarılı"),
                    self.lm.tr("excel_export_success", "Materialite analizi Excel'e export edildi!\n\n 2 sayfa oluşturuldu:\n  • Materialite Analizi (renk kodlamalı)\n  • Özet İstatistikler\n\nDosya: {path}").format(path=file_path))

                # Dosyayı aç
                if messagebox.askyesno(self.lm.tr("open_file", "Dosyayı Aç"), self.lm.tr("open_file_confirm", "Excel dosyasını açmak ister misiniz?")):
                    os.startfile(file_path)
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("excel_export_error", "Excel export başarısız!"))

        except Exception as e:
            import traceback
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("excel_export_exception", "Excel export hatası:\n{e}").format(e=str(e)))

    def save_matrix_image(self) -> None:
        """Matris görselini PNG olarak kaydet"""
        try:
            import os
            from tkinter import filedialog

            from .materiality_matrix import MaterialityMatrix

            # Dosya kaydetme dialogu
            file_path = filedialog.asksaveasfilename(
                title=self.lm.tr('save_matrix', "Matrisi Kaydet"),
                defaultextension=".png",
                filetypes=[(self.lm.tr("png_file", "PNG dosyası"), "*.png"), (self.lm.tr("all_files", "Tüm dosyalar"), "*.*")],
                initialfile=f"Materialite_Matrisi_{datetime.now().strftime('%Y%m%d')}.png"
            )

            if not file_path:
                return

            # Görsel kaydet
            matrix = MaterialityMatrix()
            if matrix.save_matrix_image(company_id=self.company_id, output_path=file_path):
                messagebox.showinfo(self.lm.tr("success", "Başarılı"),
                    self.lm.tr("matrix_image_saved", "Materialite matrisi görseli kaydedildi!\n\nDosya: {path}\n\nYüksek çözünürlüklü (300 DPI)").format(path=file_path))

                # Dosyayı aç
                if messagebox.askyesno(self.lm.tr("open_file", "Dosyayı Aç"), self.lm.tr("open_image_confirm", "PNG dosyasını açmak ister misiniz?")):
                    os.startfile(file_path)
            else:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("image_save_error", "Görsel kaydetme başarısız!"))

        except Exception as e:
            import traceback
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("image_save_exception", "Görsel kaydetme hatası:\n{e}").format(e=str(e)))
