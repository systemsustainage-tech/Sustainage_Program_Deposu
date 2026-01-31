import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Soru Bankası GUI
Soru bankası yönetimi arayüzü
"""

import tkinter as tk
from tkinter import messagebox, ttk

from utils.language_manager import LanguageManager

from .sdg_question_bank import SDGQuestionBank


class SDGQuestionBankGUI:
    """SDG Soru Bankası GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.lm = LanguageManager()
        self.parent = parent
        self.company_id = company_id
        self.question_bank = SDGQuestionBank()
        # Görünüm modu: 'all' veya 'selected'
        self.view_mode = tk.StringVar(value='all')
        # Tree row -> question_id eşlemesi
        self.tree_row_to_question_id: dict[str, int] = {}

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_questions()

    def setup_ui(self) -> None:
        """Soru bankası arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#2c3e50', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        # Geri butonu
        back_btn = tk.Button(header_frame, text=f" {self.lm.tr('btn_back', 'Geri')}",
                             font=('Segoe UI', 10, 'bold'), bg='#1f2a36', fg='white',
                             relief='flat', bd=0, padx=15, pady=8,
                             command=self.back_to_sdg)
        back_btn.pack(side='left', padx=15, pady=15)

        title_frame = tk.Frame(header_frame, bg='#2c3e50')
        # Başlık çerçevesini genişlet
        title_frame.pack(side='left', fill='x', expand=True, padx=20, pady=15)

        title_label = tk.Label(title_frame, text=self.lm.tr('title_sdg_question_bank', "SDG Soru Bankası"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(side='left')

        subtitle_label = tk.Label(title_frame, text=self.lm.tr('subtitle_sdg_question_bank', "SDG göstergeleri için soru yönetimi"),
                                 font=('Segoe UI', 11), fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(side='left', padx=(10, 0))

        # Ana içerik
        content_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=1)
        # İç yatay/vertical padding'i sıfırla ki sağ panel tam sağa yaslansın
        content_frame.pack(fill='both', expand=True, padx=0, pady=10, ipadx=0, ipady=0)

        # Sol panel - SDG seçimi
        left_panel = tk.Frame(content_frame, bg='white', width=280)
        # Sol paneli genişlet ve iç boşlukları kaldır
        left_panel.pack(side='left', fill='y', padx=(0, 0), pady=(0, 0))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text=self.lm.tr('lbl_sdg_goals', "SDG Hedefleri"), font=('Segoe UI', 12, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor='w', padx=15, pady=(15, 10))

        # SDG listesi
        self.sdg_listbox = tk.Listbox(left_panel, width=32, height=18,
                                     font=('Segoe UI', 10), selectmode='single', exportselection=False)
        self.sdg_listbox.pack(fill='y', pady=(0, 10))
        self.sdg_listbox.bind('<<ListboxSelect>>', self.on_sdg_select)

        # Scrollbar
        sdg_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.sdg_listbox.yview)
        self.sdg_listbox.configure(yscrollcommand=sdg_scrollbar.set)
        sdg_scrollbar.pack(side='right', fill='y')

        # Sağ panel - Sorular
        right_panel = tk.Frame(content_frame, bg='white')
        # Sağ paneli yana yasla; iç paddingleri kaldır ki scrollbar en sağda olsun
        right_panel.pack(side='right', fill='both', expand=True, padx=(0, 0), pady=(0, 0), ipadx=0, ipady=0)

        tk.Label(right_panel, text=self.lm.tr('lbl_questions', "Sorular"), font=('Segoe UI', 12, 'bold'),
                bg='white', fg='#2c3e50').pack(anchor='w', pady=(0, 10))

        # Görünüm modu seçenekleri
        view_mode_frame = tk.Frame(right_panel, bg='white')
        view_mode_frame.pack(fill='x', pady=(0, 8))
        ttk.Radiobutton(view_mode_frame, text=self.lm.tr('radio_all_questions', "Tüm sorular"), variable=self.view_mode, value='all',
                        command=self.on_view_mode_change).pack(side='left', padx=(0, 10))
        ttk.Radiobutton(view_mode_frame, text=self.lm.tr('radio_selected_goal', "Seçilen hedef"), variable=self.view_mode, value='selected',
                        command=self.on_view_mode_change).pack(side='left')

        # Üst araç çubuğu - butonlar (görünürlüğü artırmak için üstte)
        toolbar_frame = tk.Frame(right_panel, bg='white')
        toolbar_frame.pack(fill='x', pady=(0, 10))

        tk.Button(toolbar_frame, text=f" {self.lm.tr('btn_new_question', 'Yeni Soru')}", command=self.add_question,
                 font=('Segoe UI', 10), bg='#27ae60', fg='white', relief='flat', padx=15).pack(side='left', padx=(0, 5))
        tk.Button(toolbar_frame, text=f" {self.lm.tr('btn_edit', 'Düzenle')}", command=self.edit_question,
                 font=('Segoe UI', 10), bg='#3498db', fg='white', relief='flat', padx=15).pack(side='left', padx=5)
        tk.Button(toolbar_frame, text=f" {self.lm.tr('btn_delete', 'Sil')}", command=self.delete_question,
                 font=('Segoe UI', 10), bg='#e74c3c', fg='white', relief='flat', padx=15).pack(side='left', padx=5)
        tk.Button(toolbar_frame, text=f" {self.lm.tr('btn_statistics', 'İstatistikler')}", command=self.show_statistics,
                 font=('Segoe UI', 10), bg='#f39c12', fg='white', relief='flat', padx=15).pack(side='left', padx=5)

        # Soru listesi
        self.question_tree = ttk.Treeview(right_panel, columns=('sdg', 'type', 'question', 'answer'),
                                         show='headings', height=15)

        self.question_tree.heading('sdg', text='SDG')
        self.question_tree.heading('type', text=self.lm.tr('col_type', 'Tür'))
        self.question_tree.heading('question', text=self.lm.tr('col_question', 'Soru'))
        self.question_tree.heading('answer', text=self.lm.tr('col_answer', 'Cevap'))

        # Sütun genişliklerini ve esnemeyi ayarla
        self.question_tree.column('sdg', width=50, stretch=False, anchor='center')
        self.question_tree.column('type', width=120, stretch=False)
        self.question_tree.column('question', width=600, stretch=True)
        self.question_tree.column('answer', width=120, stretch=False)

        self.question_tree.pack(fill='both', expand=True, pady=(0, 0))
        # Dinamik genişlik: toplam genişliğe göre "Soru" sütununu ayarla
        self.question_tree.bind('<Configure>', self._resize_question_column)

        # Scrollbar
        question_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.question_tree.yview)
        self.question_tree.configure(yscrollcommand=question_scrollbar.set)
        # Scrollbar'ı sağ panelin en sağ kenarına sabitle
        question_scrollbar.pack(side='right', fill='y')

        # Alt panel - sadece istatistik etiketi
        bottom_panel = tk.Frame(content_frame, bg='white')
        bottom_panel.pack(side='bottom', fill='x', pady=(10, 0))

        stats_frame = tk.Frame(bottom_panel, bg='white')
        stats_frame.pack(side='left')

        self.stats_label = tk.Label(stats_frame, text=self.lm.tr('lbl_total_questions', "Toplam: 0 soru").format(count=0),
                                   font=('Segoe UI', 10), bg='white', fg='#7f8c8d')
        self.stats_label.pack(side='left', padx=(0, 20))

    def back_to_sdg(self) -> None:
        """SDG ana ekranına geri dön"""
        try:
            # İçeriği temizle ve SDG ana ekranını yükle
            for widget in self.parent.winfo_children():
                widget.destroy()
            from .sdg_gui import SDGGUI
            SDGGUI(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_back', "Geri dönme işleminde hata: {e}").format(e=str(e)))

    def load_questions(self) -> None:
        """Soruları yükle"""
        try:
            # SDG listesini yükle
            self.load_sdg_list()
            # Başlangıç görünümü güncelle
            self.on_view_mode_change()

        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_load_questions', "Sorular yüklenirken hata oluştu: {e}").format(e=str(e)))

    def load_sdg_list(self) -> None:
        """SDG listesini yükle"""
        try:
            # Mevcut verileri temizle
            self.sdg_listbox.delete(0, tk.END)

            # SDG'leri yükle
            sdg_goals = self.question_bank.get_sdg_goals()
            
            prefix = self.lm.tr('lbl_sdg_prefix', 'SDG')

            for goal in sdg_goals:
                self.sdg_listbox.insert(tk.END, f"{prefix} {goal[0]}: {goal[1]}")

        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_load_sdg_list', "SDG listesi yüklenirken hata: {e}").format(e=str(e)))

    def on_sdg_select(self, event) -> None:
        """SDG seçildiğinde"""
        try:
            selection = self.sdg_listbox.curselection()
            if not selection:
                return

            # Otomatik olarak 'Seçilen hedef' moduna geç
            if self.view_mode.get() != 'selected':
                self.view_mode.set('selected')

            # Seçilen SDG'yi al
            selected_text = self.sdg_listbox.get(selection[0])
            # Parse localized SDG format: "Prefix Number: Title"
            try:
                # Split by colon to separate title
                parts = selected_text.split(':')
                if len(parts) > 0:
                    prefix_part = parts[0] # "SDG 1"
                    # Get the number part
                    sdg_no = int(prefix_part.split(' ')[-1])
                else:
                    # Fallback
                    sdg_no = int(selected_text.split(':')[0].split(' ')[1])
            except Exception:
                sdg_no = 0

            # Bu SDG'ye ait soruları yükle
            self.load_questions_for_sdg(sdg_no)

        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_sdg_selection', "SDG seçimi işlenirken hata: {e}").format(e=str(e)))

    def on_view_mode_change(self) -> None:
        """Görünüm modu değiştiğinde tabloyu güncelle"""
        try:
            mode = self.view_mode.get()
            if mode == 'all':
                self.load_all_questions()
            else:
                selection = self.sdg_listbox.curselection()
                if selection:
                    selected_text = self.sdg_listbox.get(selection[0])
                    sdg_no = int(selected_text.split(':')[0].split(' ')[1])
                    self.load_questions_for_sdg(sdg_no)
                else:
                    # Seçim yoksa tabloyu temizle
                    for item in self.question_tree.get_children():
                        self.question_tree.delete(item)
                    self.tree_row_to_question_id.clear()
                    self.stats_label.config(text=self.lm.tr('lbl_total_questions', "Toplam: 0 soru").format(count=0))
        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_view_mode_update', "Görünüm modu güncellenirken hata: {e}").format(e=str(e)))

    def load_questions_for_sdg(self, sdg_no: int) -> None:
        """Belirli SDG'ye ait soruları yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.question_tree.get_children():
                self.question_tree.delete(item)
            self.tree_row_to_question_id.clear()

            # Soruları yükle
            questions = self.question_bank.get_questions_for_sdg(sdg_no)

            for q in questions:
                # Tür olarak type_name'i göster (ör. Metin, Sayı, Evet/Hayır vs.)
                type_label = q.get('type_name', self.lm.tr('lbl_unknown', 'Belirsiz'))
                qtext = q.get('question_text', '')
                item_id = self.question_tree.insert('', 'end', values=(
                    sdg_no,
                    type_label,
                    (qtext[:80] + "...") if len(qtext) > 80 else qtext,
                    self.lm.tr('lbl_no_answer', "Cevap yok")
                ))
                self.tree_row_to_question_id[item_id] = int(q.get('id') or 0)

            # İstatistikleri güncelle
            self.stats_label.config(text=self.lm.tr('lbl_total_questions', "Toplam: {count} soru").format(count=len(questions)))

        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_load_questions', "SDG soruları yüklenirken hata: {e}").format(e=str(e)))

    def load_all_questions(self) -> None:
        """Tüm SDG'lere ait soruları yükle"""
        try:
            # Mevcut verileri temizle
            for item in self.question_tree.get_children():
                self.question_tree.delete(item)
            self.tree_row_to_question_id.clear()

            # Soruları yükle
            questions = self.question_bank.get_all_questions()

            for q in questions:
                type_label = q.get('type_name', self.lm.tr('lbl_unknown', 'Belirsiz'))
                qtext = q.get('question_text', '')
                item_id = self.question_tree.insert('', 'end', values=(
                    q.get('sdg_no', ''),
                    type_label,
                    (qtext[:80] + "...") if len(qtext) > 80 else qtext,
                    self.lm.tr('lbl_no_answer', "Cevap yok")
                ))
                self.tree_row_to_question_id[item_id] = int(q.get('id') or 0)

            # İstatistikleri güncelle
            self.stats_label.config(text=self.lm.tr('lbl_total_questions', "Toplam: {count} soru").format(count=len(questions)))
        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_load_all_questions', "Tüm sorular yüklenirken hata: {e}").format(e=str(e)))

    def add_question(self) -> None:
        """Yeni soru ekle"""
        try:
            # Seçili SDG'yi al
            selection = self.sdg_listbox.curselection()
            if not selection:
                messagebox.showwarning(self.lm.tr('title_warning', "Uyarı"), self.lm.tr('msg_warning_select_sdg', "Lütfen soldan bir SDG seçin"))
                return
            selected_text = self.sdg_listbox.get(selection[0])
            try:
                # Parse logic same as on_sdg_select
                parts = selected_text.split(':')
                if len(parts) > 0:
                    prefix_part = parts[0]
                    sdg_no = int(prefix_part.split(' ')[-1])
                else:
                    sdg_no = int(selected_text.split(':')[0].split(' ')[1])
            except Exception:
                messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_sdg_no_parse', "SDG numarası çözümlenemedi"))
                return

            from tkinter import simpledialog
            indicator_code = simpledialog.askstring(self.lm.tr('title_indicator_code', "Gösterge Kodu"), self.lm.tr('msg_enter_indicator_code', "Gösterge Kodu (ör. 1.1.1)"))
            if not indicator_code:
                return
            question_text = simpledialog.askstring(self.lm.tr('title_question_text', "Soru Metni"), self.lm.tr('msg_enter_question_text', "Soru metnini girin"))
            if not question_text:
                return
            question_type = simpledialog.askstring(self.lm.tr('title_question_type', "Soru Tipi"), self.lm.tr('msg_enter_question_type', "Tip: text | numeric | boolean"), initialvalue='text') or 'text'

            qid = self.question_bank.add_question(sdg_no=sdg_no, indicator_code=indicator_code,
                                                  question_text=question_text, question_type=question_type)
            if qid:
                messagebox.showinfo(self.lm.tr('title_success', "Başarılı"), self.lm.tr('msg_success_question_added', "Soru eklendi"))
                if self.view_mode.get() == 'selected':
                    self.load_questions_for_sdg(sdg_no)
                else:
                    self.load_all_questions()
            else:
                messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_question_add', "Soru eklenemedi"))
        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), f"{self.lm.tr('msg_error_question_add_exception', 'Soru eklenirken hata')}: {str(e)}")

    def edit_question(self) -> None:
        """Soru düzenle"""
        try:
            selection = self.question_tree.selection()
            if not selection:
                messagebox.showwarning(self.lm.tr('title_warning', "Uyarı"), self.lm.tr('msg_warning_select_question', "Lütfen listeden bir soru seçin"))
                return
            item_id = selection[0]
            question_id = self.tree_row_to_question_id.get(item_id)
            if not question_id:
                messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_question_id', "Seçili soru ID’si bulunamadı"))
                return

            # Mevcut soru detaylarını al
            q = self.question_bank.get_question_by_id(question_id)
            if not q:
                messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_question_details', "Soru detayları alınamadı"))
                return

            from tkinter import simpledialog
            new_text = simpledialog.askstring(self.lm.tr('title_question_text', "Soru Metni"), self.lm.tr('msg_new_question_text', "Yeni soru metni:"), initialvalue=q.get('question_text', ''))
            if new_text is None:
                return

            # Tip güncellemesi (isteğe bağlı)
            type_current = q.get('type_name', self.lm.tr('type_text', 'Metin'))
            
            # Localized prompt with options
            prompt_msg = self.lm.tr('msg_enter_question_type_options', "Tip (Metin / Sayı / Evet/Hayır)")
            if self.lm.current_lang == 'en':
                prompt_msg = "Type (Text / Numeric / Boolean)"
                
            type_input = simpledialog.askstring(self.lm.tr('title_question_type', "Soru Tipi"), 
                                              prompt_msg, 
                                              initialvalue=type_current)
            
            # Expanded map to handle both Turkish and English inputs
            type_map = {
                'Metin': 'text',
                'Sayı': 'numeric',
                'Evet/Hayır': 'boolean',
                'metin': 'text',
                'sayı': 'numeric',
                'evet/hayır': 'boolean',
                # English
                'Text': 'text',
                'Numeric': 'numeric',
                'Boolean': 'boolean',
                'text': 'text',
                'numeric': 'numeric',
                'boolean': 'boolean',
                # Localized keys if different
                self.lm.tr('type_text', 'Metin'): 'text',
                self.lm.tr('type_numeric', 'Sayı'): 'numeric',
                self.lm.tr('type_boolean', 'Evet/Hayır'): 'boolean'
            }
            qtype_code = type_map.get(type_input, None) if type_input else None

            # Güncelle
            ok = False
            if qtype_code:
                ok = self.question_bank.update_question(question_id, question_text=new_text, question_type=qtype_code)
            else:
                ok = self.question_bank.update_question(question_id, question_text=new_text)

            if ok:
                # Görünüm moduna göre listeyi yenile
                if self.view_mode.get() == 'selected':
                    selection_sdg = self.sdg_listbox.curselection()
                    if selection_sdg:
                        try:
                            selected_text = self.sdg_listbox.get(selection_sdg[0])
                            parts = selected_text.split(':')
                            if len(parts) > 0:
                                prefix_part = parts[0]
                                sdg_no = int(prefix_part.split(' ')[-1])
                            else:
                                sdg_no = int(selected_text.split(':')[0].split(' ')[1])
                            self.load_questions_for_sdg(sdg_no)
                        except Exception as e:
                            logging.error(f"Silent error caught: {str(e)}")
                    else:
                        # Seçim yoksa tabloyu temizle
                        for item in self.question_tree.get_children():
                            self.question_tree.delete(item)
                        self.tree_row_to_question_id.clear()
                        self.stats_label.config(text=self.lm.tr('lbl_total_questions', "Toplam: 0 soru").format(count=0))
                else:
                    self.load_all_questions()
                messagebox.showinfo(self.lm.tr('title_success', "Başarılı"), self.lm.tr('msg_success_question_updated', "Soru güncellendi"))
            else:
                messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_question_update', "Soru güncellenemedi"))
        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), f"{self.lm.tr('msg_error_question_edit_exception', 'Soru düzenlenirken hata')}: {str(e)}")

    def _resize_question_column(self, event) -> None:
        """Tree genişliğine göre 'Soru' sütununu ayarla"""
        try:
            total = event.width
            type_w = 140
            answer_w = 120
            # Kenar boşlukları için küçük pay
            question_w = max(200, total - type_w - answer_w - 30)
            self.question_tree.column('type', width=type_w)
            self.question_tree.column('answer', width=answer_w)
            self.question_tree.column('question', width=question_w)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def delete_question(self) -> None:
        """Soru sil"""
        try:
            selection = self.question_tree.selection()
            if not selection:
                messagebox.showwarning(self.lm.tr('title_warning', "Uyarı"), self.lm.tr('msg_warning_select_question', "Lütfen listeden bir soru seçin"))
                return
            item_id = selection[0]
            question_id = self.tree_row_to_question_id.get(item_id)
            if not question_id:
                messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_question_id', "Seçili soru ID’si bulunamadı"))
                return
            if messagebox.askyesno(self.lm.tr('title_confirm', "Onay"), self.lm.tr('msg_confirm_delete_question', "Seçili soruyu silmek istiyor musunuz?")):
                ok = self.question_bank.delete_question(question_id)
                if ok:
                    # Görünüm moduna göre listeyi güncelle
                    if self.view_mode.get() == 'selected':
                        selection_sdg = self.sdg_listbox.curselection()
                        if selection_sdg:
                            sdg_no = int(self.sdg_listbox.get(selection_sdg[0]).split(':')[0].split(' ')[1])
                            self.load_questions_for_sdg(sdg_no)
                        else:
                            self.question_tree.delete(item_id)
                    else:
                        self.load_all_questions()
                    messagebox.showinfo(self.lm.tr('title_success', "Başarılı"), self.lm.tr('msg_success_question_deleted', "Soru silindi"))
                else:
                    messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_question_delete', "Soru silinemedi"))
        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), f"{self.lm.tr('msg_error_question_delete_exception', 'Soru silinirken hata')}: {str(e)}")

    def show_statistics(self) -> None:
        """İstatistikleri göster"""
        try:
            # İstatistikleri al
            stats = self.question_bank.get_statistics()

            # İstatistik penceresi
            stats_window = tk.Toplevel(self.parent)
            stats_window.title(self.lm.tr('title_stats_window', "Soru Bankası İstatistikleri"))
            stats_window.geometry("400x300")
            stats_window.configure(bg='white')

            # Başlık
            title_label = tk.Label(stats_window, text=self.lm.tr('title_stats_window', "Soru Bankası İstatistikleri"),
                                 font=('Segoe UI', 14, 'bold'), bg='white', fg='#2c3e50')
            title_label.pack(pady=20)

            # İstatistikler
            stats_text = f"""
{self.lm.tr('lbl_total_sdg_goals', 'Toplam SDG Hedefi')}: {stats.get('total_sdg_goals', 0)}
{self.lm.tr('lbl_total_questions', 'Toplam Soru')}: {stats.get('total_questions', 0)}
{self.lm.tr('lbl_text_questions', 'Metin Soruları')}: {stats.get('text_questions', 0)}
{self.lm.tr('lbl_numeric_questions', 'Sayısal Sorular')}: {stats.get('numeric_questions', 0)}
{self.lm.tr('lbl_boolean_questions', 'Evet/Hayır Soruları')}: {stats.get('boolean_questions', 0)}

{self.lm.tr('lbl_avg_questions_per_sdg', 'Ortalama Soru/HDG')}: {stats.get('avg_questions_per_sdg', 0):.1f}
            """

            stats_label = tk.Label(stats_window, text=stats_text,
                                 font=('Segoe UI', 11), bg='white', fg='#34495e', justify='left')
            stats_label.pack(pady=20)

            # Kapat butonu
            close_btn = tk.Button(stats_window, text=self.lm.tr('btn_close', "Kapat"), command=stats_window.destroy,
                                font=('Segoe UI', 10), bg='#95a5a6', fg='white', relief='flat', padx=20)
            close_btn.pack(pady=10)

        except Exception as e:
            messagebox.showerror(self.lm.tr('title_error', "Hata"), self.lm.tr('msg_error_stats_load', "İstatistik yükleme hatası: {e}").format(e=str(e)))

if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("SDG Soru Bankası")
    app = SDGQuestionBankGUI(root, 1)
    root.mainloop()
