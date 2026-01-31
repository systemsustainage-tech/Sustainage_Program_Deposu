#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doküman Karşılaştırma GUI
Kullanıcı dostu doküman analiz arayüzü
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict

from utils.language_manager import LanguageManager

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tools.document_comparison import DocumentComparison
from config.database import DB_PATH


class DocumentComparisonGUI:
    """Doküman karşılaştırma GUI"""
    
    def __init__(self, parent, company_id: int, db_path: str) -> None:
        self.parent = parent
        self.company_id = company_id
        self.db_path = db_path
        self.lm = LanguageManager()
        self.comparator = DocumentComparison(db_path)
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """UI oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        # Başlık
        header_frame = tk.Frame(main_frame, bg='#8b5cf6', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=" Doküman Karşılaştırma ve Analiz", 
                font=('Segoe UI', 16, 'bold'), fg='white', bg='#8b5cf6').pack(expand=True)
        
        # İçerik
        content_frame = tk.Frame(main_frame, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Dosya seçimi
        self.create_file_selection(content_frame)
        
        # Analiz sonuçları
        self.create_results_area(content_frame)
    
    def create_file_selection(self, parent) -> None:
        """Dosya seçim alanı"""
        file_frame = tk.LabelFrame(parent, text=" Doküman Seçimi", 
                                   font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        file_frame.pack(fill='x', pady=(0, 20))
        
        content = tk.Frame(file_frame, bg='white')
        content.pack(fill='x', padx=20, pady=20)
        
        # Dosya yolu
        tk.Label(content, text="Dosya:", font=('Segoe UI', 11, 'bold'), 
                fg='#2c3e50', bg='white').grid(row=0, column=0, sticky='w', pady=10)
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(content, textvariable=self.file_path_var, 
                             font=('Segoe UI', 11), width=50, state='readonly')
        file_entry.grid(row=0, column=1, padx=(10, 10), pady=10)
        
        tk.Button(content, text=" Dosya Seç", font=('Segoe UI', 10, 'bold'), 
                 fg='white', bg='#3b82f6', relief='flat', cursor='hand2',
                 command=self.select_file, padx=20, pady=8).grid(row=0, column=2, pady=10)
        
        # Analiz butonu
        self.analyze_btn = tk.Button(content, text=" Analiz Et", 
                                     font=('Segoe UI', 12, 'bold'), fg='white', 
                                     bg='#10b981', relief='flat', cursor='hand2',
                                     command=self.analyze_document, padx=40, pady=12,
                                     state='disabled')
        self.analyze_btn.grid(row=1, column=0, columnspan=3, pady=20)
        
        content.grid_columnconfigure(1, weight=1)
    
    def create_results_area(self, parent) -> None:
        """Sonuç alanı"""
        results_frame = tk.LabelFrame(parent, text=" Analiz Sonuçları", 
                                     font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white')
        results_frame.pack(fill='both', expand=True)
        
        # Notebook
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Özet sekmesi
        self.summary_tab = tk.Frame(self.results_notebook, bg='white')
        self.results_notebook.add(self.summary_tab, text=" Özet")
        
        self.summary_text = tk.Text(self.summary_tab, font=('Segoe UI', 10), 
                                    wrap='word', height=15)
        summary_scroll = ttk.Scrollbar(self.summary_tab, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scroll.set)
        self.summary_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        summary_scroll.pack(side='right', fill='y', pady=10)
        
        # Eksiklikler sekmesi
        self.gaps_tab = tk.Frame(self.results_notebook, bg='white')
        self.results_notebook.add(self.gaps_tab, text="️ Eksiklikler")
        
        columns = ('Kategori', 'Tip', 'Önem', 'Açıklama')
        self.gaps_tree = ttk.Treeview(self.gaps_tab, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.gaps_tree.heading(col, text=col)
            self.gaps_tree.column(col, width=150)
        
        gaps_scroll = ttk.Scrollbar(self.gaps_tab, orient="vertical", command=self.gaps_tree.yview)
        self.gaps_tree.configure(yscrollcommand=gaps_scroll.set)
        self.gaps_tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        gaps_scroll.pack(side='right', fill='y', pady=10)
        
        # Öneriler sekmesi
        self.recommendations_tab = tk.Frame(self.results_notebook, bg='white')
        self.results_notebook.add(self.recommendations_tab, text=" Öneriler")
        
        self.recommendations_text = tk.Text(self.recommendations_tab, font=('Segoe UI', 10), 
                                           wrap='word', height=15)
        rec_scroll = ttk.Scrollbar(self.recommendations_tab, command=self.recommendations_text.yview)
        self.recommendations_text.configure(yscrollcommand=rec_scroll.set)
        self.recommendations_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        rec_scroll.pack(side='right', fill='y', pady=10)
    
    def select_file(self) -> None:
        """Dosya seç"""
        filename = filedialog.askopenfilename(
            title=self.lm.tr("select_analysis_doc", "Analiz Edilecek Dokümanı Seç"),
            filetypes=[
                (self.lm.tr("all_supported", "Tüm Desteklenen"), "*.pdf;*.docx"),
                (self.lm.tr("file_pdf", "PDF Dosyaları"), "*.pdf"),
                (self.lm.tr("file_word", "Word Dosyaları"), "*.docx"),
                (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")
            ]
        )
        
        if filename:
            self.file_path_var.set(filename)
            self.analyze_btn.config(state='normal')
    
    def analyze_document(self) -> None:
        """Dokümanı analiz et"""
        file_path = self.file_path_var.get()
        
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("select_valid_file", "Lütfen geçerli bir dosya seçin!"))
            return
        
        # Progress dialog
        progress = tk.Toplevel(self.parent)
        progress.title(self.lm.tr("analyzing", "Analiz Ediliyor"))
        progress.geometry("400x150")
        progress.configure(bg='white')
        progress.grab_set()
        
        tk.Label(progress, text=self.lm.tr("analyzing_doc", "Doküman analiz ediliyor..."), 
                font=('Segoe UI', 12, 'bold'), bg='white').pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill='x')
        progress_bar.start()
        
        # Analizi thread'de çalıştır
        def run_analysis() -> None:
            try:
                comparison = self.comparator.compare_document_with_modules(file_path, self.company_id)
                
                # UI'yi güncelle
                self.parent.after(0, lambda: self.display_results(comparison))
                self.parent.after(0, progress.destroy)
                
            except Exception as e:
                err_msg = f"{self.lm.tr('analysis_error', 'Analiz hatası')}: {e}"
                self.parent.after(0, lambda: messagebox.showerror(self.lm.tr("error", "Hata"), err_msg))
                self.parent.after(0, progress.destroy)
        
        thread = threading.Thread(target=run_analysis, daemon=True)
        thread.start()
    
    def display_results(self, comparison: Dict) -> None:
        """Sonuçları göster"""
        if 'error' in comparison:
            messagebox.showerror("Hata", comparison['error'])
            return
        
        # Özet
        self.summary_text.delete('1.0', tk.END)
        
        summary = f"""DOKÜMAN ANALİZ SONUÇLARI

