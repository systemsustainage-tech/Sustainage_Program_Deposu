#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin kullanıcı ve rol/izin senkronizasyon betiği

- 'admin' kullanıcısının şifresini 'admin' olarak günceller
- 'admin' rolünü oluşturur (yoksa) ve admin kullanıcıya atar
- Admin rolüne uygulama menüsünde gereken izinleri atar

Çalıştırma:
    python tools/sync_admin.py
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kökünü PYTHONPATH'e ekle (script tools klasöründen çalışır)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


ADMIN_PERMISSION_NAMES = [
    'dashboard.read', 'dashboard.advanced', 'company.read',
    'sdg.read', 'gri.read', 'tsrs.read', 'esg.read',
    'strategic.read', 'data.import', 'forms.manage',
    'tasks.auto_create', 'files.manage', 'hr.read', 'policy.read', 'surveys.read',
    'skdm.read', 'mapping.read', 'prioritization.read',
    'waste.read', 'water.read', 'supply_chain.read',
    'product_tech.read', 'report.read', 'system.settings'
]


def ensure_admin_user_and_role() -> None:
    from yonetim.kullanici_yonetimi.models.user_manager import UserManager
    um = UserManager()  # varsayılan db_path: data/sdg_desktop.sqlite

    # 1) Admin kullanıcısını doğrula ve şifreyi 'admin' olarak ayarla
    user = um.get_user_by_username('admin')
    if not user:
        logging.info("'admin' kullanıcısı bulunamadı; oluşturuluyor...")
        user_id = um.create_user({
            'username': 'admin',
            'email': 'admin@sustainage.com',
            'password': 'admin',
            'first_name': 'Sistem',
            'last_name': 'Yöneticisi',
            'is_active': True,
            'is_verified': True,
        }, created_by=None)
        if user_id <= 0:
            logging.info("Admin kullanıcısı oluşturulamadı!")
            return False
        user = um.get_user_by_username('admin')
    else:
        um.update_user_password('admin', 'admin', updated_by=user.get('id'))
        logging.info("'admin' şifresi 'admin' olarak güncellendi.")

    admin_user_id = user.get('id')

    # 2) Admin rolünü bul/oluştur
    roles = um.get_roles()
    admin_role = next((r for r in roles if r['name'] == 'admin'), None)
    if not admin_role:
        logging.info("'admin' rolü bulunamadı; oluşturuluyor...")
        admin_role_id = um.create_role({
            'name': 'admin',
            'display_name': 'Yönetici',
            'description': 'Sistem yönetimi ve modüllere erişim',
            'is_system_role': False,
            'is_active': True,
        }, created_by=admin_user_id)
        if admin_role_id <= 0:
            logging.info("Admin rolü oluşturulamadı!")
            return False
        admin_role = um.get_role_by_id(admin_role_id)
    admin_role_id = admin_role['id']

    # 3) Admin kullanıcısına admin rolünü ata (yoksa)
    user_roles_str = (user or {}).get('roles') or ''
    user_roles = [r.strip().lower() for r in user_roles_str.split(',') if r]
    if 'admin' not in user_roles:
        logging.info("Admin rolü kullanıcıya atanıyor...")
        um.assign_role_to_user(admin_user_id, admin_role_id)

    # 4) Admin rolüne gerekli izinleri ata
    logging.info("Admin rol izinleri senkronize ediliyor...")
    # İzin ID'lerini topla
    conn = um.get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TEMP TABLE IF NOT EXISTS tmp_perm_names (name TEXT)")
    cur.execute("DELETE FROM tmp_perm_names")
    cur.executemany("INSERT INTO tmp_perm_names (name) VALUES (?)", [(n,) for n in ADMIN_PERMISSION_NAMES])
    cur.execute(
        "SELECT id FROM permissions WHERE name IN (SELECT name FROM tmp_perm_names)"
    )
    perm_ids = [row[0] for row in cur.fetchall()]
    conn.close()
    if perm_ids:
        um.set_role_permissions(admin_role_id, perm_ids, updated_by=admin_user_id)
        logging.info(f"{len(perm_ids)} izin admin rolüne atandı.")
    else:
        logging.info("Uygun izin bulunamadı; şema/varsayılan izinleri kontrol edin.")

    logging.info("Senkronizasyon tamamlandı.")
    return True


if __name__ == '__main__':
    ok = ensure_admin_user_and_role()
    sys.exit(0 if ok else 1)
