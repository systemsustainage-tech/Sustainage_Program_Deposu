import os
import sys
import logging
import json
import sqlite3
import base64
import time
from datetime import datetime
from functools import wraps
from typing import Optional, Dict, List
from types import SimpleNamespace
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, session, request, flash, send_file, g, jsonify, has_request_context

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

# Ensure paths are in sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from security.core.secure_password import (
    audit_log as security_audit_log,
    lockout_check as security_lockout_check,
    record_failed_login as security_record_failed_login,
    reset_failed_attempts as security_reset_failed_attempts,
)
from security.core.enhanced_2fa import (
    enable_totp_for_user,
    disable_2fa as twofa_disable,
    get_backup_codes,
    regenerate_backup_codes,
)
from yonetim.security.core.auth import (
    is_force_2fa as core_is_force_2fa,
    set_force_2fa as core_set_force_2fa,
)
from core.db_log_handler import DBLogHandler
from core.audit_manager import AuditManager
from backend.core.language_manager import LanguageManager

from mapping.sdg_gri_mapping import SDGGRIMapping
from modules.database.backup_recovery_manager import BackupRecoveryManager
from modules.data_import.data_importer import DataImporter
from modules.lca.lca_manager import LCAManager
from modules.supply_chain.supply_chain_manager import SupplyChainManager
from modules.realtime.realtime_manager import RealTimeMonitoringManager
from modules.environmental.biodiversity_manager import BiodiversityManager
from config.database import DB_PATH
# FORCE DB_PATH for remote environment to ensure correct DB is used
if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

# Initialize Managers
audit_manager = AuditManager(DB_PATH)
language_manager = LanguageManager(BASE_DIR)

COMPANY_INFO_FIELDS = [
    "name",
    "legal_name",
    "trading_name",
    "description",
    "business_model",
    "key_products_services",
    "markets_served",
    "sector",
    "industry_code",
    "industry_description",
    "company_size",
    "employee_count",
    "isic_code",
    "registration_number",
    "tax_number",
    "legal_form",
    "establishment_date",
    "ownership_type",
    "parent_company",
    "subsidiaries",
    "stock_exchange",
    "ticker_symbol",
    "fiscal_year_end",
    "reporting_period",
    "annual_revenue",
    "currency",
    "auditor",
    "sustainability_strategy",
    "material_topics",
    "stakeholder_groups",
    "esg_rating_agency",
    "esg_rating",
    "certifications",
    "memberships",
    "headquarters_address",
    "city",
    "postal_code",
    "country",
    "phone",
    "email",
    "website",
    "sustainability_contact",
    "vizyon",
    "misyon",
    "degerler",
    "tesisler_ozet",
    "kilometre_taslari_ozet",
    "urun_hizmet_ozet",
    "karbon_profili_ozet",
    "uyelikler_ozet",
    "oduller_ozet",
    "sirket_adi",
    "ticari_unvan",
    "vergi_no",
    "vergi_dairesi",
    "telefon",
    "calisan_sayisi",
    "aktif",
    "sektor",
    "il",
    "ilce",
    "posta_kodu",
    "adres"
]


def ensure_company_info_table() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER UNIQUE
        )
        """
    )
    cur.execute("PRAGMA table_info(company_info)")
    existing = {row[1] for row in cur.fetchall()}
    for col in COMPANY_INFO_FIELDS + ["updated_at"]:
        if col in existing or col in ("id", "company_id"):
            continue
        cur.execute(f"ALTER TABLE company_info ADD COLUMN {col} TEXT")
    conn.commit()
    conn.close()


ensure_company_info_table()

# Optional integrations
import traceback
try:
    try:
        from yonetim.kullanici_yonetimi.models.user_manager import UserManager
    except ImportError:
        # Fallback if yonetim is not found directly, try via backend
        from backend.yonetim.kullanici_yonetimi.models.user_manager import UserManager
        
    USER_MANAGER_AVAILABLE = True
    # Explicitly make UserManager available in global scope to avoid NameError
    globals()['UserManager'] = UserManager
except Exception as e:
    logging.error(f"UserManager import error: {e}")
    sys.stderr.write(f"CRITICAL: UserManager import failed: {e}\n")
    traceback.print_exc(file=sys.stderr)
    USER_MANAGER_AVAILABLE = False

try:
    from modules.super_admin.components.rate_limiter import RateLimiter
    from modules.super_admin.components.ip_manager import IPManager
    from modules.super_admin.components.monitoring_dashboard import MonitoringDashboard
    from modules.super_admin.components.license_generator import LicenseGenerator
    rate_limiter = RateLimiter(DB_PATH)
    IP_MANAGER_AVAILABLE = True
    MONITORING_AVAILABLE = True
    LICENSE_MANAGER_AVAILABLE = True
except Exception as e:
    logging.error(f"Super admin components import error: {e}")
    class _DummyLimiter:
        def check_rate_limit(self, *args, **kwargs):
            return {'allowed': True, 'current_count': 0, 'limit': 999, 'reset_in': 0, 'blocked': False}
        def get_rate_limit_stats(self, *args, **kwargs):
            return []
        def cleanup_old_records(self, *args, **kwargs):
            return 0
    rate_limiter = _DummyLimiter()
    IP_MANAGER_AVAILABLE = False
    MONITORING_AVAILABLE = False
    LICENSE_MANAGER_AVAILABLE = False


def require_company_context(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        # Enforce Company Context
        company_id = session.get('company_id')
        if not company_id:
            # STRICT MODE: No fallback to 1.
            # If no company context, force logout or error.
            session.clear()
            flash('Oturum süreniz doldu veya geçerli bir şirket bulunamadı.', 'warning')
            return redirect(url_for('login'))
            
        g.company_id = company_id
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)

@app.context_processor
def inject_notifications():
    if 'user_id' not in session:
        return {'unread_notifications': [], 'unread_notification_count': 0}
    
    try:
        user_id = session.get('user_id')
        if not user_id:
            return {'unread_notifications': [], 'unread_notification_count': 0}
            
        nm = MANAGERS.get('notification')
        if nm:
            unread = nm.get_unread_notifications(user_id, limit=5)
            count = nm.get_unread_count(user_id)
            return {'unread_notifications': unread, 'unread_notification_count': count}
    except Exception as e:
        logging.error(f"Context processor error: {e}")
        
    return {'unread_notifications': [], 'unread_notification_count': 0}

# Add DB log handler
try:
    db_log_handler = DBLogHandler(DB_PATH)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    db_log_handler.setFormatter(formatter)
    
    # Add to root logger to capture all logs
    root_logger = logging.getLogger()
    root_logger.addHandler(db_log_handler)
    
    # Also ensure app logger has it
    app.logger.addHandler(db_log_handler)
    app.logger.setLevel(logging.INFO)
    
    logging.info("DBLogHandler attached to root and app loggers.")
except Exception as e:
    print(f"Failed to attach DBLogHandler: {e}")

# Fix for login loop: Use a stable secret key if environment variable is not set
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sustainage_secret_key_fixed_2024_xyz_987')

# Translation Setup
def gettext(key, *args):
    """
    Retrieves translation for the given key using LanguageManager.
    Falls back to 'tr' if session language is not set.
    """
    default = args[0] if args else None
    current_lang = session.get('lang', 'tr')
    return language_manager.get_text(key, lang=current_lang, default=default)

app.jinja_env.globals.update(_=gettext)

# Define _ in global scope for Python code usage
_ = gettext

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in language_manager.translations:
        session['lang'] = lang
        flash(f"Dil değiştirildi: {lang}", "success")
    else:
        flash("Geçersiz dil seçimi.", "danger")
    return redirect(request.referrer or url_for('dashboard'))

# --- Modern UI Route (Vue.js) ---
from flask import send_from_directory

@app.route('/modern')
@require_company_context
def modern_ui():
    """Serves the Vue.js Single Page Application."""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Try to serve index.html from static/vue/
    # If the user hasn't run 'npm run build', this file won't exist.
    try:
        return send_from_directory('static/vue', 'index.html')
    except Exception as e:
        # Fallback for when build is missing
        return render_template('base.html', title='Modern UI - Build Pending', 
                             content='<div class="alert alert-info"><h1>Modern UI Hazırlanıyor</h1><p>Vue.js arayüzü henüz derlenmemiş. Lütfen <code>frontend/</code> klasöründe <code>npm run build</code> komutunu çalıştırın.</p></div>')

# --- API v1 Routes (Vue.js Support) ---

@app.route('/api/v1/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
        
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Kullanıcı adı ve şifre gereklidir.'}), 400
        
    client_ip = request.remote_addr or 'unknown'
    max_attempts, lock_seconds = _get_login_lockout_params()
    rl = rate_limiter.check_rate_limit('login', client_ip, max_requests=max_attempts, window_seconds=lock_seconds)
    
    if not rl.get('allowed', True):
        wait_time = rl.get("reset_in", 60)
        return jsonify({'error': f'Çok fazla deneme. {wait_time} saniye sonra tekrar deneyin.'}), 429

    # Check lockout
    try:
        conn = get_db()
        row = conn.execute("SELECT locked_until FROM users WHERE username=?", (username,)).fetchone()
        if row and row['locked_until']:
            import time
            if int(row['locked_until']) > int(time.time()):
                wait = int(row['locked_until']) - int(time.time())
                conn.close()
                return jsonify({'error': f'Hesabınız kilitli. {wait} saniye bekleyin.'}), 403
        conn.close()
    except Exception as e:
        logging.error(f"Lock check error: {e}")

    if user_manager:
        user = user_manager.authenticate(username, password)
        if user:
            session['user'] = user.get('display_name', user.get('username'))
            session['user_id'] = user.get('id')
            
            # Role
            try:
                conn = get_db()
                role_row = conn.execute("""
                    SELECT r.name
                    FROM roles r
                    JOIN user_roles ur ON r.id = ur.role_id
                    WHERE ur.user_id = ?
                """, (user.get('id'),)).fetchone()
                session['role'] = role_row['name'] if role_row else 'User'
                conn.close()
            except Exception:
                session['role'] = 'User'
                
            # Company
            try:
                company_id = user_manager.get_user_company(user.get('id'))
                if isinstance(company_id, dict):
                     company_id = company_id.get('id') or company_id.get('company_id')
                session['company_id'] = company_id 
            except Exception as e:
                logging.error(f"Company id error: {e}")
                session['company_id'] = None
                
            return jsonify({
                'success': True,
                'user': {
                    'username': user.get('username'),
                    'display_name': user.get('display_name'),
                    'role': session.get('role'),
                    'company_id': session.get('company_id')
                }
            })
        else:
             return jsonify({'error': 'Kullanıcı adı veya parola hatalı.'}), 401
    else:
        return jsonify({'error': 'Sistem hatası: Kullanıcı yönetimi devre dışı.'}), 500

@app.route('/api/v1/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/v1/dashboard-stats')
@require_company_context
def api_dashboard_stats():
    # Fetch module stats
    module_data = []
    try:
        from backend.modules.dashboard_stats import DashboardStatsManager
        dsm = DashboardStatsManager(DB_PATH)
        stats = dsm.get_module_stats(g.company_id)
        
        # Transform to list of objects
        for name, score in stats.items():
            module_data.append({
                'name': name.replace('_', ' ').title(),
                'score': score,
                'status': 'Active' if score > 0 else 'Pending'
            })
    except Exception as e:
        logging.error(f"API Dashboard stats error: {e}")
        
    return jsonify({
        'alerts': 0, 
        'modules': module_data
    })

from modules.environmental.carbon_manager import CarbonManager
from modules.environmental.carbon_reporting import CarbonReporting
from modules.environmental.energy_manager import EnergyManager
from modules.environmental.energy_reporting import EnergyReporting
from modules.environmental.water_manager import WaterManager
from modules.environmental.water_reporting import WaterReporting
from modules.environmental.waste_manager import WasteManager
from modules.environmental.waste_reporting import WasteReporting
from modules.social.social_manager import SocialManager
from modules.social.social_reporting import SocialReporting
from modules.governance.corporate_governance import CorporateGovernanceManager
from modules.governance.governance_reporting import GovernanceReporting
from modules.company.company_manager import CompanyManager
from modules.reporting.report_generator import ReportGenerator
from modules.reporting.advanced_report_manager import AdvancedReportManager
from modules.stakeholder.stakeholder_engagement import StakeholderEngagement

# Manager Initialization (Lazy Loading or Global)
MANAGERS = {
    'sdg': None,
    'gri': None,
    'carbon': None,
    'energy': None,
    'water': None,
    'waste': None,
    'biodiversity': None,
    'social': None,
    'governance': None,
    'supply_chain': None,
    'economic': None,
    'esg': None,
    'cbam': None,
    'csrd': None,
    'taxonomy': None,
    'issb': None,
    'iirc': None,
    'esrs': None,
    'tcfd': None,
    'tnfd': None,
    'cdp': None,
    'product_technology': None,
    'benchmark': None,
    'regulation': None,
    'notification': None
}

# Register Supplier Portal Blueprint
# DISABLED for security: Contains hardcoded credentials (supplier/supplier). Enable only after implementing proper auth.
# try:
#     from backend.modules.supplier_portal import supplier_portal_bp
#     app.register_blueprint(supplier_portal_bp)
#     logging.info("Supplier Portal blueprint registered.")
# except Exception as e:
#     logging.error(f"Failed to register Supplier Portal blueprint: {e}")

def _init_managers():
    global MANAGERS
    try:
        from modules.sdg.sdg_manager import SDGManager
        MANAGERS['sdg'] = SDGManager(DB_PATH)
    except Exception as e:
        logging.error(f"SDGManager init: {e}")
    try:
        from modules.gri.gri_manager import GRIManager
        MANAGERS['gri'] = GRIManager(DB_PATH)
    except Exception as e:
        logging.error(f"GRIManager init: {e}")
    try:
        from modules.social.social_manager import SocialManager
        MANAGERS['social'] = SocialManager(DB_PATH)
    except Exception as e:
        logging.error(f"SocialManager init: {e}")
    try:
        from modules.governance.corporate_governance import CorporateGovernanceManager
        MANAGERS['governance'] = CorporateGovernanceManager(DB_PATH)
    except Exception as e:
        logging.error(f"CorporateGovernanceManager init: {e}")
    try:
        from modules.environmental.carbon_manager import CarbonManager
        MANAGERS['carbon'] = CarbonManager(DB_PATH)
    except Exception as e:
        logging.error(f"CarbonManager init: {e}")
    try:
        from modules.environmental.energy_manager import EnergyManager
        MANAGERS['energy'] = EnergyManager(DB_PATH)
    except Exception as e:
        logging.error(f"EnergyManager init: {e}")
    try:
        from modules.esg.esg_manager import ESGManager
        MANAGERS['esg'] = ESGManager(BACKEND_DIR)
    except Exception as e:
        logging.error(f"ESGManager init: {e}")
    try:
        from modules.cbam.cbam_manager import CBAMManager
        MANAGERS['cbam'] = CBAMManager(DB_PATH)
    except Exception as e:
        logging.error(f"CBAMManager init: {e}")
    try:
        from modules.csrd.csrd_compliance_manager import CSRDComplianceManager
        MANAGERS['csrd'] = CSRDComplianceManager(DB_PATH)
    except Exception as e:
        logging.error(f"CSRDComplianceManager init: {e}")
    try:
        from modules.eu_taxonomy.taxonomy_manager import EUTaxonomyManager
        MANAGERS['taxonomy'] = EUTaxonomyManager(DB_PATH)
    except Exception as e:
        logging.error(f"EUTaxonomyManager init: {e}")
    try:
        from modules.environmental.waste_manager import WasteManager
        MANAGERS['waste'] = WasteManager(DB_PATH)
    except Exception as e:
        logging.error(f"WasteManager init: {e}")
    try:
        from modules.environmental.water_manager import WaterManager
        MANAGERS['water'] = WaterManager(DB_PATH)
    except Exception as e:
        logging.error(f"WaterManager init: {e}")
    try:
        from modules.environmental.biodiversity_manager import BiodiversityManager
        MANAGERS['biodiversity'] = BiodiversityManager(DB_PATH)
    except Exception as e:
        logging.error(f"BiodiversityManager init: {e}")
    try:
        from modules.economic.economic_value_manager import EconomicValueManager
        MANAGERS['economic'] = EconomicValueManager(DB_PATH)
    except Exception as e:
        logging.error(f"EconomicValueManager init: {e}")
    try:
        from modules.issb.issb_manager import ISSBManager
        MANAGERS['issb'] = ISSBManager(DB_PATH)
    except Exception as e:
        logging.error(f"ISSBManager init: {e}")
    try:
        from modules.iirc.iirc_manager import IIRCManager
        MANAGERS['iirc'] = IIRCManager(DB_PATH)
    except Exception as e:
        logging.error(f"IIRCManager init: {e}")
    try:
        from modules.esrs.esrs_manager import ESRSManager
        MANAGERS['esrs'] = ESRSManager(DB_PATH)
    except Exception as e:
        logging.error(f"ESRSManager init: {e}")
    try:
        from modules.tcfd.tcfd_manager import TCFDManager
        MANAGERS['tcfd'] = TCFDManager(DB_PATH)
    except Exception as e:
        logging.error(f"TCFDManager init: {e}")
    try:
        from modules.tnfd.tnfd_manager import TNFDManager
        MANAGERS['tnfd'] = TNFDManager(DB_PATH)
    except Exception as e:
        logging.error(f"TNFDManager init: {e}")
    try:
        from modules.cdp.cdp_manager import CDPManager
        MANAGERS['cdp'] = CDPManager(DB_PATH)
    except Exception as e:
        logging.error(f"CDPManager init: {e}")
    try:
        from modules.supply_chain.supply_chain_manager import SupplyChainManager
        MANAGERS['supply_chain'] = SupplyChainManager(DB_PATH)
    except Exception as e:
        logging.error(f"SupplyChainManager init: {e}")
    try:
        from modules.cdp.cdp_manager import CDPManager
        MANAGERS['cdp'] = CDPManager(DB_PATH)
    except Exception as e:
        logging.error(f"CDPManager init: {e}")
    try:
        from modules.issb.issb_manager import ISSBManager
        MANAGERS['issb'] = ISSBManager(DB_PATH)
    except Exception as e:
        logging.error(f"ISSBManager init: {e}")
    try:
        from modules.iirc.iirc_manager import IIRCManager
        MANAGERS['iirc'] = IIRCManager(DB_PATH)
    except Exception as e:
        logging.error(f"IIRCManager init: {e}")
    try:
        from modules.esrs.esrs_manager import ESRSManager
        MANAGERS['esrs'] = ESRSManager(DB_PATH)
    except Exception as e:
        logging.error(f"ESRSManager init: {e}")
    try:
        from modules.tcfd.tcfd_manager import TCFDManager
        MANAGERS['tcfd'] = TCFDManager(DB_PATH)
    except Exception as e:
        logging.error(f"TCFDManager init: {e}")
    try:
        from modules.tnfd.tnfd_manager import TNFDManager
        MANAGERS['tnfd'] = TNFDManager(DB_PATH)
    except Exception as e:
        logging.error(f"TNFDManager init: {e}")
    try:
        from yonetim.product_technology.product_tech_manager import ProductTechManager
        MANAGERS['product_technology'] = ProductTechManager(DB_PATH)
    except Exception as e:
        logging.error(f"ProductTechManager init: {e}")

    try:
        from modules.analytics.sector_benchmark_database import SectorBenchmarkDatabase
        MANAGERS['benchmark'] = SectorBenchmarkDatabase(DB_PATH)
    except Exception as e:
        logging.error(f"BenchmarkManager init: {e}")

    try:
        from modules.regulation.regulation_manager import RegulationManager
        MANAGERS['regulation'] = RegulationManager(DB_PATH)
        MANAGERS['regulation'].populate_initial_data()
    except Exception as e:
        logging.error(f"RegulationManager init: {e}")

    try:
        from modules.stakeholder.stakeholder_engagement import StakeholderEngagement
        MANAGERS['stakeholder'] = StakeholderEngagement(DB_PATH)
    except Exception as e:
        logging.error(f"StakeholderEngagement init: {e}")

    try:
        from modules.notification.notification_manager import NotificationManager
        MANAGERS['notification'] = NotificationManager(DB_PATH)
    except Exception as e:
        logging.error(f"NotificationManager init: {e}")

    try:
        from modules.environmental.biodiversity_manager import BiodiversityManager
        MANAGERS['biodiversity'] = BiodiversityManager(DB_PATH)
    except Exception as e:
        logging.error(f"BiodiversityManager init: {e}")

_init_managers()

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_report_registry_table():
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS report_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                module_code TEXT NOT NULL,
                report_name TEXT NOT NULL,
                report_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                reporting_period TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                tags TEXT,
                description TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error ensuring report_registry table: {e}")

ensure_report_registry_table()

def _get_system_setting_int(key: str, default: int) -> int:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # Schema check/update is done via scripts now to avoid overhead here
        # But for safety in dev:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT,
                value TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER,
                PRIMARY KEY (key, company_id)
            )
            """
        )
        
        # Determine company_id from context
        company_id = None
        # Check g first (request context)
        if has_request_context() and hasattr(g, 'company_id') and g.company_id:
            company_id = g.company_id
        # Check session second (if outside request context but in session context)
        elif has_request_context() and session and 'company_id' in session:
            company_id = session['company_id']
            
        if company_id is None:
            return default

        # Try to get company-specific setting
        cur.execute("SELECT value FROM system_settings WHERE key=? AND company_id=?", (key, company_id))
        row = cur.fetchone()
        
        conn.close()
        if row and row[0] is not None:
            try:
                val = int(str(row[0]).strip())
                if val > 0:
                    return val
            except ValueError:
                pass
    except Exception as e:
        logging.error(f"System setting read error for {key}: {e}")
    return default


def _get_login_lockout_params() -> tuple[int, int]:
    max_attempts = _get_system_setting_int('sec_max_login_attempts', 5)
    lock_seconds = _get_system_setting_int('sec_lockout_seconds', 15 * 60)
    return max_attempts, lock_seconds


def _get_session_timeout_seconds() -> int:
    minutes = _get_system_setting_int('sec_session_timeout_minutes', 30)
    if minutes <= 0:
        minutes = 30
    return minutes * 60


@app.before_request
def enforce_session_timeout():
    # 1. Setup Global Context if available
    if 'company_id' in session:
        g.company_id = session['company_id']

    exempt_endpoints = {
        'login',
        'logout',
        'health',
        'forgot_password',
        'static',
    }
    endpoint = request.endpoint or ''
    if endpoint in exempt_endpoints:
        return
    if 'user' not in session:
        return
    try:
        timeout_seconds = _get_session_timeout_seconds()
        now = int(time.time())
        last = session.get('last_activity')
        if isinstance(last, (int, float)):
            if now - int(last) > timeout_seconds:
                session.clear()
                flash('Oturum zaman aşımına uğradı. Lütfen tekrar giriş yapın.', 'warning')
                return redirect(url_for('login'))
        session['last_activity'] = now
    except Exception as e:
        logging.error(f"Session timeout enforcement error: {e}")

