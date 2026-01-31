#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
Departman Yönetimi GUI
Departman ekleme, düzenleme, silme ve listeleme işlemleri
"""

import tkinter as tk
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager
from utils.tooltip import bind_treeview_header_tooltips
from yonetim.kullanici_yonetimi.models.user_manager import UserManager


class DepartmentManagementGUI:
    """Departman Yönetimi GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()
        self.user_manager = UserManager()

        self.setup_ui()
        self.load_departments()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_frame = tk.Frame(main_frame, bg='#8e44ad', height=60)
        title_frame.pack(fill='x', pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr("title_department_management", " Departman Yönetimi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#8e44ad')
        title_label.pack(expand=True)

        # Buton paneli
        button_frame = tk.Frame(main_frame, bg='#f8f9fa', relief='solid', bd=1)
        button_frame.pack(fill='x', pady=(0, 10))

        tk.Label(button_frame, text=self.lm.tr("lbl_department_operations", "Departman İşlemleri"),
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='#f8f9fa').pack(pady=10)

        btn_frame = tk.Frame(button_frame, bg='#f8f9fa')
        btn_frame.pack(pady=(0, 10))
        new_btn = ttk.Button(btn_frame, text=self.lm.tr("title_new_department", " Yeni Departman"), style='Menu.TButton',
                             command=self.create_department)
        new_btn.pack(side='left', padx=6)
        edit_btn = ttk.Button(btn_frame, text=self.lm.tr("btn_edit", " Düzenle"), style='Menu.TButton',
                              command=self.edit_department)
        edit_btn.pack(side='left', padx=6)
        del_btn = ttk.Button(btn_frame, text=self.lm.tr("btn_delete", " Sil"), style='Menu.TButton',
                             command=self.delete_department)
        del_btn.pack(side='left', padx=6)
        ref_btn = ttk.Button(btn_frame, text=self.lm.tr("btn_refresh", " Yenile"), style='Menu.TButton',
                             command=self.refresh_departments)
        ref_btn.pack(side='left', padx=6)
        try:
            from utils.tooltip import add_tooltip
            add_tooltip(new_btn, self.lm.tr("tooltip_new_department", 'Yeni departman ekle'))
            add_tooltip(edit_btn, self.lm.tr("tooltip_edit_department", 'Seçili departmanı düzenle'))
            add_tooltip(del_btn, self.lm.tr("tooltip_delete_department", 'Seçili departmanı sil'))
            add_tooltip(ref_btn, self.lm.tr("tooltip_refresh_departments", 'Departman listesini yenile'))
        except Exception as e:
            logging.error(f'Silent error in department_management_gui.py: {str(e)}')

        # Departman listesi
        list_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        list_frame.pack(fill='both', expand=True)

        tk.Label(list_frame, text=self.lm.tr("lbl_department_list", "Departman Listesi"),
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=10)

        # Treeview
        columns = ('ID', 'Ad', 'Kod', 'Açıklama', 'Durum', 'Kullanıcı Sayısı')
        self.dept_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        self.dept_tree.heading('ID', text=self.lm.tr("col_department_id", 'ID'))
        self.dept_tree.heading('Ad', text=self.lm.tr("col_department_name", 'Departman Adı'))
        self.dept_tree.heading('Kod', text=self.lm.tr("col_code", 'Kod'))
        self.dept_tree.heading('Açıklama', text=self.lm.tr("col_description", 'Açıklama'))
        self.dept_tree.heading('Durum', text=self.lm.tr("col_status", 'Durum'))
        self.dept_tree.heading('Kullanıcı Sayısı', text=self.lm.tr("col_dept_user_count", 'Kullanıcı Sayısı'))

        # Sütun genişlikleri
        self.dept_tree.column('ID', width=50)
        self.dept_tree.column('Ad', width=200)
        self.dept_tree.column('Kod', width=80)
        self.dept_tree.column('Açıklama', width=300)
        self.dept_tree.column('Durum', width=80)
        self.dept_tree.column('Kullanıcı Sayısı', width=120)

        # Scrollbar
        dept_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.dept_tree.yview)
        self.dept_tree.configure(yscrollcommand=dept_scrollbar.set)

        self.dept_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        dept_scrollbar.pack(side='right', fill='y', pady=(0, 10))

        try:
            bind_treeview_header_tooltips(self.dept_tree)
        except Exception as e:
            logging.error(f'Silent error in department_management_gui.py: {str(e)}')

        # Departman seçim olayı
        self.dept_tree.bind('<<TreeviewSelect>>', self.on_department_select)

        # İstatistikler
        self.load_statistics()

    def load_departments(self) -> None:
        """Departmanları yükle"""
        for item in self.dept_tree.get_children():
            self.dept_tree.delete(item)

        try:
            departments = self.user_manager.get_departments()

            for dept in departments:
                status = self.lm.tr("status_active", "Aktif") if dept['is_active'] else self.lm.tr("status_passive", "Pasif")
                user_count = dept.get('user_count', 0)

                self.dept_tree.insert('', 'end', values=(
                    dept['id'],
                    dept['name'],
                    dept['code'],
                    dept.get('description', '')[:50] + '...' if dept.get('description', '') and len(dept.get('description', '')) > 50 else dept.get('description', ''),
                    status,
                    user_count
                ), tags=(str(dept['id']),))

        except Exception as e:
            logging.error(self.lm.tr("log_department_fetch_error", "Departmanlar yüklenirken hata: {}").format(e))

    def on_department_select(self, event) -> None:
        """Departman seçildiğinde"""
        selection = self.dept_tree.selection()
        if selection:
            # Seçilen departman bilgilerini gösterebiliriz
            pass

    def create_department(self) -> None:
        """Yeni departman oluştur"""
        self.show_department_form()

    def edit_department(self) -> None:
        """Departman düzenle"""
        selection = self.dept_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr("msg_warning", "Uyarı"), self.lm.tr("msg_select_dept_edit", "Lütfen düzenlemek istediğiniz departmanı seçin."))
            return

        item = selection[0]
        tags = self.dept_tree.item(item, 'tags')
        if not tags:
            messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_dept_id_not_found", "Departman ID bulunamadı."))
            return

        dept_id = int(tags[0])
        self.show_department_form(dept_id)

    def delete_department(self) -> None:
        """Departman sil"""
        selection = self.dept_tree.selection()
        if not selection:
            messagebox.showwarning(self.lm.tr("msg_warning", "Uyarı"), self.lm.tr("msg_select_dept_delete", "Lütfen silmek istediğiniz departmanı seçin."))
            return

        item = selection[0]
        dept_data = self.dept_tree.item(item, 'values')
        dept_name = dept_data[1]  # Departman adı

        tags = self.dept_tree.item(item, 'tags')
        if not tags:
            messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_dept_id_not_found", "Departman ID bulunamadı."))
            return

        dept_id = int(tags[0])

        if messagebox.askyesno(self.lm.tr("title_delete_department", "Departman Sil"),
                              self.lm.tr("msg_confirm_delete_dept", f"'{dept_name}' departmanını silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!").replace("{dept_name}", dept_name)):
            try:
                success = self.user_manager.delete_department(dept_id, self.current_user_id)
                if success:
                    messagebox.showinfo(self.lm.tr("msg_success", "Başarılı"), self.lm.tr("msg_dept_deleted_success", "Departman başarıyla silindi."))
                    self.refresh_departments()
                else:
                    messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_dept_delete_failed", "Departman silinemedi."))
            except Exception as e:
                messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_dept_delete_error", f"Departman silinirken hata oluştu: {e}").replace("{e}", str(e)))

    def refresh_departments(self) -> None:
        """Departmanları yenile"""
        self.load_departments()
        self.load_statistics()

    def show_department_form(self, dept_id=None) -> None:
        """Departman formu göster"""
        form_window = tk.Toplevel(self.parent)
        form_window.title(self.lm.tr("title_new_department", "Yeni Departman") if not dept_id else self.lm.tr("title_edit_department", "Departman Düzenle"))
        form_window.geometry("500x500")
        form_window.resizable(True, True)
        form_window.configure(bg='white')

        # Center the window
        form_window.update_idletasks()
        width = form_window.winfo_width()
        height = form_window.winfo_height()
        x = (form_window.winfo_screenwidth() // 2) - (width // 2)
        y = (form_window.winfo_screenheight() // 2) - (height // 2)
        form_window.geometry(f'{width}x{height}+{x}+{y}')

        # Ana container - scrollable
        main_container = tk.Frame(form_window, bg='white')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Canvas ve scrollbar
        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel desteği
        def _on_mousewheel(event) -> None:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

        main_frame = scrollable_frame

        tk.Label(main_frame, text=self.lm.tr("title_department_info", "Departman Bilgileri"),
                font=('Segoe UI', 14, 'bold'), bg='white', fg='#333').pack(pady=(0, 20))

        # Form alanları
        fields = {}

        # Departman Adı
        tk.Label(main_frame, text=self.lm.tr("lbl_department_name", "Departman Adı:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        fields['name'] = ttk.Entry(main_frame, font=('Segoe UI', 10), width=50)
        fields['name'].pack(fill='x', pady=(0, 10))

        # Departman Kodu
        tk.Label(main_frame, text=self.lm.tr("lbl_department_code", "Departman Kodu:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        fields['code'] = ttk.Entry(main_frame, font=('Segoe UI', 10), width=50)
        fields['code'].pack(fill='x', pady=(0, 10))

        # Açıklama
        tk.Label(main_frame, text=self.lm.tr("lbl_description", "Açıklama:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        desc_text = tk.Text(main_frame, font=('Segoe UI', 10), width=50, height=4)
        desc_text.pack(fill='x', pady=(0, 10))

        # Aktif/Pasif
        tk.Label(main_frame, text=self.lm.tr("lbl_status", "Durum:"), font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 0))
        is_active_var = tk.BooleanVar(value=True)
        tk.Checkbutton(main_frame, text=self.lm.tr("lbl_active", "Aktif"), variable=is_active_var,
                      font=('Segoe UI', 10), bg='white').pack(anchor='w', pady=(0, 15))

        def save_department() -> None:
            """Departman kaydet"""
            name = fields['name'].get().strip()
            code = fields['code'].get().strip()
            description = desc_text.get('1.0', 'end').strip()
            is_active = is_active_var.get()

            if not name:
                messagebox.showwarning(self.lm.tr("msg_warning", "Uyarı"), self.lm.tr("msg_dept_name_required", "Departman adı zorunludur."))
                return

            if not code:
                messagebox.showwarning(self.lm.tr("msg_warning", "Uyarı"), self.lm.tr("msg_dept_code_required", "Departman kodu zorunludur."))
                return

            dept_data = {
                'name': name,
                'code': code.upper(),
                'description': description,
                'is_active': is_active
            }

            try:
                if dept_id:
                    # Düzenleme
                    success = self.user_manager.update_department(dept_id, dept_data, self.current_user_id)
                    success_msg = self.lm.tr("msg_dept_updated_success", "Departman başarıyla güncellendi.")
                    error_msg = self.lm.tr("msg_dept_update_failed", "Departman güncellenemedi.")
                else:
                    # Yeni departman
                    success = self.user_manager.create_department(dept_data, self.current_user_id)
                    success_msg = self.lm.tr("msg_dept_created_success", "Departman başarıyla oluşturuldu.")
                    error_msg = self.lm.tr("msg_dept_create_failed", "Departman oluşturulamadı.")

                if success:
                    messagebox.showinfo(self.lm.tr("msg_success", "Başarılı"), success_msg)
                    self.refresh_departments()
                    form_window.destroy()
                else:
                    messagebox.showerror(self.lm.tr("msg_error", "Hata"), error_msg)
            except Exception as e:
                messagebox.showerror(self.lm.tr("msg_error", "Hata"), self.lm.tr("msg_dept_save_error", f"Departman kaydedilirken hata oluştu: {e}").replace("{e}", str(e)))

        # Butonlar
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))

        center_frame = tk.Frame(button_frame, bg='white')
        center_frame.pack(expand=True)

        tk.Button(center_frame, text=self.lm.tr("btn_save", " Kaydet"), font=('Segoe UI', 12, 'bold'), bg='#27ae60',
                 fg='white', relief='raised', bd=2, padx=30, pady=10, cursor='hand2',
                 command=save_department).pack(side='left', padx=(0, 15))

        tk.Button(center_frame, text=self.lm.tr("btn_cancel", " İptal"), font=('Segoe UI', 12, 'bold'), bg='#95a5a6',
                 fg='white', relief='raised', bd=2, padx=30, pady=10, cursor='hand2',
                 command=form_window.destroy).pack(side='left', padx=(15, 0))

        # Eğer düzenleme modundaysa, mevcut verileri yükle
        if dept_id:
            try:
                dept = self.user_manager.get_department_by_id(dept_id)
                if dept:
                    fields['name'].insert(0, dept.get('name', ''))
                    fields['code'].insert(0, dept.get('code', ''))
                    desc_text.insert('1.0', dept.get('description', ''))
                    is_active_var.set(dept.get('is_active', True))
            except Exception as e:
                logging.error(f"Departman verileri yüklenirken hata: {e}")

    def load_statistics(self) -> None:
        """İstatistikleri yükle"""
        try:
            departments = self.user_manager.get_departments()
            total_departments = len(departments)
            active_departments = len([d for d in departments if d['is_active']])
            inactive_departments = total_departments - active_departments

            # İstatistikleri göstermek için label ekleyebiliriz
            # Şimdilik loga yazdırıyoruz
            logging.info(self.lm.tr("log_stats_summary", "Toplam Departman: {}, Aktif: {}, Pasif: {}").format(
                total_departments, active_departments, inactive_departments))

        except Exception as e:
            logging.error(self.lm.tr("log_stats_fetch_error", "İstatistikler yüklenirken hata: {}").format(e))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Departman Yönetimi Test")
    app = DepartmentManagementGUI(root)
    root.mainloop()
