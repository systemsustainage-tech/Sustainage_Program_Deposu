#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adım Adım Wizard Sistemi
Kullanıcıyı adım adım yönlendiren wizard arayüzü
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, List, Optional

from utils.language_manager import LanguageManager
from config.icons import Icons


class WizardStep:
    """Tek bir wizard adımı"""

    def __init__(self, step_id: str, title_key: str, title_default: str, 
                 desc_key: str, desc_default: str,
                 content_builder: Callable,
                 validate_fn: Optional[Callable] = None,
                 on_next: Optional[Callable] = None):
        """
        Args:
            step_id: Adım ID
            title_key: Adım başlığı çeviri anahtarı
            title_default: Adım başlığı varsayılan metin
            desc_key: Adım açıklaması çeviri anahtarı
            desc_default: Adım açıklaması varsayılan metin
            content_builder: İçerik oluşturan fonksiyon (parent_frame) -> None
            validate_fn: Validasyon fonksiyonu () -> (bool, str)
            on_next: İleri butonuna tıklandığında çağrılacak fonksiyon
        """
        self.step_id = step_id
        self.title_key = title_key
        self.title_default = title_default
        self.desc_key = desc_key
        self.desc_default = desc_default
        self.content_builder = content_builder
        self.validate_fn = validate_fn
        self.on_next = on_next


class StepWizard:
    """Adım adım wizard arayüzü"""

    def __init__(self, parent, title: str, steps: List[WizardStep],
                 on_complete: Optional[Callable] = None,
                 width: int = 800, height: int = 600):
        """
        Args:
            parent: Ana pencere
            title: Wizard başlığı
            steps: Wizard adımları
            on_complete: Tamamlandığında çağrılacak fonksiyon
            width: Pencere genişliği
            height: Pencere yüksekliği
        """
        self.parent = parent
        self.title = title
        self.steps = steps
        self.on_complete = on_complete
        self.current_step_index = 0
        self.step_data = {}  # Adımlar arası veri paylaşımı
        self.lm = LanguageManager()

        # Pencere
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(f"{width}x{height}")
        self.window.transient(parent)
        self.window.grab_set()

        self.setup_gui()
        self.show_step(0)

    def setup_gui(self) -> None:
        """GUI bileşenlerini oluştur"""
        # Üst kısım: Başlık ve ilerleme
        header_frame = tk.Frame(self.window, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        self.title_label = tk.Label(
            header_frame,
            text="",
            font=('Segoe UI', 16, 'bold'),
            bg='#34495e',
            fg='white'
        )
        self.title_label.pack(pady=10, padx=20, anchor='w')

        self.description_label = tk.Label(
            header_frame,
            text="",
            font=('Segoe UI', 10),
            bg='#34495e',
            fg='#ecf0f1',
            wraplength=700,
            justify=tk.LEFT
        )
        self.description_label.pack(padx=20, anchor='w')

        # İlerleme çubuğu
        progress_frame = tk.Frame(self.window, bg='#ecf0f1', height=60)
        progress_frame.pack(fill=tk.X)
        progress_frame.pack_propagate(False)

        tk.Label(
            progress_frame,
            text=f"{self.lm.tr('step', 'Adım')} {self.current_step_index + 1} / {len(self.steps)}",
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#7f8c8d'
        ).pack(pady=(10, 5))

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            maximum=len(self.steps)
        )
        self.progress_bar.pack(fill=tk.X, padx=50, pady=(0, 10))

        # Orta kısım: İçerik alanı
        self.content_frame = tk.Frame(self.window, bg='white')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Alt kısım: Navigasyon butonları
        nav_frame = tk.Frame(self.window, bg='#ecf0f1', height=70)
        nav_frame.pack(fill=tk.X, side=tk.BOTTOM)
        nav_frame.pack_propagate(False)

        button_container = tk.Frame(nav_frame, bg='#ecf0f1')
        button_container.pack(expand=True)

        self.back_btn = tk.Button(
            button_container,
            text=f"{Icons.LEFT} {self.lm.tr('btn_back', 'Geri')}",
            command=self.go_back,
            bg='#95a5a6',
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            cursor='hand2',
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT, padx=10)

        self.next_btn = tk.Button(
            button_container,
            text=f"{self.lm.tr('btn_next', 'İleri')} ️",
            command=self.go_next,
            bg='#27ae60',
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            cursor='hand2',
            padx=20,
            pady=10
        )
        self.next_btn.pack(side=tk.LEFT, padx=10)

        self.cancel_btn = tk.Button(
            button_container,
            text=f" {self.lm.tr('btn_cancel', 'İptal')}",
            command=self.cancel,
            bg='#e74c3c',
            fg='white',
            font=('Segoe UI', 11),
            cursor='hand2',
            padx=20,
            pady=10
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=10)

    def show_step(self, index: int) -> None:
        """Adımı göster"""
        if index < 0 or index >= len(self.steps):
            return

        self.current_step_index = index
        step = self.steps[index]

        # Başlık ve açıklama
        self.title_label.config(text=f"{step.title}")
        self.description_label.config(text=step.description)

        # İlerleme
        self.progress_bar['value'] = index + 1

        # İçeriği temizle
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Yeni içeriği oluştur
        step.content_builder(self.content_frame, self.step_data)

        # Buton durumları
        self.back_btn.config(state=tk.NORMAL if index > 0 else tk.DISABLED)

        if index == len(self.steps) - 1:
            self.next_btn.config(text=f" {self.lm.tr('btn_finish', 'Tamamla')}")
        else:
            self.next_btn.config(text=f"{self.lm.tr('btn_next', 'İleri')} ️")

    def go_next(self) -> None:
        """İleri git"""
        step = self.steps[self.current_step_index]

        # Validasyon
        if step.validate_fn:
            is_valid, error_msg = step.validate_fn(self.step_data)
            if not is_valid:
                messagebox.showerror(self.lm.tr('error', "Hata"), error_msg, parent=self.window)
                return

        # On next callback
        if step.on_next:
            try:
                step.on_next(self.step_data)
            except Exception as e:
                messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('process_error', 'İşlem hatası')}: {e}", parent=self.window)
                return

        # Son adım mı?
        if self.current_step_index == len(self.steps) - 1:
            # Tamamla
            if self.on_complete:
                try:
                    self.on_complete(self.step_data)
                except Exception as e:
                    messagebox.showerror(self.lm.tr('error', "Hata"), f"{self.lm.tr('completion_error', 'Tamamlama hatası')}: {e}", parent=self.window)
                    return

            self.window.destroy()
        else:
            # Sonraki adım
            self.show_step(self.current_step_index + 1)

    def go_back(self) -> None:
        """Geri git"""
        if self.current_step_index > 0:
            self.show_step(self.current_step_index - 1)

    def cancel(self) -> None:
        """İptal et"""
        if messagebox.askyesno(self.lm.tr('confirmation', "Onay"), self.lm.tr('wizard_exit_confirm', "Wizard'dan çıkmak istediğinizden emin misiniz?"), parent=self.window):
            self.window.destroy()


