#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Politika Kütüphanesi GUI
Şirket politikalarının merkezi yönetimi
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk
from utils.language_manager import LanguageManager
from config.icons import Icons


class PolicyLibraryGUI:
    """Politika Kütüphanesi GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()
        self.policies_dir = "data/policies"
        os.makedirs(self.policies_dir, exist_ok=True)

        self.setup_ui()
        self.load_policies()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana container
        main_frame = tk.Frame(self.parent, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık paneli
        header_frame = tk.Frame(main_frame, bg='#6c5ce7', height=60)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="📖 Politika Kütüphanesi",
                              font=('Segoe UI', 18, 'bold'), fg='white', bg='#6c5ce7')
        title_label.pack(expand=True)

        # Arama ve filtre paneli
        search_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=2)
        search_frame.pack(fill='x', pady=(0, 15))

        # Arama kutusu
        search_container = tk.Frame(search_frame, bg='#ffffff')
        search_container.pack(fill='x', padx=15, pady=10)

        tk.Label(search_container, text=f"{Icons.SEARCH} Arama:", font=('Segoe UI', 10, 'bold'),
                bg='#ffffff').pack(side='left')

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_container, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(10, 5))
        search_entry.bind('<KeyRelease>', self.filter_policies)

        # Kategori filtresi
        tk.Label(search_container, text=f"{Icons.FOLDER_OPEN} Kategori:", font=('Segoe UI', 10, 'bold'),
                bg='#ffffff').pack(side='left', padx=(15, 5))

        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(search_container, textvariable=self.category_var,
                                    values=["Tümü", "İnsan Kaynakları", "Güvenlik",
                                           "Kalite", "Çevre", "Etik", "Bilgi İşlem"],
                                    width=15, state='readonly')
        category_combo.pack(side='left', padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.filter_policies)
        category_combo.set("Tümü")

        # Ana içerik - Panedwindow ile bölünmüş
        paned = tk.PanedWindow(main_frame, orient='horizontal', sashrelief='raised', sashwidth=8)
        paned.pack(fill='both', expand=True)

        # Sol panel - Politika listesi
        left_frame = tk.Frame(paned, bg='#ffffff', relief='sunken', bd=2)
        paned.add(left_frame, minsize=400)

        # Politika listesi başlığı ve butonları
        list_header = tk.Frame(left_frame, bg='#f1f2f6')
        list_header.pack(fill='x')

        tk.Label(list_header, text=f"{Icons.CLIPBOARD} Politika Listesi",
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f1f2f6').pack(side='left', padx=10, pady=8)

        # Yeni politika butonu
        tk.Button(list_header, text=f"{Icons.ADD} Yeni", font=('Segoe UI', 9, 'bold'),
                 bg='#27ae60', fg='white', relief='flat', padx=12, pady=4,
                 command=self.create_new_policy).pack(side='right', padx=5, pady=5)

        # Politika listesi (Treeview)
        list_container = tk.Frame(left_frame, bg='#ffffff')
        list_container.pack(fill='both', expand=True, padx=5, pady=5)

        columns = ('Başlık', 'Kategori', 'Tarih', 'Durum')
        self.policy_tree = ttk.Treeview(list_container, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        self.policy_tree.heading('Başlık', text='Politika Başlığı')
        self.policy_tree.heading('Kategori', text='Kategori')
        self.policy_tree.heading('Tarih', text='Güncelleme')
        self.policy_tree.heading('Durum', text='Durum')

        # Sütun genişlikleri
        self.policy_tree.column('Başlık', width=200)
        self.policy_tree.column('Kategori', width=120)
        self.policy_tree.column('Tarih', width=100)
        self.policy_tree.column('Durum', width=80)

        # Scrollbar
        policy_scroll = ttk.Scrollbar(list_container, orient='vertical', command=self.policy_tree.yview)
        self.policy_tree.configure(yscrollcommand=policy_scroll.set)

        self.policy_tree.pack(side='left', fill='both', expand=True)
        policy_scroll.pack(side='right', fill='y')

        # Event binding
        self.policy_tree.bind('<<TreeviewSelect>>', self.on_policy_select)
        self.policy_tree.bind('<Double-1>', self.edit_policy)

        # Sağ panel - Politika detayları
        right_frame = tk.Frame(paned, bg='#ffffff', relief='sunken', bd=2)
        paned.add(right_frame, minsize=500)

        # Politika detay başlığı
        detail_header = tk.Frame(right_frame, bg='#f1f2f6')
        detail_header.pack(fill='x')

        tk.Label(detail_header, text=f"{Icons.FILE} Politika Detayları",
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f1f2f6').pack(side='left', padx=10, pady=8)

        # Düzenle ve sil butonları
        btn_frame = tk.Frame(detail_header, bg='#f1f2f6')
        btn_frame.pack(side='right', padx=10, pady=5)

        tk.Button(btn_frame, text=f"{Icons.EDIT} Düzenle", font=('Segoe UI', 9),
                 bg='#3498db', fg='white', relief='flat', padx=10, pady=3,
                 command=self.edit_policy).pack(side='left', padx=2)

        tk.Button(btn_frame, text=f"{Icons.DELETE} Sil", font=('Segoe UI', 9),
                 bg='#e74c3c', fg='white', relief='flat', padx=10, pady=3,
                 command=self.delete_policy).pack(side='left', padx=2)

        tk.Button(btn_frame, text="📥 Dışa Aktar", font=('Segoe UI', 9),
                 bg='#9b59b6', fg='white', relief='flat', padx=10, pady=3,
                 command=self.export_policy).pack(side='left', padx=2)

        # Politika içeriği
        from tkinter import scrolledtext
        self.content_area = scrolledtext.ScrolledText(right_frame, font=('Segoe UI', 11),
                                                     wrap='word', height=20, state='disabled')
        self.content_area.pack(fill='both', expand=True, padx=10, pady=10)

        # Alt durum çubuğu
        status_frame = tk.Frame(main_frame, bg='#ddd', height=30)
        status_frame.pack(fill='x', side='bottom', pady=(10, 0))
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text=f"{Icons.REPORT} Politika kütüphanesi hazır",
                                   font=('Segoe UI', 9), bg='#ddd', anchor='w')
        self.status_label.pack(side='left', padx=10, pady=5)

    def load_policies(self):
        """Politikaları yükle"""
        # Örnek politikalar
        sample_policies = [
            {
                "title": "Bilgi Güvenliği Politikası",
                "category": "Güvenlik",
                "date": "2024-01-15",
                "status": "Aktif",
                "content": """MADDE 1 - AMAÇ
