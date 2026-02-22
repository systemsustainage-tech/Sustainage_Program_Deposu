import os
import sys
import logging
import json
import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from typing import Optional, Dict
from types import SimpleNamespace
from flask import Flask, render_template, redirect, url_for, session, request, flash, send_file, g, jsonify, has_request_context, abort, make_response
import time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
import psutil
import threading
from flask_wtf.csrf import CSRFProtect
from backend.config.database import DB_PATH

try:
    from security.alert_system import report_violation
except ImportError:
    # Fallback if security module is not found
    def report_violation(type, ip, details=None):
        logging.error(f"Security Alert (Fallback): {type} from {ip} - {details}")

# --- SYSTEM MONITOR FOR ALERTING ---
def run_system_monitor(app):
    """Background thread to monitor system resources and send alerts."""
    logging.info("Starting System Monitor Thread...")
    while True:
        try:
            # Check CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            mem_percent = mem.percent
            
            # Log metrics (optional, for debug)
            # logging.debug(f"System Check: CPU={cpu_percent}%, MEM={mem_percent}%")
            
            # Thresholds
            if cpu_percent > 90:
                report_violation('SYSTEM_OVERLOAD', 'localhost', 
                               details={'metric': 'CPU', 'value': f"{cpu_percent}%"})
                logging.warning(f"HIGH CPU USAGE: {cpu_percent}% - Alert sent.")
                
            if mem_percent > 90:
                report_violation('SYSTEM_OVERLOAD', 'localhost', 
                               details={'metric': 'MEMORY', 'value': f"{mem_percent}%"})
                logging.warning(f"HIGH MEMORY USAGE: {mem_percent}% - Alert sent.")
                
        except Exception as e:
            logging.error(f"SystemMonitor Error: {e}")
            
        # Check every 60 seconds
        time.sleep(60)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)

from modules.sdg.sdg_manager import SDGManager
from core.language_manager import LanguageManager
from core.database import TenantAwareDB
from backend.core.database_manager import DatabaseManager
from backend.yonetim.license_manager import LicenseManager

# Initialize Language Manager
language_manager = LanguageManager()

# Initialize License Manager
license_manager = LicenseManager(DB_PATH)

# DB_PATH is now imported from backend.config.database
# DB_PATH = os.path.join(BACKEND_DIR, 'data', 'sdg_desktop.sqlite')

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
]


def ensure_company_info_table() -> None:
    db = DatabaseManager(DB_PATH)
    with db.get_connection() as conn:
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


ensure_company_info_table()

# Optional integrations
USER_MANAGER_AVAILABLE = False
IP_MANAGER_AVAILABLE = False
MONITORING_AVAILABLE = False
LICENSE_MANAGER_AVAILABLE = False

try:
    from yonetim.kullanici_yonetimi.models.user_manager import UserManager
    USER_MANAGER_AVAILABLE = True
except Exception as e:
    logging.error(f"UserManager import error: {e}")
    USER_MANAGER_AVAILABLE = False

try:
    from modules.super_admin.components.rate_limiter import RateLimiter
    rate_limiter = RateLimiter(DB_PATH)
except Exception as e:
    logging.error(f"RateLimiter import error: {e}")
    class _DummyLimiter:
        def check_rate_limit(self, *args, **kwargs):
            return {'allowed': True, 'current_count': 0, 'limit': 999, 'reset_in': 0, 'blocked': False}
    rate_limiter = _DummyLimiter()

try:
    from modules.super_admin.components.license_generator import LicenseGenerator
    LICENSE_MANAGER_AVAILABLE = True
except Exception as e:
    logging.error(f"LicenseGenerator import error: {e}")
    LICENSE_MANAGER_AVAILABLE = False

app = Flask(__name__)
# Fix for login loop: Use a stable secret key if environment variable is not set
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sustainage_secret_key_fixed_2024_xyz_987')

# CSRF Protection
csrf = CSRFProtect(app)

@app.context_processor
def inject_csp_nonce():
    if not hasattr(g, 'csp_nonce'):
        g.csp_nonce = secrets.token_hex(16)
    return dict(csp_nonce=lambda: g.csp_nonce)

# Prometheus Metrics
metrics = PrometheusMetrics(app)
# Add default static info
metrics.info('app_info', 'Application info', version='1.0.3')

# Start System Monitor Thread
if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    monitor_thread = threading.Thread(target=run_system_monitor, args=(app,), daemon=True)
    monitor_thread.start()

# Rate Limiter Initialization
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://"
)

def limiter_exempt(f):
    func = getattr(limiter, 'exempt', None)
    if callable(func):
        return func(f)
    return f

@app.errorhandler(429)
def rate_limit_error(e):
    client_ip = get_remote_address()
    # Log the violation using the alert system
    try:
        report_violation('RATE_LIMIT', client_ip, details={'limit': str(e.description)})
    except Exception as log_err:
        logging.error(f"Error reporting rate limit: {log_err}")
        
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({'error': 'Rate limit exceeded', 'message': str(e.description)}), 429
    return "Too Many Requests. Please try again later.", 429

# Translation Setup (Replaced with LanguageManager)
def gettext(key, default=None):
    lang = 'tr'
    if has_request_context():
        lang = session.get('lang', 'tr')
    
    # language_manager is initialized at the top
    return language_manager.get_text(key, lang=lang, default=default)

app.jinja_env.globals.update(_=gettext, lang=gettext)
_ = gettext

@app.route('/set_language/<lang>', endpoint='set_language')
@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in language_manager.translations:
        session['lang'] = lang
        resp = make_response(redirect(request.referrer or url_for('dashboard')))
        resp.set_cookie('lang', lang, max_age=60 * 60 * 24 * 30)
        return resp
    return redirect(request.referrer or url_for('dashboard'))

@app.before_request
def load_language_preference():
    if 'lang' not in session:
        session['lang'] = request.cookies.get('lang', 'tr')

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
from mapping.sdg_gri_mapping import SDGGRIMapping
from backend.modules.stakeholder.stakeholder_engagement import StakeholderEngagement
from modules.reporting.report_generator import ReportGenerator

# Manager Initialization (Lazy Loading or Global)
MANAGERS = {
    'sdg': None,  # Will be initialized if module exists
    'gri': None,
    'carbon': None, # Placeholder for carbon
    'energy': None,
    'water': None,
    'waste': None,
    'social': None,
    'governance': None
}
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
        from modules.economic.economic_manager import EconomicManager
        MANAGERS['economic'] = EconomicManager(DB_PATH)
    except Exception as e:
        logging.error(f"EconomicManager init: {e}")
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
        from modules.file_manager.advanced_file_manager import AdvancedFileManager
        MANAGERS['file_manager'] = AdvancedFileManager(DB_PATH)
    except Exception as e:
        logging.error(f"AdvancedFileManager init: {e}")
    try:
        from backend.modules.auto_tasks.auto_task_manager import AutoTaskManager
        MANAGERS['auto_tasks'] = AutoTaskManager(DB_PATH)
    except Exception as e:
        logging.error(f"AutoTaskManager init: {e}")
    try:
        from backend.modules.visualization.visualization_manager import VisualizationManager
        MANAGERS['visualization'] = VisualizationManager(DB_PATH)
    except Exception as e:
        logging.error(f"VisualizationManager init: {e}")
    try:
        from backend.modules.automated_reporting.auto_report import AutoReportManager
        MANAGERS['automated_reporting'] = AutoReportManager(DB_PATH)
    except Exception as e:
        logging.error(f"AutoReportManager init: {e}")
    try:
        from backend.modules.analytics.trend_analyzer import TrendAnalyzer
        MANAGERS['analytics'] = TrendAnalyzer(DB_PATH)
    except Exception as e:
        logging.error(f"TrendAnalyzer init: {e}")
    try:
        from backend.modules.notification.notification_manager import NotificationManager
        MANAGERS['notification'] = NotificationManager(DB_PATH)
    except Exception as e:
        logging.error(f"NotificationManager init: {e}")
    try:
        from backend.modules.data_inventory.advanced_dashboard import AdvancedDashboard
        MANAGERS['data_inventory'] = AdvancedDashboard(DB_PATH)
    except Exception as e:
        logging.error(f"AdvancedDashboard init: {e}")
_init_managers()

# Register Blueprints
try:
    from backend.api.file_api import file_bp
    app.register_blueprint(file_bp)
    
    from backend.api.notification_api import notification_bp
    app.register_blueprint(notification_bp)
    
    from backend.api.audit_api import audit_bp
    app.register_blueprint(audit_bp)
    
    app.config['MANAGERS'] = MANAGERS
except Exception as e:
    logging.error(f"Blueprint registration error: {e}")

def _get_system_setting(key, default=None):
    if not has_request_context():
        return default
    
    # Use g.company_id if available, otherwise default to None
    company_id = getattr(g, 'company_id', None)
    
    try:
        conn = get_db()
        if company_id:
            # Try company specific setting
            cur = conn.execute("SELECT value FROM system_settings WHERE key=? AND company_id=?", (key, company_id))
            row = cur.fetchone()
            if row and row[0] is not None:
                conn.close()
                return row[0]
            
        conn.close()
        return default
    except Exception as e:
        logging.error(f"Error getting system setting {key}: {e}")
        return default

def _get_system_setting_int(key: str, default: int) -> int:
    val = _get_system_setting(key)
    if val is None or val == '':
        return default
    try:
        return int(val)
    except ValueError:
        return default

def _get_login_lockout_params():
    max_attempts = _get_system_setting_int('sec_max_login_attempts', 5)
    lockout_time = _get_system_setting_int('sec_lockout_seconds', 300) # 5 minutes
    return max_attempts, lockout_time

def _get_session_timeout_seconds():
    # Default 30 minutes
    minutes = _get_system_setting_int('sec_session_timeout_minutes', 30)
    return minutes * 60

