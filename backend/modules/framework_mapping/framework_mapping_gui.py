import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Framework Eşleştirme Modülü GUI - UNGC ↔ SDG/GRI/TSRS eşleştirmelerini yönetme
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class FrameworkMappingGUI:
    """Framework Eşleştirme Modülü GUI - UNGC, SDG, GRI, TSRS eşleştirmeleri"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Framework Eşleştirme modülü arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#2c3e50', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        title_frame.pack(side='left', padx=20, pady=15)

        title_label = tk.Label(title_frame, text="Framework Eşleştirme Modülü",
                             font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(side='left')

        subtitle_label = tk.Label(title_frame, text="UNGC ↔ SDG/GRI/TSRS Eşleştirmeleri",
                                 font=('Segoe UI', 11), fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(side='left', padx=(10, 0))

        # Ana içerik - Tabbed interface
        self.create_tabbed_interface(main_frame)

    def create_tabbed_interface(self, parent) -> None:
        """Tabbed interface oluştur"""
        # Notebook (tab container)
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True)

        # UNGC-SDG Tab
        self.ungc_sdg_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.ungc_sdg_frame, text="UNGC-SDG Eşleştirmeleri")
        self.create_ungc_sdg_tab()

        # UNGC-GRI Tab
        self.ungc_gri_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.ungc_gri_frame, text="UNGC-GRI Eşleştirmeleri")
        self.create_ungc_gri_tab()

        # UNGC-TSRS Tab
        self.ungc_tsrs_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.ungc_tsrs_frame, text="UNGC-TSRS Eşleştirmeleri")
        self.create_ungc_tsrs_tab()

        # UNGC Compliance Tab
        self.compliance_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.compliance_frame, text="UNGC Uyum Durumu")
        self.create_compliance_tab()

        # Mapping Analysis Tab
        self.analysis_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.analysis_frame, text="Eşleştirme Analizi")
        self.create_analysis_tab()

    def create_ungc_sdg_tab(self) -> None:
        """UNGC-SDG eşleştirmeleri tab'ı oluştur"""
        # Başlık
        title_label = tk.Label(self.ungc_sdg_frame, text="UNGC-SDG Eşleştirmeleri",
                             font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(pady=(20, 10))

        # Açıklama
        desc_label = tk.Label(self.ungc_sdg_frame,
                             text="United Nations Global Compact 10 İlkesi ile SDG Hedeflerinin Eşleştirmesi",
                             font=('Segoe UI', 10), fg='#7f8c8d', bg='white')
        desc_label.pack(pady=(0, 20))

        # Arama ve filtreleme
        search_frame = tk.Frame(self.ungc_sdg_frame, bg='white')
        search_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(search_frame, text="Ara:", font=('Segoe UI', 10), bg='white').pack(side='left')
        self.ungc_sdg_search = tk.Entry(search_frame, font=('Segoe UI', 10), width=30)
        self.ungc_sdg_search.pack(side='left', padx=10)
        self.ungc_sdg_search.bind('<KeyRelease>', lambda e: self.filter_ungc_sdg())

        # Treeview
        columns = ('UNGC İlkesi', 'SDG Hedefi', 'SDG Göstergesi', 'İlişki Tipi', 'Notlar')
        self.ungc_sdg_tree = ttk.Treeview(self.ungc_sdg_frame, columns=columns, show='headings', height=15)

        # Başlık ve hücreleri ortala
        for col in columns:
            self.ungc_sdg_tree.heading(col, text=col, anchor='center')
            self.ungc_sdg_tree.column(col, width=160, anchor='center')

        # Scrollbar
        ungc_sdg_scrollbar = ttk.Scrollbar(self.ungc_sdg_frame, orient='vertical', command=self.ungc_sdg_tree.yview)
        self.ungc_sdg_tree.configure(yscrollcommand=ungc_sdg_scrollbar.set)

        self.ungc_sdg_tree.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        ungc_sdg_scrollbar.pack(side='right', fill='y', pady=10)

    def create_ungc_gri_tab(self) -> None:
        """UNGC-GRI eşleştirmeleri tab'ı oluştur"""
        # Başlık
        title_label = tk.Label(self.ungc_gri_frame, text="UNGC-GRI Eşleştirmeleri",
                             font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(pady=(20, 10))

        # Açıklama
        desc_label = tk.Label(self.ungc_gri_frame,
                             text="United Nations Global Compact 10 İlkesi ile GRI Standartlarının Eşleştirmesi",
                             font=('Segoe UI', 10), fg='#7f8c8d', bg='white')
        desc_label.pack(pady=(0, 20))

        # Arama ve filtreleme
        search_frame = tk.Frame(self.ungc_gri_frame, bg='white')
        search_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(search_frame, text="Ara:", font=('Segoe UI', 10), bg='white').pack(side='left')
        self.ungc_gri_search = tk.Entry(search_frame, font=('Segoe UI', 10), width=30)
        self.ungc_gri_search.pack(side='left', padx=10)
        self.ungc_gri_search.bind('<KeyRelease>', lambda e: self.filter_ungc_gri())

        # Treeview
        columns = ('UNGC İlkesi', 'GRI Standart', 'GRI Göstergesi', 'İlişki Tipi', 'Notlar')
        self.ungc_gri_tree = ttk.Treeview(self.ungc_gri_frame, columns=columns, show='headings', height=15)

        # Başlık ve hücreleri ortala
        for col in columns:
            self.ungc_gri_tree.heading(col, text=col, anchor='center')
            self.ungc_gri_tree.column(col, width=160, anchor='center')

        # Scrollbar
        ungc_gri_scrollbar = ttk.Scrollbar(self.ungc_gri_frame, orient='vertical', command=self.ungc_gri_tree.yview)
        self.ungc_gri_tree.configure(yscrollcommand=ungc_gri_scrollbar.set)

        self.ungc_gri_tree.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        ungc_gri_scrollbar.pack(side='right', fill='y', pady=10)

    def create_ungc_tsrs_tab(self) -> None:
        """UNGC-TSRS eşleştirmeleri tab'ı oluştur"""
        # Başlık
        title_label = tk.Label(self.ungc_tsrs_frame, text="UNGC-TSRS Eşleştirmeleri",
                             font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(pady=(20, 10))

        # Açıklama
        desc_label = tk.Label(self.ungc_tsrs_frame,
                             text="United Nations Global Compact 10 İlkesi ile TSRS Standartlarının Eşleştirmesi",
                             font=('Segoe UI', 10), fg='#7f8c8d', bg='white')
        desc_label.pack(pady=(0, 20))

        # Arama ve filtreleme
        search_frame = tk.Frame(self.ungc_tsrs_frame, bg='white')
        search_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(search_frame, text="Ara:", font=('Segoe UI', 10), bg='white').pack(side='left')
        self.ungc_tsrs_search = tk.Entry(search_frame, font=('Segoe UI', 10), width=30)
        self.ungc_tsrs_search.pack(side='left', padx=10)
        self.ungc_tsrs_search.bind('<KeyRelease>', lambda e: self.filter_ungc_tsrs())

        # Treeview
        columns = ('UNGC İlkesi', 'TSRS Bölüm', 'TSRS Metrik', 'İlişki Tipi', 'Notlar')
        self.ungc_tsrs_tree = ttk.Treeview(self.ungc_tsrs_frame, columns=columns, show='headings', height=15)

        # Başlık ve hücreleri ortala
        for col in columns:
            self.ungc_tsrs_tree.heading(col, text=col, anchor='center')
            self.ungc_tsrs_tree.column(col, width=160, anchor='center')

        # Scrollbar
        ungc_tsrs_scrollbar = ttk.Scrollbar(self.ungc_tsrs_frame, orient='vertical', command=self.ungc_tsrs_tree.yview)
        self.ungc_tsrs_tree.configure(yscrollcommand=ungc_tsrs_scrollbar.set)

        self.ungc_tsrs_tree.pack(side='left', fill='both', expand=True, padx=20, pady=10)
        ungc_tsrs_scrollbar.pack(side='right', fill='y', pady=10)

    def create_compliance_tab(self) -> None:
        """UNGC Uyum Durumu tab'ı oluştur"""
        # Başlık
        title_label = tk.Label(self.compliance_frame, text="UNGC Uyum Durumu",
                             font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(pady=(20, 10))

        # Açıklama
        desc_label = tk.Label(self.compliance_frame,
                             text="UNGC 10 İlkesi için Uyum Durumu ve İlerleme Takibi",
                             font=('Segoe UI', 10), fg='#7f8c8d', bg='white')
        desc_label.pack(pady=(0, 20))

        # UNGC İlkeleri Listesi
        self.create_ungc_principles_list()

    def create_ungc_principles_list(self) -> None:
        """UNGC 10 İlkesini listele"""
        principles_frame = tk.Frame(self.compliance_frame, bg='white')
        principles_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # UNGC İlkeleri
        ungc_principles = [
            ("İnsan Hakları", [
                "İlke 1: İş dünyası uluslararası ilan edilmiş insan haklarını desteklemeli ve saygı göstermeli",
                "İlke 2: İş dünyası insan hakları ihlallerinin ortağı olmamalı"
            ]),
            ("İşçi Hakları", [
                "İlke 3: İş dünyası örgütlenme özgürlüğünü ve toplu pazarlık hakkını tanımalı",
                "İlke 4: İş dünyası her türlü zorla çalıştırmayı ortadan kaldırmalı",
                "İlke 5: İş dünyası çocuk işçiliğini etkili bir şekilde ortadan kaldırmalı",
                "İlke 6: İş dünyası işe alma ve meslekte ayrımcılığı ortadan kaldırmalı"
            ]),
            ("Çevre", [
                "İlke 7: İş dünyası çevre sorunlarına karşı ihtiyatlı yaklaşım benimsemeli",
                "İlke 8: İş dünyası çevresel sorumluluğu artıracak girişimlerde bulunmalı",
                "İlke 9: İş dünyası çevre dostu teknolojilerin geliştirilmesini ve yaygınlaştırılmasını teşvik etmeli"
            ]),
            ("Yolsuzlukla Mücadele", [
                "İlke 10: İş dünyası rüşvet ve haraç dahil her türlü yolsuzlukla mücadele etmeli"
            ])
        ]

        # Canvas ve scrollbar
        canvas = tk.Canvas(principles_frame, bg='white')
        scrollbar = ttk.Scrollbar(principles_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for category, principles in ungc_principles:
            # Kategori başlığı
            category_frame = tk.Frame(scrollable_frame, bg='#3498db', relief='solid', bd=1)
            category_frame.pack(fill='x', pady=(0, 10))

            category_label = tk.Label(category_frame, text=category,
                                    font=('Segoe UI', 12, 'bold'), fg='white', bg='#3498db')
            category_label.pack(pady=10)

            # İlkeler
            for principle in principles:
                principle_frame = tk.Frame(scrollable_frame, bg='#ecf0f1', relief='solid', bd=1)
                principle_frame.pack(fill='x', pady=(0, 5))

                # Sol taraf - İlke metni
                text_frame = tk.Frame(principle_frame, bg='#ecf0f1')
                text_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

                principle_label = tk.Label(text_frame, text=principle,
                                         font=('Segoe UI', 10), fg='#2c3e50', bg='#ecf0f1',
                                         wraplength=600, justify='left')
                principle_label.pack(anchor='w')

                # Sağ taraf - Uyum durumu
                status_frame = tk.Frame(principle_frame, bg='#ecf0f1')
                status_frame.pack(side='right', padx=10, pady=10)

                # Uyum durumu seçimi
                status_var = tk.StringVar(value="Değerlendirilmedi")
                status_combo = ttk.Combobox(status_frame, textvariable=status_var,
                                          values=["Değerlendirilmedi", "Uyumlu", "Kısmen Uyumlu", "Uyumsuz"],
                                          state='readonly', width=15)
                status_combo.pack()

                # İlerleme yüzdesi
                progress_label = tk.Label(status_frame, text="İlerleme: 0%",
                                        font=('Segoe UI', 9), fg='#7f8c8d', bg='#ecf0f1')
                progress_label.pack(pady=(5, 0))

                # İlerleme barı
                progress_bar = ttk.Progressbar(status_frame, length=120, mode='determinate')
                progress_bar.pack()
                progress_bar['value'] = 0

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel binding
        def _on_mousewheel(event) -> None:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def create_analysis_tab(self) -> None:
        """Eşleştirme Analizi tab'ı oluştur"""
        # Başlık
        title_label = tk.Label(self.analysis_frame, text="Eşleştirme Analizi",
                             font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white')
        title_label.pack(pady=(20, 10))

        # Analiz kartları
        analysis_frame = tk.Frame(self.analysis_frame, bg='white')
        analysis_frame.pack(fill='x', padx=20, pady=20)

        # Analiz kartları oluştur
        analysis_cards = [
            ("UNGC-SDG Eşleştirme Oranı", "85%", "#3498db"),
            ("UNGC-GRI Eşleştirme Oranı", "78%", "#e67e22"),
            ("UNGC-TSRS Eşleştirme Oranı", "92%", "#27ae60"),
            ("Genel Uyum Skoru", "82%", "#9b59b6")
        ]

        for i, (title, value, color) in enumerate(analysis_cards):
            card_frame = tk.Frame(analysis_frame, bg=color, relief='solid', bd=1)
            card_frame.pack(side='left', fill='x', expand=True, padx=5)

            title_label = tk.Label(card_frame, text=title,
                                 font=('Segoe UI', 10, 'bold'), fg='white', bg=color)
            title_label.pack(pady=(10, 0))

            value_label = tk.Label(card_frame, text=value,
                                 font=('Segoe UI', 20, 'bold'), fg='white', bg=color)
            value_label.pack(pady=(0, 10))

        # Detaylı analiz
        detail_frame = tk.Frame(self.analysis_frame, bg='white')
        detail_frame.pack(fill='both', expand=True, padx=20, pady=20)

        detail_label = tk.Label(detail_frame, text="Detaylı Eşleştirme Analizi",
                               font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        detail_label.pack(anchor='w', pady=(0, 10))

        # Analiz metni
        analysis_text = tk.Text(detail_frame, height=10, width=80,
                               font=('Segoe UI', 10), bg='#f8f9fa', relief='solid', bd=1)
        analysis_text.pack(fill='both', expand=True)

        analysis_content = """
UNGC-SDG Eşleştirme Analizi:

• İnsan Hakları (İlke 1-2): SDG 16 (Barış ve Adalet) ile güçlü eşleştirme
• İşçi Hakları (İlke 3-6): SDG 8 (İnsana Yakışır İş) ile tam eşleştirme
• Çevre (İlke 7-9): SDG 6,7,12,13,14,15 ile kapsamlı eşleştirme
• Yolsuzlukla Mücadele (İlke 10): SDG 16 ile doğrudan eşleştirme

UNGC-GRI Eşleştirme Analizi:

• GRI 2 (Genel Açıklamalar): Tüm UNGC ilkeleri için temel yapı
• GRI 3 (Materyal Konular): UNGC ilkelerinin önceliklendirilmesi
• GRI 4xx (Çevresel): UNGC çevre ilkeleri ile güçlü eşleştirme
• GRI 5xx (Sosyal): UNGC insan hakları ve işçi hakları ile eşleştirme

UNGC-TSRS Eşleştirme Analizi:

• TSRS-E (Çevresel): UNGC çevre ilkeleri ile tam uyum
• TSRS-S (Sosyal): UNGC sosyal ilkeleri ile kapsamlı eşleştirme
• TSRS-G (Yönetişim): UNGC yolsuzlukla mücadele ilkesi ile eşleştirme

Öneriler:
• UNGC ilkelerinin tümü için detaylı politika dokümanları oluşturulmalı
• Düzenli uyum değerlendirmeleri yapılmalı
• Stakeholder katılımı artırılmalı
• Sürekli iyileştirme süreçleri kurulmalı
        """

        analysis_text.insert('1.0', analysis_content)
        analysis_text.config(state='disabled')

    def load_data(self) -> None:
        """Verileri yükle"""
        self.load_ungc_sdg_data()
        self.load_ungc_gri_data()
        self.load_ungc_tsrs_data()

    def load_ungc_sdg_data(self) -> None:
        """UNGC-SDG eşleştirme verilerini yükle"""
        # Örnek veri - gerçek uygulamada veritabanından gelecek
        sample_data = [
            ("İlke 1: İnsan Hakları", "SDG 16", "16.1.1", "Güçlü", "Doğrudan eşleştirme"),
            ("İlke 2: İnsan Hakları", "SDG 16", "16.1.2", "Güçlü", "Doğrudan eşleştirme"),
            ("İlke 3: İşçi Hakları", "SDG 8", "8.8.1", "Tam", "Örgütlenme özgürlüğü"),
            ("İlke 4: İşçi Hakları", "SDG 8", "8.7.1", "Tam", "Zorla çalıştırma"),
            ("İlke 5: İşçi Hakları", "SDG 8", "8.7.2", "Tam", "Çocuk işçiliği"),
            ("İlke 6: İşçi Hakları", "SDG 8", "8.5.1", "Güçlü", "Ayrımcılık"),
            ("İlke 7: Çevre", "SDG 13", "13.1.1", "Güçlü", "İklim değişikliği"),
            ("İlke 8: Çevre", "SDG 12", "12.2.1", "Güçlü", "Sürdürülebilir üretim"),
            ("İlke 9: Çevre", "SDG 7", "7.3.1", "Güçlü", "Temiz enerji"),
            ("İlke 10: Yolsuzlukla Mücadele", "SDG 16", "16.5.1", "Tam", "Yolsuzluk")
        ]

        # Treeview'ı temizle
        for item in self.ungc_sdg_tree.get_children():
            self.ungc_sdg_tree.delete(item)

        # Verileri ekle
        for row in sample_data:
            self.ungc_sdg_tree.insert('', 'end', values=row)

    def load_ungc_gri_data(self) -> None:
        """UNGC-GRI eşleştirme verilerini yükle"""
        # Örnek veri
        sample_data = [
            ("İlke 1-2: İnsan Hakları", "GRI 2", "2-22", "Güçlü", "İnsan hakları politikası"),
            ("İlke 3-6: İşçi Hakları", "GRI 2", "2-23", "Tam", "İşçi hakları politikası"),
            ("İlke 7-9: Çevre", "GRI 2", "2-24", "Güçlü", "Çevre politikası"),
            ("İlke 10: Yolsuzluk", "GRI 2", "2-25", "Tam", "Etik ve yolsuzlukla mücadele"),
            ("İlke 1-2: İnsan Hakları", "GRI 4", "4-1", "Güçlü", "İnsan hakları değerlendirmesi"),
            ("İlke 3-6: İşçi Hakları", "GRI 4", "4-2", "Tam", "İşçi hakları değerlendirmesi"),
            ("İlke 7-9: Çevre", "GRI 3", "3-1", "Güçlü", "Materyal konular"),
            ("İlke 10: Yolsuzluk", "GRI 3", "3-2", "Tam", "Materyal konu yönetimi")
        ]

        # Treeview'ı temizle
        for item in self.ungc_gri_tree.get_children():
            self.ungc_gri_tree.delete(item)

        # Verileri ekle
        for row in sample_data:
            self.ungc_gri_tree.insert('', 'end', values=row)

    def load_ungc_tsrs_data(self) -> None:
        """UNGC-TSRS eşleştirme verilerini yükle"""
        # Örnek veri
        sample_data = [
            ("İlke 1-2: İnsan Hakları", "TSRS-G", "G1", "Güçlü", "İş davranışı"),
            ("İlke 3-6: İşçi Hakları", "TSRS-S", "S1", "Tam", "Kendi işgücü"),
            ("İlke 3-6: İşçi Hakları", "TSRS-S", "S2", "Tam", "Değer zinciri işçileri"),
            ("İlke 7-9: Çevre", "TSRS-E", "E1", "Tam", "İklim değişikliği"),
            ("İlke 7-9: Çevre", "TSRS-E", "E2", "Güçlü", "Kirlilik"),
            ("İlke 7-9: Çevre", "TSRS-E", "E3", "Güçlü", "Su ve deniz kaynakları"),
            ("İlke 7-9: Çevre", "TSRS-E", "E4", "Güçlü", "Biyoçeşitlilik"),
            ("İlke 7-9: Çevre", "TSRS-E", "E5", "Güçlü", "Kaynak kullanımı"),
            ("İlke 10: Yolsuzluk", "TSRS-G", "G1", "Tam", "İş davranışı")
        ]

        # Treeview'ı temizle
        for item in self.ungc_tsrs_tree.get_children():
            self.ungc_tsrs_tree.delete(item)

        # Verileri ekle
        for row in sample_data:
            self.ungc_tsrs_tree.insert('', 'end', values=row)

    def filter_ungc_sdg(self) -> None:
        """UNGC-SDG eşleştirmelerini filtrele"""
        search_term = self.ungc_sdg_search.get().lower()

        for item in self.ungc_sdg_tree.get_children():
            values = self.ungc_sdg_tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                self.ungc_sdg_tree.reattach(item, '', 'end')
            else:
                self.ungc_sdg_tree.detach(item)

    def filter_ungc_gri(self) -> None:
        """UNGC-GRI eşleştirmelerini filtrele"""
        search_term = self.ungc_gri_search.get().lower()

        for item in self.ungc_gri_tree.get_children():
            values = self.ungc_gri_tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                self.ungc_gri_tree.reattach(item, '', 'end')
            else:
                self.ungc_gri_tree.detach(item)

    def filter_ungc_tsrs(self) -> None:
        """UNGC-TSRS eşleştirmelerini filtrele"""
        search_term = self.ungc_tsrs_search.get().lower()

        for item in self.ungc_tsrs_tree.get_children():
            values = self.ungc_tsrs_tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                self.ungc_tsrs_tree.reattach(item, '', 'end')
            else:
                self.ungc_tsrs_tree.detach(item)
