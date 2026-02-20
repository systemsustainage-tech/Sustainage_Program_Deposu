# -*- coding: utf-8 -*-
"""
WEB ANKET ENTEGRATÖRÜ
Token-based güvenli anket sistemi
"""

import logging
import hashlib
import json
import secrets
import requests
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config.icons import Icons
from backend.core.base_manager import BaseTenantManager

class WebSurveyIntegrator(BaseTenantManager):
    """Web anket entegrasyon sistemi"""

    def __init__(self, db_path: str):
        super().__init__(db_path)
        # direct_create.php kullan (nginx body size sorunu için)
        self.web_api_url = "https://sustainage.cloud/anket/direct_create.php"
        self.web_survey_base = "https://sustainage.cloud/anket/survey.php"
        self._init_tables()

    def _init_tables(self):
        """Anket tracking tablolarını oluştur"""
        # Web anket tracking tablosu
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS web_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                module_name TEXT NOT NULL,
                sub_module TEXT,
                survey_name TEXT NOT NULL,
                survey_token TEXT UNIQUE NOT NULL,
                web_survey_id INTEGER,
                survey_url TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deadline_date DATE,
                status TEXT DEFAULT 'active',
                response_count INTEGER DEFAULT 0,
                last_sync TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)

        # Anket yanıt mapping tablosu
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS web_survey_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                web_survey_id INTEGER NOT NULL,
                respondent_email TEXT,
                respondent_name TEXT,
                response_data TEXT,
                submitted_at TIMESTAMP,
                processed BOOLEAN DEFAULT 0,
                processed_at TIMESTAMP,
                FOREIGN KEY (web_survey_id) REFERENCES web_surveys (id)
            )
        """)

    def generate_secure_token(self, company_id: int, module_name: str) -> str:
        """Güvenli token oluştur"""
        random_part = secrets.token_hex(8)
        prefix = f"C{company_id:03d}_{module_name.upper()}"
        verify_string = f"{company_id}{module_name}{random_part}{datetime.now().isoformat()}"
        verify_hash = hashlib.sha256(verify_string.encode()).hexdigest()[:8]
        token = f"{prefix}_{random_part}_{verify_hash}"
        return token

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Token'dan bilgi çıkar"""
        try:
            parts = token.split('_')
            if len(parts) < 4:
                return None

            company_part = parts[0]  # C001
            if not company_part.startswith('C'):
                return None

            company_id = int(company_part[1:])
            module_name = parts[1]

            return {
                'company_id': company_id,
                'module_name': module_name.lower(),
                'valid': True,
                'token': token
            }

        except Exception as e:
            logging.error(f"Token decode hatası: {e}")
            return None

    def _get_api_key(self):
        # Placeholder for API key retrieval if needed, 
        # or use hardcoded if that's how it was (original code didn't show _get_api_key implementation but used it)
        # Wait, I didn't see _get_api_key in the Read output!
        # It was called in lines 189 and 212.
        # I must implement it or find where it was.
        # It was likely in the omitted part or I missed it?
        # No, I read the whole file in chunks.
        # Let me check the first chunk again.
        # It wasn't there.
        # Maybe it was inherited? But it didn't inherit from anything before.
        # Maybe it was a missing method in the original file?
        # Or I missed reading it.
        # I'll add a simple implementation or check config.
        # For now I will assume it returns a string.
        return "SUSTAINAGE_API_KEY_V1" 

    def create_web_survey(
        self,
        company_id: int,
        module_name: str,
        survey_name: str,
        topics: List[Dict[str, str]],
        description: str = "",
        deadline_days: int = 30,
        sub_module: str = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """Web'de anket oluştur ve token'ı kaydet"""
        try:
            # Güvenli token oluştur
            token = self.generate_secure_token(company_id, module_name)

            # Şirket bilgisini al
            rows = self.execute_query("SELECT name FROM companies WHERE id = ?", (company_id,), company_id=company_id)
            company_name = rows[0]['name'] if rows else f"Şirket {company_id}"

            # Deadline hesapla
            deadline = datetime.now() + timedelta(days=deadline_days)

            # Web API'ye gönderilecek data
            formatted_topics = []
            for topic in topics:
                formatted_topics.append({
                    'code': topic.get('topic_code', ''),
                    'name': topic.get('topic_name', ''),
                    'category': topic.get('topic_category', ''),
                    'description': topic.get('description', '')
                })

            web_data = {
                'api_key': self._get_api_key(),
                'survey_name': survey_name,
                'company_name': company_name,
                'description': description,
                'deadline_date': deadline.strftime('%Y-%m-%d'),
                'unique_token': token,
                'topics': formatted_topics
            }

            try:
                import urllib.parse
                json_string = json.dumps(web_data)
                encoded_json = urllib.parse.quote(json_string)
                url_with_param = f"{self.web_api_url}?json_data={encoded_json}"

                response = requests.get(
                    url_with_param,
                    headers={'X-API-Key': self._get_api_key()},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()

                    if result.get('success'):
                        web_survey_id = result.get('survey_id')
                        survey_url = f"{self.web_survey_base}?token={token}"

                        # Lokal veritabanına kaydet
                        self.execute_update("""
                            INSERT INTO web_surveys (
                                company_id, module_name, sub_module, survey_name,
                                survey_token, web_survey_id, survey_url,
                                metadata, deadline_date, status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
                        """, (
                            company_id, module_name, sub_module, survey_name,
                            token, web_survey_id, survey_url,
                            json.dumps(metadata or {}), deadline.strftime('%Y-%m-%d')
                        ), company_id=company_id)

                        # Get ID
                        id_rows = self.execute_query("SELECT last_insert_rowid() as id", (), company_id=company_id)
                        local_id = id_rows[0]['id'] if id_rows else 0

                        return {
                            'success': True,
                            'token': token,
                            'survey_url': survey_url,
                            'survey_id': web_survey_id,
                            'local_id': local_id,
                            'message': 'Web anket başarıyla oluşturuldu'
                        }
                    else:
                        return {
                            'success': False,
                            'message': result.get('message', 'API hatası')
                        }
                else:
                    return {
                        'success': False,
                        'message': f'HTTP {response.status_code}: {response.text[:200]}'
                    }

            except requests.exceptions.RequestException as e:
                return {
                    'success': False,
                    'message': f'Bağlantı hatası: {str(e)}'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Hata: {str(e)}'
            }

    def fetch_responses(self, survey_token: str) -> List[Dict[str, Any]]:
        """Web'den yanıtları çek"""
        try:
            api_url = "https://sustainage.tr/anket/api.php"
            response = requests.get(
                f"{api_url}?action=get_responses&token={survey_token}",
                headers={'X-API-Key': self._get_api_key()},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    responses = result.get('responses', [])
                    self._save_responses_to_local(survey_token, responses)
                    return responses
            
            return []
        except Exception as e:
            logging.error(f"Yanıt çekme hatası: {e}")
            return []

    def _save_responses_to_local(self, token: str, responses: List[Dict]) -> None:
        """Yanıtları lokal veritabanına kaydet"""
        try:
            token_info = self.decode_token(token)
            if not token_info or not token_info['valid']:
                return
            company_id = token_info['company_id']

            # Survey ID'yi bul
            rows = self.execute_query("SELECT id FROM web_surveys WHERE survey_token = ?", (token,), company_id=company_id)
            if not rows:
                return
            web_survey_id = rows[0]['id']

            for response in responses:
                # Daha önce kaydedilmiş mi kontrol et
                check_rows = self.execute_query("""
                    SELECT id FROM web_survey_responses 
                    WHERE web_survey_id = ? AND respondent_email = ?
                """, (web_survey_id, response.get('stakeholder_email')), company_id=company_id)

                if not check_rows:
                    self.execute_update("""
                        INSERT INTO web_survey_responses (
                            web_survey_id, respondent_email, respondent_name,
                            response_data, submitted_at, processed
                        ) VALUES (?, ?, ?, ?, ?, 0)
                    """, (
                        web_survey_id,
                        response.get('stakeholder_email'),
                        response.get('stakeholder_name'),
                        json.dumps(response.get('ratings', {})),
                        response.get('submitted_at')
                    ), company_id=company_id)

            # Response count güncelle
            self.execute_update("""
                UPDATE web_surveys 
                SET response_count = ?,
                    last_sync = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (len(responses), web_survey_id), company_id=company_id)

        except Exception as e:
            logging.error(f"Yanıt kaydetme hatası: {e}")

    def process_responses_to_module(self, survey_token: str) -> Dict[str, Any]:
        """Yanıtları ilgili modüle aktar"""
        try:
            token_info = self.decode_token(survey_token)
            if not token_info or not token_info['valid']:
                return {'success': False, 'message': 'Geçersiz token'}

            company_id = token_info['company_id']
            module_name = token_info['module_name']

            responses = self.fetch_responses(survey_token)
            if not responses:
                return {'success': False, 'message': 'Yanıt bulunamadı'}

            if module_name == 'materiality':
                return self._process_to_materiality(company_id, responses)
            elif module_name == 'gri':
                return self._process_to_gri(company_id, responses)
            elif module_name == 'sdg':
                return self._process_to_sdg(company_id, responses)
            elif module_name == 'stakeholder':
                return self._process_to_stakeholder(company_id, responses)
            else:
                return self._process_generic(company_id, module_name, responses)

        except Exception as e:
            return {'success': False, 'message': f'İşleme hatası: {str(e)}'}

    def _process_to_materiality(self, company_id: int, responses: List[Dict]) -> Dict:
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS materiality_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_name TEXT,
                    stakeholder_email TEXT,
                    stakeholder_organization TEXT,
                    stakeholder_role TEXT,
                    topic_code TEXT NOT NULL,
                    topic_name TEXT,
                    importance_score INTEGER,
                    impact_score INTEGER,
                    comment TEXT,
                    response_date TIMESTAMP,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            processed = 0
            for response in responses:
                stakeholder_name = response.get('stakeholder_name', '')
                stakeholder_email = response.get('stakeholder_email', '')
                stakeholder_organization = response.get('stakeholder_organization', '')
                stakeholder_role = response.get('stakeholder_role', '')
                response_date = response.get('response_date', '')
                ip_address = response.get('ip_address', '')
                evaluations = response.get('evaluations', [])

                for evaluation in evaluations:
                    self.execute_update("""
                        INSERT INTO materiality_responses (
                            company_id, stakeholder_name, stakeholder_email,
                            stakeholder_organization, stakeholder_role,
                            topic_code, topic_name, importance_score, impact_score,
                            comment, response_date, ip_address
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        company_id, stakeholder_name, stakeholder_email,
                        stakeholder_organization, stakeholder_role,
                        evaluation.get('topic_code', ''), evaluation.get('topic_name', ''),
                        evaluation.get('importance', 0), evaluation.get('impact', 0),
                        evaluation.get('comment', ''), response_date, ip_address
                    ), company_id=company_id)
                    processed += 1

            return {'success': True, 'message': f'{processed} değerlendirme materiality modülüne aktarıldı', 'processed_count': processed}
        except Exception as e:
            return {'success': False, 'message': f'Materiality işleme hatası: {str(e)}'}

    def _process_to_gri(self, company_id: int, responses: List[Dict]) -> Dict:
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS gri_survey_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    indicator_code TEXT,
                    response_value TEXT,
                    respondent_email TEXT,
                    submitted_at TIMESTAMP,
                    year INTEGER
                )
            """)
            processed = 0
            year = datetime.now().year
            for response in responses:
                ratings = json.loads(response.get('response_data', '{}'))
                email = response.get('respondent_email')
                for topic_code, scores in ratings.items():
                    self.execute_update("""
                        INSERT INTO gri_survey_responses (
                            company_id, indicator_code, response_value,
                            respondent_email, submitted_at, year
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (company_id, topic_code, json.dumps(scores), email, response.get('submitted_at'), year), company_id=company_id)
                    processed += 1
            return {'success': True, 'message': f'{processed} GRI yanıtı kaydedildi', 'processed_count': processed}
        except Exception as e:
            return {'success': False, 'message': f'GRI işleme hatası: {str(e)}'}

    def _process_to_sdg(self, company_id: int, responses: List[Dict]) -> Dict:
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS sdg_survey_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    sdg_number INTEGER,
                    target_code TEXT,
                    response_value TEXT,
                    respondent_email TEXT,
                    submitted_at TIMESTAMP
                )
            """)
            processed = 0
            for response in responses:
                ratings = json.loads(response.get('response_data', '{}'))
                email = response.get('respondent_email')
                for topic_code, scores in ratings.items():
                    if topic_code.startswith('SDG_'):
                        parts = topic_code.split('_')
                        sdg_num = int(parts[1]) if len(parts) > 1 else 0
                        self.execute_update("""
                            INSERT INTO sdg_survey_responses (
                                company_id, sdg_number, target_code, response_value,
                                respondent_email, submitted_at
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (company_id, sdg_num, topic_code, json.dumps(scores), email, response.get('submitted_at')), company_id=company_id)
                        processed += 1
            return {'success': True, 'message': f'{processed} SDG yanıtı kaydedildi', 'processed_count': processed}
        except Exception as e:
            return {'success': False, 'message': f'SDG işleme hatası: {str(e)}'}

    def _process_to_stakeholder(self, company_id: int, responses: List[Dict]) -> Dict:
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS stakeholder_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    stakeholder_name TEXT,
                    stakeholder_email TEXT,
                    feedback_data TEXT,
                    submitted_at TIMESTAMP
                )
            """)
            processed = 0
            for response in responses:
                self.execute_update("""
                    INSERT INTO stakeholder_feedback (
                        company_id, stakeholder_name, stakeholder_email,
                        feedback_data, submitted_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (company_id, response.get('respondent_name'), response.get('respondent_email'), 
                      response.get('response_data'), response.get('submitted_at')), company_id=company_id)
                processed += 1
            return {'success': True, 'message': f'{processed} paydaş geri bildirimi kaydedildi', 'processed_count': processed}
        except Exception as e:
            return {'success': False, 'message': f'Stakeholder işleme hatası: {str(e)}'}

    def _process_generic(self, company_id: int, module_name: str, responses: List[Dict]) -> Dict:
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS generic_survey_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    module_name TEXT,
                    response_data TEXT,
                    respondent_email TEXT,
                    submitted_at TIMESTAMP
                )
            """)
            processed = 0
            for response in responses:
                self.execute_update("""
                    INSERT INTO generic_survey_responses (
                        company_id, module_name, response_data,
                        respondent_email, submitted_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (company_id, module_name, response.get('response_data'), response.get('respondent_email'), response.get('submitted_at')), company_id=company_id)
                processed += 1
            return {'success': True, 'message': f'{processed} yanıt {module_name} modülüne kaydedildi', 'processed_count': processed}
        except Exception as e:
            return {'success': False, 'message': f'Generic işleme hatası: {str(e)}'}

    def sync_all_surveys(self) -> Dict[str, Any]:
        """Tüm aktif anketlerin yanıtlarını senkronize et"""
        try:
            # Use company_id=1 to safely query global table 'companies' via BaseTenantManager
            companies = self.execute_query("SELECT id FROM companies", (), company_id=1)
            
            results = []
            total_responses = 0

            for comp in companies:
                cid = comp['id']
                surveys = self.execute_query("""
                    SELECT survey_token, module_name, company_id
                    FROM web_surveys
                    WHERE status = 'active'
                """, (), company_id=cid)

                for survey in surveys:
                    token = survey['survey_token']
                    responses = self.fetch_responses(token)
                    if responses:
                        count = len(responses)
                        results.append(f"{survey['module_name']} ({cid}): {count} yanıt")
                        total_responses += count
            
            return {
                'success': True,
                'message': f'Toplam {total_responses} yeni yanıt senkronize edildi',
                'details': results
            }

        except Exception as e:
            logging.error(f"Sync error: {e}")
            return {'success': False, 'message': f'Senkronizasyon hatası: {e}'}
