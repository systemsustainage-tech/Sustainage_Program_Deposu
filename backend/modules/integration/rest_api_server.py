#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REST API Server - TAM VE EKSİKSİZ
Flask tabanlı RESTful API endpoints
"""

import os
import sqlite3
from datetime import datetime
from functools import wraps
from typing import List

from flask import Flask, jsonify, request
from flask_cors import CORS
from config.database import DB_PATH


class RESTAPIServer:
    """REST API Server"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.app = Flask(__name__)
        origins_env = os.getenv('ALLOWED_ORIGINS')
        allowed_origins = [o.strip() for o in (origins_env.split(',') if origins_env else []) if o.strip()]
        if allowed_origins:
            CORS(self.app, origins=allowed_origins)
        else:
            CORS(self.app, origins=[])

        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

        self.app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
        self.app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        self._register_routes()
        self._allowed_modules = set(['SDG', 'GRI', 'TSRS', 'ESG', 'CARBON'])
        self._rate_limits = {}

    def _require_api_key(self, f):
        """API key kontrolü decorator"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')

            if not api_key:
                return jsonify({"error": "API key gerekli"}), 401

            # API key doğrula
            if not self._validate_api_key(api_key):
                return jsonify({"error": "Geçersiz API key"}), 403

            return f(*args, **kwargs)

        return decorated_function

    def _validate_api_key(self, api_key: str) -> bool:
        env_key = os.getenv('API_KEY')
        if env_key:
            return api_key == env_key
        return len(api_key) > 10

    def _rate_limit(self, key: str, max_per_min: int = 60) -> bool:
        now = int(datetime.now().timestamp())
        bucket = self._rate_limits.get(key)
        if not bucket or bucket['ts'] <= now - 60:
            self._rate_limits[key] = {'ts': now, 'cnt': 1}
            return True
        if bucket['cnt'] > max_per_min:
            return False
        bucket['cnt'] += 1
        return True

    def _register_routes(self) -> None:
        """API endpoints'leri kaydet"""

        # =====================================================
        # GENEL ENDPOİNTS
        # =====================================================

        @self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """Sistem sağlık kontrolü"""
            return jsonify({
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            })

        @self.app.route('/api/v1/info', methods=['GET'])
        def api_info():
            """API bilgileri"""
            return jsonify({
                "name": "SUSTAINAGE SDG API",
                "version": "1.0.0",
                "description": "Sürdürülebilirlik veri platformu API",
                "endpoints": self._get_endpoint_list()
            })

        # =====================================================
        # ŞİRKET ENDPOİNTS
        # =====================================================

        @self.app.route('/api/v1/company/<int:company_id>', methods=['GET'])
        @self._require_api_key
        def get_company(company_id):
            """Şirket bilgilerini getir"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT company_id, COALESCE(ticari_unvan, sirket_adi), sektor, created_at
                    FROM company_info WHERE company_id = ?
                    """,
                    (company_id,),
                )

                row = cursor.fetchone()
                conn.close()

                if row:
                    return jsonify({
                        "id": row[0],
                        "name": row[1],
                        "sector": row[2],
                        "created_at": row[3]
                    })

                return jsonify({"error": "Şirket bulunamadı"}), 404

            except Exception:
                return jsonify({"error": "İç sunucu hatası"}), 500

        # =====================================================
        # KARBON VERİLERİ ENDPOİNTS
        # =====================================================

        @self.app.route('/api/v1/carbon/emissions/<int:company_id>', methods=['GET'])
        @self._require_api_key
        def get_carbon_emissions(company_id):
            """Karbon emisyon verilerini getir"""
            try:
                y = request.args.get('year', str(datetime.now().year))
                try:
                    year = int(y)
                except Exception:
                    year = datetime.now().year

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT scope1_emissions, scope2_emissions, scope3_emissions,
                           total_emissions, reporting_year
                    FROM carbon_emissions
                    WHERE company_id = ? AND reporting_year = ?
                """, (company_id, year))

                row = cursor.fetchone()
                conn.close()

                if row:
                    return jsonify({
                        "company_id": company_id,
                        "year": row[4],
                        "scope1": row[0],
                        "scope2": row[1],
                        "scope3": row[2],
                        "total": row[3]
                    })

                return jsonify({"error": "Veri bulunamadı"}), 404

            except Exception:
                return jsonify({"error": "İç sunucu hatası"}), 500

        @self.app.route('/api/v1/carbon/emissions/<int:company_id>', methods=['POST'])
        @self._require_api_key
        def create_carbon_emissions(company_id):
            """Karbon emisyon verisi ekle"""
            try:
                data = request.get_json()

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT OR REPLACE INTO carbon_emissions
                    (company_id, reporting_year, scope1_emissions, scope2_emissions,
                     scope3_emissions, total_emissions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    company_id,
                    data.get('year', datetime.now().year),
                    data.get('scope1', 0),
                    data.get('scope2', 0),
                    data.get('scope3', 0),
                    data.get('total', 0)
                ))

                conn.commit()
                conn.close()

                return jsonify({"message": "Veri kaydedildi", "company_id": company_id}), 201

            except Exception:
                return jsonify({"error": "İç sunucu hatası"}), 500

        # =====================================================
        # SDG ENDPOİNTS
        # =====================================================

        @self.app.route('/api/v1/sdg/goals/<int:company_id>', methods=['GET'])
        @self._require_api_key
        def get_sdg_goals(company_id):
            """Seçilen SDG hedeflerini getir"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT goal_id FROM user_sdg_selections
                    WHERE company_id = ?
                    ORDER BY goal_id
                """, (company_id,))

                goals = [row[0] for row in cursor.fetchall()]
                conn.close()

                return jsonify({
                    "company_id": company_id,
                    "selected_goals": goals,
                    "total": len(goals)
                })

            except Exception:
                return jsonify({"error": "İç sunucu hatası"}), 500

        # =====================================================
        # RAPOR ENDPOİNTS
        # =====================================================

        @self.app.route('/api/v1/reports/<int:company_id>', methods=['GET'])
        @self._require_api_key
        def get_reports(company_id):
            """Şirket raporlarını listele"""
            try:
                module = request.args.get('module', None)
                client_ip = request.headers.get('X-Forwarded-For') or request.remote_addr or '0.0.0.0'
                rl_key = 'reports:' + client_ip
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                if module:
                    safe_module = ''.join([c for c in str(module) if c.isalnum() or c == '_' ])
                    if safe_module.upper() not in self._allowed_modules:
                        return jsonify({"error": "Geçersiz modül"}), 400
                    if not self._rate_limit(rl_key, 120):
                        return jsonify({"error": "Rate limit"}), 429
                    cursor.execute("""
                        SELECT id, report_name, module_code, report_type,
                               reporting_period, created_at
                        FROM report_registry
                        WHERE company_id = ? AND module_code = ?
                        ORDER BY created_at DESC
                    """, (company_id, safe_module))
                else:
                    if not self._rate_limit(rl_key, 120):
                        return jsonify({"error": "Rate limit"}), 429
                    cursor.execute("""
                        SELECT id, report_name, module_code, report_type,
                               reporting_period, created_at
                        FROM report_registry
                        WHERE company_id = ?
                        ORDER BY created_at DESC
                    """, (company_id,))

                reports = []
                for row in cursor.fetchall():
                    reports.append({
                        "id": row[0],
                        "name": row[1],
                        "module": row[2],
                        "type": row[3],
                        "period": row[4],
                        "created_at": row[5]
                    })

                conn.close()

                return jsonify({
                    "company_id": company_id,
                    "reports": reports,
                    "total": len(reports)
                })

            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def _get_endpoint_list(self) -> List[str]:
        """Tüm endpoint'leri listele"""
        return [
            "GET /api/v1/health - Sistem sağlık kontrolü",
            "GET /api/v1/info - API bilgileri",
            "GET /api/v1/company/{id} - Şirket bilgileri",
            "GET /api/v1/carbon/emissions/{id} - Karbon verileri",
            "POST /api/v1/carbon/emissions/{id} - Karbon verisi ekle",
            "GET /api/v1/sdg/goals/{id} - SDG hedefleri",
            "GET /api/v1/reports/{id} - Raporlar listesi"
        ]

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False) -> None:
        """API server'ı başlat"""
        @self.app.after_request
        def _set_security_headers(resp):
            resp.headers['X-Content-Type-Options'] = 'nosniff'
            resp.headers['X-Frame-Options'] = 'DENY'
            resp.headers['Cache-Control'] = 'no-store'
            return resp
        self.app.run(host=host, port=port, debug=debug)
