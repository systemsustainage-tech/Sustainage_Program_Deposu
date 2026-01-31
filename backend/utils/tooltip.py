import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tooltip Sistemi
Fare üzerine geldiğinde açıklama baloncukları göster
"""

import tkinter as tk
from typing import Dict, Optional


class ToolTip:
    """
    Basit ve kullanışlı tooltip sınıfı
    
    Kullanım:
        ToolTip(widget, "Bu bir açıklama baloncuğudur")
    """

    def __init__(self, widget, text: str, delay: int = 500, wraplength: int = 300) -> None:
        """
        Args:
            widget: Tooltip eklenecek widget
            text: Gösterilecek açıklama metni
            delay: Tooltip gösterim gecikmesi (ms)
            wraplength: Metin satır uzunluğu
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        self.tooltip_window = None
        self.schedule_id = None

        # Event binding
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Button>", self.on_leave)  # Tıklamada kapat

    def on_enter(self, event=None) -> None:
        """Fare widget üzerine geldiğinde"""
        self.schedule_show()

    def on_leave(self, event=None) -> None:
        """Fare widget'tan ayrıldığında"""
        self.cancel_schedule()
        self.hide()

    def schedule_show(self) -> None:
        """Tooltip gösterimini zamanla"""
        self.cancel_schedule()
        self.schedule_id = self.widget.after(self.delay, self.show)

    def cancel_schedule(self) -> None:
        """Zamanlanmış gösterimi iptal et"""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None

    def show(self) -> None:
        """Tooltip'i göster"""
        if self.tooltip_window:
            return

        # Widget'ın ekran koordinatlarını al
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Tooltip penceresi oluştur
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Pencere çerçevesi yok
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Tooltip içeriği
        frame = tk.Frame(self.tooltip_window, background="#ffffe0", relief='solid',
                        borderwidth=1, padx=5, pady=5)
        frame.pack()

        label = tk.Label(frame, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", foreground="#000000",
                        relief=tk.FLAT, font=('Segoe UI', 9),
                        wraplength=self.wraplength)
        label.pack()

    def hide(self) -> None:
        """Tooltip'i gizle"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class RichToolTip(ToolTip):
    """
    Gelişmiş tooltip - Çoklu satır, başlık ve renk desteği
    
    Kullanım:
        RichToolTip(widget, 
                   title="Başlık", 
                   text="Açıklama",
                   example="Örnek: ornek@sirket.com")
    """

    def __init__(self, widget, title: str = "", text: str = "",
                 example: str = "", delay: int = 500):
        self.widget = widget
        self.title = title
        self.description = text
        self.example = example
        self.delay = delay
        self.tooltip_window = None
        self.schedule_id = None

        # Event binding
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Button>", self.on_leave)

    def show(self) -> None:
        """Gelişmiş tooltip'i göster"""
        if self.tooltip_window:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Ana frame
        main_frame = tk.Frame(self.tooltip_window, background="white",
                             relief='solid', borderwidth=2, padx=10, pady=8)
        main_frame.pack()

        # Başlık (varsa)
        if self.title:
            title_label = tk.Label(main_frame, text=self.title,
                                  font=('Segoe UI', 10, 'bold'),
                                  background="white", foreground="#2E8B57")
            title_label.pack(anchor='w')

            # Ayırıcı çizgi
            separator = tk.Frame(main_frame, height=1, background="#e0e0e0")
            separator.pack(fill='x', pady=(3, 5))

        # Açıklama
        if self.description:
            desc_label = tk.Label(main_frame, text=self.description,
                                 font=('Segoe UI', 9), justify=tk.LEFT,
                                 background="white", foreground="#333333",
                                 wraplength=300)
            desc_label.pack(anchor='w')

        # Örnek (varsa)
        if self.example:
            example_frame = tk.Frame(main_frame, background="#f0f0f0",
                                    relief='solid', borderwidth=1)
            example_frame.pack(fill='x', pady=(5, 0))

            example_label = tk.Label(example_frame, text=self.example,
                                    font=('Courier', 8),
                                    background="#f0f0f0", foreground="#666666",
                                    padx=5, pady=3)
            example_label.pack()


def add_tooltip(widget, text: str, delay: int = 500) -> None:
    """
    Widget'a basit tooltip ekle
    
    Args:
        widget: Tooltip eklenecek widget
        text: Gösterilecek metin
        delay: Gösterim gecikmesi (ms)
    
    Returns:
        ToolTip instance
    """
    return ToolTip(widget, text, delay)