user_manager = None
if USER_MANAGER_AVAILABLE:
    try:
        logging.info(f"Initializing UserManager with DB_PATH: {DB_PATH}")
        user_manager = UserManager(DB_PATH)
    except Exception as e:
        logging.error(f"UserManager init error: {e}")
        user_manager = None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        role = str(session.get('role', 'User')).lower()
        if role not in ['admin', 'super_admin', 'test admin']:
            flash('Bu işlem için yetkiniz bulunmamaktadır.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        role = str(session.get('role', 'User')).lower()
        if role not in ['super_admin', '__super__']:
            flash(_('admin_only_access', 'Bu sayfaya sadece Süper Admin erişebilir.'), 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/health')
def health():
    return "OK", 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    client_ip = request.remote_addr or 'unknown'
    user_agent = request.headers.get('User-Agent', '')

    if request.method == 'POST':
        username = (request.form.get('username', '') or '').strip()
        password = request.form.get('password', '')
        
        # Admin ve super user için limitleri esnet
        is_privileged = username in ['admin', '__super__']

        if not is_privileged:
            rl = rate_limiter.check_rate_limit('login', client_ip, max_requests=5, window_seconds=60)
            if not rl.get('allowed', True):
                flash(f'Çok fazla deneme. {rl.get("reset_in", 60)} saniye sonra tekrar deneyin.', 'danger')
                try:
                    security_audit_log(DB_PATH, "LOGIN_RATE_LIMIT_WEB", username=None, user_id=None, success=False, ip_address=client_ip, metadata={"reason": "rate_limited", "user_agent": user_agent})
                except Exception as e:
                    logging.error(f"Login rate limit audit error: {e}")
                return render_template('login.html'), 429

        max_attempts, lock_seconds = _get_login_lockout_params()

        try:
            # Privileged users skip lockout check
            if not is_privileged:
                can_login, wait_seconds = security_lockout_check(DB_PATH, username)
                if not can_login:
                    flash(f'Hesabınız kilitli. {wait_seconds} saniye bekleyin.', 'danger')
                    try:
                        security_audit_log(
                            DB_PATH,
                            "LOGIN_LOCKED_WEB",
                            username=username,
                            user_id=None,
                            success=False,
                            ip_address=client_ip,
                            metadata={"wait_seconds": wait_seconds, "user_agent": user_agent},
                        )
                    except Exception as e:
                        logging.error(f"Login locked audit error: {e}")
                    return render_template('login.html')
        except Exception as e:
            logging.error(f"Lock check error: {e}")

        if user_manager:
            logging.error("DEBUG: Calling user_manager.authenticate...")
            user = user_manager.authenticate(username, password)
            logging.error(f"DEBUG: Authenticate result: {user}")
            if user:
                try:
                    security_reset_failed_attempts(DB_PATH, username)
                except Exception as e:
                    logging.error(f"Reset failed attempts error: {e}")
                session['user'] = user.get('display_name', user.get('username'))
                session['user_id'] = user.get('id')
                try:
                    conn = get_db()
                    role_row = conn.execute("""
                        SELECT r.name
                        FROM roles r
                        JOIN user_roles ur ON r.id = ur.role_id
                        WHERE ur.user_id = ?
                    """, (user.get('id'),)).fetchone()
                    session['role'] = role_row['name'] if role_row else 'User'
                    conn.close()
                except Exception:
                    session['role'] = 'User'
                try:
                    company_id = user_manager.get_user_company(user.get('id'))
                    # STRICT MODE: If no company assigned, do NOT fallback to 1.
                    session['company_id'] = company_id
                except Exception as e:
                    logging.error(f"Company id error: {e}")
                    session['company_id'] = None
                try:
                    security_audit_log(DB_PATH, "LOGIN_SUCCESS_WEB", username=username, user_id=user.get('id'), success=True, ip_address=client_ip, metadata={"role": session.get('role'), "user_agent": user_agent})
                    # General Audit Log
                    audit_manager.log_action(user_id=user.get('id'), action="LOGIN", resource="web_app", details="User logged in", ip_address=client_ip, company_id=session.get('company_id'))
                except Exception as e:
                    logging.error(f"Login success audit error: {e}")
                flash('Giriş başarılı!', 'success')
                return redirect(url_for('dashboard'))
            else:
                if username == 'admin' and password == 'admin':
                    conn = get_db()
                    exists = conn.execute("SELECT 1 FROM users WHERE username='admin'").fetchone()
                    conn.close()
                    if not exists:
                        session['user'] = 'admin_test'
                        session['role'] = 'Test Admin'
                        try:
                            security_audit_log(DB_PATH, "LOGIN_SUCCESS_WEB_TEST", username='admin_test', user_id=None, success=True, ip_address=client_ip, metadata={"role": session.get('role'), "user_agent": user_agent})
                        except Exception as e:
                            logging.error(f"Test login audit error: {e}")
                        flash('Test modu girişi', 'warning')
                        return redirect(url_for('dashboard'))
                try:
                    if not is_privileged:
                        security_record_failed_login(DB_PATH, username, max_attempts=max_attempts, lock_seconds=lock_seconds)
                except Exception as e:
                    logging.error(f"Record failed login error: {e}")
                try:
                    security_audit_log(DB_PATH, "LOGIN_FAIL_WEB", username=username, user_id=None, success=False, ip_address=client_ip, metadata={"reason": "invalid_credentials", "user_agent": user_agent})
                except Exception as e:
                    logging.error(f"Login fail audit error: {e}")
                flash('Kullanıcı adı veya parola hatalı!', 'danger')
        else:
            try:
                security_audit_log(DB_PATH, "LOGIN_ERROR_WEB", username=username, user_id=None, success=False, ip_address=client_ip, metadata={"reason": "user_manager_unavailable", "user_agent": user_agent})
            except Exception as e:
                logging.error(f"Login system error audit error: {e}")
            flash('Sistem hatası: Kullanıcı yönetimi devre dışı.', 'danger')
    return render_template('login.html')

@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    user_id = session.get('pre_2fa_user_id')
    username = session.get('pre_2fa_username')
    
    if not user_id or not username:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        code = request.form.get('code')
        backup_code = request.form.get('backup_code')
        client_ip = request.remote_addr or 'unknown'
        
        success = False
        method = "totp"
        
        if code:
            success, msg = verify_totp_code(DB_PATH, username, code)
        elif backup_code:
            success, msg = verify_backup_code(DB_PATH, username, backup_code)
            method = "backup_code"
            
        if success:
            # Login Process
            session.pop('pre_2fa_user_id', None)
            session.pop('pre_2fa_username', None)
            
            # Fetch full user details again to be safe
            user = user_manager.get_user_by_id(user_id)
            if not user:
                flash('Kullanıcı bulunamadı.', 'danger')
                return redirect(url_for('login'))

            try:
                security_reset_failed_attempts(DB_PATH, username)
            except Exception:
                pass

            session['user'] = user.get('display_name', user.get('username'))
            session['user_id'] = user.get('id')
            
            # Set Role
            try:
                conn = get_db()
                role_row = conn.execute("""
                    SELECT r.name
                    FROM roles r
                    JOIN user_roles ur ON r.id = ur.role_id
                    WHERE ur.user_id = ?
                """, (user_id,)).fetchone()
                session['role'] = role_row['name'] if role_row else 'User'
                conn.close()
            except Exception:
                session['role'] = 'User'
                
            # Set Company
            try:
                company_id = user_manager.get_user_company(user_id)
                session['company_id'] = company_id
            except Exception:
                session['company_id'] = None
                
            # Log Success
            try:
                security_audit_log(DB_PATH, "LOGIN_SUCCESS_2FA", username=username, user_id=user_id, success=True, ip_address=client_ip, metadata={"method": method})
                audit_manager.log_action(user_id=user_id, action="LOGIN_2FA", resource="web_app", details=f"User logged in via {method}", ip_address=client_ip, company_id=session.get('company_id'))
            except Exception as e:
                logging.error(f"2FA Audit error: {e}")
                
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Geçersiz kod. Lütfen tekrar deneyiniz.', 'danger')
            # Log failure
            try:
                security_audit_log(DB_PATH, "LOGIN_FAILED_2FA", username=username, user_id=user_id, success=False, ip_address=client_ip, metadata={"method": method})
            except:
                pass
            
    return render_template('verify_2fa.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        if not username:
            flash('Lütfen kullanıcı adınızı girin.', 'warning')
            return redirect(url_for('forgot_password'))
        try:
            from backend.security.core.password_reset import request_password_reset
        except Exception as e:
            logging.error(f"Password reset import error: {e}")
            flash('Şifre sıfırlama şu anda kullanılamıyor.', 'danger')
            return redirect(url_for('login'))
        try:
            ok, msg = request_password_reset(DB_PATH, username)
        except Exception as e:
            logging.error(f"Password reset request error: {e}")
            ok, msg = False, 'Sistem hatası. Lütfen daha sonra tekrar deneyin.'
        if ok:
            session['pw_reset_username'] = username
            flash(msg or 'Şifre sıfırlama kodu e-posta adresinize gönderildi.', 'success')
            return redirect(url_for('verify_reset_code'))
        flash(msg or 'Şifre sıfırlama isteği başarısız.', 'danger')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')


@app.route('/verify_reset_code', methods=['GET', 'POST'])
def verify_reset_code():
    username = session.get('pw_reset_username')
    if not username:
        flash('Şifre sıfırlama oturumu bulunamadı. Lütfen tekrar deneyin.', 'warning')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        code = (request.form.get('code') or '').strip()
        if not code:
            flash('Lütfen doğrulama kodunu girin.', 'warning')
            return redirect(url_for('verify_reset_code'))
        session['pw_reset_code'] = code
        return redirect(url_for('reset_password_web'))
    return render_template('verify_code.html')


@app.route('/reset_password', methods=['GET', 'POST'])
@require_company_context
def reset_password_web():
    username = session.get('pw_reset_username')
    code = session.get('pw_reset_code')
    if not username or not code:
        flash('Şifre sıfırlama oturumu bulunamadı. Lütfen tekrar deneyin.', 'warning')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        password = (request.form.get('password') or '').strip()
        confirm = (request.form.get('confirm_password') or '').strip()
        if not password or not confirm:
            flash('Lütfen tüm alanları doldurun.', 'warning')
            return redirect(url_for('reset_password_web'))
        if password != confirm:
            flash('Şifreler eşleşmiyor.', 'warning')
            return redirect(url_for('reset_password_web'))
        try:
            from backend.security.core.password_reset import verify_reset_code_and_change_password
        except Exception as e:
            logging.error(f"Password reset verify import error: {e}")
            flash('Şifre sıfırlama şu anda kullanılamıyor.', 'danger')
            return redirect(url_for('login'))
        try:
            ok, msg = verify_reset_code_and_change_password(DB_PATH, username, code, password)
        except Exception as e:
            logging.error(f"Password reset verify error: {e}")
            ok, msg = False, 'Sistem hatası. Lütfen daha sonra tekrar deneyin.'
        if ok:
            session.pop('pw_reset_username', None)
            session.pop('pw_reset_code', None)
            flash(msg or 'Şifreniz başarıyla değiştirildi.', 'success')
            return redirect(url_for('login'))
        flash(msg or 'Şifre sıfırlama işlemi başarısız.', 'danger')
        return redirect(url_for('reset_password_web'))
    return render_template('reset_password.html')

from backend.core.reporting_journey_manager import ReportingJourneyManager

@app.route('/journey')
@require_company_context
def reporting_journey():
    """Sürdürülebilirlik Raporlama Yolculuğu Ana Sayfası"""
    if 'user' not in session:
        return redirect(url_for('login'))
        
    company_id = g.company_id
    manager = ReportingJourneyManager()
    journey = manager.get_journey_status(company_id)
    
    return render_template('reporting_journey.html', journey=journey)

@app.route('/journey/complete/<int:step_number>', methods=['POST'])
@require_company_context
def complete_journey_step(step_number):
    """Adımı tamamla"""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    company_id = g.company_id
    manager = ReportingJourneyManager()
    success = manager.mark_step_completed(company_id, step_number)
    
    return jsonify({'success': success})

@app.route('/analysis')
@require_company_context
def analysis():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    
    stats = {}
    records = []
    columns = ['topic_name', 'stakeholder_priority', 'business_impact', 'materiality_level', 'quadrant']
    
    try:
        from backend.modules.analytics.advanced_materiality_analyzer import AdvancedMaterialityAnalyzer
        analyzer = AdvancedMaterialityAnalyzer(DB_PATH)
        summary = analyzer.get_materiality_summary(company_id)
        
        stats = {
            'toplam_konu': summary.get('total_topics', 0),
            'yuksek_oncelik': summary.get('high_materiality_count', 0),
            'orta_oncelik': summary.get('medium_materiality_count', 0),
            'dusuk_oncelik': summary.get('low_materiality_count', 0)
        }
        
        records = summary.get('matrix_data', [])
        
    except Exception as e:
        logging.error(f"Materiality analysis error: {e}")
        
    return render_template('analysis.html', title='Materialite Analizi', stats=stats, records=records, columns=columns, manager_available=True)

@app.route('/dashboard')
@require_company_context
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    stats: Dict[str, int] = {}
    try:
        conn = get_db()
        # Filter by company_id
        stats['user_count'] = conn.execute('SELECT COUNT(*) FROM users WHERE company_id=?', (g.company_id,)).fetchone()[0]
        try:
            # Users only see their own company
            stats['company_count'] = conn.execute('SELECT COUNT(*) FROM companies WHERE id=?', (g.company_id,)).fetchone()[0]
        except Exception:
            stats['company_count'] = 1
        try:
            stats['report_count'] = conn.execute('SELECT COUNT(*) FROM report_registry WHERE company_id=?', (g.company_id,)).fetchone()[0]
        except Exception:
            stats['report_count'] = 0
        try:
            data_count = 0
            for t in ['carbon_emissions', 'energy_consumption', 'water_consumption', 'waste_generation']:
                try:
                    # Check if table exists and has company_id
                    cur = conn.execute(f"PRAGMA table_info({t})")
                    cols = [c[1] for c in cur.fetchall()]
                    if 'company_id' in cols:
                        data_count += conn.execute(f'SELECT COUNT(*) FROM {t} WHERE company_id=?', (g.company_id,)).fetchone()[0]
                except Exception:
                    pass
            stats['data_count'] = data_count
        except Exception:
            stats['data_count'] = 0
        conn.close()
    except Exception as e:
        logging.error(f"Dashboard stats error: {e}")

    # Anket İstatistikleri
    try:
        conn = get_db()
        try:
            # Use online_surveys table instead of legacy surveys table
            # Check if company_id exists in online_surveys (it should)
            cur = conn.execute("SELECT COUNT(*) FROM online_surveys WHERE is_active=1 AND company_id=?", (g.company_id,))
            stats['active_surveys'] = cur.fetchone()[0]
        except Exception:
            stats['active_surveys'] = 0
            
        try:
            # response_count column stores unique respondents count per survey
            cur = conn.execute("SELECT SUM(response_count) FROM online_surveys WHERE company_id=?", (g.company_id,))
            res = cur.fetchone()[0]
            stats['total_responses'] = res if res else 0
        except Exception:
            stats['total_responses'] = 0
        conn.close()
    except Exception as e:
        logging.error(f"Dashboard survey stats error: {e}")
        stats['active_surveys'] = 0
        stats['total_responses'] = 0

    # Yeni Modül Verileri: Çifte Önemlilik ve ESRS
    top_material_topics = []
    esrs_stats = {'completion_rate': 0}
    try:
        from backend.modules.prioritization.prioritization_manager import PrioritizationManager
        pm = PrioritizationManager(DB_PATH)
        # get_materiality_topics zaten puana göre sıralı geliyor
        all_topics = pm.get_materiality_topics(g.company_id)
        top_material_topics = all_topics[:5] if all_topics else []
    except Exception as e:
        logging.error(f"Dashboard prioritization data error: {e}")

    try:
        from backend.modules.esrs.esrs_manager import ESRSManager
        em = ESRSManager(DB_PATH)
        esrs_stats = em.get_dashboard_stats(g.company_id)
    except Exception as e:
        logging.error(f"Dashboard ESRS data error: {e}")

    # Module Completion Stats (Item 6)
    module_stats = {}
    try:
        from backend.modules.dashboard_stats import DashboardStatsManager
        dsm = DashboardStatsManager(DB_PATH)
        module_stats = dsm.get_module_stats(g.company_id)
    except Exception as e:
        logging.error(f"Dashboard module stats error: {e}")
    
    try:
        return render_template('dashboard.html', stats=stats, top_material_topics=top_material_topics, esrs_stats=esrs_stats, module_stats=module_stats)
    except Exception as e:
        import traceback
        logging.error(f"Template rendering error: {traceback.format_exc()}")
        return f"Template Error: {e}", 500


@app.route('/super_admin')
@super_admin_required
@require_company_context
def super_admin_panel():
    if 'user' not in session:
        return redirect(url_for('login'))
    stats: Dict[str, int] = {}
    try:
        conn = get_db()
        try:
            stats['user_count'] = conn.execute('SELECT COUNT(*) FROM users WHERE company_id = ?', (g.company_id,)).fetchone()[0]
        except Exception:
            stats['user_count'] = 0
        try:
            stats['company_count'] = conn.execute('SELECT COUNT(*) FROM companies WHERE id = ?', (g.company_id,)).fetchone()[0]
        except Exception:
            stats['company_count'] = 0
        try:
            stats['report_count'] = conn.execute('SELECT COUNT(*) FROM report_registry WHERE company_id = ?', (g.company_id,)).fetchone()[0]
        except Exception:
            stats['report_count'] = 0
        conn.close()
    except Exception as e:
        logging.error(f"Super admin stats error: {e}")
    rate_stats = []
    try:
        if hasattr(rate_limiter, 'get_rate_limit_stats'):
            rate_stats = rate_limiter.get_rate_limit_stats()
    except Exception as e:
        logging.error(f"Rate limit stats error: {e}")
    ip_available = IP_MANAGER_AVAILABLE
    monitoring_available = MONITORING_AVAILABLE
    license_available = LICENSE_MANAGER_AVAILABLE
    return render_template(
        'super_admin.html',
        title=_('admin_panel', 'Super Admin Paneli'),
        stats=stats,
        rate_stats=rate_stats,
        ip_available=ip_available,
        monitoring_available=monitoring_available,
        license_available=license_available
    )


@app.route('/super_admin/system_stats')
@super_admin_required
@require_company_context
def super_admin_system_stats():
    if 'user' not in session:
        return redirect(url_for('login'))
    stats: Dict[str, int] = {}
    try:
        conn = get_db()
        try:
            stats['table_count'] = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()[0]
        except Exception:
            stats['table_count'] = 0
        try:
            stats['user_count'] = conn.execute(
                "SELECT COUNT(*) FROM users WHERE company_id = ?", (g.company_id,)
            ).fetchone()[0]
        except Exception:
            stats['user_count'] = 0
        company_count = 0
        try:
            company_count = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE id = ?", (g.company_id,)
            ).fetchone()[0]
        except Exception:
            try:
                company_count = conn.execute(
                    "SELECT COUNT(*) FROM company_info WHERE company_id = ?", (g.company_id,)
                ).fetchone()[0]
            except Exception:
                company_count = 0
        stats['company_count'] = company_count
        conn.close()
    except Exception as e:
        logging.error(f"Super admin system stats error: {e}")
    return render_template(
        'super_admin_system_stats.html',
        title=_('system_stats_title', 'Sistem İstatistikleri'),
        stats=stats
    )


@app.route('/super_admin/audit_logs')
@super_admin_required
@require_company_context
def super_admin_audit_logs():
    if 'user' not in session:
        return redirect(url_for('login'))
    logs: list[Dict[str, str]] = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username VARCHAR(50),
                action VARCHAR(100),
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45)
            )
        """)
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'username' not in columns:
            try:
                cursor.execute("ALTER TABLE audit_logs ADD COLUMN username VARCHAR(50)")
                conn.commit()
            except Exception as e:
                logging.error(f"Audit logs username column alter error: {e}")
        def fetch_from_audit_logs(cur: sqlite3.Cursor):
            cols: list[str] = []
            try:
                cur.execute("PRAGMA table_info(audit_logs)")
                cols = [c[1] for c in cur.fetchall()]
            except Exception as e:
                logging.error(f"Audit logs pragma error: {e}")
            ts_col = 'timestamp' if 'timestamp' in cols else (
                'created_at' if 'created_at' in cols else ('ts' if 'ts' in cols else None)
            )
            det_col = 'details' if 'details' in cols else (
                'payload_json' if 'payload_json' in cols else ('metadata' if 'metadata' in cols else "''")
            )
            if ts_col is None:
                ts_expr = "datetime('now')"
            else:
                ts_expr = f"COALESCE(a.{ts_col}, datetime('now'))"
            det_expr = f"COALESCE(a.{det_col}, '')" if det_col != "''" else "''"
            query = f"""
                SELECT a.id,
                       COALESCE(a.username, u.username, 'Sistem') as username,
                       a.action,
                       {ts_expr} as ts,
                       {det_expr} as details
                FROM audit_logs a
                LEFT JOIN users u ON a.user_id = u.id
                WHERE u.company_id = ?
                ORDER BY a.id DESC
                LIMIT 1000
            """
            cur.execute(query, (g.company_id,))
            return cur.fetchall()
        def fetch_from_security_logs(cur: sqlite3.Cursor):
            cols: list[str] = []
            try:
                cur.execute("PRAGMA table_info(security_logs)")
                cols = [c[1] for c in cur.fetchall()]
            except Exception as e:
                logging.error(f"Security logs pragma error: {e}")
            ts_col = 'created_at' if 'created_at' in cols else (
                'timestamp' if 'timestamp' in cols else None
            )
            det_col = 'details' if 'details' in cols else (
                'metadata' if 'metadata' in cols else "''"
            )
            ts_expr = f"COALESCE({ts_col}, datetime('now'))" if ts_col else "datetime('now')"
            det_expr = f"COALESCE({det_col}, '')" if det_col != "''" else "''"
            if 'username' in cols:
                user_expr = 'username'
            elif 'user_id' in cols:
                user_expr = "COALESCE((SELECT username FROM users WHERE id = user_id), 'Sistem')"
            else:
                user_expr = "'Sistem'"
            if 'action' in cols:
                action_col = 'action'
            elif 'event_type' in cols:
                action_col = 'event_type'
            else:
                return []
            
            # Enforce company isolation for security logs if possible
            where_clause = ""
            params = []
            if 'user_id' in cols:
                 where_clause = "WHERE user_id IN (SELECT id FROM users WHERE company_id = ?)"
                 params.append(g.company_id)
            elif 'company_id' in cols:
                 where_clause = "WHERE company_id = ?"
                 params.append(g.company_id)

            query = f"""
                SELECT id,
                       {user_expr} as username,
                       {action_col} as action,
                       {ts_expr} as ts,
                       {det_expr} as details
                FROM security_logs
                {where_clause}
                ORDER BY id DESC
                LIMIT 1000
            """
            cur.execute(query, params)
            return cur.fetchall()
        rows_a = []
        try:
            # Directly fetch with isolation (no global count check)
            rows_a = fetch_from_audit_logs(cursor)
        except Exception as e:
            logging.error(f"Error fetching audit logs: {e}")
            rows_a = []

        rows_s = []
        try:
            # Directly fetch with isolation (no global count check)
            rows_s = fetch_from_security_logs(cursor)
        except Exception as e:
            logging.error(f"Error fetching security logs: {e}")
            rows_s = []

        # Combine and sort
        all_rows = rows_a + rows_s
        # Sort by timestamp (index 3) descending
        all_rows.sort(key=lambda x: x[3] if x[3] else '', reverse=True)
        rows = all_rows[:1000]

        for row in rows:
            log_id, username, action, timestamp, details = row
            text = details or 'Detay yok'
            if text and len(text) > 80:
                text_short = text[:80] + '...'
            else:
                text_short = text
            logs.append({
                'id': log_id,
                'username': username or 'Sistem',
                'action': action or 'Bilinmiyor',
                'timestamp': timestamp or '',
                'details': text_short
            })
        try:
            conn.commit()
        except Exception as e:
            logging.error(f"Audit logs commit error: {e}")
        conn.close()
    except Exception as e:
        logging.error(f"Super admin audit logs error: {e}")
    return render_template(
        'super_admin_audit_logs.html',
        title=_('audit_logs_title', 'Audit Logları'),
        logs=logs
    )


@app.route('/super_admin/backup', methods=['GET', 'POST'])
@super_admin_required
def super_admin_backup():
    if 'user' not in session:
        return redirect(url_for('login'))
    backup_dir = os.path.join(BACKEND_DIR, 'data', 'backups')
    manager = BackupRecoveryManager(DB_PATH, backup_dir=backup_dir)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            backup_type = request.form.get('backup_type') or 'full'
            include_files = True
            if backup_type == 'database_only':
                include_files = False
            if backup_type == 'files_only':
                include_files = True
            try:
                created_by = session.get('user', 'web_superadmin')
                ok, info = manager.create_backup(backup_type=backup_type, created_by=created_by, include_files=include_files)
                if ok:
                    flash('Yedekleme başarıyla oluşturuldu.', 'success')
                else:
                    flash(info or 'Yedekleme oluşturulamadı.', 'danger')
            except Exception as e:
                logging.error(f"Backup create error: {e}")
                flash(f'Yedekleme sırasında hata oluştu: {e}', 'danger')
        elif action == 'restore':
            backup_id_raw = request.form.get('backup_id') or ''
            try:
                backup_id = int(backup_id_raw)
            except Exception:
                backup_id = 0
            if not backup_id:
                flash('Lütfen geri yüklenecek bir yedek seçin.', 'warning')
            else:
                backups = manager.get_backup_list(200)
                backup_path = None
                for b in backups:
                    if b.get('id') == backup_id:
                        backup_path = b.get('path')
                        break
                if not backup_path:
                    flash('Seçilen yedek bulunamadı.', 'danger')
                else:
                    try:
                        restored_by = session.get('user', 'web_superadmin')
                        ok, msg = manager.restore_backup(backup_path, restored_by=restored_by)
                        if ok:
                            flash(msg or 'Yedek başarıyla geri yüklendi.', 'success')
                        else:
                            flash(msg or 'Yedek geri yüklenemedi.', 'danger')
                    except Exception as e:
                        logging.error(f"Backup restore error: {e}")
                        flash(f'Yedek geri yükleme sırasında hata oluştu: {e}', 'danger')
        elif action == 'save_config':
            config = manager.get_backup_config()
            auto_enabled = request.form.get('auto_backup_enabled') == '1'
            freq = request.form.get('backup_frequency') or config.get('backup_frequency', 'daily')
            time_str = request.form.get('backup_time') or config.get('backup_time', '02:00')
            max_backups_raw = request.form.get('max_backups') or str(config.get('max_backups', 30))
            try:
                max_backups = int(max_backups_raw)
                if max_backups <= 0:
                    max_backups = 30
            except Exception:
                max_backups = config.get('max_backups', 30)
            new_config = dict(config)
            new_config['auto_backup_enabled'] = auto_enabled
            new_config['backup_frequency'] = freq
            new_config['backup_time'] = time_str
            new_config['max_backups'] = max_backups
            updated = manager.update_backup_config(new_config)
            if updated:
                flash('Yedekleme ayarları güncellendi.', 'success')
            else:
                flash('Yedekleme ayarları kaydedilemedi.', 'danger')
        return redirect(url_for('super_admin_backup'))
    stats = {}
    try:
        stats = manager.get_backup_statistics()
    except Exception as e:
        logging.error(f"Backup stats error: {e}")
    config = {}
    try:
        config = manager.get_backup_config()
    except Exception as e:
        logging.error(f"Backup config load error: {e}")
    backups = []
    try:
        backups = manager.get_backup_list(50)
    except Exception as e:
        logging.error(f"Backup list error: {e}")
    return render_template(
        'super_admin_backup.html',
        title='Yedekleme ve Geri Yükleme',
        stats=stats,
        config=config,
        backups=backups
    )


@app.route('/super_admin/backup/download/<int:backup_id>')
@super_admin_required
def super_admin_backup_download(backup_id: int):
    if 'user' not in session:
        return redirect(url_for('login'))
    backup_dir = os.path.join(BACKEND_DIR, 'data', 'backups')
    manager = BackupRecoveryManager(DB_PATH, backup_dir=backup_dir)
    backups = []
    try:
        backups = manager.get_backup_list(200)
    except Exception as e:
        logging.error(f"Backup download list error: {e}")
    backup_path = None
    for b in backups:
        if b.get('id') == backup_id:
            backup_path = b.get('path')
            break
    if not backup_path or not os.path.exists(backup_path):
        flash('Yedek dosyası bulunamadı.', 'danger')
        return redirect(url_for('super_admin_backup'))
    try:
        filename = os.path.basename(backup_path)
        return send_file(backup_path, as_attachment=True, download_name=filename)
    except Exception as e:
        logging.error(f"Backup download error: {e}")
        flash('Yedek dosyası indirilemedi.', 'danger')
        return redirect(url_for('super_admin_backup'))


@app.route('/super_admin/2fa', methods=['GET', 'POST'])
@super_admin_required
def super_admin_twofa():
    if 'user' not in session:
        return redirect(url_for('login'))
    users = []
    try:
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, username, display_name FROM users ORDER BY username")
            rows = cur.fetchall()
            for row in rows:
                users.append(
                    {
                        "id": row["id"],
                        "username": row["username"],
                        "display_name": row["display_name"] or row["username"],
                    }
                )
        except Exception as e:
            logging.error(f"2FA user list error: {e}")
        conn.close()
    except Exception as e:
        logging.error(f"2FA user connection error: {e}")
    selected_username = None
    if request.method == "POST":
        selected_username = request.form.get("username") or None
    else:
        selected_username = request.args.get("username") or None
    if not selected_username and users:
        selected_username = users[0]["username"]
    backup_codes = []
    qr_data_uri = None
    force_2fa = False
    status_text = None
    if request.method == "POST":
        action = request.form.get("action")
        if not selected_username:
            flash("Önce bir kullanıcı seçin.", "danger")
        else:
            try:
                if action == "enable":
                    ok, msg, secret, qr_bytes = enable_totp_for_user(DB_PATH, selected_username)
                    if ok:
                        try:
                            qr_b64 = base64.b64encode(qr_bytes).decode("ascii")
                            qr_data_uri = "data:image/png;base64," + qr_b64
                        except Exception as e:
                            logging.error(f"2FA QR encode error: {e}")
                        ok_codes, msg_codes, codes = regenerate_backup_codes(DB_PATH, selected_username)
                        if ok_codes:
                            backup_codes = codes
                        flash("2FA etkinleştirildi.", "success")
                    else:
                        flash(msg or "2FA etkinleştirilemedi.", "danger")
                elif action == "disable":
                    ok, msg = twofa_disable(DB_PATH, selected_username)
                    if ok:
                        flash("2FA devre dışı bırakıldı.", "success")
                    else:
                        flash(msg or "2FA devre dışı bırakılamadı.", "danger")
                elif action == "show_codes":
                    ok, msg, codes = get_backup_codes(DB_PATH, selected_username)
                    if ok:
                        backup_codes = codes
                        flash("Yedek kodlar oluşturuldu.", "success")
                    else:
                        flash(msg or "Yedek kodlar alınamadı.", "danger")
                elif action == "regen_codes":
                    ok, msg, codes = regenerate_backup_codes(DB_PATH, selected_username)
                    if ok:
                        backup_codes = codes
                        flash("Yedek kodlar yenilendi.", "success")
                    else:
                        flash(msg or "Yedek kodlar yenilenemedi.", "danger")
                elif action == "save_force":
                    value = request.form.get("force_2fa") == "1"
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        core_set_force_2fa(conn, bool(value))
                        force_2fa = core_is_force_2fa(conn)
                        conn.close()
                        flash("Zorunlu 2FA ayarı güncellendi.", "success")
                    except Exception as e:
                        logging.error(f"Force 2FA save error: {e}")
                        flash("Zorunlu 2FA ayarı kaydedilemedi.", "danger")
            except Exception as e:
                logging.error(f"2FA management error: {e}")
                flash(f"2FA işlemi sırasında hata: {e}", "danger")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(users)")
        cols = [c[1] for c in cur.fetchall()]
        if selected_username and "totp_enabled" in cols:
            cur.execute("SELECT totp_enabled FROM users WHERE username=?", (selected_username,))
            row = cur.fetchone()
            if row is not None:
                status_text = "Aktif" if int(row[0] or 0) == 1 else "Pasif"
        if not force_2fa:
            try:
                force_2fa = core_is_force_2fa(conn)
            except Exception as e:
                logging.error(f"Force 2FA read error: {e}")
        conn.close()
    except Exception as e:
        logging.error(f"2FA status load error: {e}")
    return render_template(
        "super_admin_2fa.html",
        title="2FA Yönetimi",
        users=users,
        selected_username=selected_username,
        status_text=status_text,
        backup_codes=backup_codes,
        qr_data_uri=qr_data_uri,
        force_2fa=force_2fa,
    )


@app.route('/super_admin/ip', methods=['GET', 'POST'])
@super_admin_required
def super_admin_ip():
    if 'user' not in session:
        return redirect(url_for('login'))
    if not IP_MANAGER_AVAILABLE:
        flash('IP yönetim bileşeni yüklenemedi.', 'danger')
        return redirect(url_for('super_admin_panel'))
    manager = IPManager(DB_PATH)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_whitelist':
            ip_address = request.form.get('ip_address', '').strip()
            description = request.form.get('description', '').strip()
            if not ip_address:
                flash('IP adresi gerekli.', 'danger')
            else:
                result = manager.add_to_whitelist(ip_address, description, session.get('user', 'admin'))
                if result.get('success'):
                    flash(result.get('message', ''), 'success')
                else:
                    flash(result.get('message', ''), 'danger')
        elif action == 'remove_whitelist':
            ip_address = request.form.get('ip_address', '').strip()
            if ip_address and manager.remove_from_whitelist(ip_address):
                flash('IP whitelist listesinden kaldırıldı.', 'success')
            else:
                flash('IP whitelist listesinden kaldırılamadı.', 'danger')
        elif action == 'add_blacklist':
            ip_address = request.form.get('ip_address', '').strip()
            reason = request.form.get('reason', '').strip() or 'manual'
            duration = request.form.get('duration', 'permanent')
            if not ip_address:
                flash('IP adresi gerekli.', 'danger')
            else:
                duration_minutes = None
                if duration != 'permanent':
                    try:
                        duration_minutes = int(duration)
                    except Exception:
                        duration_minutes = None
                result = manager.add_to_blacklist(ip_address, reason, session.get('user', 'admin'), 'manual', duration_minutes)
                if result.get('success'):
                    flash(result.get('message', ''), 'success')
                else:
                    flash(result.get('message', ''), 'danger')
        elif action == 'remove_blacklist':
            ip_address = request.form.get('ip_address', '').strip()
            if ip_address and manager.remove_from_blacklist(ip_address):
                flash('IP blacklist listesinden kaldırıldı.', 'success')
            else:
                flash('IP blacklist listesinden kaldırılamadı.', 'danger')
        return redirect(url_for('super_admin_ip'))
    whitelist = manager.get_whitelist()
    blacklist = manager.get_blacklist()
    stats = manager.get_ip_statistics()
    return render_template(
        'super_admin_ip.html',
        title='IP Kontrolü',
        whitelist=whitelist,
        blacklist=blacklist,
        stats=stats
    )


@app.route('/super_admin/rate', methods=['GET', 'POST'])
@super_admin_required
@require_company_context
def super_admin_rate():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    company_id = g.company_id
    
    if not hasattr(rate_limiter, 'get_rate_limit_stats'):
        flash('Rate limiting bileşeni yüklenemedi.', 'danger')
        return redirect(url_for('super_admin_panel'))
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'cleanup':
            try:
                deleted = rate_limiter.cleanup_old_records(24)
                flash(f'{deleted} eski kayıt temizlendi.', 'success')
            except Exception as e:
                logging.error(f"Rate cleanup error: {e}")
                flash('Kayıtlar temizlenirken hata oluştu.', 'danger')
        elif action == 'save_rules':
            keys = ['rl_login_limit', 'rl_login_window', 'rl_api_limit', 'rl_api_window', 'rl_report_limit', 'rl_report_window', 'rl_export_limit', 'rl_export_window']
            values = {}
            for k in keys:
                values[k] = request.form.get(k, '').strip()
            try:
                import sqlite3
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_settings (
                        key TEXT,
                        value TEXT,
                        category TEXT,
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        company_id INTEGER,
                        PRIMARY KEY (key, company_id)
                    )
                    """
                )
                for k, val in values.items():
                    if k.endswith('_limit') or k.endswith('_window'):
                        if val and not str(val).isdigit():
                            conn.close()
                            flash(f"Geçersiz sayı: {k} = {val}", 'danger')
                            return redirect(url_for('super_admin_rate'))
                    cur.execute(
                        """
                        INSERT INTO system_settings (key, value, category, description, company_id)
                        VALUES (?, ?, 'rate_limit', 'Rate limit ayarı', ?)
                        ON CONFLICT(key, company_id) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
                        """,
                        (k, val, company_id),
                    )
                conn.commit()
                conn.close()
                flash('Rate limit kuralları güncellendi.', 'success')
            except Exception as e:
                logging.error(f"Save rate rules error: {e}")
                flash('Rate limit kuralları kaydedilemedi.', 'danger')
        return redirect(url_for('super_admin_rate'))
    stats = []
    try:
        stats = rate_limiter.get_rate_limit_stats()
    except Exception as e:
        logging.error(f"Get rate stats error: {e}")
    current_rules = {}
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT,
                value TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER,
                PRIMARY KEY (key, company_id)
            )
            """
        )
        keys = ['rl_login_limit', 'rl_login_window', 'rl_api_limit', 'rl_api_window', 'rl_report_limit', 'rl_report_window', 'rl_export_limit', 'rl_export_window']
        for k in keys:
            cur.execute("SELECT value FROM system_settings WHERE key=? AND company_id=?", (k, company_id))
            row = cur.fetchone()
            if row and row[0] is not None:
                current_rules[k] = str(row[0])
            else:
                current_rules[k] = ''
        conn.close()
    except Exception as e:
        logging.error(f"Load rate rules error: {e}")
    return render_template(
        'super_admin_rate.html',
        title='Rate Limiting',
        rate_stats=stats,
        current_rules=current_rules
    )


@app.route('/super_admin/monitoring')
@super_admin_required
def super_admin_monitoring():
    if 'user' not in session:
        return redirect(url_for('login'))
    if not MONITORING_AVAILABLE:
        flash('Monitoring bileşeni yüklenemedi.', 'danger')
        return redirect(url_for('super_admin_panel'))
    dashboard = MonitoringDashboard(DB_PATH)
    live_stats = dashboard.get_live_stats()
    events = dashboard.get_recent_events(50)
    login_activity = dashboard.get_chart_data('login_activity', 24)
    failed_logins = dashboard.get_chart_data('failed_logins', 24)
    return render_template(
        'super_admin_monitoring.html',
        title='Monitoring Dashboard',
        live_stats=live_stats,
        events=events,
        login_activity=login_activity,
        failed_logins=failed_logins
    )


@app.route('/super_admin/performance', methods=['GET', 'POST'])
@super_admin_required
@require_company_context
def super_admin_performance():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    company_id = g.company_id
    
    performance_keys = [
        'perf_list_page_size',
        'perf_dashboard_limit',
        'perf_enable_caching'
    ]
    current_settings: Dict[str, str] = {}
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'save_settings':
            values: Dict[str, str] = {}
            for k in performance_keys:
                values[k] = request.form.get(k, '').strip()
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_settings (
                        key TEXT,
                        value TEXT,
                        category TEXT,
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        company_id INTEGER,
                        PRIMARY KEY (key, company_id)
                    )
                    """
                )
                for k, val in values.items():
                    if k in ('perf_list_page_size', 'perf_dashboard_limit'):
                        if val and not str(val).isdigit():
                            conn.close()
                            flash(f"Geçersiz sayı: {k} = {val}", "danger")
                            return redirect(url_for('super_admin_performance'))
                    cur.execute(
                        """
                        INSERT INTO system_settings (key, value, category, description, company_id)
                        VALUES (?, ?, 'performance', 'Performans ayarı', ?)
                        ON CONFLICT(key, company_id) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
                        """,
                        (k, val, company_id),
                    )
                conn.commit()
                conn.close()
                flash("Performans ayarları güncellendi.", "success")
            except Exception as e:
                logging.error(f"Save performance settings error: {e}")
                flash("Performans ayarları kaydedilemedi.", "danger")
        return redirect(url_for('super_admin_performance'))
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT,
                value TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER,
                PRIMARY KEY (key, company_id)
            )
            """
        )
        for k in performance_keys:
            cur.execute("SELECT value FROM system_settings WHERE key=? AND company_id=?", (k, company_id))
            row = cur.fetchone()
            if row and row[0] is not None:
                current_settings[k] = str(row[0])
            else:
                # No fallback to company_id=1. Strict isolation.
                current_settings[k] = ''
        conn.close()
    except Exception as e:
        logging.error(f"Load performance settings error: {e}")
    metrics: Dict[str, object] = {
        'db_size_mb': 0.0,
        'table_count': 0,
        'index_count': 0,
        'total_records': 0,
        'table_stats': []
    }
    try:
        if os.path.exists(DB_PATH):
            db_size = os.path.getsize(DB_PATH)
            metrics['db_size_mb'] = round(db_size / (1024 * 1024), 2)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        metrics['table_count'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
        metrics['index_count'] = cur.fetchone()[0]
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [r[0] for r in cur.fetchall()]
        table_stats = []
        total_records = 0
        for name in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {name}")
                count = cur.fetchone()[0]
                total_records += count
                table_stats.append({'name': name, 'rows': count})
            except Exception:
                continue
        table_stats.sort(key=lambda x: x['rows'], reverse=True)
        metrics['total_records'] = total_records
        metrics['table_stats'] = table_stats[:20]
        conn.close()
    except Exception as e:
        logging.error(f"Performance metrics error: {e}")
    return render_template(
        'super_admin_performance.html',
        title='Performans Dashboard',
        settings=current_settings,
        metrics=metrics
    )


@app.route('/super_admin/licenses', methods=['GET', 'POST'])
@super_admin_required
def super_admin_licenses():
    if 'user' not in session:
        return redirect(url_for('login'))
    if not LICENSE_MANAGER_AVAILABLE:
        flash('Lisans bileşeni yüklenemedi.', 'danger')
        return redirect(url_for('super_admin_panel'))
    manager = LicenseGenerator(DB_PATH)
    validation_result = None
    generated_result = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'generate':
            company_name = request.form.get('company_name', '').strip()
            license_type = request.form.get('license_type', '').strip() or 'standard'
            duration_days = int(request.form.get('duration_days') or 0)
            max_users = int(request.form.get('max_users') or 0)
            modules_raw = request.form.get('modules', '').strip()
            modules = []
            if modules_raw:
                modules = [m.strip() for m in modules_raw.split(',') if m.strip()]
            contact_email = request.form.get('contact_email', '').strip() or None
            contact_phone = request.form.get('contact_phone', '').strip() or None
            result = manager.generate_license_key(
                company_name,
                license_type,
                duration_days,
                max_users,
                modules,
                None,
                contact_email,
                contact_phone
            )
            generated_result = result
            if result.get('success'):
                flash('Lisans anahtarı oluşturuldu.', 'success')
            else:
                flash(result.get('message', ''), 'danger')
        elif action == 'deactivate':
            license_id = int(request.form.get('license_id') or 0)
            reason = request.form.get('reason', '').strip()
            if license_id and manager.deactivate_license(license_id, reason):
                flash('Lisans devre dışı bırakıldı.', 'success')
            else:
                flash('Lisans devre dışı bırakılamadı.', 'danger')
        elif action == 'renew':
            license_id = int(request.form.get('license_id') or 0)
            additional_days = int(request.form.get('additional_days') or 0)
            if license_id and additional_days > 0 and manager.renew_license(license_id, additional_days):
                flash('Lisans süresi uzatıldı.', 'success')
            else:
                flash('Lisans süresi uzatılamadı.', 'danger')
        elif action == 'validate':
            license_key = request.form.get('license_key', '').strip()
            hw_id = request.form.get('hardware_id', '').strip() or None
            if license_key:
                validation_result = manager.validate_license(license_key, hw_id)
                if validation_result.get('valid'):
                    flash('Lisans geçerli.', 'success')
                else:
                    flash(validation_result.get('message', ''), 'danger')
        return redirect(url_for('super_admin_licenses'))
    licenses = manager.get_all_licenses()
    stats = manager.get_license_statistics()
    return render_template(
        'super_admin_licenses.html',
        title='Lisans Yönetimi',
        licenses=licenses,
        stats=stats,
        validation_result=validation_result,
        generated_result=generated_result
    )


@app.route('/super_admin/system_logs')
@super_admin_required
@require_company_context
def super_admin_system_logs():
    if 'user' not in session:
        return redirect(url_for('login'))
    logs: list[Dict[str, str]] = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        def table_exists(cursor: sqlite3.Cursor, name: str) -> bool:
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
                return cursor.fetchone() is not None
            except Exception:
                return False

        has_system = table_exists(cur, 'system_logs')
        has_audit = table_exists(cur, 'audit_logs')
        has_security = table_exists(cur, 'security_logs')

        if has_system:
            try:
                cur.execute(
                    """
                    SELECT s.created_at, s.level, s.user_id, s.module, s.message
                    FROM system_logs s
                    LEFT JOIN users u ON s.user_id = u.id
                    WHERE u.company_id = ?
                    ORDER BY s.created_at DESC
                    LIMIT 200
                    """, (g.company_id,)
                )
                rows = cur.fetchall()
                for ts, level, user_id, module, message in rows:
                    timestamp = str(ts or '')
                    level_text = (level or 'INFO').upper()
                    user_text = str(user_id or 'sistem')
                    module_text = module or 'Sistem'
                    msg_text = message or ''
                    logs.append(
                        {
                            'timestamp': timestamp,
                            'level': level_text,
                            'user': user_text,
                            'module': module_text,
                            'message': msg_text,
                        }
                    )
            except Exception as e:
                logging.error(f"System logs query error: {e}")
        
        if has_audit:
            try:
                cur.execute(
                    """
                    SELECT a.created_at, a.level, a.user_id, a.module, COALESCE(a.message, a.action) as msg
                    FROM audit_logs a
                    LEFT JOIN users u ON a.user_id = u.id
                    WHERE u.company_id = ?
                    ORDER BY a.created_at DESC
                    LIMIT 200
                    """, (g.company_id,)
                )
                rows = cur.fetchall()
                for ts, level, user_id, module, message in rows:
                    timestamp = str(ts or '')
                    level_text = (level or 'INFO').upper()
                    user_text = str(user_id or 'sistem')
                    module_text = module or 'Audit'
                    msg_text = message or ''
                    logs.append(
                        {
                            'timestamp': timestamp,
                            'level': level_text,
                            'user': user_text,
                            'module': module_text,
                            'message': msg_text,
                        }
                    )
            except Exception as e:
                logging.error(f"Audit logs for system logs error: {e}")

        if has_security:
            try:
                # Check for available columns to filter securely
                cur.execute("PRAGMA table_info(security_logs)")
                cols = [c[1] for c in cur.fetchall()]
                
                where_clause = "WHERE 0=1" # Default safe
                params = []
                
                if 'company_id' in cols:
                    where_clause = "WHERE company_id = ?"
                    params.append(g.company_id)
                elif 'user_id' in cols:
                    where_clause = "WHERE user_id IN (SELECT id FROM users WHERE company_id = ?)"
                    params.append(g.company_id)
                
                query = f"""
                    SELECT created_at, username, event_type, action, success, details
                    FROM security_logs
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT 200
                """
                cur.execute(query, params)
                rows = cur.fetchall()
                for ts, username, event_type, action, success, details in rows:
                    timestamp = str(ts or '')
                    level_text = 'INFO' if success else 'WARN'
                    user_text = str(username or 'sistem')
                    module_text = 'Security'
                    msg_text = f"{event_type}: {action} ({details})"
                    logs.append(
                        {
                            'timestamp': timestamp,
                            'level': level_text,
                            'user': user_text,
                            'module': module_text,
                            'message': msg_text,
                        }
                    )
            except Exception as e:
                logging.error(f"Security logs for system logs error: {e}")
        conn.close()
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        logs = logs[:300]
    except Exception as e:
        logging.error(f"Super admin system logs error: {e}")
    return render_template(
        'super_admin_system_logs.html',
        title='Sistem Logları',
        logs=logs,
    )


@app.route('/super_admin/settings', methods=['GET', 'POST'])
@super_admin_required
@require_company_context
def super_admin_settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    company_id = g.company_id
    
    setting_keys = [
        'app_name',
        'default_language',
        'support_email',
        'auto_backup_enabled',
        'auto_backup_hour',
        'log_level'
    ]
    boolean_keys = {'auto_backup_enabled'}
    current_settings: Dict[str, str] = {}
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'save_settings':
            values: Dict[str, str] = {}
            for k in setting_keys:
                if k in boolean_keys:
                    values[k] = '1' if request.form.get(k) == '1' else '0'
                else:
                    values[k] = (request.form.get(k) or '').strip()
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_settings (
                        key TEXT,
                        value TEXT,
                        category TEXT,
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        company_id INTEGER,
                        PRIMARY KEY (key, company_id)
                    )
                    """
                )
                for k, val in values.items():
                    cur.execute(
                        """
                        INSERT INTO system_settings (key, value, category, description, company_id)
                        VALUES (?, ?, 'system', 'Sistem genel ayarı', ?)
                        ON CONFLICT(key, company_id) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
                        """,
                        (k, val, company_id),
                    )
                conn.commit()
                conn.close()
                flash('Sistem ayarları güncellendi.', 'success')
            except Exception as e:
                logging.error(f"Save system settings error: {e}")
                flash('Sistem ayarları kaydedilemedi.', 'danger')
            return redirect(url_for('super_admin_settings'))
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT,
                value TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER,
                PRIMARY KEY (key, company_id)
            )
            """
        )
        for k in setting_keys:
            cur.execute("SELECT value FROM system_settings WHERE key=? AND company_id=?", (k, company_id))
            row = cur.fetchone()
            if row and row[0] is not None:
                current_settings[k] = str(row[0])
            else:
                current_settings[k] = ''
        conn.close()
    except Exception as e:
        logging.error(f"Load system settings error: {e}")
    return render_template(
        'super_admin_settings.html',
        title='Sistem Ayarları',
        settings=current_settings
    )


@app.route('/super_admin/security', methods=['GET', 'POST'])
@super_admin_required
@require_company_context
def super_admin_security():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    company_id = g.company_id
    
    setting_keys = [
        'sec_max_login_attempts',
        'sec_lockout_seconds',
        'sec_session_timeout_minutes',
        'sec_password_min_length',
        'sec_password_require_special'
    ]
    boolean_keys = {'sec_password_require_special'}
    current_settings: Dict[str, str] = {}
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'save_settings':
            values: Dict[str, str] = {}
            for k in setting_keys:
                values[k] = request.form.get(k, '').strip()
                if k in boolean_keys:
                    values[k] = '1' if request.form.get(k) == '1' else '0'
                else:
                    values[k] = (request.form.get(k) or '').strip()
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_settings (
                        key TEXT,
                        value TEXT,
                        category TEXT,
                        description TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        company_id INTEGER,
                        PRIMARY KEY (key, company_id)
                    )
                    """
                )
                for k, val in values.items():
                    cur.execute(
                        """
                        INSERT INTO system_settings (key, value, category, description, company_id)
                        VALUES (?, ?, 'security', 'Güvenlik ayarı', ?)
                        ON CONFLICT(key, company_id) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
                        """,
                        (k, val, company_id),
                    )
                conn.commit()
                conn.close()
                flash('Güvenlik ayarları güncellendi.', 'success')
            except Exception as e:
                logging.error(f"Save security settings error: {e}")
                flash('Güvenlik ayarları kaydedilemedi.', 'danger')
            return redirect(url_for('super_admin_security'))
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT,
                value TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER,
                PRIMARY KEY (key, company_id)
            )
            """
        )
        for k in setting_keys:
            cur.execute("SELECT value FROM system_settings WHERE key=? AND company_id=?", (k, company_id))
            row = cur.fetchone()
            if row and row[0] is not None:
                current_settings[k] = str(row[0])
            else:
                current_settings[k] = ''
        conn.close()
    except Exception as e:
        logging.error(f"Load security settings error: {e}")
    return render_template(
        'super_admin_security.html',
        title='Güvenlik Ayarları',
        settings=current_settings
    )


@app.route('/super_admin/maintenance', methods=['GET'])
@super_admin_required
def super_admin_maintenance():
    if 'user' not in session:
        return redirect(url_for('login'))
    metrics: Dict[str, object] = {
        'db_size_mb': 0.0,
        'table_count': 0,
        'backup_count': 0,
        'last_backup_at': None
    }
    try:
        if os.path.exists(DB_PATH):
            db_size = os.path.getsize(DB_PATH)
            metrics['db_size_mb'] = round(db_size / (1024 * 1024), 2)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        metrics['table_count'] = cur.fetchone()[0]
        try:
            cur.execute("SELECT COUNT(*), MAX(backup_date) FROM backup_history")
            row = cur.fetchone()
            if row:
                metrics['backup_count'] = row[0] or 0
                metrics['last_backup_at'] = row[1]
        except Exception as e:
            logging.error(f"Maintenance backup stats error: {e}")
        conn.close()
    except Exception as e:
        logging.error(f"Maintenance metrics error: {e}")
    return render_template(
        'super_admin_maintenance.html',
        title='Bakım ve Onarım',
        metrics=metrics
    )

@app.route('/help')
@require_company_context
def help_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('help.html', title='Yardım Merkezi', manager_available=True)

@app.route('/support/create_ticket', methods=['GET', 'POST'])
@require_company_context
def create_ticket():
    if 'user' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            subject = request.form.get('subject')
            message = request.form.get('message')
            priority = request.form.get('priority', 'medium')
            category = request.form.get('category', 'general')
            
            conn = get_db()
            # Ensure support_tickets table exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    company_id INTEGER,
                    subject TEXT NOT NULL,
                    message TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    category TEXT DEFAULT 'general',
                    status TEXT DEFAULT 'open',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                INSERT INTO support_tickets (user_id, company_id, subject, message, priority, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session.get('user_id'), g.company_id, subject, message, priority, category))
            conn.commit()
            conn.close()
            
            flash('Destek talebiniz başarıyla oluşturuldu. Ekibimiz en kısa sürede sizinle iletişime geçecektir.', 'success')
            return redirect(url_for('help_module'))
        except Exception as e:
            logging.error(f"Support ticket error: {e}")
            flash(f'Hata oluştu: {e}', 'danger')
            
    return render_template('support_ticket.html', title='Destek Talebi Oluştur')

@app.route('/documentation')
@require_company_context
def documentation():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('documentation.html', title='Dokümantasyon')


@app.route('/stakeholder_survey/<token>', methods=['GET', 'POST'])
@require_company_context
def stakeholder_survey_public(token: str):
    conn = get_db()
    cur = conn.execute(
        """
        SELECT id, company_id, survey_title, survey_description
        FROM online_surveys
        WHERE survey_link LIKE ? AND is_active = 1
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (f"%/{token}",),
    )
    survey = cur.fetchone()

    company = None
    if survey:
        cur = conn.execute("SELECT id, name FROM companies WHERE id = ?", (survey["company_id"],))
        crow = cur.fetchone()
        if crow:
            company = SimpleNamespace(id=crow["id"], name=crow["name"])

    conn.close()

    if not survey:
        return render_template("stakeholder_survey.html", company=None, sdg_questions=[], demographic_questions=[], submitted=False), 404

    engagement = StakeholderEngagement(DB_PATH)
    sdg_questions = engagement.get_general_sdg_survey_questions()
    demographic_questions = engagement.get_demographic_questions()

    if request.method == "POST":
        responses = {}
        for q in sdg_questions:
            key = f"q_{q['id']}"
            value = request.form.get(key)
            if value is not None and value != "":
                responses[q["id"]] = value
        for dq in demographic_questions:
            key = dq["id"]
            value = request.form.get(key)
            if value is not None and value != "":
                responses[dq["id"]] = value
        open_feedback = request.form.get("open_feedback", "").strip()
        if open_feedback:
            responses["open_feedback"] = open_feedback

        ok = engagement.submit_survey_response(token, responses)
        if ok:
            return render_template("stakeholder_survey.html", company=company, sdg_questions=sdg_questions, demographic_questions=demographic_questions, submitted=True)

        flash("Anket yanıtı kaydedilirken bir hata oluştu.", "danger")

    return render_template("stakeholder_survey.html", company=company, sdg_questions=sdg_questions, demographic_questions=demographic_questions, submitted=False)

