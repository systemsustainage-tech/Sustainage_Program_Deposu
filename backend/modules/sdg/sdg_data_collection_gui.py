import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Veri Toplama GUI
Her SDG göstergesi için 3 soru sistemi
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List

from utils.language_manager import LanguageManager

from .sdg_data_collection import SDGDataCollection


class SDGDataCollectionGUI:
    """SDG Veri Toplama GUI"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.data_collection = SDGDataCollection()
        self.question_widgets: List[Dict[str, Any]] = []
        self.lm = LanguageManager()

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()

    def setup_ui(self) -> None:
        """Veri toplama arayüzünü oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f8f9fa')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Başlık
        header_frame = tk.Frame(main_frame, bg='#27ae60', height=70)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)

        # Geri butonu
        back_btn = tk.Button(header_frame, text=f" {self.lm.tr('btn_back', 'Geri')}",
                             font=('Segoe UI', 10, 'bold'), bg='#1e8f4e', fg='white',
                             relief='flat', bd=0, padx=15, pady=8,
                             command=self.back_to_sdg)
        back_btn.pack(side='left', padx=15, pady=15)

        title_frame = tk.Frame(header_frame, bg='#27ae60')
        title_frame.pack(side='left', padx=20, pady=15)

        title_label = tk.Label(title_frame, text=self.lm.tr("sdg_data_collection_title", "SDG Veri Toplama Sistemi"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#27ae60')
        title_label.pack(side='left')

        subtitle_label = tk.Label(title_frame, text=self.lm.tr("sdg_data_collection_subtitle", "Her SDG göstergesi için 3 soru sistemi"),
                                 font=('Segoe UI', 11), fg='#e8f5e8', bg='#27ae60')
        subtitle_label.pack(side='left', padx=(10, 0))

        # İlerleme çubuğu
        progress_frame = tk.Frame(header_frame, bg='#27ae60')
        progress_frame.pack(side='right', padx=20, pady=15)

        self.progress_label = tk.Label(progress_frame, text=self.lm.tr("lbl_progress", "İlerleme: %{progress}").format(progress="0"),
                                      font=('Segoe UI', 10, 'bold'), fg='white', bg='#27ae60')
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        self.progress_bar.pack(pady=(5, 0))

        # Ana içerik - Sol panel (SDG listesi) ve Sağ panel (sorular)
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Sol panel - SDG listesi
        left_panel = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Sol panel başlığı
        left_title = tk.Label(left_panel, text=self.lm.tr("title_sdg_goals_indicators", "SDG Hedefleri ve Göstergeler"),
                             font=('Segoe UI', 12, 'bold'), bg='white', fg='#2c3e50')
        left_title.pack(pady=10)

        # SDG seçimi
        sdg_selection_frame = tk.Frame(left_panel, bg='white')
        sdg_selection_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(sdg_selection_frame, text=self.lm.tr("lbl_select_sdg", "SDG Hedefi Seçin:"),
                font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')

        self.sdg_var = tk.StringVar()
        self.sdg_combo = ttk.Combobox(sdg_selection_frame, textvariable=self.sdg_var,
                                     state='readonly', width=30)
        self.sdg_combo.pack(fill='x', pady=5)
        self.sdg_combo.bind('<<ComboboxSelected>>', self.on_sdg_selected)

        # Göstergeler listesi
        indicators_frame = tk.Frame(left_panel, bg='white')
        indicators_frame.pack(fill='both', expand=True, padx=10, pady=5)

        tk.Label(indicators_frame, text=self.lm.tr("lbl_indicators", "Göstergeler:"),
                font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w')

        # Göstergeler için Treeview
        columns = ('Kod', 'Tanım', 'Durum', 'İlerleme')
        self.indicators_tree = ttk.Treeview(indicators_frame, columns=columns, show='headings', height=15)

        # Sütun başlıkları
        self.indicators_tree.heading('Kod', text=self.lm.tr("col_indicator_code", "Gösterge Kodu"))
        self.indicators_tree.heading('Tanım', text=self.lm.tr("col_indicator_definition", "Gösterge Tanımı"))
        self.indicators_tree.heading('Durum', text=self.lm.tr("col_status", "Durum"))
        self.indicators_tree.heading('İlerleme', text=self.lm.tr("col_progress", "İlerleme %"))

        # Sütun genişlikleri
        self.indicators_tree.column('Kod', width=80)
        self.indicators_tree.column('Tanım', width=300)
        self.indicators_tree.column('Durum', width=80)
        self.indicators_tree.column('İlerleme', width=80)

        # Scrollbar
        indicators_scrollbar = ttk.Scrollbar(indicators_frame, orient="vertical", command=self.indicators_tree.yview)
        self.indicators_tree.configure(yscrollcommand=indicators_scrollbar.set)

        self.indicators_tree.pack(side='left', fill='both', expand=True)
        indicators_scrollbar.pack(side='right', fill='y')

        # Gösterge seçimi
        self.indicators_tree.bind('<<TreeviewSelect>>', self.on_indicator_selected)

        # Sağ panel - Sorular
        right_panel = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

        # Sağ panel başlığı
        right_title = tk.Label(right_panel, text=self.lm.tr("title_questions_answers", "Soru ve Yanıtlar"),
                              font=('Segoe UI', 12, 'bold'), bg='white', fg='#2c3e50')
        right_title.pack(pady=10)

        # Seçilen gösterge bilgisi (çerçeve aşağı doğru genişleyebilir ve metin sarılır)
        self.selected_indicator_frame = tk.Frame(right_panel, bg='#ecf0f1', relief='solid', bd=1)
        self.selected_indicator_frame.pack(fill='x', padx=10, pady=5)

        self.indicator_info_label = tk.Label(
            self.selected_indicator_frame,
            text=self.lm.tr("msg_select_indicator", "Lütfen bir gösterge seçin"),
            font=('Segoe UI', 10), bg='#ecf0f1', fg='#2c3e50',
            justify='left', anchor='w'
        )
        # Başlangıçta makul bir wraplength; sonra dinamik olarak güncellenecek
        self.indicator_info_label.config(wraplength=600)
        self.indicator_info_label.pack(fill='x', padx=10, pady=8)
        # Çerçeve genişliği değiştikçe label'ın wraplength değerini güncelle
        def _update_indicator_wrap(event) -> None:
            try:
                new_wrap = max(200, event.width - 20)
                self.indicator_info_label.config(wraplength=new_wrap)
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        self.selected_indicator_frame.bind('<Configure>', _update_indicator_wrap)

        # Sorular alanı
        self.questions_frame = tk.Frame(right_panel, bg='white')
        self.questions_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Kaydet butonu
        save_frame = tk.Frame(right_panel, bg='white')
        save_frame.pack(fill='x', padx=10, pady=10)

        self.save_button = tk.Button(save_frame, text=self.lm.tr("btn_save_responses", "Yanıtları Kaydet"),
                                    font=('Segoe UI', 10, 'bold'), bg='#27ae60', fg='white',
                                    relief='flat', bd=0, padx=20, pady=10,
                                    command=self.save_responses, state='disabled')
        self.save_button.pack(side='right')

        # Mevcut yanıtları yükle butonu
        self.load_button = tk.Button(save_frame, text=self.lm.tr("btn_load_responses", "Mevcut Yanıtları Yükle"),
                                    font=('Segoe UI', 10), bg='#3498db', fg='white',
                                    relief='flat', bd=0, padx=15, pady=10,
                                    command=self.load_existing_responses, state='disabled')
        self.load_button.pack(side='left')

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            # SDG hedeflerini yükle
            self.load_sdg_goals()

            # İlerleme bilgisini güncelle
            self.update_progress()

        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_data_load', 'Veriler yüklenirken hata oluştu')}: {str(e)}")

    def back_to_sdg(self) -> None:
        """SDG ana ekranına geri dön"""
        try:
            # Mevcut içeriği temizle ve SDG ana ekranını yükle
            for widget in self.parent.winfo_children():
                widget.destroy()
            from .sdg_gui import SDGGUI
            SDGGUI(self.parent, self.company_id)
        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_back_nav', 'Geri dönme işleminde hata')}: {str(e)}")

    def load_sdg_goals(self) -> None:
        """SDG hedeflerini yükle"""
        try:
            # SDG hedeflerini al
            conn = self.data_collection.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, code, title_tr FROM sdg_goals ORDER BY code")
            goals = cursor.fetchall()
            conn.close()

            # ComboBox'a ekle
            goal_options = []
            for goal in goals:
                code = goal[1]
                default_title = goal[2]
                title = self.lm.tr(f"sdg_goal_{code}", default_title)
                prefix = self.lm.tr("sdg_prefix", "SDG")
                goal_options.append(f"{prefix} {code}: {title}")
            
            self.sdg_combo['values'] = goal_options

            if goal_options:
                self.sdg_combo.set(goal_options[0])
                self.on_sdg_selected(None)

        except Exception as e:
            logging.error(f"SDG hedefleri yüklenirken hata: {e}")

    def on_sdg_selected(self, event) -> None:
        """SDG hedefi seçildiğinde"""
        try:
            selected_text = self.sdg_var.get()
            if not selected_text:
                return

            # SDG numarasını çıkar
            sdg_no = int(selected_text.split(':')[0].split()[-1])

            # Göstergeleri yükle
            self.load_indicators(sdg_no)

        except Exception as e:
            logging.error(f"SDG seçimi işlenirken hata: {e}")

    def load_indicators(self, sdg_no: int) -> None:
        """Gösterge listesini yükle"""
        try:
            # Mevcut gösterge listesini temizle
            for item in self.indicators_tree.get_children():
                self.indicators_tree.delete(item)

            # Göstergeleri al
            questions = self.data_collection.get_questions_for_company(self.company_id, sdg_no)

            for question_data in questions:
                indicator_code = question_data['indicator_code']
                indicator_title = question_data['indicator_title']

                # Gösterge durumunu al
                status = self.get_indicator_status(indicator_code)
                progress = status.get('completion_percentage', 0)

                # Durum metni
                if progress == 0:
                    status_text = self.lm.tr("status_not_started", "Başlanmadı")
                elif progress < 100:
                    status_text = self.lm.tr("status_in_progress", "Devam Ediyor")
                else:
                    status_text = self.lm.tr("status_completed", "Tamamlandı")

                # Treeview'a ekle
                self.indicators_tree.insert('', 'end', values=(
                    indicator_code,
                    indicator_title[:50] + '...' if len(indicator_title) > 50 else indicator_title,
                    status_text,
                    f"{progress:.1f}%"
                ))

        except Exception as e:
            logging.error(f"Göstergeler yüklenirken hata: {e}")

    def get_indicator_status(self, indicator_code: str) -> Dict:
        """Gösterge durumunu getir"""
        try:
            conn = self.data_collection.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT answered_questions, total_questions, completion_percentage
                FROM sdg_indicator_status 
                WHERE company_id = ? AND indicator_code = ?
            """, (self.company_id, indicator_code))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'answered_questions': result[0],
                    'total_questions': result[1],
                    'completion_percentage': result[2]
                }
            else:
                return {
                    'answered_questions': 0,
                    'total_questions': 3,
                    'completion_percentage': 0.0
                }

        except Exception as e:
            logging.error(f"Gösterge durumu getirilirken hata: {e}")
            return {
                'answered_questions': 0,
                'total_questions': 3,
                'completion_percentage': 0.0
            }

    def on_indicator_selected(self, event) -> None:
        """Gösterge seçildiğinde"""
        try:
            selection = self.indicators_tree.selection()
            if not selection:
                return

            item = self.indicators_tree.item(selection[0])
            indicator_code = item['values'][0]

            # Gösterge bilgilerini göster
            self.show_indicator_info(indicator_code)

            # Soruları yükle
            self.load_questions(indicator_code)

            # Butonları aktif et
            self.save_button.config(state='normal')
            self.load_button.config(state='normal')

        except Exception as e:
            logging.error(f"Gösterge seçimi işlenirken hata: {e}")

    def show_indicator_info(self, indicator_code: str) -> None:
        """Gösterge bilgilerini göster"""
        try:
            # Gösterge bilgilerini al
            questions = self.data_collection.get_questions_for_company(self.company_id)
            indicator_data = None

            for question_data in questions:
                if question_data['indicator_code'] == indicator_code:
                    indicator_data = question_data
                    break

            if indicator_data:
                info_text = f"SDG {indicator_data['sdg_no']}: {indicator_data['sdg_title']}\n"
                info_text += f"{self.lm.tr('lbl_target', 'Alt Hedef:')} {indicator_data['target_code']} - {indicator_data['target_title']}\n"
                info_text += f"{self.lm.tr('lbl_indicator', 'Gösterge:')} {indicator_code} - {indicator_data['indicator_title']}"

                self.indicator_info_label.config(text=info_text)
            else:
                self.indicator_info_label.config(text=f"{self.lm.tr('lbl_indicator', 'Gösterge:')} {indicator_code}")

        except Exception as e:
            logging.error(f"Gösterge bilgileri gösterilirken hata: {e}")

    def load_questions(self, indicator_code: str) -> None:
        """Soruları yükle"""
        try:
            # Mevcut soruları temizle
            for widget in self.questions_frame.winfo_children():
                widget.destroy()

            # Soruları al
            questions = self.data_collection.get_questions_for_indicator(indicator_code)

            if not questions:
                no_questions_label = tk.Label(self.questions_frame,
                                            text=self.lm.tr("msg_no_questions_found", "Bu gösterge için soru bulunamadı"),
                                            font=('Segoe UI', 12), fg='#7f8c8d', bg='white')
                no_questions_label.pack(expand=True)
                return

            # Soruları göster
            self.question_widgets = []

            for i, question in enumerate(questions):
                # Soru çerçevesi
                question_frame = tk.Frame(self.questions_frame, bg='#f8f9fa', relief='solid', bd=1)
                question_frame.pack(fill='x', padx=5, pady=5)

                # Soru numarası ve metni
                question_header = tk.Frame(question_frame, bg='#3498db', height=40)
                question_header.pack(fill='x')
                question_header.pack_propagate(False)

                question_title = tk.Label(question_header,
                                        text=self.lm.tr("lbl_question_number", "Soru {number}").format(number=question['question_number']),
                                        font=('Segoe UI', 10, 'bold'), fg='white', bg='#3498db')
                question_title.pack(side='left', padx=10, pady=10)

                # Soru metni
                question_text_frame = tk.Frame(question_frame, bg='#f8f9fa')
                question_text_frame.pack(fill='x', padx=10, pady=5)

                question_text_label = tk.Label(question_text_frame,
                                             text=question['question_text'],
                                             font=('Segoe UI', 9), fg='#2c3e50', bg='#f8f9fa',
                                             wraplength=500, justify='left')
                question_text_label.pack(anchor='w')

                # Yanıt alanı
                answer_frame = tk.Frame(question_frame, bg='#f8f9fa')
                answer_frame.pack(fill='x', padx=10, pady=5)

                # Yanıt türü seçimi
                answer_type_frame = tk.Frame(answer_frame, bg='#f8f9fa')
                answer_type_frame.pack(fill='x', pady=2)

                tk.Label(answer_type_frame, text=self.lm.tr("lbl_answer_type", "Yanıt Türü:"),
                        font=('Segoe UI', 8, 'bold'), bg='#f8f9fa').pack(side='left')

                answer_type_var = tk.StringVar(value='text')
                answer_type_combo = ttk.Combobox(answer_type_frame, textvariable=answer_type_var,
                                               values=['text', 'number', 'yes_no'], state='readonly', width=10)
                answer_type_combo.pack(side='left', padx=5)

                # Yanıt girişi
                answer_input_frame = tk.Frame(answer_frame, bg='#f8f9fa')
                answer_input_frame.pack(fill='x', pady=2)

                # Metin yanıtı
                text_answer = tk.Text(answer_input_frame, height=3, width=60, font=('Segoe UI', 9))
                text_answer.pack(fill='x')

                # Sayısal yanıtı
                number_answer = tk.Entry(answer_input_frame, font=('Segoe UI', 9))

                # Evet/Hayır yanıtı
                yes_no_var = tk.StringVar()
                yes_no_frame = tk.Frame(answer_input_frame, bg='#f8f9fa')
                yes_radio = tk.Radiobutton(yes_no_frame, text=self.lm.tr("lbl_yes", "Evet"), variable=yes_no_var, value="Evet", bg='#f8f9fa')
                no_radio = tk.Radiobutton(yes_no_frame, text=self.lm.tr("lbl_no", "Hayır"), variable=yes_no_var, value="Hayır", bg='#f8f9fa')
                yes_radio.pack(side='left', padx=5)
                no_radio.pack(side='left', padx=5)

                # Yanıt türü değiştiğinde
                def on_answer_type_change(event, text_widget=text_answer, number_widget=number_answer, yes_no_widget=yes_no_frame) -> None:
                    selected_type = answer_type_var.get()

                    # Tüm widget'ları gizle
                    text_widget.pack_forget()
                    number_widget.pack_forget()
                    yes_no_widget.pack_forget()

                    # Seçilen türe göre göster
                    if selected_type == 'text':
                        text_widget.pack(fill='x')
                    elif selected_type == 'number':
                        number_widget.pack(fill='x')
                    elif selected_type == 'yes_no':
                        yes_no_widget.pack(fill='x')

                answer_type_combo.bind('<<ComboboxSelected>>', on_answer_type_change)

                # İlk yüklemede metin göster
                on_answer_type_change(None)

                # Widget'ları sakla
                self.question_widgets.append({
                    'question_number': question['question_number'],
                    'question_text': question['question_text'],
                    'answer_type_var': answer_type_var,
                    'text_answer': text_answer,
                    'number_answer': number_answer,
                    'yes_no_var': yes_no_var,
                    'responsible_unit': question.get('responsible_unit', ''),
                    'data_source': question.get('data_source', ''),
                    'data_method': question.get('data_method', ''),
                    'measurement_frequency': question.get('measurement_frequency', ''),
                    'related_sectors': question.get('related_sectors', ''),
                    'related_funds': question.get('related_funds', ''),
                    'kpi_metric': question.get('kpi_metric', ''),
                    'gri_connection': question.get('gri_connection', ''),
                    'tsrs_connection': question.get('tsrs_connection', ''),
                    'implementation_requirement': question.get('implementation_requirement', ''),
                    'data_quality': question.get('data_quality', ''),
                    'notes': question.get('notes', '')
                })

            # Scrollbar ekle
            canvas = tk.Canvas(self.questions_frame, bg='white')
            scrollbar = ttk.Scrollbar(self.questions_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Mevcut widget'ları scrollable frame'e taşı
            for widget in self.questions_frame.winfo_children():
                if isinstance(widget, tk.Frame) and widget != canvas and widget != scrollbar:
                    widget.pack(in_=scrollable_frame, fill='x', padx=5, pady=5)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            logging.error(f"Sorular yüklenirken hata: {e}")

    def save_responses(self) -> None:
        """Yanıtları kaydet"""
        try:
            # Seçili göstergeyi al
            selection = self.indicators_tree.selection()
            if not selection:
                messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_select_indicator", "Lütfen bir gösterge seçin"))
                return

            item = self.indicators_tree.item(selection[0])
            indicator_code = item['values'][0]

            # Her soru için yanıtı kaydet
            for widget_data in self.question_widgets:
                question_number = widget_data['question_number']
                answer_type = widget_data['answer_type_var'].get()

                answer_text = None
                answer_value = None
                answer_boolean = None

                if answer_type == 'text':
                    answer_text = widget_data['text_answer'].get('1.0', tk.END).strip()
                elif answer_type == 'number':
                    try:
                        answer_value = float(widget_data['number_answer'].get())
                    except ValueError:
                        answer_value = None
                elif answer_type == 'yes_no':
                    yes_no_value = widget_data['yes_no_var'].get()
                    answer_boolean = (yes_no_value == "Evet")
                    answer_text = yes_no_value

                # Yanıtı kaydet
                success = self.data_collection.save_answer(
                    company_id=self.company_id,
                    indicator_code=indicator_code,
                    question_number=question_number,
                    answer_text=answer_text,
                    answer_value=answer_value,
                    answer_boolean=answer_boolean,
                    responsible_unit=widget_data['responsible_unit'],
                    data_source=widget_data['data_source'],
                    data_method=widget_data['data_method'],
                    measurement_frequency=widget_data['measurement_frequency'],
                    related_sectors=widget_data['related_sectors'],
                    related_funds=widget_data['related_funds'],
                    kpi_metric=widget_data['kpi_metric'],
                    gri_connection=widget_data['gri_connection'],
                    tsrs_connection=widget_data['tsrs_connection'],
                    implementation_requirement=widget_data['implementation_requirement'],
                    data_quality=widget_data['data_quality'],
                    notes=widget_data['notes']
                )

                if not success:
                    messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('lbl_question_number', 'Soru {number}').format(number=question_number)} kaydedilemedi")
                    return

            messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_responses_saved", "Yanıtlar başarıyla kaydedildi"))

            # Gösterge listesini güncelle
            self.load_indicators(int(self.sdg_var.get().split(':')[0].split()[-1]))

            # İlerleme bilgisini güncelle
            self.update_progress()

        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_saving_responses', 'Yanıtlar kaydedilirken hata oluştu')}: {str(e)}")

    def load_existing_responses(self) -> None:
        """Mevcut yanıtları yükle"""
        try:
            # Seçili göstergeyi al
            selection = self.indicators_tree.selection()
            if not selection:
                messagebox.showwarning(self.lm.tr("title_warning", "Uyarı"), self.lm.tr("msg_select_indicator", "Lütfen bir gösterge seçin"))
                return

            item = self.indicators_tree.item(selection[0])
            indicator_code = item['values'][0]

            # Mevcut yanıtları al
            responses = self.data_collection.get_indicator_responses(self.company_id, indicator_code)

            if not responses:
                messagebox.showinfo(self.lm.tr("title_info", "Bilgi"), self.lm.tr("msg_no_responses_found", "Bu gösterge için kayıtlı yanıt bulunamadı"))
                return

            # Yanıtları widget'lara yükle
            for response in responses:
                question_number = response['question_number']

                # İlgili widget'ı bul
                widget_data = None
                for widget in self.question_widgets:
                    if widget['question_number'] == question_number:
                        widget_data = widget
                        break

                if widget_data:
                    # Yanıt türünü belirle
                    if response['answer_text'] and response['answer_text'] in ['Evet', 'Hayır']:
                        widget_data['answer_type_var'].set('yes_no')
                        widget_data['yes_no_var'].set(response['answer_text'])
                    elif response['answer_value'] is not None:
                        widget_data['answer_type_var'].set('number')
                        widget_data['number_answer'].delete(0, tk.END)
                        widget_data['number_answer'].insert(0, str(response['answer_value']))
                    else:
                        widget_data['answer_type_var'].set('text')
                        widget_data['text_answer'].delete('1.0', tk.END)
                        widget_data['text_answer'].insert('1.0', response['answer_text'] or '')

            messagebox.showinfo(self.lm.tr("title_success", "Başarılı"), self.lm.tr("msg_responses_loaded", "Mevcut yanıtlar yüklendi"))

        except Exception as e:
            messagebox.showerror(self.lm.tr("title_error", "Hata"), f"{self.lm.tr('err_loading_responses', 'Mevcut yanıtlar yüklenirken hata oluştu')}: {str(e)}")

    def update_progress(self) -> None:
        """İlerleme bilgisini güncelle"""
        try:
            progress = self.data_collection.get_company_progress(self.company_id)

            completion_percentage = progress['completion_percentage']
            answered_questions = progress['answered_questions']
            total_questions = progress['total_questions']

            self.progress_label.config(text=self.lm.tr("lbl_progress", "İlerleme: %{progress}").format(progress=f"{completion_percentage:.1f}") + f" ({answered_questions}/{total_questions})")
            self.progress_bar['value'] = completion_percentage

        except Exception as e:
            logging.error(f"İlerleme bilgisi güncellenirken hata: {e}")

if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.title("SDG Veri Toplama Sistemi")
    app = SDGDataCollectionGUI(root, 1)
    root.mainloop()
