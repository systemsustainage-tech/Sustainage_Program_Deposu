"""
Uygulama ayarları
"""

import logging
from pathlib import Path

# Temel dizinler
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
EXPORT_DIR = BASE_DIR / 'exports'
REPORTS_DIR = BASE_DIR / 'reports'
LOGS_DIR = BASE_DIR / 'logs'
UPLOADS_DIR = BASE_DIR / 'uploads'

# Database
DATABASE_PATH = DATA_DIR / 'sdg_desktop.sqlite'
DATABASE_TIMEOUT = 30  # saniye

# Cache ayarları
CACHE_ENABLED = True
CACHE_TTL = 300  # 5 dakika (saniye)
USER_PERMISSIONS_CACHE_TTL = 600  # 10 dakika
QUERY_CACHE_TTL = 180  # 3 dakika

# Performans ayarları
LAZY_LOADING_ENABLED = True
ASYNC_IMAGE_LOADING = True
ASYNC_SETTINGS_LOADING = True
ASYNC_PERMISSIONS_LOADING = True

# GUI ayarları
DEFAULT_DASHBOARD_VARIANT = 'classic'  # 'classic' veya 'experimental'
DEFAULT_DASHBOARD_IMAGE_MODE = 'cover'  # 'cover', 'contain', 'fill'
SHOW_WELCOME_BANNER = True

# Güvenlik ayarları
PASSWORD_MIN_LENGTH = 6
PASSWORD_HASH_ALGORITHM = 'sha256'
SESSION_TIMEOUT = 3600  # 1 saat (saniye)
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 dakika

# Audit ayarları
AUDIT_ENABLED = True
AUDIT_RETENTION_DAYS = 365  # 1 yıl

# Rapor ayarları
REPORT_EXPORT_FORMATS = ['pdf', 'excel', 'word', 'pptx']
REPORT_TEMPLATE_DIR = BASE_DIR / 'templates' / 'reports'
DEFAULT_REPORT_LANGUAGE = 'tr'

# E-posta ayarları
EMAIL_ENABLED = False  # Varsayılan olarak kapalı
SMTP_CONFIG_FILE = BASE_DIR / 'config' / 'smtp_config.json'

# Logging ayarları
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Modül ayarları
ENABLED_MODULES = [
    'dashboard',
    'sdg',
    'gri',
    'tsrs',
    'esg',
    'skdm',
    'strategic',
    'reports',
    'management',
    'tasks',
    'surveys',
    'innovation',
    'quality',
    'digital_security',
    'emergency',
]

# UI ayarları
UI_COLORS = {
    'primary': '#1e40af',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#3498db',
    'secondary': '#7f8c8d',
}

# Firma ayarları
MAX_COMPANIES = 100
DEFAULT_COMPANY_ID = 1

# Veri validasyon ayarları
VALIDATE_PHONE = True
PHONE_FORMAT = 'TR'  # Türkiye formatı
VALIDATE_EMAIL = True
VALIDATE_TAX_ID = True

# Export ayarları
EXCEL_ENGINE = 'openpyxl'
PDF_ENGINE = 'reportlab'
WORD_ENGINE = 'python-docx'
PPTX_ENGINE = 'python-pptx'

# Debug modu
DEBUG = False

# Version
APP_VERSION = '2.0.0'
APP_NAME = 'SUSTAINAGE SDG'
APP_DESCRIPTION = 'Sürdürülebilir Kalkınma Yönetim Sistemi'

def get_db_path() -> str:
    """Database yolunu döndür"""
    return str(DATABASE_PATH)

def get_company_data_dir(company_id: int) -> Path:
    """Firma veri dizinini döndür"""
    company_dir = DATA_DIR / 'companies' / str(company_id)
    company_dir.mkdir(parents=True, exist_ok=True)
    return company_dir

def get_export_dir(company_id: int) -> Path:
    """Export dizinini döndür"""
    export_dir = get_company_data_dir(company_id) / 'exports'
    export_dir.mkdir(exist_ok=True)
    return export_dir

def get_report_dir(company_id: int) -> Path:
    """Rapor dizinini döndür"""
    report_dir = get_company_data_dir(company_id) / 'reports'
    report_dir.mkdir(exist_ok=True)
    return report_dir

# Klasörleri oluştur
def ensure_directories() -> None:
    """Gerekli klasörleri oluştur"""
    directories = [
        DATA_DIR,
        EXPORT_DIR,
        REPORTS_DIR,
        LOGS_DIR,
        UPLOADS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    # Test
    logging.info(f"APP: {APP_NAME} v{APP_VERSION}")
    logging.info(f"Database: {DATABASE_PATH}")
    logging.info(f"Cache Enabled: {CACHE_ENABLED}")
    logging.info(f"Lazy Loading: {LAZY_LOADING_ENABLED}")

    ensure_directories()
    logging.info("\nKlasorler hazir!")

