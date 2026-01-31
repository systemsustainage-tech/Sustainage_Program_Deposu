#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yeni kullanıcı hoş geldiniz e-postası için HTML önizleme üretir.
Temadaki CID görsel referansını tarayıcıda görüntülenebilir dosya yoluna çevirir.
"""

import logging
import os
import shutil

from config.email_config import EMAIL_TEMPLATES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def render_new_user_preview(output_dir: str) -> None:
    tpl = EMAIL_TEMPLATES.get('new_user_welcome')
    if not tpl:
        raise RuntimeError('new_user_welcome şablonu bulunamadı')

    variables = {
        'program_name': 'Sustainage SDG Platform',
        'user_name': 'Test Kullanıcı',
        'short_description': 'Hesabınız oluşturuldu ve programa giriş yapabilirsiniz.',
        'reason': 'Yeni kullanıcı tanımlandığı için gönderildi',
        'login_url': 'https://sustainage.cloud/login',
        'support_email': 'sdg@digage.tr'
    }

    # .format yerine hedefli token replace (CSS süslü parantez uyumluluğu)
    html = tpl['template']
    for k, v in variables.items():
        token = '{' + str(k) + '}'
        html = html.replace(token, str(v))
    # CID referansını tarayıcı için lokal dosyaya çevir
    html = html.replace('cid:sustainage_logo', 'sustainage_logo.png')

    os.makedirs(output_dir, exist_ok=True)
    preview_path = os.path.join(output_dir, 'email_new_user.html')
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(html)

    # Görseli kopyala
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_logo = os.path.join(base_dir, "resimler", "sustainage_logo.png")
    target_logo = os.path.join(output_dir, 'sustainage_logo.png')
    if os.path.exists(source_logo):
        shutil.copyfile(source_logo, target_logo)
    else:
        # Görsel yoksa uyarı amaçlı boş bir placeholder oluştur
        with open(target_logo, 'wb') as f:
            f.write(b'')

    logging.info(f" Önizleme hazır: {preview_path}")


def main() -> None:
    output_dir = os.path.join(os.getcwd(), 'preview')
    render_new_user_preview(output_dir)


if __name__ == '__main__':
    main()
