import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

def main():
    try:
        from app.login_screen import LoginScreen
    except Exception as e:
        logging.error(f"[ERROR] login_screen import: {e}")
        sys.exit(1)

    root = tk.Tk()
    root.withdraw()
    ui = LoginScreen(root)

    # Giriş bilgilerini yerleştir
    ui.username_entry.delete(0, 'end')
    ui.username_entry.insert(0, 'admin')
    ui.password_entry.delete(0, 'end')
    ui.password_entry.insert(0, 'Admin_2025!')

    # Ana uygulama başlatma stub'u
    result = {'ok': False}
    def start_main_app_stub(user_info):
        result['ok'] = True
        logging.info(f"[OK] LOGIN_OK: {user_info}")
    ui.start_main_app = start_main_app_stub

    # 2FA penceresi olmaması için basit override
    ui._verify_totp_simple = lambda s, c: True

    try:
        ui.login()
    except Exception as e:
        logging.error(f"[ERROR] login() hata: {e}")
        sys.exit(2)
    finally:
        try:
            root.destroy()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    logging.info(f"[RESULT] success={result['ok']}")
    sys.exit(0 if result['ok'] else 3)

if __name__ == '__main__':
    main()