@app.route('/messages')
@require_company_context
def messages():
    if 'user' not in session: return redirect(url_for('login'))
    box = request.args.get('box', 'inbox')
    return render_template('messages.html', title='Mesajlar', box=box)

@app.route('/messages/new', methods=['GET', 'POST'])
@require_company_context
def messages_new():
    if 'user' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        flash('Mesajınız gönderildi.', 'success')
        return redirect(url_for('messages', box='sent'))
    return render_template('message_new.html', title='Yeni Mesaj')

@app.route('/tsrs')
@require_company_context
def tsrs_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('tsrs')
    
    if not manager:
        return render_template('tsrs.html', title='TSRS', manager_available=False, stats={}, records=[])
        
    # Get indicators for the modal
    indicators = manager.get_tsrs_indicators()
    
    # Get recent responses as records
    records = manager.get_tsrs_responses(company_id)
    
    # Get TSRS-ESRS Mappings
    mappings = []
    if hasattr(manager, 'get_tsrs_esrs_mappings'):
        mappings = manager.get_tsrs_esrs_mappings()
    
    # Simple stats
    stats = {
        'total_indicators': len(indicators),
        'reported_indicators': len(records),
        'total_mappings': len(mappings)
    }
    
    return render_template('tsrs.html', title='TSRS', manager_available=True, stats=stats, records=records, indicators=indicators, mappings=mappings, columns=['indicator_code', 'indicator_title', 'response_value', 'unit', 'reporting_period'])




@app.route('/ifrs')
@require_company_context
def ifrs_module():
    if 'user' not in session: return redirect(url_for('login'))
    return redirect(url_for('issb_module'))

@app.route('/data')
@require_company_context
def data():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    data_ctx = {'carbon': [], 'energy': [], 'water': [], 'waste': []}
    try:
        conn = get_db()
        try: data_ctx['carbon'] = conn.execute("SELECT * FROM carbon_emissions WHERE company_id = ? ORDER BY created_at DESC LIMIT 50", (company_id,)).fetchall()
        except: pass
        try: data_ctx['energy'] = conn.execute("SELECT * FROM energy_consumption WHERE company_id = ? ORDER BY year DESC, month DESC LIMIT 50", (company_id,)).fetchall()
        except: pass
        try: data_ctx['water'] = conn.execute("SELECT * FROM water_consumption WHERE company_id = ? ORDER BY year DESC, month DESC LIMIT 50", (company_id,)).fetchall()
        except: pass
        try: data_ctx['waste'] = conn.execute("SELECT * FROM waste_generation WHERE company_id = ? ORDER BY date DESC LIMIT 50", (company_id,)).fetchall()
        except: pass
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        
    return render_template('data.html', title='Veri Girişi', data=data_ctx)

@app.route('/data/add', methods=['GET', 'POST'])
@require_company_context
def data_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_type = request.args.get('type')
    if not data_type:
        data_type = request.args.get('data_type')
        
    module = request.args.get('module')
    
    if request.method == 'POST':
        try:
            dtype = request.form.get('data_type')
            date_str = request.form.get('date', '')
            company_id = g.company_id
            
            # Parse date
            year = datetime.now().year
            month = datetime.now().month
            if date_str:
                try:
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                    year = dt.year
                    month = dt.month
                except:
                    pass

            if dtype == 'carbon':
                manager = MANAGERS.get('carbon')
                if not manager: raise Exception("Carbon Manager not initialized")
                
                scope = request.form.get('scope')
                # Flexible field names
                category = request.form.get('category') or request.form.get('source_type')
                quantity = float(request.form.get('amount') or request.form.get('quantity') or 0)
                unit = request.form.get('unit')
                
                if scope == 'Scope 1':
                    manager.add_scope1_emission(company_id, year, category, category, quantity, unit, invoice_date=date_str)
                elif scope == 'Scope 2':
                    manager.add_scope2_emission(company_id, year, category, quantity, unit, invoice_date=date_str)
                elif scope == 'Scope 3':
                    manager.add_scope3_emission(company_id, year, category, None, quantity, unit, invoice_date=date_str)
            
            elif dtype == 'energy':
                manager = MANAGERS.get('energy')
                if not manager: raise Exception("Energy Manager not initialized")
                
                etype = request.form.get('energy_type')
                cons = float(request.form.get('energy_consumption') or request.form.get('amount') or 0)
                unit = request.form.get('energy_unit') or request.form.get('unit')
                cost = float(request.form.get('cost') or 0)
                source = request.form.get('source')
                
                manager.add_energy_consumption(company_id, year, etype, cons, unit, cost, month=month, invoice_date=date_str, source=source)
                
            elif dtype == 'water':
                manager = MANAGERS.get('water')
                if not manager: raise Exception("Water Manager not initialized")
                
                # Flexible field names
                wtype = request.form.get('water_type') or request.form.get('source') # source is used in template
                cons = float(request.form.get('water_consumption') or request.form.get('amount') or 0)
                unit = request.form.get('water_unit') or request.form.get('unit')
                cost = float(request.form.get('cost') or 0)
                consumption_type = request.form.get('consumption_type') or 'industrial'
                
                manager.add_water_consumption(company_id, year, consumption_type, cons, unit, cost=cost, source=wtype, month=month, invoice_date=date_str)
                
            elif dtype == 'waste':
                manager = MANAGERS.get('waste')
                if not manager: raise Exception("Waste Manager not initialized")
                
                wtype = request.form.get('waste_type')
                category = request.form.get('category') or wtype
                amount = float(request.form.get('waste_amount') or request.form.get('amount') or 0)
                unit = request.form.get('waste_unit') or request.form.get('unit')
                method = request.form.get('disposal_method')
                
                manager.add_waste_generation(company_id, year, wtype, category, amount, unit, disposal_method=method, month=month, invoice_date=date_str)

            elif dtype == 'biodiversity':
                manager = MANAGERS.get('biodiversity')
                if not manager: raise Exception("Biodiversity Manager not initialized")
                
                bio_category = request.form.get('bio_category')
                
                if bio_category == 'habitat':
                    habitat_name = request.form.get('habitat_name')
                    habitat_type = request.form.get('habitat_type')
                    area_size = float(request.form.get('area_size') or 0)
                    area_unit = request.form.get('area_unit') or 'm²'
                    protection_status = request.form.get('protection_status')
                    management_plan = request.form.get('management_plan')
                    
                    manager.add_habitat_area(company_id, habitat_name, habitat_type, area_size, area_unit, 
                                           protection_status=protection_status, management_plan=management_plan)
                                           
                elif bio_category == 'species':
                    species_name = request.form.get('species_name')
                    species_type = request.form.get('species_type')
                    conservation_status = request.form.get('conservation_status')
                    population_count = int(request.form.get('population_count') or 0)
                    protection_measures = request.form.get('protection_measures')
                    
                    manager.add_biodiversity_species(company_id, species_name, species_type, 
                                                   conservation_status=conservation_status, 
                                                   population_count=population_count, 
                                                   protection_measures=protection_measures)
                                                   
                elif bio_category == 'project':
                    project_name = request.form.get('project_name')
                    project_type = request.form.get('project_type')
                    start_date = request.form.get('start_date')
                    end_date = request.form.get('end_date')
                    investment_cost = float(request.form.get('investment_cost') or 0)
                    expected_benefits = request.form.get('expected_benefits')
                    
                    manager.add_biodiversity_project(company_id, project_name, project_type, start_date, end_date,
                                                   investment_cost, expected_benefits=expected_benefits)

                elif bio_category == 'ecosystem':
                    year_val = int(request.form.get('year') or year)
                    service_type = request.form.get('service_type')
                    service_value = float(request.form.get('service_value') or 0)
                    value_unit = request.form.get('value_unit')
                    beneficiary = request.form.get('beneficiary')
                    measurement_method = request.form.get('measurement_method')
                    
                    manager.add_ecosystem_service(company_id, year_val, service_type, service_value, value_unit,
                                                measurement_method=measurement_method, beneficiary=beneficiary)
                
                # Legacy fallback (if bio_category is generic or missing)
                elif bio_category:
                     cat = bio_category
                     desc = request.form.get('bio_description')
                     area = float(request.form.get('bio_area') or 0)
                     status = request.form.get('bio_status')
                     
                     if 'habitat' in cat.lower():
                         manager.add_habitat_area(company_id, cat, 'General', area, 'm2', protection_status=status, management_plan=desc)
                     elif 'proje' in cat.lower() or 'project' in cat.lower():
                         manager.add_biodiversity_project(company_id, cat, 'Conservation', date_str, date_str, 0, area, 'm2', expected_benefits=desc)
                     else:
                         manager.add_biodiversity_species(company_id, cat, 'General', conservation_status=status, protection_measures=desc)

            elif dtype == 'social':
                manager = MANAGERS.get('social')
                if not manager: raise Exception("Social Manager not initialized")

                social_category = request.form.get('social_category')

                try:
                    year_for_social = int(str(date_str)[:4]) if date_str and str(date_str)[:4].isdigit() else year
                except Exception:
                    year_for_social = year

                if social_category == 'employment':
                    employee_count = int(request.form.get('employee_count') or 0)
                    gender = request.form.get('gender') or 'All'
                    department = request.form.get('department') or ''
                    manager.add_employee_data(company_id, employee_count, gender, department, '', year_for_social)
                elif social_category == 'ohs':
                    incident_type = request.form.get('incident_type') or ''
                    severity = request.form.get('severity') or ''
                    lost_time_days = int(request.form.get('lost_time_days') or 0)
                    manager.add_ohs_incident(company_id, incident_type, date_str, severity, '', lost_time_days)
                elif social_category == 'training':
                    training_name = request.form.get('training_name') or ''
                    hours = float(request.form.get('training_hours') or request.form.get('hours') or 0)
                    participants = int(request.form.get('participants') or 0)
                    manager.add_training(company_id, training_name, hours, participants, date_str, 'training')

            elif dtype == 'governance':
                manager = MANAGERS.get('governance')
                if not manager: raise Exception("Governance Manager not initialized")

                governance_category = request.form.get('governance_category')
                
                # Check for direct type from hidden fields if category not set
                if not governance_category:
                     # Fallback logic if category is not explicitly sent but data_type might be specialized
                     # In standardized forms, we expect governance_category to be set.
                     pass

                if governance_category == 'board' or governance_category == 'board_member':
                    name = request.form.get('member_name')
                    pos = request.form.get('position')
                    mtype = request.form.get('member_type')
                    indep = request.form.get('independence_status')
                    gender = request.form.get('gender')
                    expert = request.form.get('expertise_area')
                    
                    manager.add_board_member(
                        company_id=company_id,
                        member_name=name,
                        position=pos,
                        member_type=mtype,
                        independence_status=indep,
                        gender=gender,
                        expertise_area=expert
                    )
                elif governance_category == 'ethics':
                    training_name = request.form.get('training_name')
                    participants = int(request.form.get('participants') or 0)
                    hours = float(request.form.get('total_hours') or request.form.get('ethics_training_hours') or 0)
                    desc = request.form.get('description')
                    
                    manager.add_ethics_training(
                        company_id=company_id,
                        training_name=training_name,
                        participants=participants,
                        total_hours=hours,
                        description=desc
                    )
                elif governance_category == 'committee':
                    name = request.form.get('committee_name')
                    ctype = request.form.get('committee_type')
                    count = int(request.form.get('member_count') or 0)
                    resp = request.form.get('responsibilities')
                    
                    manager.add_governance_committee(
                        company_id=company_id,
                        committee_name=name,
                        committee_type=ctype,
                        member_count=count,
                        responsibilities=resp
                    )

            elif dtype == 'economic':
                manager = MANAGERS.get('economic')
                if not manager: raise Exception("Economic Manager not initialized")

                economic_category = request.form.get('economic_category')

                try:
                    year_for_economic = int(request.form.get('year') or year)
                except Exception:
                    year_for_economic = year

                if economic_category == 'value' or economic_category == 'value_distribution':
                    revenue = float(request.form.get('revenue') or 0)
                    operating_costs = float(request.form.get('operating_costs') or 0)
                    employee_wages = float(request.form.get('employee_wages') or 0)
                    payments_capital = float(request.form.get('payments_capital') or 0)
                    payments_gov = float(request.form.get('payments_gov') or 0)
                    community_investments = float(request.form.get('community_investments') or 0)
                    
                    manager.add_economic_value_distribution(
                        company_id=company_id,
                        year=year_for_economic,
                        revenue=revenue,
                        operating_costs=operating_costs,
                        employee_wages=employee_wages,
                        payments_to_capital_providers=payments_capital,
                        payments_to_governments=payments_gov,
                        community_investments=community_investments
                    )
                elif economic_category == 'climate' or economic_category == 'financial_performance':
                    assets = float(request.form.get('total_assets') or request.form.get('financial_impact') or 0)
                    liabilities = float(request.form.get('total_liabilities') or 0)
                    net_profit = float(request.form.get('net_profit') or assets) # Fallback to assets/impact if only one field
                    ebitda = float(request.form.get('ebitda') or 0)
                    equity = assets - liabilities
                    
                    manager.add_financial_performance(
                        company_id=company_id,
                        year=year_for_economic,
                        total_assets=assets,
                        total_liabilities=liabilities,
                        net_profit=net_profit,
                        ebitda=ebitda,
                        equity=equity
                    )
                elif economic_category == 'tax':
                    corporate_tax = float(request.form.get('corporate_tax') or request.form.get('tax_paid') or 0)
                    payroll_tax = float(request.form.get('payroll_tax') or 0)
                    vat_collected = float(request.form.get('vat_collected') or 0)
                    property_tax = float(request.form.get('property_tax') or 0)
                    other_taxes = float(request.form.get('other_taxes') or 0)
                    
                    manager.add_tax_contributions(
                        company_id=company_id,
                        year=year_for_economic,
                        corporate_tax=corporate_tax,
                        payroll_tax=payroll_tax,
                        vat_collected=vat_collected,
                        property_tax=property_tax,
                        other_taxes=other_taxes
                    )

            elif dtype == 'supply_chain':
                manager = MANAGERS.get('supply_chain')
                if not manager: raise Exception("Supply Chain Manager not initialized")
                
                name = request.form.get('supplier_name')
                stype = request.form.get('supplier_type')
                country = request.form.get('country')
                score = float(request.form.get('score') or 0)
                risk = request.form.get('risk_level')
                
                # Auto-generate code
                import time
                supplier_code = f"SUP-{int(time.time())}"
                
                supplier_id = manager.add_supplier(
                    company_id=company_id,
                    supplier_code=supplier_code,
                    supplier_name=name,
                    country=country,
                    supplier_type=stype,
                    risk_level=risk
                )
                
                if supplier_id:
                    manager.add_assessment(
                        company_id=company_id,
                        supplier_id=supplier_id,
                        assessment_period='Initial',
                        overall_score=score,
                        risk_level=risk,
                        assessment_notes='Initial manual entry'
                    )

            elif dtype == 'tcfd':
                year_val = request.form.get('year')
                category = request.form.get('category')
                disclosure = request.form.get('disclosure')
                impact = request.form.get('impact')
                
                conn = get_db()
                conn.execute("""
                    INSERT INTO tcfd_disclosures (company_id, year, category, disclosure, impact)
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, year_val, category, disclosure, impact))
                conn.commit()
                conn.close()

            flash('Veri başarıyla eklendi.', 'success')
            return redirect(url_for('data'))
            
        except Exception as e:
            logging.error(f"Error adding data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('data_edit.html', title='Yeni Veri Girişi', data_type=data_type, module=module)

# --- Module Routes ---

@app.route('/sdg/goals')
@require_company_context
def sdg_goals():
    return redirect(url_for('sdg_module'))

@app.route('/gri/dashboard')
@require_company_context
def gri_dashboard():
    return redirect(url_for('gri_module'))

@app.route('/environmental/carbon')
@require_company_context
def environmental_carbon():
    return redirect(url_for('carbon_module'))

@app.route('/environmental/energy')
@require_company_context
def environmental_energy():
    return redirect(url_for('energy_module'))

@app.route('/product_technology/add', methods=['POST'])
@require_company_context
def product_tech_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('product_technology')
    if not manager:
        flash('Üretim ve Teknoloji modülü aktif değil.', 'danger')
        # Try to find the correct route name, usually product_technology_module?
        # Let's assume it is product_technology_module based on pattern
        return redirect(url_for('product_technology_module'))
        
    try:
        company_id = g.company_id
        reporting_period = request.form.get('reporting_period')
        rd_ratio = float(request.form.get('rd_investment_ratio') or 0)
        patents = int(request.form.get('patent_applications') or 0)
        budget = float(request.form.get('innovation_budget') or 0)
        ecodesign = request.form.get('ecodesign_integration') == 'on'
        lca = request.form.get('lca_implementation') == 'on'
        
        success = manager.save_innovation_metrics(
            company_id=company_id,
            rd_investment_ratio=rd_ratio,
            patent_applications=patents,
            ecodesign_integration=ecodesign,
            lca_implementation=lca,
            innovation_budget=budget,
            reporting_period=reporting_period
        )
        
        if success:
            flash('İnovasyon verisi başarıyla eklendi.', 'success')
        else:
            flash('Veri eklenirken bir hata oluştu.', 'danger')
            
    except Exception as e:
        logging.error(f"Error adding product technology data: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('product_technology_module'))

@app.route('/environmental/water')
@require_company_context
def environmental_water():
    return redirect(url_for('water_module'))

@app.route('/environmental/waste')
@require_company_context
def environmental_waste():
    return redirect(url_for('waste_module'))

@app.route('/environmental/biodiversity')
@require_company_context
def environmental_biodiversity():
    return redirect(url_for('biodiversity_module'))

@app.route('/social/dashboard')
@require_company_context
def social_dashboard():
    return redirect(url_for('social_module'))

@app.route('/governance/dashboard')
@require_company_context
def governance_dashboard():
    return redirect(url_for('governance_module'))

@app.route('/supply_chain/dashboard')
@require_company_context
def supply_chain_dashboard():
    return redirect(url_for('supply_chain_module'))

@app.route('/economic/dashboard')
@require_company_context
def economic_dashboard():
    return redirect(url_for('economic_module'))

@app.route('/esg/dashboard')
@require_company_context
def esg_dashboard():
    return redirect(url_for('esg_module'))

@app.route('/cbam/dashboard')
@require_company_context
def cbam_dashboard():
    return redirect(url_for('cbam_module'))

@app.route('/csrd/dashboard')
@require_company_context
def csrd_dashboard():
    return redirect(url_for('csrd_module'))

@app.route('/eu_taxonomy/dashboard')
@require_company_context
def eu_taxonomy_dashboard():
    return redirect(url_for('taxonomy_module'))

@app.route('/issb/dashboard')
@require_company_context
def issb_dashboard():
    return redirect(url_for('issb_module'))

@app.route('/iirc/dashboard')
@require_company_context
def iirc_dashboard():
    return redirect(url_for('iirc_module'))

@app.route('/esrs/dashboard')
@require_company_context
def esrs_dashboard():
    return redirect(url_for('esrs_module'))

@app.route('/tcfd/dashboard')
@require_company_context
def tcfd_dashboard():
    return redirect(url_for('tcfd_module'))

@app.route('/tnfd/dashboard')
@require_company_context
def tnfd_dashboard():
    return redirect(url_for('tnfd_module'))

@app.route('/cdp/dashboard')
@require_company_context
def cdp_dashboard():
    return redirect(url_for('cdp_module'))

@app.route('/cdp/settings')
@require_company_context
def cdp_settings():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('cdp')
    if not manager:
        flash(_('module_not_active', 'Modül aktif değil'), 'warning')
        return redirect(url_for('cdp_module'))
    
    current_scheme = manager.get_weighting_scheme(company_id, 2024)
    
    questions = {}
    if current_scheme == 'Custom':
        questions['Climate Change'] = manager.get_questions('Climate Change', company_id, 2024)
        questions['Water Security'] = manager.get_questions('Water Security', company_id, 2024)
        questions['Forests'] = manager.get_questions('Forests', company_id, 2024)
    
    return render_template('cdp_settings.html', 
                           title='CDP Ayarları', 
                           current_scheme=current_scheme,
                           questions=questions)

@app.route('/cdp/settings/update_scheme', methods=['POST'])
@require_company_context
def cdp_settings_update_scheme():
    if 'user' not in session: return redirect(url_for('login'))
    
    scheme = request.form.get('scheme')
    company_id = g.company_id
    manager = MANAGERS.get('cdp')
    
    if manager and manager.update_weighting_scheme(company_id, scheme, 2024):
        flash(_('settings_updated', 'Ayarlar güncellendi'), 'success')
        # If switching to Standard, we might want to auto-reset weights?
        # For now, let's keep it manual or let the user decide via the reset button.
    else:
        flash(_('error_occurred', 'Hata oluştu'), 'danger')
        
    return redirect(url_for('cdp_settings'))

@app.route('/cdp/settings/update_weights', methods=['POST'])
@require_company_context
def cdp_settings_update_weights():
    if 'user' not in session: return redirect(url_for('login'))
    
    questionnaire_type = request.form.get('questionnaire_type')
    company_id = g.company_id
    manager = MANAGERS.get('cdp')
    
    if not manager:
        return redirect(url_for('cdp_settings'))
        
    updated_count = 0
    for key, value in request.form.items():
        if key.startswith('weight_'):
            question_id = key.replace('weight_', '')
            try:
                weight = float(value)
                if manager.update_question_weight(questionnaire_type, company_id, question_id, weight, 2024):
                    updated_count += 1
            except ValueError:
                pass
                
    flash(f'{updated_count} {_("weights_updated", "ağırlık güncellendi")}', 'success')
    return redirect(url_for('cdp_settings'))

@app.route('/cdp/settings/reset', methods=['POST'])
@require_company_context
def cdp_settings_reset():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('cdp')
    
    if manager and manager.reset_weights_to_standard(company_id, 2024):
        flash(_('weights_reset', 'Ağırlıklar standart değerlere sıfırlandı'), 'success')
    else:
        flash(_('error_occurred', 'Hata oluştu'), 'danger')
        
    return redirect(url_for('cdp_settings'))



# --- Basic Admin Pages ---

@app.route('/users')
@admin_required
@require_company_context
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    users = []
    pagination = None
    try:
        conn = get_db()
        offset = (page - 1) * per_page
        
        # Super admin olmayanlar için super_admin departmanını ve __super__ kullanıcılarını gizle
        current_role = session.get('role', '')
        
        if current_role == '__super__':
            count_query = "SELECT COUNT(*) FROM users"
            data_query = """
                SELECT u.id, u.username, u.email, u.first_name || ' ' || u.last_name as full_name, 
                       u.department, u.is_active, u.last_login, r.name as role
                FROM users u
                LEFT JOIN user_roles ur ON u.id = ur.user_id
                LEFT JOIN roles r ON ur.role_id = r.id
                ORDER BY u.id DESC
                LIMIT ? OFFSET ?
            """
            params = (per_page, offset)
            total = conn.execute(count_query).fetchone()[0]
            rows = conn.execute(data_query, params).fetchall()
        else:
            # Super admin olmayanlar için filtrele: Sadece kendi şirketinin kullanıcılarını gör
            count_query = "SELECT COUNT(*) FROM users WHERE company_id = ? AND (department != 'super_admin' OR department IS NULL)"
            
            data_query = """
                SELECT u.id, u.username, u.email, u.first_name || ' ' || u.last_name as full_name, 
                       u.department, u.is_active, u.last_login, r.name as role
                FROM users u
                LEFT JOIN user_roles ur ON u.id = ur.user_id
                LEFT JOIN roles r ON ur.role_id = r.id
                WHERE u.company_id = ?
                AND (u.department != 'super_admin' OR u.department IS NULL)
                AND (r.name != '__super__' OR r.name IS NULL)
                ORDER BY u.id DESC
                LIMIT ? OFFSET ?
            """
            params = (g.company_id, g.company_id, per_page, offset)
            total = conn.execute(count_query, (g.company_id,)).fetchone()[0]
            rows = conn.execute(data_query, params).fetchall()
        
        conn.close()
        
        users = [dict(row) for row in rows]
        
        # Simple pagination object
        import math
        class Pagination:
            def __init__(self, page, per_page, total):
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = int(math.ceil(total / per_page))
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1
                self.next_num = page + 1
                self.iter_pages = lambda: range(1, self.pages + 1)
        
        pagination = Pagination(page, per_page, total)
        
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        flash('Kullanıcı listesi alınamadı.', 'danger')
        
    return render_template('users.html', title='Kullanıcı Yönetimi', users=users, pagination=pagination)

@app.route('/survey/<token>', methods=['GET', 'POST'])
def public_survey(token):
    try:
        logging.info(f"Public survey requested with token: {token}")
        conn = get_db()
        
        # Anket var mı kontrol et
        query = "SELECT * FROM online_surveys WHERE survey_link = ? AND is_active = 1"
        param = f"/survey/{token}"
        logging.info(f"Executing query: {query} with param: {param}")
        
        row = conn.execute(query, (param,)).fetchone()
        
        if not row:
            logging.warning(f"Survey not found for token: {token}")
            conn.close()
            return render_template('404.html'), 404
            
        logging.info(f"Survey found: {dict(row)}")
        survey = dict(row)
        
        # Get questions
        # Use company_id from survey for extra safety
        cursor = conn.execute("SELECT * FROM survey_questions WHERE survey_id=? AND company_id=? ORDER BY display_order, id", (survey['id'], survey['company_id']))
        rows = cursor.fetchall()
        
        # Safely convert to list of dicts
        questions = []
        for row in rows:
            q = dict(row)
            if 'category' not in q: q['category'] = 'General'
            if 'question_type' not in q: q['question_type'] = 'scale_1_5'
            if 'is_required' not in q: q['is_required'] = 1
            questions.append(q)
        
        # Group questions by category for public view
        questions_by_category = {}
        if questions:
            for q in questions:
                cat = q['category']
                if not cat: cat = 'General'
                
                if cat not in questions_by_category:
                    questions_by_category[cat] = []
                questions_by_category[cat].append(q)
        
        # Get demographics config
        demographics = {}
        if survey.get('demographics_config'):
            try:
                import json
                demographics = json.loads(survey['demographics_config'])
            except:
                pass
        
        if request.method == 'POST':
            try:
                # 1. Collect respondent info
                respondent_info = {
                    'name': request.form.get('respondent_name'),
                    'email': request.form.get('respondent_email'),
                    'company': request.form.get('respondent_company'),
                    'department': request.form.get('respondent_department'),
                    'stakeholder_group': request.form.get('stakeholder_group'),
                    'ip_address': request.remote_addr,
                    'user_agent': request.user_agent.string
                }
                
                # 2. Insert response record
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO survey_responses (
                        survey_id, respondent_name, respondent_email, 
                        respondent_company, respondent_department, stakeholder_group,
                        ip_address, user_agent, company_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    survey['id'], 
                    respondent_info['name'], 
                    respondent_info['email'],
                    respondent_info['company'], 
                    respondent_info['department'],
                    respondent_info['stakeholder_group'],
                    respondent_info['ip_address'],
                    respondent_info['user_agent'],
                    survey['company_id']
                ))
                response_id = cur.lastrowid
                
                # 3. Save answers
                for key, value in request.form.items():
                    if key.startswith('q_'):
                        try:
                            question_id = int(key.replace('q_', ''))
                            
                            answer_text = value
                            score = None
                            
                            # Try to extract score if it's a scale (and value is digit)
                            if value.isdigit() and 1 <= int(value) <= 5:
                                score = int(value)
                            
                            cur.execute("""
                                INSERT INTO survey_answers (response_id, question_id, answer_text, score, company_id)
                                VALUES (?, ?, ?, ?, ?)
                            """, (response_id, question_id, answer_text, score, survey['company_id']))
                        except Exception as e:
                            logging.error(f"Error saving answer {key}: {e}")
                
                # 4. Update stats
                cur.execute("UPDATE online_surveys SET response_count = response_count + 1 WHERE id=? AND company_id=?", (survey['id'], survey['company_id']))
                
                conn.commit()
                conn.close()
                return render_template('survey_success.html')
                
            except Exception as e:
                logging.error(f"Error submitting survey: {e}")
                conn.rollback()
                conn.close()
                flash('Anket gönderilirken bir hata oluştu.', 'error')
                # Fall through to render form again
        else:
            conn.close()
            
        return render_template('survey_public.html', survey=survey, questions=questions, questions_by_category=questions_by_category, demographics=demographics, now=datetime.now())
        
    except Exception as e:
        logging.error(f"Public survey error: {e}")
        return render_template('500.html'), 500


@app.route('/stakeholder-portal/<token>')
def stakeholder_portal(token):
    try:
        from backend.modules.stakeholder.stakeholder_engagement import StakeholderEngagement
        engagement = StakeholderEngagement(DB_PATH)
        
        stakeholder = engagement.verify_portal_access(token)
        if not stakeholder:
            return render_template('404.html'), 404
            
        return render_template('stakeholder_portal.html', stakeholder=stakeholder)
    except Exception as e:
        logging.error(f"Portal access error: {e}")
        return render_template('500.html'), 500


@app.route('/users/add', methods=['GET', 'POST'])
@admin_required
@require_company_context
def user_add():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            full_name = request.form.get('full_name', '')
            # role_name = request.form.get('role', 'User') # OLD
            role_names = request.form.getlist('roles') # NEW: Multi-select
            department = request.form.get('department')
            is_active = request.form.get('is_active') == 'on'
            
            # Şirketleri al (Multi-select)
            company_ids = request.form.getlist('companies')
            
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
            
            conn = get_db()
            exist = conn.execute("SELECT 1 FROM users WHERE username=? OR email=?", (username, email)).fetchone()
            if exist:
                flash('Kullanıcı adı veya e-posta zaten kayıtlı.', 'warning')
                conn.close()
                return render_template('user_edit.html', user=None)

            if user_manager:
                # Rol ID'lerini bul
                role_ids = []
                if role_names:
                    placeholders = ','.join(['?'] * len(role_names))
                    cursor = conn.execute(f"SELECT id FROM roles WHERE name IN ({placeholders})", role_names)
                    role_ids = [row[0] for row in cursor.fetchall()]
                else:
                    # Varsayılan User rolü
                    role_row = conn.execute("SELECT id FROM roles WHERE name='user'").fetchone()
                    if role_row:
                        role_ids.append(role_row['id'])

                conn.close()

                user_data = {
                    'username': username,
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'department': department,
                    'is_active': is_active,
                    'role_ids': role_ids,
                    'company_ids': [int(cid) for cid in company_ids] if company_ids else []
                }
                
                uid = user_manager.create_user(user_data, created_by=session.get('user_id'))
                if uid > 0:
                    flash('Kullanıcı başarıyla oluşturuldu ve hoş geldin e-postası gönderildi.', 'success')
                    return redirect(url_for('users'))
                else:
                    flash('Kullanıcı oluşturulurken bir hata oluştu.', 'danger')
                    return render_template('user_edit.html', user=None)

        except Exception as e:
            logging.error(f"Error creating user: {e}")
            flash(f'Hata: {e}', 'danger')

    # GET request
    all_roles = []
    all_companies = []
    if user_manager:
        all_roles = user_manager.get_roles()
        all_companies = user_manager.get_companies()
    return render_template('user_edit.html', user=None, roles=all_roles, companies=all_companies)

# --- Role Management Routes ---

@app.route('/roles')
@admin_required
@require_company_context
def roles():
    if not user_manager:
        flash(_('system_error', 'Sistem hatası: Kullanıcı yöneticisi başlatılamadı.'), 'danger')
        return redirect(url_for('dashboard'))
    
    all_roles = user_manager.get_roles()
    return render_template('roles.html', roles=all_roles)

@app.route('/roles/add')
@admin_required
@require_company_context
def role_add():
    if not user_manager:
        flash(_('system_error', 'Sistem hatası: Kullanıcı yöneticisi başlatılamadı.'), 'danger')
        return redirect(url_for('dashboard'))
        
    permissions = user_manager.get_permissions()
    
    # Group permissions by module
    permissions_by_module = {}
    for p in permissions:
        module = p['module']
        if module not in permissions_by_module:
            permissions_by_module[module] = []
        permissions_by_module[module].append(p)
        
    return render_template('role_edit.html', role=None, permissions_by_module=permissions_by_module, role_permissions=[])

@app.route('/roles/edit/<int:role_id>')
@admin_required
@require_company_context
def role_edit(role_id):
    if not user_manager:
        flash(_('system_error', 'Sistem hatası: Kullanıcı yöneticisi başlatılamadı.'), 'danger')
        return redirect(url_for('dashboard'))
        
    role = user_manager.get_role_by_id(role_id)
    if not role:
        flash(_('role_not_found', 'Rol bulunamadı.'), 'danger')
        return redirect(url_for('roles'))
        
    permissions = user_manager.get_permissions()
    role_perm_ids = user_manager.get_role_permissions(role_id)
    
    # Group permissions by module
    permissions_by_module = {}
    for p in permissions:
        module = p['module']
        if module not in permissions_by_module:
            permissions_by_module[module] = []
        permissions_by_module[module].append(p)
        
    return render_template('role_edit.html', role=role, permissions_by_module=permissions_by_module, role_permissions=role_perm_ids)

@app.route('/roles/save', methods=['POST'])
@admin_required
@require_company_context
def role_save():
    if not user_manager:
        flash(_('system_error', 'Sistem hatası: Kullanıcı yöneticisi başlatılamadı.'), 'danger')
        return redirect(url_for('dashboard'))
        
    role_id = request.form.get('role_id')
    name = request.form.get('name')
    display_name = request.form.get('display_name')
    description = request.form.get('description')
    is_active = request.form.get('is_active') == 'on'
    permission_ids = request.form.getlist('permissions')
    
    role_data = {
        'name': name,
        'display_name': display_name,
        'description': description,
        'is_active': 1 if is_active else 0,
        'permission_ids': [int(pid) for pid in permission_ids]
    }
    
    try:
        if role_id:
            # Update
            role_id = int(role_id)
            # Check if system role name is being changed (not allowed)
            current_role = user_manager.get_role_by_id(role_id)
            if current_role and current_role['is_system_role']:
                role_data.pop('name', None) # Don't update name for system roles
                
            success = user_manager.update_role_full(role_id, role_data, updated_by=session.get('user_id'))
            if success:
                flash(_('role_update_success', 'Rol başarıyla güncellendi.'), 'success')
            else:
                flash(_('role_update_error', 'Rol güncellenirken hata oluştu.'), 'danger')
        else:
            # Create
            new_id = user_manager.create_role(role_data, created_by=session.get('user_id'))
            if new_id > 0:
                flash(_('role_create_success', 'Yeni rol başarıyla oluşturuldu.'), 'success')
            else:
                flash(_('role_create_error', 'Rol oluşturulurken hata oluştu.'), 'danger')
                
    except Exception as e:
        logging.error(f"Error saving role: {e}")
        flash(_('error_occurred', 'Bir hata oluştu: {}').format(str(e)), 'danger')
        
    return redirect(url_for('roles'))

@app.route('/roles/delete/<int:role_id>')
@super_admin_required
@require_company_context
def role_delete(role_id):
    if not user_manager:
        flash(_('system_error', 'Sistem hatası: Kullanıcı yöneticisi başlatılamadı.'), 'danger')
        return redirect(url_for('dashboard'))
        
    success = user_manager.delete_role(role_id, deleted_by=session.get('user_id'))
    if success:
        flash(_('role_delete_success', 'Rol başarıyla silindi.'), 'success')
    else:
        flash(_('role_delete_error', 'Rol silinemedi (Sistem rolü olabilir).'), 'danger')
    return redirect(url_for('roles'))



@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
@require_company_context
def user_edit(user_id):
    if not user_manager:
        flash('Kullanıcı yöneticisi başlatılamadı.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            # Form verilerini al
            user_data = {
                'email': request.form.get('email'),
                'first_name': request.form.get('first_name', '').split(' ')[0], # Basit parse
                'last_name': ' '.join(request.form.get('full_name', '').split(' ')[1:]) if ' ' in request.form.get('full_name', '') else '',
                'department': request.form.get('department'),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # Full name'i tekrar birleştir (optional, user_manager first/last kullanıyor)
            if request.form.get('full_name'):
                parts = request.form.get('full_name').split(' ', 1)
                user_data['first_name'] = parts[0]
                user_data['last_name'] = parts[1] if len(parts) > 1 else ''

            # Şifre varsa ekle
            password = request.form.get('password')
            if password:
                user_data['password'] = password

            # Rolleri al (Multi-select)
            role_names = request.form.getlist('roles')
            if role_names:
                conn = get_db()
                placeholders = ','.join(['?'] * len(role_names))
                cursor = conn.execute(f"SELECT id FROM roles WHERE name IN ({placeholders})", role_names)
                role_ids = [row[0] for row in cursor.fetchall()]
                conn.close()
                user_data['role_ids'] = role_ids

            # Şirketleri al (Multi-select)
            company_ids = request.form.getlist('companies')
            if company_ids:
                user_data['company_ids'] = [int(cid) for cid in company_ids]
            
            # Güncelle
            success = user_manager.update_user(user_id, user_data, updated_by=session.get('user_id'))
            
            if success:
                flash('Kullanıcı başarıyla güncellendi.', 'success')
                return redirect(url_for('users'))
            else:
                flash('Kullanıcı güncellenirken hata oluştu.', 'danger')
                
        except Exception as e:
            logging.error(f"Error editing user: {e}")
            flash(f'Hata: {e}', 'danger')
            
    # Kullanıcıyı getir
    user = user_manager.get_user_by_id(user_id)
    
    if not user:
        flash('Kullanıcı bulunamadı.', 'warning')
        return redirect(url_for('users'))
        
    all_roles = user_manager.get_roles()
    all_companies = user_manager.get_companies()
    user_company_ids = user_manager.get_user_company_ids(user_id)
    
    # Template için user objesine ekle
    user['company_ids'] = user_company_ids
    
    return render_template('user_edit.html', user=user, roles=all_roles, companies=all_companies)

@app.route('/users/delete/<int:user_id>')
@admin_required
@require_company_context
def user_delete(user_id):
    if user_id == session.get('user_id'):
        flash('Kendinizi silemezsiniz.', 'warning')
        return redirect(url_for('users'))
    try:
        conn = get_db()
        conn.execute("DELETE FROM user_roles WHERE user_id=?", (user_id,))
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        flash('Kullanıcı silindi.', 'success')
    except Exception as e:
        logging.error(f"Error deleting user: {e}")
        flash('Silme hatası.', 'danger')
    return redirect(url_for('users'))

@app.route('/companies')
@require_company_context
def companies():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    companies = []
    try:
        conn = get_db()
        # Strict Isolation: Regular users see only their own company
        # Super admins can see all (if we decide so, but for now stick to strict isolation or check role)
        if session.get('role') == '__super__':
             companies = conn.execute("SELECT * FROM companies ORDER BY id DESC").fetchall()
        else:
             companies = conn.execute("SELECT * FROM companies WHERE id = ? ORDER BY id DESC", (g.company_id,)).fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching companies: {e}")
        
    return render_template('companies.html', title='Şirketler', companies=companies)

@app.route('/companies/add', methods=['GET', 'POST'])
@super_admin_required
@require_company_context
def company_add():
    if request.method == 'POST':
        try:
            # Map form fields (support both English and Turkish field names from company_edit.html)
            name = request.form.get('name') or request.form.get('sirket_adi')
            sector = request.form.get('sector') or request.form.get('sektor')
            country = request.form.get('country') or 'Türkiye' # Default to Türkiye if not in form
            tax_number = request.form.get('tax_number') or request.form.get('vergi_no')
            
            # Handle checkbox (on/off or True/False)
            is_active_val = request.form.get('is_active') or request.form.get('aktif')
            is_active = is_active_val == 'on' or is_active_val == 'True'

            if not name:
                flash('Şirket adı zorunludur.', 'warning')
                return render_template('company_edit.html', company=None)

            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO companies (name, sector, country, tax_number, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (name, sector, country, tax_number, is_active),
            )
            company_id = cur.lastrowid
            conn.commit()
            conn.close()
            flash('Şirket oluşturuldu. Lütfen firma bilgilerini doldurun.', 'success')
            return redirect(url_for('company_info_edit', company_id=company_id))
        except Exception as e:
            logging.error(f"Error adding company: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('company_edit.html', company=None)


@app.route('/companies/edit/<int:company_id>', methods=['GET', 'POST'])
@admin_required
@require_company_context
def company_edit(company_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    flash('Şirket düzenleme, merkezi Firma Bilgileri sayfasından yapılmaktadır.', 'info')
    return redirect(url_for('company_info_edit', company_id=company_id))

@app.route('/companies/<int:company_id>/info', methods=['GET', 'POST'])
@require_company_context
def company_info_edit(company_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    # Strict Isolation Check
    if session.get('role') not in ['__super__', 'super_admin'] and company_id != g.company_id:
        flash('Bu şirketin bilgilerini düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('companies'))

    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        if request.method == 'POST':
            data = {}
            for name in COMPANY_INFO_FIELDS:
                value = request.form.get(name)
                data[name] = value.strip() if isinstance(value, str) and value.strip() != "" else None

            data["updated_at"] = datetime.now().isoformat()

            cur.execute("PRAGMA table_info(company_info)")
            available_cols = {row[1] for row in cur.fetchall()}

            cur.execute("SELECT company_id FROM company_info WHERE company_id = ?", (company_id,))
            exists = cur.fetchone()

            if exists:
                update_data = {k: v for k, v in data.items() if k in available_cols}
                if update_data:
                    set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
                    values = list(update_data.values()) + [company_id]
                    cur.execute(f"UPDATE company_info SET {set_clause} WHERE company_id = ?", values)
            else:
                insert_data = {k: v for k, v in data.items() if k in available_cols}
                insert_data["company_id"] = company_id
                columns = ", ".join(insert_data.keys())
                placeholders = ", ".join(["?" for _ in insert_data])
                values = list(insert_data.values())
                cur.execute(f"INSERT INTO company_info ({columns}) VALUES ({placeholders})", values)

            conn.commit()
            flash('Şirket bilgileri kaydedildi.', 'success')
            return redirect(url_for('company_info_edit', company_id=company_id))

        row = conn.execute(
            "SELECT * FROM company_info WHERE company_id = ?",
            (company_id,),
        ).fetchone()

        data = {}
        if row:
            keys = row.keys() if hasattr(row, "keys") else []
            for name in COMPANY_INFO_FIELDS:
                data[name] = row[name] if name in keys and row[name] is not None else ""
        else:
            for name in COMPANY_INFO_FIELDS:
                data[name] = ""

        info = SimpleNamespace(**data)
        return render_template('company_info_edit.html', company_id=company_id, info=info)

    except Exception as e:
        logging.error(f"Error in company_info_edit: {e}")
        flash(f'Hata: {e}', 'danger')
        return redirect(url_for('company_detail', company_id=company_id))
    finally:
        if conn:
            conn.close()


@app.route('/companies/<int:company_id>/stakeholder_survey')
@require_company_context
def company_stakeholder_survey(company_id: int):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    # Strict Isolation Check
    if session.get('role') != '__super__' and company_id != g.company_id:
        flash('Yetkisiz erişim.', 'danger')
        return redirect(url_for('companies'))

    conn = get_db()
    cur = conn.execute("SELECT id, name, sector, country, tax_number, created_at, is_active FROM companies WHERE id = ?", (company_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        flash('Şirket bulunamadı.', 'danger')
        return redirect(url_for('companies'))

    company = SimpleNamespace(
        id=row['id'],
        name=row['name'],
        sector=row['sector'],
        country=row['country'],
        tax_number=row['tax_number'],
        created_at=row['created_at'],
        is_active=bool(row['is_active']),
    )

    engagement = StakeholderEngagement(DB_PATH)

    cur = conn.execute(
        """
        SELECT survey_link
        FROM online_surveys
        WHERE company_id = ? AND survey_title = ?
          AND is_active = 1
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (company_id, "Genel Paydaş Sürdürülebilirlik Anketi (SDG 1-17)"),
    )
    existing = cur.fetchone()

    survey_url = None
    if existing and existing["survey_link"]:
        survey_url = existing["survey_link"]
    else:
        title = "Genel Paydaş Sürdürülebilirlik Anketi (SDG 1-17)"
        description = "Şirketin sürdürülebilirlik performansını 17 Sürdürülebilir Kalkınma Amacı çerçevesinde değerlendiren genel paydaş anketi."
        target_groups = list(StakeholderEngagement.STAKEHOLDER_GROUPS.values())
        questions = engagement.get_general_sdg_survey_questions()
        survey_url = engagement.create_online_survey(company_id, title, description, target_groups, questions, duration_days=365)

    conn.close()
    return render_template('company_stakeholder_survey.html', company=company, survey_url=survey_url)

