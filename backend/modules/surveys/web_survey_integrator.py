# -*- coding: utf-8 -*-
"""
WEB ANKET ENTEGRATÖRÜ
Token-based güvenli anket sistemi
"""

import logging
import hashlib
import json
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from config.icons import Icons
from config.database import DB_PATH


class WebSurveyIntegrator:
    """Web anket entegrasyon sistemi"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        # direct_create.php kullan (nginx body size sorunu için)
        self.web_api_url = "https://sustainage.cloud/anket/direct_create.php"
        self.web_survey_base = "https://sustainage.cloud/anket/survey.php"
        self._init_tables()

    def _init_tables(self):
        """Anket tracking tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Web anket tracking tablosu
        cursor.execute("""
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
        cursor.execute("""
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

        conn.commit()
        conn.close()

    def generate_secure_token(self, company_id: int, module_name: str) -> str:
        """Güvenli token oluştur
        
        Format: COMPANY_MODULE_RANDOM
        Örnek: C001_MATERIALITY_a3f9d8e2b1c4
        """
        # Random component
        random_part = secrets.token_hex(8)

        # Şirket ve modül bilgisi
        prefix = f"C{company_id:03d}_{module_name.upper()}"

        # Hash component (doğrulama için)
        verify_string = f"{company_id}{module_name}{random_part}{datetime.now().isoformat()}"
        verify_hash = hashlib.sha256(verify_string.encode()).hexdigest()[:8]

        # Final token
        token = f"{prefix}_{random_part}_{verify_hash}"

        return token

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Token'dan bilgi çıkar
        
        Returns:
            {
                'company_id': int,
                'module_name': str,
                'valid': bool
            }
        """
        try:
            parts = token.split('_')
            if len(parts) < 4:
                return None

            # Company ID
            company_part = parts[0]  # C001
            if not company_part.startswith('C'):
                return None

            company_id = int(company_part[1:])

            # Module name
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
        """Web'de anket oluştur ve token'ı kaydet
        
        Args:
            company_id: Şirket ID
            module_name: Modül adı (materiality, gri, sdg, vb.)
            survey_name: Anket başlığı
            topics: Anket konuları listesi
            description: Anket açıklaması
            deadline_days: Kaç gün sonra kapansın
            sub_module: Alt modül (opsiyonel)
            metadata: Ek bilgiler (opsiyonel)
        
        Returns:
            {
                'success': bool,
                'token': str,
                'survey_url': str,
                'survey_id': int,
                'local_id': int
            }
        """
        try:
            # Güvenli token oluştur
            token = self.generate_secure_token(company_id, module_name)

            # Şirket bilgisini al
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM companies WHERE id = ?", (company_id,))
            company = cursor.fetchone()
            company_name = company[0] if company else f"Şirket {company_id}"

            # Deadline hesapla
            deadline = datetime.now() + timedelta(days=deadline_days)

            # Web API'ye gönderilecek data
            # direct_create.php için field name'leri düzelt
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

            # Web API'ye istek gönder
            # NOT: Nginx body size sorundan dolayı GET method + json_data parametresi kullanıyoruz
            try:
                import urllib.parse

                # JSON'u URL encode et
                json_string = json.dumps(web_data)
                encoded_json = urllib.parse.quote(json_string)

                # GET parametresi olarak gönder
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
                        cursor.execute("""
                            INSERT INTO web_surveys (
                                company_id, module_name, sub_module, survey_name,
                                survey_token, web_survey_id, survey_url,
                                metadata, deadline_date, status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
                        """, (
                            company_id, module_name, sub_module, survey_name,
                            token, web_survey_id, survey_url,
                            json.dumps(metadata or {}), deadline.strftime('%Y-%m-%d')
                        ))

                        local_id = cursor.lastrowid
                        conn.commit()
                        conn.close()

                        return {
                            'success': True,
                            'token': token,
                            'survey_url': survey_url,
                            'survey_id': web_survey_id,
                            'local_id': local_id,
                            'message': 'Web anket başarıyla oluşturuldu'
                        }
                    else:
                        conn.close()
                        return {
                            'success': False,
                            'message': result.get('message', 'API hatası')
                        }
                else:
                    conn.close()
                    return {
                        'success': False,
                        'message': f'HTTP {response.status_code}: {response.text[:200]}'
                    }

            except requests.exceptions.RequestException as e:
                conn.close()
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
        """Web'den yanıtları çek
        
        Args:
            survey_token: Anket token'ı
        
        Returns:
            Yanıt listesi
        """
        try:
            # API endpoint düzeltmesi
            api_url = "https://sustainage.tr/anket/api.php"

            # API'den yanıtları al
            response = requests.get(
                f"{api_url}?action=get_responses&token={survey_token}",
                headers={'X-API-Key': self._get_api_key()},
                timeout=30
            )

            logging.debug(f"[DEBUG] API URL: {api_url}?action=get_responses&token={survey_token}")
            logging.debug(f"[DEBUG] HTTP Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                logging.debug(f"[DEBUG] Success: {result.get('success')}")
                logging.debug(f"[DEBUG] Total responses: {result.get('total_responses', 0)}")

                if result.get('success'):
                    responses = result.get('responses', [])

                    # Lokal veritabanına kaydet
                    self._save_responses_to_local(survey_token, responses)

                    return responses
            else:
                logging.error(f"[DEBUG] HTTP Error: {response.text[:200]}")

            return []

        except Exception as e:
            logging.error(f"Yanıt çekme hatası: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _save_responses_to_local(self, token: str, responses: List[Dict]) -> None:
        """Yanıtları lokal veritabanına kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Survey ID'yi bul
            cursor.execute("SELECT id FROM web_surveys WHERE survey_token = ?", (token,))
            survey = cursor.fetchone()

            if not survey:
                conn.close()
                return

            web_survey_id = survey[0]

            for response in responses:
                # Daha önce kaydedilmiş mi kontrol et
                cursor.execute("""
                    SELECT id FROM web_survey_responses 
                    WHERE web_survey_id = ? AND respondent_email = ?
                """, (web_survey_id, response.get('stakeholder_email')))

                if not cursor.fetchone():
                    cursor.execute("""
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
                    ))

            # Response count güncelle
            cursor.execute("""
                UPDATE web_surveys 
                SET response_count = ?,
                    last_sync = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (len(responses), web_survey_id))

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"Yanıt kaydetme hatası: {e}")

    def process_responses_to_module(self, survey_token: str) -> Dict[str, Any]:
        """Yanıtları ilgili modüle aktar
        
        Token'dan şirket ve modül bilgisini çıkarıp,
        yanıtları ilgili modülün veritabanı tablosuna yazar
        """
        try:
            # Token'ı decode et
            token_info = self.decode_token(survey_token)
            if not token_info or not token_info['valid']:
                return {'success': False, 'message': 'Geçersiz token'}

            company_id = token_info['company_id']
            module_name = token_info['module_name']

            # Yanıtları çek
            responses = self.fetch_responses(survey_token)

            if not responses:
                return {'success': False, 'message': 'Yanıt bulunamadı'}

            # Modüle göre işle
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
        """Çift önemlilik (materiality) modülüne aktar"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # materiality_responses tablosuna veri ekle (detaylı yanıtlar)
            cursor.execute("""
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

            # Her yanıtı işle
            for response in responses:
                stakeholder_name = response.get('stakeholder_name', '')
                stakeholder_email = response.get('stakeholder_email', '')
                stakeholder_organization = response.get('stakeholder_organization', '')
                stakeholder_role = response.get('stakeholder_role', '')
                response_date = response.get('response_date', '')
                ip_address = response.get('ip_address', '')

                # Her topic değerlendirmesini kaydet
                evaluations = response.get('evaluations', [])

                for evaluation in evaluations:
                    topic_code = evaluation.get('topic_code', '')
                    topic_name = evaluation.get('topic_name', '')
                    importance = evaluation.get('importance', 0)
                    impact = evaluation.get('impact', 0)
                    comment = evaluation.get('comment', '')

                    cursor.execute("""
                        INSERT INTO materiality_responses (
                            company_id, stakeholder_name, stakeholder_email,
                            stakeholder_organization, stakeholder_role,
                            topic_code, topic_name, importance_score, impact_score,
                            comment, response_date, ip_address
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        company_id, stakeholder_name, stakeholder_email,
                        stakeholder_organization, stakeholder_role,
                        topic_code, topic_name, importance, impact,
                        comment, response_date, ip_address
                    ))

                    processed += 1

            conn.commit()
            conn.close()

            return {
                'success': True,
                'message': f'{processed} değerlendirme materiality modülüne aktarıldı',
                'processed_count': processed
            }

        except Exception as e:
            return {'success': False, 'message': f'Materiality işleme hatası: {str(e)}'}

    def _process_to_gri(self, company_id: int, responses: List[Dict]) -> Dict:
        """GRI modülüne aktar"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # GRI responses tablosuna aktar
            cursor.execute("""
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
                    cursor.execute("""
                        INSERT INTO gri_survey_responses (
                            company_id, indicator_code, response_value,
                            respondent_email, submitted_at, year
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (company_id, topic_code, json.dumps(scores),
                         email, response.get('submitted_at'), year))
                    processed += 1

            conn.commit()
            conn.close()

            return {
                'success': True,
                'message': f'{processed} GRI yanıtı kaydedildi',
                'processed_count': processed
            }

        except Exception as e:
            return {'success': False, 'message': f'GRI işleme hatası: {str(e)}'}

    def _process_to_sdg(self, company_id: int, responses: List[Dict]) -> Dict:
        """SDG modülüne aktar"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # SDG survey responses
            cursor.execute("""
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
                    # SDG numarasını çıkar (örn: SDG_7_1 -> 7)
                    if topic_code.startswith('SDG_'):
                        parts = topic_code.split('_')
                        sdg_num = int(parts[1]) if len(parts) > 1 else 0

                        cursor.execute("""
                            INSERT INTO sdg_survey_responses (
                                company_id, sdg_number, target_code, response_value,
                                respondent_email, submitted_at
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (company_id, sdg_num, topic_code, json.dumps(scores),
                             email, response.get('submitted_at')))
                        processed += 1

            conn.commit()
            conn.close()

            return {
                'success': True,
                'message': f'{processed} SDG yanıtı kaydedildi',
                'processed_count': processed
            }

        except Exception as e:
            return {'success': False, 'message': f'SDG işleme hatası: {str(e)}'}

    def _process_to_stakeholder(self, company_id: int, responses: List[Dict]) -> Dict:
        """Stakeholder engagement modülüne aktar"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Stakeholder feedback tablosu
            cursor.execute("""
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
                cursor.execute("""
                    INSERT INTO stakeholder_feedback (
                        company_id, stakeholder_name, stakeholder_email,
                        feedback_data, submitted_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    company_id,
                    response.get('respondent_name'),
                    response.get('respondent_email'),
                    response.get('response_data'),
                    response.get('submitted_at')
                ))
                processed += 1

            conn.commit()
            conn.close()

            return {
                'success': True,
                'message': f'{processed} paydaş geri bildirimi kaydedildi',
                'processed_count': processed
            }

        except Exception as e:
            return {'success': False, 'message': f'Stakeholder işleme hatası: {str(e)}'}

    def _process_generic(self, company_id: int, module_name: str, responses: List[Dict]) -> Dict:
        """Generic modül için işle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Generic survey responses
            cursor.execute("""
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
                cursor.execute("""
                    INSERT INTO generic_survey_responses (
                        company_id, module_name, response_data,
                        respondent_email, submitted_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    company_id, module_name,
                    response.get('response_data'),
                    response.get('respondent_email'),
                    response.get('submitted_at')
                ))
                processed += 1

            conn.commit()
            conn.close()

            return {
                'success': True,
                'message': f'{processed} yanıt {module_name} modülüne kaydedildi',
                'processed_count': processed
            }

        except Exception as e:
            return {'success': False, 'message': f'Generic işleme hatası: {str(e)}'}

    def sync_all_surveys(self) -> Dict[str, Any]:
        """Tüm aktif anketlerin yanıtlarını senkronize et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Aktif anketleri al
            cursor.execute("""
                SELECT survey_token, module_name, company_id
                FROM web_surveys
                WHERE status = 'active'
            """)

            surveys = cursor.fetchall()
            conn.close()

            results = []
            total_responses = 0

            for survey in surveys:
                token, module, company_id = survey

                # Yanıtları çek
                responses = self.fetch_responses(token)

                if responses:
                    # Modüle aktar
                    process_result = self.process_responses_to_module(token)

                    results.append({
                        'token': token,
                        'module': module,
                        'responses': len(responses),
                        'success': process_result['success']
                    })

                    total_responses += len(responses)

            return {
                'success': True,
                'synced_surveys': len(results),
                'total_responses': total_responses,
                'results': results
            }

        except Exception as e:
            return {'success': False, 'message': f'Senkronizasyon hatası: {str(e)}'}

    def get_survey_status(self, survey_token: str) -> Dict[str, Any]:
        """Anket durumunu kontrol et"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    id, company_id, module_name, survey_name,
                    survey_url, deadline_date, status, response_count
                FROM web_surveys
                WHERE survey_token = ?
            """, (survey_token,))

            survey = cursor.fetchone()
            conn.close()

            if not survey:
                return {'success': False, 'message': 'Anket bulunamadı'}

            return {
                'success': True,
                'survey': {
                    'id': survey[0],
                    'company_id': survey[1],
                    'module': survey[2],
                    'name': survey[3],
                    'url': survey[4],
                    'deadline': survey[5],
                    'status': survey[6],
                    'response_count': survey[7]
                }
            }

        except Exception as e:
            return {'success': False, 'message': f'Durum kontrolü hatası: {str(e)}'}

    def _get_api_key(self) -> str:
        """API key'i al - config.php ile aynı"""
        # PHP: define('ADMIN_API_KEY', 'sustainage_secure_api_key_2025_' . hash('sha256', 'sustainage.tr'));
        return "sustainage_secure_api_key_2025_" + hashlib.sha256(b"sustainage.tr").hexdigest()

    def send_survey_email(
        self,
        survey_token: str,
        recipient_email: str,
        recipient_name: str,
        custom_message: str = None
    ) -> bool:
        """Anket e-postası gönder"""
        try:
            # Survey bilgisini al
            status = self.get_survey_status(survey_token)

            if not status['success']:
                return False

            survey = status['survey']

            from services.email_service import EmailService
            email_service = EmailService(db_path=self.db_path)

            subject = f"{Icons.REPORT} Anket Daveti: {survey['name']}"

            body = f"""
            <html>
            <body style="font-family: Segoe UI, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0;">Icons.REPORT Anket Daveti</h1>
                </div>
                
                <div style="padding: 30px; background: #f8f9fa;">
                    <h2 style="color: #333;">Görüşünüz Bizim İçin Önemli!</h2>
                    <p style="color: #666;">Sayın <strong>{recipient_name}</strong>,</p>
                    
                    {f'<p style="color: #666;">{custom_message}</p>' if custom_message else ''}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{survey['url']}" style="display: inline-block; background: #4facfe; color: white; padding: 20px 60px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 18px;">
                            Icons.ROCKET Ankete Başla
                        </a>
                    </div>
                    
                    <p style="color: #999; font-size: 12px;">Son tarih: {survey['deadline']}</p>
                </div>
            </body>
            </html>
            """

            return email_service.send_email_direct(recipient_email, subject, body)

        except Exception as e:
            logging.error(f"E-posta gönderme hatası: {e}")
            return False

    def update_survey_status(self, survey_token: str, new_status: str) -> Dict[str, Any]:
        """Anket durumunu güncelle (active, paused, closed)
        
        Args:
            survey_token: Anket token'ı
            new_status: Yeni durum ('active', 'paused', 'closed')
        
        Returns:
            Başarı durumu ve mesaj
        """
        try:
            # API'ye istek gönder
            api_url = "https://sustainage.tr/anket/api.php"

            response = requests.post(
                api_url,
                params={'action': 'update_status'},
                json={
                    'token': survey_token,
                    'status': new_status
                },
                headers={'X-API-Key': self._get_api_key()},
                timeout=10
            )

            logging.debug(f"[DEBUG] Status Update - HTTP {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                if result.get('success'):
                    # Lokal veritabanını da güncelle
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute("""
                        UPDATE web_surveys
                        SET status = ?
                        WHERE survey_token = ?
                    """, (new_status, survey_token))

                    conn.commit()
                    conn.close()

                    return {
                        'success': True,
                        'message': f'Anket durumu "{new_status}" olarak güncellendi'
                    }
                else:
                    return {
                        'success': False,
                        'message': result.get('message', 'Bilinmeyen API hatası')
                    }
            else:
                return {
                    'success': False,
                    'message': f'HTTP {response.status_code}: {response.text[:200]}'
                }

        except Exception as e:
            logging.error(f"Status güncelleme hatası: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f'Hata: {str(e)}'
            }


# Test
if __name__ == "__main__":
    integrator = WebSurveyIntegrator(DB_PATH)

    # Token oluştur ve decode et (test)
    token = integrator.generate_secure_token(1, "materiality")
    logging.info(f"Oluşturulan Token: {token}")

    decoded = integrator.decode_token(token)
    logging.info(f"Decode Sonucu: {decoded}")

