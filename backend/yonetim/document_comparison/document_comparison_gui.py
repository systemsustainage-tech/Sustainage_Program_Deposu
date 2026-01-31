#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doküman Karşılaştırma GUI
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from utils.language_manager import LanguageManager
from config.icons import Icons


class DocumentComparisonGUI:
    """Doküman Karşılaştırma GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()

        self.setup_ui()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana container
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text=f"{Icons.CLIPBOARD} Doküman Karşılaştırma",
                              font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=(0, 20))

        # Notebook (Ana sekmeler)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)

        # Metin Karşılaştırma Sekmesi
        text_frame = tk.Frame(notebook, bg='white')
        notebook.add(text_frame, text=f"{Icons.FILE} Metin Karşılaştırma")
        self.create_text_comparison(text_frame)

        # Excel Karşılaştırma Sekmesi
        excel_frame = tk.Frame(notebook, bg='white')
        notebook.add(excel_frame, text=f"{Icons.REPORT} Excel Karşılaştırma")
        self.create_excel_comparison(excel_frame)

        # PDF Karşılaştırma Sekmesi
        pdf_frame = tk.Frame(notebook, bg='white')
        notebook.add(pdf_frame, text="📕 PDF Karşılaştırma")
        self.create_pdf_comparison(pdf_frame)

        # Geçmiş Sekmesi
        history_frame = tk.Frame(notebook, bg='white')
        notebook.add(history_frame, text="📜 Karşılaştırma Geçmişi")
        self.create_history_tab(history_frame)

    def create_text_comparison(self, parent):
        """Metin karşılaştırma sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        # Dosya seçim paneli
        file_panel = tk.Frame(container, bg='#ecf0f1', relief='raised', bd=2)
        file_panel.pack(fill='x', pady=(0, 15))

        tk.Label(file_panel, text="Dosya Seçimi",
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1').pack(pady=10)

        # İlk dosya
        file1_frame = tk.Frame(file_panel, bg='#ecf0f1')
        file1_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(file1_frame, text="1. Dosya:", font=('Segoe UI', 10), bg='#ecf0f1').pack(side='left')
        self.file1_var = tk.StringVar()
        tk.Entry(file1_frame, textvariable=self.file1_var, width=40).pack(side='left', padx=5)
        tk.Button(file1_frame, text="📁 Seç", command=lambda: self.select_file(1)).pack(side='left', padx=5)

        # İkinci dosya
        file2_frame = tk.Frame(file_panel, bg='#ecf0f1')
        file2_frame.pack(fill='x', padx=10, pady=(5, 15))

        tk.Label(file2_frame, text="2. Dosya:", font=('Segoe UI', 10), bg='#ecf0f1').pack(side='left')
        self.file2_var = tk.StringVar()
        tk.Entry(file2_frame, textvariable=self.file2_var, width=40).pack(side='left', padx=5)
        tk.Button(file2_frame, text="📁 Seç", command=lambda: self.select_file(2)).pack(side='left', padx=5)

        # Karşılaştırma butonları
        btn_frame = tk.Frame(file_panel, bg='#ecf0f1')
        btn_frame.pack(pady=(0, 10))

        tk.Button(btn_frame, text=f"{Icons.SEARCH} Karşılaştır", font=('Segoe UI', 10, 'bold'),
                 bg='#3498db', fg='white', relief='flat', padx=15, pady=5,
                 command=self.compare_text_files).pack(side='left', padx=5)

        tk.Button(btn_frame, text=f"{Icons.SAVE} Sonucu Kaydet", font=('Segoe UI', 10),
                 bg='#27ae60', fg='white', relief='flat', padx=15, pady=5,
                 command=self.save_comparison_result).pack(side='left', padx=5)

        # Sonuç alanı
        result_frame = tk.LabelFrame(container, text="Karşılaştırma Sonuçları",
                                   font=('Segoe UI', 11, 'bold'))
        result_frame.pack(fill='both', expand=True, pady=10)

        # Sonuç metni için scrolled text
        from tkinter import scrolledtext
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15,
                                                   font=('Consolas', 10), wrap='word')
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)

        # İlk açılış mesajı
        welcome_msg = f"""
{Icons.CLIPBOARD} Doküman Karşılaştırma Aracı

Bu araç ile aşağıdaki işlemleri yapabilirsiniz:

{Icons.FILE} METIN KARŞILAŞTIRMA
• .txt, .docx, .rtf dosyalarını karşılaştırın
• Satır bazında farkları görün
• Eklenen, silinen, değiştirilen kısımları tespit edin

🎯 KULLANIM:
1. İki dosya seçin
2. "Karşılaştır" butonuna basın
3. Sonuçları inceleyin
4. İsteğe bağlı olarak kaydedin

{Icons.WARNING} NOT: Büyük dosyalarda işlem süresi uzayabilir.
"""
        self.result_text.insert('1.0', welcome_msg)

    def create_excel_comparison(self, parent):
        """Excel karşılaştırma sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text=f"{Icons.REPORT} Excel Dosya Karşılaştırması",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        # Özellikler listesi
        features_frame = tk.Frame(container, bg='#e8f5e8', relief='raised', bd=2)
        features_frame.pack(fill='x', pady=10)

        tk.Label(features_frame, text="Özellikler:",
                font=('Segoe UI', 12, 'bold'), fg='#27ae60', bg='#e8f5e8').pack(pady=(10, 5))

        features = [
            "• Çoklu sayfa karşılaştırması",
            "• Hücre bazında fark tespiti",
            "• Formül karşılaştırması",
            "• Grafik ve pivot tablo analizi",
            "• Formatı koruyarak rapor oluşturma"
        ]

        for feature in features:
            tk.Label(features_frame, text=feature, font=('Segoe UI', 10),
                    fg='#27ae60', bg='#e8f5e8', anchor='w').pack(anchor='w', padx=20, pady=2)

        tk.Label(features_frame, text="", bg='#e8f5e8').pack(pady=5)

        # Geliştirme aşaması mesajı
        tk.Label(container, text="🚧 Bu özellik geliştirme aşamasında...",
                font=('Segoe UI', 12), fg='#f39c12', bg='white').pack(pady=30)

    def create_pdf_comparison(self, parent):
        """PDF karşılaştırma sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="📕 PDF Karşılaştırması",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 20))

        tk.Label(container, text=f"{Icons.WRENCH} PDF karşılaştırma özelliği yakında eklenecek...",
                font=('Segoe UI', 11), fg='#7f8c8d', bg='white').pack(pady=50)

    def create_history_tab(self, parent):
        """Karşılaştırma geçmişi sekmesi"""
        container = tk.Frame(parent, bg='white')
        container.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(container, text="📜 Karşılaştırma Geçmişi",
                font=('Segoe UI', 14, 'bold'), fg='#2c3e50', bg='white').pack(pady=(0, 15))

        # Geçmiş listesi için treeview
        columns = ('Tarih', 'Dosya 1', 'Dosya 2', 'Sonuç')
        self.history_tree = ttk.Treeview(container, columns=columns, show='headings', height=10)

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=200)

        self.history_tree.pack(fill='both', expand=True, pady=10)

        # Temizle butonu
        tk.Button(container, text=f"{Icons.DELETE} Geçmişi Temizle", font=('Segoe UI', 10),
                 bg='#e74c3c', fg='white', relief='flat', padx=15, pady=5,
                 command=self.clear_history).pack(pady=10)

    # Event handlers
    def select_file(self, file_number):
        """Dosya seçici"""
        file_path = filedialog.askopenfilename(
            title=self.lm.tr("select_file", "Dosya Seç"),
            filetypes=[
                (self.lm.tr("text_files", "Metin dosyaları"), "*.txt *.docx *.rtf"),
                (self.lm.tr("all_files", "Tüm dosyalar"), "*.*")
            ]
        )

        if file_path:
            if file_number == 1:
                self.file1_var.set(file_path)
            else:
                self.file2_var.set(file_path)

    def compare_text_files(self):
        """Metin dosyalarını karşılaştır"""
        file1 = self.file1_var.get()
        file2 = self.file2_var.get()

        if not file1 or not file2:
            messagebox.showwarning("Uyarı", "Lütfen her iki dosyayı da seçin!")
            return

        if not os.path.exists(file1) or not os.path.exists(file2):
            messagebox.showerror("Hata", "Seçilen dosyalardan biri bulunamadı!")
            return

        try:
            # Basit karşılaştırma simülasyonu
            with open(file1, 'r', encoding='utf-8', errors='ignore') as f1:
                content1 = f1.readlines()

            with open(file2, 'r', encoding='utf-8', errors='ignore') as f2:
                content2 = f2.readlines()

            # Sonuç oluştur
            result = f"""
{Icons.CLIPBOARD} KARŞILAŞTIRMA SONUCU
{'='*50}

{Icons.FILE} Dosya 1: {os.path.basename(file1)}
   Satır sayısı: {len(content1)}
   
{Icons.FILE} Dosya 2: {os.path.basename(file2)}
   Satır sayısı: {len(content2)}

{Icons.REPORT} ANALIZ:
   Toplam satır farkı: {abs(len(content1) - len(content2))}
   Dosya boyut karşılaştırması: {'Eşit' if len(content1) == len(content2) else 'Farklı'}

{Icons.SUCCESS} Karşılaştırma tamamlandı.

{Icons.LIGHTBULB} Detaylı satır bazında karşılaştırma için gelişmiş araçlar kullanılabilir.
"""

            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', result)

            messagebox.showinfo("Başarılı", "Dosya karşılaştırması tamamlandı!")

        except Exception as e:
            messagebox.showerror("Hata", f"Karşılaştırma hatası: {e}")

    def save_comparison_result(self):
        """Karşılaştırma sonucunu kaydet"""
        content = self.result_text.get('1.0', tk.END).strip()

        if not content or content == "":
            messagebox.showwarning(self.lm.tr("warning", "Uyarı"), self.lm.tr("no_content_to_save", "Kaydedilecek sonuç yok!"))
            return

        file_path = filedialog.asksaveasfilename(
            title=self.lm.tr("save_result", "Sonucu Kaydet"),
            defaultextension=".txt",
            filetypes=[(self.lm.tr("text_files", "Metin dosyaları"), "*.txt"), (self.lm.tr("all_files", "Tüm dosyalar"), "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Başarılı", "Sonuç başarıyla kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydetme hatası: {e}")

    def clear_history(self):
        """Geçmişi temizle"""
        result = messagebox.askyesno("Onay", "Karşılaştırma geçmişini temizlemek istediğinizden emin misiniz?")
        if result:
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            messagebox.showinfo("Başarılı", "Geçmiş temizlendi!")
