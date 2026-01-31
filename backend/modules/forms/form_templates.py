#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Form Şablonları Yöneticisi
GRI, TSRS, SDG göstergeleri için standart form şablonları
"""

import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class FormTemplateManager:
    """Form şablonlarını yöneten sınıf"""

    def __init__(self, db_path: str) -> None:
        """
        Args:
            db_path: Veritabanı yolu
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Veritabanı tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Form şablonları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS form_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                standard TEXT,
                schema_json TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Form yanıtları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS form_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id TEXT NOT NULL,
                company_id INTEGER NOT NULL,
                response_data TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT,
                created_by INTEGER,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        conn.commit()
        conn.close()

    def create_template(self, form_id: str, title: str, schema: Dict,
                       description: str = "", category: str = "",
                       standard: str = "") -> bool:
        """
        Yeni form şablonu oluştur
        
        Args:
            form_id: Benzersiz form ID
            title: Form başlığı
            schema: Form şeması (dict)
            description: Form açıklaması
            category: Kategori (GRI, TSRS, SDG vb.)
            standard: Standart kodu
        
        Returns:
            Başarılı ise True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO form_templates 
                (form_id, title, description, category, standard, schema_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                form_id,
                title,
                description,
                category,
                standard,
                json.dumps(schema, ensure_ascii=False),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Şablon oluşturma hatası: {e}")
            return False

    def get_template(self, form_id: str) -> Optional[Dict]:
        """
        Şablonu getir
        
        Args:
            form_id: Form ID
        
        Returns:
            Form şeması veya None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT schema_json, title, description 
                FROM form_templates 
                WHERE form_id = ?
            """, (form_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                schema = json.loads(result[0])
                schema['title'] = result[1]
                schema['description'] = result[2]
                schema['form_id'] = form_id
                return schema

            return None

        except Exception as e:
            logging.error(f"Şablon getirme hatası: {e}")
            return None

    def list_templates(self, category: Optional[str] = None) -> List[Dict]:
        """
        Şablonları listele
        
        Args:
            category: Kategori filtresi (opsiyonel)
        
        Returns:
            Şablon listesi
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if category:
                cursor.execute("""
                    SELECT form_id, title, description, category, standard, created_at
                    FROM form_templates
                    WHERE category = ?
                    ORDER BY category, standard
                """, (category,))
            else:
                cursor.execute("""
                    SELECT form_id, title, description, category, standard, created_at
                    FROM form_templates
                    ORDER BY category, standard
                """)

            templates = []
            for row in cursor.fetchall():
                templates.append({
                    'form_id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'category': row[3],
                    'standard': row[4],
                    'created_at': row[5]
                })

            conn.close()
            return templates

        except Exception as e:
            logging.error(f"Şablon listeleme hatası: {e}")
            return []

    def delete_template(self, form_id: str) -> bool:
        """
        Şablonu sil
        
        Args:
            form_id: Form ID
        
        Returns:
            Başarılı ise True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM form_templates WHERE form_id = ?", (form_id,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Şablon silme hatası: {e}")
            return False

    # ============================================
    # HAZIR ŞABLONLAR
    # ============================================

    def install_default_templates(self) -> None:
        """Varsayılan şablonları yükle"""
        # GRI Şablonları
        self._install_gri_templates()

        # TSRS Şablonları
        self._install_tsrs_templates()

        # SDG Şablonları
        self._install_sdg_templates()

        # Çevresel Şablonlar
        self._install_environmental_templates()

        # Sosyal Şablonlar
        self._install_social_templates()

        # Ekonomik Şablonlar
        self._install_economic_templates()

    def _install_gri_templates(self) -> None:
        """GRI standart şablonlarını yükle"""

        # GRI 2-1: Organizational Details
        self.create_template(
            form_id='gri_2_1',
            title='GRI 2-1: Organizasyon Detayları',
            description='Organizasyonun temel bilgileri',
            category='GRI',
            standard='GRI 2-1',
            schema={
                'fields': [
                    {
                        'name': 'org_name',
                        'type': 'text',
                        'label': 'Organizasyon Adı',
                        'required': True,
                        'help': 'Yasal organizasyon adı'
                    },
                    {
                        'name': 'org_location',
                        'type': 'text',
                        'label': 'Merkez Lokasyonu',
                        'required': True,
                        'help': 'Şirket merkezinin bulunduğu şehir ve ülke'
                    },
                    {
                        'name': 'ownership_nature',
                        'type': 'select',
                        'label': 'Mülkiyet Yapısı',
                        'required': True,
                        'options': ['Halka Açık', 'Özel Şirket', 'Kamu', 'Kooperatif', 'Ortaklık']
                    },
                    {
                        'name': 'countries_of_operation',
                        'type': 'textarea',
                        'label': 'Faaliyet Gösterilen Ülkeler',
                        'help': 'Şirketin faaliyet gösterdiği tüm ülkeleri listeleyin'
                    }
                ]
            }
        )

        # GRI 2-6: Activities, Workers and Governance
        self.create_template(
            form_id='gri_2_6',
            title='GRI 2-6: Faaliyetler, Çalışanlar ve Yönetişim',
            description='İş faaliyetleri ve çalışan bilgileri',
            category='GRI',
            standard='GRI 2-6',
            schema={
                'fields': [
                    {
                        'type': 'section',
                        'label': 'İş Faaliyetleri',
                        'description': 'Organizasyonun ana iş faaliyetleri'
                    },
                    {
                        'name': 'sector',
                        'type': 'select',
                        'label': 'Sektör',
                        'required': True,
                        'options': ['İmalat', 'Hizmet', 'Enerji', 'Teknoloji', 'Finans', 'Diğer']
                    },
                    {
                        'name': 'main_products',
                        'type': 'textarea',
                        'label': 'Ana Ürün ve Hizmetler',
                        'required': True,
                        'help': 'Şirketin sunduğu temel ürün ve hizmetleri listeleyin'
                    },
                    {
                        'type': 'section',
                        'label': 'Çalışan Bilgileri',
                        'description': 'İş gücü istatistikleri'
                    },
                    {
                        'name': 'total_employees',
                        'type': 'number',
                        'label': 'Toplam Çalışan Sayısı',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'permanent_employees',
                        'type': 'number',
                        'label': 'Sürekli Çalışan Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'temporary_employees',
                        'type': 'number',
                        'label': 'Geçici Çalışan Sayısı',
                        'validation': {'min': 0}
                    }
                ]
            }
        )

        # GRI 201-1: Economic Value Generated and Distributed
        self.create_template(
            form_id='gri_201_1',
            title='GRI 201-1: Ekonomik Değer Dağılımı',
            description='Yaratılan ve dağıtılan ekonomik değer',
            category='GRI',
            standard='GRI 201-1',
            schema={
                'fields': [
                    {
                        'type': 'section',
                        'label': 'Yaratılan Ekonomik Değer',
                    },
                    {
                        'name': 'revenues',
                        'type': 'decimal',
                        'label': 'Gelirler (TL)',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Dağıtılan Ekonomik Değer',
                    },
                    {
                        'name': 'operating_costs',
                        'type': 'decimal',
                        'label': 'İşletme Maliyetleri (TL)',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'employee_wages',
                        'type': 'decimal',
                        'label': 'Çalışan Ücretleri (TL)',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'payments_to_capital',
                        'type': 'decimal',
                        'label': 'Sermaye Sağlayıcılara Ödemeler (TL)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'payments_to_government',
                        'type': 'decimal',
                        'label': 'Hükümete Ödemeler (TL)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'community_investments',
                        'type': 'decimal',
                        'label': 'Toplum Yatırımları (TL)',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Hesaplama',
                    },
                    {
                        'name': 'retained_value',
                        'type': 'calculated',
                        'label': 'Elde Tutulan Ekonomik Değer',
                        'formula': '{revenues} - ({operating_costs} + {employee_wages} + {payments_to_capital} + {payments_to_government} + {community_investments})'
                    }
                ]
            }
        )

        # GRI 302-1: Energy Consumption
        self.create_template(
            form_id='gri_302_1',
            title='GRI 302-1: Enerji Tüketimi',
            description='Organizasyon içi enerji tüketimi',
            category='GRI',
            standard='GRI 302-1',
            schema={
                'fields': [
                    {
                        'type': 'section',
                        'label': 'Yenilenemeyen Enerji Tüketimi',
                    },
                    {
                        'name': 'fuel_consumption',
                        'type': 'decimal',
                        'label': 'Yakıt Tüketimi (GJ)',
                        'help': 'Doğalgaz, dizel, benzin vb. toplam tüketim',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'purchased_electricity',
                        'type': 'decimal',
                        'label': 'Satın Alınan Elektrik (GJ)',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Yenilenebilir Enerji Tüketimi',
                    },
                    {
                        'name': 'renewable_energy',
                        'type': 'decimal',
                        'label': 'Yenilenebilir Enerji (GJ)',
                        'help': 'Güneş, rüzgar, jeotermal vb.',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Toplam',
                    },
                    {
                        'name': 'total_energy',
                        'type': 'calculated',
                        'label': 'Toplam Enerji Tüketimi (GJ)',
                        'formula': '{fuel_consumption} + {purchased_electricity} + {renewable_energy}'
                    }
                ]
            }
        )

    def _install_tsrs_templates(self) -> None:
        """TSRS/ESRS şablonlarını yükle"""

        # ESRS E1: İklim Değişikliği
        self.create_template(
            form_id='esrs_e1_climate',
            title='ESRS E1: İklim Değişikliği',
            description='İklim değişikliği ile ilgili açıklamalar',
            category='TSRS',
            standard='ESRS E1',
            schema={
                'fields': [
                    {
                        'type': 'section',
                        'label': 'İklim Stratejisi',
                        'description': 'İklim değişikliği ile ilgili strateji ve hedefler'
                    },
                    {
                        'name': 'climate_strategy',
                        'type': 'textarea',
                        'label': 'İklim Stratejisi',
                        'required': True,
                        'help': 'İklim değişikliği ile mücadele stratejinizi açıklayın'
                    },
                    {
                        'name': 'climate_targets',
                        'type': 'textarea',
                        'label': 'İklim Hedefleri',
                        'required': True,
                        'help': 'Kısa, orta ve uzun vadeli iklim hedefleriniz'
                    },
                    {
                        'type': 'section',
                        'label': 'Sera Gazı Emisyonları',
                    },
                    {
                        'name': 'scope1_emissions',
                        'type': 'decimal',
                        'label': 'Scope 1 Emisyonları (tCO2e)',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'scope2_emissions',
                        'type': 'decimal',
                        'label': 'Scope 2 Emisyonları (tCO2e)',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'scope3_emissions',
                        'type': 'decimal',
                        'label': 'Scope 3 Emisyonları (tCO2e)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'total_emissions',
                        'type': 'calculated',
                        'label': 'Toplam Emisyonlar (tCO2e)',
                        'formula': '{scope1_emissions} + {scope2_emissions} + {scope3_emissions}'
                    }
                ]
            }
        )

        # ESRS S1: İş Gücü
        self.create_template(
            form_id='esrs_s1_workforce',
            title='ESRS S1: İş Gücü',
            description='Kendi iş gücü ile ilgili açıklamalar',
            category='TSRS',
            standard='ESRS S1',
            schema={
                'fields': [
                    {
                        'type': 'section',
                        'label': 'İş Gücü Profili',
                    },
                    {
                        'name': 'total_workforce',
                        'type': 'number',
                        'label': 'Toplam İş Gücü',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'female_employees',
                        'type': 'number',
                        'label': 'Kadın Çalışan Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'male_employees',
                        'type': 'number',
                        'label': 'Erkek Çalışan Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Çalışan Hakları ve Refahı',
                    },
                    {
                        'name': 'collective_agreement',
                        'type': 'checkbox',
                        'label': 'Toplu İş Sözleşmesi',
                        'checkbox_label': 'Çalışanlar toplu iş sözleşmesi kapsamında'
                    },
                    {
                        'name': 'training_hours',
                        'type': 'decimal',
                        'label': 'Ortalama Eğitim Saati / Çalışan',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'workplace_incidents',
                        'type': 'number',
                        'label': 'İş Kazası Sayısı',
                        'validation': {'min': 0}
                    }
                ]
            }
        )

    def _install_sdg_templates(self) -> None:
        """SDG gösterge şablonlarını yükle"""

        # SDG 7: Erişilebilir ve Temiz Enerji
        self.create_template(
            form_id='sdg_7_energy',
            title='SDG 7: Erişilebilir ve Temiz Enerji',
            description='Enerji erişimi ve yenilenebilir enerji göstergeleri',
            category='SDG',
            standard='SDG 7',
            schema={
                'fields': [
                    {
                        'name': 'renewable_energy_percentage',
                        'type': 'decimal',
                        'label': 'Yenilenebilir Enerji Oranı (%)',
                        'required': True,
                        'validation': {'min': 0, 'max': 100}
                    },
                    {
                        'name': 'energy_efficiency_improvement',
                        'type': 'decimal',
                        'label': 'Enerji Verimliliği İyileştirmesi (%)',
                        'help': 'Önceki yıla göre enerji verimliliği artışı',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'energy_investments',
                        'type': 'decimal',
                        'label': 'Enerji Yatırımları (TL)',
                        'help': 'Temiz enerji altyapısına yapılan yatırımlar',
                        'validation': {'min': 0}
                    }
                ]
            }
        )

        # SDG 13: İklim Eylemi
        self.create_template(
            form_id='sdg_13_climate',
            title='SDG 13: İklim Eylemi',
            description='İklim değişikliği ile mücadele göstergeleri',
            category='SDG',
            standard='SDG 13',
            schema={
                'fields': [
                    {
                        'name': 'climate_action_plan',
                        'type': 'checkbox',
                        'label': 'İklim Eylem Planı',
                        'checkbox_label': 'İklim eylem planımız mevcut'
                    },
                    {
                        'name': 'emission_reduction_target',
                        'type': 'decimal',
                        'label': 'Emisyon Azaltım Hedefi (%)',
                        'help': '2030 yılına kadar hedeflenen azaltım oranı',
                        'validation': {'min': 0, 'max': 100}
                    },
                    {
                        'name': 'carbon_offset',
                        'type': 'decimal',
                        'label': 'Karbon Dengeleme (tCO2e)',
                        'help': 'Yıllık karbon dengeleme miktarı',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'climate_adaptation_measures',
                        'type': 'textarea',
                        'label': 'İklim Adaptasyon Önlemleri',
                        'help': 'İklim değişikliğine adaptasyon için alınan önlemleri açıklayın'
                    }
                ]
            }
        )

    def _install_environmental_templates(self) -> None:
        """Çevresel veri toplama şablonları"""

        # Su Yönetimi
        self.create_template(
            form_id='env_water_management',
            title='Su Yönetimi',
            description='Su tüketimi ve yönetimi verileri',
            category='Çevre',
            standard='Su',
            schema={
                'fields': [
                    {
                        'type': 'section',
                        'label': 'Su Çekimi',
                    },
                    {
                        'name': 'surface_water',
                        'type': 'decimal',
                        'label': 'Yüzey Suyu (m³)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'groundwater',
                        'type': 'decimal',
                        'label': 'Yeraltı Suyu (m³)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'municipal_water',
                        'type': 'decimal',
                        'label': 'Şebeke Suyu (m³)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'total_withdrawal',
                        'type': 'calculated',
                        'label': 'Toplam Su Çekimi (m³)',
                        'formula': '{surface_water} + {groundwater} + {municipal_water}'
                    },
                    {
                        'type': 'section',
                        'label': 'Su Deşarjı',
                    },
                    {
                        'name': 'surface_discharge',
                        'type': 'decimal',
                        'label': 'Yüzey Suyuna Deşarj (m³)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'groundwater_discharge',
                        'type': 'decimal',
                        'label': 'Yeraltı Suyuna Deşarj (m³)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'municipal_discharge',
                        'type': 'decimal',
                        'label': 'Kanalizasyona Deşarj (m³)',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Su Geri Kazanımı',
                    },
                    {
                        'name': 'water_recycled',
                        'type': 'decimal',
                        'label': 'Geri Kazanılan Su (m³)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'water_reused',
                        'type': 'decimal',
                        'label': 'Yeniden Kullanılan Su (m³)',
                        'validation': {'min': 0}
                    }
                ]
            }
        )

        # Atık Yönetimi
        self.create_template(
            form_id='env_waste_management',
            title='Atık Yönetimi',
            description='Atık üretimi ve bertaraf verileri',
            category='Çevre',
            standard='Atık',
            schema={
                'fields': [
                    {
                        'type': 'section',
                        'label': 'Tehlikeli Atıklar',
                    },
                    {
                        'name': 'hazardous_waste_total',
                        'type': 'decimal',
                        'label': 'Toplam Tehlikeli Atık (ton)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'hazardous_waste_recycled',
                        'type': 'decimal',
                        'label': 'Geri Dönüştürülen (ton)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'hazardous_waste_incinerated',
                        'type': 'decimal',
                        'label': 'Yakılan (ton)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'hazardous_waste_landfilled',
                        'type': 'decimal',
                        'label': 'Düzenli Depolamaya Gönderilen (ton)',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Tehlikesiz Atıklar',
                    },
                    {
                        'name': 'nonhazardous_waste_total',
                        'type': 'decimal',
                        'label': 'Toplam Tehlikesiz Atık (ton)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'nonhazardous_waste_recycled',
                        'type': 'decimal',
                        'label': 'Geri Dönüştürülen (ton)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'nonhazardous_waste_composted',
                        'type': 'decimal',
                        'label': 'Kompostlanan (ton)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'nonhazardous_waste_landfilled',
                        'type': 'decimal',
                        'label': 'Düzenli Depolamaya Gönderilen (ton)',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Toplam',
                    },
                    {
                        'name': 'total_waste',
                        'type': 'calculated',
                        'label': 'Toplam Atık (ton)',
                        'formula': '{hazardous_waste_total} + {nonhazardous_waste_total}'
                    }
                ]
            }
        )

    def _install_social_templates(self) -> None:
        """Sosyal veri toplama şablonları"""

        # İSG (İş Sağlığı ve Güvenliği)
        self.create_template(
            form_id='social_ohs',
            title='İş Sağlığı ve Güvenliği',
            description='İSG performans göstergeleri',
            category='Sosyal',
            standard='İSG',
            schema={
                'fields': [
                    {
                        'type': 'section',
                        'label': 'İş Kazaları',
                    },
                    {
                        'name': 'recordable_injuries',
                        'type': 'number',
                        'label': 'Kaydedilebilir İş Kazası Sayısı',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'lost_time_injuries',
                        'type': 'number',
                        'label': 'İş Kaybına Yol Açan Kaza Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'fatalities',
                        'type': 'number',
                        'label': 'Ölümlü Kaza Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'lost_days',
                        'type': 'number',
                        'label': 'Kayıp Gün Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Çalışma Saatleri',
                    },
                    {
                        'name': 'total_hours_worked',
                        'type': 'number',
                        'label': 'Toplam Çalışılan Saat',
                        'required': True,
                        'help': 'Tüm çalışanların yıllık toplam çalışma saati',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Oranlar',
                        'description': 'Otomatik hesaplanan oranlar (milyon saate göre)'
                    },
                    {
                        'name': 'ltifr',
                        'type': 'calculated',
                        'label': 'LTIFR (Kayıp Zamanlı Kaza Oranı)',
                        'formula': '({lost_time_injuries} / {total_hours_worked}) * 1000000'
                    },
                    {
                        'name': 'trifr',
                        'type': 'calculated',
                        'label': 'TRIFR (Toplam Kaydedilebilir Kaza Oranı)',
                        'formula': '({recordable_injuries} / {total_hours_worked}) * 1000000'
                    }
                ]
            }
        )

        # Eğitim ve Gelişim
        self.create_template(
            form_id='social_training',
            title='Eğitim ve Gelişim',
            description='Çalışan eğitim metrikleri',
            category='Sosyal',
            standard='Eğitim',
            schema={
                'fields': [
                    {
                        'name': 'total_training_hours',
                        'type': 'decimal',
                        'label': 'Toplam Eğitim Saati',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'total_employees_trained',
                        'type': 'number',
                        'label': 'Eğitim Alan Çalışan Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'training_investment',
                        'type': 'decimal',
                        'label': 'Eğitim Yatırımı (TL)',
                        'help': 'Eğitim için yapılan toplam harcama',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'training_programs',
                        'type': 'table',
                        'label': 'Eğitim Programları',
                        'columns': ['Program Adı', 'Katılımcı Sayısı', 'Süre (saat)', 'Kategori']
                    },
                    {
                        'type': 'section',
                        'label': 'Eğitim Kategorileri',
                    },
                    {
                        'name': 'technical_training_hours',
                        'type': 'decimal',
                        'label': 'Teknik Eğitim (saat)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'leadership_training_hours',
                        'type': 'decimal',
                        'label': 'Liderlik Eğitimi (saat)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'compliance_training_hours',
                        'type': 'decimal',
                        'label': 'Uyum Eğitimi (saat)',
                        'validation': {'min': 0}
                    }
                ]
            }
        )

    def _install_economic_templates(self) -> None:
        """Ekonomik veri toplama şablonları"""

        # Tedarik Zinciri
        self.create_template(
            form_id='economic_supply_chain',
            title='Tedarik Zinciri Yönetimi',
            description='Tedarikçi değerlendirme ve yönetim',
            category='Ekonomik',
            standard='Tedarik',
            schema={
                'fields': [
                    {
                        'type': 'section',
                        'label': 'Tedarikçi Profili',
                    },
                    {
                        'name': 'total_suppliers',
                        'type': 'number',
                        'label': 'Toplam Tedarikçi Sayısı',
                        'required': True,
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'local_suppliers',
                        'type': 'number',
                        'label': 'Yerel Tedarikçi Sayısı',
                        'help': 'Aynı ülke içindeki tedarikçiler',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'certified_suppliers',
                        'type': 'number',
                        'label': 'Sertifikalı Tedarikçi Sayısı',
                        'help': 'ISO, çevre veya sosyal sertifikası olan tedarikçiler',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Tedarikçi Değerlendirme',
                    },
                    {
                        'name': 'suppliers_assessed',
                        'type': 'number',
                        'label': 'Değerlendirilen Tedarikçi Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'suppliers_audited',
                        'type': 'number',
                        'label': 'Denetlenen Tedarikçi Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'supplier_issues',
                        'type': 'number',
                        'label': 'Tespit Edilen Sorun Sayısı',
                        'help': 'Denetimler sonucu tespit edilen uygunsuzluklar',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'corrective_actions',
                        'type': 'number',
                        'label': 'Düzeltici Faaliyet Sayısı',
                        'validation': {'min': 0}
                    },
                    {
                        'type': 'section',
                        'label': 'Harcamalar',
                    },
                    {
                        'name': 'total_procurement',
                        'type': 'decimal',
                        'label': 'Toplam Satınalma (TL)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'local_procurement',
                        'type': 'decimal',
                        'label': 'Yerel Satınalma (TL)',
                        'validation': {'min': 0}
                    },
                    {
                        'name': 'local_procurement_ratio',
                        'type': 'calculated',
                        'label': 'Yerel Satınalma Oranı (%)',
                        'formula': '({local_procurement} / {total_procurement}) * 100'
                    }
                ]
            }
        )


# Kullanım örneği
if __name__ == "__main__":
    import os

    # Veritabanı yolu
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sdg_desktop.sqlite")

    # Template manager oluştur
    manager = FormTemplateManager(db_path)

    # Varsayılan şablonları yükle
    logging.info("Varsayılan şablonlar yükleniyor...")
    manager.install_default_templates()

    # Şablonları listele
    logging.info("\nYüklenen şablonlar:")
    for template in manager.list_templates():
        logging.info(f"  - [{template['category']}] {template['title']} ({template['standard']})")

    logging.info("\n Şablonlar başarıyla yüklendi!")

