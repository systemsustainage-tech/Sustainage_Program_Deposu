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
Refactored for Multi-tenancy: 2026-02-04
"""

import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple, Optional

import requests
from config.database import DB_PATH
from backend.core.base_manager import BaseTenantManager

class HostingSurveyManager(BaseTenantManager):
    """Hosting tabanlı anket sistemi yöneticisi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None):
        """
        Args:
            db_path: Lokal veritabanı yolu
            company_id: Şirket ID
        """
        final_db_path = db_path
        if final_db_path is None:
            try:
                from config.settings import get_db_path
                final_db_path = get_db_path()
            except Exception:
                final_db_path = DB_PATH
        
        super().__init__(final_db_path, company_id)

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
            # Anket takip tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS hosting_surveys (
                    local_survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER DEFAULT 1,
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
            
            self.execute_update("CREATE INDEX IF NOT EXISTS idx_hosting_surveys_company_id ON hosting_surveys(company_id)")

            # Paydaş listesi tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS survey_stakeholders (
                    stakeholder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER DEFAULT 1,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    organization TEXT,
                    role TEXT,
                    phone TEXT,
                    category TEXT,
                    notes TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            self.execute_update("CREATE INDEX IF NOT EXISTS idx_survey_stakeholders_company_id ON survey_stakeholders(company_id)")

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
            if response:
                logging.debug(f"[DEBUG] HTTP Status: {response.status_code}")
                logging.debug(f"[DEBUG] Response Headers: {dict(response.headers)}")
                logging.debug(f"[DEBUG] Response Text (ilk 500 char): {response.text[:500]}")

            if response and response.status_code == 200:
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
                    return {'success': False, 'error': error_msg}
            else:
                status = response.status_code if response else "No Response"
                logging.error(f"[HATA] HTTP {status}")
                return {'success': False, 'error': f"HTTP {status}"}

        except Exception as e:
            logging.error(f"[HATA] Genel Hata: {type(e).__name__}: {e}")
            return {'success': False, 'error': f'{type(e).__name__}: {str(e)}'}

    def _save_survey_locally(self, survey_data: Dict) -> None:
        """Anketi lokal veritabanına kaydet"""
        try:
            cid = self._ensure_context(None)
            
            self.insert('hosting_surveys', {
                'hosting_survey_id': survey_data['survey_id'],
                'survey_name': survey_data.get('survey_name', ''),
                'company_name': survey_data.get('company_name', ''),
                'survey_type': survey_data.get('survey_type', 'materiality'),
                'survey_url': survey_data['survey_url'],
                'survey_token': survey_data['token'],
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'deadline_date': survey_data.get('deadline_date', ''),
                'status': 'active',
                'last_sync_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }, company_id=cid)

        except Exception as e:
            logging.error(f"[HATA] Lokal kayıt hatası: {e}")

    def get_responses(self, survey_id: int) -> Dict[str, Any]:
        """Anket yanıtlarını çek"""
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
        """Özet istatistikleri çek"""
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
        """Paydaş yorumlarını çek"""
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

    def list_local_surveys(self, company_id: Optional[int] = None) -> List[Dict]:
        """
        Lokal veritabanındaki anketleri listele (Multi-tenant)
        """
        try:
            cid = self._ensure_context(company_id)
            return self.select(
                'hosting_surveys',
                company_id=cid,
                order_by='created_date DESC'
            )
        except Exception as e:
            logging.error(f"[HATA] Lokal anket listeleme hatası: {e}")
            return []

    def get_local_survey(self, hosting_survey_id: int, company_id: Optional[int] = None) -> Optional[Dict]:
        """
        Belirli bir anketi getir (Multi-tenant kontrolü ile)
        """
        try:
            cid = self._ensure_context(company_id)
            return self.select_one(
                'hosting_surveys',
                where='hosting_survey_id = ?',
                params=(hosting_survey_id,),
                company_id=cid
            )
        except Exception as e:
            logging.error(f"[HATA] Lokal anket getirme hatası: {e}")
            return None

    def list_surveys(self, status: str = 'all') -> Dict[str, Any]:
        """
        Anketleri listele.
        Önce lokal veritabanını kullanır, eğer boşsa veya senkronizasyon gerekirse API'ye (fallback) gider.
        Ancak multi-tenant yapıda API tüm anketleri döneceği için lokal tercih edilir.
        """
        try:
            # Multi-tenant: Sadece kendi şirketinin anketlerini gör
            local_surveys = self.list_local_surveys()
            
            # Eğer status filtresi varsa uygula
            if status != 'all':
                local_surveys = [s for s in local_surveys if s.get('status') == status]
            
            # API formatına uygun dönüş yap
            return {
                'success': True,
                'surveys': local_surveys,
                'source': 'local_db'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_status(self, survey_id: int, status: str) -> Dict[str, Any]:
        """Anket durumunu güncelle"""
        try:
            # Önce yetki kontrolü
            if not self.get_local_survey(survey_id):
                return {'success': False, 'error': 'Survey not found or access denied'}

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
            # Önce yetki kontrolü
            if not self.get_local_survey(survey_id):
                return {'success': False, 'error': 'Survey not found or access denied'}

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
            # Hosting survey ID'ye göre güncelliyoruz, company_id kontrolü opsiyonel ama iyi olur
            # Ancak hosting_survey_id zaten unique olmalı.
            self.execute_update("""
                UPDATE hosting_surveys 
                SET response_count = ?, last_sync_date = ?
                WHERE hosting_survey_id = ?
            """, (count, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), survey_id))
        except Exception as e:
            logging.error(f"[HATA] Yanıt sayısı güncelleme hatası: {e}")

    def _update_local_status(self, survey_id: int, status: str) -> None:
        """Lokal anket durumunu güncelle"""
        try:
            self.execute_update("""
                UPDATE hosting_surveys 
                SET status = ?, last_sync_date = ?
                WHERE hosting_survey_id = ?
            """, (status, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), survey_id))
        except Exception as e:
            logging.error(f"[HATA] Durum güncelleme hatası: {e}")

    def _delete_local_survey(self, survey_id: int) -> None:
        """Lokal anket kaydını sil"""
        try:
            self.execute_update("DELETE FROM hosting_surveys WHERE hosting_survey_id = ?", (survey_id,))
        except Exception as e:
            logging.error(f"[HATA] Lokal silme hatası: {e}")