def add_rich_tooltip(widget, title: str = "", text: str = "", example: str = "", delay: int = 500) -> None:
    """
    Widget'a gelişmiş tooltip ekle
    
    Args:
        widget: Tooltip eklenecek widget
        title: Başlık
        text: Açıklama metni
        example: Örnek kullanım
        delay: Gösterim gecikmesi (ms)
    
    Returns:
        RichToolTip instance
    """
    return RichToolTip(widget, title, text, example, delay)


DEFAULT_HEADER_TIPS: Dict[str, str] = {
    # Ortak başlıklar
    'ID': 'Tekil kayıt kimliği.',
    'Kod': 'Standart/öğe kodu; tekil tanımlayıcı.',
    'Başlık': 'Kısa başlık; raporlama ve eşleştirmede referans.',
    'Kategori': 'Ana kategori; gruplama ve odak sağlar.',
    'Alt Kategori': 'Alt kırılım; metodoloji/politika/hedef ayrımı.',
    'Durum': 'İlerleme/durum bilgisi.',
    'Son Güncelleme': 'Son değişiklik tarihi/saat.',
    'Email': 'Elektronik posta adresi.',
    'Kullanıcı Adı': 'Sistemdeki kullanıcı adı.',
    'Kayıt Tarihi': 'Hesabın oluşturulma tarihi.',
    'Son Giriş': 'Kullanıcının son giriş zamanı.',
    'İlişki Türü': 'Eşleştirme ilişkisi türü.',
    'SDG Hedef': 'Sürdürülebilir Kalkınma Amacı.',
    'SDG Alt Hedef': 'SDG hedefinin alt kırılımı.',
    'Sirket Adi': 'Şirketin ticari unvanı.',
    'Tarih/Saat': 'Zaman damgası.',
    'Kullanıcı': 'İşlemi gerçekleştiren kullanıcı.',
    'İşlem': 'Gerçekleştirilen eylem.',
    'Kaynak': 'Etkilenen nesne/kaynak.',
    'Detaylar': 'İşlemle ilgili açıklama.'
}

def bind_treeview_header_tooltips(tree, tips: Optional[Dict[str, str]] = None) -> None:
    try:
        if tips is None:
            try:
                # Use item access or str conversion to avoid Tcl_Obj errors
                raw_cols = tree.cget('columns')
                if isinstance(raw_cols, (list, tuple)):
                    cols = list(raw_cols)
                else:
                    # Convert Tcl_Obj to string and split if necessary, or let list() try to handle it if iterable
                    # Safer to force string conversion first
                    cols = str(raw_cols).split() if raw_cols else []
            except Exception:
                cols = []
            tips = {h: DEFAULT_HEADER_TIPS.get(h, '') for h in cols}
        def _on_motion(event):
            region = tree.identify_region(event.x, event.y)
            if region != 'heading':
                try:
                    # Hide any existing tooltip on leave of header
                    if hasattr(tree, '_hover_tip') and tree._hover_tip:
                        tree._hover_tip.destroy()
                        tree._hover_tip = None
                    tree._last_tip_text = None
                except Exception as e:
                    # print(f"[Tooltip] Error clearing hover tip: {e}")
                    logging.error(f"Silent error caught: {str(e)}")
                return
            col_id = tree.identify_column(event.x)
            heading = ''
            try:
                heading = tree.heading(col_id).get('text', '')
            except Exception as e:
                # print(f"[Tooltip] Error getting heading text: {e}")
                heading = ''
            text = tips.get(heading)
            if not text:
                return
            if getattr(tree, '_last_tip_text', None) == text:
                return
            tree._last_tip_text = text
            # Show tooltip
            try:
                if hasattr(tree, '_hover_tip') and tree._hover_tip:
                    tree._hover_tip.destroy()
                tip = tk.Toplevel(tree)
                tip.wm_overrideredirect(True)
                tip.wm_geometry(f"+{event.x_root+12}+{event.y_root+12}")
                frame = tk.Frame(tip, background="#ffffe0", relief='solid', borderwidth=1)
                frame.pack()
                label = tk.Label(frame, text=text, background="#ffffe0", font=('Segoe UI', 9), justify='left', wraplength=300)
                label.pack(padx=8, pady=6)
                tree._hover_tip = tip
            except Exception as e:
                logging.error(f"[Tooltip] Error showing tooltip: {e}")
        def _on_leave(event):
            try:
                if hasattr(tree, '_hover_tip') and tree._hover_tip:
                    tree._hover_tip.destroy()
                    tree._hover_tip = None
                tree._last_tip_text = None
            except Exception as e:
                # print(f"[Tooltip] Error on leave: {e}")
                logging.error(f"Silent error caught: {str(e)}")
        tree.bind('<Motion>', _on_motion)
        tree.bind('<Leave>', _on_leave)
    except Exception as e:
        logging.error(f"[Tooltip] Error binding tooltips: {e}")