# ============================================
# ÖRNEK WIZARD'LAR
# ============================================

def create_company_setup_wizard(parent, db_path: str, company_id: int) -> None:
    """Şirket kurulum wizard'ı"""
    lm = LanguageManager()

    def step1_content(frame, data) -> None:
        """Şirket Bilgileri"""
        tk.Label(frame, text=lm.tr('company_basic_info', "Şirket Temel Bilgileri"), font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w', pady=(0, 20))

        # Şirket Adı
        tk.Label(frame, text=f"{lm.tr('company_name', 'Şirket Adı')} *", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        company_name_entry = tk.Entry(frame, font=('Segoe UI', 11), width=60)
        company_name_entry.pack(fill=tk.X, pady=(0, 15))
        company_name_entry.insert(0, data.get('company_name', ''))
        data['_company_name_widget'] = company_name_entry

        # Sektör
        tk.Label(frame, text=f"{lm.tr('sector', 'Sektör')} *", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        sector_var = tk.StringVar(value=data.get('sector', ''))
        sector_combo = ttk.Combobox(frame, textvariable=sector_var, width=57, state='readonly')
        
        # Localized sector list
        sectors = [
            lm.tr('sector_manufacturing', 'İmalat'),
            lm.tr('sector_service', 'Hizmet'),
            lm.tr('sector_energy', 'Enerji'),
            lm.tr('sector_technology', 'Teknoloji'),
            lm.tr('sector_finance', 'Finans'),
            lm.tr('sector_construction', 'İnşaat'),
            lm.tr('sector_other', 'Diğer')
        ]
        sector_combo['values'] = sectors
        sector_combo.pack(fill=tk.X, pady=(0, 15))
        data['_sector_widget'] = sector_combo

        # Çalışan Sayısı
        tk.Label(frame, text=f"{lm.tr('employee_count', 'Çalışan Sayısı')} *", font=('Segoe UI', 10, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        employee_entry = tk.Entry(frame, font=('Segoe UI', 11), width=20)
        employee_entry.pack(anchor='w', pady=(0, 15))
        employee_entry.insert(0, data.get('employee_count', ''))
        data['_employee_widget'] = employee_entry

    def step1_validate(data) -> None:
        # Verileri al
        data['company_name'] = data['_company_name_widget'].get().strip()
        data['sector'] = data['_sector_widget'].get()
        data['employee_count'] = data['_employee_widget'].get().strip()

        if not data['company_name']:
            return False, lm.tr('company_name_required', "Şirket adı gereklidir")
        if not data['sector']:
            return False, lm.tr('sector_required', "Sektör seçimi gereklidir")
        if not data['employee_count'].isdigit():
            return False, lm.tr('employee_count_invalid', "Geçerli bir çalışan sayısı girin")

        return True, ""

    def step2_content(frame, data) -> None:
        """Hedefler"""
        tk.Label(frame, text=lm.tr('sustainability_goals', "Sürdürülebilirlik Hedefleri"), font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w', pady=(0, 20))

        tk.Label(
            frame,
            text=lm.tr('goals_select_msg', "Hangi alanlarda hedefleriniz var? (Birden fazla seçebilirsiniz)"),
            font=('Segoe UI', 10),
            bg='white',
            wraplength=700,
            justify=tk.LEFT
        ).pack(anchor='w', pady=(0, 15))

        # Map internal IDs (Turkish) to translation keys
        goals_map = {
            'Karbon emisyonlarını azaltma': 'goal_carbon_reduction',
            'Enerji verimliliğini artırma': 'goal_energy_efficiency',
            'Su tüketimini azaltma': 'goal_water_reduction',
            'Atık geri dönüşümünü artırma': 'goal_waste_recycling',
            'İş sağlığı ve güvenliğini iyileştirme': 'goal_occupational_safety',
            'Çalışan memnuniyetini artırma': 'goal_employee_satisfaction',
            'Çeşitlilik ve kapsayıcılığı geliştirme': 'goal_diversity_inclusion',
            'Yerel tedarikçileri destekleme': 'goal_local_suppliers'
        }

        goal_vars = {}
        # Iterate over the map to preserve order if possible, or use a list of tuples if order matters.
        # Python 3.7+ preserves insertion order.
        
        # Original order
        goal_order = [
            'Karbon emisyonlarını azaltma',
            'Enerji verimliliğini artırma',
            'Su tüketimini azaltma',
            'Atık geri dönüşümünü artırma',
            'İş sağlığı ve güvenliğini iyileştirme',
            'Çalışan memnuniyetini artırma',
            'Çeşitlilik ve kapsayıcılığı geliştirme',
            'Yerel tedarikçileri destekleme'
        ]

        for goal_id in goal_order:
            tr_key = goals_map.get(goal_id, goal_id)
            translated_goal = lm.tr(tr_key, goal_id)
            
            var = tk.BooleanVar(value=goal_id in data.get('selected_goals', []))
            chk = tk.Checkbutton(frame, text=translated_goal, variable=var, font=('Segoe UI', 10), bg='white', activebackground='white')
            chk.pack(anchor='w', pady=3)
            goal_vars[goal_id] = var

        data['_goal_vars'] = goal_vars

    def step2_next(data) -> None:
        data['selected_goals'] = [goal for goal, var in data['_goal_vars'].items() if var.get()]

    def step3_content(frame, data) -> None:
        """Özet"""
        tk.Label(frame, text=lm.tr('setup_summary', "Kurulum Özeti"), font=('Segoe UI', 14, 'bold'), bg='white').pack(anchor='w', pady=(0, 20))

        summary_text = f"""
{lm.tr('company_name', 'Şirket Adı')}: {data.get('company_name', '-')}
{lm.tr('sector', 'Sektör')}: {data.get('sector', '-')}
{lm.tr('employee_count', 'Çalışan Sayısı')}: {data.get('employee_count', '-')}

{lm.tr('selected_goals', 'Seçilen Hedefler')} ({len(data.get('selected_goals', []))} {lm.tr('count_unit', 'adet')}):
""" + '\n'.join(f"  • {lm.tr(goal, goal)}" for goal in data.get('selected_goals', []))

        tk.Label(
            frame,
            text=summary_text,
            font=('Segoe UI', 10),
            bg='#ecf0f1',
            fg='#2c3e50',
            justify=tk.LEFT,
            padx=20,
            pady=20
        ).pack(fill=tk.BOTH, expand=True)

    def on_complete(data) -> None:
        # Veritabanına kaydet
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE companies 
            SET company_name = ?, sector = ?, employee_count = ?
            WHERE id = ?
        """, (data['company_name'], data['sector'], int(data['employee_count']), company_id))

        conn.commit()
        conn.close()

        messagebox.showinfo(lm.tr('success', "Başarılı"), lm.tr('company_info_saved', "Şirket bilgileri başarıyla kaydedildi!"))

    # Wizard adımları
    steps = [
        WizardStep(
            'company_info',
            'wizard_step_1_title', '1. Şirket Bilgileri',
            'wizard_step_1_desc', 'Temel şirket bilgilerinizi girin',
            step1_content,
            step1_validate
        ),
        WizardStep(
            'goals',
            'wizard_step_2_title', '2. Hedefler',
            'wizard_step_2_desc', 'Sürdürülebilirlik hedeflerinizi seçin',
            step2_content,
            on_next=step2_next
        ),
        WizardStep(
            'summary',
            'wizard_step_3_title', '3. Özet',
            'wizard_step_3_desc', 'Girdiğiniz bilgileri kontrol edin',
            step3_content
        )
    ]

    wizard = StepWizard(parent, lm.tr('company_setup_wizard', "Şirket Kurulum Wizard"), steps, on_complete, width=900, height=650)

    return wizard