@app.before_request
def enforce_session_timeout():
    exempt_endpoints = {
        'login',
        'logout',
        'health',
        'forgot_password',
        'static',
        'verify_reset_code', 
        'reset_password_web'
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

@app.before_request
def license_check():
    if not request.path.startswith('/api/'):
        return
    if request.endpoint in ['api_login', 'api_register', 'api_logout', 'static']:
        return

    def check_constraints(payload):
        allowed_domains = payload.get('allowed_domains')
        if allowed_domains and isinstance(allowed_domains, list) and len(allowed_domains) > 0:
            request_domain = request.host.split(':')[0].lower()
            normalized_allowed = [d.lower() for d in allowed_domains]
            if request_domain not in normalized_allowed:
                return False, f"Domain '{request_domain}' not authorized by license."

        allowed_ips = payload.get('allowed_ips')
        if allowed_ips and isinstance(allowed_ips, list) and len(allowed_ips) > 0:
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                client_ip = forwarded_for.split(',')[0].strip()
            else:
                try:
                    client_ip = get_remote_address()
                except Exception:
                    client_ip = request.remote_addr or 'unknown'
            if client_ip not in allowed_ips:
                return False, f"IP '{client_ip}' not authorized by license."
        return True, None

    api_key = request.headers.get('X-License-Key')
    if api_key:
        is_valid, msg, payload = license_manager.verify_license_key(api_key)
        if not is_valid:
            return jsonify({'error': f'License Error: {msg}'}), 403
        allowed, fail_msg = check_constraints(payload)
        if not allowed:
            return jsonify({'error': f'License Access Denied: {fail_msg}'}), 403
        g.license = payload
        return

    if 'company_id' in session:
        active_key = license_manager.get_active_license(session['company_id'])
        if not active_key:
            return jsonify({'error': 'No active license found for this company.'}), 403
        is_valid, msg, payload = license_manager.verify_license_key(active_key)
        if not is_valid:
            return jsonify({'error': f'License Expired/Invalid: {msg}'}), 403
        allowed, fail_msg = check_constraints(payload)
        if not allowed:
            return jsonify({'error': f'License Access Denied: {fail_msg}'}), 403
        g.license = payload
        return

    return jsonify({'error': 'License verification failed. Please provide X-License-Key or login.'}), 403

def get_db():
    return TenantAwareDB(DB_PATH)

user_manager: Optional[UserManager] = None
if USER_MANAGER_AVAILABLE:
    try:
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
        if role not in ['super_admin', 'test admin']:
            flash('Bu sayfaya sadece Süper Admin erişebilir.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- SaaS / Multi-Tenant Middleware & Decorators ---

def require_company_context(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        # Enforce Company Context
        company_id = session.get('company_id')
        
        # DEBUG: Check if company_id is a dict (SaaS isolation fix)
        if isinstance(company_id, dict):
            logging.warning(f"DEBUG: company_id in session is a dict: {company_id}. Extracting ID.")
            company_id = company_id.get('id') or company_id.get('company_id')
            session['company_id'] = company_id # Update session
            
        if not company_id:
            # STRICT MODE: No fallback to 1.
            # If no company context, force logout or error.
            session.clear()
            flash('Oturum süreniz doldu veya geçerli bir şirket bulunamadı.', 'warning')
            return redirect(url_for('login'))
            
        g.company_id = int(company_id) # Ensure int
        
        # --- LICENSE RESTRICTION CHECK ---
        try:
            # Get active license for this company
            license_key = license_manager.get_active_license(g.company_id)
            if license_key:
                # Verify and get payload (IP/Domain rules)
                verify_result = license_manager.verify_license_key(license_key)
                if not verify_result or len(verify_result) != 3:
                     logging.error(f"Invalid verify_license_key return: {verify_result}")
                     is_valid, msg, payload = False, "Internal Error", {}
                else:
                     is_valid, msg, payload = verify_result
                     
                if is_valid:
                    allowed_ips = payload.get('allowed_ips')
                    allowed_domains = payload.get('allowed_domains')
                    
                    # IP Check
                    if allowed_ips:
                        # Normalize list if string (comma separated)
                        if isinstance(allowed_ips, str): 
                            allowed_ips = [ip.strip() for ip in allowed_ips.split(',')]
                        
                        client_ip = get_remote_address()
                        # Handle potential localhost mapping
                        if client_ip == '127.0.0.1' and 'localhost' in allowed_ips:
                            pass # Allowed
                        elif client_ip not in allowed_ips:
                            logging.warning(f"License Violation: IP {client_ip} not in {allowed_ips}")
                            report_violation('LICENSE_VIOLATION', client_ip, details={'reason': 'IP_MISMATCH', 'expected': allowed_ips})
                            if request.path.startswith('/api/'):
                                return jsonify({'error': f"IP '{client_ip}' not authorized by license"}), 403
                            abort(403, description=f"IP Adresi ({client_ip}) lisans kapsamında yetkilendirilmemiş.")
                            
                    # Domain Check (if referrer/host is available)
                    if allowed_domains:
                        if isinstance(allowed_domains, str):
                            allowed_domains = [d.strip() for d in allowed_domains.split(',')]
                        
                        host = request.host.split(':')[0]
                        if host not in allowed_domains:
                            logging.warning(f"License Violation: Domain {host} not in {allowed_domains}")
                            report_violation('LICENSE_VIOLATION', get_remote_address(), details={'reason': 'DOMAIN_MISMATCH', 'expected': allowed_domains})
                            if request.path.startswith('/api/'):
                                return jsonify({'error': f"Domain '{host}' not authorized by license"}), 403
                            abort(403, description=f"Domain ({host}) lisans kapsamında yetkilendirilmemiş.")
                
        except Exception as e:
            logging.error(f"License restriction check error: {e}")
            # Do not block on error, just log
        # ---------------------------------
        
        return f(*args, **kwargs)
    return decorated_function

# --- SaaS Demo API Endpoint ---
@app.route('/api/saas/demo')
@require_company_context
def saas_demo_api():
    """
    Demonstrates Multi-Tenant Data Isolation.
    Returns data ONLY for the currently logged-in company.
    """
    stats = {
        'company_id': g.company_id,
        'tenant_status': 'active',
        'server_timestamp': datetime.now().isoformat(),
        'modules_active': []
    }
    
    # Example: Fetch real data for this tenant
    try:
        conn = get_db()
        # Get Company Name
        company = conn.execute("SELECT name FROM companies WHERE id=?", (g.company_id,)).fetchone()
        stats['company_name'] = company['name'] if company else 'Unknown'
        
        # Get Employee Count (Social Module)
        row = conn.execute("SELECT SUM(employee_count) FROM hr_employees WHERE company_id=?", (g.company_id,)).fetchone()
        stats['employee_count'] = row[0] if row and row[0] else 0
        
        conn.close()
    except Exception as e:
        stats['error'] = str(e)
        
    return jsonify(stats)

@app.route('/api/v1/translations')
def api_translations():
    current_lang = session.get('lang')
    if not current_lang:
        current_lang = request.cookies.get('lang', 'tr')
    translations = language_manager.get_all_translations(current_lang)
    version = language_manager.get_version(current_lang)
    response = jsonify({'lang': current_lang, 'translations': translations})
    response.set_etag(version)
    response.headers['Cache-Control'] = 'no-cache, must-revalidate'
    return response.make_conditional(request)

@app.route('/api/dashboard/stats')
@require_company_context
def dashboard_stats_api():
    """
    SaaS API for Dashboard Statistics.
    Strictly isolated by company_id.
    """
    stats = {}
    conn = None
    try:
        conn = get_db()
        
        # Helper to safely get sum
        def get_sum(table, column):
            try:
                # check if table exists first? No, just try-except
                row = conn.execute(f"SELECT SUM({column}) FROM {table} WHERE company_id = ?", (g.company_id,)).fetchone()
                return row[0] if row and row[0] else 0
            except Exception as e:
                logging.warning(f"Stats API: Error fetching {table}: {e}")
                return 0

        stats['energy_consumption'] = get_sum('energy_consumption', 'consumption_amount')
        stats['water_consumption'] = get_sum('water_consumption', 'consumption_amount')
        stats['waste_amount'] = get_sum('waste_generation', 'waste_amount')
        
    except Exception as e:
        logging.error(f"API Error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if conn: conn.close()
        
    return jsonify(stats)

@app.route('/api/v1/dashboard-stats')
def api_dashboard_stats_v1():
    """
    New API for Vue.js Dashboard.
    Returns module performance and status.
    """
    module_data = []
    completed_reports = 0
    carbon_data = {'Scope 1': 0, 'Scope 2': 0, 'Scope 3': 0}
    survey_status = {'Completed': 0, 'Pending': 0, 'Not Started': 0}

    try:
        from modules.dashboard_stats import DashboardStatsManager
        dsm = DashboardStatsManager(DB_PATH)
        stats = dsm.get_module_stats(g.company_id)
        
        # Transform to list of objects and calculate survey status
        for name, score in stats.items():
            status = 'Pending'
            if score >= 100:
                status = 'Completed'
                survey_status['Completed'] += 1
            elif score > 0:
                status = 'Active'
                survey_status['Pending'] += 1
            else:
                survey_status['Not Started'] += 1

            module_data.append({
                'key': name,
                'name': name.replace('_', ' ').title(),
                'score': score,
                'status': 'Active' if score > 0 else 'Pending'
            })
            
        # Get completed reports count
        try:
            conn = get_db()
            row = conn.execute("SELECT COUNT(*) FROM report_registry WHERE company_id = ?", (g.company_id,)).fetchone()
            if row:
                completed_reports = row[0]
            
            # Get real Carbon Data
            try:
                # Try to fetch carbon data summing up emissions by scope
                # Using co2e_kg column as per schema
                c_rows = []
                try:
                    c_rows = conn.execute("SELECT scope, SUM(co2e_kg) FROM carbon_emissions WHERE company_id = ? GROUP BY scope", (g.company_id,)).fetchall()
                except Exception as ex:
                    logging.warning(f"Could not fetch carbon data with co2e_kg: {ex}")
                    # Fallback to co2e_emissions just in case of schema drift
                    try:
                        c_rows = conn.execute("SELECT scope, SUM(co2e_emissions) FROM carbon_emissions WHERE company_id = ? GROUP BY scope", (g.company_id,)).fetchall()
                    except:
                        pass
                
                for r in c_rows:
                    scope_val = str(r[0])
                    emission_val = r[1] or 0
                    if '1' in scope_val: carbon_data['Scope 1'] += emission_val
                    elif '2' in scope_val: carbon_data['Scope 2'] += emission_val
                    elif '3' in scope_val: carbon_data['Scope 3'] += emission_val
            except Exception as e:
                logging.error(f"Error fetching carbon stats: {e}")

            # Get Next Deadline from auto_tasks or audit_assignments
            next_deadline = '2025-12-31' # Default
            try:
                # Check for nearest due date in active tasks
                task_date = conn.execute("SELECT MIN(due_date) FROM auto_tasks WHERE company_id = ? AND status != 'Tamamlandı' AND due_date >= DATE('now')", (g.company_id,)).fetchone()
                if task_date and task_date[0]:
                    next_deadline = task_date[0]
                else:
                    # Check audit assignments
                    audit_date = conn.execute("SELECT MIN(deadline) FROM audit_assignments WHERE company_id = ? AND status = 'assigned' AND deadline >= DATE('now')", (g.company_id,)).fetchone()
                    if audit_date and audit_date[0]:
                        next_deadline = audit_date[0]
            except Exception as e:
                logging.error(f"Error fetching deadline: {e}")

            conn.close()
        except Exception as e:
            logging.error(f"Error fetching extra stats: {e}")

    except Exception as e:
        logging.error(f"API Dashboard stats v1 error: {e}")
        return jsonify({'error': str(e)}), 500
        
    return jsonify({
        'alerts': 0, 
        'next_deadline': next_deadline, 
        'completed_reports': completed_reports,
        'carbon_data': carbon_data,
        'survey_status': survey_status,
        'modules': module_data
    })

@app.route('/')
@require_company_context
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@limiter_exempt
def login():
    client_ip = request.remote_addr or 'unknown'

    if request.method == 'POST':
        max_attempts, lock_seconds = _get_login_lockout_params()
        rl = rate_limiter.check_rate_limit('login', client_ip, max_requests=max_attempts, window_seconds=lock_seconds)
        if not rl.get('allowed', True):
            flash(f'Çok fazla deneme. {rl.get("reset_in", 60)} saniye sonra tekrar deneyin.', 'danger')
            return render_template('login.html'), 429

        username = request.form.get('username', '')
        password = request.form.get('password', '')

        try:
            conn = get_db()
            row = conn.execute("SELECT locked_until FROM users WHERE username=?", (username,)).fetchone()
            if row and row['locked_until']:
                import time
                if int(row['locked_until']) > int(time.time()):
                    wait = int(row['locked_until']) - int(time.time())
                    flash(f'Hesabınız kilitli. {wait} saniye bekleyin.', 'danger')
                    conn.close()
                    return render_template('login.html')
            conn.close()
        except Exception as e:
            logging.error(f"Lock check error: {e}")

        if user_manager:
            user = user_manager.authenticate(username, password)
            if user:
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
                    logging.info(f"User {username} authenticated. ID: {user.get('id')}")
                    company_id = user_manager.get_user_company(user.get('id'))
                    logging.info(f"Retrieved company_id: {company_id} (Type: {type(company_id)})")
                    
                    # DEBUG: Ensure company_id is int
                    if isinstance(company_id, dict):
                         logging.warning(f"DEBUG: get_user_company returned dict: {company_id}")
                         company_id = company_id.get('id') or company_id.get('company_id')

                    # Fallback for super.admin if company lookup failed but diagnosis shows it exists
                    if not company_id and username == 'super.admin':
                        logging.warning("super.admin has no company from get_user_company. Forcing company_id=1.")
                        company_id = 1

                    # STRICT: If no company assigned, do not default to 1.
                    # This will be caught by require_company_context if None.
                    session['company_id'] = company_id 
                except Exception as e:
                    logging.error(f"Company id error: {e}")
                    session['company_id'] = None
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
                        flash('Test modu girişi', 'warning')
                        return redirect(url_for('dashboard'))
                flash('Kullanıcı adı veya parola hatalı!', 'danger')
        else:
            flash('Sistem hatası: Kullanıcı yönetimi devre dışı.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/reporting_journey')
@require_company_context
def reporting_journey():
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        from backend.core.reporting_journey_manager import ReportingJourneyManager
        company_id = g.company_id
        manager = ReportingJourneyManager()
        journey = manager.get_journey_status(company_id)
    except Exception:
        logging.exception("Reporting journey error")
        journey = []
    return render_template('reporting_journey.html', journey=journey)

@app.route('/journey')
@require_company_context
def reporting_journey_alias():
    return redirect(url_for('reporting_journey'))

@app.route('/journey/complete/<int:step_number>', methods=['POST'])
@require_company_context
def complete_journey_step(step_number):
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    try:
        from backend.core.reporting_journey_manager import ReportingJourneyManager
        company_id = g.company_id
        manager = ReportingJourneyManager()
        success = manager.mark_step_completed(company_id, step_number)
        return jsonify({'success': success})
    except Exception as e:
        logging.error(f"Complete journey step error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/forgot_password', methods=['GET', 'POST'])
@limiter_exempt
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
@limiter_exempt
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
@limiter_exempt
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

@app.route('/dashboard')
@require_company_context
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    stats: Dict[str, int] = {}
    try:
        conn = get_db()
        # Strict Isolation: Only count users belonging to the current tenant
        stats['user_count'] = conn.execute('SELECT COUNT(*) FROM users WHERE company_id = ?', (g.company_id,)).fetchone()[0]
        # Tenant sees only their own company
        stats['company_count'] = 1
        try:
            stats['report_count'] = conn.execute('SELECT COUNT(*) FROM report_registry WHERE company_id = ?', (g.company_id,)).fetchone()[0]
        except Exception:
            stats['report_count'] = 0
        try:
            data_count = 0
            module_stats = {}
            for t, key in [('carbon_emissions', 'carbon'), ('energy_consumption', 'energy'), ('water_consumption', 'water'), ('waste_generation', 'waste')]:
                try:
                    count = conn.execute(f'SELECT COUNT(*) FROM {t} WHERE company_id = ?', (g.company_id,)).fetchone()[0]
                    data_count += count
                    # Simple progress simulation: 1 record = 10%, max 100%
                    module_stats[key] = min(100, count * 10)
                except Exception:
                    module_stats[key] = 0
            stats['data_count'] = data_count
        except Exception:
            stats['data_count'] = 0
            module_stats = {'carbon': 0, 'energy': 0, 'water': 0, 'waste': 0}
        conn.close()
    except Exception as e:
        logging.error(f"Dashboard stats error: {e}")
        module_stats = {'carbon': 0, 'energy': 0, 'water': 0, 'waste': 0}
    
    # Placeholder for ESRS stats to prevent template error
    esrs_stats = {'completion_rate': 0}
    top_material_topics = []
    
    # Placeholder for chart data
    social_chart_data = [0, 0, 0, 0, 0]
    emission_trend_data = [0] * 12

    try:
        return render_template('dashboard.html', 
                             stats=stats, 
                             module_stats=module_stats, 
                             esrs_stats=esrs_stats, 
                             top_material_topics=top_material_topics,
                             social_chart_data=social_chart_data,
                             emission_trend_data=emission_trend_data)
    except Exception as e:
        import traceback
        logging.error(f"Template rendering error: {traceback.format_exc()}")
        return f"Template Error: {e}", 500

@app.route('/help')
@require_company_context
def help_module():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('help.html', title='Yardım Merkezi', manager_available=True)


@app.route('/support')
@require_company_context
def support_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    from backend.modules.support.support_manager import SupportManager
    manager = SupportManager(DB_PATH)

    tickets = manager.get_user_tickets(g.company_id, session.get('user_id'), limit=per_page, offset=offset)
    total_count = manager.get_user_tickets_count(g.company_id, session.get('user_id'))
    total_pages = (total_count + per_page - 1) // per_page

    return render_template('support_list.html', title='Destek Taleplerim', tickets=tickets, page=page, total_pages=total_pages)


@app.route('/support/create', methods=['GET', 'POST'])
@require_company_context
def support_create():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            subject = request.form.get('subject')
            message = request.form.get('description')
            priority = request.form.get('priority', 'medium')
            category = request.form.get('category', 'general')

            from backend.modules.support.support_manager import SupportManager
            manager = SupportManager(DB_PATH)

            success = manager.create_ticket(
                session.get('user_id'),
                g.company_id,
                subject,
                message,
                priority,
                category
            )

            if success:
                flash('Destek talebiniz başarıyla oluşturuldu.', 'success')
                return redirect(url_for('support_dashboard'))
            else:
                flash('Talep oluşturulurken bir hata oluştu.', 'danger')

        except Exception as e:
            logging.error(f"Support ticket error: {e}")
            flash(f'Hata: {e}', 'danger')

    return render_template('support_ticket.html', title='Yeni Destek Talebi')


@app.route('/support/view/<int:ticket_id>', methods=['GET', 'POST'])
@require_company_context
def support_detail(ticket_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    from backend.modules.support.support_manager import SupportManager
    manager = SupportManager(DB_PATH)

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            is_admin = session.get('username') == '__super__'
            manager.add_reply(ticket_id, session.get('user_id'), message, is_admin)
            flash('Yanıtınız gönderildi.', 'success')
            return redirect(url_for('support_detail', ticket_id=ticket_id))

    ticket = manager.get_ticket_details(ticket_id)
    if not ticket:
        flash('Talep bulunamadı.', 'danger')
        return redirect(url_for('support_dashboard'))

    if ticket['company_id'] != g.company_id and session.get('username') != '__super__':
        flash('Erişim reddedildi.', 'danger')
        return redirect(url_for('support_dashboard'))

    return render_template('support_detail.html', title=f"Talep #{ticket['id']}", ticket=ticket)

@app.route('/automated_reporting')
@require_company_context
def automated_reporting():
    if 'user' not in session: return redirect(url_for('login'))
    manager = MANAGERS.get('automated_reporting')
    records = []
    if manager:
        records = manager.get_scheduled_reports(g.company_id)
    return render_template('automated_reporting.html', 
                         manager_available=bool(manager),
                         records=records,
                         columns=['id', 'report_type', 'frequency', 'email_to', 'created_at'])

@app.route('/analytics')
@require_company_context
def analytics():
    if 'user' not in session: return redirect(url_for('login'))
    manager = MANAGERS.get('analytics')
    
    # Gerçek istatistikler (TrendAnalyzer)
    stats = {'Analyzed Metrics': 0, 'Forecasts': 0}
    trend_records = []
    
    if manager:
        # Örnek olarak Karbon emisyon trendini çekmeye çalışalım
        # company_id, table_name, metric_name, years
        current_year = datetime.now().year
        years = list(range(current_year - 4, current_year + 1))
        
        # Trend analizi için örnek metrikler
        try:
            # Carbon emissions tablosunda 'year' kolonu yok, 'period_start' var.
            carbon_trend = manager.get_metric_trend(g.company_id, 'carbon_emissions', 'amount', years, date_column='period_start')
            if carbon_trend:
                trend_stats = manager.calculate_trend_statistics(carbon_trend)
                stats['Analyzed Metrics'] = len(carbon_trend)
                stats['Trend Direction'] = trend_stats.get('trend_text', '-')
                
                # Frontend için kayıtlar
                trend_records.append({
                    'metric': 'Carbon Emissions (Scope 1)',
                    'trend': trend_stats.get('trend_text', '-'),
                    'change': f"%{trend_stats.get('total_change_percent', 0)}",
                    'average': trend_stats.get('average', 0)
                })
        except Exception as e:
            logging.error(f"Analytics metric fetch error: {e}")

    return render_template('analytics.html', 
                         manager_available=bool(manager),
                         stats=stats,
                         records=trend_records)

@app.route('/data_inventory')
@require_company_context
def data_inventory():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('data_inventory')
    
    # Default empty values
    dashboard_data = {
        'stats': {},
        'records': [],
        'columns': [],
        'widgets': [],
        'data_sources': [],
        'kpis': []
    }
    
    if manager:
        try:
            # Get dashboard data using the manager
            dashboard_data = manager.get_dashboard_data(g.company_id)
        except Exception as e:
            logging.error(f"Data Inventory dashboard data error: {e}")
            flash('Veri envanteri yüklenirken bir hata oluştu.', 'danger')
            
    return render_template('data_inventory.html', 
                         manager_available=bool(manager),
                         stats=dashboard_data.get('stats', {}),
                         records=dashboard_data.get('records', []),
                         columns=dashboard_data.get('columns', []),
                         widgets=dashboard_data.get('widgets', []),
                         data_sources=dashboard_data.get('data_sources', []),
                         kpis=dashboard_data.get('kpis', []))

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

@app.route('/ifrs')
@require_company_context
def ifrs_module():
    if 'user' not in session: return redirect(url_for('login'))
    return redirect(url_for('issb_module'))

@app.route('/data')
@require_company_context
def data():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_ctx = {'carbon': [], 'energy': [], 'water': [], 'waste': []}
    try:
        conn = get_db()
        try: data_ctx['carbon'] = conn.execute("SELECT * FROM carbon_emissions WHERE company_id = ? ORDER BY created_at DESC LIMIT 50", (g.company_id,)).fetchall()
        except: pass
        try: data_ctx['energy'] = conn.execute("SELECT * FROM energy_consumption WHERE company_id = ? ORDER BY year DESC, month DESC LIMIT 50", (g.company_id,)).fetchall()
        except: pass
        try: data_ctx['water'] = conn.execute("SELECT * FROM water_consumption WHERE company_id = ? ORDER BY year DESC, month DESC LIMIT 50", (g.company_id,)).fetchall()
        except: pass
        try: data_ctx['waste'] = conn.execute("SELECT * FROM waste_generation WHERE company_id = ? ORDER BY date DESC LIMIT 50", (g.company_id,)).fetchall()
        except: pass
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        
    return render_template('data.html', title='Veri Girişi', data=data_ctx)

@app.route('/data/add', methods=['GET', 'POST'])
@require_company_context
@limiter.limit("10 per minute")
def data_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_type = request.args.get('type') or request.args.get('data_type')
    
    module = request.args.get('module')
    
    if request.method == 'POST':
        try:
            dtype = request.form.get('data_type')
            date_str = request.form.get('date', '')
            company_id = g.company_id
            
            if not dtype:
                flash('Lütfen veri türünü seçin.', 'danger')
                return render_template('data_edit.html', title='Yeni Veri Girişi', data_type=data_type, module=module, date=date_str)
            
            if not date_str:
                flash('Lütfen tarih veya dönemi girin.', 'danger')
                return render_template('data_edit.html', title='Yeni Veri Girişi', data_type=dtype, module=module, date=date_str)
            
            conn = get_db()
            
            if dtype == 'carbon':
                scope = request.form.get('scope') or ''
                category = request.form.get('category') or ''
                quantity = request.form.get('amount') or ''
                unit = request.form.get('unit') or ''
                co2e = request.form.get('co2e') or ''
                
                missing = []
                if not scope: missing.append('Kapsam')
                if not category: missing.append('Kategori')
                if not quantity: missing.append('Miktar')
                if not unit: missing.append('Birim')
                
                if missing:
                    flash('Lütfen zorunlu alanları doldurun: ' + ', '.join(missing), 'danger')
                    return render_template('data_edit.html', title='Yeni Veri Girişi', data_type=dtype, module=module, date=date_str, scope=scope, category=category, amount=quantity, unit=unit, co2e=co2e)
                
                conn.execute("INSERT INTO carbon_emissions (company_id, scope, category, quantity, unit, co2e_emissions, period, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (company_id, scope, category, quantity, unit, co2e, date_str))
            
            elif dtype == 'energy':
                etype = request.form.get('energy_type') or ''
                cons = request.form.get('energy_consumption') or ''
                unit = request.form.get('energy_unit') or ''
                cost = request.form.get('cost') or ''
                
                missing = []
                if not etype: missing.append('Enerji Türü')
                if not cons: missing.append('Tüketim Miktarı')
                if not unit: missing.append('Birim')
                
                if missing:
                    flash('Lütfen zorunlu alanları doldurun: ' + ', '.join(missing), 'danger')
                    return render_template('data_edit.html', title='Yeni Veri Girişi', data_type=dtype, module=module, date=date_str, energy_type=etype, energy_consumption=cons, energy_unit=unit, cost=cost)
                
                year, month = 2024, 1
                if '-' in date_str:
                     parts = date_str.split('-')
                     if len(parts) >= 2:
                        year = parts[0]
                        month = parts[1]
                conn.execute("INSERT INTO energy_consumption (company_id, energy_type, consumption_amount, unit, cost, year, month, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (company_id, etype, cons, unit, cost, year, month))
                
            elif dtype == 'water':
                wtype = request.form.get('water_type') or ''
                cons = request.form.get('water_consumption') or ''
                unit = request.form.get('water_unit') or ''
                
                missing = []
                if not wtype: missing.append('Su Kaynağı')
                if not cons: missing.append('Tüketim Miktarı')
                if not unit: missing.append('Birim')
                
                if missing:
                    flash('Lütfen zorunlu alanları doldurun: ' + ', '.join(missing), 'danger')
                    return render_template('data_edit.html', title='Yeni Veri Girişi', data_type=dtype, module=module, date=date_str, water_type=wtype, water_consumption=cons, water_unit=unit)
                
                conn.execute("INSERT INTO water_consumption (company_id, source_type, consumption_amount, unit, year, month, created_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (company_id, wtype, cons, unit, 2024, 1))
                
            elif dtype == 'waste':
                wtype = request.form.get('waste_type') or ''
                amount = request.form.get('waste_amount') or ''
                unit = request.form.get('waste_unit') or ''
                method = request.form.get('disposal_method') or ''
                
                missing = []
                if not wtype: missing.append('Atık Türü')
                if not amount: missing.append('Miktar')
                if not unit: missing.append('Birim')
                if not method: missing.append('Bertaraf Yöntemi')
                
                if missing:
                    flash('Lütfen zorunlu alanları doldurun: ' + ', '.join(missing), 'danger')
                    return render_template('data_edit.html', title='Yeni Veri Girişi', data_type=dtype, module=module, date=date_str, waste_type=wtype, waste_amount=amount, waste_unit=unit, disposal_method=method)
                
                conn.execute("INSERT INTO waste_generation (company_id, waste_type, amount, unit, disposal_method, date, created_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (company_id, wtype, amount, unit, method, date_str))

            elif dtype == 'biodiversity':
                cat = request.form.get('bio_category')
                desc = request.form.get('bio_description')
                area = request.form.get('bio_area')
                status = request.form.get('bio_status')
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS biodiversity_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        category TEXT,
                        description TEXT,
                        affected_area REAL,
                        status TEXT,
                        date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("INSERT INTO biodiversity_data (company_id, category, description, affected_area, status, date, created_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (company_id, cat, desc, area, status, date_str))

            conn.commit()
            conn.close()
            flash('Veri başarıyla eklendi.', 'success')
            return redirect(url_for('data'))
            
        except Exception as e:
            logging.error(f"Error adding data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('data_edit.html', title='Yeni Veri Girişi', data_type=data_type, module=module)

# --- Basic Admin Pages ---

@app.route('/users')
@require_company_context
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    users = []
    pagination = None
    try:
        conn = get_db()
        offset = (page - 1) * per_page
        total = conn.execute("SELECT COUNT(*) FROM users WHERE company_id = ?", (g.company_id,)).fetchone()[0]
        
        rows = conn.execute("""
            SELECT u.id, u.username, u.email, u.first_name || ' ' || u.last_name as full_name, 
                   u.department, u.is_active, u.last_login, r.name as role
            FROM users u
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            WHERE u.company_id = ?
            ORDER BY u.id DESC
            LIMIT ? OFFSET ?
        """, (g.company_id, per_page, offset)).fetchall()
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

@app.route('/users/add', methods=['GET', 'POST'])
@require_company_context
@admin_required
def user_add():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            full_name = request.form.get('full_name', '')
            role_name = request.form.get('role', 'User')
            department = request.form.get('department')
            is_active = request.form.get('is_active') == 'on'
            
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
            
            conn = get_db()
            exist = conn.execute("SELECT 1 FROM users WHERE username=? OR email=?", (username, email)).fetchone()
            if exist:
                flash('Kullanıcı adı veya e-posta zaten kayıtlı.', 'warning')
                conn.close()
                return render_template('user_edit.html', user=None)

            from werkzeug.security import generate_password_hash
            pw_hash = generate_password_hash(password)
            
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, department, is_active, company_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (username, email, pw_hash, first_name, last_name, department, is_active, g.company_id))
            user_id = cur.lastrowid
            
            role_row = conn.execute("SELECT id FROM roles WHERE name=?", (role_name,)).fetchone()
            if role_row:
                cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_row['id']))
                
            conn.commit()
            conn.close()
            flash('Kullanıcı başarıyla oluşturuldu.', 'success')
            return redirect(url_for('users'))
            
        except Exception as e:
            logging.error(f"Error adding user: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('user_edit.html', user=None)

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@require_company_context
@admin_required
def user_edit(user_id):
    conn = get_db()
    
    # Security check: User must belong to the same company
    check_user = conn.execute("SELECT id FROM users WHERE id=? AND company_id=?", (user_id, g.company_id)).fetchone()
    if not check_user:
        conn.close()
        flash('Kullanıcı bulunamadı veya bu işlem için yetkiniz yok.', 'danger')
        return redirect(url_for('users'))

    if request.method == 'POST':
        try:
            email = request.form.get('email')
            full_name = request.form.get('full_name', '')
            role_name = request.form.get('role', 'User')
            department = request.form.get('department')
            is_active = request.form.get('is_active') == 'on'
            password = request.form.get('password')
            
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
            
            update_sql = """
                UPDATE users SET email=?, first_name=?, last_name=?, department=?, is_active=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """
            params = [email, first_name, last_name, department, is_active, user_id]
            conn.execute(update_sql, params)
            
            if password:
                from werkzeug.security import generate_password_hash
                pw_hash = generate_password_hash(password)
                conn.execute("UPDATE users SET password_hash=? WHERE id=?", (pw_hash, user_id))
            
            conn.execute("DELETE FROM user_roles WHERE user_id=?", (user_id,))
            role_row = conn.execute("SELECT id FROM roles WHERE name=?", (role_name,)).fetchone()
            if role_row:
                conn.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_row['id']))
                
            conn.commit()
            flash('Kullanıcı güncellendi.', 'success')
            conn.close()
            return redirect(url_for('users'))
        except Exception as e:
            logging.error(f"Error editing user: {e}")
            flash(f'Hata: {e}', 'danger')
            
    user = conn.execute("""
        SELECT u.*, r.name as role, (u.first_name || ' ' || u.last_name) as full_name
        FROM users u
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE u.id=?
    """, (user_id,)).fetchone()
    conn.close()
    
    if not user:
        flash('Kullanıcı bulunamadı.', 'warning')
        return redirect(url_for('users'))
        
    return render_template('user_edit.html', user=user)

@app.route('/users/delete/<int:user_id>')
@require_company_context
@admin_required
def user_delete(user_id):
    if user_id == session.get('user_id'):
        flash('Kendinizi silemezsiniz.', 'warning')
        return redirect(url_for('users'))
    try:
        conn = get_db()
        # Security check
        check = conn.execute("SELECT 1 FROM users WHERE id=? AND company_id=?", (user_id, g.company_id)).fetchone()
        if not check:
            conn.close()
            flash('Yetkisiz işlem.', 'danger')
            return redirect(url_for('users'))
            
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
        # Strict Isolation: Tenant sees only their own company
        companies = conn.execute("SELECT * FROM companies WHERE id = ?", (g.company_id,)).fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching companies: {e}")
        
    return render_template('companies.html', title='Şirketler', companies=companies)

@app.route('/companies/add', methods=['GET', 'POST'])
@admin_required
def company_add():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            sector = request.form.get('sector')
            country = request.form.get('country')
            tax_number = request.form.get('tax_number')
            is_active = request.form.get('is_active') == 'on'
            
            conn = get_db()
            conn.execute("""
                INSERT INTO companies (name, sector, country, tax_number, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, sector, country, tax_number, is_active))
            conn.commit()
            conn.close()
            flash('Şirket oluşturuldu.', 'success')
            return redirect(url_for('companies'))
        except Exception as e:
            logging.error(f"Error adding company: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('company_edit.html', company=None)

@app.route('/companies/<int:company_id>/info', methods=['GET', 'POST'])
@require_company_context
def company_info_edit(company_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    # Security check: Tenant isolation
    if company_id != g.company_id:
        flash('Yetkisiz erişim.', 'danger')
        return redirect(url_for('dashboard'))

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


@app.route('/companies/<int:company_id>/gri', methods=['GET', 'POST'])
def company_gri_edit(company_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    flash('Firma bilgileri artık tek bir sayfadan yönetiliyor.', 'info')
    return redirect(url_for('company_info_edit', company_id=company_id))

@app.route('/companies/detail/<int:company_id>')
@require_company_context
def company_detail(company_id):
    if 'user' not in session: return redirect(url_for('login'))
    
    # Security check
    if company_id != g.company_id:
        flash('Yetkisiz erişim.', 'danger')
        return redirect(url_for('dashboard'))
        
    conn = get_db()
    company = conn.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
    conn.close()
    if not company:
        flash('Şirket bulunamadı.', 'warning')
        return redirect(url_for('companies'))
    return render_template('company_detail.html', company=company)

@app.route('/reports')
@require_company_context
def reports():
    if 'user' not in session:
        return redirect(url_for('login'))
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

        total_row = conn.execute("SELECT COUNT(*) FROM report_registry WHERE company_id = ?", (g.company_id,)).fetchone()
        total = total_row[0] if total_row else 0

        reports = conn.execute(
            "SELECT * FROM report_registry WHERE company_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (g.company_id, per_page, offset),
        ).fetchall()

        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total,
        }
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching reports: {e}")
    return render_template('reports.html', title='Raporlar', reports=reports, pagination=pagination)


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
            manager = MANAGERS.get('advanced_report')
            if manager:
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


@app.route('/reports/wizard/generate', methods=['POST'])
@require_company_context
def report_wizard_generate():
    if 'user' not in session: return redirect(url_for('login'))
    
    try:
        module_code = request.form.get('module')
        report_name = request.form.get('report_name')
        period = request.form.get('period')
        fmt = request.form.get('format', 'pdf')
        include_ai = request.form.get('include_ai') == 'on'
        
        company_id = g.company_id
        
        # Unified Report Handling
        if module_code == 'unified':
            return redirect(url_for('unified_report'))
            
        # Standard Modules
        formats = [fmt]
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
            sr = SocialReporting(DB_PATH)
            generated = sr.generate_social_report(company_id, period, formats=formats)
        elif module_code == 'governance':
            gm = CorporateGovernanceManager(DB_PATH)
            gr = GovernanceReporting(gm)
            generated = gr.generate_governance_report(company_id, period, formats=formats)
        else:
            flash('Seçilen modül henüz desteklenmiyor.', 'warning')
            return redirect(url_for('report_wizard'))
            
        if generated:
            flash(f'{report_name} başarıyla oluşturuldu.', 'success')
            # If AI summary requested and supported, we could trigger it here
            # For now, we rely on the managers doing their job
        else:
            flash('Rapor oluşturulamadı.', 'danger')
            
        return redirect(url_for('reports'))
        
    except Exception as e:
        logging.error(f"Wizard Error: {e}")
        flash(f'Hata: {e}', 'danger')
        return redirect(url_for('report_wizard'))

@app.route('/reports/wizard')
@app.route('/report_wizard')
@require_company_context
def report_wizard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('report_wizard.html', title='Rapor Oluşturma Sihirbazı')

@app.route('/reports/add', methods=['GET', 'POST'])
@require_company_context
@limiter.limit("5 per minute")
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
            elif module_code in ['carbon', 'energy', 'water', 'waste', 'social', 'governance']:
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
                    
                    if generated:
                        # İlk üretilen dosyayı al
                        key = formats[0] if formats else 'docx'
                        if key in generated:
                            gen_path = generated[key]
                            # Dosyayı uploads klasörüne taşı
                            import shutil
                            upload_folder = os.path.join(BACKEND_DIR, 'uploads', 'reports')
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
            selected_modules = request.form.getlist('modules')
            include_ai = request.form.get('include_ai') in ['on', '1', 'true', 'True']
            if not selected_modules:
                flash('En az bir modül seçmelisiniz.', 'warning')
                return redirect(url_for('unified_report'))
            context_for_ai = {
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
                metrics = {}
                taxonomy_mappings = []
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
                                aggregated = {}
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
                    ai_comment, _ = ai_manager.generate_summary(context_for_ai, report_type='unified')
                    if not ai_comment:
                        ai_comment = ''
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
        try:
            default_reporting_period = session.get('reporting_period') or str(datetime.now().year)
        except Exception:
            default_reporting_period = str(datetime.now().year)
        default_report_name = 'Birleşik Sürdürülebilirlik Raporu'
        survey_summary = None
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
            totals = {}
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
        suggested_modules = []
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
        # Enforce company isolation
        report = conn.execute(
            "SELECT * FROM report_registry WHERE id=? AND company_id=?", 
            (report_id, g.company_id)
        ).fetchone()
        conn.close()

        if not report:
            flash('Rapor bulunamadı veya erişim yetkiniz yok.', 'warning')
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


@app.route('/reports/delete/<int:report_id>', methods=['POST'])
@require_company_context
def report_delete(report_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        conn = get_db()
        # Enforce company isolation
        report = conn.execute(
            "SELECT file_path FROM report_registry WHERE id=? AND company_id=?", 
            (report_id, g.company_id)
        ).fetchone()

        if report:
            if report['file_path'] and os.path.exists(report['file_path']):
                try:
                    os.remove(report['file_path'])
                except Exception as e:
                    logging.error(f"Error deleting file: {e}")
            
            # Only delete if it belongs to the company (already checked by SELECT, but good for WHERE clause in DELETE too)
            conn.execute("DELETE FROM report_registry WHERE id=? AND company_id=?", (report_id, g.company_id))
            conn.commit()
            conn.close()
            flash('Rapor silindi.', 'success')
        else:
            conn.close()
            flash('Rapor bulunamadı veya silme yetkiniz yok.', 'warning')

    except Exception as e:
        logging.error(f"Error deleting report: {e}")
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


@app.route('/reports/bulk_delete', methods=['POST'])
@require_company_context
def reports_bulk_delete():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        report_ids = request.form.getlist('report_ids')
        if not report_ids:
            flash('Hiçbir rapor seçilmedi.', 'warning')
            return redirect(url_for('reports'))

        conn = get_db()
        deleted_count = 0

        for report_id in report_ids:
            try:
                report = conn.execute("SELECT file_path FROM report_registry WHERE id=? AND company_id=?", (report_id, g.company_id)).fetchone()
                if report:
                    file_path = report['file_path']
                    if file_path and '\\' in file_path and os.name != 'nt':
                        file_path = file_path.replace('\\', '/')
                    if file_path and not os.path.exists(file_path):
                        if 'reports' in file_path:
                            normalized_path = file_path.replace('\\', '/')
                            idx = normalized_path.rfind('reports')
                            if idx != -1:
                                rel_path = normalized_path[idx:]
                                if os.path.exists(rel_path):
                                    file_path = rel_path
                        if not os.path.exists(file_path):
                            basename = os.path.basename(file_path)
                            candidate = os.path.join('reports', basename)
                            if os.path.exists(candidate):
                                file_path = candidate

                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            logging.error(f"Error deleting file {file_path}: {e}")

                    conn.execute("DELETE FROM report_registry WHERE id=? AND company_id=?", (report_id, g.company_id))
                    deleted_count += 1
            except Exception as e:
                logging.error(f"Error processing bulk delete for id {report_id}: {e}")

        conn.commit()
        conn.close()

        if deleted_count > 0:
            flash(f'{deleted_count} rapor başarıyla silindi.', 'success')
        else:
            flash('Silinecek rapor bulunamadı veya yetki hatası.', 'warning')

    except Exception as e:
        logging.error(f"Error in bulk delete: {e}")
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

@app.route('/sdg', methods=['GET', 'POST'])
@require_company_context
def sdg_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = SDGManager(DB_PATH)
    company_id = g.company_id

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

    try:
        all_goals = manager.get_all_goals()
        selected_ids = manager.get_selected_goals(company_id)
        stats = manager.get_statistics(company_id)
        
        selected_goals_details = []
        recent_data = manager.get_recent_responses(company_id)
        
        selected_goals_objs = [goal_item for goal_item in all_goals if goal_item['id'] in selected_ids]
        
        for goal in selected_goals_objs:
            g_detail = {
                'id': goal['id'],
                'title': goal['name_tr'],
                'description': goal.get('description', ''), 
                'targets': [],
                'module_link': None
            }
            
            # Module mapping
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

            targets = manager.get_goal_targets(goal['id'])
            for target in targets:
                t_detail = {
                    'id': target['id'],
                    'code': target['code'],
                    'title': target['name_tr'],
                    'indicators': []
                }
                
                indicators = manager.get_target_indicators(target['id'])
                for ind in indicators:
                    i_detail = {
                        'id': ind['id'],
                        'code': ind['code'],
                        'title': ind['name_tr'],
                        'gri_mappings': []
                    }
                    if ind.get('gri_mapping'):
                        i_detail['gri_mappings'] = [{'code': ind['gri_mapping'], 'type': 'direct'}]
                    t_detail['indicators'].append(i_detail)
                
                g_detail['targets'].append(t_detail)
            
            selected_goals_details.append(g_detail)

        return render_template('sdg.html', 
                             title='Sürdürülebilir Kalkınma Amaçları', 
                             manager_available=True, 
                             stats=stats, 
                             all_goals=all_goals,
                             selected_ids=selected_ids,
                             selected_goals_details=selected_goals_details,
                             recent_data=recent_data)
                             
    except Exception as e:
        logging.error(f"SDG module error: {e}")
        flash(f"Bir hata oluştu: {e}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/sdg/add', methods=['GET', 'POST'])
@require_company_context
def sdg_add():
    if 'user' not in session: return redirect(url_for('login'))
    
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
            form_indicator_id = request.form.get('indicator_id')
            
            if form_indicator_id:
                action = request.form.get('action') or request.form.get('notes')
                progress_pct = request.form.get('progress_pct', 0)
                value = request.form.get('value', 0)
                
                manager.save_response(
                    company_id=company_id,
                    indicator_id=int(form_indicator_id),
                    period=str(year),
                    value=value,
                    progress_pct=int(progress_pct),
                    status=request.form.get('status', 'pending'),
                    action=action
                )
                
                flash('SDG ilerlemesi kaydedildi.', 'success')
                return redirect(url_for('sdg_module'))
            
            else:
                goal_id = request.form.get('goal_id')
                target = request.form.get('target')
                action = request.form.get('action')
                status = request.form.get('status')
                progress_pct = request.form.get('progress_pct')

                conn = get_db()
                conn.execute(
                    """
                    INSERT INTO sdg_progress 
                    (company_id, year, goal_id, target, action, status, progress_pct, created_at) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (company_id, year, goal_id, target, action, status, progress_pct),
                )
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
            SELECT gd.*, gs.sector, gs.title as standard_title 
            FROM gri_data gd 
            LEFT JOIN gri_standards gs ON gd.standard = gs.code 
            WHERE gd.company_id = ? 
            ORDER BY gd.created_at DESC
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

@app.route('/social')
@require_company_context
def social_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    stats = {'employees': 0, 'incidents': 0, 'training_hours': 0}
    recent_data = []
    company_id = g.company_id
    
    try:
        conn = get_db()
        
        # Ensure tables exist with company_id
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hr_employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    employee_count INTEGER,
                    gender TEXT,
                    department TEXT,
                    age_group TEXT,
                    year INTEGER,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ohs_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    incident_type TEXT,
                    date DATE,
                    severity TEXT,
                    description TEXT,
                    lost_time_days INTEGER,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    training_name TEXT,
                    hours REAL,
                    participants INTEGER,
                    date DATE,
                    category TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ensure company_id exists in all tables
            try: conn.execute("ALTER TABLE hr_employees ADD COLUMN company_id INTEGER")
            except: pass
            try: conn.execute("ALTER TABLE ohs_incidents ADD COLUMN company_id INTEGER")
            except: pass
            try: conn.execute("ALTER TABLE training_records ADD COLUMN company_id INTEGER")
            except: pass
            
        except Exception as e:
            logging.error(f"Error creating social tables: {e}")

        # Employees
        try:
            row = conn.execute("SELECT SUM(employee_count) FROM hr_employees WHERE company_id = ?", (company_id,)).fetchone()
            if row and row[0]: stats['employees'] = row[0]
        except: pass
        
        # OHS
        try:
            row = conn.execute("SELECT COUNT(*) FROM ohs_incidents WHERE company_id = ?", (company_id,)).fetchone()
            if row and row[0]: stats['incidents'] = row[0]
        except: pass
        
        # Training
        try:
            row = conn.execute("SELECT SUM(hours) FROM training_records WHERE company_id = ?", (company_id,)).fetchone()
            if row and row[0]: stats['training_hours'] = row[0]
        except: pass
        
        # Recent Data Fetch
        try:
            # HR
            hr_rows = conn.execute("SELECT 'employee' as type, department || ' (' || gender || ')' as detail, year as date, employee_count as value, created_date FROM hr_employees WHERE company_id = ? ORDER BY created_date DESC LIMIT 5", (company_id,)).fetchall()
            for r in hr_rows: recent_data.append(dict(r))
            
            # OHS
            ohs_rows = conn.execute("SELECT 'ohs' as type, incident_type as detail, date, severity as value, created_date FROM ohs_incidents WHERE company_id = ? ORDER BY created_date DESC LIMIT 5", (company_id,)).fetchall()
            for r in ohs_rows: recent_data.append(dict(r))
            
            # Training
            tr_rows = conn.execute("SELECT 'training' as type, training_name as detail, date, hours || ' saat' as value, created_date FROM training_records WHERE company_id = ? ORDER BY created_date DESC LIMIT 5", (company_id,)).fetchall()
            for r in tr_rows: recent_data.append(dict(r))
            
            # Sort all by created_date desc
            recent_data.sort(key=lambda x: x['created_date'], reverse=True)
            recent_data = recent_data[:10]
            
        except Exception as e:
            logging.error(f"Error fetching social recent data: {e}")
            
        conn.close()
    except Exception as e:
        logging.error(f"Error in social stats: {e}")
        
    return render_template('social.html', title='Sosyal Etki', stats=stats, recent_data=recent_data)


@app.route('/social/add', methods=['GET', 'POST'])
@require_company_context
def social_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_type = request.args.get('type', 'employee')
    
    if request.method == 'POST':
        try:
            dtype = request.form.get('data_type')
            company_id = g.company_id
            conn = get_db()
            
            if dtype == 'employee':
                count = request.form.get('employee_count')
                gender = request.form.get('gender')
                dept = request.form.get('department')
                age = request.form.get('age_group')
                year = request.form.get('year')
                conn.execute("INSERT INTO hr_employees (company_id, employee_count, gender, department, age_group, year, created_date) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (company_id, count, gender, dept, age, year))
                
            elif dtype == 'ohs':
                itype = request.form.get('incident_type')
                date = request.form.get('date')
                severity = request.form.get('severity')
                desc = request.form.get('description')
                lost = request.form.get('lost_time_days')
                conn.execute("INSERT INTO ohs_incidents (company_id, incident_type, date, severity, description, lost_time_days, created_date) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (company_id, itype, date, severity, desc, lost))
                
            elif dtype == 'training':
                name = request.form.get('training_name')
                hours = request.form.get('hours')
                parts = request.form.get('participants')
                date = request.form.get('date')
                cat = request.form.get('category')
                conn.execute("INSERT INTO training_records (company_id, training_name, hours, participants, date, category, created_date) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (company_id, name, hours, parts, date, cat))
            
            conn.commit()
            conn.close()
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
    
    stats = {'board_members': 0, 'committees': 0}
    company_id = g.company_id
    
    try:
        conn = get_db()
        # Board Members Count
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS board_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    member_name TEXT NOT NULL,
                    position TEXT NOT NULL,
                    member_type TEXT NOT NULL,
                    independence_status TEXT,
                    gender TEXT,
                    expertise_area TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            row = conn.execute("SELECT COUNT(*) FROM board_members WHERE company_id = ?", (company_id,)).fetchone()
            if row: stats['board_members'] = row[0]
        except Exception as e:
            logging.error(f"Error fetching board stats: {e}")
            
        # Committees Count
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS governance_committees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    committee_name TEXT NOT NULL,
                    committee_type TEXT NOT NULL,
                    member_count INTEGER,
                    responsibilities TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            row = conn.execute("SELECT COUNT(*) FROM governance_committees WHERE company_id = ?", (company_id,)).fetchone()
            if row: stats['committees'] = row[0]
        except Exception as e:
            logging.error(f"Error fetching committee stats: {e}")
            
        conn.close()
    except Exception as e:
        logging.error(f"Error in governance module: {e}")

    return render_template('governance.html', title='Kurumsal Yönetişim', manager_available=bool(MANAGERS.get('governance')), stats=stats)

@app.route('/governance/add', methods=['GET', 'POST'])
@require_company_context
def governance_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_type = request.args.get('type', 'board_member')
    
    if request.method == 'POST':
        try:
            dtype = request.form.get('data_type')
            company_id = g.company_id
            conn = get_db()
            
            if dtype == 'board_member':
                name = request.form.get('member_name')
                pos = request.form.get('position')
                mtype = request.form.get('member_type')
                indep = request.form.get('independence_status')
                gender = request.form.get('gender')
                expert = request.form.get('expertise_area')
                
                conn.execute("""
                    INSERT INTO board_members 
                    (company_id, member_name, position, member_type, independence_status, gender, expertise_area) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (company_id, name, pos, mtype, indep, gender, expert))
                
            elif dtype == 'committee':
                name = request.form.get('committee_name')
                ctype = request.form.get('committee_type')
                count = request.form.get('member_count')
                resp = request.form.get('responsibilities')
                
                conn.execute("""
                    INSERT INTO governance_committees 
                    (company_id, committee_name, committee_type, member_count, responsibilities) 
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, name, ctype, count, resp))
                
            conn.commit()
            conn.close()
            flash('Veri başarıyla eklendi.', 'success')
            return redirect(url_for('governance_module'))
            
        except Exception as e:
            logging.error(f"Error adding governance data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('governance_edit.html', title='Yönetişim Veri Girişi', data_type=data_type)

@app.route('/carbon')
@require_company_context
def carbon_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {'total_co2e': 0, 'scope1': 0, 'scope2': 0, 'scope3': 0}
    recent_data = []
    
    try:
        conn = get_db()
        # Stats
        rows = conn.execute("SELECT scope, SUM(co2e_emissions) FROM carbon_emissions WHERE company_id = ? GROUP BY scope", (company_id,)).fetchall()
        for r in rows:
            scope = r[0]
            val = r[1] or 0
            if scope == 'Scope 1': stats['scope1'] = val
            elif scope == 'Scope 2': stats['scope2'] = val
            elif scope == 'Scope 3': stats['scope3'] = val
            
        stats['total_co2e'] = stats['scope1'] + stats['scope2'] + stats['scope3']
        
        # Recent Data
        recent_data = conn.execute("SELECT * FROM carbon_emissions WHERE company_id = ? ORDER BY created_at DESC LIMIT 10", (company_id,)).fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching carbon stats: {e}")

    return render_template('carbon.html', title='Karbon Ayak İzi', manager_available=bool(MANAGERS.get('carbon')), stats=stats, recent_data=recent_data)

@app.route('/energy')
@require_company_context
def energy_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {'total_consumption': 0, 'renewable_ratio': 0, 'total_cost': 0}
    recent_data = []
    
    try:
        conn = get_db()
        # Stats
        row = conn.execute("SELECT SUM(consumption_amount), SUM(cost) FROM energy_consumption WHERE company_id = ?", (company_id,)).fetchone()
        if row:
            stats['total_consumption'] = row[0] or 0
            stats['total_cost'] = row[1] or 0
            
        # Recent Data
        recent_data = conn.execute("SELECT * FROM energy_consumption WHERE company_id = ? ORDER BY created_at DESC LIMIT 10", (company_id,)).fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching energy stats: {e}")

    return render_template('energy.html', title='Enerji Yönetimi', manager_available=bool(MANAGERS.get('energy')), stats=stats, recent_data=recent_data)

@app.route('/esg')
@require_company_context
def esg_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('esg')
    
    if not manager:
        stats = {'environmental': 0, 'social': 0, 'governance': 0}
        history = []
        return render_template('esg.html', title='ESG Skorlama', manager_available=False, stats=stats, history=history)

    try:
        stats = manager.get_dashboard_stats(company_id)
        history = manager.get_history(company_id)
    except Exception as e:
        logging.error(f"ESG module error: {e}")
        stats = {'environmental': 0, 'social': 0, 'governance': 0}
        history = []

    return render_template('esg.html', title='ESG Skorlama', manager_available=True, stats=stats, history=history)

@app.route('/auto_tasks')
@require_company_context
def auto_tasks_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('auto_tasks')
    
    stats = {'total_tasks': 0, 'active_tasks': 0, 'completed_tasks': 0}
    records = []
    
    if manager:
        try:
            stats = manager.get_stats(company_id)
            records = manager.get_records(company_id)
        except Exception as e:
            logging.error(f"AutoTasks module error: {e}")
            
    columns = list(records[0].keys()) if records else []
            
    return render_template('auto_tasks.html', 
                         title='Otomatik Görevler',
                         manager_available=bool(manager),
                         stats=stats,
                         records=records,
                         columns=columns)

@app.route('/visualization')
@require_company_context
def visualization_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('visualization')
    
    stats = {'total_charts': 0, 'dashboards': 0}
    records = []
    
    if manager:
        try:
            stats = manager.get_stats(company_id)
            records = manager.get_records(company_id)
        except Exception as e:
            logging.error(f"Visualization module error: {e}")
            
    columns = list(records[0].keys()) if records else []
            
    return render_template('visualization.html', 
                         title='Görselleştirme',
                         manager_available=bool(manager),
                         stats=stats,
                         records=records,
                         columns=columns)


@app.route('/esg/add', methods=['GET', 'POST'])
@require_company_context
def esg_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    manager = MANAGERS.get('esg')
    if not manager:
        flash('ESG modülü aktif değil.', 'danger')
        return redirect(url_for('esg_module'))

    company_id = g.company_id
    computed_scores = None

    try:
        computed_scores = manager.compute_scores(company_id)
    except Exception as e:
        logging.error(f"Error computing ESG scores for form: {e}")

    if request.method == 'POST':
        try:
            year = int(request.form.get('year'))
            quarter = int(request.form.get('quarter'))

            scores = manager.compute_scores(company_id)
            env = scores['E']
            soc = scores['S']
            gov = scores['G']
            total = scores['overall']
            
            conn = get_db()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS esg_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER,
                    quarter INTEGER,
                    environmental_score REAL,
                    social_score REAL,
                    governance_score REAL,
                    total_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            conn.execute("""
                INSERT INTO esg_scores 
                (company_id, year, quarter, environmental_score, social_score, governance_score, total_score, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, year, quarter, env, soc, gov, total))
            conn.commit()
            conn.close()
            flash('ESG skorları mevcut verilerden hesaplanarak kaydedildi.', 'success')
            return redirect(url_for('esg_module'))
        except Exception as e:
            logging.error(f"Error adding ESG scores: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('esg_edit.html', title='ESG Veri Girişi', scores=computed_scores)

@app.route('/cbam')
@require_company_context
def cbam_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('cbam')

    if not manager:
        return render_template(
            'cbam.html',
            title='CBAM Uyumluluk',
            manager_available=False,
            stats={'total_emissions': 0, 'total_imports': 0, 'liability': 0, 'imports': []},
        )

    period = request.args.get('period')
    report = None
    ets_factors = []
    try:
        stats = manager.get_dashboard_stats(company_id)
        if period:
            report = manager.calculate_cbam_liability(company_id, period)
        if hasattr(manager, 'get_ets_factors'):
            ets_factors = manager.get_ets_factors()
    except Exception as e:
        logging.error(f"CBAM module error: {e}")
        stats = {'total_emissions': 0, 'total_imports': 0, 'liability': 0, 'imports': []}

    return render_template(
        'cbam.html',
        title='CBAM Uyumluluk',
        manager_available=True,
        stats=stats,
        report=report,
        period=period,
        ets_factors=ets_factors,
    )

@app.route('/cbam/add', methods=['GET', 'POST'])
@require_company_context
def cbam_add():
    if 'user' not in session:
        return redirect(url_for('login'))

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

            product = manager.get_product_by_code(company_id, product_code)
            if not product:
                manager.add_product(
                    company_id,
                    product_code=product_code,
                    product_name=product_code,
                    sector=sector,
                )
                product = manager.get_product_by_code(company_id, product_code)

            if product:
                ok = manager.add_import(
                    company_id,
                    product['id'],
                    origin_country,
                    quantity,
                    total_emissions,
                    carbon_price_paid,
                    offset_type=offset_type,
                    offset_quantity=offset_quantity
                )
                if ok:
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
    if 'user' not in session:
        return redirect(url_for('login'))

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
    
    materiality_data = []
    company_id = g.company_id
    
    try:
        conn = get_db()
        # Create table if not exists (matching basic needs of Manager)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS double_materiality_assessment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                topic_code TEXT NOT NULL,
                topic_name TEXT NOT NULL,
                esrs_reference TEXT,
                impact_materiality_score INTEGER DEFAULT 0,
                financial_materiality_score INTEGER DEFAULT 0,
                impact_rationale TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # Ensure created_at exists
        try:
            conn.execute("ALTER TABLE double_materiality_assessment ADD COLUMN created_at TIMESTAMP")
        except:
            pass

        
        rows = conn.execute("SELECT * FROM double_materiality_assessment WHERE company_id = ? ORDER BY created_at DESC", (company_id,)).fetchall()
        materiality_data = [dict(r) for r in rows]
        conn.close()
    except Exception as e:
        logging.error(f"CSRD module error: {e}")

    return render_template('csrd.html', title='CSRD Raporlama', manager_available=bool(MANAGERS.get('csrd')), materiality=materiality_data)

@app.route('/csrd/materiality', methods=['GET', 'POST'])
@require_company_context
def csrd_materiality():
    if 'user' not in session: return redirect(url_for('login'))
    
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
            
            conn = get_db()
            conn.execute("""
                INSERT INTO double_materiality_assessment 
                (company_id, topic_code, topic_name, impact_materiality_score, financial_materiality_score, impact_rationale, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, code, name, impact, financial, rationale))
            conn.commit()
            conn.close()
            flash('Önemlilik analizi kaydedildi.', 'success')
            return redirect(url_for('csrd_module'))
        except Exception as e:
            logging.error(f"Error adding CSRD data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('csrd_materiality.html', title='Çift Önemlilik Analizi')

@app.route('/taxonomy')
@require_company_context
def taxonomy_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    stats = {
        'turnover': 0, 'turnover_aligned': 0, 'turnover_pct': 0,
        'capex': 0, 'capex_aligned': 0, 'capex_pct': 0,
        'opex': 0, 'opex_aligned': 0, 'opex_pct': 0
    }
    recent_data = []
    company_id = g.company_id
    
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS taxonomy_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                activity_name TEXT NOT NULL,
                nace_code TEXT,
                year INTEGER,
                turnover_amount REAL DEFAULT 0,
                capex_amount REAL DEFAULT 0,
                opex_amount REAL DEFAULT 0,
                eligible_pct REAL DEFAULT 0,
                aligned_pct REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # Fetch all activities
        rows = conn.execute("SELECT * FROM taxonomy_activities WHERE company_id = ? ORDER BY created_at DESC", (company_id,)).fetchall()
        recent_data = [dict(r) for r in rows]
        
        # Calculate stats
        for r in recent_data:
            t = r['turnover_amount'] or 0
            c = r['capex_amount'] or 0
            o = r['opex_amount'] or 0
            align = r['aligned_pct'] or 0
            
            stats['turnover'] += t
            stats['turnover_aligned'] += t * (align / 100.0)
            
            stats['capex'] += c
            stats['capex_aligned'] += c * (align / 100.0)
            
            stats['opex'] += o
            stats['opex_aligned'] += o * (align / 100.0)
            
        if stats['turnover'] > 0:
            stats['turnover_pct'] = round((stats['turnover_aligned'] / stats['turnover']) * 100, 1)
        if stats['capex'] > 0:
            stats['capex_pct'] = round((stats['capex_aligned'] / stats['capex']) * 100, 1)
        if stats['opex'] > 0:
            stats['opex_pct'] = round((stats['opex_aligned'] / stats['opex']) * 100, 1)
            
        conn.close()
    except Exception as e:
        logging.error(f"Taxonomy module error: {e}")

    return render_template('taxonomy.html', title='AB Taksonomisi', manager_available=bool(MANAGERS.get('taxonomy')), stats=stats, recent_data=recent_data)

@app.route('/taxonomy/add', methods=['GET', 'POST'])
@require_company_context
def taxonomy_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            company_id = g.company_id
            year = request.form.get('year')
            name = request.form.get('activity_name')
            nace = request.form.get('nace_code')
            turnover = float(request.form.get('turnover_amount') or 0)
            capex = float(request.form.get('capex_amount') or 0)
            opex = float(request.form.get('opex_amount') or 0)
            eligible = float(request.form.get('eligible_pct') or 0)
            aligned = float(request.form.get('aligned_pct') or 0)
            
            conn = get_db()
            conn.execute("""
                INSERT INTO taxonomy_activities 
                (company_id, year, activity_name, nace_code, turnover_amount, capex_amount, opex_amount, eligible_pct, aligned_pct, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, year, name, nace, turnover, capex, opex, eligible, aligned))
            conn.commit()
            conn.close()
            flash('Taksonomi faaliyeti başarıyla eklendi.', 'success')
            return redirect(url_for('taxonomy_module'))
        except Exception as e:
            logging.error(f"Error adding taxonomy data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('taxonomy_edit.html', title='Taksonomi Veri Girişi')

@app.route('/waste')
@require_company_context
def waste_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {'total_waste': 0, 'recycled_waste': 0}
    recent_data = []
    
    try:
        conn = get_db()
        # Stats
        row = conn.execute("SELECT SUM(amount) FROM waste_generation WHERE company_id = ?", (company_id,)).fetchone()
        if row and row[0]: stats['total_waste'] = row[0]
            
        # Recent Data
        recent_data = conn.execute("SELECT * FROM waste_generation WHERE company_id = ? ORDER BY created_at DESC LIMIT 10", (company_id,)).fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching waste stats: {e}")

    return render_template('waste.html', title='Atık Yönetimi', manager_available=bool(MANAGERS.get('waste')), stats=stats, recent_data=recent_data)

@app.route('/water')
@require_company_context
def water_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {'total_consumption': 0}
    recent_data = []
    
    try:
        conn = get_db()
        # Stats
        row = conn.execute("SELECT SUM(consumption_amount) FROM water_consumption WHERE company_id = ?", (company_id,)).fetchone()
        if row and row[0]: stats['total_consumption'] = row[0]
            
        # Recent Data
        recent_data = conn.execute("SELECT * FROM water_consumption WHERE company_id = ? ORDER BY created_at DESC LIMIT 10", (company_id,)).fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Error fetching water stats: {e}")

    return render_template('water.html', title='Su Yönetimi', manager_available=bool(MANAGERS.get('water')), stats=stats, recent_data=recent_data)

@app.route('/biodiversity')
@require_company_context
def biodiversity_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('biodiversity.html', title='Biyoçeşitlilik', manager_available=bool(MANAGERS.get('biodiversity')))

@app.route('/economic')
@require_company_context
def economic_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    stats = {'revenue': 0, 'climate_impact': 0, 'tax_paid': 0}
    recent_data = []
    company_id = g.company_id
    
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS economic_value_distribution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                revenue REAL NOT NULL,
                operating_costs REAL,
                employee_wages REAL,
                payments_to_capital_providers REAL,
                payments_to_governments REAL,
                community_investments REAL,
                retained_earnings REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS economic_tax (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                corporate_tax REAL,
                payroll_tax REAL,
                vat_collected REAL,
                property_tax REAL,
                other_taxes REAL,
                total_tax REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        row = conn.execute("SELECT SUM(revenue) FROM economic_value_distribution WHERE company_id = ?", (company_id,)).fetchone()
        if row and row[0] is not None:
            stats['revenue'] = row[0]
        
        row = conn.execute("SELECT SUM(total_tax) FROM economic_tax WHERE company_id = ?", (company_id,)).fetchone()
        if row and row[0] is not None:
            stats['tax_paid'] = row[0]

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT total_financial_impact
                FROM tcfd_scenarios
                WHERE company_id = ?
                ORDER BY reporting_year DESC, created_at DESC
                LIMIT 1
            """, (company_id,))
            r = cur.fetchone()
            if r and r[0] is not None:
                stats['climate_impact'] = r[0] * 1_000_000
        except Exception as e:
            logging.error(f"Error fetching TCFD financial impact for economic stats: {e}")
            
        try:
            rows = conn.execute("SELECT * FROM economic_value_distribution WHERE company_id = ? ORDER BY created_at DESC LIMIT 5", (company_id,)).fetchall()
            for r in rows:
                recent_data.append({
                    'data_type': 'revenue',
                    'amount': r['revenue'],
                    'year': r['year'],
                    'description': 'Ekonomik Değer Dağılımı',
                    'created_at': r['created_at']
                })
                
            conn.execute("""
                CREATE TABLE IF NOT EXISTS financial_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_assets REAL,
                    total_liabilities REAL,
                    net_profit REAL,
                    ebitda REAL,
                    return_on_equity REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            fp_rows = conn.execute("SELECT * FROM financial_performance WHERE company_id = ? ORDER BY created_at DESC LIMIT 5", (company_id,)).fetchall()
            for r in fp_rows:
                recent_data.append({
                    'data_type': 'risk',
                    'amount': r['net_profit'],
                    'year': r['year'],
                    'description': 'Net Kâr',
                    'created_at': r['created_at']
                })
            
            tax_rows = conn.execute("SELECT * FROM economic_tax WHERE company_id = ? ORDER BY created_at DESC LIMIT 5", (company_id,)).fetchall()
            for r in tax_rows:
                recent_data.append({
                    'data_type': 'tax',
                    'amount': r['total_tax'],
                    'year': r['year'],
                    'description': 'Toplam Vergi',
                    'created_at': r['created_at']
                })
                
            recent_data.sort(key=lambda x: x['created_at'], reverse=True)
            recent_data = recent_data[:10]
        except Exception as e:
            logging.error(f"Error fetching economic recent data: {e}")

        conn.close()
    except Exception as e:
        logging.error(f"Error in economic module: {e}")

    return render_template('economic.html', title='Ekonomik Performans', manager_available=bool(MANAGERS.get('economic')), stats=stats, recent_data=recent_data)

@app.route('/economic/add', methods=['GET', 'POST'])
@require_company_context
def economic_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_type = request.args.get('type', 'value_distribution')
    if data_type == 'revenue':
        data_type = 'value_distribution'
    elif data_type == 'risk':
        data_type = 'financial_performance'
    
    if request.method == 'POST':
        try:
            dtype = request.form.get('data_type') or data_type
            if dtype == 'revenue':
                dtype = 'value_distribution'
            elif dtype == 'risk':
                dtype = 'financial_performance'
            company_id = g.company_id
            conn = get_db()
            
            if dtype == 'value_distribution':
                year = request.form.get('year')
                rev = request.form.get('revenue')
                op_costs = request.form.get('operating_costs') or 0
                wages = request.form.get('employee_wages') or 0
                caps = request.form.get('payments_capital') or 0
                govs = request.form.get('payments_gov') or 0
                comm = request.form.get('community_investments') or 0
                
                # Ensure table exists
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS economic_value_distribution (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        year INTEGER NOT NULL,
                        revenue REAL NOT NULL,
                        operating_costs REAL,
                        employee_wages REAL,
                        payments_to_capital_providers REAL,
                        payments_to_governments REAL,
                        community_investments REAL,
                        retained_earnings REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    INSERT INTO economic_value_distribution 
                    (company_id, year, revenue, operating_costs, employee_wages, payments_to_capital_providers, payments_to_governments, community_investments) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (company_id, year, rev, op_costs, wages, caps, govs, comm))
                
            elif dtype == 'financial_performance':
                year = 2024 # Default or from form if added later
                assets = request.form.get('total_assets') or 0
                liabs = request.form.get('total_liabilities') or 0
                net = request.form.get('net_profit') or 0
                ebitda = request.form.get('ebitda') or 0
                roe = request.form.get('roe') or 0
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS financial_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        year INTEGER NOT NULL,
                        total_assets REAL,
                        total_liabilities REAL,
                        net_profit REAL,
                        ebitda REAL,
                        return_on_equity REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    INSERT INTO financial_performance 
                    (company_id, year, total_assets, total_liabilities, net_profit, ebitda, return_on_equity) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (company_id, year, assets, liabs, net, ebitda, roe))
            elif dtype == 'tax':
                year = int(request.form.get('year', 2024))
                corporate_tax = float(request.form.get('corporate_tax') or 0)
                payroll_tax = float(request.form.get('payroll_tax') or 0)
                vat_collected = float(request.form.get('vat_collected') or 0)
                property_tax = float(request.form.get('property_tax') or 0)
                other_taxes = float(request.form.get('other_taxes') or 0)
                total_tax = corporate_tax + payroll_tax + vat_collected + property_tax + other_taxes
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS economic_tax (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        year INTEGER NOT NULL,
                        corporate_tax REAL,
                        payroll_tax REAL,
                        vat_collected REAL,
                        property_tax REAL,
                        other_taxes REAL,
                        total_tax REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    INSERT INTO economic_tax 
                    (company_id, year, corporate_tax, payroll_tax, vat_collected, property_tax, other_taxes, total_tax) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (company_id, year, corporate_tax, payroll_tax, vat_collected, property_tax, other_taxes, total_tax))
                
            conn.commit()
            conn.close()
            flash('Ekonomik veri başarıyla eklendi.', 'success')
            return redirect(url_for('economic_module'))
            
        except Exception as e:
            logging.error(f"Error adding economic data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('economic_edit.html', title='Ekonomik Veri Girişi', data_type=data_type)

@app.route('/supply_chain')
@require_company_context
def supply_chain_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    stats = {
        'total_suppliers': 0,
        'avg_score': 0,
        'high_risk_count': 0
    }
    suppliers = []
    company_id = g.company_id
    
    try:
        conn = get_db()
        # Create table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                supplier_name TEXT NOT NULL,
                supplier_type TEXT NOT NULL,
                country TEXT,
                certification_status TEXT,
                sustainability_score REAL,
                risk_level TEXT,
                last_assessment_date TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # Stats
        row = conn.execute("SELECT COUNT(*), AVG(sustainability_score) FROM suppliers WHERE company_id = ? AND status = 'active'", (company_id,)).fetchone()
        if row:
            stats['total_suppliers'] = row[0]
            stats['avg_score'] = round(row[1], 1) if row[1] else 0
            
        row = conn.execute("SELECT COUNT(*) FROM suppliers WHERE company_id = ? AND risk_level = 'high'", (company_id,)).fetchone()
        if row:
            stats['high_risk_count'] = row[0]
            
        # List
        rows = conn.execute("SELECT * FROM suppliers WHERE company_id = ? ORDER BY created_at DESC", (company_id,)).fetchall()
        suppliers = []
        for r in rows:
            suppliers.append({
                'name': r['supplier_name'],
                'type': r['supplier_type'],
                'country': r['country'],
                'score': r['sustainability_score'],
                'risk': r['risk_level']
            })
            
        conn.close()
    except Exception as e:
        logging.error(f"Supply Chain module error: {e}")

    return render_template('supply_chain.html', title='Tedarik Zinciri', manager_available=bool(MANAGERS.get('supply_chain')), stats=stats, suppliers=suppliers)

@app.route('/supply_chain/add', methods=['GET', 'POST'])
@require_company_context
def supply_chain_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            company_id = g.company_id
            name = request.form.get('supplier_name')
            stype = request.form.get('supplier_type')
            country = request.form.get('country')
            score = float(request.form.get('score') or 0)
            risk = request.form.get('risk_level')
            
            conn = get_db()
            conn.execute("""
                INSERT INTO suppliers 
                (company_id, supplier_name, supplier_type, country, sustainability_score, risk_level, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, name, stype, country, score, risk))
            conn.commit()
            conn.close()
            
            flash('Tedarikçi başarıyla eklendi.', 'success')
            return redirect(url_for('supply_chain_module'))
        except Exception as e:
            logging.error(f"Error adding supplier: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('supply_chain_edit.html', title='Tedarikçi Ekle')

@app.route('/cdp')
@require_company_context
def cdp_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {}
    submissions = []
    manager = MANAGERS.get('cdp')
    
    if manager:
        try:
            # Calculate scores for each questionnaire type
            for q_type in ['Climate Change', 'Water Security', 'Forests']:
                scores = manager.calculate_scores(q_type, company_id, 2024)
                # Map to template keys (climate_score, water_score, forests_score)
                if q_type == 'Climate Change':
                    key = 'climate_score'
                elif q_type == 'Water Security':
                    key = 'water_score'
                else:
                    key = 'forests_score'
                
                stats[key] = scores.get('total_score', 0)
                
                # Check for submissions
                responses = manager.get_company_responses(q_type, company_id, 2024)
                if responses:
                    filled = sum(1 for r in responses if r.get('response'))
                    total = len(responses)
                    pct = int((filled / total * 100)) if total > 0 else 0
                    submissions.append({
                        'module_type': q_type,
                        'year': 2024,
                        'status': 'Tamamlandı' if pct == 100 else 'Devam Ediyor',
                        'score': scores.get('grade', 'D')
                    })
        except Exception as e:
            logging.error(f"CDP stats error: {e}")
            
    return render_template('cdp.html', title='CDP Raporlama', manager_available=bool(manager), stats=stats, submissions=submissions)

@app.route('/issb')
@require_company_context
def issb_module():
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
            CREATE TABLE IF NOT EXISTS issb_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER,
                standard TEXT,
                disclosure TEXT,
                metric TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # Fetch data
        rows = conn.execute("SELECT * FROM issb_data WHERE company_id = ? ORDER BY created_at DESC", (company_id,)).fetchall()
        standards = [dict(r) for r in rows]
        
        # Calculate stats
        stats['total_disclosures'] = len(standards)
        stats['standards_covered'] = len(set([s['standard'] for s in standards])) if standards else 0
        
        # Mock completion rate (assuming target is ~20 key disclosures)
        stats['completion_rate'] = min(100, int((stats['total_disclosures'] / 20) * 100))
        
        conn.close()
    except Exception as e:
        logging.error(f"ISSB module error: {e}")

    return render_template('issb.html', title='ISSB Standartları', manager_available=bool(MANAGERS.get('issb')), stats=stats, standards=standards)

@app.route('/issb/add', methods=['GET', 'POST'])
@require_company_context
def issb_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            year = request.form.get('year')
            standard = request.form.get('standard')
            disclosure = request.form.get('disclosure')
            metric = request.form.get('metric')
            company_id = g.company_id
            
            conn = get_db()
            conn.execute("""
                INSERT INTO issb_data (company_id, year, standard, disclosure, metric)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, year, standard, disclosure, metric))
            conn.commit()
            conn.close()
            
            flash('ISSB verisi başarıyla eklendi.', 'success')
            return redirect(url_for('issb_module'))
        except Exception as e:
            logging.error(f"ISSB add error: {e}")
            flash('Bir hata oluştu.', 'danger')
            
    return render_template('issb_edit.html', title='ISSB Veri Girişi')

@app.route('/iirc')
@require_company_context
def iirc_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('iirc.html', title='Entegre Raporlama (IIRC)', manager_available=bool(MANAGERS.get('iirc')))

@app.route('/esrs')
@require_company_context
def esrs_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {'covered_standards': 0, 'completion_rate': 0}
    materiality_items = []
    
    standards = [
        {'code': 'ESRS 1', 'title': 'General Requirements', 'category': 'Cross-cutting'},
        {'code': 'ESRS 2', 'title': 'General Disclosures', 'category': 'Cross-cutting'},
        {'code': 'E1', 'title': 'Climate Change', 'category': 'Environmental'},
        {'code': 'E2', 'title': 'Pollution', 'category': 'Environmental'},
        {'code': 'E3', 'title': 'Water and Marine Resources', 'category': 'Environmental'},
        {'code': 'E4', 'title': 'Biodiversity and Ecosystems', 'category': 'Environmental'},
        {'code': 'E5', 'title': 'Resource Use and Circular Economy', 'category': 'Environmental'},
        {'code': 'S1', 'title': 'Own Workforce', 'category': 'Social'},
        {'code': 'S2', 'title': 'Workers in the Value Chain', 'category': 'Social'},
        {'code': 'S3', 'title': 'Affected Communities', 'category': 'Social'},
        {'code': 'S4', 'title': 'Consumers and End-users', 'category': 'Social'},
        {'code': 'G1', 'title': 'Business Conduct', 'category': 'Governance'}
    ]
    
    manager = MANAGERS.get('esrs')
    if manager:
        try:
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
        except Exception as e:
            logging.error(f"ESRS stats error: {e}")
            
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
    stats = {}
    financial_impacts = []
    manager = MANAGERS.get('tcfd')
    
    if manager:
        try:
            gov = manager.get_governance(company_id, 2024)
            strat = manager.get_strategy(company_id, 2024)
            metrics = manager.get_metrics(company_id, 2024)
            
            # Simple progress calculation
            stats['governance_score'] = 100 if gov else 0
            stats['strategy_score'] = 100 if strat else 0
            stats['metrics_score'] = 100 if metrics else 0
            
            # Risk Management Score (check if any risk data exists in strategy)
            stats['risk_score'] = 0
            
            # Populate stats for template
            stats['total_risks'] = 0
            stats['total_opps'] = 0
            stats['financial_impact'] = '0 TL'
            
            if strat:
                if strat.get('short_term_risks'): stats['total_risks'] += 1
                if strat.get('medium_term_risks'): stats['total_risks'] += 1
                if strat.get('long_term_risks'): stats['total_risks'] += 1
                
                if strat.get('short_term_opportunities'): stats['total_opps'] += 1
                if strat.get('medium_term_opportunities'): stats['total_opps'] += 1
                if strat.get('long_term_opportunities'): stats['total_opps'] += 1
                
                if strat.get('financial_impact'): stats['financial_impact'] = strat.get('financial_impact')
                
                if stats['total_risks'] > 0:
                     stats['risk_score'] = 100

            # Financial Impacts from new table
            financial_impacts = manager.get_financial_impacts(company_id)
            if financial_impacts:
                total_impact = sum([float(i['financial_impact'] or 0) for i in financial_impacts])
                stats['financial_impact'] = f"{total_impact:,.0f}"
                 
        except Exception as e:
            logging.error(f"TCFD stats error: {e}")
            
    return render_template('tcfd.html', title='TCFD İklim Riskleri', manager_available=bool(manager), stats=stats, recommendations=[], financial_impacts=financial_impacts)

@app.route('/tnfd')
@require_company_context
def tnfd_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {}
    manager = MANAGERS.get('tnfd')
    
    if manager:
        try:
            stats = manager.get_stats(company_id, 2024)
        except Exception as e:
            logging.error(f"TNFD stats error: {e}")
            
    return render_template('tnfd.html', title='TNFD Doğa İlişkili Beyanlar', manager_available=bool(manager), stats=stats, recommendations=[])

@app.route('/tcfd/add', methods=['GET', 'POST'])
@require_company_context
def tcfd_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        flash('Veriler başarıyla kaydedildi.', 'success')
        return redirect(url_for('tcfd_module'))
        
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
        flash('Veriler başarıyla kaydedildi.', 'success')
        return redirect(url_for('tnfd_module'))
        
    return render_template('tnfd_edit.html', title='TNFD Veri Girişi')

@app.route('/cdp/add', methods=['GET', 'POST'])
@require_company_context
def cdp_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            year = request.form.get('year')
            module_type = request.form.get('module_type')
            score = request.form.get('score')
            status = request.form.get('status')
            company_id = g.company_id
            
            conn = get_db()
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cdp_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER,
                    module_type TEXT,
                    score TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            conn.execute("INSERT INTO cdp_responses (company_id, year, module_type, score, status) VALUES (?, ?, ?, ?, ?)", 
                         (company_id, year, module_type, score, status))
            conn.commit()
            conn.close()
            
            flash('Veriler başarıyla kaydedildi.', 'success')
            return redirect(url_for('cdp_module'))
        except Exception as e:
            logging.error(f"CDP add error: {e}")
            flash('Hata oluştu.', 'danger')
        
    return render_template('cdp_edit.html', title='CDP Veri Girişi')

@app.route('/cdp/settings')
@require_company_context
def cdp_settings():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('cdp')
    if not manager:
        flash('Modül aktif değil', 'warning')
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
        flash('Ayarlar güncellendi', 'success')
    else:
        flash('Hata oluştu', 'danger')
        
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
                
    flash(f'{updated_count} ağırlık güncellendi', 'success')
    return redirect(url_for('cdp_settings'))

@app.route('/cdp/settings/reset', methods=['POST'])
@require_company_context
def cdp_settings_reset():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    manager = MANAGERS.get('cdp')
    
    if manager and manager.reset_weights_to_standard(company_id, 2024):
        flash('Ağırlıklar standart değerlere sıfırlandı', 'success')
    else:
        flash('Hata oluştu', 'danger')
        
    return redirect(url_for('cdp_settings'))

# --- Migrated Routes for SaaS ---

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
    ]
}

# Helper to load stakeholder groups
def load_stakeholder_groups():
    groups = {}
    try:
        import json
        import os
        json_path = os.path.join(BACKEND_DIR, 'data', 'stakeholder_questions.json')
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, val in data.items():
                    groups[key] = val['name']
    except Exception as e:
        logging.error(f"Error loading stakeholder questions: {e}")
    return groups

@app.route('/surveys')
@require_company_context
def surveys_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    stats = {}
    records = []
    columns = ['survey_title', 'status', 'response_count', 'created_at']
    
    stakeholder_groups = load_stakeholder_groups()

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

@app.route('/surveys/add', methods=['POST'])
@require_company_context
def add_survey():
    if 'user' not in session: return redirect(url_for('login'))
    
    company_id = g.company_id
    title = request.form.get('survey_title')
    desc = request.form.get('survey_description')
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
                json_path = os.path.join(BACKEND_DIR, 'data', 'stakeholder_questions.json')
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
                    t_cursor = conn.execute("SELECT * FROM survey_template_questions WHERE template_id=?", (template_id,))
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
        
        conn.commit()
        conn.close()
        flash('Anket başarıyla oluşturuldu.', 'success')
    except Exception as e:
        logging.error(f"Error adding survey: {e}")
        flash('Anket oluşturulurken hata oluştu.', 'error')
        
    return redirect(url_for('surveys_module'))

@app.route('/surveys/<int:survey_id>')
@require_company_context
def survey_detail(survey_id):
    if 'user' not in session: return redirect(url_for('login'))
    company_id = g.company_id
    
    stakeholder_groups = load_stakeholder_groups()

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
    
    questions = []
    for row in rows:
        q = dict(row)
        if 'category' not in q: q['category'] = 'General'
        if 'question_type' not in q: q['question_type'] = 'scale_1_5'
        if 'is_required' not in q: q['is_required'] = 1
        questions.append(q)
    
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
        
        # Update total questions count
        conn.execute("UPDATE online_surveys SET total_questions = total_questions + ? WHERE id=? AND company_id=?", (count, survey_id, company_id))
        
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

@app.route('/survey/<token>', methods=['GET', 'POST'])
def public_survey(token):
    try:
        conn = get_db()
        
        # Anket var mı kontrol et
        # Check for both exact path and full URL match (ending with token)
        row = conn.execute("SELECT * FROM online_surveys WHERE (survey_link = ? OR survey_link LIKE ?) AND is_active = 1", (f"/survey/{token}", f"%/{token}")).fetchone()
        
        if not row:
            conn.close()
            return render_template('404.html'), 404
            
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
                            
                # Update response count
                conn.execute("UPDATE online_surveys SET response_count = response_count + 1 WHERE id=? AND company_id=?", (survey['id'], survey['company_id']))
                
                conn.commit()
                return render_template('survey_thank_you.html')
                
            except Exception as e:
                logging.error(f"Error submitting survey: {e}")
                conn.rollback()
                flash('Anket gönderilirken hata oluştu.', 'error')
        
        conn.close()
        
        return render_template('public_survey.html', survey=survey, questions=questions_by_category, demographics=demographics, stakeholder_groups=load_stakeholder_groups())
        
    except Exception as e:
        logging.error(f"Error in public survey: {e}")
        return render_template('404.html'), 404

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

@app.route('/targets_module')
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
    
    try:
        from backend.modules.reporting.target_manager import TargetManager
        data = {
            'name': request.form.get('name'),
            'metric_type': request.form.get('metric_type'),
            'baseline_year': request.form.get('baseline_year'),
            'baseline_value': float(request.form.get('baseline_value') or 0),
            'target_year': request.form.get('target_year'),
            'target_value': float(request.form.get('target_value') or 0)
        }
        
        tm = TargetManager(DB_PATH)
        tm.add_target(company_id, data)
        
        flash('Hedef başarıyla eklendi.', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
        
    return redirect(url_for('targets_module'))

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
    
    return render_template(
        'super_admin.html',
        title='Super Admin Paneli',
        stats=stats,
        rate_stats=rate_stats,
        ip_available=IP_MANAGER_AVAILABLE,
        monitoring_available=MONITORING_AVAILABLE,
        license_available=LICENSE_MANAGER_AVAILABLE
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
            keys = [
                'rl_login_limit',
                'rl_login_window',
                'rl_api_limit',
                'rl_api_window',
                'rl_report_limit',
                'rl_report_window',
                'rl_export_limit',
                'rl_export_window',
            ]
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
        keys = [
            'rl_login_limit',
            'rl_login_window',
            'rl_api_limit',
            'rl_api_window',
            'rl_report_limit',
            'rl_report_window',
            'rl_export_limit',
            'rl_export_window',
        ]
        for k in keys:
            cur.execute(
                "SELECT value FROM system_settings WHERE key=? AND company_id=?",
                (k, company_id),
            )
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
        current_rules=current_rules,
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
        title='Sistem İstatistikleri',
        stats=stats
    )


@app.route('/super_admin/modules', methods=['GET', 'POST'])
@super_admin_required
def super_admin_modules():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    try:
        companies = conn.execute(
            "SELECT id, name FROM companies ORDER BY name"
        ).fetchall()
    except Exception:
        companies = []
    if not companies:
        conn.close()
        flash('Sistemde tanımlı firma bulunamadı.', 'warning')
        return redirect(url_for('super_admin_panel'))
    selected_company_id = request.values.get('company_id')
    if selected_company_id:
        try:
            selected_company_id = int(selected_company_id)
        except ValueError:
            selected_company_id = companies[0]['id']
    else:
        selected_company_id = companies[0]['id']
    modules = []
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                m.id,
                m.module_code,
                m.module_name,
                m.category,
                m.is_core,
                COALESCE(cm.is_enabled, m.default_enabled) AS is_enabled
            FROM modules m
            LEFT JOIN company_modules cm 
                ON m.id = cm.module_id AND cm.company_id = ?
            ORDER BY m.display_order, m.module_name
            """,
            (selected_company_id,),
        )
        modules = cur.fetchall()
        if request.method == 'POST':
            selected_codes = request.form.getlist('module_codes')
            cur.execute(
                """
                SELECT id, module_code, is_core, default_enabled 
                FROM modules
                ORDER BY display_order, module_name
                """
            )
            all_modules = cur.fetchall()
            cur.execute(
                """
                SELECT module_id, is_enabled 
                FROM company_modules
                WHERE company_id = ?
                """,
                (selected_company_id,),
            )
            existing = {row['module_id']: row['is_enabled'] for row in cur.fetchall()}
            for mod in all_modules:
                module_id = mod['id']
                module_code = mod['module_code']
                is_core = mod['is_core']
                if is_core:
                    is_enabled = 1
                else:
                    is_enabled = 1 if module_code in selected_codes else 0
                if module_id in existing:
                    cur.execute(
                        """
                        UPDATE company_modules
                        SET is_enabled = ?
                        WHERE company_id = ? AND module_id = ?
                        """,
                        (is_enabled, selected_company_id, module_id),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO company_modules (company_id, module_id, is_enabled)
                        VALUES (?, ?, ?)
                        """,
                        (selected_company_id, module_id, is_enabled),
                    )
            conn.commit()
            flash('Modül ayarları güncellendi.', 'success')
            return redirect(url_for('super_admin_modules', company_id=selected_company_id))
    except Exception as e:
        logging.error(f"Super admin module config error: {e}")
        flash('Modül ayarları yüklenirken bir hata oluştu.', 'danger')
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return render_template(
        'super_admin_modules.html',
        title='Modül Yönetimi',
        companies=companies,
        selected_company_id=selected_company_id,
        modules=modules,
    )

@app.route('/super_admin/tests')
@super_admin_required
@require_company_context
def super_admin_tests():
    import os

    if 'user' not in session:
        return redirect(url_for('login'))
    test_files = []
    legacy_tests = {
        'connectivity': {'path': 'tests/test_connectivity.py', 'name': 'Bağlantı Testi'},
        'performance': {'path': 'tests/test_database_performance.py', 'name': 'Veritabanı Performans Testi'},
        'users': {'path': 'tests/test_user_management.py', 'name': 'Kullanıcı Yönetimi Testi'},
        'reporting': {'path': 'tests/test_reporting.py', 'name': 'Raporlama Testi'},
        'email': {'path': 'tests/test_email_service.py', 'name': 'E-posta Servis Testi'},
    }
    for key, info in legacy_tests.items():
        if os.path.exists(os.path.join(BASE_DIR, info['path'])):
            test_files.append(
                {
                    'id': key,
                    'name': info['name'],
                    'path': info['path'],
                    'category': 'Sistem Testleri',
                }
            )
    testler_dir = os.path.join(BASE_DIR, 'TESTLER')
    if os.path.exists(testler_dir):
        for filename in os.listdir(testler_dir):
            if filename.endswith('.py'):
                file_path = os.path.join('TESTLER', filename)
                test_id = filename
                test_name = filename.replace('.py', '').replace('_', ' ').title()
                test_files.append(
                    {
                        'id': test_id,
                        'name': test_name,
                        'path': file_path,
                        'category': 'TESTLER',
                    }
                )
    return render_template('super_admin_tests.html', tests=test_files)

@app.route('/super_admin/run_test/<test_id>', methods=['POST'])
@super_admin_required
@require_company_context
def super_admin_run_test(test_id: str):
    import subprocess
    import sys
    import os

    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Oturum bulunamadı'})
    test_path = None
    legacy_tests = {
        'connectivity': {'path': 'tests/test_connectivity.py', 'name': 'Bağlantı Testi'},
        'performance': {'path': 'tests/test_database_performance.py', 'name': 'Veritabanı Performans Testi'},
        'users': {'path': 'tests/test_user_management.py', 'name': 'Kullanıcı Yönetimi Testi'},
        'reporting': {'path': 'tests/test_reporting.py', 'name': 'Raporlama Testi'},
        'email': {'path': 'tests/test_email_service.py', 'name': 'E-posta Servis Testi'},
    }
    if test_id in legacy_tests:
        test_path = os.path.join(BASE_DIR, legacy_tests[test_id]['path'])
    elif test_id.endswith('.py'):
        potential_path = os.path.join(BASE_DIR, 'TESTLER', test_id)
        if os.path.exists(potential_path) and os.path.isfile(potential_path):
            test_path = potential_path
    if not test_path or not os.path.exists(test_path):
        return jsonify({'success': False, 'error': f'Test dosyası bulunamadı: {test_id}'})
    try:
        cmd = [sys.executable, test_path]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=BASE_DIR,
        )
        out, err = proc.communicate(timeout=300)
        return jsonify(
            {
                'success': proc.returncode == 0,
                'returncode': proc.returncode,
                'stdout': out.decode(errors='replace'),
                'stderr': err.decode(errors='replace'),
            }
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/super_admin/ip')
@super_admin_required
@require_company_context
def super_admin_ip():
    if 'user' not in session:
        return redirect(url_for('login'))
    flash('IP yönetimi özelliği henüz aktif değil.', 'warning')
    return redirect(url_for('super_admin_panel'))

@app.route('/super_admin/monitoring')
@super_admin_required
def super_admin_monitoring():
    if 'user' not in session:
        return redirect(url_for('login'))
    flash('Monitoring özelliği henüz aktif değil.', 'warning')
    return redirect(url_for('super_admin_panel'))

@app.route('/super_admin/system_logs')
@super_admin_required
@require_company_context
def super_admin_system_logs():
    if 'user' not in session:
        return redirect(url_for('login'))
    flash('Sistem logları ekranı henüz aktif değil.', 'warning')
    return redirect(url_for('super_admin_panel'))

@app.route('/super_admin/twofa')
@super_admin_required
@require_company_context
def super_admin_twofa():
    if 'user' not in session:
        return redirect(url_for('login'))
    flash('2FA yönetimi henüz aktif değil.', 'warning')
    return redirect(url_for('super_admin_panel'))

@app.route('/super_admin/backup')
@super_admin_required
@require_company_context
def super_admin_backup():
    if 'user' not in session:
        return redirect(url_for('login'))
    flash('Yedekleme ekranı henüz aktif değil.', 'warning')
    return redirect(url_for('super_admin_panel'))

@app.route('/super_admin/performance', methods=['GET', 'POST'])
@super_admin_required
@require_company_context
def super_admin_performance():
    if 'user' not in session:
        return redirect(url_for('login'))
    flash('Performans ekranı henüz aktif değil.', 'warning')
    return redirect(url_for('super_admin_panel'))

@app.route('/super_admin/settings')
@super_admin_required
@require_company_context
def super_admin_settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    flash('Sistem ayarları ekranı henüz aktif değil.', 'warning')
    return redirect(url_for('super_admin_panel'))

@app.route('/super_admin/maintenance')
@super_admin_required
@require_company_context
def super_admin_maintenance():
    if 'user' not in session:
        return redirect(url_for('login'))
    flash('Bakım ve onarım ekranı henüz aktif değil.', 'warning')
    return redirect(url_for('super_admin_panel'))

@app.route('/super_admin/security')
@super_admin_required
@require_company_context
def super_admin_security():
    if 'user' not in session:
        return redirect(url_for('login'))
    flash('Güvenlik ayarları ekranı henüz aktif değil.', 'warning')
    return redirect(url_for('super_admin_panel'))

@app.route('/super_admin/audit_logs')
@super_admin_required
@require_company_context
def super_admin_audit_logs():
    if 'user' not in session:
        return redirect(url_for('login'))
    logs: list[Dict[str, str]] = []
    try:
        conn = get_db()
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
        
        # Enforce Company Isolation
        # Try to use company_id column if available, otherwise fallback to JOIN
        try:
            cursor.execute("PRAGMA table_info(audit_logs)")
            cols = [c[1] for c in cursor.fetchall()]
            
            if 'company_id' in cols:
                # Use company_id column directly (more reliable)
                cursor.execute("""
                    SELECT id, username, action, timestamp, details 
                    FROM audit_logs
                    WHERE company_id = ?
                    ORDER BY id DESC LIMIT 100
                """, (g.company_id,))
            else:
                # Fallback to JOIN if column missing (should not happen after fix script)
                cursor.execute("""
                    SELECT al.id, al.username, al.action, al.timestamp, al.details 
                    FROM audit_logs al
                    JOIN users u ON al.user_id = u.id
                    WHERE u.company_id = ?
                    ORDER BY al.id DESC LIMIT 100
                """, (g.company_id,))
        except Exception as e:
            # Fallback in case of error
             cursor.execute("""
                SELECT al.id, al.username, al.action, al.timestamp, al.details 
                FROM audit_logs al
                JOIN users u ON al.user_id = u.id
                WHERE u.company_id = ?
                ORDER BY al.id DESC LIMIT 100
            """, (g.company_id,))
        
        rows = cursor.fetchall()
        for row in rows:
            logs.append({
                'id': row[0],
                'username': row[1] or 'Sistem',
                'action': row[2] or 'Bilinmiyor',
                'timestamp': row[3] or '',
                'details': row[4] or ''
            })
        conn.close()
    except Exception as e:
        logging.error(f"Super admin audit logs error: {e}")
    return render_template(
        'super_admin_audit_logs.html',
        title='Audit Logları',
        logs=logs
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
                contact_phone,
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
        generated_result=generated_result,
    )

# --- Legal & Compliance Routes ---
@app.route('/legal/privacy')
def legal_privacy():
    return render_template('legal/privacy.html', title='Gizlilik Politikası')

@app.route('/legal/sla')
def legal_sla():
    return render_template('legal/sla.html', title='Hizmet Seviyesi Anlaşması')

@app.route('/legal/dpa')
def legal_dpa():
    return render_template('legal/dpa.html', title='Veri İşleme Sözleşmesi')

# Supplier Portal Blueprint
# try:
#     from modules.supplier_portal import supplier_portal_bp
#     app.register_blueprint(supplier_portal_bp)
# except Exception as e:
#     logging.error(f"Supplier Portal Blueprint registration error: {e}")

def check_and_migrate_schema():
    """Checks and migrates database schema on startup"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 1. Audit Logs Migration
        try:
            cursor.execute("PRAGMA table_info(audit_logs)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'company_id' not in cols:
                logging.info("Migrating audit_logs: Adding company_id column")
                cursor.execute("ALTER TABLE audit_logs ADD COLUMN company_id INTEGER DEFAULT NULL")
                conn.commit()
        except Exception as e:
            logging.error(f"Schema migration error (audit_logs): {e}")

        # 2. System Settings Migration
        try:
            cursor.execute("PRAGMA table_info(system_settings)")
            cols = [c[1] for c in cursor.fetchall()]
            if cols and 'company_id' not in cols:
                logging.info("Migrating system_settings: Adding company_id column")
                cursor.execute("ALTER TABLE system_settings ADD COLUMN company_id INTEGER DEFAULT 1")
                cursor.execute("UPDATE system_settings SET company_id = 1 WHERE company_id IS NULL")
                conn.commit()
        except Exception as e:
            logging.error(f"Schema migration error (system_settings): {e}")

        # 3. SDG Goals Migration
        try:
            cursor.execute("PRAGMA table_info(sdg_goals)")
            cols = [c[1] for c in cursor.fetchall()]
            if cols and 'company_id' not in cols:
                logging.info("Migrating sdg_goals: Adding company_id column")
                cursor.execute("ALTER TABLE sdg_goals ADD COLUMN company_id INTEGER DEFAULT 1")
                cursor.execute("UPDATE sdg_goals SET company_id = 1 WHERE company_id IS NULL")
                conn.commit()
        except Exception as e:
            logging.error(f"Schema migration error (sdg_goals): {e}")

        # 4. Survey Templates Migration
        try:
            cursor.execute("PRAGMA table_info(survey_templates)")
            cols = [c[1] for c in cursor.fetchall()]
            if cols and 'company_id' not in cols:
                logging.info("Migrating survey_templates: Adding company_id column")
                cursor.execute("ALTER TABLE survey_templates ADD COLUMN company_id INTEGER DEFAULT NULL")
                conn.commit()
        except Exception as e:
            logging.error(f"Schema migration error (survey_templates): {e}")

        # 5. Survey Questions Migration
        try:
            cursor.execute("PRAGMA table_info(survey_questions)")
            cols = [c[1] for c in cursor.fetchall()]
            if cols and 'company_id' not in cols:
                logging.info("Migrating survey_questions: Adding company_id column")
                cursor.execute("ALTER TABLE survey_questions ADD COLUMN company_id INTEGER")
                # Populate company_id from online_surveys
                cursor.execute("""
                    UPDATE survey_questions
                    SET company_id = (
                        SELECT company_id 
                        FROM online_surveys 
                        WHERE online_surveys.id = survey_questions.survey_id
                    )
                    WHERE survey_id IN (SELECT id FROM online_surveys)
                """)
                conn.commit()
        except Exception as e:
            logging.error(f"Schema migration error (survey_questions): {e}")

        conn.close()
    except Exception as e:
        logging.error(f"Database connection error during migration: {e}")

if __name__ == '__main__':
    # Run schema checks
    check_and_migrate_schema()
    
    # Production'da debug=False olmalı
    is_debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=is_debug)