@app.route('/companies/<int:company_id>/gri', methods=['GET', 'POST'])
@require_company_context
def company_gri_edit(company_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    flash('Firma bilgileri artık tek bir sayfadan yönetiliyor.', 'info')
    return redirect(url_for('company_info_edit', company_id=company_id))

@app.route('/companies/detail/<int:company_id>')
@require_company_context
def company_detail(company_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    company = None
    reports = []

    try:
        conn = get_db()
        row = conn.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
        if not row:
            conn.close()
            flash('Şirket bulunamadı.', 'warning')
            return redirect(url_for('companies'))

        keys = row.keys() if hasattr(row, "keys") else []

        def _get(name, default=None):
            return row[name] if name in keys else default

        company = {
            "id": _get("id"),
            "name": _get("name") or "",
            "sector": _get("sector") or "",
            "country": _get("country") or "",
            "tax_number": _get("tax_number"),
            "is_active": bool(_get("is_active", 1)),
            "created_at": _get("created_at") or "",
        }

        try:
            report_rows = conn.execute(
                """
                SELECT id, report_name, report_type, created_at, file_size
                FROM report_registry
                WHERE company_id = ?
                ORDER BY created_at DESC
                """,
                (company_id,),
            ).fetchall()

            for r in report_rows:
                r_keys = r.keys() if hasattr(r, "keys") else []

                def _rget(name, default=None):
                    return r[name] if name in r_keys else default

                size_bytes = _rget("file_size", 0) or 0
                size_label = ""
                try:
                    if size_bytes:
                        size_kb = size_bytes / 1024.0
                        size_label = f"{size_kb:.1f} KB"
                except Exception:
                    size_label = ""

                reports.append(
                    {
                        "id": _rget("id"),
                        "name": _rget("report_name") or "",
                        "type": _rget("report_type") or "",
                        "date": _rget("created_at") or "",
                        "size": size_label,
                    }
                )
        except Exception as e:
            logging.error(f"Error fetching company reports: {e}")

        conn.close()
    except Exception as e:
        logging.error(f"Error fetching company detail: {e}")
        flash(f'Hata: {e}', 'danger')
        return redirect(url_for('companies'))

    return render_template('company_detail.html', company=company, reports=reports)


@app.route('/companies/delete/<int:company_id>', methods=['POST'])
@super_admin_required
@require_company_context
def company_delete(company_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        manager = CompanyManager(DB_PATH)
        if not manager.hard_delete_company(company_id):
            flash('Şirket silinemedi.', 'danger')
        else:
            flash('Şirket ve ilişkili veriler silindi.', 'success')
    except Exception as e:
        logging.error(f"Error deleting company: {e}")
        flash(f'Hata: {e}', 'danger')

    return redirect(url_for('companies'))

@app.route('/reports')
@require_company_context
def reports():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    company_id = g.company_id
    reports = []
    pagination = None
    try:
        conn = get_db()
        try:
            page = int(request.args.get('page', 1))
        except Exception:
            page = 1
        per_page = 25
        offset = (page - 1) * per_page

        total = 0
        try:
            total_row = conn.execute("SELECT COUNT(*) FROM report_registry WHERE company_id = ?", (company_id,)).fetchone()
            total = total_row[0] if total_row else 0
        except Exception as e:
            logging.error(f"Error counting reports: {e}")

        rows = []
        try:
            rows = conn.execute(
                "SELECT * FROM report_registry WHERE company_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
                (company_id, per_page, offset),
            ).fetchall()
        except Exception as e:
            logging.error(f"Error querying reports: {e}")

        for row in rows:
            keys = row.keys() if hasattr(row, "keys") else []
            def _get(name, default=None):
                return row[name] if name in keys else default
            reports.append(
                {
                    "id": _get("id"),
                    "report_name": _get("report_name") or _get("name") or "",
                    "report_type": _get("report_type") or _get("type") or "",
                    "created_at": _get("created_at") or _get("date") or "",
                }
            )

        total_pages = (total + per_page - 1) // per_page if per_page and total else 1
        pagination = SimpleNamespace(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_prev=page > 1,
            has_next=page < total_pages,
        )
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching reports: {e}")
    return render_template('reports.html', title='Raporlar', reports=reports, pagination=pagination)

@app.route('/reports/add', methods=['GET', 'POST'])
@require_company_context
def report_add():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        try:
            company_id = g.company_id
            module_code = request.form.get('module_code')
            report_name = request.form.get('report_name')
            report_type = request.form.get('report_type')
            reporting_period = request.form.get('reporting_period')
            description = request.form.get('description')
            
            file_path = ''
            file_size = 0
            
            # 1. Dosya Yükleme Kontrolü
            if 'report_file' in request.files and request.files['report_file'].filename:
                f = request.files['report_file']
                if f and f.filename:
                    import os
                    upload_folder = os.path.join(BACKEND_DIR, 'uploads', 'reports', f"company_{company_id}")
                    os.makedirs(upload_folder, exist_ok=True)
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(f.filename)
                    f_path = os.path.join(upload_folder, filename)
                    f.save(f_path)
                    file_path = f_path
                    file_size = os.path.getsize(f_path)
            
            # 2. Otomatik Rapor Oluşturma (Eğer dosya yüklenmediyse ve modül destekliyorsa)
            elif module_code in ['carbon', 'energy', 'water', 'waste', 'social', 'governance', 'cbam', 'esg', 'tsrs', 'sdg', 'gri', 'taxonomy', 'csrd']:
                try:
                    formats = []
                    if report_type == 'DOCX': formats = ['docx']
                    elif report_type == 'XLSX': formats = ['excel']
                    else: formats = ['docx'] # Varsayılan DOCX
                    
                    period = reporting_period or str(datetime.now().year)
                    generated = {}

                    if module_code == 'carbon':
                        cm = CarbonManager(DB_PATH)
                        cr = CarbonReporting(cm)
                        generated = cr.generate_carbon_report(company_id, period, formats=formats)
                    elif module_code == 'energy':
                        em = EnergyManager(DB_PATH)
                        er = EnergyReporting(em)
                        generated = er.generate_energy_report(company_id, period, formats=formats)
                    elif module_code == 'water':
                        wm = WaterManager(DB_PATH)
                        wr = WaterReporting(wm)
                        generated = wr.generate_water_report(company_id, period, formats=formats)
                    elif module_code == 'waste':
                        wm = WasteManager(DB_PATH)
                        wr = WasteReporting(wm)
                        generated = wr.generate_waste_report(company_id, period, formats=formats)
                    elif module_code == 'social':
                        # SocialReporting direkt db_path alabilir veya default path kullanır
                        sr = SocialReporting(DB_PATH)
                        generated = sr.generate_social_report(company_id, period, formats=formats)
                    elif module_code == 'governance':
                        gm = CorporateGovernanceManager(DB_PATH)
                        gr = GovernanceReporting(gm)
                        generated = gr.generate_governance_report(company_id, period, formats=formats)
                    elif module_code == 'cbam':
                        from backend.modules.cbam.cbam_manager import CBAMManager
                        manager = CBAMManager(DB_PATH)
                        from backend.modules.cbam.cbam_reporting import CBAMReporting
                        cr = CBAMReporting(manager)
                        generated = cr.generate_cbam_report(company_id, period, formats=formats)
                    elif module_code == 'tsrs':
                        from backend.modules.tsrs.tsrs_reporting import TSRSReporting
                        trm = TSRSReporting(DB_PATH)
                        output_dir = os.path.join(BACKEND_DIR, 'uploads', 'reports', f"company_{company_id}")
                        os.makedirs(output_dir, exist_ok=True)
                        pdf_path = os.path.join(output_dir, f"tsrs_report_{company_id}_{period}.pdf")
                        if trm.create_tsrs_pdf_report(company_id, period, pdf_path):
                            generated = {'docx': pdf_path}
                    elif module_code == 'sdg':
                        from backend.modules.sdg.sdg_reporting import SDGReporting
                        srm = SDGReporting(DB_PATH)
                        out_path = srm.generate_sdg_summary_report(company_id, period)
                        if out_path:
                            generated = {'docx': out_path}
                    elif module_code == 'gri':
                        from backend.modules.gri.gri_reporting import GRIReporting
                        grm = GRIReporting(DB_PATH)
                        out_path = grm.generate_gri_index_report(company_id, period)
                        if out_path:
                            generated = {'docx': out_path}
                    elif module_code == 'taxonomy':
                        from backend.modules.eu_taxonomy.taxonomy_manager import TaxonomyManager
                        from backend.modules.eu_taxonomy.taxonomy_reporting import TaxonomyReporting
                        tm = TaxonomyManager(DB_PATH)
                        trm = TaxonomyReporting(tm)
                        output_dir = os.path.join(BACKEND_DIR, 'uploads', 'reports', f"company_{company_id}")
                        os.makedirs(output_dir, exist_ok=True)
                        if 'excel' in formats:
                            excel_path = trm.generate_excel_report(company_id, period, output_dir)
                            if excel_path:
                                generated['excel'] = excel_path
                        if 'docx' in formats:
                            docx_path = trm.generate_docx_report(company_id, period, output_dir)
                            if docx_path:
                                generated['docx'] = docx_path
                    
                    if generated:
                        # İlk üretilen dosyayı al
                        key = formats[0] if formats else 'docx'
                        if key in generated:
                            gen_path = generated[key]
                            # Dosyayı uploads klasörüne taşı
                            import shutil
                            upload_folder = os.path.join(BACKEND_DIR, 'uploads', 'reports', f"company_{company_id}")
                            os.makedirs(upload_folder, exist_ok=True)
                            filename = os.path.basename(gen_path)
                            dest_path = os.path.join(upload_folder, filename)
                            
                            # Eğer dosya zaten varsa üzerine yaz veya taşı
                            shutil.move(gen_path, dest_path)
                            
                            file_path = dest_path
                            file_size = os.path.getsize(dest_path)
                            flash(f'Rapor otomatik olarak oluşturuldu: {filename}', 'success')
                            
                except Exception as e:
                    logging.error(f"Otomatik rapor oluşturma hatası: {e}")
                    flash(f"Rapor oluşturulurken hata: {e}", "warning")
            
            conn = get_db()
            conn.execute("""
                INSERT INTO report_registry 
                (company_id, module_code, report_name, report_type, file_path, file_size, reporting_period, description, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, module_code, report_name, report_type, file_path, file_size, reporting_period, description, session.get('user_id')))
            conn.commit()
            conn.close()

            flash('Rapor kaydı oluşturuldu.', 'success')
            return redirect(url_for('reports'))
        except Exception as e:
            logging.error(f"Error adding report: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('report_edit.html', title='Yeni Rapor')


@app.route('/reports/sustainability_ai', methods=['POST'])
@require_company_context
def generate_sustainability_md_report():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        company_id = g.company_id
        reporting_period = request.form.get('reporting_period') or str(datetime.now().year)
        report_name = request.form.get('report_name') or f"Sürdürülebilirlik Raporu {reporting_period}"
        report_format = (request.form.get('format') or 'docx').lower()

        generator = ReportGenerator(DB_PATH)

        output_dir = os.path.join(BACKEND_DIR, 'uploads', 'reports', f"company_{company_id}")
        os.makedirs(output_dir, exist_ok=True)
        safe_period = str(reporting_period).replace("/", "-").replace("\\", "-").replace(" ", "_")
        base_name = f"sustainability_report_{company_id}_{safe_period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        file_path = None
        report_type = ""

        if report_format == "pdf":
            target_path = os.path.join(output_dir, f"{base_name}.pdf")
            file_path = generator.generate_sustainability_pdf(company_id, reporting_period, target_path)
            report_type = "PDF"
        elif report_format in ("docx", "word"):
            target_path = os.path.join(output_dir, f"{base_name}.docx")
            file_path = generator.generate_sustainability_docx(company_id, reporting_period, target_path)
            report_type = "DOCX"
        else:
            md_content = generator.generate_sustainability_report(company_id, reporting_period)
            target_path = os.path.join(output_dir, f"{base_name}.md")
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            file_path = target_path
            report_type = "MD"

        if not file_path or not os.path.exists(file_path):
            flash("Rapor oluşturulamadı.", "danger")
            return redirect(url_for('reports'))

        try:
            manager = AdvancedReportManager(DB_PATH)
            manager.register_existing_file(
                company_id=company_id,
                module_code="esg",
                report_name=report_name,
                report_type=report_type,
                file_path=file_path,
                reporting_period=reporting_period,
                tags=["sustainability", "ai", report_type.lower()],
                description=f"AI destekli sürdürülebilirlik raporu ({report_type})"
            )
        except Exception as reg_e:
            logging.error(f"Sustainability report registry error: {reg_e}")

        flash(f"AI destekli sürdürülebilirlik {report_type} raporu oluşturuldu.", 'success')
        return redirect(url_for('reports'))
    except Exception as e:
        logging.error(f"Sustainability report error: {e}")
        flash(f"Hata: {e}", "danger")
        return redirect(url_for('reports'))


@app.route('/reports/unified', methods=['GET', 'POST'])
@require_company_context
def unified_report():
    if 'user' not in session:
        return redirect(url_for('login'))

    company_id = g.company_id

    if request.method == 'POST':
        try:
            report_name = request.form.get('report_name') or 'Birleşik Sürdürülebilirlik Raporu'
            reporting_period = request.form.get('reporting_period') or str(datetime.now().year)
            description = request.form.get('description') or ''
            selected_modules: List[str] = request.form.getlist('modules')
            include_ai = request.form.get('include_ai') in ['on', '1', 'true', 'True']

            if not selected_modules:
                flash('En az bir modül seçmelisiniz.', 'warning')
                return redirect(url_for('unified_report'))

            context_for_ai: Dict = {
                'company_id': company_id,
                'reporting_period': reporting_period,
                'modules': selected_modules,
                'module_reports': [],
                'metrics': {}
            }

            try:
                conn = get_db()

                for m in selected_modules:
                    rows = conn.execute(
                        """
                        SELECT id, module_code, report_name, report_type, reporting_period, created_at
                        FROM report_registry
                        WHERE company_id = ? AND module_code = ?
                        ORDER BY created_at DESC
                        LIMIT 1
                        """,
                        (company_id, m),
                    ).fetchall()
                    for r in rows:
                        context_for_ai['module_reports'].append(
                            {
                                'module_code': r['module_code'],
                                'report_name': r['report_name'],
                                'report_type': r['report_type'],
                                'reporting_period': r['reporting_period'],
                                'created_at': r['created_at'],
                            }
                        )

                metrics: Dict[str, Dict[str, float]] = {}
                taxonomy_mappings: List[Dict] = []

                try:
                    rows = conn.execute(
                        """
                        SELECT scope, SUM(co2e_emissions) AS total_co2e
                        FROM carbon_emissions
                        WHERE company_id = ? AND period LIKE ?
                        GROUP BY scope
                        """,
                        (company_id, f"{reporting_period}%"),
                    ).fetchall()
                    metrics['carbon'] = {
                        'total_co2e': sum((r['total_co2e'] or 0) for r in rows),
                        'scope_breakdown': [
                            {'scope': r['scope'], 'co2e': r['total_co2e'] or 0}
                            for r in rows
                        ],
                    }
                except Exception as e:
                    logging.error(f"Unified AI carbon metrics error: {e}")

                try:
                    rows = conn.execute(
                        """
                        SELECT energy_type, SUM(consumption_amount) AS total_consumption
                        FROM energy_consumption
                        WHERE company_id = ? AND year = ?
                        GROUP BY energy_type
                        """,
                        (company_id, reporting_period),
                    ).fetchall()
                    metrics['energy'] = {
                        'total_consumption': sum((r['total_consumption'] or 0) for r in rows),
                        'type_breakdown': [
                            {'energy_type': r['energy_type'], 'consumption': r['total_consumption'] or 0}
                            for r in rows
                        ],
                    }
                except Exception as e:
                    logging.error(f"Unified AI energy metrics error: {e}")

                try:
                    rows = conn.execute(
                        """
                        SELECT source, SUM(consumption_amount) AS total_consumption
                        FROM water_consumption
                        WHERE company_id = ? AND year = ?
                        GROUP BY source
                        """,
                        (company_id, reporting_period),
                    ).fetchall()
                    metrics['water'] = {
                        'total_consumption': sum((r['total_consumption'] or 0) for r in rows),
                        'source_breakdown': [
                            {'water_source': r['source'], 'consumption': r['total_consumption'] or 0}
                            for r in rows
                        ],
                    }
                except Exception as e:
                    logging.error(f"Unified AI water metrics error: {e}")

                try:
                    rows = conn.execute(
                        """
                        SELECT waste_type, SUM(waste_amount) AS total_amount
                        FROM waste_generation
                        WHERE company_id = ? AND (year = ? OR period LIKE ?)
                        GROUP BY waste_type
                        """,
                        (company_id, reporting_period, f"{reporting_period}%"),
                    ).fetchall()
                    metrics['waste'] = {
                        'total_amount': sum((r['total_amount'] or 0) for r in rows),
                        'type_breakdown': [
                            {'waste_type': r['waste_type'], 'amount': r['total_amount'] or 0}
                            for r in rows
                        ],
                    }
                except Exception as e:
                    logging.error(f"Unified AI waste metrics error: {e}")

                try:
                    # SQLite semasina uygun sorgu (id, survey_title, survey_description, response_count, created_at)
                    survey_row = conn.execute(
                        """
                        SELECT id, survey_title, survey_description, response_count, created_at
                        FROM online_surveys
                        WHERE is_active = 1
                        ORDER BY created_at DESC
                        LIMIT 1
                        """
                    ).fetchone()

                    if survey_row:
                        survey_id = survey_row['id']
                        total_responses = survey_row['response_count'] or 0
                        questions_summary = []
                        
                        # Yanitlari topic_code bazinda grupla ve ortalamalari al
                        rows = conn.execute(
                           """
                           SELECT topic_code, AVG(importance_score) as avg_imp
                           FROM survey_responses
                           WHERE survey_id = ?
                           GROUP BY topic_code
                           """,
                           (survey_id,),
                        ).fetchall()
                        
                        totals = {r['topic_code']: (r['avg_imp'] or 0) for r in rows}
                        
                        from backend.modules.stakeholder.stakeholder_engagement import StakeholderEngagement
                        questions_map = {q["id"]: q for q in StakeholderEngagement.SDG17_QUESTION_SET}
                        
                        for code, avg_score in totals.items():
                            q_def = questions_map.get(code)
                            if q_def:
                                questions_summary.append({
                                    "id": code,
                                    "goal": q_def.get("goal"),
                                    "title": q_def.get("title"),
                                    "question": q_def.get("question"),
                                    "avg_score": round(avg_score, 2)
                                })

                        if questions_summary:
                            questions_summary.sort(key=lambda x: x.get("goal") or 0)
                            ordered = sorted(
                                questions_summary,
                                key=lambda x: (x.get("avg_score") if x.get("avg_score") is not None else 0),
                                reverse=True,
                            )
                            strongest = ordered[:3]
                            weakest = list(reversed(ordered[-3:])) if ordered else []
                            metrics["stakeholder_survey"] = {
                                "survey_title": survey_row["survey_title"],
                                "survey_description": survey_row["survey_description"],
                                "created_at": survey_row["created_at"],
                                "response_count": total_responses,
                                "questions": questions_summary,
                                "top3": strongest,
                                "bottom3": weakest,
                            }
                            try:
                                insight_lines = []
                                if strongest:
                                    parts = []
                                    for item in strongest:
                                        g = item.get("goal")
                                        t = item.get("title") or ""
                                        s = item.get("avg_score")
                                        if g is not None and s is not None:
                                            parts.append(f"SDG {g} - {t} (ortalama {s})")
                                    if parts:
                                        insight_lines.append("En guclu hedefler: " + ", ".join(parts))
                                if weakest:
                                    parts = []
                                    for item in weakest:
                                        g = item.get("goal")
                                        t = item.get("title") or ""
                                        s = item.get("avg_score")
                                        if g is not None and s is not None:
                                            parts.append(f"SDG {g} - {t} (ortalama {s})")
                                    if parts:
                                        insight_lines.append("Gelisim gerektiren hedefler: " + ", ".join(parts))
                                if insight_lines:
                                    metrics["stakeholder_survey"]["insights_text"] = " | ".join(insight_lines)
                            except Exception as insight_e:
                                logging.error(f"Unified AI stakeholder survey insights build error: {insight_e}")
                except Exception as e:
                    logging.error(f"Unified AI stakeholder survey metrics error: {e}")

                try:
                    if 'taxonomy' in selected_modules:
                        manager = MANAGERS.get('csrd')
                        if manager:
                            try:
                                year_str = str(reporting_period)
                                year_int = int(year_str[:4])
                            except Exception:
                                year_int = datetime.now().year
                            tax_report = manager.generate_taxonomy_alignment_report(company_id, year_int) or {}
                            metrics['taxonomy'] = {
                                'assessment_year': tax_report.get('assessment_year'),
                                'total_revenue': tax_report.get('total_revenue', 0),
                                'aligned_revenue': tax_report.get('aligned_revenue', 0),
                                'alignment_percentage_revenue': tax_report.get('alignment_percentage_revenue', 0),
                                'total_capex': tax_report.get('total_capex', 0),
                                'aligned_capex': tax_report.get('aligned_capex', 0),
                                'alignment_percentage_capex': tax_report.get('alignment_percentage_capex', 0),
                                'total_opex': tax_report.get('total_opex', 0),
                                'aligned_opex': tax_report.get('aligned_opex', 0),
                                'alignment_percentage_opex': tax_report.get('alignment_percentage_opex', 0),
                                'by_objective': tax_report.get('by_objective', {}),
                            }
                            try:
                                config_path = os.path.join(BACKEND_DIR, 'config', 'eu_taxonomy_config.json')
                                objective_names = {}
                                if os.path.exists(config_path):
                                    with open(config_path, 'r', encoding='utf-8') as f:
                                        cfg = json.load(f)
                                        for obj in cfg.get('objectives', []):
                                            oid = obj.get('id')
                                            if oid:
                                                objective_names[oid] = obj.get('name_tr') or obj.get('name') or oid
                                tax_year = tax_report.get('assessment_year') or year_int
                                rows = conn.execute(
                                    """
                                    SELECT a.activity_code,
                                           a.activity_name,
                                           o.objective_code,
                                           m.sdg_target,
                                           m.gri_disclosure,
                                           m.tsrs_metric
                                    FROM eu_taxonomy_alignment a
                                    LEFT JOIN eu_taxonomy_objectives o ON o.alignment_id = a.id
                                    LEFT JOIN taxonomy_framework_mapping m
                                      ON m.activity_code = a.activity_code
                                     AND m.objective_code = o.objective_code
                                    WHERE a.company_id = ? AND a.assessment_year = ?
                                    """,
                                    (company_id, tax_year),
                                ).fetchall()
                                aggregated: Dict[str, Dict] = {}
                                for row in rows:
                                    code = row['objective_code']
                                    if not code:
                                        continue
                                    key = str(code)
                                    if key not in aggregated:
                                        aggregated[key] = {
                                            'objective_code': key,
                                            'objective_name_tr': objective_names.get(key, key),
                                            'activities': set(),
                                            'sdg_targets': set(),
                                            'gri_disclosures': set(),
                                            'tsrs_metrics': set(),
                                        }
                                    item = aggregated[key]
                                    activity_code = row['activity_code']
                                    if activity_code:
                                        item['activities'].add(activity_code)
                                    if row['sdg_target']:
                                        item['sdg_targets'].add(row['sdg_target'])
                                    if row['gri_disclosure']:
                                        item['gri_disclosures'].add(row['gri_disclosure'])
                                    if row['tsrs_metric']:
                                        item['tsrs_metrics'].add(row['tsrs_metric'])
                                for obj_code, item in aggregated.items():
                                    taxonomy_mappings.append(
                                        {
                                            'objective_code': item['objective_code'],
                                            'objective_name_tr': item['objective_name_tr'],
                                            'activities': sorted(item['activities']) if item['activities'] else [],
                                            'sdg_targets': sorted(item['sdg_targets']) if item['sdg_targets'] else [],
                                            'gri_disclosures': sorted(item['gri_disclosures']) if item['gri_disclosures'] else [],
                                            'tsrs_metrics': sorted(item['tsrs_metrics']) if item['tsrs_metrics'] else [],
                                        }
                                    )
                            except Exception as map_e:
                                logging.error(f"Unified AI taxonomy mapping error: {map_e}")
                except Exception as e:
                    logging.error(f"Unified AI taxonomy metrics error: {e}")

                # --- YENİ EKLENEN: Materiality ve ESRS Verileri ---
                try:
                    mat_rows = conn.execute("""
                        SELECT topic_name, category, priority_score
                        FROM materiality_topics
                        WHERE company_id = ?
                        ORDER BY priority_score DESC
                        LIMIT 5
                    """, (company_id,)).fetchall()
                    
                    metrics['materiality'] = {
                        'top_priority_topics': [
                            {'topic': r['topic_name'], 'category': r['category'], 'score': r['priority_score']}
                            for r in mat_rows
                        ]
                    }
                except Exception as e:
                    logging.error(f"Unified AI materiality metrics error: {e}")

                try:
                    esrs_stats = conn.execute("""
                        SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN completion_status = 'tamamlandi' THEN 1 ELSE 0 END) as completed,
                            SUM(CASE WHEN is_material = 1 THEN 1 ELSE 0 END) as material_count
                        FROM esrs_disclosures
                        WHERE company_id=?
                    """, (company_id,)).fetchone()
                    
                    if esrs_stats:
                        metrics['esrs'] = {
                            'total_disclosures': esrs_stats[0],
                            'completed': esrs_stats[1] or 0,
                            'material_count': esrs_stats[2] or 0
                        }
                except Exception as e:
                    logging.error(f"Unified AI esrs metrics error: {e}")
                # --------------------------------------------------

                context_for_ai['metrics'] = metrics
                if taxonomy_mappings:
                    context_for_ai['taxonomy_mappings'] = taxonomy_mappings
                try:
                    from modules.ai.ai_manager import AIManager
                    ai_snapshot_manager = AIManager(DB_PATH)
                    snapshot = ai_snapshot_manager.build_unified_kpi_snapshot(
                        company_id=company_id,
                        reporting_period=reporting_period,
                        selected_modules=selected_modules,
                    )
                    if snapshot:
                        context_for_ai['kpi_snapshot'] = snapshot
                        kpis = snapshot.get('kpis')
                        if kpis:
                            context_for_ai['kpis'] = kpis
                except Exception as snap_e:
                    logging.error(f"Unified AI KPI snapshot error: {snap_e}")
                conn.close()
            except Exception as e:
                logging.error(f"Birleşik rapor için modül raporları okunamadı: {e}")

            ai_comment = ''
            if include_ai:
                try:
                    from modules.ai.ai_manager import AIManager

                    ai_manager = AIManager(DB_PATH)
                    ai_comment = ai_manager.generate_summary(context_for_ai, report_type='unified') or ''
                except Exception as e:
                    logging.error(f"AI yorumlama hatası: {e}")
                    ai_comment = f"AI yorumlama kullanılamıyor: {e}"

            from modules.reporting.unified_report_docx import UnifiedReportDocxGenerator

            generator = UnifiedReportDocxGenerator(BACKEND_DIR)
            file_path = generator.generate(
                company_id=company_id,
                reporting_period=reporting_period,
                report_name=report_name,
                selected_modules=selected_modules,
                module_reports=context_for_ai['module_reports'],
                ai_comment=ai_comment,
                description=description,
                metrics=context_for_ai['metrics'],
            )

            if not file_path or not os.path.exists(file_path):
                raise Exception("Birleşik DOCX raporu oluşturulamadı")

            file_size = os.path.getsize(file_path)

            conn = get_db()
            cur = conn.execute(
                """
                INSERT INTO report_registry 
                (company_id, module_code, report_name, report_type, file_path, file_size, reporting_period, description, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    company_id,
                    'unified',
                    report_name,
                    'AI-DOCX' if include_ai else 'DOCX',
                    file_path,
                    file_size,
                    reporting_period,
                    description,
                    session.get('user_id'),
                ),
            )
            conn.commit()
            report_id = cur.lastrowid
            conn.close()

            flash('Birleşik sürdürülebilirlik raporu oluşturuldu.', 'success')
            if report_id:
                return redirect(url_for('view_report', report_id=report_id))
            return redirect(url_for('reports'))
        except Exception as e:
            logging.error(f"Birleşik rapor oluşturma hatası: {e}")
            flash(f'Hata: {e}', 'danger')

    try:
        default_reporting_period = session.get('reporting_period') or str(datetime.now().year)
    except Exception:
        default_reporting_period = str(datetime.now().year)
    default_report_name = 'Birleşik Sürdürülebilirlik Raporu'
    survey_summary = None
    try:
        conn = get_db()
        survey_row = conn.execute(
            """
            SELECT id, survey_title, survey_description, response_count, created_at
            FROM online_surveys
            WHERE company_id = ?
              AND survey_title = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (company_id, "Genel Paydaş Sürdürülebilirlik Anketi (SDG 1-17)"),
        ).fetchone()
        if survey_row:
            responses_rows = conn.execute(
                """
                SELECT responses
                FROM survey_responses
                WHERE survey_id = ?
                """,
                (survey_row['id'],),
            ).fetchall()
            totals: Dict[str, Dict[str, float]] = {}
            total_responses = 0
            for row in responses_rows:
                try:
                    data = json.loads(row['responses'] or "{}")
                except Exception:
                    continue
                has_answer = False
                for key, value in data.items():
                    if not isinstance(key, str) or not key.startswith("SDG"):
                        continue
                    try:
                        score = float(value)
                    except (TypeError, ValueError):
                        continue
                    item = totals.setdefault(key, {"sum": 0.0, "count": 0})
                    item["sum"] += score
                    item["count"] += 1
                    has_answer = True
                if has_answer:
                    total_responses += 1
            if totals:
                questions_map = {q["id"]: q for q in StakeholderEngagement.SDG17_QUESTION_SET}
                questions_summary = []
                for qid, agg in totals.items():
                    meta = questions_map.get(qid, {})
                    count = agg["count"] or 0
                    avg_score = round(agg["sum"] / count, 2) if count else 0
                    questions_summary.append(
                        {
                            "id": qid,
                            "goal": meta.get("goal"),
                            "title": meta.get("title") or qid,
                            "question": meta.get("question") or "",
                            "avg_score": avg_score,
                            "response_count": count,
                        }
                    )
                questions_summary.sort(key=lambda x: x.get("goal") or 0)
                ordered = sorted(
                    questions_summary,
                    key=lambda x: (x.get("avg_score") if x.get("avg_score") is not None else 0),
                    reverse=True,
                )
                strongest = ordered[:3]
                weakest = list(reversed(ordered[-3:])) if ordered else []
                insights_text = None
                try:
                    lines = []
                    if strongest:
                        parts = []
                        for item in strongest:
                            g = item.get("goal")
                            t = item.get("title") or ""
                            s = item.get("avg_score")
                            if g is not None and s is not None:
                                parts.append(f"SDG {g} - {t} (ortalama {s})")
                        if parts:
                            lines.append("En guclu hedefler: " + ", ".join(parts))
                    if weakest:
                        parts = []
                        for item in weakest:
                            g = item.get("goal")
                            t = item.get("title") or ""
                            s = item.get("avg_score")
                            if g is not None and s is not None:
                                parts.append(f"SDG {g} - {t} (ortalama {s})")
                        if parts:
                            lines.append("Gelisim gerektiren hedefler: " + ", ".join(parts))
                    if lines:
                        insights_text = " | ".join(lines)
                except Exception as e:
                    logging.error(f"Unified survey summary insights build error: {e}")
                survey_summary = {
                    "survey_title": survey_row["survey_title"],
                    "survey_description": survey_row["survey_description"],
                    "created_at": survey_row["created_at"],
                    "response_count": total_responses,
                    "top3": strongest,
                    "bottom3": weakest,
                    "insights_text": insights_text,
                }
        suggested_modules: List[str] = []
        try:
            try:
                row = conn.execute("SELECT COUNT(*) FROM carbon_emissions WHERE company_id=?", (company_id,)).fetchone()
                if row and row[0]:
                    suggested_modules.append('carbon')
            except Exception:
                pass
            try:
                row = conn.execute("SELECT COUNT(*) FROM energy_consumption WHERE company_id=?", (company_id,)).fetchone()
                if row and row[0]:
                    suggested_modules.append('energy')
            except Exception:
                pass
            try:
                row = conn.execute("SELECT COUNT(*) FROM water_consumption WHERE company_id=?", (company_id,)).fetchone()
                if row and row[0]:
                    suggested_modules.append('water')
            except Exception:
                pass
            try:
                row = conn.execute("SELECT COUNT(*) FROM waste_generation WHERE company_id=?", (company_id,)).fetchone()
                if row and row[0]:
                    suggested_modules.append('waste')
            except Exception:
                pass
            framework_modules = ['cbam', 'sdg', 'gri', 'tsrs', 'taxonomy', 'csrd', 'tcfd', 'tnfd', 'cdp', 'issb', 'esrs']
            for code in framework_modules:
                try:
                    row = conn.execute(
                        "SELECT COUNT(*) FROM report_registry WHERE company_id=? AND module_code=?",
                        (company_id, code),
                    ).fetchone()
                    if row and row[0] and code not in suggested_modules:
                        suggested_modules.append(code)
                except Exception:
                    pass
        finally:
            conn.close()
    except Exception as e:
        logging.error(f"Unified report suggested modules error: {e}")
        suggested_modules = []

    return render_template(
        'unified_report.html',
        title='Birleşik Rapor',
        default_report_name=default_report_name,
        default_reporting_period=default_reporting_period,
        suggested_modules=suggested_modules,
        survey_summary=survey_summary,
    )


@app.route('/reports/download/<int:report_id>')
@require_company_context
def report_download(report_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        conn = get_db()
        report = conn.execute("SELECT * FROM report_registry WHERE id=? AND company_id=?", (report_id, g.company_id)).fetchone()
        conn.close()

        if not report:
            flash('Rapor bulunamadı.', 'warning')
            return redirect(url_for('reports'))

        file_path = report['file_path']
        if not file_path or not os.path.exists(file_path):
            flash('Dosya sunucuda bulunamadı.', 'danger')
            return redirect(url_for('reports'))

        download_name = report['report_name'] if report['report_name'] else 'report'
        _, ext = os.path.splitext(file_path)
        return send_file(file_path, as_attachment=True, download_name=download_name + ext)

    except Exception as e:
        logging.error(f"Error downloading report: {e}")
        flash(f'Hata: {e}', 'danger')
        return redirect(url_for('reports'))


@app.route('/reports/view/<int:report_id>')
@require_company_context
def view_report(report_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        conn = get_db()
        report = conn.execute("SELECT * FROM report_registry WHERE id=? AND company_id=?", (report_id, g.company_id)).fetchone()
        conn.close()

        if not report:
            flash('Rapor bulunamadı.', 'warning')
            return redirect(url_for('reports'))

        file_path = report['file_path']
        if not file_path or not os.path.exists(file_path):
            flash('Dosya sunucuda bulunamadı.', 'danger')
            return redirect(url_for('reports'))

        download_name = report['report_name'] if report['report_name'] else 'report'
        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()
        mimetype = None
        if ext_lower == '.pdf':
            mimetype = 'application/pdf'
        elif ext_lower == '.docx':
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif ext_lower == '.doc':
            mimetype = 'application/msword'
        elif ext_lower == '.xlsx':
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        return send_file(file_path, mimetype=mimetype, as_attachment=False, download_name=download_name + ext)

    except Exception as e:
        logging.error(f"Error viewing report: {e}")
        flash(f'Hata: {e}', 'danger')
        return redirect(url_for('reports'))


@app.route('/reports/delete/<int:report_id>', methods=['POST'])
@require_company_context
def report_delete(report_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        conn = get_db()
        report = conn.execute("SELECT file_path FROM report_registry WHERE id=? AND company_id=?", (report_id, g.company_id)).fetchone()

        if report and report['file_path'] and os.path.exists(report['file_path']):
            try:
                os.remove(report['file_path'])
            except Exception as e:
                logging.error(f"Error deleting file: {e}")

        conn.execute("DELETE FROM report_registry WHERE id=? AND company_id=?", (report_id, g.company_id))
        conn.commit()
        conn.close()
        flash('Rapor silindi.', 'success')

    except Exception as e:
        logging.error(f"Error deleting report: {e}")
        flash(f'Hata: {e}', 'danger')

    return redirect(url_for('reports'))

@app.route('/api/ai/feedback', methods=['POST'])
@require_company_context
def save_ai_feedback():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        report_id = data.get('report_id')
        rating = data.get('rating')
        comment = data.get('comment', '')

        if not report_id or not rating:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        conn = get_db()
        # Verify report exists and belongs to company
        report = conn.execute("SELECT id FROM report_registry WHERE id=? AND company_id=?", (report_id, g.company_id)).fetchone()
        if not report:
            conn.close()
            return jsonify({'success': False, 'message': 'Report not found'}), 404

        conn.execute(
            """
            INSERT INTO ai_feedback (report_id, user_id, company_id, rating, comment)
            VALUES (?, ?, ?, ?, ?)
            """,
            (report_id, session.get('user_id'), g.company_id, rating, comment)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Feedback saved'})
    except Exception as e:
        logging.error(f"Error saving feedback: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# --- Module Routes ---

from mapping.sdg_gri_mapping import SDGGRIMapping

@app.route('/sdg', methods=['GET', 'POST'])
@require_company_context
def sdg_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('sdg')
    company_id = g.company_id

    # Fallback initialization if manager is missing (though it should be there)
    if not manager:
        flash('SDG Modülü yüklenemedi.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        conn = get_db()
        cur = conn.execute("SELECT COUNT(*) FROM sdg_goals")
        row = cur.fetchone()
        total_goals = row[0] if row else 0
        if total_goals == 0:
            goals_data = [
                (1, "Yoksulluğa Son", "Yoksulluğun tüm biçimlerini her yerde sona erdirmek"),
                (2, "Açlığa Son", "Açlığı bitirmek, gıda güvenliğini sağlamak ve iyi beslenmeyi desteklemek"),
                (3, "Sağlık ve Kaliteli Yaşam", "Sağlıklı ve kaliteli yaşamı her yaşta güvence altına almak"),
                (4, "Nitelikli Eğitim", "Kapsayıcı ve hakkaniyetli nitelikli eğitimi sağlamak"),
                (5, "Toplumsal Cinsiyet Eşitliği", "Toplumsal cinsiyet eşitliğini sağlamak ve tüm kadınlar ile kız çocuklarını güçlendirmek"),
                (6, "Temiz Su ve Sanitasyon", "Herkes için erişilebilir su ve atıksu yönetimi sağlamak"),
                (7, "Erişilebilir ve Temiz Enerji", "Herkes için uygun maliyetli, güvenilir, sürdürülebilir ve modern enerjiye erişimi sağlamak"),
                (8, "İnsana Yakışır İş ve Ekonomik Büyüme", "İstikrarlı, kapsayıcı ve sürdürülebilir ekonomik büyümeyi desteklemek"),
                (9, "Sanayi, Yenilikçilik ve Altyapı", "Dayanıklı altyapılar tesis etmek, kapsayıcı ve sürdürülebilir sanayileşmeyi desteklemek"),
                (10, "Eşitsizliklerin Azaltılması", "Ülkelerin içinde ve arasındaki eşitsizlikleri azaltmak"),
                (11, "Sürdürülebilir Şehirler ve Topluluklar", "Şehirleri ve insan yerleşimlerini kapsayıcı, güvenli, dayanıklı ve sürdürülebilir kılmak"),
                (12, "Sorumlu Üretim ve Tüketim", "Sürdürülebilir üretim ve tüketim kalıplarını sağlamak"),
                (13, "İklim Eylemi", "İklim değişikliği ve etkileri ile mücadele için acil eyleme geçmek"),
                (14, "Sudaki Yaşam", "Sürdürülebilir kalkınma için okyanusları, denizleri ve deniz kaynaklarını korumak"),
                (15, "Karasal Yaşam", "Karasal ekosistemleri korumak, iyileştirmek ve sürdürülebilir kullanımını desteklemek"),
                (16, "Barış, Adalet ve Güçlü Kurumlar", "Sürdürülebilir kalkınma için barışçıl ve kapsayıcı toplumlar tesis etmek"),
                (17, "Amaçlar için Ortaklıklar", "Uygulama araçlarını güçlendirmek ve sürdürülebilir kalkınma için küresel ortaklığı canlandırmak")
            ]
            try:
                cur = conn.execute("PRAGMA table_info(sdg_goals)")
                cols = [c[1] for c in cur.fetchall()]
            except Exception:
                cols = []
            has_code = "code" in cols
            has_description = "description" in cols
            for goal_item in goals_data:
                code = goal_item[0]
                title = goal_item[1]
                desc = goal_item[2]
                if has_code and has_description:
                    conn.execute(
                        "INSERT OR IGNORE INTO sdg_goals (id, code, title_tr, description, company_id) VALUES (?, ?, ?, ?, ?)",
                        (code, code, title, desc, company_id),
                    )
                elif has_code:
                    conn.execute(
                        "INSERT OR IGNORE INTO sdg_goals (id, code, title_tr, company_id) VALUES (?, ?, ?, ?)",
                        (code, code, title, company_id),
                    )
                else:
                    conn.execute(
                        "INSERT OR IGNORE INTO sdg_goals (id, title_tr, company_id) VALUES (?, ?, ?)",
                        (code, title, company_id),
                    )
            conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"SDG master data init error: {e}")

    # Handle POST - Selection Saving
    if request.method == 'POST' and 'save_selections' in request.form:
        try:
            selected_ids = [int(x) for x in request.form.getlist('selected_goals')]
            if manager.save_selected_goals(company_id, selected_ids):
                flash('SDG Hedef seçimleriniz güncellendi.', 'success')
            else:
                flash('Seçimler kaydedilirken bir hata oluştu.', 'danger')
        except Exception as e:
            logging.error(f"SDG save error: {e}")
            flash(f'Hata: {e}', 'danger')
        return redirect(url_for('sdg_module'))

    # Fetch Data using Manager
    try:
        # Get all goals
        # manager.get_all_goals returns dicts
        all_goals = manager.get_all_goals()
        
        # Get selected goal IDs
        selected_ids = manager.get_selected_goals(company_id)
        
        # Get Statistics
        stats = manager.get_statistics(company_id)
        
        # Fetch detailed structure for selected goals
        selected_goals_details = []
        mapping_data = [] 
        
        # Get Recent Responses
        recent_data = manager.get_recent_responses(company_id)

        if selected_ids:
            # 1. Fetch Mapping Data (GRI, Questions, etc.)
            try:
                # Initialize mapper with DB path (optional if default works)
                mapper = SDGGRIMapping()
                mapping_data = mapper.get_questions_for_goals(selected_ids)
            except Exception as e:
                logging.error(f"SDG Mapping error: {e}")

            # Prepare details for selected goals
            # We filter all_goals for selected ones
            selected_goals_objs = [g for g in all_goals if g['id'] in selected_ids]
            
            for goal in selected_goals_objs:
                g_detail = {
                    'id': goal['id'],
                    'title': goal['title'],
                    # description might not be in get_all_goals output depending on manager, check manager
                    'description': goal.get('description', ''), 
                    'targets': [],
                    'module_link': None
                }
                
                # Determine Module Link - Expanded Logic
                # Mapping: Goal -> Module Route Name
                module_map = {
                    1: {'url': 'social_module', 'name': 'Sosyal Etki (Yoksulluk)'},
                    2: {'url': 'social_module', 'name': 'Sosyal Etki (Açlık)'},
                    3: {'url': 'social_module', 'name': 'Sağlık ve Refah'},
                    4: {'url': 'social_module', 'name': 'Eğitim'},
                    5: {'url': 'social_module', 'name': 'Sosyal Etki (Cinsiyet Eşitliği)'},
                    6: {'url': 'water_module', 'name': 'Su Yönetimi'},
                    7: {'url': 'energy_module', 'name': 'Enerji Yönetimi'},
                    8: {'url': 'economic_module', 'name': 'Ekonomik Göstergeler'},
                    9: {'url': 'supply_chain_module', 'name': 'Sanayi ve Altyapı'},
                    10: {'url': 'social_module', 'name': 'Eşitsizliklerin Azaltılması'},
                    11: {'url': 'waste_module', 'name': 'Şehirler ve Toplumlar'},
                    12: {'url': 'waste_module', 'name': 'Sorumlu Tüketim ve Üretim'},
                    13: {'url': 'carbon_module', 'name': 'İklim Eylemi'},
                    14: {'url': 'biodiversity_module', 'name': 'Sudaki Yaşam'},
                    15: {'url': 'biodiversity_module', 'name': 'Karasal Yaşam'},
                    16: {'url': 'governance_module', 'name': 'Barış, Adalet ve Güçlü Kurumlar'},
                    17: {'url': 'governance_module', 'name': 'Amaçlar için Ortaklıklar'}
                }
                
                if goal['id'] in module_map:
                    m_info = module_map[goal['id']]
                    if m_info['url'] in app.view_functions:
                         g_detail['module_link'] = {'url': url_for(m_info['url']), 'name': m_info['name']}

                # Get Targets and Indicators via Manager
                targets = manager.get_goal_targets(goal['id'])
                for target in targets:
                    t_detail = {
                        'id': target['id'],
                        'code': target['code'],
                        'title': target['title'],
                        'indicators': []
                    }
                    
                    indicators = manager.get_target_indicators(target['id'])
                    for ind in indicators:
                        i_detail = {
                            'id': ind['id'],
                            'code': ind['code'],
                            'title': ind['title'],
                            'gri_mappings': []
                        }
                        
                        # Get GRI Mappings (Manual SQL for now as manager doesn't seem to expose this directly yet, or use Mapping class)
                        try:
                            conn = get_db()
                            mappings = conn.execute("""
                                SELECT gri_disclosure, relation_type 
                                FROM map_sdg_gri 
                                WHERE sdg_indicator_code = ?
                            """, (ind['code'],)).fetchall()
                            i_detail['gri_mappings'] = [{'code': m['gri_disclosure'], 'type': m['relation_type']} for m in mappings]
                            conn.close()
                        except:
                            pass
                            
                        t_detail['indicators'].append(i_detail)
                    
                    g_detail['targets'].append(t_detail)
                
                selected_goals_details.append(g_detail)

        # Progress records (manual for now as manager might not have it fully aligned with this view yet)
        # Or check if manager has get_responses? It does.
        # But existing template expects 'sdg_progress' table structure which is different from 'responses' table in manager.
        # For now, let's keep the manual 'sdg_progress' fetch for backward compatibility if the template uses it.
        # However, the user wants desktop replication. Desktop uses 'responses'.
        # Let's try to align.
        
        # Check if we should use manager responses
        # The manager.get_responses returns a list of dicts.
        # We might need to adapt it for the template.
        
        progress_records = []
        try:
             # Use manager's responses if available
             responses = manager.get_responses(company_id)
             for r in responses:
                 progress_records.append({
                     'goal_title': r['goal_title'],
                     'target': r['indicator_code'], # Mapping indicator to target column for display
                     'action': r['action'] or '',
                     'status': r['status'],
                     'progress_pct': r['progress_pct'],
                     'created_at': r['period'] # or use period
                 })
        except Exception as e:
            logging.error(f"Error fetching manager responses: {e}")

        # If manager responses are empty, maybe fallback to old table?
        # But we are moving to manager.
        
        return render_template('sdg.html', 
                             title=_('sdg_title'), 
                             manager_available=True, 
                             stats=stats, 
                             progress_records=progress_records,
                             all_goals=all_goals,
                             selected_ids=selected_ids,
                             selected_goals_details=selected_goals_details,
                             mapping_data=mapping_data,
                             recent_data=recent_data)
                             
    except Exception as e:
        logging.error(f"SDG module error: {e}")
        import traceback
        traceback.print_exc()
        flash(f"Bir hata oluştu: {e}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/sdg/add', methods=['GET', 'POST'])
@require_company_context
def sdg_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    # Initialize manager
    from modules.sdg.sdg_manager import SDGManager
    manager = SDGManager(DB_PATH)
    
    indicator_id = request.args.get('indicator_id')
    indicator = None
    
    if indicator_id:
        try:
            conn = get_db()
            row = conn.execute("SELECT id, code, title_tr, kpi_metric as unit, measurement_frequency as frequency FROM sdg_indicators WHERE id = ?", (indicator_id,)).fetchone()
            if row:
                indicator = {
                    'id': row[0],
                    'code': row[1],
                    'title': row[2],
                    'unit': row[3],
                    'frequency': row[4]
                }
            conn.close()
        except Exception as e:
            logging.error(f"Error fetching indicator: {e}")

    if request.method == 'POST':
        try:
            company_id = g.company_id
            year = request.form.get('year')
            
            # Check if we have indicator_id from form
            form_indicator_id = request.form.get('indicator_id')
            
            if form_indicator_id:
                action = request.form.get('action') or request.form.get('notes')
                status = request.form.get('status')
                progress_pct = request.form.get('progress_pct', 0)
                value = request.form.get('value', 0)
                
                # Save using Manager
                manager.save_response(
                    company_id=company_id,
                    indicator_id=int(form_indicator_id),
                    period=str(year),
                    answer_json="{}",
                    value_num=float(value),
                    progress_pct=int(progress_pct),
                    notes=action
                )
                
                # Note: Status is not updated via save_response in current version, defaults to 'Gönderilmedi'
                # If needed, we can update it manually or extend Manager.
                
                flash('SDG ilerlemesi kaydedildi.', 'success')
                return redirect(url_for('sdg_module'))
            
            else:
                # Fallback to legacy
                goal_id = request.form.get('goal_id')
                target = request.form.get('target')
                action = request.form.get('action')
                status = request.form.get('status')
                progress_pct = request.form.get('progress_pct')
                
                conn = get_db()
                conn.execute("""
                    INSERT INTO sdg_progress 
                    (company_id, year, goal_id, target, action, status, progress_pct, created_at) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (company_id, year, goal_id, target, action, status, progress_pct))
                conn.commit()
                conn.close()
                flash('SDG ilerlemesi kaydedildi.', 'success')
                return redirect(url_for('sdg_module'))
        except Exception as e:
            logging.error(f"Error adding SDG data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('sdg_edit.html', title='SDG Veri Girişi', indicator=indicator)

@app.route('/gri')
@require_company_context
def gri_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    stats = {
        'total_disclosures': 0,
        'standards_covered': 0,
        'completion_rate': 0
    }
    standards = []
    company_id = g.company_id
    
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gri_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER,
                standard TEXT,
                disclosure TEXT,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # Fetch data with sector info
        rows = conn.execute("""
            SELECT d.*, s.sector, s.title as standard_title
            FROM gri_data d
            LEFT JOIN gri_standards s ON d.standard = s.code
            WHERE d.company_id = ? 
            ORDER BY d.created_at DESC
        """, (company_id,)).fetchall()
        standards = [dict(r) for r in rows]
        
        # Fetch all standards for dropdown
        try:
            all_standards_rows = conn.execute("SELECT code, title, sector FROM gri_standards ORDER BY code").fetchall()
            all_standards = [dict(r) for r in all_standards_rows]
        except Exception as e:
            logging.error(f"Error fetching gri_standards: {e}")
            all_standards = []
        
        # Calculate stats
        stats['total_disclosures'] = len(standards)
        stats['standards_covered'] = len(set([s['standard'] for s in standards]))
        
        # Mock completion rate (assuming target is ~20 key disclosures)
        stats['completion_rate'] = min(100, int((stats['total_disclosures'] / 20) * 100))
        
        conn.close()
    except Exception as e:
        logging.error(f"GRI module error: {e}")
        all_standards = []

    return render_template('gri.html', title='GRI Raporlama', manager_available=bool(MANAGERS.get('gri')), stats=stats, standards=standards, all_standards=all_standards)

@app.route('/api/gri/indicators/<standard_code>')
@require_company_context
def get_gri_indicators_api(standard_code):
    if 'user' not in session: return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db()
        # Get standard ID first
        std = conn.execute("SELECT id FROM gri_standards WHERE code = ?", (standard_code,)).fetchone()
        if not std:
            return jsonify({'indicators': []})
            
        std_id = std[0]
        rows = conn.execute("""
            SELECT code, title, unit 
            FROM gri_indicators 
            WHERE standard_id = ? 
            ORDER BY code
        """, (std_id,)).fetchall()
        
        indicators = [dict(r) for r in rows]
        return jsonify({'indicators': indicators})
    except Exception as e:
        logging.error(f"Error fetching GRI indicators: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/gri/add', methods=['GET', 'POST'])
@require_company_context
def gri_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            company_id = g.company_id
            year = request.form.get('year')
            standard = request.form.get('standard')
            disclosure = request.form.get('disclosure')
            value = request.form.get('value')
            
            conn = get_db()
            conn.execute("""
                INSERT INTO gri_data 
                (company_id, year, standard, disclosure, value, created_at) 
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, year, standard, disclosure, value))
            conn.commit()
            conn.close()
            flash('GRI verisi başarıyla eklendi.', 'success')
            return redirect(url_for('gri_module'))
        except Exception as e:
            logging.error(f"Error adding GRI data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('gri_edit.html', title='GRI Veri Girişi')

@app.route('/cdp', methods=['GET', 'POST'])
@require_company_context
def cdp_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('cdp')
    company_id = g.company_id
    
    # Handle POST - Save Responses
    if request.method == 'POST':
        try:
            q_type = request.form.get('questionnaire_type')
            if q_type and manager:
                # Iterate form data to find answers
                # Expected format: question_{id}
                count = 0
                for key, value in request.form.items():
                    if key.startswith('question_'):
                        q_id = key.replace('question_', '')
                        # Save if value is not empty or different?
                        # For now, save all submitted
                        manager.save_response(q_type, company_id, q_id, value)
                        count += 1
                
                # Recalculate scores after save
                manager.calculate_scores(q_type, company_id)
                flash(f'{count} yanıt kaydedildi.', 'success')
            return redirect(url_for('cdp_module', type=q_type))
        except Exception as e:
            logging.error(f"CDP save error: {e}")
            flash(f'Hata: {e}', 'danger')

    # Default View
    current_type = request.args.get('type', 'Climate Change')
    valid_types = ['Climate Change', 'Water Security', 'Forests']
    if current_type not in valid_types:
        current_type = 'Climate Change'

    stats = {
        'climate_score': '-',
        'water_score': '-',
        'forests_score': '-'
    }
    
    questions = []
    responses_map = {}
    
    try:
        if manager:
            # Get stats for all types
            for t in valid_types:
                s = manager.calculate_scores(t, company_id)
                if t == 'Climate Change': stats['climate_score'] = s.get('grade', '-')
                elif t == 'Water Security': stats['water_score'] = s.get('grade', '-')
                elif t == 'Forests': stats['forests_score'] = s.get('grade', '-')

            # Get questions for current type
            questions = manager.get_questions(current_type, company_id)
            
            # Get existing responses to pre-fill
            responses = manager.get_company_responses(current_type, company_id)
            responses_map = {r['question_id']: r['response'] for r in responses}
            
        else:
            # Fallback (keep existing logic or show error)
            pass
            
    except Exception as e:
        logging.error(f"CDP module error: {e}")
        
    return render_template('cdp.html', 
                         title=_('cdp_page_title'),
                         manager_available=bool(manager),
                         stats=stats,
                         current_type=current_type,
                         questions=questions,
                         responses_map=responses_map)

@app.route('/cdp/add')
@require_company_context
def cdp_add():
    # Redirect to main module as we integrated entry there
    return redirect(url_for('cdp_module'))

@app.route('/social')
@require_company_context
def social_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('social')
    company_id = g.company_id
    
    stats = {'employees': 0, 'incidents': 0, 'training_hours': 0}
    recent_data = []
    trends = {'years': [], 'satisfaction': [], 'turnover': []}

    if manager:
        try:
            stats = manager.get_stats(company_id)
            recent_data = manager.get_recent_data(company_id)
            trends = manager.get_satisfaction_trends(company_id)
        except Exception as e:
            logging.error(f"Error in social manager fetch: {e}")
            
    return render_template('social.html', title='Sosyal Etki', stats=stats, recent_data=recent_data, trends=trends)


@app.route('/social/export')
@require_company_context
def social_export():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('social')
    company_id = g.company_id
    
    if manager:
        try:
            output = manager.export_social_data(company_id)
            if output:
                return send_file(
                    output,
                    as_attachment=True,
                    download_name=f'social_report_{company_id}_{datetime.now().strftime("%Y%m%d")}.xlsx',
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                flash('Rapor oluşturulamadı.', 'danger')
        except Exception as e:
            logging.error(f"Error exporting social data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return redirect(url_for('social_module'))


@app.route('/social/add', methods=['GET', 'POST'])
@require_company_context
def social_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_type = request.args.get('type', 'employee')
    
    if request.method == 'POST':
        try:
            manager = MANAGERS.get('social')
            if not manager:
                raise Exception("Social Manager not initialized")

            dtype = request.form.get('data_type')
            company_id = g.company_id
            
            if dtype == 'employee':
                count = int(request.form.get('employee_count', 0))
                gender = request.form.get('gender')
                dept = request.form.get('department')
                age = request.form.get('age_group')
                year = int(request.form.get('year', 2024))
                manager.add_employee_data(company_id, count, gender, dept, age, year)
                
            elif dtype == 'ohs':
                itype = request.form.get('incident_type')
                date = request.form.get('date')
                severity = request.form.get('severity')
                desc = request.form.get('description')
                lost = int(request.form.get('lost_time_days', 0))
                manager.add_ohs_incident(company_id, itype, date, severity, desc, lost)
                
            elif dtype == 'training':
                name = request.form.get('training_name')
                hours = float(request.form.get('hours', 0))
                parts = int(request.form.get('participants', 0))
                date = request.form.get('date')
                cat = request.form.get('category')
                manager.add_training(company_id, name, hours, parts, date, cat)

            elif dtype == 'satisfaction':
                year = int(request.form.get('year'))
                date = request.form.get('survey_date')
                score = float(request.form.get('satisfaction_score', 0))
                turnover = float(request.form.get('turnover_rate', 0))
                participation = float(request.form.get('participation_rate', 0))
                comments = request.form.get('comments')
                manager.add_employee_satisfaction(company_id, year, date, score, turnover, participation, comments)

            elif dtype == 'investment':
                name = request.form.get('project_name')
                amount = float(request.form.get('investment_amount', 0))
                beneficiaries = int(request.form.get('beneficiaries_count', 0))
                desc = request.form.get('impact_description')
                date = request.form.get('date')
                manager.add_community_investment(company_id, name, amount, beneficiaries, desc, date)
            
            flash('Veri başarıyla eklendi.', 'success')
            return redirect(url_for('social_module'))
            
        except Exception as e:
            logging.error(f"Error adding social data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('social_edit.html', title='Sosyal Veri Girişi', data_type=data_type)


@app.route('/governance')
@require_company_context
def governance_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('governance')
    company_id = g.company_id
    
    stats = {'board_members': 0, 'committees': 0, 'ethics_training': 0}
    recent_data = []
    
    if manager:
        try:
            stats = manager.get_stats(company_id)
            if hasattr(manager, 'get_recent_records'):
                recent_data = manager.get_recent_records(company_id)
        except Exception as e:
            logging.error(f"Error in governance manager stats: {e}")

    return render_template('governance.html', title='Kurumsal Yönetişim', manager_available=bool(manager), stats=stats, recent_data=recent_data)

@app.route('/governance/add', methods=['GET', 'POST'])
@require_company_context
def governance_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_type = request.args.get('type', 'board_member')
    if data_type == 'board': data_type = 'board_member'
    
    if request.method == 'POST':
        manager = MANAGERS.get('governance')
        if not manager:
            flash('Kurumsal Yönetişim modülü aktif değil.', 'danger')
            return redirect(url_for('governance_module'))

        try:
            dtype = request.form.get('data_type')
            company_id = g.company_id
            success = False
            
            if dtype == 'board_member':
                name = request.form.get('member_name')
                pos = request.form.get('position')
                mtype = request.form.get('member_type')
                indep = request.form.get('independence_status')
                gender = request.form.get('gender')
                expert = request.form.get('expertise_area')
                
                success = manager.add_board_member(
                    company_id=company_id,
                    member_name=name,
                    position=pos,
                    member_type=mtype,
                    independence_status=indep,
                    gender=gender,
                    expertise_area=expert
                )
                
            elif dtype == 'committee':
                name = request.form.get('committee_name')
                ctype = request.form.get('committee_type')
                try:
                    count = int(request.form.get('member_count', 0))
                except ValueError:
                    count = 0
                resp = request.form.get('responsibilities')
                
                success = manager.add_governance_committee(
                    company_id=company_id,
                    committee_name=name,
                    committee_type=ctype,
                    member_count=count,
                    responsibilities=resp
                )
                
            elif dtype == 'ethics':
                training_name = request.form.get('training_name')
                try:
                    participants = int(request.form.get('participants', 0))
                    hours = float(request.form.get('total_hours', 0))
                except ValueError:
                    participants = 0
                    hours = 0.0
                desc = request.form.get('description')
                
                success = manager.add_ethics_training(
                    company_id=company_id,
                    training_name=training_name,
                    participants=participants,
                    total_hours=hours,
                    description=desc
                )
            
            if success:
                flash('Veri başarıyla eklendi.', 'success')
                return redirect(url_for('governance_module'))
            else:
                flash('Veri eklenirken bir hata oluştu.', 'danger')
            
        except Exception as e:
            logging.error(f"Error adding governance data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('governance_edit.html', title='Yönetişim Veri Girişi', data_type=data_type)

@app.route('/carbon')
@require_company_context
def carbon_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('carbon')
    
    if not manager:
        return render_template('carbon.html', title='Karbon Ayak İzi', manager_available=False, stats={'total_co2e': 0, 'scope1': 0, 'scope2': 0, 'scope3': 0}, recent_data=[])
        
    stats = manager.get_dashboard_stats(company_id)
    recent_data = manager.get_recent_records(company_id)

    return render_template('carbon.html', title='Karbon Ayak İzi', manager_available=True, stats=stats, recent_data=recent_data)

@app.route('/energy')
@require_company_context
def energy_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('energy')
    
    if not manager:
        return render_template('energy.html', title='Enerji Yönetimi', manager_available=False, stats={'total_consumption': 0, 'renewable_ratio': 0, 'total_cost': 0}, recent_data=[])
        
    stats = manager.get_dashboard_stats(company_id)
    recent_data = manager.get_recent_records(company_id)

    return render_template('energy.html', title='Enerji Yönetimi', manager_available=True, stats=stats, recent_data=recent_data)

@app.route('/esg')
@require_company_context
def esg_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('esg')
    company_id = g.company_id
    
    if not manager:
        return render_template('esg.html', title='ESG Skorlama', manager_available=False, stats={'environmental': 0, 'social': 0, 'governance': 0}, history=[])

    # Live stats from data
    stats = manager.get_dashboard_stats(company_id)
    # History from saved snapshots
    history = manager.get_history(company_id)
    
    return render_template('esg.html', title='ESG Skorlama', manager_available=True, stats=stats, history=history)

@app.route('/esg/add', methods=['GET', 'POST'])
@require_company_context
def esg_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        manager = MANAGERS.get('esg')
        if not manager:
             flash('ESG Modülü aktif değil.', 'danger')
             return redirect(url_for('esg_module'))
             
        try:
            company_id = g.company_id
            year = request.form.get('year')
            quarter = request.form.get('quarter')
            env = float(request.form.get('environmental_score'))
            soc = float(request.form.get('social_score'))
            gov = float(request.form.get('governance_score'))
            
            # Use configured weights
            weights = manager.config.get('weights', {'E': 0.4, 'S': 0.3, 'G': 0.3})
            total = (env * weights.get('E', 0.4)) + (soc * weights.get('S', 0.3)) + (gov * weights.get('G', 0.3))
            
            if manager.save_score(company_id, year, quarter, env, soc, gov, total):
                flash('ESG skorları başarıyla eklendi.', 'success')
            else:
                flash('Kaydedilirken hata oluştu.', 'danger')
                
            return redirect(url_for('esg_module'))
        except Exception as e:
            logging.error(f"Error adding ESG scores: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('esg_edit.html', title='ESG Veri Girişi')

@app.route('/esg/settings', methods=['GET'])
@require_company_context
def esg_settings():
    if 'user' not in session: return redirect(url_for('login'))
    manager = MANAGERS.get('esg')
    if not manager:
        flash('ESG Modülü aktif değil.', 'danger')
        return redirect(url_for('esg_module'))
    
    weights = manager.config.get('weights', {'E': 0.4, 'S': 0.3, 'G': 0.3})
    return render_template('esg_settings.html', weights=weights)

@app.route('/esg/settings/update', methods=['POST'])
@require_company_context
def esg_settings_update():
    if 'user' not in session: return redirect(url_for('login'))
    manager = MANAGERS.get('esg')
    if not manager:
        flash('ESG Modülü aktif değil.', 'danger')
        return redirect(url_for('esg_module'))

    try:
        e_weight = float(request.form.get('E', 0))
        s_weight = float(request.form.get('S', 0))
        g_weight = float(request.form.get('G', 0))
        
        new_weights = {'E': e_weight, 'S': s_weight, 'G': g_weight}
        
        if manager.update_weights(new_weights):
            flash('ESG ağırlık ayarları güncellendi.', 'success')
        else:
            flash('Ağırlıklar güncellenemedi (Toplam 1.0 olmalı).', 'warning')
            
    except Exception as e:
        logging.error(f"ESG settings update error: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('esg_settings'))

@app.route('/cbam')
@require_company_context
def cbam_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('cbam')
    
    if not manager:
        return render_template('cbam.html', title='CBAM Uyumluluk', manager_available=False, stats={'total_emissions': 0, 'total_imports': 0, 'liability': 0, 'imports': []})
    
    period = request.args.get('period')
    report = None
    ets_factors = []
    recent_data = []
    try:
        stats = manager.get_dashboard_stats(company_id)
        if hasattr(manager, 'get_recent_records'):
            recent_data = manager.get_recent_records(company_id)
        if period:
            report = manager.calculate_cbam_liability(company_id, period)
        if hasattr(manager, 'get_ets_factors'):
            ets_factors = manager.get_ets_factors()
    except Exception as e:
        logging.error(f"CBAM module error: {e}")
        stats = {'total_emissions': 0, 'total_imports': 0, 'liability': 0, 'imports': []}
    
    return render_template('cbam.html', title='CBAM Uyumluluk', manager_available=True, stats=stats, report=report, period=period, ets_factors=ets_factors, recent_data=recent_data)

@app.route('/cbam/add', methods=['GET', 'POST'])
@require_company_context
def cbam_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('cbam')
    if not manager:
        flash('CBAM modülü aktif değil.', 'danger')
        return redirect(url_for('cbam_module'))
    
    if request.method == 'POST':
        try:
            company_id = g.company_id
            sector = request.form.get('sector')
            product_code = request.form.get('product_code')
            origin_country = request.form.get('origin_country')
            quantity = float(request.form.get('quantity'))
            direct_emissions = float(request.form.get('direct_emissions'))
            indirect_emissions = float(request.form.get('indirect_emissions'))
            carbon_price_paid = float(request.form.get('carbon_price_paid') or 0)
            offset_type = request.form.get('offset_type')
            offset_quantity = float(request.form.get('offset_quantity') or 0)
            
            total_emissions = direct_emissions + indirect_emissions
            
            # Find or create product
            product = manager.get_product_by_code(company_id, product_code)
            if not product:
                # Use product_code as name if not provided
                manager.add_product(company_id, product_code=product_code, product_name=product_code, sector=sector)
                product = manager.get_product_by_code(company_id, product_code)
            
            if product:
                if manager.add_import(company_id, product['id'], origin_country, quantity, total_emissions, carbon_price_paid, offset_type=offset_type, offset_quantity=offset_quantity):
                    flash('CBAM verisi başarıyla eklendi.', 'success')
                else:
                    flash('Veri eklenirken hata oluştu.', 'danger')
            else:
                flash('Ürün oluşturulamadı.', 'danger')
                
            return redirect(url_for('cbam_module'))
        except Exception as e:
            logging.error(f"Error adding CBAM data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('cbam_edit.html', title='CBAM Veri Girişi')

@app.route('/cbam/factor', methods=['POST'])
@require_company_context
def cbam_factor():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('cbam')
    if not manager:
        flash('CBAM modülü aktif değil.', 'danger')
        return redirect(url_for('cbam_module'))
    
    try:
        period = int(request.form.get('factor_period'))
        price = float(request.form.get('factor_price'))
        if manager.save_ets_factor(period, price):
            flash('EU ETS fiyatı güncellendi.', 'success')
        else:
            flash('EU ETS fiyatı kaydedilemedi.', 'danger')
    except Exception as e:
        logging.error(f"Error saving ETS factor: {e}")
        flash(f'Hata: {e}', 'danger')
    
    return redirect(url_for('cbam_module'))


@app.route('/cbam/quarterly-report')
@require_company_context
def cbam_quarterly_report():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    manager = MANAGERS.get('cbam')
    if not manager:
        flash('CBAM modülü aktif değil.', 'danger')
        return redirect(url_for('cbam_module'))
    
    company_id = g.company_id
    period = request.args.get('period')
    if not period:
        now = datetime.now()
        quarter = (now.month - 1) // 3 + 1
        period = f"{now.year}-Q{quarter}"
    
    try:
        ok = manager.generate_quarterly_report(company_id, period)
        if ok:
            flash(f'Çeyrek rapor başarıyla oluşturuldu: {period}', 'success')
        else:
            flash('Rapor oluşturulurken hata oluştu.', 'danger')
    except Exception as e:
        logging.error(f"Error generating CBAM quarterly report: {e}")
        flash('Rapor oluşturulurken teknik bir hata oluştu.', 'danger')
    
    return redirect(url_for('cbam_module', period=period))

@app.route('/csrd')
@require_company_context
def csrd_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('csrd')
    
    if not manager:
        return render_template('csrd.html', title='CSRD Raporlama', manager_available=False, materiality=[])
        
    materiality_data = manager.get_recent_records(company_id, limit=50)
    return render_template('csrd.html', title='CSRD Raporlama', manager_available=True, materiality=materiality_data)

@app.route('/csrd/materiality', methods=['GET', 'POST'])
@require_company_context
def csrd_materiality():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('csrd')
    if not manager:
        flash('CSRD modülü aktif değil.', 'danger')
        return redirect(url_for('csrd_module'))
    
    if request.method == 'POST':
        try:
            company_id = g.company_id
            raw_topic = request.form.get('topic') # "E1-Climate Change"
            
            if '-' in raw_topic:
                code, name = raw_topic.split('-', 1)
            else:
                code, name = 'GEN', raw_topic

            impact = int(request.form.get('impact_score'))
            financial = int(request.form.get('financial_score'))
            rationale = request.form.get('rationale')
            
            if manager.add_materiality_assessment(company_id, code, name, impact, financial, rationale):
                flash('Önemlilik analizi kaydedildi.', 'success')
            else:
                flash('Kaydedilirken hata oluştu.', 'danger')
                
            return redirect(url_for('csrd_module'))
        except Exception as e:
            logging.error(f"Error adding CSRD data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('csrd_materiality.html', title='Çift Önemlilik Analizi')

@app.route('/taxonomy')
@require_company_context
def taxonomy_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    taxonomy_manager = MANAGERS.get('taxonomy')
    
    if not taxonomy_manager:
        return render_template('taxonomy.html', title='AB Taksonomisi', manager_available=False, stats={'turnover': 0, 'turnover_aligned': 0, 'turnover_pct': 0, 'capex': 0, 'capex_aligned': 0, 'capex_pct': 0, 'opex': 0, 'opex_aligned': 0, 'opex_pct': 0}, recent_data=[], framework_mappings=[])
        
    stats = taxonomy_manager.get_taxonomy_stats(company_id)
    recent_data = taxonomy_manager.get_taxonomy_activities(company_id)
    framework_mappings = []
    try:
        framework_mappings = taxonomy_manager.get_framework_mappings()
    except Exception as e:
        logging.error(f"Taxonomy framework mappings error: {e}")
    detail_item = None
    try:
        activity_id = request.args.get('activity_id', type=int)
        if activity_id:
            for row in recent_data:
                if row.get('id') == activity_id:
                    detail_item = row
                    break
    except Exception as e:
        logging.error(f"Taxonomy detail parse error: {e}")
    
    return render_template('taxonomy.html', title='AB Taksonomisi', manager_available=True, stats=stats, recent_data=recent_data, detail_item=detail_item, framework_mappings=framework_mappings)

@app.route('/taxonomy/add', methods=['GET', 'POST'])
@require_company_context
def taxonomy_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('taxonomy')
    if not manager:
        flash('Taksonomi modülü aktif değil.', 'danger')
        return redirect(url_for('taxonomy_module'))
    
    if request.method == 'POST':
        try:
            company_id = g.company_id
            year = int(request.form.get('year') or 2024)
            name = request.form.get('activity_name')
            nace = request.form.get('nace_code')
            turnover = float(request.form.get('turnover_amount') or 0)
            capex = float(request.form.get('capex_amount') or 0)
            opex = float(request.form.get('opex_amount') or 0)
            aligned = float(request.form.get('aligned_pct') or 0)
            substantial = bool(request.form.get('substantial_contribution'))
            dnsh = bool(request.form.get('dnsh_compliance'))
            minimum = bool(request.form.get('minimum_safeguards'))
            documentation = request.form.get('documentation') or ""
            env_objective = request.form.get('env_objective') or "CCM"
            secondary_objectives = request.form.getlist('secondary_objectives')
            
            if manager.add_company_activity(
                company_id,
                {
                    'activity_name': name,
                    'nace_code': nace,
                    'turnover': turnover,
                    'capex': capex,
                    'opex': opex,
                    'aligned': aligned,
                    'documentation': documentation,
                    'year': year,
                    'substantial': substantial,
                    'dnsh': dnsh,
                    'minimum': minimum,
                    'env_objective': env_objective
                }
            ):
                flash('Taksonomi faaliyeti başarıyla eklendi.', 'success')
            else:
                flash('Kaydedilirken hata oluştu.', 'danger')
                
            return redirect(url_for('taxonomy_module'))
        except Exception as e:
            with open('taxonomy_error.log', 'w') as f:
                import traceback
                traceback.print_exc(file=f)
            logging.error(f"Error adding taxonomy data: {e}")
            flash(f'Hata oluştu: {str(e)}', 'danger')
            return redirect(url_for('taxonomy_module'))
            
    return render_template('taxonomy_edit.html', title='Taksonomi Veri Girişi')

@app.route('/taxonomy/mapping/add', methods=['POST'])
@require_company_context
def taxonomy_mapping_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    taxonomy_manager = MANAGERS.get('taxonomy')
    if not taxonomy_manager:
        flash('Taxonomy framework mapping modülü aktif değil.', 'danger')
        return redirect(url_for('taxonomy_module'))
    
    try:
        activity_code = request.form.get('activity_code')
        objective_code = request.form.get('objective_code')
        sdg_target = request.form.get('sdg_target') or None
        gri_disclosure = request.form.get('gri_disclosure') or None
        tsrs_metric = request.form.get('tsrs_metric') or None
        rationale = request.form.get('mapping_rationale') or None
        
        if not activity_code or not objective_code:
            flash('Faaliyet kodu ve hedef kodu zorunludur.', 'danger')
            return redirect(url_for('taxonomy_module'))
        
        if not (sdg_target or gri_disclosure or tsrs_metric):
            flash('En az bir SDG, GRI veya TSRS alanı doldurulmalıdır.', 'danger')
            return redirect(url_for('taxonomy_module'))
        
        if taxonomy_manager.map_to_frameworks(
            activity_code=activity_code,
            objective_code=objective_code,
            sdg_target=sdg_target,
            gri_disclosure=gri_disclosure,
            tsrs_metric=tsrs_metric,
            rationale=rationale,
        ):
            flash('Çerçeve eşleştirmesi eklendi.', 'success')
        else:
            flash('Eşleştirme kaydedilirken hata oluştu.', 'danger')
    except Exception as e:
        logging.error(f"Error adding taxonomy framework mapping: {e}")
        flash(f'Hata: {e}', 'danger')
    
    return redirect(url_for('taxonomy_module'))

@app.route('/energy/add', methods=['POST'])
@require_company_context
def energy_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('energy')
    if not manager:
        flash('Enerji modülü aktif değil.', 'danger')
        return redirect(url_for('energy_module'))
        
    try:
        company_id = g.company_id
        
        energy_type = request.form.get('energy_type')
        source = request.form.get('source')
        amount = float(request.form.get('amount', 0))
        unit = request.form.get('unit')
        cost = float(request.form.get('cost', 0) or 0)
        date_str = request.form.get('date')
        
        # Parse date
        year = datetime.now().year
        month = datetime.now().month
        if date_str:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                year = dt.year
                month = dt.month
            except:
                pass
                
        manager.add_energy_consumption(
            company_id=company_id, 
            year=year, 
            energy_type=energy_type, 
            consumption_amount=amount, 
            unit=unit, 
            cost=cost,
            source=source,
            month=month, 
            invoice_date=date_str
        )
        
        flash('Enerji tüketim kaydı başarıyla eklendi.', 'success')
    except Exception as e:
        logging.error(f"Error adding energy consumption: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('energy_module'))

@app.route('/waste')
@require_company_context
def waste_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('waste')
    
    if not manager:
        return render_template('waste.html', title='Atık Yönetimi', manager_available=False, stats={'total_waste': 0, 'recycled_waste': 0}, recent_data=[])
        
    stats = manager.get_dashboard_stats(company_id)
    recent_data = manager.get_recent_records(company_id)

    return render_template('waste.html', title='Atık Yönetimi', manager_available=True, stats=stats, recent_data=recent_data)

@app.route('/waste/add', methods=['POST'])
@require_company_context
def waste_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('waste')
    if not manager:
        flash('Atık modülü aktif değil.', 'danger')
        return redirect(url_for('waste_module'))
        
    try:
        company_id = g.company_id
        
        waste_type = request.form.get('waste_type')
        category = request.form.get('category')
        amount = float(request.form.get('amount', 0))
        unit = request.form.get('unit')
        disposal_method = request.form.get('disposal_method')
        date_str = request.form.get('date')
        
        # Parse date
        year = datetime.now().year
        month = datetime.now().month
        if date_str:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                year = dt.year
                month = dt.month
            except:
                pass
                
        manager.add_waste_generation(
            company_id=company_id, 
            year=year, 
            month=month, 
            waste_type=waste_type, 
            waste_category=category, 
            waste_amount=amount, 
            unit=unit, 
            disposal_method=disposal_method, 
            invoice_date=date_str
        )
        
        flash('Atık kaydı başarıyla eklendi.', 'success')
    except Exception as e:
        logging.error(f"Error adding waste: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('waste_module'))

@app.route('/carbon/add', methods=['POST'])
@require_company_context
def carbon_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('carbon')
    if not manager:
        flash('Karbon modülü aktif değil.', 'danger')
        return redirect(url_for('carbon_module'))
        
    try:
        company_id = g.company_id
        
        scope = request.form.get('scope')
        source_type = request.form.get('source_type')
        amount = float(request.form.get('amount', 0))
        unit = request.form.get('unit')
        date_str = request.form.get('date')
        
        # Parse date
        year = datetime.now().year
        if date_str:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                year = dt.year
            except:
                pass
        
        if scope == 'Scope 1':
            manager.add_scope1_emission(
                company_id=company_id, 
                year=year, 
                emission_source=source_type, 
                fuel_type=source_type, 
                fuel_consumption=amount, 
                fuel_unit=unit, 
                invoice_date=date_str
            )
        elif scope == 'Scope 2':
             manager.add_scope2_emission(
                company_id=company_id, 
                year=year, 
                energy_source=source_type, 
                energy_consumption=amount, 
                energy_unit=unit, 
                invoice_date=date_str
            )
        elif scope == 'Scope 3':
             manager.add_scope3_emission(
                company_id=company_id, 
                year=year, 
                category=source_type, 
                subcategory=None,
                activity_data=amount, 
                activity_unit=unit, 
                invoice_date=date_str
            )
        
        flash('Karbon emisyon kaydı başarıyla eklendi.', 'success')
    except Exception as e:
        logging.error(f"Error adding carbon emission: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('carbon_module'))

@app.route('/water')
@require_company_context
def water_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('water')
    
    if not manager:
        return render_template('water.html', title='Su Yönetimi', manager_available=False, stats={'total_consumption': 0}, recent_data=[])
        
    stats = manager.get_dashboard_stats(company_id)
    recent_data = manager.get_recent_records(company_id)

    return render_template('water.html', title='Su Yönetimi', manager_available=True, stats=stats, recent_data=recent_data)

@app.route('/water/add', methods=['POST'])
@require_company_context
def water_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('water')
    if not manager:
        flash('Su modülü aktif değil.', 'danger')
        return redirect(url_for('water_module'))
        
    try:
        company_id = g.company_id
        
        consumption_type = request.form.get('consumption_type')
        source = request.form.get('source')
        amount = float(request.form.get('amount', 0))
        unit = request.form.get('unit')
        cost = float(request.form.get('cost', 0) or 0)
        date_str = request.form.get('date')
        
        # Parse date
        year = datetime.now().year
        month = datetime.now().month
        if date_str:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                year = dt.year
                month = dt.month
            except:
                pass
                
        manager.add_water_consumption(
            company_id=company_id, 
            year=year, 
            consumption_type=consumption_type, 
            consumption_amount=amount, 
            unit=unit, 
            cost=cost,
            source=source,
            month=month, 
            invoice_date=date_str
        )
        
        flash('Su tüketim kaydı başarıyla eklendi.', 'success')
    except Exception as e:
        logging.error(f"Error adding water consumption: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('water_module'))

@app.route('/biodiversity')
@require_company_context
def biodiversity_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('biodiversity')
    
    if not manager:
        return render_template('biodiversity.html', title='Biyoçeşitlilik', manager_available=False, stats={'total_areas': 0, 'protected_species': 0}, recent_data=[])
        
    stats = manager.get_dashboard_stats(company_id)
    recent_data = manager.get_recent_records(company_id)

    return render_template('biodiversity.html', title='Biyoçeşitlilik', manager_available=True, stats=stats, recent_data=recent_data)

@app.route('/biodiversity/add', methods=['POST'])
@require_company_context
def biodiversity_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('biodiversity')
    if not manager:
        flash('Biyoçeşitlilik modülü aktif değil.', 'danger')
        return redirect(url_for('biodiversity_module'))
        
    try:
        company_id = g.company_id
        cat = request.form.get('bio_category', '')
        desc = request.form.get('bio_description')
        area = float(request.form.get('bio_area') or 0)
        status = request.form.get('bio_status')
        date_str = request.form.get('date')
        
        success = False
        
        # Determine specific method based on category
        if 'habitat' in cat.lower():
            # Habitat Areas
            success = manager.add_habitat_area(
                company_id=company_id, 
                habitat_name=f"Habitat {date_str}", 
                habitat_type=cat, 
                area_size=area, 
                area_unit='m2', 
                protection_status=status, 
                management_plan=desc
            )
        elif 'impact' in cat.lower() or 'ekosistem' in cat.lower() or 'hizmet' in cat.lower():
            # Ecosystem Services
            # Note: ecosystem_services table expects: year, service_type, service_value, value_unit...
            # We map form fields to best fit:
            # area -> service_value (assuming value is monetary or quantitative)
            # desc -> measurement_method or beneficiary
            year = int(date_str[:4]) if date_str else datetime.now().year
            success = manager.add_ecosystem_service(
                company_id=company_id,
                year=year,
                service_type=cat, # e.g. "Ecosystem Services"
                service_value=area, # Using area input as value
                value_unit='TL' if 'tl' in str(status).lower() else 'Unit',
                measurement_method=desc,
                location='General'
            )
        else:
            # Default to Species (for 'species' category or others)
            success = manager.add_biodiversity_species(
                company_id=company_id, 
                species_name=f"Species {date_str}", 
                species_type=cat, 
                conservation_status=status, 
                protection_measures=desc
            )
            
        if success:
            flash('Biyoçeşitlilik verisi başarıyla eklendi.', 'success')
        else:
            flash('Veri eklenirken bir hata oluştu.', 'danger')
            
    except Exception as e:
        logging.error(f"Error adding biodiversity data: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('biodiversity_module'))


@app.route('/economic')
@require_company_context
def economic_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('economic')
    
    if not manager:
        return render_template('economic.html', title='Ekonomik Performans', manager_available=False, stats={}, recent_data=[])
        
    stats = manager.get_stats(company_id)
    recent_data = manager.get_recent_data(company_id)
    investment_projects = manager.get_investment_projects(company_id) if hasattr(manager, 'get_investment_projects') else []
    
    return render_template('economic.html', title='Ekonomik Performans', manager_available=True, stats=stats, recent_data=recent_data, investment_projects=investment_projects)

@app.route('/economic/add', methods=['GET', 'POST'])
@require_company_context
def economic_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_type = request.args.get('type', 'value_distribution')
    # Alias mapping
    if data_type == 'revenue': data_type = 'value_distribution'
    if data_type == 'risk': data_type = 'financial_performance'
    if data_type == 'investment': data_type = 'investment_project'
    
    manager = MANAGERS.get('economic')
    if not manager:
        flash('Modül aktif değil.', 'danger')
        return redirect(url_for('economic_module'))
    
    if request.method == 'POST':
        try:
            dtype = request.form.get('data_type')
            company_id = g.company_id
            success = False
            
            if dtype == 'value_distribution':
                success = manager.add_economic_value_distribution(
                    company_id=company_id,
                    year=int(request.form.get('year')),
                    revenue=float(request.form.get('revenue')),
                    operating_costs=float(request.form.get('operating_costs') or 0),
                    employee_wages=float(request.form.get('employee_wages') or 0),
                    payments_to_capital_providers=float(request.form.get('payments_capital') or 0),
                    payments_to_governments=float(request.form.get('payments_gov') or 0),
                    community_investments=float(request.form.get('community_investments') or 0)
                )
            elif dtype == 'financial_performance':
                assets = float(request.form.get('total_assets') or 0)
                liabilities = float(request.form.get('total_liabilities') or 0)
                equity = assets - liabilities
                
                success = manager.add_financial_performance(
                    company_id=company_id,
                    year=int(request.form.get('year', 2024)),
                    total_assets=assets,
                    total_liabilities=liabilities,
                    net_profit=float(request.form.get('net_profit') or 0),
                    ebitda=float(request.form.get('ebitda') or 0),
                    equity=equity
                )
            elif dtype == 'tax':
                success = manager.add_tax_contributions(
                    company_id=company_id,
                    year=int(request.form.get('year', 2024)),
                    corporate_tax=float(request.form.get('corporate_tax') or 0),
                    payroll_tax=float(request.form.get('payroll_tax') or 0),
                    vat_collected=float(request.form.get('vat_collected') or 0),
                    property_tax=float(request.form.get('property_tax') or 0),
                    other_taxes=float(request.form.get('other_taxes') or 0)
                )
            elif dtype == 'investment_project':
                success = manager.add_investment_project(
                    company_id=company_id,
                    project_name=request.form.get('project_name'),
                    initial_investment=float(request.form.get('initial_investment') or 0),
                    start_date=request.form.get('start_date'),
                    description=request.form.get('description'),
                    discount_rate=float(request.form.get('discount_rate') or 0.10),
                    duration_years=int(request.form.get('duration_years') or 5)
                )
                if success:
                    # Auto calculate metrics for initial state (even if no flows yet)
                    manager.calculate_project_metrics(success) # success returns rowid which is truthy
                    success = True # Convert back to bool for check below
            
            elif dtype == 'cash_flow':
                project_id = int(request.form.get('project_id'))
                year = int(request.form.get('year'))
                cash_flow = float(request.form.get('cash_flow') or 0)
                
                success = manager.add_project_cash_flow(
                    project_id=project_id,
                    year=year,
                    cash_flow=cash_flow
                )
                if success:
                    # Recalculate metrics
                    manager.calculate_project_metrics(project_id)
                
            if success:
                flash('Ekonomik veri başarıyla eklendi.', 'success')
                return redirect(url_for('economic_module'))
            else:
                flash('Veri eklenirken bir hata oluştu.', 'danger')
            
        except Exception as e:
            logging.error(f"Error adding economic data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('economic_edit.html', title='Ekonomik Veri Girişi', data_type=data_type)


@app.route('/benchmark')
@require_company_context
def benchmark_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('benchmark')
    
    if not manager:
        return render_template('benchmark.html', title='Benchmarking', manager_available=False, sectors=[], metrics=[], averages={})
        
    # Get all sectors for dropdown
    sectors = manager.SECTORS
    
    # Get metrics
    metrics = manager.STANDARD_METRICS
    
    # Get selected sector from query param or default to company's sector if available
    # For now, default to 'imalat' if not provided
    selected_sector = request.args.get('sector', 'imalat')
    
    # Get comprehensive sector data for the selected sector
    # Since existing class doesn't have a simple "get all metrics for sector" method that returns a nice dict,
    # we might need to query the database directly or use _get_comprehensive_sector_data logic if exposed.
    # Looking at the class, get_sector_benchmark returns one row.
    
    # Let's fetch all metrics for the selected sector
    averages = {}
    for metric_code in metrics.keys():
        data = manager.get_sector_benchmark(selected_sector, metric_code)
        if data:
            averages[metric_code] = data
            
    return render_template('benchmark.html', title='Benchmarking', manager_available=True, sectors=sectors, metrics=metrics, averages=averages, selected_sector=selected_sector)

@app.route('/regulation')
@require_company_context
def regulation_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('regulation')
    
    if not manager:
        return render_template('regulation.html', title='Regülasyon Takip', manager_available=False, regulations=[], upcoming=[])
        
    regulations = manager.get_company_compliance(company_id)
    upcoming = manager.get_upcoming_deadlines()
    
    return render_template('regulation.html', title='Regülasyon Takip', manager_available=True, regulations=regulations, upcoming=upcoming)


@app.route('/issb')
@require_company_context
def issb_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('issb')
    
    if not manager:
        return render_template('issb.html', title='ISSB Standartları', manager_available=False, stats={'total_disclosures': 0, 'standards_covered': 0, 'completion_rate': 0}, standards=[])
        
    stats = manager.get_dashboard_stats(company_id)
    standards = manager.get_recent_records(company_id, limit=100)

    return render_template('issb.html', title='ISSB Standartları', manager_available=True, stats=stats, standards=standards)

@app.route('/issb/add', methods=['GET', 'POST'])
@require_company_context
def issb_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        manager = MANAGERS.get('issb')
        if not manager:
            flash('ISSB Modülü aktif değil.', 'danger')
            return redirect(url_for('issb_module'))
            
        try:
            year = request.form.get('year')
            standard = request.form.get('standard')
            disclosure = request.form.get('disclosure')
            metric = request.form.get('metric')
            company_id = g.company_id
            
            if manager.add_disclosure(company_id, year, standard, disclosure, metric):
                flash('ISSB verisi başarıyla eklendi.', 'success')
            else:
                flash('Veri eklenirken bir hata oluştu.', 'danger')
                
            return redirect(url_for('issb_module'))
        except Exception as e:
            logging.error(f"ISSB add error: {e}")
            flash('Bir hata oluştu.', 'danger')
            
    return render_template('issb_edit.html', title='ISSB Veri Girişi')

@app.route('/iirc')
@require_company_context
def iirc_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('iirc')
    
    if not manager:
        return render_template('iirc.html', title='Entegre Raporlama (IIRC)', manager_available=False, stats={'total_reports': 0, 'latest_year': '-'}, reports=[])
        
    stats = manager.get_dashboard_stats(company_id)
    reports = manager.get_recent_reports(company_id)
        
    return render_template('iirc.html', title='Entegre Raporlama (IIRC)', manager_available=True, stats=stats, reports=reports)

@app.route('/iirc/add', methods=['GET', 'POST'])
@require_company_context
def iirc_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        manager = MANAGERS.get('iirc')
        if not manager:
            flash('IIRC Modülü aktif değil.', 'danger')
            return redirect(url_for('iirc_module'))

        try:
            company_id = g.company_id
            year = request.form.get('year')
            name = request.form.get('report_name')
            description = request.form.get('report_description', '')
            
            # Additional capitals can be added here if form supports it
            capitals = {} 
            
            if manager.add_report(company_id, year, name, description, capitals):
                flash('Rapor başarıyla eklendi.', 'success')
            else:
                flash('Rapor eklenirken hata oluştu.', 'danger')
                
            return redirect(url_for('iirc_module'))
        except Exception as e:
            logging.error(f"Error adding IIRC report: {e}")
            flash('Bir hata oluştu.', 'danger')
            
    return render_template('iirc_edit.html', title='Entegre Rapor Ekle')

@app.route('/esrs')
@require_company_context
def esrs_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {'covered_standards': 0, 'completion_rate': 0}
    materiality_items = []
    
    standards = [
        {'code': 'ESRS 1', 'title': 'Genel Gereklilikler (General Requirements)', 'category': 'Cross-cutting'},
        {'code': 'ESRS 2', 'title': 'Genel Açıklamalar (General Disclosures)', 'category': 'Cross-cutting'},
        {'code': 'E1', 'title': 'İklim Değişikliği (Climate Change)', 'category': 'Environmental'},
        {'code': 'E2', 'title': 'Kirlilik (Pollution)', 'category': 'Environmental'},
        {'code': 'E3', 'title': 'Su ve Deniz Kaynakları (Water and Marine Resources)', 'category': 'Environmental'},
        {'code': 'E4', 'title': 'Biyoçeşitlilik ve Ekosistemler (Biodiversity and Ecosystems)', 'category': 'Environmental'},
        {'code': 'E5', 'title': 'Kaynak Kullanımı ve Döngüsel Ekonomi (Resource Use and Circular Economy)', 'category': 'Environmental'},
        {'code': 'S1', 'title': 'Kendi İşgücü (Own Workforce)', 'category': 'Social'},
        {'code': 'S2', 'title': 'Değer Zincirindeki Çalışanlar (Workers in the Value Chain)', 'category': 'Social'},
        {'code': 'S3', 'title': 'Etkilenen Topluluklar (Affected Communities)', 'category': 'Social'},
        {'code': 'S4', 'title': 'Tüketiciler ve Son Kullanıcılar (Consumers and End-users)', 'category': 'Social'},
        {'code': 'G1', 'title': 'İş Ahlakı (Business Conduct)', 'category': 'Governance'}
    ]
    
    manager = MANAGERS.get('esrs')
    if manager:
        stats = manager.get_dashboard_stats(company_id)
        # Fetch materiality analysis
        materiality_items = manager.get_materiality_analysis(company_id)
        
        # Fetch detailed assessment for each standard
        for s in standards:
            details = manager.get_assessment_details(company_id, s['code'])
            s['status'] = details.get('status', 'not_started')
            s['notes'] = details.get('notes', '')
            s['governance_notes'] = details.get('governance_notes', '')
            s['strategy_notes'] = details.get('strategy_notes', '')
            s['impact_risk_notes'] = details.get('impact_risk_notes', '')
            s['metrics_notes'] = details.get('metrics_notes', '')
    else:
        stats = {'covered_standards': 0, 'completion_rate': 0}
        
    return render_template('esrs.html', title='ESRS Standartları', manager_available=bool(manager), standards=standards, stats=stats, materiality_items=materiality_items)

@app.route('/esrs/update/<code_id>', methods=['POST'])
@require_company_context
def esrs_update(code_id):
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('esrs')
    if manager:
        try:
            company_id = g.company_id
            status = request.form.get('status')
            notes = request.form.get('notes')
            governance_notes = request.form.get('governance_notes')
            strategy_notes = request.form.get('strategy_notes')
            impact_risk_notes = request.form.get('impact_risk_notes')
            metrics_notes = request.form.get('metrics_notes')
            
            manager.update_assessment(
                company_id=company_id, 
                standard_code=code_id, 
                status=status, 
                notes=notes,
                governance_notes=governance_notes,
                strategy_notes=strategy_notes,
                impact_risk_notes=impact_risk_notes,
                metrics_notes=metrics_notes
            )
            flash(f'{code_id} durumu güncellendi.', 'success')
        except Exception as e:
            logging.error(f"ESRS update error: {e}")
            flash('Güncelleme hatası.', 'danger')
            
    return redirect(url_for('esrs_module'))

@app.route('/esrs/materiality/add', methods=['POST'])
@require_company_context
def esrs_materiality_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('esrs')
    if not manager:
        flash('ESRS modülü yüklenemedi.', 'danger')
        return redirect(url_for('esrs_module'))
        
    company_id = g.company_id
    
    topic = request.form.get('topic')
    impact_score = request.form.get('impact_score')
    likelihood = request.form.get('likelihood')
    financial_effect = request.form.get('financial_effect')
    environmental_effect = request.form.get('environmental_effect')
    
    try:
        impact_score = int(impact_score) if impact_score else 0
        likelihood = int(likelihood) if likelihood else 0
    except ValueError:
        impact_score = 0
        likelihood = 0
        
    # Validation
    if not topic:
        flash('Konu başlığı zorunludur.', 'warning')
        return redirect(url_for('esrs_module'))
        
    if not (1 <= impact_score <= 5) or not (1 <= likelihood <= 5):
        flash('Etki ve Olasılık değerleri 1-5 arasında olmalıdır.', 'warning')
        return redirect(url_for('esrs_module'))
        
    success = manager.add_materiality_item(company_id, topic, impact_score, likelihood, financial_effect, environmental_effect)
    if success:
        flash('Önemlilik maddesi eklendi.', 'success')
    else:
        flash('Madde eklenirken hata oluştu.', 'danger')
    return redirect(url_for('esrs_module'))

@app.route('/esrs/materiality/delete/<int:item_id>', methods=['POST'])
@require_company_context
def esrs_materiality_delete(item_id):
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('esrs')
    if manager:
        company_id = g.company_id
        if manager.delete_materiality_item(item_id, company_id):
            flash('Madde silindi.', 'success')
        else:
            flash('Silme hatası.', 'danger')
            
    return redirect(url_for('esrs_module'))

@app.route('/tcfd')
@require_company_context
def tcfd_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {
        'governance_score': 0,
        'strategy_score': 0,
        'risk_score': 0,
        'metrics_score': 0,
        'total_risks': 0,
        'financial_impact': '-'
    }
    recommendations = []
    financial_impacts = []
    
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tcfd_disclosures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER,
                category TEXT,
                disclosure TEXT,
                impact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        rows = conn.execute("SELECT * FROM tcfd_disclosures WHERE company_id = ? ORDER BY created_at DESC", (company_id,)).fetchall()
        recommendations = [dict(r) for r in rows]
        
        # Calculate stats
        cats = set([r['category'] for r in recommendations])
        if 'Governance' in cats: stats['governance_score'] = 100
        if 'Strategy' in cats: stats['strategy_score'] = 100
        if 'Risk Management' in cats: stats['risk_score'] = 100
        if 'Metrics & Targets' in cats: stats['metrics_score'] = 100
        
        stats['total_risks'] = len(recommendations)
        
        conn.close()

        # Get Financial Impacts
        manager = MANAGERS.get('tcfd')
        if manager:
            financial_impacts = manager.get_financial_impacts(company_id)
            if financial_impacts:
                total_impact = sum([float(i['financial_impact'] or 0) for i in financial_impacts])
                stats['financial_impact'] = f"{total_impact:,.0f}"

    except Exception as e:
        logging.error(f"TCFD module error: {e}")
            
    return render_template('tcfd.html', title='TCFD İklim Riskleri', manager_available=True, stats=stats, recommendations=recommendations, financial_impacts=financial_impacts)

@app.route('/tnfd')
@require_company_context
def tnfd_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {
        'governance_score': 0,
        'strategy_score': 0,
        'risk_score': 0,
        'metrics_score': 0,
        'total_risks': 0,
        'nature_impact': '-'
    }
    recommendations = []
    
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tnfd_disclosures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER,
                pillar TEXT,
                disclosure TEXT,
                nature_impact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        rows = conn.execute("SELECT * FROM tnfd_disclosures WHERE company_id = ? ORDER BY created_at DESC", (company_id,)).fetchall()
        recommendations = [dict(r) for r in rows]
        
        # Calculate stats
        pillars = set([r['pillar'] for r in recommendations])
        if 'Governance' in pillars: stats['governance_score'] = 100
        if 'Strategy' in pillars: stats['strategy_score'] = 100
        if 'Risk & Impact Management' in pillars: stats['risk_score'] = 100
        if 'Metrics & Targets' in pillars: stats['metrics_score'] = 100
        
        stats['total_risks'] = len(recommendations)
        
        conn.close()
    except Exception as e:
        logging.error(f"TNFD module error: {e}")
            
    return render_template('tnfd.html', title='TNFD Doğa İlişkili Beyanlar', manager_available=True, stats=stats, recommendations=recommendations)

@app.route('/tcfd/add', methods=['GET', 'POST'])
@require_company_context
def tcfd_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            company_id = g.company_id
            year = request.form.get('year')
            category = request.form.get('category')
            disclosure = request.form.get('disclosure')
            impact = request.form.get('impact')
            
            conn = get_db()
            conn.execute("""
                INSERT INTO tcfd_disclosures (company_id, year, category, disclosure, impact)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, year, category, disclosure, impact))
            conn.commit()
            conn.close()
            
            flash('TCFD verisi başarıyla eklendi.', 'success')
            return redirect(url_for('tcfd_module'))
        except Exception as e:
            logging.error(f"Error adding TCFD data: {e}")
            flash(f'Hata: {e}', 'danger')
        
    return render_template('tcfd_edit.html', title='TCFD Veri Girişi')

@app.route('/tcfd/add_impact', methods=['POST'])
@require_company_context
def tcfd_add_impact():
    """Finansal etki ekleme"""
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('tcfd')
    if not manager:
        flash('TCFD Yöneticisi başlatılamadı.', 'danger')
        return redirect(url_for('tcfd_module'))

    company_id = g.company_id
    data = {
        'risk_opportunity_type': request.form.get('risk_opportunity_type'),
        'description': request.form.get('description'),
        'financial_impact': float(request.form.get('financial_impact') or 0),
        'impact_description': request.form.get('impact_description'),
        'probability': request.form.get('probability'),
        'time_horizon': request.form.get('time_horizon'),
        'scenario': request.form.get('scenario')
    }

    success, msg = manager.add_financial_impact(company_id, data)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    
    return redirect(url_for('tcfd_module'))

@app.route('/tcfd/delete_impact/<int:impact_id>', methods=['POST'])
@require_company_context
def tcfd_delete_impact(impact_id):
    """Finansal etki silme"""
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('tcfd')
    if not manager:
        flash('TCFD Yöneticisi başlatılamadı.', 'danger')
        return redirect(url_for('tcfd_module'))

    company_id = g.company_id
    success, msg = manager.delete_financial_impact(company_id, impact_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    
    return redirect(url_for('tcfd_module'))

@app.route('/tnfd/add', methods=['GET', 'POST'])
@require_company_context
def tnfd_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            company_id = g.company_id
            year = request.form.get('year')
            pillar = request.form.get('pillar')
            disclosure = request.form.get('disclosure')
            nature_impact = request.form.get('nature_impact')
            
            conn = get_db()
            conn.execute("""
                INSERT INTO tnfd_disclosures (company_id, year, pillar, disclosure, nature_impact)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, year, pillar, disclosure, nature_impact))
            conn.commit()
            conn.close()
            
            flash('TNFD verisi başarıyla eklendi.', 'success')
            return redirect(url_for('tnfd_module'))
        except Exception as e:
            logging.error(f"Error adding TNFD data: {e}")
            flash(f'Hata: {e}', 'danger')
        
    return render_template('tnfd_edit.html', title='TNFD Veri Girişi')

@app.route('/sasb')
@require_company_context
def sasb_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {
        'total_metrics': 0,
        'topics_covered': 0,
        'completion_rate': 0
    }
    disclosures = []
    
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sasb_disclosures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER,
                topic TEXT,
                metric TEXT,
                value TEXT,
                unit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        rows = conn.execute("SELECT * FROM sasb_disclosures WHERE company_id = ? ORDER BY created_at DESC", (company_id,)).fetchall()
        disclosures = [dict(r) for r in rows]
        
        # Calculate stats
        stats['total_metrics'] = len(disclosures)
        stats['topics_covered'] = len(set([r['topic'] for r in disclosures]))
        # Mock completion (assuming ~10 key metrics per sector)
        stats['completion_rate'] = min(100, int((stats['total_metrics'] / 10) * 100))
        
        conn.close()
    except Exception as e:
        logging.error(f"SASB module error: {e}")
            
    return render_template('sasb.html', title='SASB Standartları', manager_available=True, stats=stats, disclosures=disclosures)

@app.route('/sasb/add', methods=['GET', 'POST'])
@require_company_context
def sasb_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            company_id = g.company_id
            year = request.form.get('year')
            topic = request.form.get('topic')
            metric = request.form.get('metric')
            value = request.form.get('value')
            unit = request.form.get('unit')
            
            conn = get_db()
            conn.execute("""
                INSERT INTO sasb_disclosures (company_id, year, topic, metric, value, unit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, year, topic, metric, value, unit))
            conn.commit()
            conn.close()
            
            flash('SASB verisi başarıyla eklendi.', 'success')
            return redirect(url_for('sasb_module'))
        except Exception as e:
            logging.error(f"Error adding SASB data: {e}")
            flash(f'Hata: {e}', 'danger')
        
    return render_template('sasb_edit.html', title='SASB Veri Girişi')


@app.route('/targets')
@require_company_context
def targets_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    try:
        company_id = g.company_id
        from backend.modules.reporting.target_manager import TargetManager
        tm = TargetManager(DB_PATH)
        tm.update_progress(company_id) # Ensure fresh data
        targets = tm.get_targets(company_id)
        
        return render_template('targets.html', title='Hedef Takibi', targets=targets)
    except Exception as e:
        import traceback
        logging.error(f"Error in targets_module: {e}\n{traceback.format_exc()}")
        return f"Internal Server Error: {e}", 500

@app.route('/targets/add', methods=['POST'])
@require_company_context
def targets_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    from backend.modules.reporting.target_manager import TargetManager
    
    try:
        data = {
            'name': request.form.get('name'),
            'metric_type': request.form.get('metric_type'),
            'baseline_year': request.form.get('baseline_year'),
            'baseline_value': float(request.form.get('baseline_value') or 0),
            'target_year': request.form.get('target_year'),
            'target_value': float(request.form.get('target_value') or 0)
        }
        
        tm = TargetManager()
        tm.add_target(company_id, data)
        
        # Audit Log
        audit_manager.log_action(
            user_id=session.get('user_id'), 
            action="CREATE_TARGET", 
            resource="company_targets", 
            details=f"Target '{data['name']}' created", 
            ip_address=request.remote_addr,
            company_id=company_id
        )
        
        flash('Hedef başarıyla eklendi.', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
        
    return redirect(url_for('targets_module'))



# --- SYSTEM HEALTH CHECK ROUTE ---
@app.route('/system/health')
def system_health_check():
    results = {
        'status': 'ok',
        'checks': {}
    }
    
    # 1. Database Check
    try:
        conn = get_db()
        cursor = conn.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        results['checks']['database'] = 'ok'
    except Exception as e:
        results['checks']['database'] = str(e)
        results['status'] = 'error'

    # 2. Template Folder Check
    template_dir = os.path.join(BASE_DIR, 'templates')
    if os.path.exists(template_dir) and os.path.isdir(template_dir):
         results['checks']['templates_dir'] = 'ok'
    else:
         results['checks']['templates_dir'] = 'missing'
         results['status'] = 'error'

    # 3. Critical Tables Check
    required_tables = ['users', 'companies', 'online_surveys', 'survey_questions']
    try:
        conn = get_db()
        cursor = conn.cursor()
        existing_tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            results['checks']['missing_tables'] = missing_tables
            results['status'] = 'error'
        else:
            results['checks']['tables'] = 'ok'
    except Exception:
        pass

    return jsonify(results)

if __name__ == '__main__':
    # Production'da debug=False olmalı
    is_debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=is_debug)


@app.route('/advanced_calculation')
@require_company_context
def advanced_calculation_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('advanced_calculation.html', title='Advanced Calculation')


@app.route('/advanced_inventory')
@require_company_context
def advanced_inventory_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('advanced_inventory.html', title='Advanced Inventory')


@app.route('/advanced_reporting')
@require_company_context
def advanced_reporting_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('advanced_reporting.html', title='Advanced Reporting')


@app.route('/ai')
@require_company_context
def ai_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('ai.html', title='Ai')


@app.route('/ai_reports', methods=['GET', 'POST'])
@require_company_context
def ai_reports_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    
    # Imports
    try:
        from backend.modules.ai.ai_manager import AIManager
        from backend.modules.sdg.sdg_manager import SdgManager
        from backend.modules.analytics.advanced_materiality_analyzer import AdvancedMaterialityAnalyzer
        
        ai_manager = AIManager(DB_PATH)
        sdg_manager = SdgManager(DB_PATH)
        mat_analyzer = AdvancedMaterialityAnalyzer(DB_PATH)
    except ImportError:
        logging.error("Module import error in ai_reports_module")
        return render_template('ai_reports.html', title='AI Analiz Merkezi', error="Modüller yüklenemedi.")
    
    # Fetch Data
    sdg_stats = {}
    try:
        selected_goals = sdg_manager.get_selected_goals(company_id)
        sdg_stats['selected_count'] = len(selected_goals)
    except Exception as e:
        logging.error(f"SDG fetch error: {e}")
        sdg_stats['selected_count'] = 0
        
    mat_stats = {}
    try:
        mat_summary = mat_analyzer.get_materiality_summary(company_id)
        mat_stats['high_priority'] = mat_summary.get('high_materiality_count', 0)
        mat_stats['total_topics'] = mat_summary.get('total_topics', 0)
    except Exception as e:
        logging.error(f"Materiality fetch error: {e}")
        mat_stats['high_priority'] = 0
        mat_stats['total_topics'] = 0

    analysis_result = None
    
    if request.method == 'POST':
        # Generate Analysis
        if ai_manager.is_available():
            # Gather comprehensive data
            data_payload = {
                "company_id": company_id,
                "reporting_period": datetime.now().year,
                "modules": ["sdg", "materiality"],
                "metrics": {
                    "sdg_selected": sdg_stats['selected_count'],
                    "materiality_high": mat_stats['high_priority'],
                    "materiality_total": mat_stats['total_topics']
                }
            }
            # Use unified report type for comprehensive summary
            analysis_result = ai_manager.generate_summary(data_payload, report_type="unified")
        else:
            # Simulation for demo/fallback
            analysis_result = f"""
**AI Analiz Simülasyonu**

**1. Yönetici Özeti**
Kurumunuzun sürdürülebilirlik yolculuğunda temel yapı taşları (SKA ve Önceliklendirme) oluşturulmuştur. Mevcut veri seti, başlangıç seviyesinde olgunluk göstermektedir.

**2. Mevcut Durum**
*   **SKA Uyumu:** {sdg_stats['selected_count']} adet Sürdürülebilir Kalkınma Amacı (SKA) seçilerek kurumsal hedeflerle hizalanmıştır.
*   **Önceliklendirme:** Paydaş ve etki analizi sonucunda {mat_stats['total_topics']} konu değerlendirilmiş, bunlardan {mat_stats['high_priority']} tanesi "Yüksek Öncelikli" olarak belirlenmiştir.

**3. İyileştirme Fırsatları**
*   Seçilen SKA'lar için somut KPI (Anahtar Performans Göstergesi) hedefleri tanımlayın.
*   Yüksek öncelikli konular için veri toplama sıklığını artırın.
*   Çevresel (E) ve Sosyal (S) metrikler arasında denge kurun.

*Not: Bu analiz, OpenAI API anahtarı tanımlanmadığı için simülasyon modunda üretilmiştir.*
"""
            
    return render_template('ai_reports.html', 
                         title='AI Analiz Merkezi', 
                         manager_available=ai_manager.is_available() if 'ai_manager' in locals() else False,
                         sdg_stats=sdg_stats,
                         mat_stats=mat_stats,
                         analysis_result=analysis_result)




@app.route('/analytics')
@require_company_context
def analytics_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('analytics.html', title='Analytics')


@app.route('/auditor')
@require_company_context
def auditor_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('auditor.html', title='Auditor')


@app.route('/automated_reporting')
@require_company_context
def automated_reporting_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('automated_reporting.html', title='Automated Reporting')


@app.route('/automation')
@require_company_context
def automation_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('automation.html', title='Automation')


@app.route('/auto_tasks')
@require_company_context
def auto_tasks_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('auto_tasks.html', title='Auto Tasks')


@app.route('/cbam_edit')
@require_company_context
def cbam_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('cbam_edit.html', title='Cbam Edit')


@app.route('/cdp_edit')
@require_company_context
def cdp_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('cdp_edit.html', title='Cdp Edit')


@app.route('/company')
@require_company_context
def company_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('company.html', title='Company')


@app.route('/company_detail')
@require_company_context
def company_detail_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('company_detail.html', title='Company Detail')


@app.route('/company_edit', methods=['GET', 'POST'])
@require_company_context
def company_edit_module():
    if 'user' not in session: return redirect(url_for('login'))

    company_id = g.company_id
    
    if request.method == 'POST':
        try:
            # Form verilerini al
            form_data = {
                'sirket_adi': request.form.get('sirket_adi'),
                'ticari_unvan': request.form.get('ticari_unvan'),
                'vergi_no': request.form.get('vergi_no'),
                'vergi_dairesi': request.form.get('vergi_dairesi'),
                'email': request.form.get('email'),
                'telefon': request.form.get('telefon'),
                'website': request.form.get('website'),
                'calisan_sayisi': request.form.get('calisan_sayisi', type=int),
                'aktif': 1 if request.form.get('aktif') == 'on' else 0,
                'sektor': request.form.get('sektor'),
                'il': request.form.get('il'),
                'ilce': request.form.get('ilce'),
                'posta_kodu': request.form.get('posta_kodu'),
                'adres': request.form.get('adres'),
                'vizyon': request.form.get('vizyon'),
                'misyon': request.form.get('misyon'),
                'degerler': request.form.get('degerler'),
                'tesisler_ozet': request.form.get('tesisler_ozet'),
                'kilometre_taslari_ozet': request.form.get('kilometre_taslari_ozet'),
                'urun_hizmet_ozet': request.form.get('urun_hizmet_ozet'),
                'karbon_profili_ozet': request.form.get('karbon_profili_ozet'),
                'uyelikler_ozet': request.form.get('uyelikler_ozet'),
                'oduller_ozet': request.form.get('oduller_ozet'),
            }

            conn = get_db()
            cursor = conn.cursor()
            
            # Kontrol et: Kayıt var mı?
            # Ensure company_info table exists
            ensure_company_info_table()
            
            cursor.execute("SELECT id FROM company_info WHERE company_id = ?", (company_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Güncelleme
                update_query = """
                    UPDATE company_info SET
                        sirket_adi = ?, ticari_unvan = ?, vergi_no = ?, vergi_dairesi = ?,
                        email = ?, telefon = ?, website = ?, calisan_sayisi = ?,
                        aktif = ?, sektor = ?, il = ?, ilce = ?, posta_kodu = ?, adres = ?,
                        vizyon = ?, misyon = ?, degerler = ?, tesisler_ozet = ?,
                        kilometre_taslari_ozet = ?, urun_hizmet_ozet = ?,
                        karbon_profili_ozet = ?, uyelikler_ozet = ?, oduller_ozet = ?,
                        
                        -- İngilizce alanları da güncelle (uyumluluk için)
                        name = ?, tax_number = ?, phone = ?, 
                        sector = ?, employee_count = ?, is_active = ?,
                        headquarters_address = ?, city = ?, postal_code = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE company_id = ?
                """
                cursor.execute(update_query, (
                    form_data['sirket_adi'], form_data['ticari_unvan'], form_data['vergi_no'], form_data['vergi_dairesi'],
                    form_data['email'], form_data['telefon'], form_data['website'], form_data['calisan_sayisi'],
                    form_data['aktif'], form_data['sektor'], form_data['il'], form_data['ilce'], form_data['posta_kodu'], form_data['adres'],
                    form_data['vizyon'], form_data['misyon'], form_data['degerler'], form_data['tesisler_ozet'],
                    form_data['kilometre_taslari_ozet'], form_data['urun_hizmet_ozet'],
                    form_data['karbon_profili_ozet'], form_data['uyelikler_ozet'], form_data['oduller_ozet'],
                    
                    # İngilizce mapping
                    form_data['sirket_adi'], form_data['vergi_no'], form_data['telefon'],
                    form_data['sektor'], form_data['calisan_sayisi'], form_data['aktif'],
                    form_data['adres'], form_data['il'], form_data['posta_kodu'],
                    
                    company_id
                ))
            else:
                # Yeni Kayıt
                insert_query = """
                    INSERT INTO company_info (
                        company_id, sirket_adi, ticari_unvan, vergi_no, vergi_dairesi,
                        email, telefon, website, calisan_sayisi,
                        aktif, sektor, il, ilce, posta_kodu, adres,
                        vizyon, misyon, degerler, tesisler_ozet,
                        kilometre_taslari_ozet, urun_hizmet_ozet,
                        karbon_profili_ozet, uyelikler_ozet, oduller_ozet,
                        
                        name, tax_number, phone, sector, employee_count, is_active,
                        headquarters_address, city, postal_code
                    ) VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?,
                        ?, ?, ?,
                        
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?
                    )
                """
                cursor.execute(insert_query, (
                    company_id, form_data['sirket_adi'], form_data['ticari_unvan'], form_data['vergi_no'], form_data['vergi_dairesi'],
                    form_data['email'], form_data['telefon'], form_data['website'], form_data['calisan_sayisi'],
                    form_data['aktif'], form_data['sektor'], form_data['il'], form_data['ilce'], form_data['posta_kodu'], form_data['adres'],
                    form_data['vizyon'], form_data['misyon'], form_data['degerler'], form_data['tesisler_ozet'],
                    form_data['kilometre_taslari_ozet'], form_data['urun_hizmet_ozet'],
                    form_data['karbon_profili_ozet'], form_data['uyelikler_ozet'], form_data['oduller_ozet'],
                    
                    form_data['sirket_adi'], form_data['vergi_no'], form_data['telefon'], form_data['sektor'], form_data['calisan_sayisi'], form_data['aktif'],
                    form_data['adres'], form_data['il'], form_data['posta_kodu']
                ))
                
            conn.commit()
            conn.close()
            flash('Firma bilgileri başarıyla güncellendi.', 'success')
            return redirect(url_for('company_edit_module'))
            
        except Exception as e:
            logging.error(f"Company update error: {e}")
            flash(f'Hata oluştu: {str(e)}', 'danger')
            return redirect(url_for('company_edit_module'))

    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # company_info'dan çek
    cursor.execute("SELECT * FROM company_info WHERE company_id = ?", (company_id,))
    row = cursor.fetchone()
    
    company = {}
    if row:
        company = dict(row)
    
    # Eğer company_info boşsa veya eksikse companies tablosundan temel bilgileri birleştir
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    basic_company = cursor.fetchone()
    
    if basic_company:
        basic_data = dict(basic_company)
        # Temel verileri company dict'ine yedekle (varsa üzerine yazmaz, yoksa ekler)
        # Ancak burada öncelik company_info olmalı.
        # company_info'da olmayan ama companies'de olanları ekleyelim.
        
        # Mapping: companies -> company_info keys
        mapping = {
            'name': 'sirket_adi',
            'sector': 'sektor',
            'is_active': 'aktif',
            'tax_number': 'vergi_no',
            'phone': 'telefon',
            'email': 'email',
            'website': 'website',
            'address': 'adres',
            'city': 'il',
            'country': 'ulke'
        }
        
        for basic_key, info_key in mapping.items():
            if basic_key in basic_data and (info_key not in company or not company[info_key]):
                company[info_key] = basic_data[basic_key]
                
        # Also keep original keys just in case
        for k, v in basic_data.items():
            if k not in company:
                company[k] = v

    # Jinja2 template'de .attribute erişimi için SafeDict kullanımı
    class SafeDict(dict):
        def __getattr__(self, item):
            return self.get(item, None)
            
    company = SafeDict(company)


    conn.close()
    return render_template('company_edit.html', title='Company Edit', company=company)


@app.route('/company_info')
@require_company_context
def company_info_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('company_info.html', title='Company Info')


@app.route('/company_info_edit')
@require_company_context
def company_info_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('company_info_edit.html', title='Company Info Edit')


@app.route('/company_stakeholder_survey')
@require_company_context
def company_stakeholder_survey_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('company_stakeholder_survey.html', title='Company Stakeholder Survey')


@app.route('/database')
@require_company_context
def database_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('database.html', title='Database')


@app.route('/data_collection')
@require_company_context
def data_collection_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('data_collection.html', title='Data Collection')


@app.route('/data_edit')
@require_company_context
def data_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('data_edit.html', title='Data Edit')


@app.route('/data_import', methods=['GET', 'POST'])
@require_company_context
def data_import_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    importer = DataImporter(DB_PATH)
    stats = {}
    records = []
    
    # Check for existing imports
    try:
        conn = get_db()
        # Fetch import history
        # (This is a simplified view, normally we'd query data_imports table if it exists)
        # But for now, let's just show the upload form.
        conn.close()
    except: pass

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Dosya seçilmedi', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('Dosya seçilmedi', 'danger')
            return redirect(request.url)
            
        allowed_extensions = {'csv', 'xlsx', 'xls'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
             flash('Geçersiz dosya formatı. Sadece .csv, .xlsx, .xls yüklenebilir.', 'danger')
             return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(BACKEND_DIR, 'data', 'uploads', str(g.company_id))
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            import_type = request.form.get('import_type')
            
            # Simple mapping of import_type to table
            type_table_map = {
                'carbon': 'carbon_emissions',
                'energy': 'energy_consumption',
                'water': 'water_consumption',
                'waste': 'waste_generation'
            }
            
            target_table = type_table_map.get(import_type)
            if not target_table:
                 flash('Geçersiz import tipi.', 'danger')
                 return redirect(request.url)
            
            # Prepare mapping: Standard Turkish keys + English DB keys
            column_mapping = importer.STANDARD_KEY_MAP.copy()
            # Add some common English keys for flexibility
            extra_keys = ['source_type', 'amount', 'unit', 'year', 'period', 'description', 'date', 'value']
            for k in extra_keys:
                column_mapping[k] = k
                
            try:
                result = importer.import_data(
                    company_id=g.company_id,
                    file_path=file_path,
                    import_type=import_type,
                    column_mapping=column_mapping,
                    target_table=target_table,
                    imported_by=session.get('user_id')
                )
                
                msg_type = 'success' if result['failed'] == 0 else 'warning'
                flash(f"Import tamamlandı: {result['successful']} satır eklendi, {result['failed']} satır hatalı.", msg_type)
                
                if result['errors']:
                    # Show first few errors
                    for err in result['errors'][:5]:
                        flash(err, 'danger')
                        
            except Exception as e:
                logging.error(f"Import error: {e}")
                flash(f"Import işlemi sırasında hata: {e}", 'danger')
                
            return redirect(url_for('data_import_module'))

    return render_template('data_import.html', title='Data Import')


@app.route('/data_inventory')
@require_company_context
def data_inventory_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('data_inventory.html', title='Data Inventory')


@app.route('/data_provenance')
@require_company_context
def data_provenance_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('data_provenance.html', title='Data Provenance')


@app.route('/digital_security')
@require_company_context
def digital_security_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('digital_security.html', title='Digital Security')


@app.route('/document_processing')
@require_company_context
def document_processing_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('document_processing.html', title='Document Processing')


@app.route('/economic_edit')
@require_company_context
def economic_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('economic_edit.html', title='Economic Edit')


@app.route('/emergency')
@require_company_context
def emergency_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('emergency.html', title='Emergency')


@app.route('/emission_reduction')
@require_company_context
def emission_reduction_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('emission_reduction.html', title='Emission Reduction')


@app.route('/environmental')
@require_company_context
def environmental_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {
        'carbon_emissions': 0,
        'energy_consumption': 0,
        'water_consumption': 0,
        'waste_generation': 0
    }
    
    try:
        conn = get_db()
        # Simple counts or sums
        try:
            stats['carbon_emissions'] = conn.execute("SELECT COUNT(*) FROM carbon_emissions WHERE company_id=?", (company_id,)).fetchone()[0]
        except: pass
        try:
            stats['energy_consumption'] = conn.execute("SELECT COUNT(*) FROM energy_consumption WHERE company_id=?", (company_id,)).fetchone()[0]
        except: pass
        try:
            stats['water_consumption'] = conn.execute("SELECT COUNT(*) FROM water_consumption WHERE company_id=?", (company_id,)).fetchone()[0]
        except: pass
        try:
            stats['waste_generation'] = conn.execute("SELECT COUNT(*) FROM waste_generation WHERE company_id=?", (company_id,)).fetchone()[0]
        except: pass
        conn.close()
    except Exception as e:
        logging.error(f"Environmental stats error: {e}")
        
    return render_template('environmental.html', title='Çevresel Yönetim', stats=stats, manager_available=True)


@app.route('/erp_integration')
@require_company_context
def erp_integration_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('erp_integration.html', title='Erp Integration')


@app.route('/esg_edit')
@require_company_context
def esg_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('esg_edit.html', title='Esg Edit')


@app.route('/eu_taxonomy')
@require_company_context
def eu_taxonomy_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {}
    records = []
    
    try:
        from backend.modules.eu_taxonomy.taxonomy_manager import EUTaxonomyManager
        manager = EUTaxonomyManager(DB_PATH)
        
        stats = manager.get_taxonomy_stats(company_id)
        records = manager.get_taxonomy_activities(company_id)
        
    except Exception as e:
        logging.error(f"EU Taxonomy module error: {e}")
        
    return render_template('eu_taxonomy.html', title='Eu Taxonomy', stats=stats, records=records, manager_available=True)


@app.route('/file_manager')
@require_company_context
def file_manager_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('file_manager.html', title='File Manager')


@app.route('/forms')
@require_company_context
def forms_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('forms.html', title='Forms')


@app.route('/framework_mapping')
@require_company_context
def framework_mapping_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('framework_mapping.html', title='Framework Mapping')


@app.route('/governance_edit')
@require_company_context
def governance_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('governance_edit.html', title='Governance Edit')


@app.route('/gri_edit')
@require_company_context
def gri_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('gri_edit.html', title='Gri Edit')


@app.route('/innovation')
@require_company_context
def innovation_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('innovation.html', title='Innovation')


@app.route('/integration')
@require_company_context
def integration_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('integration.html', title='Integration')


@app.route('/issb_edit')
@require_company_context
def issb_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('issb_edit.html', title='Issb Edit')


@app.route('/mapping')
@require_company_context
def mapping_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('mapping')
    mappings = []
    suggestions = []
    stats = {}
    
    if manager:
        try:
            mappings = manager.get_all_mappings()
            suggestions = manager.get_suggestions('pending')
            
            stats['total_mappings'] = len(mappings)
            stats['verified'] = sum(1 for m in mappings if m.get('verified'))
            stats['suggestions'] = len(suggestions)
        except Exception as e:
            logging.error(f"Mapping module error: {e}")
            
    return render_template('mapping.html', title='Eşleştirme', mappings=mappings, suggestions=suggestions, stats=stats, manager_available=bool(manager))


@app.route('/mapping/suggestions/generate', methods=['POST'])
@require_company_context
def mapping_generate_suggestions():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('mapping')
    if manager:
        try:
            count = manager.generate_suggestions()
            if count > 0:
                flash(f'{count} yeni eşleştirme önerisi oluşturuldu.', 'success')
            else:
                flash('Yeni öneri bulunamadı veya oluşturulamadı.', 'info')
        except Exception as e:
            flash(f'Hata: {e}', 'danger')
            
    return redirect(url_for('mapping_module'))


@app.route('/mapping/suggestions/approve/<int:id>', methods=['POST'])
@require_company_context
def mapping_approve_suggestion(id):
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('mapping')
    if manager:
        try:
            if manager.approve_suggestion(id):
                flash('Öneri onaylandı ve eklendi.', 'success')
            else:
                flash('Öneri onaylanamadı.', 'danger')
        except Exception as e:
            flash(f'Hata: {e}', 'danger')
            
    return redirect(url_for('mapping_module'))


@app.route('/mapping/suggestions/reject/<int:id>', methods=['POST'])
@require_company_context
def mapping_reject_suggestion(id):
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('mapping')
    if manager:
        try:
            if manager.reject_suggestion(id):
                flash('Öneri reddedildi.', 'success')
            else:
                flash('Öneri reddedilemedi.', 'danger')
        except Exception as e:
            flash(f'Hata: {e}', 'danger')
            
    return redirect(url_for('mapping_module'))


@app.route('/message_new')
@require_company_context
def message_new_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('message_new.html', title='Message New')


@app.route('/policy_library')
@require_company_context
def policy_library_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('policy_library.html', title='Policy Library')


@app.route('/prioritization')
@require_company_context
def prioritization_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {}
    records = []
    columns = ['topic_name', 'category', 'priority_score', 'stakeholder_impact', 'business_impact']
    
    try:
        from backend.modules.prioritization.prioritization_manager import PrioritizationManager
        manager = PrioritizationManager(DB_PATH)
        records = manager.get_materiality_topics(company_id)
        
        # Basit istatistikler
        stats['total_topics'] = len(records)
        stats['high_priority'] = sum(1 for r in records if r.get('priority_score', 0) >= 4) # 1-5 scale varsayımı
        
    except Exception as e:
        logging.error(f"Prioritization module error: {e}")
        
    return render_template('prioritization.html', title='Prioritization', stats=stats, records=records, columns=columns, manager_available=True)


@app.route('/product_technology')
@require_company_context
def product_technology_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('product_technology.html', title='Product Technology')


@app.route('/quality')
@require_company_context
def quality_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('quality.html', title='Quality')


@app.route('/reporting')
@require_company_context
def reporting_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {'total_reports': 0, 'completed_reports': 0, 'pending_reports': 0}
    records = []
    
    try:
        conn = get_db()
        stats['total_reports'] = conn.execute("SELECT COUNT(*) FROM report_registry WHERE company_id=?", (company_id,)).fetchone()[0]
        try:
             records = conn.execute("SELECT * FROM report_registry WHERE company_id=? ORDER BY created_at DESC LIMIT 5", (company_id,)).fetchall()
        except: pass
        conn.close()
    except Exception as e:
        logging.error(f"Reporting stats error: {e}")
        
    return render_template('reporting.html', title='Raporlama', stats=stats, records=records, manager_available=True)


@app.route('/report_edit')
@require_company_context
def report_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('report_edit.html', title='Report Edit')


@app.route('/reset_password')
@require_company_context
def reset_password_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password')


@app.route('/sasb_edit')
@require_company_context
def sasb_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('sasb_edit.html', title='Sasb Edit')


@app.route('/scenario_analysis')
@require_company_context
def scenario_analysis_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('scenario_analysis.html', title='Scenario Analysis')


@app.route('/scope3')
@require_company_context
def scope3_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('scope3.html', title='Scope3')


@app.route('/sdg_edit')
@require_company_context
def sdg_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('sdg_edit.html', title='Sdg Edit')


@app.route('/security')
@require_company_context
def security_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('security.html', title='Security')


@app.route('/skdm')
@require_company_context
def skdm_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('skdm.html', title='Skdm')


@app.route('/social_edit')
@require_company_context
def social_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('social_edit.html', title='Social Edit')


@app.route('/stakeholder')
@require_company_context
def stakeholder_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {}
    records = []
    columns = ['stakeholder_name', 'stakeholder_type', 'organization', 'influence_level', 'interest_level', 'status']
    
    try:
        from backend.modules.stakeholder.stakeholder_manager import StakeholderManager
        manager = StakeholderManager(DB_PATH)
        
        # Get stats
        summary = manager.get_stakeholder_summary(company_id)
        
        stats['total_stakeholders'] = summary.get('total_stakeholders', 0)
        stats['total_engagements'] = summary.get('total_engagements', 0)
        
        online_stats = summary.get('online_survey_summary', {})
        if online_stats:
            stats['active_surveys'] = online_stats.get('active_surveys', 0)
            stats['survey_responses'] = online_stats.get('total_responses', 0)
            stats['sdg_performance'] = online_stats.get('sdg_performance', {})
        
        # Fallback if 0
        if stats['total_stakeholders'] == 0:
            conn = get_db()
            try:
                stats['total_stakeholders'] = conn.execute("SELECT COUNT(*) FROM stakeholders WHERE company_id=?", (company_id,)).fetchone()[0]
            except: pass
            conn.close()
        
        # Get records
        try:
            conn = get_db()
            records = conn.execute("SELECT * FROM stakeholders WHERE company_id=? ORDER BY id DESC", (company_id,)).fetchall()
            # Convert to dict list
            records = [dict(row) for row in records]
            conn.close()
        except Exception as e:
            logging.error(f"Error fetching stakeholders: {e}")
            
    except Exception as e:
        logging.error(f"Stakeholder module error: {e}")
        
    return render_template('stakeholder.html', title='Paydaş Yönetimi', stats=stats, records=records, columns=columns, manager_available=True)


@app.route('/stakeholder/add', methods=['POST'])
@require_company_context
def add_stakeholder():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    # Form data
    name = request.form.get('stakeholder_name')
    type_ = request.form.get('stakeholder_type')
    organization = request.form.get('organization')
    contact = request.form.get('contact_person')
    email = request.form.get('contact_email')
    phone = request.form.get('contact_phone')
    influence = request.form.get('influence_level')
    interest = request.form.get('interest_level')
    
    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO stakeholders (
                company_id, stakeholder_name, stakeholder_type, organization, 
                contact_person, contact_email, contact_phone, 
                influence_level, interest_level, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (company_id, name, type_, organization, contact, email, phone, influence, interest))
        conn.commit()
        conn.close()
        flash('Paydaş başarıyla eklendi.', 'success')
    except Exception as e:
        logging.error(f"Error adding stakeholder: {e}")
        # Fallback for 'stakeholder_group' column name difference if needed
        try:
            conn = get_db()
            conn.execute("""
                INSERT INTO stakeholders (
                    company_id, stakeholder_name, stakeholder_group, organization, 
                    email, phone, priority_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, name, type_, organization, email, phone, influence))
            conn.commit()
            conn.close()
            flash('Paydaş başarıyla eklendi.', 'success')
        except Exception as e2:
             logging.error(f"Error adding stakeholder (retry): {e2}")
             flash('Paydaş eklenirken hata oluştu.', 'error')

    return redirect(url_for('stakeholder_module'))


@app.route('/surveys/add', methods=['POST'])
@require_company_context
def add_survey():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    title = request.form.get('survey_title')
    desc = request.form.get('survey_description')
    # target = request.form.get('target_groups') # Legacy
    stakeholder_group = request.form.get('stakeholder_group')
    template_id = request.form.get('template_id')
    
    # Set target group name from selection if possible
    target = stakeholder_group if stakeholder_group else request.form.get('target_groups')
    
    import secrets
    token = secrets.token_urlsafe(16)
    link = f"/survey/{token}"
    
    try:
        conn = get_db()
        # Create table if not exists (just in case)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS online_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                survey_title TEXT NOT NULL,
                survey_description TEXT,
                target_groups TEXT NOT NULL,
                survey_link TEXT UNIQUE NOT NULL,
                start_date DATE,
                end_date DATE,
                total_questions INTEGER DEFAULT 0,
                response_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        cursor = conn.execute("""
            INSERT INTO online_surveys (
                company_id, survey_title, survey_description, target_groups, 
                survey_link, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, 1, datetime('now'))
        """, (company_id, title, desc, target, link))
        
        survey_id = cursor.lastrowid
        
        # If stakeholder group selected, load specific questions
        if stakeholder_group:
            try:
                import json
                import os
                json_path = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'stakeholder_questions.json')
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        group_data = data.get(stakeholder_group)
                        if group_data and 'questions' in group_data:
                            questions = group_data['questions']
                            for q in questions:
                                conn.execute("""
                                    INSERT INTO survey_questions (
                                        survey_id, question_text, question_type, 
                                        category, options, is_required, display_order, company_id
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    survey_id, q['question_text'], q['question_type'],
                                    q.get('category', 'General'), q.get('options'), 
                                    1, 0, company_id
                                ))
                            # Update count
                            conn.execute("UPDATE online_surveys SET total_questions=? WHERE id=? AND company_id=?", (len(questions), survey_id, company_id))
            except Exception as e:
                logging.error(f"Error loading stakeholder questions: {e}")

        # If template selected (legacy), copy questions
        elif template_id:
            try:
                # Verify template access
                tmpl = conn.execute("SELECT id FROM survey_templates WHERE id=? AND (company_id=? OR company_id IS NULL)", (template_id, company_id)).fetchone()
                if tmpl:
                    # Get template questions
                    t_cursor = conn.execute("SELECT tq.* FROM survey_template_questions tq JOIN survey_templates st ON tq.template_id = st.id WHERE tq.template_id=? AND (st.company_id=? OR st.company_id IS NULL)", (template_id, company_id))
                    t_questions = t_cursor.fetchall()
                    
                    for tq in t_questions:
                        q = dict(tq)
                        conn.execute("""
                            INSERT INTO survey_questions (
                                survey_id, question_text, question_type, 
                                category, options, is_required, display_order, company_id
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            survey_id, q['question_text'], q['question_type'],
                            q.get('category', 'General'), q.get('options'), 
                            1, 0, company_id
                        ))
                    
                    # Update question count
                    conn.execute("UPDATE online_surveys SET total_questions=? WHERE id=? AND company_id=?", (len(t_questions), survey_id, company_id))
                else:
                    logging.warning(f"Unauthorized template access: {template_id}")
                
            except Exception as te:
                logging.error(f"Error copying template questions: {te}")
                # Continue even if template copy fails, user can add manually
        
        conn.commit()
        conn.close()
        flash('Anket başarıyla oluşturuldu.', 'success')
    except Exception as e:
        logging.error(f"Error adding survey: {e}")
        flash('Anket oluşturulurken hata oluştu.', 'error')
        
    return redirect(url_for('surveys_module'))



@app.route('/stakeholder_survey')
@require_company_context
def stakeholder_survey_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('stakeholder_survey.html', title='Stakeholder Survey')


@app.route('/standards')
@require_company_context
def standards_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('standards.html', title='Standards')


@app.route('/strategic')
@require_company_context
def strategic_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('strategic.html', title='Strategic')


# Duplicate super_admin route removed


@app.route('/super_admin_2fa')
@super_admin_required
def super_admin_2fa_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('super_admin_2fa.html', title='Super Admin 2Fa')


@app.route('/supply_chain_edit')
@require_company_context
def supply_chain_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('supply_chain_edit.html', title='Supply Chain Edit')


@app.route('/support_ticket')
@require_company_context
def support_ticket_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('support_ticket.html', title='Support Ticket')


@app.route('/surveys')
@require_company_context
def surveys_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {}
    records = []
    columns = ['survey_title', 'status', 'response_count', 'created_at']
    
    # Load stakeholder groups for dropdown
    stakeholder_groups = {}
    try:
        import json
        import os
        json_path = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'stakeholder_questions.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Format: code -> name
                for key, val in data.items():
                    stakeholder_groups[key] = val['name']
    except Exception as e:
        logging.error(f"Error loading stakeholder questions: {e}")

    try:
        from backend.modules.stakeholder.stakeholder_manager import StakeholderManager
        manager = StakeholderManager(DB_PATH)
        
        # Get stats (reuse summary)
        summary = manager.get_stakeholder_summary(company_id)
        online_stats = summary.get('online_survey_summary', {})
        
        stats['active_surveys'] = online_stats.get('active_surveys', 0)
        stats['total_responses'] = online_stats.get('total_responses', 0)
        
        # Get survey records
        conn = get_db()
        cursor = conn.execute("""
            SELECT 
                id,
                survey_title, 
                CASE WHEN is_active = 1 THEN 'Aktif' ELSE 'Pasif' END as status,
                response_count, 
                created_at,
                survey_link
            FROM online_surveys 
            WHERE company_id=? 
            ORDER BY created_at DESC
        """, (company_id,))
        
        rows = cursor.fetchall()
        # Add survey_link to the dict keys but keep columns list same for display
        records = []
        for row in rows:
            rec = dict(zip(['id'] + columns + ['survey_link'], row))
            # Safely extract token for template usage
            if rec.get('survey_link') and '/' in rec['survey_link']:
                rec['token'] = rec['survey_link'].split('/')[-1]
            else:
                rec['token'] = ''
            records.append(rec)
        
        conn.close()
    except Exception as e:
        logging.error(f"Surveys module error: {e}")
        
    return render_template('surveys.html', title='Surveys', stats=stats, records=records, columns=columns, manager_available=True, stakeholder_groups=stakeholder_groups)



# Standard Survey Questions Pool
STANDARD_QUESTIONS = {
    'Environmental': [
        {'text': 'Şirketinizin karbon ayak izini ölçüyor musunuz?', 'type': 'yes_no', 'required': 1},
        {'text': 'Yıllık enerji tüketiminizde azalma hedefiniz var mı?', 'type': 'yes_no', 'required': 1},
        {'text': 'Atık yönetimi politikanız ne kadar etkin uygulanıyor?', 'type': 'scale_1_5', 'required': 1},
        {'text': 'Su tüketimini azaltmak için hangi önlemleri alıyorsunuz?', 'type': 'text', 'required': 0},
        {'text': 'Yenilenebilir enerji kaynakları kullanıyor musunuz?', 'type': 'yes_no', 'required': 1},
        {'text': 'İklim değişikliği risk analizi yapıyor musunuz?', 'type': 'yes_no', 'required': 1},
        {'text': 'Tedarikçilerinizin çevresel performansını değerlendiriyor musunuz?', 'type': 'scale_1_5', 'required': 1},
        {'text': 'Ürünlerinizin yaşam döngüsü analizi yapılıyor mu?', 'type': 'yes_no', 'required': 0},
        {'text': 'Biyoçeşitliliği koruma politikanız var mı?', 'type': 'yes_no', 'required': 1},
        {'text': 'Sıfır atık hedefleriniz var mı?', 'type': 'yes_no', 'required': 1}
    ],
    'Social': [
        {'text': 'Çalışan memnuniyeti anketleri düzenli yapılıyor mu?', 'type': 'yes_no', 'required': 1},
        {'text': 'İş sağlığı ve güvenliği eğitimleri ne sıklıkla veriliyor?', 'type': 'text', 'required': 1},
        {'text': 'Cinsiyet eşitliği ve kapsayıcılık politikanız var mı?', 'type': 'yes_no', 'required': 1},
        {'text': 'Toplumsal katkı projelerine katılımınız ne düzeyde?', 'type': 'scale_1_5', 'required': 1},
        {'text': 'Tedarik zincirinde insan hakları denetimi yapıyor musunuz?', 'type': 'yes_no', 'required': 1},
        {'text': 'Çalışanlarınızın sendikal hakları korunuyor mu?', 'type': 'yes_no', 'required': 1},
        {'text': 'Müşteri memnuniyeti oranınız nedir?', 'type': 'text', 'required': 0},
        {'text': 'Yerel topluluklarla etkileşim mekanizmalarınız var mı?', 'type': 'yes_no', 'required': 1},
        {'text': 'Çalışan devir hızınız (turnover) nedir?', 'type': 'text', 'required': 0},
        {'text': 'Ayrımcılık karşıtı politikanız etkin uygulanıyor mu?', 'type': 'scale_1_5', 'required': 1}
    ],
    'Governance': [
        {'text': 'Yönetim kurulunda sürdürülebilirlik temsil ediliyor mu?', 'type': 'yes_no', 'required': 1},
        {'text': 'Etik kuralları ve uyum politikalarınız mevcut mu?', 'type': 'yes_no', 'required': 1},
        {'text': 'Yolsuzlukla mücadele eğitimleri veriliyor mu?', 'type': 'yes_no', 'required': 1},
        {'text': 'Şeffaflık ve raporlama standartlarına uyumunuz ne düzeyde?', 'type': 'scale_1_5', 'required': 1},
        {'text': 'Paydaş katılımı mekanizmalarınız ne kadar etkin?', 'type': 'scale_1_5', 'required': 1},
        {'text': 'Risk yönetimi süreçleriniz ESG risklerini kapsıyor mu?', 'type': 'yes_no', 'required': 1},
        {'text': 'Yöneticilerin performansı sürdürülebilirlik hedeflerine bağlı mı?', 'type': 'yes_no', 'required': 1},
        {'text': 'Veri gizliliği ve güvenliği politikanız güncel mi?', 'type': 'yes_no', 'required': 1},
        {'text': 'İç denetim mekanizmanız ne sıklıkla çalışıyor?', 'type': 'text', 'required': 1},
        {'text': 'Hissedarların sürdürülebilirlik kararlarına katılımı nasıl sağlanıyor?', 'type': 'text', 'required': 0}
    ],
    'General': [
        {'text': 'Kurumunuzun genel sürdürülebilirlik performansını nasıl değerlendiriyorsunuz?', 'type': 'scale_1_5', 'required': 1},
        {'text': 'Gelecek yıl için en önemli önceliğiniz nedir?', 'type': 'text', 'required': 1}
    ]
}

@app.route('/surveys/<int:survey_id>')
@require_company_context
def survey_detail(survey_id):
    if 'user' not in session: return redirect(url_for('login'))
    company_id = g.company_id
    
    # Load stakeholder groups for display/edit
    stakeholder_groups = {}
    try:
        import json
        import os
        json_path = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'stakeholder_questions.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, val in data.items():
                    stakeholder_groups[key] = val['name']
    except Exception as e:
        logging.error(f"Error loading stakeholder questions: {e}")

    conn = get_db()
    
    # Get survey details
    cursor = conn.execute("SELECT * FROM online_surveys WHERE id=? AND company_id=?", (survey_id, company_id))
    survey = cursor.fetchone()
    
    if not survey:
        conn.close()
        flash('Anket bulunamadı.', 'error')
        return redirect(url_for('surveys_module'))
        
    # Convert Row to dict to modify
    survey = dict(survey)
    if survey.get('survey_link') and '/' in survey['survey_link']:
        survey['token'] = survey['survey_link'].split('/')[-1]
    else:
        survey['token'] = ''
        
    # Get questions
    cursor = conn.execute("SELECT * FROM survey_questions WHERE survey_id=? AND company_id=? ORDER BY display_order, id", (survey_id, company_id))
    rows = cursor.fetchall()
    
    # Safely convert to list of dicts to avoid missing column errors in template
    questions = []
    for row in rows:
        q = dict(row)
        # Ensure new columns exist with defaults
        if 'category' not in q: q['category'] = 'General'
        if 'question_type' not in q: q['question_type'] = 'scale_1_5'
        if 'is_required' not in q: q['is_required'] = 1
        questions.append(q)
    
    # Get demographics config
    demographics = {}
    if survey['demographics_config']:
        try:
            import json
            demographics = json.loads(survey['demographics_config'])
        except:
            pass
            
    conn.close()
    
    return render_template('survey_detail.html', title=survey['survey_title'], survey=survey, questions=questions, demographics=demographics, standard_questions=STANDARD_QUESTIONS, stakeholder_groups=stakeholder_groups)

@app.route('/surveys/<int:survey_id>/add_standard_questions', methods=['POST'])
@require_company_context
def add_standard_survey_questions(survey_id):
    if 'user' not in session: return redirect(url_for('login'))
    company_id = g.company_id
    
    selected_items = request.form.getlist('selected_questions')
    
    if not selected_items:
        flash('Hiçbir soru seçilmedi.', 'warning')
        return redirect(url_for('survey_detail', survey_id=survey_id))
        
    conn = get_db()
    try:
        # Verify ownership
        cursor = conn.execute("SELECT id FROM online_surveys WHERE id=? AND company_id=?", (survey_id, company_id))
        if not cursor.fetchone():
            raise Exception("Unauthorized")
            
        count = 0
        for item in selected_items:
            try:
                cat, idx = item.split('|')
                idx = int(idx)
                if cat in STANDARD_QUESTIONS and 0 <= idx < len(STANDARD_QUESTIONS[cat]):
                    q = STANDARD_QUESTIONS[cat][idx]
                    conn.execute("""
                        INSERT INTO survey_questions (survey_id, question_text, question_type, category, is_required, display_order, company_id)
                        VALUES (?, ?, ?, ?, ?, 99, ?)
                    """, (survey_id, q['text'], q['type'], cat, q['required'], company_id))
                    count += 1
            except Exception as e:
                logging.error(f"Error parsing selection {item}: {e}")
                continue
                
        conn.commit()
        flash(f'{count} standart soru eklendi.', 'success')
    except Exception as e:
        logging.error(f"Error adding standard questions: {e}")
        flash('Hata oluştu.', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('survey_detail', survey_id=survey_id))

@app.route('/surveys/<int:survey_id>/add_question', methods=['POST'])
@require_company_context
def add_survey_question(survey_id):
    if 'user' not in session: return redirect(url_for('login'))
    company_id = g.company_id
    
    question_text = request.form.get('question_text')
    question_type = request.form.get('question_type')
    category = request.form.get('category', 'General')
    is_required = 1 if request.form.get('is_required') else 0
    
    if not question_text:
        flash('Soru metni gereklidir.', 'error')
        return redirect(url_for('survey_detail', survey_id=survey_id))
        
    conn = get_db()
    try:
        # Verify ownership
        cursor = conn.execute("SELECT id FROM online_surveys WHERE id=? AND company_id=?", (survey_id, company_id))
        if not cursor.fetchone():
            raise Exception("Unauthorized")
            
        conn.execute("""
            INSERT INTO survey_questions (survey_id, question_text, question_type, category, is_required, company_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (survey_id, question_text, question_type, category, is_required, company_id))
        
        # Update total questions count
        conn.execute("UPDATE online_surveys SET total_questions = total_questions + 1 WHERE id=? AND company_id=?", (survey_id, company_id))
        
        conn.commit()
        flash('Soru başarıyla eklendi.', 'success')
    except Exception as e:
        logging.error(f"Error adding question: {e}")
        flash('Hata oluştu.', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('survey_detail', survey_id=survey_id))

@app.route('/surveys/<int:survey_id>/delete_question/<int:question_id>', methods=['POST'])
@require_company_context
def delete_survey_question(survey_id, question_id):
    if 'user' not in session: return redirect(url_for('login'))
    company_id = g.company_id
    
    conn = get_db()
    try:
        # Verify ownership
        cursor = conn.execute("SELECT id FROM online_surveys WHERE id=? AND company_id=?", (survey_id, company_id))
        if not cursor.fetchone():
            raise Exception("Unauthorized")
            
        conn.execute("DELETE FROM survey_questions WHERE id=? AND survey_id=? AND company_id=?", (question_id, survey_id, company_id))
        
        # Update total questions count
        conn.execute("UPDATE online_surveys SET total_questions = total_questions - 1 WHERE id=? AND company_id=?", (survey_id, company_id))
        
        conn.commit()
        flash('Soru silindi.', 'success')
    except Exception as e:
        logging.error(f"Error deleting question: {e}")
        flash('Hata oluştu.', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('survey_detail', survey_id=survey_id))

@app.route('/surveys/<int:survey_id>/edit_question/<int:question_id>', methods=['POST'])
@require_company_context
def edit_survey_question(survey_id, question_id):
    if 'user' not in session: return redirect(url_for('login'))
    company_id = g.company_id
    
    question_text = request.form.get('question_text')
    question_type = request.form.get('question_type')
    category = request.form.get('category', 'General')
    is_required = 1 if request.form.get('is_required') else 0
    
    if not question_text:
        flash('Soru metni gereklidir.', 'error')
        return redirect(url_for('survey_detail', survey_id=survey_id))
        
    conn = get_db()
    try:
        # Verify ownership
        cursor = conn.execute("SELECT id FROM online_surveys WHERE id=? AND company_id=?", (survey_id, company_id))
        if not cursor.fetchone():
            raise Exception("Unauthorized")
            
        conn.execute("""
            UPDATE survey_questions 
            SET question_text=?, question_type=?, category=?, is_required=?
            WHERE id=? AND survey_id=? AND company_id=?
        """, (question_text, question_type, category, is_required, question_id, survey_id, company_id))
        
        conn.commit()
        flash('Soru güncellendi.', 'success')
    except Exception as e:
        logging.error(f"Error editing question: {e}")
        flash('Hata oluştu.', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('survey_detail', survey_id=survey_id))

@app.route('/surveys/<int:survey_id>/update_settings', methods=['POST'])
@require_company_context
def update_survey_settings(survey_id):
    if 'user' not in session: return redirect(url_for('login'))
    company_id = g.company_id
    
    # Get form data
    title = request.form.get('survey_title')
    description = request.form.get('survey_description')
    target_groups = request.form.get('target_groups')
    
    demographics = {
        'require_name': 1 if request.form.get('require_name') else 0,
        'require_email': 1 if request.form.get('require_email') else 0,
        'require_company': 1 if request.form.get('require_company') else 0,
        'require_department': 1 if request.form.get('require_department') else 0
    }
    
    conn = get_db()
    try:
        # Verify ownership
        cursor = conn.execute("SELECT id FROM online_surveys WHERE id=? AND company_id=?", (survey_id, company_id))
        if not cursor.fetchone():
            raise Exception("Unauthorized")
            
        import json
        
        # Update everything including title, description, target_groups and demographics
        conn.execute("""
            UPDATE online_surveys 
            SET survey_title=?, survey_description=?, target_groups=?, demographics_config=? 
            WHERE id=? AND company_id=?
        """, (title, description, target_groups, json.dumps(demographics), survey_id, company_id))
        
        conn.commit()
        flash('Ayarlar güncellendi.', 'success')
    except Exception as e:
        logging.error(f"Error updating settings: {e}")
        flash('Hata oluştu.', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('survey_detail', survey_id=survey_id))


@app.route('/surveys/<int:survey_id>/delete', methods=['POST'])
@require_company_context
def delete_survey(survey_id):
    if 'user' not in session: return redirect(url_for('login'))
    company_id = g.company_id
    
    conn = get_db()
    try:
        # Verify ownership
        cursor = conn.execute("SELECT id FROM online_surveys WHERE id=? AND company_id=?", (survey_id, company_id))
        if not cursor.fetchone():
            conn.close()
            flash('Yetkisiz işlem veya anket bulunamadı.', 'error')
            return redirect(url_for('surveys_module'))
            
        # Delete related questions first (foreign key might handle this but be safe)
        conn.execute("DELETE FROM survey_questions WHERE survey_id=? AND company_id=?", (survey_id, company_id))
        # Delete survey
        conn.execute("DELETE FROM online_surveys WHERE id=? AND company_id=?", (survey_id, company_id))
        
        conn.commit()
        flash('Anket başarıyla silindi.', 'success')
    except Exception as e:
        logging.error(f"Error deleting survey: {e}")
        flash('Silme işlemi sırasında hata oluştu.', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('surveys_module'))


@app.route('/taxonomy_edit')
@require_company_context
def taxonomy_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('taxonomy_edit.html', title='Taxonomy Edit')


@app.route('/tcfd_edit')
@require_company_context
def tcfd_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('tcfd_edit.html', title='Tcfd Edit')


@app.route('/tnfd_edit')
@require_company_context
def tnfd_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('tnfd_edit.html', title='Tnfd Edit')


@app.route('/tracking')
@require_company_context
def tracking_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('tracking.html', title='Tracking')




@app.route('/tsrs/add', methods=['POST'])
@require_company_context
def tsrs_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('tsrs')
    if not manager:
        flash('TSRS modülü aktif değil.', 'danger')
        return redirect(url_for('tsrs_module'))
        
    try:
        company_id = g.company_id
        indicator_id = request.form.get('indicator_id')
        reporting_period = request.form.get('reporting_period')
        
        response_data = {
            'response_value': request.form.get('response_value'),
            'numerical_value': request.form.get('numerical_value'),
            'unit': request.form.get('unit'),
            'methodology_used': request.form.get('methodology_used'),
            'data_source': request.form.get('data_source'),
            'reporting_status': request.form.get('reporting_status', 'Draft'),
            'evidence_url': request.form.get('evidence_url'),
            'notes': request.form.get('notes')
        }
        
        # Handle numerical value conversion
        if response_data['numerical_value']:
            try:
                response_data['numerical_value'] = float(response_data['numerical_value'])
            except ValueError:
                response_data['numerical_value'] = None
        
        success = manager.save_tsrs_response(
            company_id=company_id,
            indicator_id=indicator_id,
            reporting_period=reporting_period,
            response_data=response_data
        )
        
        if success:
            flash('TSRS verisi başarıyla eklendi.', 'success')
        else:
            flash('Veri eklenirken bir hata oluştu.', 'danger')
            
    except Exception as e:
        logging.error(f"Error adding TSRS data: {e}")
        flash(f'Hata: {e}', 'danger')
    
    return redirect(url_for('tsrs_module'))


@app.route('/ungc/add', methods=['POST'])
@require_company_context
def ungc_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('ungc')
    if not manager:
        flash('UNGC modülü aktif değil.', 'danger')
        return redirect(url_for('ungc_module'))
        
    try:
        company_id = g.company_id
        principle_id = request.form.get('principle_id')
        compliance_level = request.form.get('compliance_level')
        notes = request.form.get('notes')
        
        success = manager.save_compliance_data(
            company_id=company_id,
            principle_id=principle_id,
            compliance_level=compliance_level,
            notes=notes
        )
        
        if success:
            flash('UNGC uyumluluk verisi başarıyla eklendi.', 'success')
        else:
            flash('Veri eklenirken bir hata oluştu.', 'danger')
            
    except Exception as e:
        logging.error(f"Error adding UNGC data: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('ungc_module'))


@app.route('/ungc')
@require_company_context
def ungc_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('ungc')
    if not manager:
        try:
            from modules.ungc.ungc_manager import UNGCManager
            manager = UNGCManager(DB_PATH)
            MANAGERS['ungc'] = manager
        except ImportError:
            logging.error("Could not import UNGCManager")
            return render_template('ungc.html', title='UNGC (Modül Yüklenemedi)')

    # Ensure tables exist
    if hasattr(manager, 'create_ungc_tables'):
        manager.create_ungc_tables()
    
    company_id = g.company_id
    period = request.args.get('period', str(datetime.now().year))
    
    # Get data
    stats = manager.get_dashboard_stats(company_id)
    status_data = manager.compute_principle_status(company_id, period)
    evidence = manager.get_evidence(company_id)
    thresholds = manager.get_thresholds()
    
    return render_template('ungc.html', 
        title='UNGC',
        stats=stats,
        category_scores=status_data.get('category_scores', {}),
        principles=status_data.get('principles', []),
        evidence=evidence,
        thresholds=thresholds,
        current_period=period,
        overall_score=status_data.get('overall_score', 0)
    )

@app.route('/ungc/upload_evidence', methods=['POST'])
@require_company_context
def ungc_upload_evidence():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('ungc')
    if not manager:
        flash('UNGC modülü aktif değil.', 'danger')
        return redirect(url_for('ungc_module'))
        
    try:
        company_id = g.company_id
        principle_id = request.form.get('principle_id')
        evidence_type = request.form.get('evidence_type', 'file')
        description = request.form.get('description')
        
        file = request.files.get('evidence_file')
        file_path = None
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            # Create uploads directory if not exists
            upload_dir = os.path.join(BASE_DIR, 'static', 'uploads', 'ungc')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            timestamp = int(time.time())
            saved_filename = f"{company_id}_{timestamp}_{filename}"
            full_path = os.path.join(upload_dir, saved_filename)
            file.save(full_path)
            
            # Store relative path
            file_path = f"ungc/{saved_filename}"
            
        success = manager.add_evidence(
            company_id=company_id,
            principle_id=principle_id,
            evidence_type=evidence_type,
            description=description,
            file_path=file_path
        )
        
        if success:
            flash('Kanıt belgesi başarıyla yüklendi.', 'success')
        else:
            flash('Kanıt eklenirken veritabanı hatası oluştu.', 'danger')
            
    except Exception as e:
        logging.error(f"Error uploading UNGC evidence: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('ungc_module'))

@app.route('/ungc/update_thresholds', methods=['POST'])
@require_company_context
def ungc_update_thresholds():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('ungc')
    if not manager:
        flash('UNGC modülü aktif değil.', 'danger')
        return redirect(url_for('ungc_module'))
        
    try:
        full = float(request.form.get('full_threshold', 0.6))
        partial = float(request.form.get('partial_threshold', 0.2))
        
        success = manager.update_thresholds(full, partial)
        
        if success:
            flash('Eşik değerleri güncellendi.', 'success')
        else:
            flash('Ayarlar kaydedilemedi.', 'danger')
            
    except Exception as e:
        logging.error(f"Error updating UNGC thresholds: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('ungc_module'))


@app.route('/user_edit')
@require_company_context
def user_edit_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('user_edit.html', title='User Edit')


@app.route('/user_experience')
@require_company_context
def user_experience_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('user_experience.html', title='User Experience')


@app.route('/validation')
@require_company_context
def validation_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('validation.html', title='Validation')


@app.route('/verify_code')
@require_company_context
def verify_code_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('verify_code.html', title='Verify Code')


@app.route('/visualization')
@require_company_context
def visualization_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('visualization.html', title='Visualization')


@app.route('/waste_management')
@require_company_context
def waste_management_module():
    if 'user' not in session: return redirect(url_for('login'))
    return redirect(url_for('waste_module'))


@app.route('/water_management')
@require_company_context
def water_management_module():
    if 'user' not in session: return redirect(url_for('login'))
    return redirect(url_for('water_module'))


@app.route('/workflow')
@require_company_context
def workflow_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('workflow.html', title='Workflow')


@app.route('/prioritization/add', methods=['POST'])
@require_company_context
def prioritization_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('prioritization')
    if not manager:
        flash('Önceliklendirme modülü aktif değil.', 'danger')
        return redirect(url_for('prioritization'))
        
    try:
        company_id = g.company_id
        topic_name = request.form.get('topic_name')
        category = request.form.get('category')
        stakeholder_impact = float(request.form.get('stakeholder_impact', 0))
        business_impact = float(request.form.get('business_impact', 0))
        description = request.form.get('description')
        
        # Calculate priority score
        priority_score = (stakeholder_impact * business_impact) / 25.0 * 5.0 # Normalizing if inputs are 1-5? 
        # Actually Manager just takes float. Let's assume inputs are 1-5.
        # Let's just average them for now or use product.
        # Matrix usually uses X and Y axes.
        # Let's keep it simple: Average.
        priority_score = (stakeholder_impact + business_impact) / 2.0
        
        manager.save_materiality_topic(
            company_id=company_id,
            topic_name=topic_name,
            category=category,
            stakeholder_impact=stakeholder_impact,
            business_impact=business_impact,
            priority_score=priority_score,
            description=description
        )
        
        flash('Materyal konu başarıyla eklendi.', 'success')
    except Exception as e:
        logging.error(f"Error adding prioritization topic: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('prioritization'))


# --- SPA API Routes (Added for Option 1: UI Modernization) ---

@app.route('/api/v1/login', methods=['POST'])
@require_company_context
def api_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing credentials'}), 400
            
        user = None
        if user_manager:
            user = user_manager.authenticate(username, password)
            
        if user:
            # Session handling for hybrid approach
            session['user'] = user.username
            session['role'] = user.role
            session['user_id'] = user.id
            session['company_id'] = user.company_id if hasattr(user, 'company_id') else 1
            
            return jsonify({
                'success': True,
                'token': 'session_based', 
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'company_id': getattr(user, 'company_id', 1)
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logging.error(f"API Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/dashboard-stats', methods=['GET'])
@require_company_context
def api_dashboard_stats():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        company_id = g.company_id
        year = datetime.now().year
        stats = {
            'modules': [],
            'alerts': 0,
            'next_deadline': f'{year}-12-31'
        }

        # Carbon Module
        carbon_score = 0
        carbon_status = 'Pending'
        if MANAGERS.get('carbon'):
            try:
                total_emissions = MANAGERS['carbon'].get_total_carbon_footprint(company_id, year)
                if total_emissions > 0:
                    carbon_score = 100 # Simplified logic
                    carbon_status = 'Active'
                else:
                    records = MANAGERS['carbon'].get_carbon_records(company_id, year)
                    if records:
                        carbon_score = 50
                        carbon_status = 'Active'
            except Exception as e:
                logging.error(f"API Carbon stats error: {e}")
        
        stats['modules'].append({
            'name': 'Karbon (Carbon)',
            'status': carbon_status,
            'score': carbon_score
        })

        # Water Module
        water_score = 0
        water_status = 'Pending'
        if MANAGERS.get('water'):
            try:
                water_data = MANAGERS['water'].calculate_water_footprint(company_id, str(year))
                if water_data and water_data.get('total_water_footprint', 0) > 0:
                    water_score = 100
                    water_status = 'Active'
            except Exception as e:
                logging.error(f"API Water stats error: {e}")

        stats['modules'].append({
            'name': 'Su (Water)',
            'status': water_status,
            'score': water_score
        })

        # Social Module
        social_score = 0
        social_status = 'Pending'
        if MANAGERS.get('social'):
            try:
                social_data = MANAGERS['social'].get_dashboard_stats(company_id)
                if social_data and social_data.get('employees', 0) > 0:
                    social_score = 100
                    social_status = 'Active'
            except Exception as e:
                logging.error(f"API Social stats error: {e}")

        stats['modules'].append({
            'name': 'Sosyal (Social)',
            'status': social_status,
            'score': social_score
        })

        return jsonify(stats)
    except Exception as e:
        logging.error(f"API Dashboard error: {e}")
        return jsonify({'error': str(e)}), 500

# ==========================================
# DYNAMIC MODULE INTEGRATION (AUTO-GENERATED)
# ==========================================
try:
    from backend.core.universal_manager import UniversalManagerWrapper
except ImportError:
    try:
        from core.universal_manager import UniversalManagerWrapper
    except ImportError:
        logging.error("Could not import UniversalManagerWrapper")
        UniversalManagerWrapper = None

import importlib.util
import inspect

def _auto_load_managers():
    """
    Dynamically finds and loads Manager classes from backend/modules
    and adds them to the global MANAGERS dictionary.
    """
    global MANAGERS
    modules_dir = os.path.join(BACKEND_DIR, 'modules')
    
    # Map of specific module names to Manager classes (overrides)
    # or heuristics
    
    for root, dirs, files in os.walk(modules_dir):
        for file in files:
            if (file.endswith('_manager.py') or file.endswith('Manager.py') or 'manager' in file.lower()) and file.endswith('.py'):
                if file.startswith('__'): continue
                
                full_path = os.path.join(root, file)
                module_name_guess = os.path.splitext(file)[0]
                
                # Try to import
                try:
                    spec = importlib.util.spec_from_file_location(module_name_guess, full_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    # Find Manager class
                    for name, obj in inspect.getmembers(mod):
                        if inspect.isclass(obj) and 'Manager' in name and name != 'Manager':
                            # Found a manager class
                            # Determine key for MANAGERS dict
                            # e.g. WasteManager -> waste
                            key = name.lower().replace('manager', '').replace('enhanced', '')
                            if key not in MANAGERS or MANAGERS[key] is None:
                                try:
                                    instance = obj(DB_PATH)
                                    MANAGERS[key] = instance
                                    logging.info(f"Auto-loaded {name} as {key}")
                                except Exception as e:
                                    # Maybe it doesn't take DB_PATH or other init args
                                    try:
                                        instance = obj()
                                        MANAGERS[key] = instance
                                        logging.info(f"Auto-loaded {name} as {key} (no args)")
                                    except Exception as e2:
                                        pass
                except Exception as e:
                    logging.warning(f"Failed to auto-load {file}: {e}")

# Run auto-loader
_auto_load_managers()

# List of templates that were "under construction" and now need routes
UNDER_CONSTRUCTION_MODULES = [
    'advanced_calculation', 'advanced_inventory', 'advanced_reporting', 'ai', 'ai_reports', 
    'analysis', 'analytics', 'auditor', 'automated_reporting', 'automation', 'auto_tasks', 
    'company', 'company_info', 'database', 'data_collection', 'data_import', 'data_inventory', 
    'data_provenance', 'digital_security', 'document_processing', 'emergency', 'emission_reduction', 
    'environmental', 'erp_integration', 'eu_taxonomy', 'file_manager', 'forms', 'framework_mapping', 
    'ifrs', 'innovation', 'integration', 'mapping', 'policy_library', 'prioritization', 
    'product_technology', 'quality', 'reporting', 'scenario_analysis', 'scope3', 'security', 
    'skdm', 'stakeholder', 'standards', 'strategic', 'surveys', 'tracking', 'tsrs', 'ungc', 
    'user_experience', 'validation', 'visualization', 'waste_management', 'water_management', 'workflow'
]

def register_dynamic_routes():
    """
    Registers routes for the modules that were previously under construction.
    Uses UniversalManagerWrapper to provide data.
    """
    
    def create_view_func(template_name, route_key):
        def view_func():
            if 'user' not in session:
                return redirect(url_for('login'))
            
            # Try to find a manager
            # 1. Exact match
            manager = MANAGERS.get(route_key)
            
            # 2. Fuzzy match
            if not manager:
                for k, v in MANAGERS.items():
                    if k in route_key or route_key in k:
                        manager = v
                        break
            
            data = {}
            if manager and UniversalManagerWrapper:
                wrapper = UniversalManagerWrapper(manager)
                data = wrapper.get_dashboard_data()
            
            # Add some context even if no manager found
            if not data:
                data = {'stats': {}, 'records': []}
                
            return render_template(f'{template_name}.html', **data)
        return view_func

    for mod in UNDER_CONSTRUCTION_MODULES:
        route_path = f'/{mod}'
        endpoint = mod
        
        # Check if route already exists
        exists = False
        for rule in app.url_map.iter_rules():
            if rule.rule == route_path:
                exists = True
                break
        
        if not exists:
            # Map module name to manager key
            # e.g. waste_management -> waste
            manager_key = mod.replace('_management', '').replace('_manager', '')
            
            app.add_url_rule(
                route_path, 
                endpoint=endpoint, 
                view_func=create_view_func(mod, manager_key)
            )
            logging.info(f"Registered dynamic route: {route_path}")

register_dynamic_routes()

def ensure_survey_tables():
    """Ensure survey tables have all required columns (migration)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check and add columns if missing in survey_questions
        try:
            cursor.execute("SELECT category FROM survey_questions LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding category column to survey_questions")
            cursor.execute("ALTER TABLE survey_questions ADD COLUMN category TEXT DEFAULT 'General'")
            
        try:
            cursor.execute("SELECT question_type FROM survey_questions LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding question_type column to survey_questions")
            cursor.execute("ALTER TABLE survey_questions ADD COLUMN question_type TEXT DEFAULT 'scale_1_5'")
            
        try:
            cursor.execute("SELECT is_required FROM survey_questions LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding is_required column to survey_questions")
            cursor.execute("ALTER TABLE survey_questions ADD COLUMN is_required BOOLEAN DEFAULT 1")
            
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error ensuring survey tables: {e}")

# Ensure tables on module load (works for Gunicorn too)
try:
    ensure_company_info_table()
    ensure_survey_tables()
except Exception as e:
    logging.error(f"Error running initial migrations: {e}")

# ==========================================
# Main
# ==========================================

# --- LCA MODULE ROUTES ---
@app.route('/lca')
@require_company_context
def lca_module():
    if 'user' not in session: return redirect(url_for('login'))
    manager = LCAManager(DB_PATH)
    products = manager.get_products(g.company_id)
    return render_template('lca.html', products=products)

@app.route('/lca/add_product', methods=['POST'])
@require_company_context
def lca_add_product():
    if 'user' not in session: return redirect(url_for('login'))
    name = request.form.get('name')
    description = request.form.get('description')
    unit = request.form.get('unit')
    
    manager = LCAManager(DB_PATH)
    manager.add_product(g.company_id, name, description, unit)
    flash('Ürün başarıyla eklendi.', 'success')
    return redirect(url_for('lca_module'))

@app.route('/lca/product/<int:product_id>')
@require_company_context
def lca_product_detail(product_id):
    if 'user' not in session: return redirect(url_for('login'))
    manager = LCAManager(DB_PATH)
    assessments = manager.get_assessments(product_id, g.company_id)
    conn = manager.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM lca_products WHERE id=? AND company_id=?', (product_id, g.company_id))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        flash('Ürün bulunamadı.', 'error')
        return redirect(url_for('lca_module'))
        
    return render_template('lca_product.html', product=dict(product), assessments=assessments)

@app.route('/lca/product/<int:product_id>/add_assessment', methods=['POST'])
@require_company_context
def lca_add_assessment(product_id):
    if 'user' not in session: return redirect(url_for('login'))
    name = request.form.get('name')
    date = request.form.get('date')
    
    manager = LCAManager(DB_PATH)
    manager.add_assessment(product_id, g.company_id, name, date)
    flash('Analiz oluşturuldu.', 'success')
    return redirect(url_for('lca_product_detail', product_id=product_id))

@app.route('/lca/assessment/<int:assessment_id>')
@require_company_context
def lca_assessment_detail(assessment_id):
    if 'user' not in session: return redirect(url_for('login'))
    manager = LCAManager(DB_PATH)
    assessment = manager.get_assessment_details(assessment_id, g.company_id)
    if not assessment:
        flash('Analiz bulunamadı.', 'error')
        return redirect(url_for('lca_module'))
        
    entries = manager.get_entries(assessment_id, g.company_id)
    results = manager.calculate_results(assessment_id, g.company_id)
    
    return render_template('lca_assessment.html', assessment=assessment, entries=entries, results=results)

@app.route('/lca/assessment/<int:assessment_id>/add_entry', methods=['POST'])
@require_company_context
def lca_add_entry(assessment_id):
    if 'user' not in session: return redirect(url_for('login'))
    manager = LCAManager(DB_PATH)
    
    data = {
        'stage': request.form.get('stage'),
        'item_name': request.form.get('item_name'),
        'quantity': float(request.form.get('quantity') or 0),
        'unit': request.form.get('unit'),
        'co2e_factor': float(request.form.get('co2e_factor') or 0),
        'energy_consumption': float(request.form.get('energy_consumption') or 0),
        'water_consumption': float(request.form.get('water_consumption') or 0),
        'notes': request.form.get('notes')
    }
    
    manager.add_entry(assessment_id, g.company_id, data)
    flash('Veri eklendi.', 'success')
    return redirect(url_for('lca_assessment_detail', assessment_id=assessment_id))

@app.route('/lca/assessment/<int:assessment_id>/delete_entry/<int:entry_id>', methods=['POST'])
@require_company_context
def lca_delete_entry(assessment_id, entry_id):
    if 'user' not in session: return redirect(url_for('login'))
    manager = LCAManager(DB_PATH)
    manager.delete_entry(entry_id, g.company_id)
    flash('Veri silindi.', 'success')
    return redirect(url_for('lca_assessment_detail', assessment_id=assessment_id))

# --- Supply Chain Routes ---

@app.route('/supply_chain')
@require_company_context
def supply_chain_module():
    if 'user' not in session: return redirect(url_for('login'))
    manager = SupplyChainManager(DB_PATH)
    suppliers = manager.get_suppliers(g.company_id)
    return render_template('supply_chain.html', suppliers=suppliers)

@app.route('/supply_chain/add_supplier', methods=['POST'])
@require_company_context
def supply_chain_add_supplier():
    if 'user' not in session: return redirect(url_for('login'))
    manager = SupplyChainManager(DB_PATH)
    
    manager.add_supplier(
        g.company_id,
        request.form.get('name'),
        request.form.get('sector'),
        request.form.get('region'),
        request.form.get('contact_info')
    )
    flash('Tedarikçi başarıyla eklendi.', 'success')
    return redirect(url_for('supply_chain_module'))

@app.route('/supply_chain/profile/<int:supplier_id>')
@require_company_context
def supply_chain_profile(supplier_id):
    if 'user' not in session: return redirect(url_for('login'))
    manager = SupplyChainManager(DB_PATH)
    
    supplier = manager.get_supplier(supplier_id, g.company_id)
    if not supplier:
        flash('Tedarikçi bulunamadı.', 'error')
        return redirect(url_for('supply_chain_module'))
        
    assessments = manager.get_assessments(supplier_id, g.company_id)
    return render_template('supply_chain_profile.html', supplier=supplier, assessments=assessments, today_date=datetime.now().strftime('%Y-%m-%d'))

@app.route('/supply_chain/profile/<int:supplier_id>/add_assessment', methods=['POST'])
@require_company_context
def supply_chain_add_assessment(supplier_id):
    if 'user' not in session: return redirect(url_for('login'))
    manager = SupplyChainManager(DB_PATH)
    
    details = {
        'env_score': int(request.form.get('env_score') or 0),
        'social_score': int(request.form.get('social_score') or 0),
        'gov_score': int(request.form.get('gov_score') or 0),
        'notes': request.form.get('notes')
    }
    
    # Calculate simple average score
    score = (details['env_score'] + details['social_score'] + details['gov_score']) / 3
    
    manager.add_assessment(
        supplier_id,
        g.company_id,
        request.form.get('assessment_date'),
        score,
        request.form.get('risk_level'),
        details
    )
    flash('Değerlendirme eklendi.', 'success')
    return redirect(url_for('supply_chain_profile', supplier_id=supplier_id))

# --- Real-Time Monitoring Routes ---

@app.route('/realtime')
@require_company_context
def realtime_module():
    if 'user' not in session: return redirect(url_for('login'))
    manager = RealTimeMonitoringManager(DB_PATH)
    devices = manager.get_devices(g.company_id)
    alerts = manager.get_alerts(g.company_id)
    return render_template('realtime.html', devices=devices, alerts=alerts)

@app.route('/realtime/add_device', methods=['POST'])
@require_company_context
def realtime_add_device():
    if 'user' not in session: return redirect(url_for('login'))
    manager = RealTimeMonitoringManager(DB_PATH)
    
    threshold = request.form.get('threshold_value')
    if threshold:
        threshold = float(threshold)
    else:
        threshold = None

    manager.add_device(
        g.company_id,
        request.form.get('name'),
        request.form.get('device_type'),
        request.form.get('unit'),
        threshold
    )
    flash('Cihaz eklendi.', 'success')
    return redirect(url_for('realtime_module'))

@app.route('/realtime/device/<int:device_id>')
@require_company_context
def realtime_device_detail(device_id):
    if 'user' not in session: return redirect(url_for('login'))
    manager = RealTimeMonitoringManager(DB_PATH)
    
    device = manager.get_device(device_id, g.company_id)
    if not device:
        flash('Cihaz bulunamadı.', 'error')
        return redirect(url_for('realtime_module'))
        
    readings = manager.get_readings(device_id)
    return render_template('realtime_device.html', device=device, readings=readings)

@app.route('/realtime/device/<int:device_id>/add_reading', methods=['POST'])
@require_company_context
def realtime_add_reading(device_id):
    if 'user' not in session: return redirect(url_for('login'))
    manager = RealTimeMonitoringManager(DB_PATH)
    
    value = float(request.form.get('value'))
    manager.add_reading(device_id, value)
    
    flash('Okuma eklendi.', 'success')
    return redirect(url_for('realtime_device_detail', device_id=device_id))

# IoT Ingestion API (Simulated)
@app.route('/api/iot/ingest', methods=['POST'])
def api_iot_ingest():
    data = request.json
    if not data or 'device_id' not in data or 'value' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    manager = RealTimeMonitoringManager(DB_PATH)
    # Note: In a real scenario, we would validate the device token/secret here
    manager.add_reading(data['device_id'], float(data['value']))
    
    return jsonify({'status': 'success', 'message': 'Data ingested'}), 201

