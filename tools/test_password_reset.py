#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Şifre sıfırlama isteğini hızlı test aracı.

Kullanım:
    python tools/test_password_reset.py <db_path> <username>

Örnek:
    python tools/test_password_reset.py data/sdg_desktop.sqlite __super__
"""

import logging
import sys

sys.path.insert(0, '.')

from security.core.password_reset import request_password_reset

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    # Default values for testing
    if len(sys.argv) < 3:
        # logging.info("Kullanım: python tools/test_password_reset.py <db_path> <username>")
        # sys.exit(1)
        from config.database import DB_PATH
        db_path = DB_PATH
        username = "Admin"
        logging.info(f"Using default values: DB={db_path}, User={username}")
    else:
        db_path = sys.argv[1]
        username = sys.argv[2]

    success, message = request_password_reset(db_path, username)
    logging.info(f"Başarılı mı: {success}")
    logging.info(f"Mesaj: {message}")


if __name__ == "__main__":
    main()