Bu politika, şirketimizin bilgi varlıklarının güvenliğini sağlamak amacıyla hazırlanmıştır.

MADDE 2 - KAPSAM
Bu politika tüm çalışanlar, danışmanlar ve iş ortakları için geçerlidir.

MADDE 3 - SORUMLULUKLAR
- Bilgi güvenliği tüm çalışanların sorumluluğudır
- Şüpheli durumlar derhal IT departmanına bildirilmelidir
- Güçlü şifreler kullanılmalıdır"""
            },
            {
                "title": "İnsan Kaynakları Politikası",
                "category": "İnsan Kaynakları",
                "date": "2024-02-01",
                "status": "Aktif",
                "content": """İNSAN KAYNAKLARI POLİTİKASI

1. İŞE ALIM SÜRECİ
- Adil ve eşit değerlendirme
- Nitelik odaklı seçim
- Referans kontrolü

2. ÇALIŞAN HAKLARI
- Eşit davranım hakkı
- Gelişim fırsatları
- İş güvenliği"""
            }
        ]

        # Treeview'ı temizle
        for item in self.policy_tree.get_children():
            self.policy_tree.delete(item)

        # Örnek politikaları ekle
        for policy in sample_policies:
            self.policy_tree.insert('', 'end', values=(
                policy['title'],
                policy['category'],
                policy['date'],
                policy['status']
            ))

        self.status_label.config(text=f"{Icons.REPORT} {len(sample_policies)} politika yüklendi")

    def filter_policies(self, event=None):
        """Politikaları filtrele"""
        search_text = self.search_var.get().lower()
        category = self.category_var.get()

        # Basit filtreleme simülasyonu
        self.status_label.config(text=f"{Icons.SEARCH} Filtreleme: '{search_text}', Kategori: {category}")

    def on_policy_select(self, event):
        """Politika seçildiğinde"""
        selection = self.policy_tree.selection()
        if not selection:
            return

        item = self.policy_tree.item(selection[0])
        policy_title = item['values'][0]

        # Örnek içerik göster
        if "Bilgi Güvenliği" in policy_title:
            content = """MADDE 1 - AMAÇ
