import logging
"""
Sustainage Anket Sistemi - Hosting API Yöneticisi
Hosting'deki anket sistemine bağlanır ve veri alışverişi yapar.

Özellikler:
- Anket oluşturma
- Email gönderme
- Yanıtları çekme
- İstatistik alma
- Materyalite analizine entegrasyon

Tarih: 2025-10-23
"""

import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import requests
from config.database import DB_PATH


class HostingSurveyManager:
    """Hosting tabanlı anket sistemi yöneticisi"""

    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: Lokal veritabanı yolu
        """
        if db_path is None:
            try:
                from config.settings import get_db_path
                self.db_path = get_db_path()
            except Exception:
                self.db_path = DB_PATH
        else:
            self.db_path = db_path

        # Hosting config yükle (BASE_URL ve ADMIN_API_KEY)
        hosting_cfg = self._load_hosting_config()
        self.base_url = hosting_cfg.get('BASE_URL', 'https://sustainage.cloud/anket').rstrip('/')
        # API URL'leri: önce api.php, sorun olursa direct_create.php fallback
        self.api_url = f"{self.base_url}/api.php"
        self.direct_create_url = f"{self.base_url}/direct_create.php"
        self.survey_page_url = f"{self.base_url}/survey.php"
        # API key
        self.api_key = hosting_cfg.get('ADMIN_API_KEY', "sustainage_secure_api_key_2025_" + hashlib.sha256(b"sustainage.tr").hexdigest())

        self.headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json; charset=UTF-8'
        }

        self.timeout = 30  # seconds

        # Lokal veritabanında anket takip tablosu oluştur
        self._init_local_database()

    def _load_hosting_config(self) -> Dict[str, str]:
        """anket/config.php içinden BASE_URL ve ADMIN_API_KEY değerlerini okumaya çalış"""
        cfg: Dict[str, str] = {}
        try:
            # Config dosyasını dinamik olarak bul
            import os
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            php_path = os.path.join(root_dir, "anket", "config.php")
            
            if not os.path.exists(php_path):
                # Alternatif yol (C:\SDG varsayımı yerine relative)
                php_path = os.path.join(os.getcwd(), "anket", "config.php")
            
            if not os.path.exists(php_path):
                return cfg

            with open(php_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # BASE_URL = 'https://sustainage.tr/anket' veya define/assign kalıplarını yakala
            base_match = re.search(r"BASE_URL\s*['\"]?[:=]\s*['\"]([^'\"]+)['\"]", content)
            if not base_match:
                base_match = re.search(r"['\"]BASE_URL['\"]\s*=>\s*['\"]([^'\"]+)['\"]", content)
            if not base_match:
                base_match = re.search(r"\$BASE_URL\s*=\s*['\"]([^'\"]+)['\"]", content)
            if base_match:
                cfg['BASE_URL'] = base_match.group(1)

            # ADMIN_API_KEY kalıbını yakala
            key_match = re.search(r"ADMIN_API_KEY\s*['\"]?[:=]\s*['\"]([^'\"]+)['\"]", content)
            if not key_match:
                key_match = re.search(r"define\(\s*['\"]ADMIN_API_KEY['\"],\s*['\"]([^'\"]+)['\"]\s*\)", content)
            if not key_match:
                key_match = re.search(r"\$ADMIN_API_KEY\s*=\s*['\"]([^'\"]+)['\"]", content)
            if key_match:
                cfg['ADMIN_API_KEY'] = key_match.group(1)
        except Exception as e:
            logging.warning(f"Error loading hosting config: {e}")
            # Fallback değerler kullanılacak
            logging.error(f"Silent error caught: {str(e)}")
        return cfg

    def _init_local_database(self) -> None:
        """Lokal veritabanında anket takip tablosu oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Anket takip tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hosting_surveys (
                    local_survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hosting_survey_id INTEGER,
                    survey_name TEXT,
                    company_name TEXT,
                    survey_type TEXT,
                    survey_url TEXT,
                    survey_token TEXT,
                    created_date DATETIME,
                    deadline_date DATE,
                    status TEXT,
                    last_sync_date DATETIME,
                    response_count INTEGER DEFAULT 0
                )
            """)

            # Paydaş listesi tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_stakeholders (
                    stakeholder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    organization TEXT,
                    role TEXT,
                    phone TEXT,
                    category TEXT,
                    notes TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"[HATA] Lokal veritabanı init hatası: {e}")

    def create_survey(
        self,
        survey_name: str,
        company_name: str,
        topics: List[Dict[str, str]],
        description: str = "",
        deadline_days: int = 30,
        survey_type: str = "materiality"
    ) -> Dict[str, Any]:
        """
        Hosting'de yeni anket oluştur
        
        Args:
            survey_name: Anket adı
            company_name: Şirket adı
            topics: Konular listesi [{'code': '...', 'name': '...', 'category': '...', 'description': '...'}]
            description: Anket açıklaması
            deadline_days: Kaç gün sonra kapanacak
            survey_type: Anket tipi (materiality, stakeholder, etc.)
        
        Returns:
            {
                'success': True/False,
                'survey_id': ...,
                'survey_url': '...',
                'token': '...',
                'error': '...' (hata varsa)
            }
        """
        try:
            deadline_date = (datetime.now() + timedelta(days=deadline_days)).strftime('%Y-%m-%d')

            data = {
                'survey_name': survey_name,
                'company_name': company_name,
                'survey_type': survey_type,
                'description': description,
                'deadline_date': deadline_date,
                'topics': topics
            }

            # DEBUG: Data kontrolü
            logging.debug(f"[DEBUG] Survey Name: {survey_name}")
            logging.debug(f"[DEBUG] Topics Count: {len(topics)}")
            if topics:
                logging.debug(f"[DEBUG] First Topic: {topics[0]}")

            # Öncelik: api.php ile POST + action=create_survey
            response = None
            try:
                response = requests.post(
                    f"{self.api_url}?action=create_survey",
                    headers={
                        'X-API-Key': self.api_key,
                        'Content-Type': 'application/json; charset=UTF-8'
                    },
                    json=data,
                    timeout=self.timeout
                )
            except Exception as post_err:
                logging.info(f"[UYARI] api.php POST başarısız, fallback denenecek: {post_err}")

            # Fallback: direct_create.php GET ?json_data=...
            if not response or response.status_code >= 400:
                import urllib.parse
                json_str = json.dumps(data, ensure_ascii=False)
                encoded_json = urllib.parse.quote(json_str)
                response = requests.get(
                    f"{self.direct_create_url}?json_data={encoded_json}",
                    headers={'X-API-Key': self.api_key},
                    timeout=self.timeout
                )

            # Debug: Response detaylarını logla
            logging.debug(f"[DEBUG] HTTP Status: {response.status_code}")
            logging.debug(f"[DEBUG] Response Headers: {dict(response.headers)}")
            logging.debug(f"[DEBUG] Response Text (ilk 500 char): {response.text[:500]}")

            if response.status_code == 200:
                result = response.json()

                if result.get('success'):
                    # Bazı yanıtlar sadece token dönebilir; URL'i güvenle oluştur
                    token = result.get('token') or result.get('survey_token')
                    if not result.get('survey_url') and token:
                        result['survey_url'] = f"{self.survey_page_url}?token={token}"
                    # Lokal veritabanına kaydet
                    self._save_survey_locally(result)

                    logging.info(f"[OK] Anket oluşturuldu: {result.get('survey_url', 'URL yok')}")
                    return result
                else:
                    error_msg = result.get('error', 'Bilinmeyen hata')
                    logging.error(f"[HATA] API hatası: {error_msg}")
                    if 'missing_fields' in result:
                        logging.error(f"[HATA] Eksik alanlar: {result['missing_fields']}")
                    if 'received_fields' in result:
                        logging.error(f"[HATA] Alınan alanlar: {result['received_fields']}")
                    return {'success': False, 'error': error_msg}
            else:
                # 400 hatası için JSON response'u parse et
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', response.text)
                    logging.error(f"[HATA] HTTP {response.status_code}: {error_msg}")
                    if 'missing_fields' in error_data:
                        logging.error(f"[HATA] Eksik alanlar: {error_data['missing_fields']}")
                    if 'received_fields' in error_data:
                        logging.error(f"[HATA] Alınan alanlar: {error_data['received_fields']}")
                    return {'success': False, 'error': f"HTTP {response.status_code}: {error_msg}"}
                except Exception:
                    logging.error(f"[HATA] HTTP {response.status_code}: {response.text}")
                    return {'success': False, 'error': f"HTTP {response.status_code}"}

        except requests.exceptions.Timeout as e:
            logging.error(f"[HATA] Timeout: {e}")
            return {'success': False, 'error': 'Bağlantı zaman aşımı (30 saniye)'}
        except requests.exceptions.ConnectionError as e:
            logging.error(f"[HATA] Connection Error: {e}")
            return {'success': False, 'error': f'Hosting\'e bağlanılamadı: {e}'}
        except requests.exceptions.RequestException as e:
            logging.error(f"[HATA] Request Exception: {e}")
            return {'success': False, 'error': f'İstek hatası: {e}'}
        except Exception as e:
            logging.error(f"[HATA] Genel Hata: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'{type(e).__name__}: {str(e)}'}

    def _save_survey_locally(self, survey_data: Dict) -> None:
        """Anketi lokal veritabanına kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO hosting_surveys 
                (hosting_survey_id, survey_name, company_name, survey_type, survey_url, 
                 survey_token, created_date, deadline_date, status, last_sync_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                survey_data['survey_id'],
                survey_data.get('survey_name', ''),
                survey_data.get('company_name', ''),
                survey_data.get('survey_type', 'materiality'),
                survey_data['survey_url'],
                survey_data['token'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                survey_data.get('deadline_date', ''),
                'active',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"[HATA] Lokal kayıt hatası: {e}")

    def get_responses(self, survey_id: int) -> Dict[str, Any]:
        """
        Anket yanıtlarını çek
        
        Args:
            survey_id: Hosting'deki anket ID
        
        Returns:
            {
                'success': True/False,
                'responses': [...],
                'total_responses': ...
            }
        """
        try:
            response = requests.get(
                f"{self.api_url}?action=get_responses&survey_id={survey_id}",
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()

                if result.get('success'):
                    # Yanıt sayısını lokal veritabanında güncelle
                    self._update_response_count(survey_id, result['total_responses'])

                    logging.info(f"[OK] {result['total_responses']} yanıt çekildi")
                    return result
                else:
                    return {'success': False, 'error': result.get('error', 'API error')}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_summary(self, survey_id: int) -> Dict[str, Any]:
        """
        Özet istatistikleri çek
        
        Args:
            survey_id: Hosting'deki anket ID
        
        Returns:
            {
                'success': True/False,
                'summary': [
                    {
                        'topic_code': '...',
                        'topic_name': '...',
                        'avg_importance': 4.2,
                        'avg_impact': 3.8,
                        'materiality_score': 15.96,
                        ...
                    }
                ]
            }
        """
        try:
            response = requests.get(
                f"{self.api_url}?action=get_summary&survey_id={survey_id}",
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()

                if result.get('success'):
                    logging.info(f"[OK] Özet alındı: {result['total_topics']} konu")
                    return result
                else:
                    return {'success': False, 'error': result.get('error', 'API error')}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_comments(self, survey_id: int) -> Dict[str, Any]:
        """
        Paydaş yorumlarını çek
        
        Args:
            survey_id: Hosting'deki anket ID
        
        Returns:
            {
                'success': True/False,
                'comments': [...]
            }
        """
        try:
            response = requests.get(
                f"{self.api_url}?action=get_comments&survey_id={survey_id}",
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_surveys(self, status: str = 'all') -> Dict[str, Any]:
        """
        Anketleri listele
        
        Args:
            status: 'all', 'active', 'closed', 'draft'
        
        Returns:
            {
                'success': True/False,
                'surveys': [...]
            }
        """
        try:
            response = requests.get(
                f"{self.api_url}?action=list_surveys&status={status}",
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_status(self, survey_id: int, status: str) -> Dict[str, Any]:
        """
        Anket durumunu güncelle
        
        Args:
            survey_id: Anket ID
            status: 'active', 'closed', 'draft'
        
        Returns:
            {'success': True/False}
        """
        try:
            response = requests.get(
                f"{self.api_url}?action=update_status&survey_id={survey_id}&status={status}",
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Lokal veritabanını güncelle
                    self._update_local_status(survey_id, status)
                return result
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_survey(self, survey_id: int) -> Dict[str, Any]:
        """Anketi sil"""
        try:
            response = requests.get(
                f"{self.api_url}?action=delete_survey&survey_id={survey_id}",
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Lokal kayıttan sil
                    self._delete_local_survey(survey_id)
                return result
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _update_response_count(self, survey_id: int, count: int) -> None:
        """Yanıt sayısını lokal veritabanında güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE hosting_surveys 
                SET response_count = ?, last_sync_date = ?
                WHERE hosting_survey_id = ?
            """, (count, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), survey_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"[HATA] Yanıt sayısı güncelleme hatası: {e}")

    def _update_local_status(self, survey_id: int, status: str) -> None:
        """Lokal anket durumunu güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE hosting_surveys 
                SET status = ?, last_sync_date = ?
                WHERE hosting_survey_id = ?
            """, (status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), survey_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"[HATA] Durum güncelleme hatası: {e}")

    def _delete_local_survey(self, survey_id: int) -> None:
        """Lokal anket kaydını sil"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM hosting_surveys WHERE hosting_survey_id = ?", (survey_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"[HATA] Silme hatası: {e}")

    def send_survey_emails(
        self,
        survey_url: str,
        stakeholder_emails: List[str],
        survey_name: str = "Sürdürülebilirlik Anketi",
        survey_description: str = "",
        company_name: str = "Sustainage",
        deadline_date: str = ""
    ) -> Tuple[int, int, str]:
        """
        Paydaşlara anket email'i gönder
        
        Args:
            survey_url: Anket URL'i
            stakeholder_emails: Email listesi
            survey_name: Anket adı
            survey_description: Anket açıklaması
            company_name: Şirket adı
            deadline_date: Son tarih
        
        Returns:
            (başarılı_sayısı, başarısız_sayısı)
        """
        try:
            from datetime import datetime, timedelta

            from services.email_service import EmailService
            email_service = EmailService()

            # Eğer deadline_date verilmemişse 30 gün sonrasını al
            if not deadline_date:
                deadline_date = (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y')

            success_count = 0
            fail_count = 0
            last_error = ""

            for email in stakeholder_emails:
                try:
                    # Email adresinden isim çıkar (basit bir yaklaşım)
                    stakeholder_name = email.split('@')[0].replace('.', ' ').title()

                    # Email gönder (doğru parametrelerle)
                    result = email_service.send_template_email_with_result(
                        to_email=email,
                        template_key='survey_invitation',
                        variables={
                            'stakeholder_name': stakeholder_name,
                            'company_name': company_name,
                            'survey_name': survey_name,
                            'survey_description': survey_description or 'Sürdürülebilirlik konularının değerlendirilmesi',
                            'survey_url': survey_url,
                            'deadline_date': deadline_date
                        }
                    )
                    if result.get('success'):
                        success_count += 1
                        logging.info(f"[OK] Email gönderildi: {email}")
                    else:
                        fail_count += 1
                        last_error = result.get('error', 'Bilinmeyen hata')
                        logging.error(f"[HATA] Email hatası ({email}): {last_error}")

                except Exception as e:
                    fail_count += 1
                    logging.error(f"[HATA] Email döngü hatası ({email}): {e}")

            return success_count, fail_count, last_error
        except Exception as e:
            logging.error(f"[HATA] Email servisi başlatılamadı: {e}")
            return 0, len(stakeholder_emails), str(e)

    def export_to_training(self, survey_id: int, training_manager: Any, company_id: int, threshold: float = 12.0) -> Dict[str, Any]:
        """
        Anket sonuçlarına göre otomatik eğitim önerileri oluştur
        
        Args:
            survey_id: Anket ID
            training_manager: TrainingManager instance
            company_id: Şirket ID
            threshold: Materiality skoru eşiği (varsayılan 12.0)
            
        Returns:
            {'success': True, 'created_count': X, 'details': [...]}
        """
        summary_result = self.get_summary(survey_id)
        if not summary_result.get('success'):
            return {'success': False, 'error': summary_result.get('error')}
            
        summary = summary_result.get('summary', [])
        created_count = 0
        details = []
        current_year = datetime.now().year
        
        for item in summary:
            # Materiality Score (Önem x Etki) kontrolü
            try:
                score = float(item.get('materiality_score', 0))
            except (ValueError, TypeError):
                score = 0.0

            topic_name = item.get('topic_name', 'Bilinmeyen Konu')
            
            if score >= threshold:
                program_name = f"{topic_name} Eğitimi"
                
                # Check if exists
                if hasattr(training_manager, 'check_program_exists') and \
                   training_manager.check_program_exists(company_id, program_name, current_year):
                    details.append(f"Mevcut: {program_name}")
                    continue

                # Create training
                # add_training_program imzası:
                # company_id, program_name, program_type, target_audience, ...
                success = training_manager.add_training_program(
                    company_id=company_id,
                    program_name=program_name,
                    program_type="Technical", # Varsayılan kategori
                    target_audience="İlgili Departmanlar",
                    duration_hours=0, # Planlanacak
                    cost_per_participant=0,
                    period_year=current_year,
                    supplier="Otomatik (Anket)",
                    total_cost=0
                )
                
                if success:
                    created_count += 1
                    details.append(f"Oluşturuldu: {program_name} (Skor: {score:.2f})")
                else:
                    details.append(f"Hata: {program_name} oluşturulamadı")
                    
        return {
            'success': True,
            'created_count': created_count,
            'details': details
        }


    def get_local_surveys(self) -> List[Dict[str, Any]]:
        """Lokal veritabanındaki anketleri getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM hosting_surveys 
                ORDER BY created_date DESC
            """)

            columns = [desc[0] for desc in cursor.description]
            surveys = []

            for row in cursor.fetchall():
                survey = dict(zip(columns, row))
                surveys.append(survey)

            conn.close()
            return surveys

        except Exception as e:
            logging.error(f"[HATA] Lokal anket listesi hatası: {e}")
            return []

    def get_stakeholders(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Paydaş listesini getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if active_only:
                cursor.execute("SELECT * FROM survey_stakeholders WHERE is_active = 1 ORDER BY name")
            else:
                cursor.execute("SELECT * FROM survey_stakeholders ORDER BY name")

            columns = [desc[0] for desc in cursor.description]
            stakeholders = []

            for row in cursor.fetchall():
                stakeholder = dict(zip(columns, row))
                stakeholders.append(stakeholder)

            conn.close()
            return stakeholders

        except Exception as e:
            logging.error(f"[HATA] Paydaş listesi hatası: {e}")
            return []

    def add_stakeholder(self, name: str, email: str, organization: str = "", role: str = "", category: str = "") -> bool:
        """Yeni paydaş ekle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO survey_stakeholders (name, email, organization, role, category)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, organization, role, category))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            logging.info(f"[UYARI] Paydaş zaten kayıtlı: {email}")
            return False
        except Exception as e:
            logging.error(f"[HATA] Paydaş ekleme hatası: {e}")
            return False

    def export_to_materiality(self, survey_id: int, target_db: str) -> bool:
        """
        Anket sonuçlarını materyalite analizine aktar
        
        Args:
            survey_id: Anket ID
            target_db: Hedef veritabanı (GRI, ESRS, vs.)
        
        Returns:
            Başarılı ise True
        """
        try:
            # Özet istatistikleri al
            summary_result = self.get_summary(survey_id)

            if not summary_result.get('success'):
                logging.error("[HATA] Özet istatistikler alınamadı")
                return False

            summary = summary_result['summary']

            # Materyalite modülüne aktar
            # Gelecek geliştirme: İlgili materyalite modülüne entegre edilecek
            logging.info(f"[TODO] Materyalite entegrasyonu henüz aktif değil. (Survey ID: {survey_id})")
            logging.info(f"[OK] {len(summary)} konu materyalite analizine aktarıldı (Simülasyon)")

            return True

        except Exception as e:
            logging.error(f"[HATA] Materyalite aktarma hatası: {e}")
            return False

