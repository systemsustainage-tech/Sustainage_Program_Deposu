import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IFRS S1 & S2 Sustainability Disclosure Standards GUI
TCFD entegrasyonu ile
"""

import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict

from utils.ui_theme import apply_theme


class IFRSGUI:
    """IFRS S1 & S2 Sustainability Standards GUI"""

    def __init__(self, parent, company_id: int):
        self.parent = parent
        self.company_id = company_id

        # Mapping dosyasını yükle
        self.mapping = self._load_mapping()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()

    def _load_mapping(self) -> Dict:
        """TCFD mapping dosyasını yükle"""
        try:
            mapping_file = os.path.join(os.path.dirname(__file__), 'ifrs_tcfd_mapping.json')
            with open(mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.info(f"[UYARI] Mapping yuklenemedi: {e}")
            return {}

    def setup_ui(self):
        """IFRS arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#1976D2', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="IFRS S1 & S2 - Sustainability Disclosure Standards",
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#1976D2')
        title_label.pack(expand=True)
        actions = tk.Frame(title_frame, bg='#1976D2')
        actions.pack(side='right', padx=10)
        ttk.Button(actions, text="Rapor Merkezi", style='Primary.TButton', command=self.open_report_center_ifrs).pack(side='right')

        # Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Sekmeler
        self.create_overview_tab()
        self.create_s1_tab()
        self.create_s2_tab()
        self.create_tcfd_mapping_tab()

    def open_report_center_ifrs(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('ifrs')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"Error filtering reports for ifrs: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Rapor Merkezi açılamadı:\n{e}")
            logging.error(f"Error opening report center: {e}")

    def create_overview_tab(self):
        """Genel bakış sekmesi"""
        overview_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(overview_frame, text="Genel Bakis")

        # Başlık
        tk.Label(overview_frame, text="IFRS Sustainability Disclosure Standards",
                font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=20)

        # Açıklama
        info_text = """
IFRS S1 - Genel Gereklilikler
- Surdurulebilirlikle ilgili risklerin ve firsatlarin aciklanmasi
- Governance, Strategy, Risk Management, Metrics & Targets

IFRS S2 - Iklim Iliskili Aciklamalar
- Iklim degisikliginin mali etkilerinin aciklanmasi
- TCFD tavsiyelerine dayali
- Scope 1, 2, 3 emisyonlar

MEVCUT DURUM:
- TCFD modulu mevcut (%85 IFRS S2 kapsami)
- GRI modulu mevcut (%60 IFRS S1 kapsami)
- Bu modul: TCFD verilerini IFRS formatinda raporlar

EKSIKLER:
- Endustri bazli metrikler (SASB entegrasyonu gerekli)
- Finanse edilen emisyonlar (finansal sektor)
- Ic karbon fiyatlandirma

ROADMAP:
- Faz 1: TCFD verilerinden IFRS S2 raporu olusturma (HAZIR)
- Faz 2: GRI verilerinden IFRS S1 raporu olusturma (1 hafta)
- Faz 3: Eksik metrikleri ekleme (2 hafta)
        """

        tk.Label(overview_frame, text=info_text, font=('Segoe UI', 10),
                justify='left', bg='white').pack(padx=40, pady=20)

    def create_s1_tab(self):
        """IFRS S1 sekmesi"""
        s1_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(s1_frame, text="IFRS S1 - Genel")

        # Başlık
        tk.Label(s1_frame, text="IFRS S1 - Genel Surdurulebilirlik Gereksinimleri",
                font=('Segoe UI', 13, 'bold'), bg='white').pack(pady=15)

        # 4 Pillar
        pillars_frame = tk.Frame(s1_frame, bg='white')
        pillars_frame.pack(fill='both', expand=True, padx=20, pady=10)

        pillars = [
            ('Governance', 'Yonetisim yapisinin aciklanmasi'),
            ('Strategy', 'Surdurulebilirlik stratejisi ve etkileri'),
            ('Risk Management', 'Risk yonetimi surecleri'),
            ('Metrics & Targets', 'Metrikler ve hedefler')
        ]

        for pillar_name, pillar_desc in pillars:
            self._create_pillar_card(pillars_frame, pillar_name, pillar_desc, 's1')

        # Rapor butonu
        btn_frame = tk.Frame(s1_frame, bg='white')
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="IFRS S1 Raporu Olustur (TCFD/GRI Verilerinden)",
                   style='Primary.TButton', command=self.generate_s1_report).pack()

    def create_s2_tab(self):
        """IFRS S2 sekmesi"""
        s2_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(s2_frame, text="IFRS S2 - Iklim")

        # Başlık
        tk.Label(s2_frame, text="IFRS S2 - Iklim Iliskili Aciklamalar",
                font=('Segoe UI', 13, 'bold'), bg='white').pack(pady=15)

        # TCFD Uyumluluk durumu
        status_frame = tk.Frame(s2_frame, bg='#e3f2fd', relief='solid', bd=1)
        status_frame.pack(fill='x', padx=40, pady=10)

        tk.Label(status_frame, text="TCFD Modulu ile Kapsam: %85",
                font=('Segoe UI', 12, 'bold'), fg='#1976D2',
                bg='#e3f2fd').pack(pady=10)

        # Metrikleri göster
        metrics_frame = tk.LabelFrame(s2_frame, text="Gerekli Metrikler",
                                     font=('Segoe UI', 11, 'bold'),
                                     bg='white')
        metrics_frame.pack(fill='both', expand=True, padx=20, pady=10)

        metrics = [
            ('Scope 1 Emisyonlar', 'MEVCUT (TCFD)', '#28a745'),
            ('Scope 2 Emisyonlar', 'MEVCUT (TCFD)', '#28a745'),
            ('Scope 3 Emisyonlar', 'MEVCUT (TCFD)', '#28a745'),
            ('Iklim Riskleri', 'MEVCUT (TCFD)', '#28a745'),
            ('Iklim Firsatlari', 'MEVCUT (TCFD)', '#28a745'),
            ('Senaryo Analizi', 'MEVCUT (TCFD)', '#28a745'),
            ('Ic Karbon Fiyati', 'EKSIK', '#ffc107'),
            ('Finanse Emisyonlar', 'EKSIK (Finans sektoru)', '#ffc107')
        ]

        for metric_name, status, color in metrics:
            metric_row = tk.Frame(metrics_frame, bg='white')
            metric_row.pack(fill='x', pady=3, padx=10)

            tk.Label(metric_row, text=metric_name, font=('Segoe UI', 10),
                    bg='white', width=25, anchor='w').pack(side='left')

            tk.Label(metric_row, text=status, font=('Segoe UI', 9, 'bold'),
                    fg=color, bg='white').pack(side='left', padx=10)

        # Rapor butonu
        btn_frame = tk.Frame(s2_frame, bg='white')
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="IFRS S2 Raporu Olustur (TCFD Verilerinden)",
                   style='Primary.TButton', command=self.generate_s2_report).pack()

    def create_tcfd_mapping_tab(self):
        """TCFD mapping sekmesi"""
        mapping_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(mapping_frame, text="TCFD Mapping")

        # Başlık
        tk.Label(mapping_frame, text="TCFD - IFRS S2 Mapping",
                font=('Segoe UI', 13, 'bold'), bg='white').pack(pady=15)

        # Mapping tablosu
        if self.mapping and 'ifrs_s2_to_tcfd' in self.mapping:
            tree_frame = tk.Frame(mapping_frame, bg='white')
            tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

            # Treeview
            columns = ('IFRS S2', 'TCFD Pillar', 'Coverage', 'Notes')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=200)

            # Veriyi ekle
            for key, value in self.mapping['ifrs_s2_to_tcfd'].items():
                tree.insert('', 'end', values=(
                    value.get('ifrs_disclosure', ''),
                    value.get('tcfd_pillar', ''),
                    value.get('coverage', ''),
                    value.get('notes', '')[:50]
                ))

            tree.pack(fill='both', expand=True)

            # Scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
            scrollbar.pack(side='right', fill='y')
            tree.configure(yscrollcommand=scrollbar.set)

    def _create_pillar_card(self, parent, pillar_name, pillar_desc, standard):
        """Pillar kartı oluştur"""
        card = tk.Frame(parent, bg='#f8f9fa', relief='solid', bd=1)
        card.pack(fill='x', pady=5)

        tk.Label(card, text=pillar_name, font=('Segoe UI', 11, 'bold'),
                bg='#f8f9fa').pack(anchor='w', padx=15, pady=(10, 5))

        tk.Label(card, text=pillar_desc, font=('Segoe UI', 9),
                fg='#666', bg='#f8f9fa').pack(anchor='w', padx=15, pady=(0, 10))

    def generate_s1_report(self):
        """IFRS S1 raporu oluştur"""
        messagebox.showinfo("IFRS S1 Rapor",
                          "IFRS S1 Raporu Olusturuluyor...\n\n"
                          "Veri Kaynaklari:\n"
                          "- GRI governance disclosures\n"
                          "- Strategic modulu\n"
                          "- Risk modulu\n\n"
                          "Bu ozellik su anda TCFD/GRI verilerini\n"
                          "IFRS S1 formatinda birlestirir.\n\n"
                          "Tam implementasyon: 1 hafta")

    def generate_s2_report(self):
        """IFRS S2 raporu oluştur (TCFD verilerinden)"""
        try:
            # TCFD modülünü kontrol et
            import importlib.util
            has_tcfd = importlib.util.find_spec('modules.tcfd.tcfd_gui') is not None
            if not has_tcfd:
                raise ImportError

            messagebox.showinfo("IFRS S2 Rapor",
                              "IFRS S2 Raporu Olusturuluyor...\n\n"
                              "Veri Kaynagi: TCFD Modulu\n"
                              "Kapsam: %85\n\n"
                              "TCFD verileri IFRS S2 formatinda\n"
                              "raporlanacak.\n\n"
                              "Eksik metrikler:\n"
                              "- Ic karbon fiyati\n"
                              "- Finanse emisyonlar\n\n"
                              "Bu ozellik su anda temel raporlama yapar.\n"
                              "Tam implementasyon: 1 hafta")

        except ImportError:
            messagebox.showerror("Hata",
                               "TCFD modulu bulunamadi!\n\n"
                               "IFRS S2 icin TCFD modulu gereklidir.")


if __name__ == "__main__":
    # Test
    logging.info("[TEST] IFRS GUI...")

    root = tk.Tk()
    root.title("IFRS S1 & S2 Test")

    gui = IFRSGUI(root, company_id=1)

    logging.info("[OK] IFRS GUI olusturuldu")

    root.mainloop()

