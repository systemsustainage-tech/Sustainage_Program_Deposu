#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Yönetimi Modülü
REST API ve entegrasyon yönetimi
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict
from config.database import DB_PATH


class APIManager:
    """API yönetimi ve entegrasyon"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """API yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_endpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    endpoint_name TEXT NOT NULL,
                    endpoint_url TEXT NOT NULL,
                    http_method TEXT NOT NULL,
                    description TEXT,
                    authentication_type TEXT,
                    rate_limit INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    key_name TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    permissions TEXT,
                    expires_at TEXT,
                    last_used TEXT,
                    usage_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    api_key_id INTEGER,
                    endpoint_id INTEGER,
                    request_method TEXT,
                    request_url TEXT,
                    request_headers TEXT,
                    request_body TEXT,
                    response_status INTEGER,
                    response_body TEXT,
                    execution_time REAL,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (api_key_id) REFERENCES api_keys(id),
                    FOREIGN KEY (endpoint_id) REFERENCES api_endpoints(id)
                )
            """)

            conn.commit()
            logging.info("[OK] API yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] API yonetimi modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_api_endpoint(self, company_id: int, endpoint_name: str, endpoint_url: str,
                        http_method: str, description: str = None,
                        authentication_type: str = None, rate_limit: int = None) -> bool:
        """API endpoint ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO api_endpoints 
                (company_id, endpoint_name, endpoint_url, http_method, description,
                 authentication_type, rate_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, endpoint_name, endpoint_url, http_method, description,
                  authentication_type, rate_limit))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"API endpoint ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def create_api_key(self, company_id: int, key_name: str, permissions: str = None,
                      expires_at: str = None) -> str:
        """API anahtarı oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Basit API anahtarı oluştur
            api_key = f"sk_{company_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute("""
                INSERT INTO api_keys 
                (company_id, key_name, api_key, permissions, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, key_name, api_key, permissions, expires_at))

            conn.commit()
            return api_key

        except Exception as e:
            logging.error(f"API anahtarı oluşturma hatası: {e}")
            conn.rollback()
            return ""
        finally:
            conn.close()

    def log_api_request(self, company_id: int, api_key_id: int, endpoint_id: int,
                       request_method: str, request_url: str, request_headers: str,
                       request_body: str, response_status: int, response_body: str,
                       execution_time: float, ip_address: str = None,
                       user_agent: str = None) -> bool:
        """API isteği logla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("""
                INSERT INTO api_logs 
                (company_id, api_key_id, endpoint_id, request_method, request_url,
                 request_headers, request_body, response_status, response_body,
                 execution_time, ip_address, user_agent, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, api_key_id, endpoint_id, request_method, request_url,
                  request_headers, request_body, response_status, response_body,
                  execution_time, ip_address, user_agent, timestamp))

            # API anahtarı kullanım sayısını artır
            cursor.execute("""
                UPDATE api_keys 
                SET usage_count = usage_count + 1, last_used = ?
                WHERE id = ?
            """, (timestamp, api_key_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"API isteği loglama hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_api_summary(self, company_id: int) -> Dict:
        """API özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # API endpoint'leri
            cursor.execute("""
                SELECT endpoint_name, http_method, status, COUNT(*) as endpoint_count
                FROM api_endpoints 
                WHERE company_id = ? AND status = 'active'
                GROUP BY endpoint_name, http_method, status
            """, (company_id,))

            endpoints = []
            for row in cursor.fetchall():
                endpoints.append({
                    'endpoint_name': row[0],
                    'http_method': row[1],
                    'status': row[2]
                })

            # API anahtarları
            cursor.execute("""
                SELECT key_name, usage_count, last_used, status
                FROM api_keys 
                WHERE company_id = ? AND status = 'active'
                ORDER BY usage_count DESC
            """, (company_id,))

            api_keys = []
            total_usage = 0
            for row in cursor.fetchall():
                api_keys.append({
                    'key_name': row[0],
                    'usage_count': row[1],
                    'last_used': row[2],
                    'status': row[3]
                })
                total_usage += row[1] or 0

            # API logları (son 30 gün)
            cursor.execute("""
                SELECT COUNT(*), AVG(execution_time), 
                       SUM(CASE WHEN response_status >= 200 AND response_status < 300 THEN 1 ELSE 0 END),
                       SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END)
                FROM api_logs 
                WHERE company_id = ? AND timestamp >= datetime('now', '-30 days')
            """, (company_id,))

            log_result = cursor.fetchone()
            total_requests = log_result[0] or 0
            avg_execution_time = log_result[1] or 0
            successful_requests = log_result[2] or 0
            failed_requests = log_result[3] or 0

            return {
                'endpoints': endpoints,
                'api_keys': api_keys,
                'total_usage': total_usage,
                'total_requests_30d': total_requests,
                'avg_execution_time': avg_execution_time,
                'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                'failed_requests': failed_requests,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"API özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()

    def generate_api_documentation(self, company_id: int) -> str:
        """API dokümantasyonu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT endpoint_name, endpoint_url, http_method, description, authentication_type
                FROM api_endpoints 
                WHERE company_id = ? AND status = 'active'
                ORDER BY endpoint_name
            """, (company_id,))

            endpoints = cursor.fetchall()

            doc = f"""# API Dokümantasyonu - Şirket ID: {company_id}

## Genel Bilgiler
Bu dokümantasyon, SUSTAINAGE SDG API endpoint'lerini açıklamaktadır.

## Authentication
API anahtarı gereklidir. Anahtar header'da şu şekilde gönderilmelidir:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoint'ler

"""

            for endpoint in endpoints:
                name, url, method, description, auth_type = endpoint
                doc += f"""### {name}
- **URL:** `{url}`
- **Method:** `{method}`
- **Description:** {description or 'Açıklama yok'}
- **Authentication:** {auth_type or 'API Key'}

"""

            doc += """
## Response Format
Tüm API yanıtları JSON formatındadır:

```json
{
    "success": true,
    "data": {},
    "message": "İşlem başarılı"
}
```

## Error Codes
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
"""

            return doc

        except Exception as e:
            logging.error(f"API dokümantasyonu oluşturma hatası: {e}")
            return ""
        finally:
            conn.close()
