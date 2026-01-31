#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
Dinamik Formlar GUI
Özelleştirilebilir form oluşturma ve yönetimi
"""

import tkinter as tk
from tkinter import ttk
from utils.language_manager import LanguageManager
from config.icons import Icons


class FormsGUI:
    """Dinamik Formlar GUI"""

    def __init__(self, parent, current_user_id: int = 1) -> None:
        self.parent = parent
        self.current_user_id = current_user_id
        self.lm = LanguageManager()

        self.setup_ui()

    def setup_ui(self) -> None:
        """Arayüzü oluştur"""
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Başlık
        title_label = tk.Label(main_frame, text=f"{Icons.MEMO} Dinamik Formlar",
                              font=('Segoe UI', 18, 'bold'), fg='#2c3e50', bg='#f5f5f5')
        title_label.pack(pady=(0, 20))

        # Notebook
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)

        # Form Oluşturucu
        creator_frame = tk.Frame(notebook, bg='white')
        notebook.add(creator_frame, text=f"{Icons.TOOLS} Form Oluştur")

        ttk.Button(creator_frame, text="Basit Form Oluştur", command=self.create_simple_form).pack(pady=15)

        # Form Listesi
        list_frame = tk.Frame(notebook, bg='white')
        notebook.add(list_frame, text=f"{Icons.CLIPBOARD} Form Listesi")

        tk.Label(list_frame, text="Mevcut formlar",
                font=('Segoe UI', 12, 'bold'), fg='#2c3e50', bg='white').pack(pady=(10,5))
        self.forms_list = tk.Listbox(list_frame, height=10)
        self.forms_list.pack(fill='x', padx=20)
        btns = tk.Frame(list_frame, bg='white')
        btns.pack(fill='x', padx=20, pady=10)
        ttk.Button(btns, text=self.lm.tr("btn_refresh", "Yenile"), command=self.load_forms).pack(side='left')
        ttk.Button(btns, text="Aç", command=self.open_selected_form).pack(side='left', padx=(10,0))
        ttk.Button(btns, text=self.lm.tr("btn_delete", "Sil"), command=self.delete_selected_form).pack(side='left', padx=(10,0))
        self.form_content = tk.Text(list_frame, wrap='word', font=('Segoe UI', 10))
        self.form_content.pack(fill='both', expand=True, padx=20, pady=10)
        self.load_forms()

        # Form Düzenleyici
        editor_frame = tk.Frame(notebook, bg='white')
        notebook.add(editor_frame, text=f"{Icons.EDIT} Form Düzenle")

        tk.Label(editor_frame, text="Form düzenleme aracı geliştiriliyor...",
                font=('Segoe UI', 12), fg='#7f8c8d', bg='white').pack(pady=50)

    def create_simple_form(self) -> None:
        try:
            win = tk.Toplevel(self.parent)
            win.title("Basit Form")
            win.geometry("400x250")
            tk.Label(win, text="Alan Etiketi", font=('Segoe UI', 11)).pack(pady=(15,5))
            label_var = tk.StringVar(value="Ad")
            tk.Entry(win, textvariable=label_var).pack(pady=(0,10))
            tk.Label(win, text="Alan Değeri", font=('Segoe UI', 11)).pack(pady=(10,5))
            value_var = tk.StringVar()
            tk.Entry(win, textvariable=value_var).pack(pady=(0,10))
            def save_json() -> None:
                from tkinter import filedialog, messagebox
                data = {label_var.get(): value_var.get()}
                import os
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'forms'))
                os.makedirs(base_dir, exist_ok=True)
                path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[(self.lm.tr("file_json", "JSON Dosyası"), "*.json"), (self.lm.tr("all_files", "Tüm Dosyalar"), "*.*")],
                    initialdir=base_dir,
                    title=self.lm.tr("save_form", "Formu Kaydet")
                )
                if not path:
                    return
                import json
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo(self.lm.tr("success", "Başarılı"), self.lm.tr("form_saved_success", "Form kaydedildi:\n{path}").format(path=path))
                win.destroy()
            ttk.Button(win, text=self.lm.tr("btn_save", "Kaydet"), command=save_json).pack(pady=10)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Hata", str(e))

    def load_forms(self) -> None:
        try:
            import os
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'forms'))
            if not os.path.exists(base_dir):
                self.forms_list.delete(0, tk.END)
                return
            files = [f for f in os.listdir(base_dir) if f.lower().endswith('.json')]
            self.forms_list.delete(0, tk.END)
            for name in files:
                self.forms_list.insert(tk.END, os.path.join(base_dir, name))
        except Exception:
            self.forms_list.delete(0, tk.END)

    def open_selected_form(self) -> None:
        try:
            sel = self.forms_list.curselection()
            if not sel:
                return
            path = self.forms_list.get(sel[0])
            import json
            with open(path, 'r', encoding='utf-8') as f:
                content = json.dumps(json.load(f), ensure_ascii=False, indent=2)
            self.form_content.delete('1.0', tk.END)
            self.form_content.insert('1.0', content)
        except Exception as e:
            logging.error(f'Silent error in forms_gui.py: {str(e)}')

    def delete_selected_form(self) -> None:
        try:
            sel = self.forms_list.curselection()
            if not sel:
                return
            path = self.forms_list.get(sel[0])
            import os
            os.remove(path)
            self.load_forms()
            self.form_content.delete('1.0', tk.END)
        except Exception as e:
            logging.error(f'Silent error in forms_gui.py: {str(e)}')