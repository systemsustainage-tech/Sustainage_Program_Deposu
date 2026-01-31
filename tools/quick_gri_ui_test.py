#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick GRI UI smoke test: import GRIGUI and construct core UI without mainloop.
"""
import logging
import tkinter as tk

from gri.gri_gui import GRIGUI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    try:
        root = tk.Tk()
        frame = tk.Frame(root)
        frame.pack()
        GRIGUI(frame, company_id=1)
        # Destroy immediately; this is only to catch import/constructor errors
        root.destroy()
        logging.info("OK: GRIGUI imported and constructed successfully.")
    except Exception as e:
        logging.error(f"ERROR: GRIGUI smoke test failed: {e}")

if __name__ == '__main__':
    main()
