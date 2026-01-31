# -*- coding: utf-8 -*-
"""
Sürdürülebilirlik Raporlama Yol Haritası Yöneticisi
(Reporting Journey Manager)

Bu modül, kullanıcının sürdürülebilirlik raporlama sürecindeki ilerlemesini takip eder.
13 adımlık bir akış üzerinden hangi adımların tamamlandığını, hangilerinin sırada olduğunu belirler.
"""

import logging
import sqlite3
import os
from typing import Dict, List, Any, Tuple
from config.database import DB_PATH

class ReportingJourneyManager:
    """Raporlama yolculuğu ve ilerleme takibi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Yolculuk ilerleme tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reporting_journey_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    step_number INTEGER NOT NULL,
                    step_code TEXT NOT NULL,
                    status TEXT DEFAULT 'pending', -- pending, active, completed
                    completed_at TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    UNIQUE(company_id, step_number)
                )
            """)
            conn.commit()
        except Exception as e:
            logging.error(f"Reporting Journey tables creation error: {e}")
        finally:
            conn.close()

    def get_journey_status(self, company_id: int) -> List[Dict[str, Any]]:
        """Şirketin 13 adımlık yolculuk durumunu döndürür"""
        
        steps = self._get_defined_steps()
        progress = self._get_stored_progress(company_id)
        
        # Her adımın gerçek durumunu kontrol et (Veritabanındaki verilere göre)
        real_status = self._check_real_status(company_id)
        
        journey = []
        active_found = False
        
        for i, step in enumerate(steps, 1):
            step_code = step['code']
            
            # 1. Veritabanındaki kayıtlı durum
            stored_state = progress.get(i, 'pending')
            
            # 2. Gerçek veri kontrolü (Auto-detection)
            is_really_completed = real_status.get(step_code, False)
            
            # Durum belirleme mantığı
            status = 'pending'
            if is_really_completed:
                status = 'completed'
            elif stored_state == 'completed':
                status = 'completed' # Manuel olarak tamamlandıysa
            
            # İlk tamamlanmamış adım 'active' olur
            if status == 'pending' and not active_found:
                status = 'active'
                active_found = True
            elif status == 'pending' and active_found:
                status = 'pending' # Diğerleri beklemede
                
            # Eğer hepsi tamamlandıysa sonuncusu completed kalır
            
            journey.append({
                'number': i,
                'title': step['title'],
                'description': step['description'],
                'status': status,
                'code': step_code,
                'link': step['link'],
                'action_text': step['action_text']
            })
            
        # Eğer veritabanında güncel değilse güncelle
        self._sync_progress(company_id, journey)
            
        return journey

    def _get_defined_steps(self) -> List[Dict[str, str]]:
        """13 adımlık akış tanımı"""
        return [
            {
                'code': 'company_profile',
                'title': 'Firma Profilinizi Oluşturun',
                'description': 'Şirketinizin temel bilgilerini girin. Bu bilgiler rapor kapaklarında ve genel bölümde **otomatik** kullanılacaktır.',
                'link': '/company_edit',
                'action_text': 'Profili Düzenle'
            },
            {
                'code': 'internal_stakeholders',
                'title': 'İç Paydaşlarınızı Kaydedin',
                'description': 'Çalışanlar ve yönetim kurulunu tanımlayın. Anket gönderimleri için bu liste **otomatik** kullanılır.',
                'link': '/stakeholder',
                'action_text': 'Paydaş Ekle'
            },
            {
                'code': 'send_sdg_survey_internal',
                'title': 'SKA Hizalama Anketini Gönderin',
                'description': 'Sürdürülebilir Kalkınma Amaçları anketini tek tıkla **otomatik** olarak iç paydaşlarınıza e-posta ile gönderin.',
                'link': '/surveys',
                'action_text': 'Anketi Başlat'
            },
            {
                'code': 'complete_sdg_survey',
                'title': 'SKA Hizalama Anketini Tamamlayın',
                'description': 'Gelen yanıtlar **otomatik** analiz edilir. Siz sadece sonuçlara göre nihai hedefleri seçersiniz.',
                'link': '/sdg',
                'action_text': 'Sonuçları İncele'
            },
            {
                'code': 'external_stakeholders',
                'title': 'Dış Paydaş Kaydını Tamamlayın',
                'description': 'Müşteri ve tedarikçilerinizi ekleyin. Bu liste önceliklendirme analizinde **otomatik** kullanılır.',
                'link': '/stakeholder',
                'action_text': 'Dış Paydaş Ekle'
            },
            {
                'code': 'prepare_materiality',
                'title': 'Önceliklendirme Analizi Hazırlığı',
                'description': 'Sektörünüze uygun konuları seçerek **manuel** bir anket şablonu oluşturun veya hazır şablonu kullanın.',
                'link': '/analysis',
                'action_text': 'Analiz Hazırla'
            },
            {
                'code': 'send_materiality_survey',
                'title': 'Önceliklendirme Anketini Gönderin',
                'description': 'Hazırladığınız anketi sistem üzerinden **otomatik** olarak tüm paydaşlara iletin.',
                'link': '/surveys?mode=materiality',
                'action_text': 'Anketi Gönder'
            },
            {
                'code': 'complete_materiality',
                'title': 'Önceliklendirme Analizini Tamamlayın',
                'description': 'Anket sonuçları ve matris **otomatik** oluşturulur. Kritik konuları onaylamanız yeterlidir.',
                'link': '/analysis',
                'action_text': 'Analizi Tamamla'
            },
            {
                'code': 'approve_charts',
                'title': 'Grafikleri İnceleyin ve Onaylayın',
                'description': 'Oluşan SKA ve Önceliklendirme grafikleri rapora **otomatik** eklenmeden önce son kez inceleyin.',
                'link': '/dashboard',
                'action_text': 'Dashboard\'a Git'
            },
            {
                'code': 'strategy_report',
                'title': 'Strateji Raporunu Oluşturun',
                'description': 'Vizyon, misyon ve stratejik hedeflerinizi **manuel** olarak metin formatında girin.',
                'link': '/reports',
                'action_text': 'Rapor Oluştur'
            },
            {
                'code': 'kpi_entry',
                'title': 'KPI ve Metrik Girişleri',
                'description': 'Karbon, Su, Atık verilerini girin. Hesaplamalar ve tablolar rapora **otomatik** yansır.',
                'link': '/data',
                'action_text': 'Veri Gir'
            },
            {
                'code': 'ai_insights',
                'title': 'AI İçerik Zenginleştirme',
                'description': 'Sustainfinity AI, verilerinizi analiz ederek rapora **otomatik** yorum ve iyileştirme önerileri ekler.',
                'link': '/ai_reports',
                'action_text': 'AI Asistanı Aç'
            },
            {
                'code': 'final_report',
                'title': 'Final Raporu Oluşturun',
                'description': 'Tüm **manuel** ve **otomatik** içeriklerin birleşimiyle nihai raporunuzu PDF olarak indirin.',
                'link': '/reports/unified',
                'action_text': 'Raporu İndir'
            }
        ]

    def _get_stored_progress(self, company_id: int) -> Dict[int, str]:
        """DB'den kayıtlı ilerlemeyi çeker"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        progress = {}
        try:
            cursor.execute("SELECT step_number, status FROM reporting_journey_progress WHERE company_id = ?", (company_id,))
            rows = cursor.fetchall()
            for r in rows:
                progress[r[0]] = r[1]
        except Exception:
            pass
        finally:
            conn.close()
        return progress

    def _check_real_status(self, company_id: int) -> Dict[str, bool]:
        """Sistemdeki gerçek verilere bakarak adımların tamamlanıp tamamlanmadığını kontrol eder"""
        status = {}
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 1. Company Profile: company_info tablosunda temel alanlar dolu mu?
            # sirket_adi yerine name kullanıyoruz
            cursor.execute("SELECT name, sector FROM company_info WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            if row and row[0] and row[1]:
                status['company_profile'] = True
            else:
                # Fallback to companies table
                cursor.execute("SELECT name, sector FROM companies WHERE id = ?", (company_id,))
                row = cursor.fetchone()
                status['company_profile'] = bool(row and row[0] and row[1])
            
            # 2. Internal Stakeholders: 'users' tablosunda 1'den fazla kayıt var mı veya stakeholders tablosunda 'internal' var mı?
            # Basitçe users tablosunda admin harici user var mı diye bakalım veya stakeholders tablosuna bakalım
            # Stakeholders tablosu varsa oraya bakalım
            try:
                cursor.execute("SELECT COUNT(*) FROM stakeholders WHERE company_id = ? AND (stakeholder_type = 'internal' OR stakeholder_group = 'internal')", (company_id,))
                count = cursor.fetchone()[0]
                status['internal_stakeholders'] = count > 0
            except:
                status['internal_stakeholders'] = False # Tablo yoksa false

            # 3. Send SDG Survey (Simulasyon: Anket tablosunda kayıt var mı)
            # Şimdilik manuel geçiş varsayalım veya 'surveys' tablosu varsa bakalım
            status['send_sdg_survey_internal'] = False 
            
            # 4. Complete SDG Survey: user_sdg_selections tablosunda kayıt var mı?
            try:
                cursor.execute("SELECT COUNT(*) FROM user_sdg_selections WHERE company_id = ?", (company_id,))
                count = cursor.fetchone()[0]
                status['complete_sdg_survey'] = count > 0
            except:
                # Tablo yoksa veya hata olursa false
                status['complete_sdg_survey'] = False

            # 5. External Stakeholders
            try:
                cursor.execute("SELECT COUNT(*) FROM stakeholders WHERE company_id = ? AND (stakeholder_type = 'external' OR stakeholder_group = 'external')", (company_id,))
                count = cursor.fetchone()[0]
                status['external_stakeholders'] = count > 0
            except:
                status['external_stakeholders'] = False

            # 6-8 Materiality: materiality_matrix tablosu var mı?
            try:
                # 6. Prepare Materiality: materiality_topics tablosunda konu var mı?
                cursor.execute("SELECT COUNT(*) FROM materiality_topics WHERE company_id = ?", (company_id,))
                topic_count = cursor.fetchone()[0]
                status['prepare_materiality'] = topic_count > 0
                
                # 7. Send Materiality Survey: (Simulasyon - surveys tablosu)
                # Şimdilik topics varsa bu adım da aktif/tamamlanabilir kabul edelim
                status['send_materiality_survey'] = topic_count > 0

                # 8. Complete Materiality: materiality_matrix tablosunda veri var mı?
                cursor.execute("SELECT COUNT(*) FROM materiality_matrix WHERE company_id = ?", (company_id,))
                matrix_count = cursor.fetchone()[0]
                status['complete_materiality'] = matrix_count > 0
                
                # 9. Approve Charts: Matris varsa bu da tamamdır
                status['approve_charts'] = matrix_count > 0
            except:
                status['prepare_materiality'] = False
                status['complete_materiality'] = False
                status['approve_charts'] = False
            
            # 11. KPI Entry: emission_records tablosunda kayıt var mı?
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emission_records'")
                if cursor.fetchone():
                    cursor.execute("SELECT COUNT(*) FROM emission_records WHERE company_id = ?", (company_id,))
                    count = cursor.fetchone()[0]
                    status['kpi_entry'] = count > 0
                else:
                    status['kpi_entry'] = False
            except:
                status['kpi_entry'] = False

        except Exception as e:
            logging.error(f"Journey status check error: {e}")
        finally:
            conn.close()
            
        return status

    def _sync_progress(self, company_id: int, journey: List[Dict]) -> None:
        """Hesaplanan durumu DB'ye kaydeder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            for step in journey:
                cursor.execute("""
                    INSERT OR REPLACE INTO reporting_journey_progress 
                    (company_id, step_number, step_code, status, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (company_id, step['number'], step['code'], step['status']))
            conn.commit()
        except Exception as e:
            logging.error(f"Sync progress error: {e}")
        finally:
            conn.close()

    def mark_step_completed(self, company_id: int, step_number: int) -> bool:
        """Bir adımı manuel olarak tamamlandı işaretle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE reporting_journey_progress 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE company_id = ? AND step_number = ?
            """, (company_id, step_number))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Mark completed error: {e}")
            return False
        finally:
            conn.close()
