#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yardım Sistemi
Tooltip, contextual help, best practices
"""

import tkinter as tk

from utils.language_manager import LanguageManager


class HelpSystem:
    """Yardım sistemi yöneticisi"""

    def __init__(self):
        """Utility class, başlatılmasına gerek yok"""
        pass

    @staticmethod
    def _get_help_content(topic: str) -> dict:
        lm = LanguageManager()
        
        content = {
            'gri_indicators': {
                'title': lm.tr('help_gri_title', 'GRI Göstergeleri'),
                'content': lm.tr('help_gri_content', 'GRI (Global Reporting Initiative) standartları, sürdürülebilirlik raporlaması için en yaygın kullanılan çerçevedir.\n\nGösterge Tipleri:\n• GRI 2: Genel Açıklamalar\n• GRI 3: Önemli Konular\n• GRI 200: Ekonomik\n• GRI 300: Çevresel\n• GRI 400: Sosyal'),
                'best_practices': [
                    lm.tr('help_gri_bp1', 'Her gösterge için veri kaynağını belgeleyin'),
                    lm.tr('help_gri_bp2', 'Verileri düzenli aralıklarla güncelleyin'),
                    lm.tr('help_gri_bp3', 'Yıllık trendleri takip edin')
                ]
            },
            'carbon_calculator': {
                'title': lm.tr('help_carbon_title', 'Karbon Ayak İzi Hesaplama'),
                'content': lm.tr('help_carbon_content', 'Karbon ayak izi, organizasyonunuzun greenhouse gas (GHG) emisyonlarının toplamıdır.\n\nScope Tanımları:\n• Scope 1: Doğrudan emisyonlar (araçlar, ısıtma)\n• Scope 2: Dolaylı emisyonlar (satın alınan elektrik)\n• Scope 3: Diğer dolaylı emisyonlar (tedarik zinciri)'),
                'best_practices': [
                    lm.tr('help_carbon_bp1', 'Emission faktörlerini güncel tutun'),
                    lm.tr('help_carbon_bp2', 'Tüm scope\'ları dahil edin'),
                    lm.tr('help_carbon_bp3', 'Azaltma hedefleri belirleyin')
                ]
            },
            'materiality_analysis': {
                'title': lm.tr('help_materiality_title', 'Materialite Analizi'),
                'content': lm.tr('help_materiality_content', 'Materialite analizi, organizasyonunuz ve paydaşlarınız için en önemli sürdürülebilirlik konularını belirlemenize yardımcı olur.\n\nAdımlar:\n1. Konuları belirleyin\n2. Paydaş anketleri yapın\n3. İşletme etkisi değerlendirin\n4. Önceliklendirin'),
                'best_practices': [
                    lm.tr('help_materiality_bp1', 'Tüm paydaş gruplarını dahil edin'),
                    lm.tr('help_materiality_bp2', 'Düzenli olarak (yıllık) güncelleyin'),
                    lm.tr('help_materiality_bp3', 'Sonuçları raporlama stratejinize yansıtın')
                ]
            }
        }
        return content.get(topic)

    @staticmethod
    def show_tooltip(widget, text: str, delay: int = 500) -> None:
        """Widget üzerine tooltip ekle"""

        def on_enter(event) -> None:
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = tk.Label(
                tooltip,
                text=text,
                background="#ffffe0",
                relief=tk.SOLID,
                borderwidth=1,
                font=('Segoe UI', 9),
                wraplength=300,
                justify=tk.LEFT,
                padx=10,
                pady=5
            )
            label.pack()

            widget._tooltip = tooltip

        def on_leave(event) -> None:
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    @staticmethod
    def show_help_dialog(parent, topic: str) -> None:
        """Yardım dialogu göster"""
        help_data = HelpSystem._get_help_content(topic)

        if not help_data:
            return

        dialog = tk.Toplevel(parent)
        dialog.title("Yardım")
        dialog.geometry("600x500")
        dialog.transient(parent)
        dialog.grab_set()

        # Başlık
        title_frame = tk.Frame(dialog, bg='#3498db', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame,
            text=f" {help_data['title']}",
            font=('Segoe UI', 14, 'bold'),
            bg='#3498db',
            fg='white'
        ).pack(pady=15)

        # İçerik
        content_frame = tk.Frame(dialog, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Açıklama
        tk.Label(
            content_frame,
            text=help_data['content'],
            font=('Segoe UI', 10),
            bg='white',
            justify=tk.LEFT,
            wraplength=550
        ).pack(anchor='w', pady=(0, 20))

        # Best Practices
        if 'best_practices' in help_data:
            tk.Label(
                content_frame,
                text=" En İyi Uygulamalar:",
                font=('Segoe UI', 11, 'bold'),
                bg='white',
                fg='#27ae60'
            ).pack(anchor='w', pady=(10, 10))

            for practice in help_data['best_practices']:
                practice_frame = tk.Frame(content_frame, bg='white')
                practice_frame.pack(fill=tk.X, pady=3)

                tk.Label(
                    practice_frame,
                    text="",
                    font=('Segoe UI', 10, 'bold'),
                    bg='white',
                    fg='#27ae60'
                ).pack(side=tk.LEFT, padx=(10, 5))

                tk.Label(
                    practice_frame,
                    text=practice,
                    font=('Segoe UI', 10),
                    bg='white',
                    justify=tk.LEFT,
                    wraplength=500
                ).pack(side=tk.LEFT, anchor='w')

        # Kapat butonu
        tk.Button(
            dialog,
            text="Kapat",
            command=dialog.destroy,
            bg='#3498db',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            cursor='hand2',
            padx=30,
            pady=10
        ).pack(pady=(0, 20))

    @staticmethod
    def create_help_button(parent, topic: str, **kwargs) -> None:
        """Yardım butonu oluştur"""
        btn = tk.Button(
            parent,
            text="",
            command=lambda: HelpSystem.show_help_dialog(parent.winfo_toplevel(), topic),
            bg='#3498db',
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            cursor='hand2',
            relief=tk.RAISED,
            width=3,
            **kwargs
        )

        HelpSystem.show_tooltip(btn, "Yardım")

        return btn