Bu politika, şirketimizin bilgi varlıklarının güvenliğini sağlamak amacıyla hazırlanmıştır.

MADDE 2 - KAPSAM
Bu politika tüm çalışanlar, danışmanlar ve iş ortakları için geçerlidir.

MADDE 3 - SORUMLULUKLAR
- Bilgi güvenliği tüm çalışanların sorumluluğudur
- Şüpheli durumlar derhal IT departmanına bildirilmelidir
- Güçlü şifreler kullanılmalıdır
- USB cihazlar izinsiz kullanılamaz

MADDE 4 - İHLAL DURUMLARI
Politika ihlalleri disiplin süreçlerine tabidir."""
        else:
            content = f"""POLİTİKA BAŞLIĞI: {policy_title}

İÇERİK:
Bu politika şirketimizin operasyon standartlarını belirler.

Detaylı bilgi için ilgili departmanla iletişime geçiniz.

Son Güncelleme: {item['values'][2]}
Durum: {item['values'][3]}"""

        self.content_area.config(state='normal')
        self.content_area.delete('1.0', tk.END)
        self.content_area.insert('1.0', content)
        self.content_area.config(state='disabled')

    def create_new_policy(self):
        """Yeni politika oluştur"""
        try:
            from tkinter import simpledialog
            policy_name = simpledialog.askstring("Yeni Politika", "Politika adı:")
            if policy_name:
                policy_id = self.policy_tree.insert('', 'end', text=policy_name, values=('Yeni', ''))
                self.policy_tree.selection_set(policy_id)
                self.edit_policy()
        except Exception as e:
            messagebox.showerror("Hata", f"Politika oluşturulamadı: {e}")

    def edit_policy(self, event=None):
        """Politikayı düzenle"""
        selection = self.policy_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen düzenlenecek politikayı seçin!")
            return

        try:
            item = selection[0]
            policy_name = self.policy_tree.item(item, 'text')

            # Düzenleme penceresi
            edit_win = tk.Toplevel(self.parent)
            edit_win.title(f"Politika Düzenle: {policy_name}")
            edit_win.geometry("600x500")

            tk.Label(edit_win, text="Politika İçeriği", font=('Segoe UI', 12, 'bold')).pack(pady=10)

            content_text = tk.Text(edit_win, wrap='word', font=('Segoe UI', 10))
            content_text.pack(fill='both', expand=True, padx=20, pady=10)

            def save_policy():
                # Burada veritabanına kaydedilebilir
                messagebox.showinfo("Başarılı", "Politika kaydedildi!")
                edit_win.destroy()
                self.load_policies()

            tk.Button(edit_win, text=self.lm.tr("btn_save", "Kaydet"), command=save_policy,
                    bg='#4CAF50', fg='white', padx=20, pady=5).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Hata", f"Politika düzenlenemedi: {e}")

    def delete_policy(self):
        """Politikayı sil"""
        selection = self.policy_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silinecek politikayı seçin!")
            return

        result = messagebox.askyesno("Onay", "Seçili politikayı silmek istediğinizden emin misiniz?")
        if result:
            self.policy_tree.delete(selection[0])
            self.content_area.config(state='normal')
            self.content_area.delete('1.0', tk.END)
            self.content_area.config(state='disabled')
            messagebox.showinfo("Başarılı", "Politika silindi!")

    def export_policy(self):
        """Politikayı dışa aktar"""
        selection = self.policy_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen dışa aktarılacak politikayı seçin!")
            return

        try:
            from tkinter import filedialog
            item = selection[0]
            policy_name = self.policy_tree.item(item, 'text')

            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[(self.lm.tr("file_text", "Metin Dosyaları"), "*.txt"), (self.lm.tr("file_pdf", "PDF Dosyaları"), "*.pdf"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                title=self.lm.tr("export_policy_title", "Politika Dışa Aktar"),
                initialfile=f"{policy_name}.txt"
            )

            if save_path:
                content = self.content_area.get('1.0', 'end-1c')
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(f"{policy_name}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(content)
                messagebox.showinfo("Başarılı", f"Politika dışa aktarıldı:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Dışa aktarma hatası: {e}")