Dosya: {comparison['file_name']}
Analiz Tarihi: {comparison['analyzed_at']}
Metin Uzunluğu: {comparison['text_length']:,} karakter

ANAHTAR KELİME ANALİZİ:
"""
        
        for category, matches in comparison['keywords'].items():
            if matches:
                summary += f"\n{category}:\n"
                for keyword, count in matches[:5]:
                    summary += f"  • {keyword}: {count} kez\n"
        
        summary += f"\n\nBULUNAN METRİKLER: {len(comparison['metrics'])} adet\n"
        
        for metric in comparison['metrics'][:10]:
            summary += f"  • {metric['module']}.{metric['metric_type']}: {metric['value']}\n"
        
        self.summary_text.insert('1.0', summary)
        
        # Eksiklikler
        for item in self.gaps_tree.get_children():
            self.gaps_tree.delete(item)
        
        for gap in comparison['gaps']:
            severity_icon = {'high': '', 'medium': '', 'low': ''}.get(gap['severity'], '')
            self.gaps_tree.insert('', 'end', values=(
                gap['category'],
                gap['type'],
                f"{severity_icon} {gap['severity']}",
                gap['description'][:50]
            ))
        
        # Öneriler
        self.recommendations_text.delete('1.0', tk.END)
        
        recommendations = "ÖNERİLER:\n\n"
        for i, rec in enumerate(comparison['recommendations'], 1):
            recommendations += f"{i}. {rec}\n\n"
        
        self.recommendations_text.insert('1.0', recommendations)
        
        # Başarı mesajı
        messagebox.showinfo("Başarılı", 
            f"Doküman başarıyla analiz edildi!\n\n"
            f"Anahtar Kelime Kategorisi: {len([k for k in comparison['keywords'].values() if k])}\n"
            f"Bulunan Metrik: {len(comparison['metrics'])}\n"
            f"Tespit Edilen Eksiklik: {len(comparison['gaps'])}")

# Standalone test
def test_gui() -> None:
    """GUI'yi test et"""
    root = tk.Tk()
    root.title("Doküman Karşılaştırma Test")
    root.geometry("1000x700")
    
    db_path = DB_PATH
    DocumentComparisonGUI(root, company_id=1, db_path=db_path)
    
    root.mainloop()

if __name__ == '__main__':
    test_gui()
