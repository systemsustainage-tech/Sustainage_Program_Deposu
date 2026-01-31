import logging
import tkinter as tk
from functools import partial
from tkinter import messagebox, ttk
from typing import Any, Dict, List

from utils.language_manager import LanguageManager
from utils.ui_theme import apply_theme

try:
    from utils.progress_engine import STATUS_COMPLETED, STATUS_IN_PROGRESS, STATUS_NOT_STARTED
    from utils.progress_engine import ProgressEngine as _ProgressEngine
    ProgressEngineClass: Any = _ProgressEngine
except Exception:
    ProgressEngineClass = None
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
import os
import sys

from .sdg_manager import SDGManager

# Görev yönetim sistemi
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from tasks.notification_manager import NotificationManager as _NotificationManager
    from tasks.task_manager import TaskManager as _TaskManager
    NotificationManagerClass: Any = _NotificationManager
    TaskManagerClass: Any = _TaskManager
except ImportError:
    TaskManagerClass = None
    NotificationManagerClass = None

try:
    from water.water_gui import WaterGUI as _WaterGUI
    WaterGUIClass: Any = _WaterGUI
except Exception:
    WaterGUIClass = None

class SDGGUI:
    """SDG Modülü GUI - 17 hedef, 169 alt hedef, 232 gösterge yönetimi"""

    def __init__(self, parent, company_id: int) -> None:
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()
        self.sdg_manager = SDGManager()
        try:
            # c:\SDG\modules\sdg\sdg_gui.py -> c:\SDG
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.db_path: str | None = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
        except Exception:
            self.db_path = None
        self.progress_engine = ProgressEngineClass(self.db_path) if ProgressEngineClass is not None else None
        self.step_registry = [
            ('sdg_start', self.lm.tr('step_start', 'Başlangıç')),
            ('sdg_collect', self.lm.tr('step_collect', 'Veri Toplama')),
            ('sdg_validate', self.lm.tr('step_validate', 'Doğrulama')),
            ('sdg_preview', self.lm.tr('step_preview', 'Önizleme')),
            ('sdg_complete', self.lm.tr('step_complete', 'Tamamla'))
        ]

        # Seçim sistemi için değişkenler
        self.selected_goals: List[Any] = []
        self.available_goals: List[Any] = []
        self.goal_buttons: Dict[Any, tk.Button] = {}
        self.accordion_states: Dict[Any, bool] = {}

        try:
            self.parent.winfo_toplevel().state('zoomed')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        self.setup_ui()
        self.load_data()
        self.load_saved_selections()  # Kaydedilen seçimleri yükle
        try:
            if self.progress_engine:
                self.progress_engine.initialize_steps(user_id=1, company_id=self.company_id, module_code='sdg', steps=self.step_registry)
                # İlk adımı in_progress
                self.progress_engine.set_progress(1, self.company_id, 'sdg', 'sdg_start', 'Başlangıç', STATUS_IN_PROGRESS)
                self._update_guided_header()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def setup_ui(self) -> None:
        """SDG modülü arayüzünü oluştur"""
        apply_theme(self.parent)
        # Ana frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Başlık ve guided header
        title_frame = tk.Frame(main_frame, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text=self.lm.tr('sdg_module_title', "SDG Modülü - Sürdürülebilir Kalkınma Amaçları"),
                              font=('Segoe UI', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # Guided header (stepper + progress bar + next button)
        guided = tk.Frame(main_frame, bg='#f8fafc', height=50)
        guided.pack(fill='x', pady=(0, 10))
        guided.pack_propagate(False)
        self._guided_frame = guided
        try:
            from tkinter import ttk as _ttk
            self._progress_var = tk.DoubleVar(value=0.0)
            self._progress_bar = _ttk.Progressbar(guided, maximum=100.0, variable=self._progress_var)
            self._progress_bar.pack(side='left', fill='x', expand=True, padx=10, pady=10)

            self._step_info = tk.Label(guided, text=f"{self.lm.tr('step_label', 'Adım: ')} {self.lm.tr('sdg_start', 'Başlangıç')}", font=('Segoe UI', 10, 'bold'), bg='#f8fafc', fg='#334155')
            self._step_info.pack(side='left', padx=10)

            def _next_step():
                try:
                    if not self.progress_engine:
                        return
                    # Mevcut adımı bul
                    progress = self.progress_engine.get_module_progress(self.company_id, 'sdg', user_id=1)
                    order = [sid for sid, _ in self.step_registry]
                    current_sid = None
                    for p in progress:
                        if p['status'] == STATUS_IN_PROGRESS:
                            current_sid = p['step_id']
                            break
                    if current_sid is None:
                        current_sid = order[0]
                    idx = order.index(current_sid)
                    # Mevcut adımı tamamla
                    self.progress_engine.set_progress(1, self.company_id, 'sdg', current_sid,
                                                      dict(self.step_registry)[current_sid], STATUS_COMPLETED)
                    # Sonraki adımı başlat
                    if idx + 1 < len(order):
                        next_sid = order[idx + 1]
                        self.progress_engine.set_progress(1, self.company_id, 'sdg', next_sid,
                                                          dict(self.step_registry)[next_sid], STATUS_IN_PROGRESS)
                    self._update_guided_header()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

            _ttk.Button(guided, text=self.lm.tr('next_step', " Sonraki Adım"), style='Primary.TButton', command=_next_step).pack(side='right', padx=10)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

        # İstatistik kartları
        self.create_stats_frame(main_frame)

        # Ana içerik alanı - İki panel yan yana
        content_frame = tk.Frame(main_frame, bg='#f5f5f5')
        content_frame.pack(fill='both', expand=True)

        # Sol panel - Mevcut Hedefler (kendi scroll'u ile)
        left_panel = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Sol panel başlığı
        available_title = tk.Label(left_panel, text=self.lm.tr('sdg_available_goals', "Mevcut SDG Hedefleri"),
                                  font=('Segoe UI', 12, 'bold'), bg='white', fg='#2c3e50')
        available_title.pack(pady=10)

        # Sol panel için canvas ve scrollbar
        self.left_canvas = tk.Canvas(left_panel, bg='white', highlightthickness=0)
        self.left_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.left_canvas.yview)
        self.left_scrollable_frame = tk.Frame(self.left_canvas, bg='white')

        self.left_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        )

        left_window = self.left_canvas.create_window((0, 0), window=self.left_scrollable_frame, anchor="nw")
        
        def _configure_left_canvas(event):
            # Canvas genişliği değiştiğinde iç frame'i de güncelle
            self.left_canvas.itemconfig(left_window, width=event.width)
        
        self.left_canvas.bind("<Configure>", _configure_left_canvas)
        
        self.left_canvas.configure(yscrollcommand=self.left_scrollbar.set)

        self.left_canvas.pack(side="left", fill="both", expand=True)
        self.left_scrollbar.pack(side="right", fill="y")

        # Sol panel mouse wheel desteği
        def _on_left_mousewheel(event) -> None:
            try:
                self.left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        self.left_canvas.bind("<MouseWheel>", _on_left_mousewheel)

        # Mevcut hedefler listesi - Resim tabanlı
        self.available_frame = tk.Frame(self.left_scrollable_frame, bg='white')
        self.available_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # SDG resimlerini yükle
        self.sdg_images: Dict[int, Any] = {}
        self.image_references: List[Any] = []
        try:
            self.load_sdg_images()
        except Exception as e:
            logging.info(f"[UYARI] SDG resimleri yüklenemedi: {e}")
            # Resim olmadan text butonlarla devam et

        # Sağ panel - Seçilen Hedefler (kendi scroll'u ile)
        right_panel = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

        # Sağ panel başlığı
        selected_title = tk.Label(right_panel, text=self.lm.tr('sdg_selected_goals', "Seçilen SDG Hedefleri"),
                                 font=('Segoe UI', 12, 'bold'), bg='white', fg='#2c3e50')
        selected_title.pack(pady=10)

        # Sağ panel için canvas ve scrollbar
        self.right_canvas = tk.Canvas(right_panel, bg='white', highlightthickness=0)
        self.right_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.right_canvas.yview)
        self.right_scrollable_frame = tk.Frame(self.right_canvas, bg='white')

        self.right_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        )

        right_window = self.right_canvas.create_window((0, 0), window=self.right_scrollable_frame, anchor="nw")
        
        def _configure_right_canvas(event):
            # Canvas genişliği değiştiğinde iç frame'i de güncelle
            self.right_canvas.itemconfig(right_window, width=event.width)
            
        self.right_canvas.bind("<Configure>", _configure_right_canvas)
        
        self.right_canvas.configure(yscrollcommand=self.right_scrollbar.set)

        self.right_canvas.pack(side="left", fill="both", expand=True)
        self.right_scrollbar.pack(side="right", fill="y")

        # Sağ panel mouse wheel desteği
        def _on_right_mousewheel(event) -> None:
            try:
                self.right_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        self.right_canvas.bind("<MouseWheel>", _on_right_mousewheel)

        # Seçilen hedefler listesi
        self.selected_frame = tk.Frame(self.right_scrollable_frame, bg='white')
        self.selected_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Butonlar için frame oluştur
        button_frame = tk.Frame(self.parent, bg='#2c3e50', height=80)
        button_frame.pack(fill='x', pady=(0, 10))
        button_frame.pack_propagate(False)

        # İlerleme Takibi butonu
        ttk.Button(button_frame, text=self.lm.tr('btn_progress_tracking', " İlerleme Takibi"), style='Primary.TButton', command=self.open_progress_tracking).pack(side='right', padx=5, pady=10)

        # Veri Toplama butonu
        ttk.Button(button_frame, text=self.lm.tr('btn_data_collection', " Veri Toplama"), style='Primary.TButton', command=self.open_data_collection).pack(side='right', padx=5, pady=10)

        # Gelişmiş İlerleme Takibi butonu
        ttk.Button(button_frame, text=self.lm.tr('btn_advanced_analysis', " Gelişmiş Analiz"), style='Primary.TButton', command=self.open_advanced_progress).pack(side='right', padx=5, pady=10)

        # Soru Bankası butonu
        ttk.Button(button_frame, text=self.lm.tr('btn_question_bank', " Soru Bankası"), style='Primary.TButton', command=self.open_question_bank).pack(side='right', padx=5, pady=10)

        # Veri Doğrulama butonu
        ttk.Button(button_frame, text=self.lm.tr('btn_data_validation', " Veri Doğrulama"), style='Primary.TButton', command=self.open_data_validation).pack(side='right', padx=5, pady=10)

        # Su Yönetimi butonu
        ttk.Button(button_frame, text=self.lm.tr('btn_water_management', " Su Yönetimi"), style='Primary.TButton', command=self.open_water_management).pack(side='right', padx=5, pady=10)

        # Raporlama butonu
        ttk.Button(button_frame, text=self.lm.tr('btn_reporting', " Raporlama"), style='Primary.TButton', command=self.open_reporting).pack(side='right', padx=5, pady=10)

        # AI Rapor butonu
        try:
            from modules.ai.ai_report_button import AIReportButton
            ai_frame = tk.Frame(button_frame, bg='white')
            ai_frame.pack(side='right', padx=5, pady=10)

            AIReportButton(
                parent=ai_frame,
                report_type='sdg',
                data_context={
                    'company_id': self.company_id,
                    'period': '2024'
                }
            )
        except Exception as e:
            logging.info(f"[UYARI] SDG AI Button eklenemedi: {e}")

        # Detay tablosu butonu
        ttk.Button(button_frame, text=self.lm.tr('btn_detail_table', " Detay Tablosu"), style='Primary.TButton', command=self.show_sdg_details_table).pack(side='right', padx=5, pady=10)
        ttk.Button(button_frame, text=self.lm.tr('btn_report_center', " Rapor Merkezi"), style='Primary.TButton', command=self.open_report_center_sdg).pack(side='left', padx=5, pady=10)

        # Ana Dashboard butonu kaldırıldı

    def open_report_center_sdg(self) -> None:
        try:
            from modules.reporting.report_center_gui import ReportCenterGUI
            win = tk.Toplevel(self.parent)
            apply_theme(win)
            gui = ReportCenterGUI(win, self.company_id)
            try:
                gui.module_filter_var.set('sdg')
                gui.refresh_reports()
            except Exception as e:
                logging.error(f"{self.lm.tr('sdg_report_filter_error', 'SDG raporları filtrelenirken hata')}: {e}")
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('report_center_open_error', 'Rapor Merkezi açılamadı')}:\n{e}")
            logging.error(f"{self.lm.tr('report_center_open_error_log', 'Rapor merkezi açma hatası')}: {e}")

    def _update_guided_header(self) -> None:
        try:
            if not self.progress_engine:
                return
            percent = self.progress_engine.get_completion_percentage(self.company_id, 'sdg', self.step_registry, user_id=1)
            self._progress_var.set(percent)
            # Aktif adımı göster
            progress = self.progress_engine.get_module_progress(self.company_id, 'sdg', user_id=1)
            active = None
            for p in progress:
                if p['status'] == STATUS_IN_PROGRESS:
                    active = p
                    break
            step_text = f"{self.lm.tr('step_label', 'Adım')}: {active['step_title']}" if active else f"{self.lm.tr('step_label', 'Adım')}: -"
            self._step_info.configure(text=step_text)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
    def open_water_management(self) -> None:
        """Su Yönetimi modülünü ayrı pencerede aç"""
        try:
            if WaterGUIClass is None:
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("water_module_not_found", "WaterGUI modülü bulunamadı veya yüklenemedi."))
                return
            win = tk.Toplevel(self.parent)
            win.title(self.lm.tr("water_management_title", " Su Yönetimi"))
            apply_theme(win)
            WaterGUIClass(win)
        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('water_module_open_error', 'Su Yönetimi açılırken hata')}: {e}")

    def load_sdg_images(self) -> None:
        """SDG resimlerini yükle - Gelişmiş error handling ve fallback"""
        try:
            import os

            from PIL import Image, ImageTk

            # Resimler klasörü yolunu bul
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            resimler_dir = os.path.join(base_dir, "resimler")

            # Resimler klasörünün varlığını kontrol et
            if not os.path.exists(resimler_dir):
                logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('images_dir_not_found', 'Resimler klasörü bulunamadı')}: {resimler_dir}")
                logging.info(f"[{self.lm.tr('info', 'BİLGİ')}] {self.lm.tr('using_text_buttons', 'Text tabanlı butonlar kullanılacak.')}")
                return

            loaded_count = 0
            failed_images = []

            for i in range(1, 18):  # SDG 1-17
                image_path = os.path.join(resimler_dir, f"{i}.png")

                if not os.path.exists(image_path):
                    # Alternatif formatları dene (.jpg, .jpeg)
                    for ext in ['.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
                        alt_path = os.path.join(resimler_dir, f"{i}{ext}")
                        if os.path.exists(alt_path):
                            image_path = alt_path
                            break

                if os.path.exists(image_path):
                    try:
                        # Resmi yükle ve boyutlandır
                        image: Any = Image.open(image_path)

                        # Resim boyutunu kontrol et
                        if image.size[0] == 0 or image.size[1] == 0:
                            raise ValueError(f"Geçersiz resim boyutu: {image.size}")

                        # Daha büyük boyut - buton arka planı için
                        try:
                            from PIL.Image import Resampling
                            resample: Any = Resampling.LANCZOS
                        except Exception:
                            resample = getattr(Image, 'LANCZOS', getattr(Image, 'BICUBIC', 1))
                        image = image.resize((120, 120), resample)

                        # Widgetin bulunduğu Tk bağlamına bağla
                        photo = ImageTk.PhotoImage(image, master=self.parent)

                        # Referansı sakla (garbage collection'ı önlemek için)
                        self.image_references.append(photo)
                        self.sdg_images[i] = photo
                        loaded_count += 1

                    except Exception as img_error:
                        logging.error(f"[{self.lm.tr('warning', 'UYARI')}] SDG {i} {self.lm.tr('image_load_error', 'resmi yüklenirken hata')}: {img_error}")
                        failed_images.append(i)
                        # Resim yüklenemezse None olarak işaretle
                        self.sdg_images[i] = None
                else:
                    logging.warning(f"[{self.lm.tr('warning', 'UYARI')}] SDG {i} {self.lm.tr('image_not_found', 'resmi bulunamadı')}: {image_path}")
                    failed_images.append(i)
                    self.sdg_images[i] = None

            # Başarı raporu
            logging.info(f"[OK] {self.lm.tr('total_images_loaded', 'Toplam SDG resmi başarıyla yüklendi')}: {loaded_count}/17")

            if failed_images:
                logging.error(f"[{self.lm.tr('info', 'BİLGİ')}] {self.lm.tr('failed_images_text', 'Yüklenemeyen resimler (text buton kullanılacak)')}: {failed_images}")

            if loaded_count == 0:
                logging.warning(f"[{self.lm.tr('warning', 'UYARI')}] {self.lm.tr('no_images_loaded', 'Hiçbir SDG resmi yüklenemedi. Tüm butonlar text tabanlı olacak.')}")
            elif loaded_count < 17:
                logging.info(f"[{self.lm.tr('info', 'BİLGİ')}] {17 - loaded_count} {self.lm.tr('images_using_text', 'SDG resmi için text buton kullanılacak.')}")

        except ImportError as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] PIL/Pillow {self.lm.tr('module_load_error', 'modülü yüklenemedi')}: {e}")
            logging.info(f"[{self.lm.tr('solution', 'ÇÖZÜM')}] pip install Pillow>=10.0.0")
            logging.info(f"[{self.lm.tr('info', 'BİLGİ')}] {self.lm.tr('using_text_buttons', 'Text tabanlı butonlar kullanılacak.')}")
        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('images_load_unexpected_error', 'SDG resimleri yüklenirken beklenmeyen hata')}: {e}")
            logging.info(f"[{self.lm.tr('info', 'BİLGİ')}] {self.lm.tr('using_text_buttons', 'Text tabanlı butonlar kullanılacak.')}")
            import traceback
            traceback.print_exc()

    def create_stats_frame(self, parent) -> None:
        """İstatistik kartlarını oluştur"""
        stats_frame = tk.Frame(parent, bg='#f5f5f5')
        stats_frame.pack(fill='x', pady=(0, 10))

        # İstatistik kartları
        self.stats_cards = {}

        stats_data = [
            (self.lm.tr("stats_total_goals", "Toplam Hedef (Kalan)"), "total_goals", "#3498db"),
            (self.lm.tr("stats_selected_goals", "Seçilen Hedef"), "selected_goals", "#f39c12"),
            (self.lm.tr("stats_answered_indicators", "Cevaplanan Gösterge"), "answered_indicators", "#e74c3c"),
            (self.lm.tr("stats_selection_percentage", "Seçim Yüzdesi"), "selection_percentage", "#2ecc71"),
            (self.lm.tr("stats_answer_percentage", "Yanıt Yüzdesi"), "answer_percentage", "#9b59b6")
        ]

        for i, (title, key, color) in enumerate(stats_data):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=1)
            card.pack(side='left', fill='x', expand=True, padx=(0, 5) if i < len(stats_data)-1 else 0)

            # Kart içeriği
            card_content = tk.Frame(card, bg=color)
            card_content.pack(fill='both', expand=True, padx=15, pady=10)

            # Başlık
            title_label = tk.Label(card_content, text=title, font=('Segoe UI', 9, 'bold'),
                                  fg='white', bg=color)
            title_label.pack()

            # Değer
            value_label = tk.Label(card_content, text="0", font=('Segoe UI', 16, 'bold'),
                                  fg='white', bg=color)
            value_label.pack()

            self.stats_cards[key] = value_label

    def load_data(self) -> None:
        """Verileri yükle"""
        try:
            # Hedefleri yükle
            self.available_goals = self.sdg_manager.get_sdg_goals()
            self.update_stats()
            self.display_available_goals()

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('data_load_error', 'Veriler yüklenirken hata oluştu')}: {str(e)}")

    def display_available_goals(self) -> None:
        """Mevcut hedefleri göster - resimlerle veya text ile"""
        # Önceki butonları temizle
        for widget in self.available_frame.winfo_children():
            widget.destroy()

        self.goal_buttons = {}

        # Resimleri grid formatında düzenle (3 sütun)
        row = 0
        col = 0

        for goal in self.available_goals:
            if goal not in self.selected_goals:  # Sadece seçilmemiş hedefleri göster
                goal[0]
                goal_code = goal[1]
                goal_title = goal[2]

                # Resim çerçevesi
                image_frame = tk.Frame(self.available_frame, bg='white', relief='solid', bd=2)
                image_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

                # Resim varsa resimli buton, yoksa text buton
                # goal_code verisi bazı durumlarda int dönebiliyor; .isdigit() sadece str için geçerli
                # Bu nedenle önce stringe çevirerek güvenli kontrol yapıyoruz
                goal_code_str = str(goal_code)
                goal_code_int = int(goal_code_str) if goal_code_str.isdigit() else None
                if goal_code_int and goal_code_int in self.sdg_images and self.sdg_images[goal_code_int]:
                    # Resimli buton
                    goal_btn = tk.Button(image_frame,
                                       image=self.sdg_images[goal_code_int],
                                       bg='white',
                                       relief='flat', bd=0,
                                       command=partial(self.select_goal, goal),
                                       cursor='hand2')
                    goal_btn.pack(padx=2, pady=2)

                    # Başlık label'ı
                    title_label = tk.Label(image_frame,
                                          text=f"{self.lm.tr('sdg_label','SDG')} {goal_code}: {goal_title[:30]}...",
                                          font=('Segoe UI', 8),
                                          bg='white', fg='#2c3e50',
                                          wraplength=130, justify='center')
                    title_label.pack(pady=(0, 5))
                else:
                    # Sadece metin butonu - resim yok
                    goal_btn = tk.Button(image_frame,
                                       text=f"{self.lm.tr('sdg_label','SDG')} {goal_code} - {goal_title}",
                                       font=('Segoe UI', 10, 'bold'),
                                       bg='#007bff', fg='white',
                                       relief='raised', bd=2,
                                       command=partial(self.select_goal, goal),
                                       cursor='hand2',
                                       wraplength=220,
                                       justify='center',
                                       height=3)
                    goal_btn.pack(padx=5, pady=5, fill='both', expand=True)
                    
                    # Dinamik metin kaydırma (pencere boyutu değişince)
                    goal_btn.bind('<Configure>', lambda e, b=goal_btn: b.configure(wraplength=e.width-10))

                self.goal_buttons[goal[0]] = goal_btn

                # Grid pozisyonunu güncelle
                col += 1
                if col >= 3:  # 3 sütun
                    col = 0
                    row += 1

        # Grid sütunlarını eşit genişlikte yap
        for i in range(3):
            self.available_frame.grid_columnconfigure(i, weight=1)

    def display_selected_goals(self) -> None:
        """Seçilen hedefleri accordion sistemiyle göster"""
        # Önceki içeriği temizle
        for widget in self.selected_frame.winfo_children():
            widget.destroy()

        for goal in self.selected_goals:
            # Ana hedef çerçevesi
            goal_frame = tk.Frame(self.selected_frame, bg='#f8f9fa', relief='solid', bd=2)
            goal_frame.pack(fill='x', pady=5, padx=5)

            # Üst kısım - Başlık ve genişlet butonu
            header_frame = tk.Frame(goal_frame, bg='#e74c3c')
            header_frame.pack(fill='x')

            # Başlık ve butonlar
            title_frame = tk.Frame(header_frame, bg='#e74c3c')
            title_frame.pack(fill='x', padx=5, pady=5)

            # Başlık
            goal_title = tk.Label(title_frame,
                                 text=f"{self.lm.tr('sdg_label','SDG')} {goal[1]}: {goal[2]}",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg='#e74c3c', fg='white',
                                 anchor='w')
            goal_title.pack(side='left', fill='x', expand=True)

            # Çıkış butonu (X)
            close_btn = tk.Button(title_frame,
                                  text="X",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg='#c0392b', fg='white',
                                  relief='raised', bd=2,
                                  command=partial(self.deselect_goal, goal))
            close_btn.pack(side='right', padx=(5, 0))

            # Genişlet/Küçült butonu
            button_text = "+" if not self.accordion_states.get(goal[0], False) else "-"
            expand_btn = tk.Button(title_frame,
                                  text=button_text,
                                  font=('Segoe UI', 10),
                                  bg='#007bff', fg='white',
                                  relief='raised', bd=2,
                                  command=partial(self.toggle_goal_details, goal))
            expand_btn.pack(side='right', padx=(5, 5))

            # Detay bilgileri
            detail_frame = tk.Frame(goal_frame, bg='#f8f9fa')
            detail_frame.pack(fill='x', padx=10, pady=5)

            # Alt hedefleri ve göstergeleri al
            self.add_goal_details(detail_frame, goal[0])

            # Accordion durumunu kontrol et ve göster/gizle
            if not hasattr(self, 'accordion_states'):
                self.accordion_states = {}

            if goal[0] not in self.accordion_states:
                self.accordion_states[goal[0]] = False  # Başlangıçta kapalı

            # Eğer kapalıysa gizle
            if not self.accordion_states[goal[0]]:
                detail_frame.pack_forget()

    def toggle_goal_details(self, goal) -> None:
        """Hedef detaylarını genişlet/küçült"""
        goal_id = goal[0]

        # Mevcut durumu kontrol et
        if not hasattr(self, 'accordion_states'):
            self.accordion_states = {}

        # Durumu değiştir
        self.accordion_states[goal_id] = not self.accordion_states[goal_id]

        # Tüm seçilen hedefleri yeniden çiz
        self.display_selected_goals()

    def add_goal_details(self, parent, goal_id) -> None:
        """Hedef detaylarını ekle (alt hedefler ve göstergeler)"""
        try:
            # Alt hedefleri al
            conn = self.sdg_manager.get_connection()
            cursor = conn.cursor()

            # Alt hedefler
            cursor.execute("""
                SELECT code, title_tr FROM sdg_targets 
                WHERE goal_id = ? 
                ORDER BY code
            """, (goal_id,))
            targets = cursor.fetchall()

            if targets:
                # Alt hedefler başlığı
                targets_header = tk.Frame(parent, bg='#ecf0f1', relief='raised', bd=1)
                targets_header.pack(fill='x', pady=(0, 5))

                targets_title = tk.Label(targets_header, text=self.lm.tr("sdg_targets_title", " Alt Hedefler"),
                                       font=('Segoe UI', 9, 'bold'), fg='#2c3e50', bg='#ecf0f1')
                targets_title.pack(side='left', padx=5, pady=3)

                # Alt hedefler listesi
                targets_frame = tk.Frame(parent, bg='#f8f9fa', relief='sunken', bd=1)
                targets_frame.pack(fill='x', pady=(0, 5))

                for i, (target_code, target_title) in enumerate(targets):
                    target_frame = tk.Frame(targets_frame, bg='#f8f9fa')
                    target_frame.pack(fill='x', padx=5, pady=2)

                    target_text = f"{i+1}. {target_title}"
                    target_label = tk.Label(target_frame, text=target_text,
                                          font=('Segoe UI', 8), fg='#34495e', bg='#f8f9fa',
                                          wraplength=450, justify='left')
                    target_label.pack(anchor='w')

            # Göstergeler
            cursor.execute("""
                SELECT si.code, si.title_tr, st.code as target_code
                FROM sdg_indicators si
                JOIN sdg_targets st ON si.target_id = st.id
                WHERE st.goal_id = ? 
                ORDER BY si.code
            """, (goal_id,))
            indicators = cursor.fetchall()

            if indicators:
                # Göstergeler başlığı
                indicators_header = tk.Frame(parent, bg='#e8f5e8', relief='raised', bd=1)
                indicators_header.pack(fill='x', pady=(0, 5))

                indicators_title = tk.Label(indicators_header, text=self.lm.tr("sdg_indicators_title", "Gostergeler"),
                                          font=('Segoe UI', 9, 'bold'), fg='#2c3e50', bg='#e8f5e8')
                indicators_title.pack(side='left', padx=5, pady=3)

                # Göstergeler listesi
                indicators_frame = tk.Frame(parent, bg='#f8f9fa', relief='sunken', bd=1)
                indicators_frame.pack(fill='x', pady=(0, 5))

                for i, (indicator_code, indicator_title, target_code) in enumerate(indicators):
                    indicator_frame = tk.Frame(indicators_frame, bg='#f8f9fa')
                    indicator_frame.pack(fill='x', padx=5, pady=2)

                    indicator_text = f"{i+1}. {indicator_title}"
                    indicator_label = tk.Label(indicator_frame, text=indicator_text,
                                             font=('Segoe UI', 8), fg='#34495e', bg='#f8f9fa',
                                             wraplength=450, justify='left')
                    indicator_label.pack(anchor='w')

            # GRI eşleştirmeleri
            try:
                try:
                    from mapping.sdg_gri_mapping import SDGGRIMapping
                except ImportError:
                    # Modül yolu çakışması durumunda manuel import
                    import importlib.util
                    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                    mapping_path = os.path.join(project_root, 'mapping', 'sdg_gri_mapping.py')
                    if os.path.exists(mapping_path):
                        spec = importlib.util.spec_from_file_location("sdg_gri_mapping_manual", mapping_path)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        SDGGRIMapping = mod.SDGGRIMapping
                    else:
                        raise ImportError("Mapping file not found")

                mapping = SDGGRIMapping()
                gri_mapping = mapping.get_gri_mapping_for_goals([goal_id])

                if goal_id in gri_mapping and gri_mapping[goal_id]['gri_standards']:
                    # GRI başlığı
                    gri_header = tk.Frame(parent, bg='#fff3cd', relief='raised', bd=1)
                    gri_header.pack(fill='x', pady=(0, 5))

                    gri_title = tk.Label(gri_header, text=self.lm.tr("sdg_gri_mapping_title", " GRI Eşleştirmeleri"),
                                       font=('Segoe UI', 9, 'bold'), fg='#2c3e50', bg='#fff3cd')
                    gri_title.pack(side='left', padx=5, pady=3)

                    # GRI listesi
                    gri_frame = tk.Frame(parent, bg='#f8f9fa', relief='sunken', bd=1)
                    gri_frame.pack(fill='x', pady=(0, 5))

                    for i, gri_standard in enumerate(gri_mapping[goal_id]['gri_standards']):
                        gri_item_frame = tk.Frame(gri_frame, bg='#f8f9fa')
                        gri_item_frame.pack(fill='x', padx=5, pady=2)

                        gri_text = f"{i+1}. {gri_standard}"
                        gri_item_label = tk.Label(gri_item_frame, text=gri_text,
                                                font=('Segoe UI', 8), fg='#34495e', bg='#f8f9fa',
                                                wraplength=450, justify='left')
                        gri_item_label.pack(anchor='w')
            except Exception as e:
                # print(f"{self.lm.tr('gri_mapping_error', 'GRI eşleştirmeleri alınırken hata')}: {e}")
                logging.error(f"Silent error caught: {str(e)}")

            conn.close()

        except Exception as e:
            logging.error(f"{self.lm.tr('sdg_details_load_error_log', 'Hedef detayları alınırken hata')}: {e}")
            error_label = tk.Label(parent, text=self.lm.tr("sdg_details_load_error", "Detaylar yüklenemedi"),
                                 font=('Segoe UI', 8), fg='#e74c3c', bg='#f8f9fa')
            error_label.pack(anchor='w', padx=10)

    def open_data_collection(self) -> None:
        """Veri toplama sistemini aç"""
        try:
            from modules.data_collection.data_collection_gui import DataCollectionGUI

            # Mevcut içeriği temizle
            for widget in self.parent.winfo_children():
                widget.destroy()

            # Veri toplama GUI'sini aç
            DataCollectionGUI(self.parent, self.company_id)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('data_collection_open_error', 'Veri toplama sistemi açılırken hata oluştu')}: {str(e)}")

    def open_progress_tracking(self) -> None:
        """İlerleme takibi sistemini aç"""
        try:
            from .sdg_progress_gui import SDGProgressGUI

            # Mevcut içeriği temizle
            for widget in self.parent.winfo_children():
                widget.destroy()

            # İlerleme takibi GUI'sini aç
            SDGProgressGUI(self.parent, self.company_id)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('progress_tracking_open_error', 'İlerleme takibi sistemi açılırken hata oluştu')}: {str(e)}")

    def open_advanced_progress(self) -> None:
        """Gelişmiş ilerleme takibi sistemini aç"""
        try:
            from .sdg_advanced_progress_gui import SDGAdvancedProgressGUI

            # Mevcut içeriği temizle
            for widget in self.parent.winfo_children():
                widget.destroy()

            # Gelişmiş ilerleme takibi GUI'sini aç
            SDGAdvancedProgressGUI(self.parent, self.company_id)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('advanced_progress_open_error', 'Gelişmiş ilerleme takibi sistemi açılırken hata oluştu')}: {str(e)}")

    def open_question_bank(self) -> None:
        """Soru bankası sistemini aç"""
        try:
            from .sdg_question_bank_gui import SDGQuestionBankGUI

            # Mevcut içeriği temizle
            for widget in self.parent.winfo_children():
                widget.destroy()

            # Soru bankası GUI'sini aç
            SDGQuestionBankGUI(self.parent, self.company_id)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('question_bank_open_error', 'Soru bankası sistemi açılırken hata oluştu')}: {str(e)}")

    def open_data_validation(self) -> None:
        """Veri doğrulama sistemini aç"""
        try:
            from .sdg_data_validation_gui import SDGDataValidationGUI

            # Mevcut içeriği temizle
            for widget in self.parent.winfo_children():
                widget.destroy()

            # Veri doğrulama GUI'sini aç
            SDGDataValidationGUI(self.parent, self.company_id)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('data_validation_open_error', 'Veri doğrulama sistemi açılırken hata oluştu')}: {str(e)}")

    def open_reporting(self) -> None:
        """Raporlama sistemini aç"""
        try:
            from .sdg_reporting_gui import SDGReportingGUI

            # Mevcut içeriği temizle
            for widget in self.parent.winfo_children():
                widget.destroy()

            # Raporlama GUI'sini aç
            SDGReportingGUI(self.parent, self.company_id)

        except Exception as e:
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('reporting_open_error', 'Raporlama sistemi açılırken hata oluştu')}: {str(e)}")

    def select_goal(self, goal) -> None:
        """Hedefi seç"""
        if goal not in self.selected_goals:
            self.selected_goals.append(goal)
            self.update_stats()
            self.display_available_goals()
            self.display_selected_goals()
            self.save_selections()  # Otomatik kaydet

    def deselect_goal(self, goal) -> None:
        """Hedefi seçimden çıkar"""
        if goal in self.selected_goals:
            self.selected_goals.remove(goal)
            self.update_stats()
            self.display_available_goals()
            self.display_selected_goals()
            self.save_selections()  # Otomatik kaydet

    # update_detail_content fonksiyonu kaldırıldı - detaylar artık seçilen SDG'lerin yanında gösteriliyor

    def load_saved_selections(self) -> None:
        """Kaydedilen seçimleri yükle"""
        try:
            # Veritabanından seçilen hedefleri al
            selected_goal_ids = self.sdg_manager.get_selected_goals(self.company_id)

            if selected_goal_ids:
                # Seçilen hedefleri selected_goals listesine ekle
                for goal in self.available_goals:
                    if goal[0] in selected_goal_ids:  # goal[0] = id
                        if goal not in self.selected_goals:
                            self.selected_goals.append(goal)

                # UI'yi güncelle
                self.update_stats()
                self.display_available_goals()
                self.display_selected_goals()
                # update_detail_content fonksiyonu kaldırıldı

                logging.info(f"{self.lm.tr('saved_goals_loaded', 'Kaydedilen SDG hedefi yüklendi')}: {len(selected_goal_ids)}")
        except Exception as e:
            logging.error(f"{self.lm.tr('saved_goals_load_error', 'Kaydedilen seçimler yüklenirken hata')}: {e}")

    def save_selections(self) -> None:
        """Seçimleri kaydet ve otomatik görevler oluştur"""
        try:
            selected_goal_ids = [goal[0] for goal in self.selected_goals]  # goal[0] = id
            success = self.sdg_manager.save_selected_goals(self.company_id, selected_goal_ids)

            if success:
                logging.info(f"{len(selected_goal_ids)} {self.lm.tr('sdg_goals_saved_count', 'SDG hedefi kaydedildi')}")

                # Otomatik görev oluşturma (eğer TaskManager yüklüyse)
                if TaskManagerClass is not None and NotificationManagerClass is not None:
                    try:
                        # SDG hedef numaralarını al (1-17 arası)
                        selected_goal_numbers = []
                        for goal in self.selected_goals:
                            # goal[1] = code (örn: "1", "7", "13")
                            try:
                                goal_num = int(goal[1])
                                selected_goal_numbers.append(goal_num)
                            except Exception as e:
                                logging.error(f"Silent error caught: {str(e)}")

                        if selected_goal_numbers:
                            # TaskManager ile görevler oluştur
                            task_manager = TaskManagerClass()
                            notification_manager = NotificationManagerClass()

                            # Admin ID'sini al (şimdilik 1)
                            admin_id = 1

                            # Otomatik görevler oluştur
                            created_task_ids = task_manager.auto_create_sdg_tasks(
                                selected_goals=selected_goal_numbers,
                                company_id=self.company_id,
                                admin_id=admin_id
                            )

                            # Her görev için bildirim gönder
                            if created_task_ids:
                                for task_id in created_task_ids:
                                    notification_manager.send_task_notification(
                                        task_id=task_id,
                                        notification_type='task_assigned'
                                    )

                                messagebox.showinfo(
                                    self.lm.tr("success", "Başarılı"),
                                    f"{self.lm.tr('sdg_goals_saved', 'SDG hedefleri kaydedildi!')}\n\n"
                                    f"{len(created_task_ids)} {self.lm.tr('tasks_created_and', 'adet görev oluşturuldu ve')}\n"
                                    f"{self.lm.tr('notifications_sent', 'ilgili departmanlara bildirim gönderildi.')}\n\n"
                                    + self.lm.tr('msg_track_tasks', "Görevleri 'Yönetim > Görev Dashboard' bölümünden takip edebilirsiniz.")
                                )
                            else:
                                messagebox.showinfo(
                                    self.lm.tr("info", "Bilgi"),
                                    f"{self.lm.tr('sdg_saved_no_tasks', 'SDG hedefleri kaydedildi ancak gorev olusturulamadi.')}\n"
                                    f"{self.lm.tr('check_departments', 'Lutfen departman atamalarini kontrol edin.')}"
                                )
                    except Exception as task_error:
                        logging.error(f"Otomatik görev oluşturma hatası: {task_error}")
                        messagebox.showwarning(
                            self.lm.tr("warning", "Uyari"),
                            f"{self.lm.tr('sdg_saved_task_error', 'SDG hedefleri kaydedildi ancak otomatik gorevler olusturulamadi.')}\n"
                            f"{self.lm.tr('error', 'Hata')}: {task_error}"
                        )
                else:
                    # TaskManager yüklü değil, sadece kaydet
                    messagebox.showinfo(self.lm.tr("success", "Basarili"), f"{len(selected_goal_ids)} {self.lm.tr('sdg_goals_saved_count', 'SDG hedefi kaydedildi')}")
            else:
                logging.info("SDG hedefleri kaydedilemedi")
                messagebox.showerror(self.lm.tr("error", "Hata"), self.lm.tr("sdg_save_error", "SDG hedefleri kaydedilemedi"))

        except Exception as e:
            logging.error(f"Seçimler kaydedilirken hata: {e}")
            messagebox.showerror(self.lm.tr("error", "Hata"), f"{self.lm.tr('sdg_save_exception', 'Seçimler kaydedilirken hata')}: {e}")

    def update_stats(self) -> None:
        """İstatistikleri güncelle"""
        # Toplam hedef sayısı veritabanındaki tüm hedeflerdir
        total_goals_overall = len(self.available_goals)
        selected_count = len(self.selected_goals)
        remaining_goals = max(total_goals_overall - selected_count, 0)

        # SDG istatistiklerini yöneticiden al (cevaplanan gösterge dahil)
        try:
            stats = self.sdg_manager.get_statistics(self.company_id)
            answered_count = stats.get('answered_indicators', 0)
            # Hedef seçim yüzdesini doğrudan mevcut seçimlerden hesapla
            selection_pct = (selected_count / total_goals_overall * 100) if total_goals_overall > 0 else 0
            # Yanıt yüzdesini yöneticiden al (gösterge bazlı)
            answer_pct = stats.get('answer_percentage', 0)
        except Exception as e:
            logging.error(f"İstatistikler getirilirken hata: {e}")
            answered_count = 0
            selection_pct = 0
            answer_pct = 0

        # Kartları güncelle
        self.stats_cards['total_goals'].config(text=str(remaining_goals))
        self.stats_cards['selected_goals'].config(text=str(selected_count))
        self.stats_cards['answered_indicators'].config(text=str(answered_count))
        if 'selection_percentage' in self.stats_cards:
            self.stats_cards['selection_percentage'].config(text=f"{selection_pct:.1f}%")
        if 'answer_percentage' in self.stats_cards:
            self.stats_cards['answer_percentage'].config(text=f"{answer_pct:.1f}%")

    def show_sdg_details_table(self) -> None:
        """SDG detay tablosunu göster"""
        # Tablo çerçevesi
        table_frame = tk.Frame(self.parent, bg='white')
        table_frame.pack(fill='both', expand=True, pady=20)

        # Başlık
        title_label = tk.Label(table_frame, text=self.lm.tr("sdg_details_table_title", "SDG Hedefleri Detay Tablosu"),
                              font=('Segoe UI', 14, 'bold'), fg='#2E8B57', bg='white')
        title_label.pack(pady=(0, 10))

        # Tablo
        col_keys = [
            ("col_sdg", "SDG"),
            ("col_goal", "Hedef"),
            ("col_indicator", "Gösterge"),
            ("col_gri", "GRI"),
            ("col_readiness", "Hazırlık"),
            ("col_answered", "Cevaplandı"),
            ("col_review", "İncelemede"),
            ("col_submitted", "Gönderildi")
        ]
        columns = [self.lm.tr(k, v) for k, v in col_keys]
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        # Sütun başlıkları
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        # Verileri yükle
        try:
            conn = self.sdg_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    g.code,
                    g.title_tr,
                    (
                        SELECT COUNT(i.id) 
                        FROM sdg_targets t 
                        JOIN sdg_indicators i ON i.target_id = t.id 
                        WHERE t.goal_id = g.id
                    ) AS indicator_count,
                    (
                        SELECT COUNT(DISTINCT mg.gri_disclosure)
                        FROM sdg_targets t 
                        JOIN sdg_indicators i ON i.target_id = t.id 
                        LEFT JOIN map_sdg_gri mg ON mg.sdg_indicator_code = i.code
                        WHERE t.goal_id = g.id AND mg.gri_disclosure IS NOT NULL AND TRIM(mg.gri_disclosure) <> ''
                    ) AS gri_total,
                    (
                        SELECT COUNT(*) FROM (
                            SELECT DISTINCT mg.gri_disclosure
                            FROM sdg_targets t 
                            JOIN sdg_indicators i ON i.target_id = t.id 
                            LEFT JOIN map_sdg_gri mg ON mg.sdg_indicator_code = i.code
                            WHERE t.goal_id = g.id AND LOWER(COALESCE(mg.relation_type,'')) = 'birebir'
                        ) AS x
                    ) AS birebir_count,
                    (
                        SELECT COUNT(*) FROM (
                            SELECT DISTINCT mg.gri_disclosure
                            FROM sdg_targets t 
                            JOIN sdg_indicators i ON i.target_id = t.id 
                            LEFT JOIN map_sdg_gri mg ON mg.sdg_indicator_code = i.code
                            WHERE t.goal_id = g.id AND LOWER(COALESCE(mg.relation_type,'')) = 'kısmi'
                        ) AS y
                    ) AS kismi_count,
                    COALESCE((
                        SELECT AVG(r.progress_pct) 
                        FROM responses r 
                        JOIN sdg_indicators i ON r.indicator_id = i.id 
                        JOIN sdg_targets t ON i.target_id = t.id 
                        WHERE t.goal_id = g.id
                    ), 0) AS readiness_score,
                    COALESCE((
                        SELECT ROUND(100.0 * COUNT(*) / NULLIF((
                            SELECT COUNT(*) FROM responses r2 
                            JOIN sdg_indicators i2 ON r2.indicator_id = i2.id 
                            JOIN sdg_targets t2 ON i2.target_id = t2.id 
                            WHERE t2.goal_id = g.id
                        ), 0))
                        FROM responses r 
                        JOIN sdg_indicators i ON r.indicator_id = i.id 
                        JOIN sdg_targets t ON i.target_id = t.id 
                        WHERE t.goal_id = g.id AND r.request_status = 'Cevaplandı'
                    ), 0) AS answered_pct,
                    COALESCE((
                        SELECT ROUND(100.0 * COUNT(*) / NULLIF((
                            SELECT COUNT(*) FROM responses r2 
                            JOIN sdg_indicators i2 ON r2.indicator_id = i2.id 
                            JOIN sdg_targets t2 ON i2.target_id = t2.id 
                            WHERE t2.goal_id = g.id
                        ), 0))
                        FROM responses r 
                        JOIN sdg_indicators i ON r.indicator_id = i.id 
                        JOIN sdg_targets t ON i.target_id = t.id 
                        WHERE t.goal_id = g.id AND r.request_status = 'İncelemede'
                    ), 0) AS review_pct,
                    COALESCE((
                        SELECT ROUND(100.0 * COUNT(*) / NULLIF((
                            SELECT COUNT(*) FROM responses r2 
                            JOIN sdg_indicators i2 ON r2.indicator_id = i2.id 
                            JOIN sdg_targets t2 ON i2.target_id = t2.id 
                            WHERE t2.goal_id = g.id
                        ), 0))
                        FROM responses r 
                        JOIN sdg_indicators i ON r.indicator_id = i.id 
                        JOIN sdg_targets t ON i.target_id = t.id 
                        WHERE t.goal_id = g.id AND r.request_status = 'Gönderildi'
                    ), 0) AS sent_pct
                FROM sdg_goals g
                JOIN user_sdg_selections us ON us.goal_id = g.id AND us.company_id = ?
                ORDER BY g.code
            """, (self.company_id,))

            rows = cursor.fetchall()
            if not rows:
                tree.insert('', 'end', values=("—", self.lm.tr("no_selected_sdg_goal", "Seçili SDG hedefi bulunamadı"), "—", "—", "—", "—", "—", "—"))
            for row in rows:
                gri_total = row[3] if row[3] is not None else 0
                birebir = row[4] if row[4] is not None else 0
                kismi = row[5] if row[5] is not None else 0
                gri_summary = f"{gri_total} {self.lm.tr('code', 'kod')} ({birebir} {self.lm.tr('exact', 'birebir')} / {kismi} {self.lm.tr('partial', 'kısmi')})" if gri_total else "—"

                tree.insert('', 'end', values=(
                    f"SDG {row[0]}",
                    row[1][:30] + "..." if len(row[1]) > 30 else row[1],
                    row[2],
                    gri_summary,
                    f"{row[6]:.1f}%",
                    f"{row[7]}%",
                    f"{row[8]}%",
                    f"{row[9]}%"
                ))

            conn.close()
        except Exception as e:
            logging.error(f"{self.lm.tr('table_load_error', 'Tablo yükleme hatası')}: {e}")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Yerleştir
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Detay modal açma: satıra çift tıklama
        def on_tree_double_click(event) -> None:
            try:
                item_id = tree.focus()
                if not item_id:
                    return
                values = tree.item(item_id, 'values')
                sdg_text = values[0] if values and len(values) > 0 else ''
                if not sdg_text.startswith('SDG'):
                    return
                goal_no = int(sdg_text.split()[-1])
                self.show_gri_details_for_goal(goal_no)
            except Exception as e:
                logging.error(f"{self.lm.tr('gri_detail_window_error', 'GRI detay penceresi açılırken hata')}: {e}")

        tree.bind('<Double-1>', on_tree_double_click)

    def show_gri_details_for_goal(self, goal_no: int) -> None:
        """Seçili SDG hedefi için GRI eşleştirme detaylarını modal pencerede göster"""
        try:
            conn = self.sdg_manager.get_connection()
            cursor = conn.cursor()

            # goal_id'yi al
            cursor.execute("SELECT id FROM sdg_goals WHERE code = ?", (goal_no,))
            res = cursor.fetchone()
            if not res:
                conn.close()
                return
            goal_id = res[0]

            # GRI detaylarını al
            cursor.execute("""
                SELECT mg.gri_disclosure, mg.gri_standard,
                       LOWER(COALESCE(mg.relation_type,'')) as relation_type,
                       COALESCE(mg.notes,'') as notes,
                       gi.title as disclosure_title
                FROM sdg_targets t 
                JOIN sdg_indicators i ON i.target_id = t.id 
                LEFT JOIN map_sdg_gri mg ON mg.sdg_indicator_code = i.code
                LEFT JOIN gri_indicators gi ON gi.code = mg.gri_disclosure
                WHERE t.goal_id = ? AND mg.gri_disclosure IS NOT NULL AND TRIM(mg.gri_disclosure) <> ''
                ORDER BY mg.gri_standard, mg.gri_disclosure
            """, (goal_id,))

            rows = cursor.fetchall()
            conn.close()

            # disclosure bazında tekilleştir
            details = {}
            for code, standard, relation, notes, title in rows:
                if not code:
                    continue
                if code not in details:
                    details[code] = {
                        'code': code,
                        'standard': standard or '',
                        'title': title or '',
                        'relation': relation or '',
                        'notes': notes or ''
                    }
                else:
                    # boş relation/notes varsa güncelle
                    if not details[code]['relation'] and relation:
                        details[code]['relation'] = relation
                    if not details[code]['notes'] and notes:
                        details[code]['notes'] = notes

            # Modal pencere
            win = tk.Toplevel(self.parent)
            win.title(f"SDG {goal_no} – {self.lm.tr('gri_mapping_detail', 'GRI Eşleştirme Detayı')}")
            win.geometry("700x400")
            win.configure(bg='white')

            hdr = tk.Label(win, text=f"SDG {goal_no} {self.lm.tr('for_gri_mappings', 'için GRI eşleştirmeleri')}", font=('Segoe UI', 12, 'bold'), bg='white', fg='#2c3e50')
            hdr.pack(pady=(10, 5))

            col_keys = [
                ("col_gri_code", "GRI Kodu"),
                ("col_title", "Başlık"),
                ("col_standard", "Standart"),
                ("col_relation", "İlişki"),
                ("col_notes", "Notlar")
            ]
            cols = [self.lm.tr(k, v) for k, v in col_keys]
            tv = ttk.Treeview(win, columns=cols, show='headings', height=12)
            for c in cols:
                tv.heading(c, text=c)
                tv.column(c, width=130 if c != self.lm.tr("col_notes", "Notlar") else 220, anchor='center')

            for d in details.values():
                rel = d['relation'] if d['relation'] else self.lm.tr("no_info", "bilgi yok")
                note = d['notes'] if d['notes'] else '—'
                tv.insert('', 'end', values=(d['code'], d['title'][:50] + ('...' if len(d['title'])>50 else ''), d['standard'], rel, note))

            sb = ttk.Scrollbar(win, orient='vertical', command=tv.yview)
            tv.configure(yscrollcommand=sb.set)
            tv.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            sb.pack(side='right', fill='y', pady=10)

        except Exception as e:
            logging.error(f"GRI detayları gösterilirken hata: {e}")

    # go_to_dashboard fonksiyonu kaldırıldı
