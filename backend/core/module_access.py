#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODÜL ERİŞİM KONTROLÜ
- Firma için hangi modüller açık?
- Super admin her şeyi görebilir
- Admin ve kullanıcılar sadece açık modülleri görebilir
"""

import logging
import sqlite3
from typing import Dict, List
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def is_module_enabled_for_company(db_path: str, company_id: int, module_code: str, is_super_admin: bool = False) -> bool:
    """
    Modül firma için aktif mi kontrol et
    
    Args:
        db_path: Veritabanı yolu
        company_id: Firma ID
        module_code: Modül kodu (örn: 'sdg', 'gri', 'esg')
        is_super_admin: Super admin mi?
    
    Returns:
        True: Modül göster
        False: Modülü gösterme
    """
    # Super admin her şeyi görebilir
    if is_super_admin:
        return True

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Modülü bul
        cur.execute("SELECT id, is_core, default_enabled FROM modules WHERE module_code = ?", (module_code,))
        module_row = cur.fetchone()

        if not module_row:
            # Modül tanımlı değil - güvenlik için gizle
            return False

        module_id, is_core, default_enabled = module_row

        # CORE modüller her zaman açık
        if is_core:
            return True

        # Firma için durum kontrolü
        cur.execute("""
            SELECT is_enabled FROM company_modules
            WHERE company_id = ? AND module_id = ?
        """, (company_id, module_id))

        cm_row = cur.fetchone()

        if cm_row:
            # Kayıt var - durumu kullan (kapatılmışsa erişim yok)
            return bool(cm_row[0])
        else:
            # Kayıt yok - modül hiç atanmamış, erişim yok
            return False

    except Exception as e:
        logging.error(f"[WARN] Modül erişim kontrolü hatası ({module_code}): {e}")
        # Hata durumunda güvenlik için gizle
        return False

    finally:
        conn.close()


def get_enabled_modules_for_company(db_path: str, company_id: int, is_super_admin: bool = False) -> List[Dict]:
    """
    Firma için aktif modülleri getir
    
    Returns:
        [
            {
                'module_code': 'sdg',
                'module_name': 'SDG Modülü',
                'icon': '',
                'category': 'Standards',
                'is_core': True
            },
            ...
        ]
    """
    # Super admin için tüm modüller
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        if is_super_admin:
            # Tüm modülleri döndür
            cur.execute("""
                SELECT module_code, module_name, icon, category, is_core, display_order
                FROM modules
                ORDER BY display_order, module_name
            """)
        else:
            # Firma için aktif modülleri döndür
            cur.execute("""
                SELECT m.module_code, m.module_name, m.icon, m.category, m.is_core, m.display_order
                FROM modules m
                LEFT JOIN company_modules cm ON m.id = cm.module_id AND cm.company_id = ?
                WHERE m.is_core = 1 OR COALESCE(cm.is_enabled, m.default_enabled) = 1
                ORDER BY m.display_order, m.module_name
            """, (company_id,))

        modules = []
        for row in cur.fetchall():
            modules.append({
                'module_code': row[0],
                'module_name': row[1],
                'icon': row[2] or '',
                'category': row[3],
                'is_core': bool(row[4]),
                'display_order': row[5]
            })

        return modules

    except Exception as e:
        logging.info(f"[WARN] Aktif modüller alınamadı: {e}")
        # Hata durumunda sadece temel modülleri döndür
        return [
            {'module_code': 'dashboard', 'module_name': 'Dashboard', 'icon': '', 'category': 'Core', 'is_core': True, 'display_order': 1},
            {'module_code': 'sdg', 'module_name': 'SDG Modülü', 'icon': '', 'category': 'Standards', 'is_core': True, 'display_order': 10},
        ]

    finally:
        conn.close()


# Modül kod → GUI fonksiyon eşleştirmesi
MODULE_FUNCTION_MAP = {
    'dashboard': 'show_dashboard',
    'tasks': 'show_my_tasks',
    'surveys': 'show_surveys',
    'sdg': 'show_sdg',
    'gri': 'show_gri',
    'tsrs': 'show_tsrs',
    'esg': 'show_esg',
    'skdm': 'show_skdm',
    'strategic': 'show_strategic',
    'prioritization': 'show_prioritization',
    'product_tech': 'show_product_tech',
    'reports': 'show_combined_reports',
    'management': 'show_management',
}

# Test
if __name__ == "__main__":
    company_id = 1
    db_path = DB_PATH
    logging.info(get_enabled_modules_for_company(company_id, db_path))
    logging.info(" Modül Erişim Kontrolü - Test")
    logging.info("="*60)

    db_path = "sdg.db"
    company_id = 1

    # 1. Tekil modül kontrolü
    logging.info("\n1️⃣ Tekil Modül Kontrolleri:")
    test_modules = ['dashboard', 'sdg', 'gri', 'esg', 'water', 'nonexistent']

    for module in test_modules:
        # Normal kullanıcı
        user_can_see = is_module_enabled_for_company(db_path, company_id, module, is_super_admin=False)
        # Super admin
        admin_can_see = is_module_enabled_for_company(db_path, company_id, module, is_super_admin=True)

        logging.info(f"   {module:15} - User: {'' if user_can_see else ''}  Super: {'' if admin_can_see else ''}")

    # 2. Aktif modül listesi
    logging.info("\n2️⃣ Firma için Aktif Modüller:")
    enabled_modules = get_enabled_modules_for_company(db_path, company_id, is_super_admin=False)
    for mod in enabled_modules:
        core_badge = " [CORE]" if mod['is_core'] else ""
        logging.info(f"   {mod['icon']} {mod['module_name']} ({mod['category']}){core_badge}")

    logging.info("\n3️⃣ Super Admin için Tüm Modüller:")
    all_modules = get_enabled_modules_for_company(db_path, company_id, is_super_admin=True)
    logging.info(f"   Toplam: {len(all_modules)} modül")

    logging.info("\n" + "="*60)
    logging.info(" Test tamamlandı!")

