#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Basit ekran görüntüsü aracı
- Küçük bir pencere ile dosya adı girilir ve Capture butonuna basınca
  pencere gizlenir, ekran görüntüsü alınır ve c:\SDG\resimler\sunum içine kaydedilir.
"""

from __future__ import annotations

import re
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import ImageGrab

# Proje kök dizinini bul (bu dosya tools/ altında olduğu için 2 seviye yukarı)
ROOT_DIR = Path(__file__).resolve().parent.parent
SAVE_DIR = ROOT_DIR / "resimler/sunum"
SAVE_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", name)
    return name or f"capture_{int(time.time())}"


def capture_screen(filename: str) -> None:
    img = ImageGrab.grab(all_screens=True)
    path = SAVE_DIR / f"{filename}.png"
    img.save(str(path))
    return path


def main() -> None:
    root = tk.Tk()
    root.title("Ekran Görüntüsü Aracı")
    root.attributes("-topmost", True)
    root.geometry("320x140")

    tk.Label(root, text="Dosya adı").pack(pady=(10, 0))
    name_var = tk.StringVar(value="sdg_ana_sayfa")
    entry = ttk.Entry(root, textvariable=name_var)
    entry.pack(fill="x", padx=12)

    status_var = tk.StringVar(value=f"Kayıt dizini: {SAVE_DIR}")
    ttk.Label(root, textvariable=status_var, wraplength=300).pack(pady=4)

    def do_capture() -> None:
        filename = sanitize_name(name_var.get())
        # Pencereyi gizle, çek ve geri getir
        root.withdraw()

        def perform_capture():
            try:
                out = capture_screen(filename)
                msg = f"Kaydedildi: {out}"
                status_var.set(msg)
            except Exception as e:
                messagebox.showerror("Hata", str(e))
            finally:
                root.deiconify()

        # 300ms sonra (UI bloklamadan) ekran görüntüsü al
        root.after(300, perform_capture)

    btn = ttk.Button(root, text="Capture", command=do_capture)
    btn.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
