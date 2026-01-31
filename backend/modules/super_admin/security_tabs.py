#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Super Admin Security Tabs
Yeni güvenlik sekmeleri: License, IP Control, Rate Limiting, Monitoring
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from .components.license_generator import LicenseGenerator
from config.icons import Icons


class SecurityTabsMixin:
    """Super Admin GUI için güvenlik sekmelerini ekleyen mixin"""

    def show_license_management(self):
        """Lisans Yönetimi Sekmesi"""
        self.clear_right_panel()

        # Başlık
        header = tk.Frame(self.right_frame, bg='#2ecc71', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"{Icons.KEY} LİSANS YÖNETİMİ",
            font=('Segoe UI', 16, 'bold'),
            bg='#2ecc71',
            fg='white'
        ).pack(pady=15)

        # İçerik notebook
        notebook = ttk.Notebook(self.right_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Lisans Generator
        gen_frame = tk.Frame(notebook, bg='white')
        notebook.add(gen_frame, text=" Lisans Oluştur")
        self._create_license_generator_tab(gen_frame)

        # Tab 2: Aktif Lisanslar
        list_frame = tk.Frame(notebook, bg='white')
        notebook.add(list_frame, text=" Aktif Lisanslar")
        self._create_license_list_tab(list_frame)

        # Tab 3: İstatistikler
        stats_frame = tk.Frame(notebook, bg='white')
        notebook.add(stats_frame, text=" İstatistikler")
        self._create_license_stats_tab(stats_frame)

    def _create_license_generator_tab(self, parent):
        """Lisans generator UI"""
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Form
        form_frame = tk.LabelFrame(scrollable_frame, text="Yeni Lisans Bilgileri",
                                   font=('Segoe UI', 12, 'bold'), bg='white', padx=20, pady=20)
        form_frame.pack(fill='x', padx=20, pady=20)

        # Company Name
        tk.Label(form_frame, text="Şirket Adı:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=10)
        company_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=40)
        company_entry.grid(row=0, column=1, pady=10, padx=10)

        # License Type
        tk.Label(form_frame, text="Lisans Tipi:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=10)
        license_type_var = tk.StringVar(value='trial')
        type_frame = tk.Frame(form_frame, bg='white')
        type_frame.grid(row=1, column=1, sticky='w', pady=10, padx=10)

        tk.Radiobutton(type_frame, text='Trial (30 gün)', variable=license_type_var,
                      value='trial', bg='white', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Radiobutton(type_frame, text='Standard', variable=license_type_var,
                      value='standard', bg='white', font=('Segoe UI', 9)).pack(side='left', padx=5)
        tk.Radiobutton(type_frame, text='Enterprise', variable=license_type_var,
                      value='enterprise', bg='white', font=('Segoe UI', 9)).pack(side='left', padx=5)

        # Duration
        tk.Label(form_frame, text="Süre (gün):", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=10)
        duration_var = tk.StringVar(value='365')
        duration_frame = tk.Frame(form_frame, bg='white')
        duration_frame.grid(row=2, column=1, sticky='w', pady=10, padx=10)

        tk.Radiobutton(duration_frame, text='30', variable=duration_var, value='30', bg='white').pack(side='left', padx=5)
        tk.Radiobutton(duration_frame, text='90', variable=duration_var, value='90', bg='white').pack(side='left', padx=5)
        tk.Radiobutton(duration_frame, text='365', variable=duration_var, value='365', bg='white').pack(side='left', padx=5)
        tk.Radiobutton(duration_frame, text='Unlimited', variable=duration_var, value='0', bg='white').pack(side='left', padx=5)

        # Max Users
        tk.Label(form_frame, text="Max Kullanıcı:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=3, column=0, sticky='w', pady=10)
        max_users_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=15)
        max_users_entry.insert(0, '10')
        max_users_entry.grid(row=3, column=1, sticky='w', pady=10, padx=10)

        # Contact Info
        tk.Label(form_frame, text="Email:", font=('Segoe UI', 10), bg='white').grid(row=4, column=0, sticky='w', pady=10)
        email_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=40)
        email_entry.grid(row=4, column=1, pady=10, padx=10)

        # Modules
        tk.Label(form_frame, text="Modüller:", font=('Segoe UI', 10, 'bold'), bg='white').grid(row=5, column=0, sticky='nw', pady=10)
        modules_frame = tk.Frame(form_frame, bg='white')
        modules_frame.grid(row=5, column=1, sticky='w', pady=10, padx=10)

        modules = ['GRI', 'TCFD', 'SASB', 'CDP', 'CSRD', 'SDG', 'UNGC', 'CBAM', 'Water', 'Waste']
        module_vars = {}
        for i, module in enumerate(modules):
            var = tk.BooleanVar(value=True)
            module_vars[module] = var
            tk.Checkbutton(modules_frame, text=module, variable=var, bg='white',
                          font=('Segoe UI', 9)).grid(row=i//5, column=i%5, sticky='w', padx=10, pady=2)

        # Hardware ID (optional)
        tk.Label(form_frame, text="Hardware ID:", font=('Segoe UI', 10), bg='white').grid(row=6, column=0, sticky='w', pady=10)
        hw_frame = tk.Frame(form_frame, bg='white')
        hw_frame.grid(row=6, column=1, sticky='w', pady=10, padx=10)

        hw_entry = tk.Entry(hw_frame, font=('Segoe UI', 9), width=30, state='disabled')
        hw_entry.pack(side='left', padx=5)

        bind_hw_var = tk.BooleanVar(value=False)
        tk.Checkbutton(hw_frame, text='Bu makineye bağla', variable=bind_hw_var, bg='white',
                      command=lambda: hw_entry.config(state='normal' if bind_hw_var.get() else 'disabled')).pack(side='left')

        # Buttons
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)

        def generate_license():
            try:
                company = company_entry.get().strip()
                if not company:
                    messagebox.showerror("Hata", "Şirket adı gerekli!")
                    return

                enabled_modules = [m for m, v in module_vars.items() if v.get()]
                if not enabled_modules:
                    messagebox.showerror("Hata", "En az bir modül seçilmeli!")
                    return

                lg = LicenseGenerator(self.db_path)

                hw_id = None
                if bind_hw_var.get():
                    hw_id = lg.get_hardware_id()
                    hw_entry.config(state='normal')
                    hw_entry.delete(0, tk.END)
                    hw_entry.insert(0, hw_id)
                    hw_entry.config(state='disabled')

                result = lg.generate_license_key(
                    company_name=company,
                    license_type=license_type_var.get(),
                    duration_days=int(duration_var.get()),
                    max_users=int(max_users_entry.get()),
                    enabled_modules=enabled_modules,
                    hardware_id=hw_id,
                    contact_email=email_entry.get()
                )

                if result['success']:
                    # Sonuç göster
                    result_window = tk.Toplevel(self.parent)
                    result_window.title("Lisans Oluşturuldu")
                    result_window.geometry("700x400")
                    result_window.configure(bg='white')

                    tk.Label(result_window, text=f"{Icons.SUCCESS} Lisans Başarıyla Oluşturuldu!",
                            font=('Segoe UI', 14, 'bold'), bg='white', fg='green').pack(pady=20)

                    tk.Label(result_window, text="Lisans Key:",
                            font=('Segoe UI', 10, 'bold'), bg='white').pack()

                    key_text = scrolledtext.ScrolledText(result_window, height=8, width=80,
                                                        font=('Courier', 9), wrap=tk.WORD)
                    key_text.pack(pady=10, padx=20)
                    key_text.insert('1.0', result['license_key'])
                    key_text.config(state='disabled')

                    info_text = f"""
Lisans ID: {result['license_id']}
Şirket: {company}
Tip: {license_type_var.get()}
Geçerlilik: {result['expires_at']}
Max Kullanıcı: {max_users_entry.get()}
Modüller: {', '.join(enabled_modules)}
                    """

                    tk.Label(result_window, text=info_text, font=('Segoe UI', 9),
                            bg='white', justify='left').pack(pady=10)

                    def copy_key():
                        result_window.clipboard_clear()
                        result_window.clipboard_append(result['license_key'])
                        messagebox.showinfo("Kopyalandı", "Lisans key panoya kopyalandı!")

                    tk.Button(result_window, text=f"{Icons.CLIPBOARD} Kopyala", font=('Segoe UI', 11, 'bold'),
                             bg='#3498db', fg='white', padx=20, pady=10, command=copy_key).pack(pady=10)

                else:
                    messagebox.showerror("Hata", result['message'])

            except Exception as e:
                messagebox.showerror("Hata", f"Lisans oluşturma hatası: {str(e)}")

        def get_current_hw():
            try:
                lg = LicenseGenerator()
                hw_id = lg.get_hardware_id()
                hw_entry.config(state='normal')
                hw_entry.delete(0, tk.END)
                hw_entry.insert(0, hw_id)
                bind_hw_var.set(True)
            except Exception as e:
                messagebox.showerror("Hata", f"Hardware ID alınamadı: {str(e)}")

        tk.Button(btn_frame, text=f"{Icons.KEY} Lisans Oluştur", font=('Segoe UI', 12, 'bold'),
                 bg='#27ae60', fg='white', padx=30, pady=12, command=generate_license).pack(side='left', padx=10)

        tk.Button(btn_frame, text="💻 Bu Makinenin HW ID'si", font=('Segoe UI', 10),
                 bg='#3498db', fg='white', padx=20, pady=10, command=get_current_hw).pack(side='left', padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_license_list_tab(self, parent):
        """Aktif lisanslar listesi"""
        # Toolbar
        toolbar = tk.Frame(parent, bg='white', height=50)
        toolbar.pack(fill='x', padx=10, pady=10)

        tk.Button(toolbar, text=f"{Icons.LOADING} Yenile", font=('Segoe UI', 10, 'bold'),
                 bg='#3498db', fg='white', padx=15, pady=8,
                 command=lambda: self._load_licenses(tree)).pack(side='left', padx=5)

        tk.Button(toolbar, text=f"{Icons.FAIL} Pasifleştir", font=('Segoe UI', 10, 'bold'),
                 bg='#e74c3c', fg='white', padx=15, pady=8,
                 command=lambda: self._deactivate_selected_license(tree)).pack(side='left', padx=5)

        tk.Button(toolbar, text=f"{Icons.LOADING} Yenile (30 gün)", font=('Segoe UI', 10, 'bold'),
                 bg='#f39c12', fg='white', padx=15, pady=8,
                 command=lambda: self._renew_selected_license(tree, 30)).pack(side='left', padx=5)

        # Tree
        tree_frame = tk.Frame(parent, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('ID', 'Şirket', 'Tip', 'Bitiş', 'Max User', 'Modüller', 'Durum')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Load data
        self._load_licenses(tree)

    def _load_licenses(self, tree):
        """Lisansları yükle"""
        try:
            # Clear
            for item in tree.get_children():
                tree.delete(item)

            lg = LicenseGenerator(self.db_path)
            licenses = lg.get_all_licenses()

            for lic in licenses:
                modules_str = ', '.join(lic['modules'][:3])
                if len(lic['modules']) > 3:
                    modules_str += f" +{len(lic['modules'])-3}"

                tree.insert('', 'end', values=(
                    lic['id'],
                    lic['company'],
                    lic['type'],
                    lic['expiry'][:10] if lic['expiry'] != 'Unlimited' else 'Unlimited',
                    lic['max_users'],
                    modules_str,
                    lic['status']
                ))

            messagebox.showinfo("Başarılı", f"{len(licenses)} lisans yüklendi")

        except Exception as e:
            messagebox.showerror("Hata", f"Lisans yükleme hatası: {str(e)}")

    def _deactivate_selected_license(self, tree):
        """Seçili lisansı pasifleştir"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir lisans seçin!")
            return

        item = tree.item(selection[0])
        license_id = item['values'][0]
        company = item['values'][1]

        confirm = messagebox.askyesno("Onay",
                                     f"{company} şirketinin lisansını pasifleştirmek istediğinizden emin misiniz?")
        if confirm:
            try:
                lg = LicenseGenerator(self.db_path)
                lg.deactivate_license(license_id, "Admin tarafından pasifleştirildi")
                messagebox.showinfo("Başarılı", "Lisans pasifleştirildi!")
                self._load_licenses(tree)
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def _renew_selected_license(self, tree, days):
        """Seçili lisansı yenile"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir lisans seçin!")
            return

        item = tree.item(selection[0])
        license_id = item['values'][0]
        company = item['values'][1]

        confirm = messagebox.askyesno("Onay",
                                     f"{company} şirketinin lisansını {days} gün uzatmak istiyor musunuz?")
        if confirm:
            try:
                lg = LicenseGenerator(self.db_path)
                lg.renew_license(license_id, days)
                messagebox.showinfo("Başarılı", f"Lisans {days} gün uzatıldı!")
                self._load_licenses(tree)
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def _create_license_stats_tab(self, parent):
        """Lisans istatistikleri"""
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill='both', expand=True, padx=20, pady=20)

        try:
            lg = LicenseGenerator(self.db_path)
            stats = lg.get_license_statistics()

            # İstatistik kartları
            cards_frame = tk.Frame(stats_frame, bg='white')
            cards_frame.pack(fill='x', pady=20)

            cards = [
                ('Toplam Lisans', stats['total'], '#3498db'),
                ('Aktif', stats['active'], '#27ae60'),
                ('Süresi Dolan', stats['expired'], '#e74c3c'),
                ('Yakında Dolacak', stats['expiring_soon'], '#f39c12')
            ]

            for i, (title, value, color) in enumerate(cards):
                card = tk.Frame(cards_frame, bg=color, relief='raised', bd=2)
                card.grid(row=0, column=i, padx=10, sticky='ew')
                cards_frame.grid_columnconfigure(i, weight=1)

                tk.Label(card, text=title, font=('Segoe UI', 10, 'bold'),
                        bg=color, fg='white').pack(pady=5)
                tk.Label(card, text=str(value), font=('Segoe UI', 20, 'bold'),
                        bg=color, fg='white').pack(pady=10)

            # Tipe göre dağılım
            if stats['by_type']:
                type_frame = tk.LabelFrame(stats_frame, text="Tipe Göre Dağılım",
                                          font=('Segoe UI', 12, 'bold'), bg='white')
                type_frame.pack(fill='x', pady=20)

                for type_name, count in stats['by_type'].items():
                    row = tk.Frame(type_frame, bg='white')
                    row.pack(fill='x', pady=5, padx=10)

                    tk.Label(row, text=f"{type_name.upper()}:", font=('Segoe UI', 10, 'bold'),
                            bg='white').pack(side='left', padx=10)
                    tk.Label(row, text=str(count), font=('Segoe UI', 12, 'bold'),
                            bg='white', fg='#2ecc71').pack(side='left')

        except Exception as e:
            tk.Label(stats_frame, text=f"İstatistik yükleme hatası: {str(e)}",
                    font=('Segoe UI', 10), bg='white', fg='red').pack(pady=20)



