#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Politika Şablonlarını İçe Aktarma Aracı
"""

import logging
import io
import json
import os
import sys

# Windows terminal için UTF-8 desteği
if os.name == 'nt' and not os.getenv('PYTEST_CURRENT_TEST'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Proje kök dizinini path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.policy_library.policy_manager import PolicyLibraryManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def import_templates(db_path: str, templates_file: str) -> None:
    """Şablonları içe aktar"""
    logging.info(" Politika Şablonları İçe Aktarılıyor...")
    logging.info("=" * 60)
    
    # Manager oluştur
    manager = PolicyLibraryManager(db_path)
    
    # JSON dosyasını oku
    try:
        with open(templates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logging.info(f" JSON dosyası okunamadı: {e}")
        return False
    
    # Kategorileri al
    categories = {cat['category_code']: cat['id'] 
                  for cat in manager.get_categories()}
    
    # Şablonları ekle
    templates = data.get('templates', [])
    success_count = 0
    error_count = 0
    
    for template in templates:
        try:
            # Kategori ID'sini al
            category_code = template.get('category_code')
            category_id = categories.get(category_code)
            
            if not category_id:
                logging.info(f"️  {template['template_code']}: Kategori bulunamadı - {category_code}")
                error_count += 1
                continue
            
            # Template data hazırla
            template_data = {
                'template_code': template['template_code'],
                'template_name': template['template_name'],
                'template_name_tr': template['template_name_tr'],
                'category_id': category_id,
                'description': template['description'],
                'content': template['content'],
                'version': template['version'],
                'language': template['language']
            }
            
            result = manager.add_template(template_data)
            if result:
                logging.info(f" {template['template_code']}: {template['template_name_tr']}")
                success_count += 1
            else:
                logging.error(f"️  {template['template_code']}: Zaten mevcut veya hata")
                error_count += 1
                
        except Exception as e:
            logging.error(f" {template.get('template_code', '?')}: Hata - {e}")
            error_count += 1
    
    logging.info("\n" + "=" * 60)
    logging.info(" Özet:")
    logging.info(f"   Başarılı: {success_count}")
    logging.error(f"   Hatalı: {error_count}")
    logging.info(f"   Toplam: {len(templates)}")
    
    logging.info("\n İçe aktarma tamamlandı!")
    return True

def main() -> None:
    """Ana fonksiyon"""
    # Varsayılan yollar
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
    templates_file = os.path.join(base_dir, 'data', 'policy_templates', 'default_templates.json')
    
    # Komut satırı argümanları
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    if len(sys.argv) > 2:
        templates_file = sys.argv[2]
    
    logging.info(f" Veritabanı: {db_path}")
    logging.info(f" Şablonlar: {templates_file}")
    logging.info()
    
    # İçe aktar
    import_templates(db_path, templates_file)

if __name__ == '__main__':
    main()
