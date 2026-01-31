#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGIN UI DEBUG TEST
- Gerçek UI ile login test et
"""

import logging
import os
import sys
import tkinter as tk

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path ayarı
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ui_login() -> None:
    """UI login testi"""
    root = tk.Tk()
    root.title("Login Test")
    root.geometry("400x300")
    
    from app.login_screen import LoginScreen

    # Login ekranını oluştur
    try:
        login_screen = LoginScreen(root)
        logging.info(" Login screen oluşturuldu")
    except Exception as e:
        logging.error(f" Login screen hatası: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Auto-fill admin bilgileri (test için)
    try:
        login_screen.username_entry.insert(0, "admin")
        login_screen.password_entry.insert(0, "admin123")
        logging.info(" Admin bilgileri otomatik dolduruldu")
        logging.info(" Test için login() fonksiyonunu manuel çağırın veya Enter'a basın")
    except Exception as e:
        logging.error(f" Auto-fill hatası: {e}")
    
    root.mainloop()

if __name__ == "__main__":
    logging.info(" Login UI Test")
    logging.info("="*60)
    logging.info(" Admin bilgileri otomatik doldurulacak")
    logging.info(" 'Giriş' butonuna basın veya Enter tuşuna basın")
    logging.info("="*60)
    logging.info()
    
    test_ui_login()

