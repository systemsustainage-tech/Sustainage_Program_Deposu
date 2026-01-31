#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG 7 - Erişilebilir ve Temiz Enerji
Veri Giriş Formu
"""

import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import sqlite3
from tkinter import messagebox
from typing import Dict, List, Optional

from modules.data_collection.form_builder import FormBuilder, FormField
from utils.language_manager import LanguageManager
from config.database import DB_PATH


def get_sdg7_fields() -> List[FormField]:
    """SDG 7 için form alanları"""
    lm = LanguageManager()

    return [
        # Genel Bilgiler
        FormField(
            name='reporting_year',
            label=lm.tr('reporting_year', 'Raporlama Yılı'),
            field_type='dropdown',
            required=True,
            options=['2024', '2023', '2022', '2021', '2020'],
            default_value='2024',
            help_text=lm.tr('reporting_year_help', 'Verilerin ait olduğu yıl')
        ),

        FormField(
            name='reporting_period',
            label=lm.tr('reporting_period', 'Raporlama Dönemi'),
            field_type='dropdown',
            required=True,
            options=['Yıllık', 'Q1', 'Q2', 'Q3', 'Q4', 'Ocak-Haziran', 'Temmuz-Aralık'],
            default_value='Yıllık',
            help_text=lm.tr('reporting_period_help', 'Veri toplama dönemi')
        ),

        # ELEKTRİK TÜKETİMİ
        FormField(
            name='electricity_total',
            label=lm.tr('electricity_total', 'Toplam Elektrik Tüketimi'),
            field_type='number',
            required=True,
            unit='kWh',
            help_text=lm.tr('electricity_total_help', 'Yıllık toplam elektrik tüketimi (kilowatt-saat).\n\nVeri Kaynağı: Elektrik faturaları\nHesaplama: Tüm ay faturalarının toplamı'),
            placeholder=lm.tr('example_150000', 'Örn: 150000')
        ),

        FormField(
            name='electricity_renewable',
            label=lm.tr('electricity_renewable', 'Yenilenebilir Elektrik Tüketimi'),
            field_type='number',
            required=False,
            unit='kWh',
            help_text=lm.tr('electricity_renewable_help', 'Yenilenebilir kaynaklardan sağlanan elektrik (güneş, rüzgar, hidro).\n\nBu değer toplam elektriğe dahildir.'),
            placeholder=lm.tr('example_30000', 'Örn: 30000')
        ),

        # DOĞALGAZ TÜKETİMİ
        FormField(
            name='natural_gas_total',
            label=lm.tr('natural_gas_total', 'Doğalgaz Tüketimi'),
            field_type='number',
            required=False,
            unit='m³',
            help_text=lm.tr('natural_gas_total_help', 'Yıllık toplam doğalgaz tüketimi (metreküp).\n\nVeri Kaynağı: Doğalgaz faturaları'),
            placeholder=lm.tr('example_50000', 'Örn: 50000')
        ),

        # YAKIT TÜKETİMİ
        FormField(
            name='fuel_diesel',
            label=lm.tr('fuel_diesel', 'Dizel Yakıt Tüketimi'),
            field_type='number',
            required=False,
            unit=lm.tr('liter', 'litre'),
            help_text=lm.tr('fuel_diesel_help', 'Yıllık toplam dizel yakıt tüketimi.\n\nAraçlar, jeneratörler, vb. dahil'),
            placeholder=lm.tr('example_5000', 'Örn: 5000')
        ),

        FormField(
            name='fuel_gasoline',
            label=lm.tr('fuel_gasoline', 'Benzin Tüketimi'),
            field_type='number',
            required=False,
            unit=lm.tr('liter', 'litre'),
            help_text=lm.tr('fuel_gasoline_help', 'Yıllık toplam benzin tüketimi'),
            placeholder=lm.tr('example_3000', 'Örn: 3000')
        ),

        FormField(
            name='fuel_lpg',
            label=lm.tr('fuel_lpg', 'LPG Tüketimi'),
            field_type='number',
            required=False,
            unit=lm.tr('liter', 'litre'),
            help_text=lm.tr('fuel_lpg_help', 'Yıllık toplam LPG tüketimi'),
            placeholder=lm.tr('example_1000', 'Örn: 1000')
        ),

        # ENERJİ VERİMLİLİĞİ
        FormField(
            name='energy_intensity',
            label=lm.tr('energy_intensity', 'Enerji Yoğunluğu'),
            field_type='number',
            required=False,
            unit='kWh/ürün veya kWh/m²',
            help_text=lm.tr('energy_intensity_help', 'Ürün başına veya metrekare başına enerji tüketimi.\n\nHesaplama: Toplam enerji / Üretim miktarı veya alan'),
            placeholder='Örn: 12.5'
        ),

        FormField(
            name='energy_efficiency_projects',
            label=lm.tr('energy_efficiency_projects', 'Enerji Verimliliği Projeleri'),
            field_type='textarea',
            required=False,
            help_text=lm.tr('energy_efficiency_projects_help', 'Bu yıl yapılan enerji verimliliği projelerini listeleyin.\n\nÖrnek: LED aydınlatmaya geçiş, yalıtım iyileştirmesi, vb.'),
            placeholder=lm.tr('energy_efficiency_projects_placeholder', 'Örn: 1. Tüm aydınlatma LED\'e dönüştürüldü\n2. Kompresörler yenilendi\n3. Bina yalıtımı yapıldı')
        ),

        FormField(
            name='energy_savings',
            label=lm.tr('energy_savings', 'Enerji Tasarrufu'),
            field_type='number',
            required=False,
            unit='kWh',
            help_text=lm.tr('energy_savings_help', 'Enerji verimliliği projelerinden sağlanan toplam tasarruf'),
            placeholder=lm.tr('example_25000', 'Örn: 25000')
        ),

        # YENİLENEBİLİR ENERJİ YATIRIMLARI
        FormField(
            name='renewable_investments',
            label=lm.tr('renewable_investments', 'Yenilenebilir Enerji Yatırımları'),
            field_type='textarea',
            required=False,
            help_text=lm.tr('renewable_investments_help', 'Güneş paneli, rüzgar türbini gibi yenilenebilir enerji yatırımlarını açıklayın.'),
            placeholder=lm.tr('renewable_investments_placeholder', 'Örn: Çatıya 100 kWp güneş paneli kuruldu')
        ),

        FormField(
            name='renewable_capacity',
            label=lm.tr('renewable_capacity', 'Yenilenebilir Enerji Kurulu Gücü'),
            field_type='number',
            required=False,
            unit='kW',
            help_text=lm.tr('renewable_capacity_help', 'Toplam yenilenebilir enerji kurulu gücü (kilowatt)'),
            placeholder=lm.tr('example_100', 'Örn: 100')
        ),

        # HEDEFLER
        FormField(
            name='energy_reduction_target',
            label=lm.tr('energy_reduction_target', 'Enerji Azaltma Hedefi'),
            field_type='number',
            required=False,
            unit='%',
            help_text=lm.tr('energy_reduction_target_help', 'Gelecek yıl için enerji tüketimi azaltma hedefi (yüzde olarak)'),
            placeholder=lm.tr('example_10', 'Örn: 10')
        ),

        FormField(
            name='renewable_target',
            label=lm.tr('renewable_target', 'Yenilenebilir Enerji Hedefi'),
            field_type='number',
            required=False,
            unit='%',
            help_text=lm.tr('renewable_target_help', 'Gelecek yıl için toplam enerjide yenilenebilir enerji oranı hedefi'),
            placeholder=lm.tr('example_30', 'Örn: 30')
        ),

        # NOTLAR
        FormField(
            name='notes',
            label=lm.tr('notes', 'Ek Notlar ve Açıklamalar'),
            field_type='textarea',
            required=False,
            help_text=lm.tr('notes_help', 'Verilerle ilgili ek açıklamalar, özel durumlar, metodoloji değişiklikleri vb.'),
            placeholder=lm.tr('notes_placeholder', 'Buraya ek bilgiler girebilirsiniz...')
        ),
    ]


def save_sdg7_data(form_data: Dict, is_draft: bool, company_id: int, task_id: Optional[int] = None) -> bool:
    """
    SDG 7 verilerini veritabanına kaydet
    
    Args:
        form_data: Form verileri
        is_draft: Taslak mı?
        company_id: Firma ID
        task_id: İlgili görev ID (opsiyonel)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # sdg_data tablosuna kaydet (genel tablo)
        # Veya özel sdg7_energy_data tablosu oluşturabilirsiniz

        # Önce tablo var mı kontrol et, yoksa oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg7_energy_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                task_id INTEGER,
                reporting_year TEXT,
                reporting_period TEXT,
                electricity_total REAL,
                electricity_renewable REAL,
                natural_gas_total REAL,
                fuel_diesel REAL,
                fuel_gasoline REAL,
                fuel_lpg REAL,
                energy_intensity REAL,
                energy_efficiency_projects TEXT,
                energy_savings REAL,
                renewable_investments TEXT,
                renewable_capacity REAL,
                energy_reduction_target REAL,
                renewable_target REAL,
                notes TEXT,
                is_draft INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)

        # Veriyi ekle veya güncelle
        cursor.execute("""
            INSERT INTO sdg7_energy_data (
                company_id, task_id, reporting_year, reporting_period,
                electricity_total, electricity_renewable, natural_gas_total,
                fuel_diesel, fuel_gasoline, fuel_lpg,
                energy_intensity, energy_efficiency_projects, energy_savings,
                renewable_investments, renewable_capacity,
                energy_reduction_target, renewable_target,
                notes, is_draft
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company_id,
            task_id,
            form_data.get('reporting_year'),
            form_data.get('reporting_period'),
            form_data.get('electricity_total'),
            form_data.get('electricity_renewable'),
            form_data.get('natural_gas_total'),
            form_data.get('fuel_diesel'),
            form_data.get('fuel_gasoline'),
            form_data.get('fuel_lpg'),
            form_data.get('energy_intensity'),
            form_data.get('energy_efficiency_projects'),
            form_data.get('energy_savings'),
            form_data.get('renewable_investments'),
            form_data.get('renewable_capacity'),
            form_data.get('energy_reduction_target'),
            form_data.get('renewable_target'),
            form_data.get('notes'),
            1 if is_draft else 0
        ))

        conn.commit()

        # Görev ilerlemesini güncelle (task_id varsa)
        if task_id and not is_draft:
            cursor.execute("""
                UPDATE tasks 
                SET progress = 100,
                    status = 'Tamamlandı',
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (task_id,))
            conn.commit()

            logging.info(f"[OK] SDG 7 verisi kaydedildi ve görev #{task_id} tamamlandı")
        else:
            logging.info(f"[OK] SDG 7 verisi {'taslak olarak' if is_draft else ''} kaydedildi")

        return True

    except Exception as e:
        logging.error(f"[HATA] SDG 7 veri kaydetme hatası: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


# Test için
if __name__ == "__main__":
    import tkinter as tk

    root = tk.Tk()
    root.title("SDG 7 - Enerji Formu Test")
    root.geometry("800x600")

    fields = get_sdg7_fields()

    def on_save(data, is_draft) -> None:
        logging.info("\n=== FORM VERİLERİ ===")
        for key, value in data.items():
            logging.info(f"{key}: {value}")

        save_sdg7_data(data, is_draft, company_id=1)
        messagebox.showinfo("Başarılı", "Veriler kaydedildi!")

    FormBuilder(root, "SDG 7 - Enerji Tüketimi Verileri", fields, on_save)

    root.mainloop()