# Önceden tanımlı tooltip metinleri
TOOLTIP_TEXTS = {
    # Genel
    'btn_save': 'Değişiklikleri kaydet (Ctrl+S)',
    'cancel_button': 'İptal et ve kapat (Escape)',
    'delete_button': 'Seçili kaydı sil (Delete)',
    'refresh_button': 'Listeyi yenile (F5)',
    'search_field': 'Arama yapmak için yazın (Ctrl+F)',

    # SDG
    'sdg_goal_select': 'Bu SDG hedefini seçmek için tıklayın',
    'sdg_indicator': 'SDG gösterge detaylarını görüntüle',
    'sdg_progress': 'İlerleme yüzdesini gösterir (0-100%)',

    # GRI
    'gri_standard': 'GRI Standardı - Detaylar için tıklayın',
    'gri_disclosure': 'GRI Açıklama kodu - Yanıtlamak için tıklayın',
    'gri_category': 'GRI Kategori filtresi',

    # TSRS
    'tsrs_standard': 'TSRS Standardı - Türkiye uyumlu raporlama',
    'tsrs_indicator': 'TSRS Göstergesi - Veri girişi için tıklayın',

    # Firma Bilgileri
    'company_email': 'Şirket email adresi (örnek: info@sirket.com)',
    'company_phone': 'Telefon numarası (örnek: 0 (212) 555 12 34)',
    'company_tax_no': 'Vergi numarası (10 haneli)',
    'company_mersis': 'MERSİS numarası (16 haneli)',
    'company_website': 'Web sitesi (örnek: https://sirket.com)',

    # Mapping
    'mapping_sdg_gri': 'SDG ve GRI arasındaki eşleştirme',
    'mapping_relation': 'İlişki türü: Birebir, Kısmi, veya İlgili',

    # Raporlama
    'report_type': 'Rapor formatını seçin (PDF, DOCX, Excel)',
    'report_period': 'Raporlama dönemi (yıl veya çeyrek)',

    # Yönetim
    'user_role': 'Kullanıcı rolü (Admin, User, Viewer)',
    'user_permissions': 'Modül erişim izinleri',
    'backup_frequency': 'Yedekleme sıklığı (Günlük, Haftalık, Aylık)',

    # Karbon
    'carbon_scope1': 'Scope 1: Doğrudan sera gazı emisyonları',
    'carbon_scope2': 'Scope 2: Satın alınan enerji emisyonları',
    'carbon_scope3': 'Scope 3: Diğer dolaylı emisyonlar',
    'emission_factor': 'Emisyon faktörü (tCO2e/birim)',

    # Su Yönetimi
    'water_blue': 'Mavi su: Yüzey ve yeraltı suyu tüketimi',
    'water_green': 'Yeşil su: Yağmur suyu tüketimi',
    'water_grey': 'Gri su: Kirlilik nedeniyle kullanılamaz hale gelen su',
    'water_recycling': 'Su geri dönüşüm oranı (%)',
    'water_efficiency': 'Su kullanım verimliliği (0-1)',
}


def apply_tooltips_to_form(form_frame, field_tooltips: Dict[str, str]) -> None:
    """
    Form alanlarına toplu tooltip ekle
    
    Args:
        form_frame: Form frame'i
        field_tooltips: {field_name: tooltip_text} sözlüğü
    
    Example:
        tooltips = {
            'email': TOOLTIP_TEXTS['company_email'],
            'phone': TOOLTIP_TEXTS['company_phone']
        }
        apply_tooltips_to_form(form_frame, tooltips)
    """
    for field_name, tooltip_text in field_tooltips.items():
        # Form frame içindeki widget'ları bul
        for widget in form_frame.winfo_children():
            # Entry, Text, Combobox widget'larına tooltip ekle
            if isinstance(widget, (tk.Entry, tk.Text, tk.ttk.Combobox)):
                try:
                    add_tooltip(widget, tooltip_text)
                except Exception as e:
                    logging.error(f"Tooltip ekleme hatası ({field_name}): {e}")

