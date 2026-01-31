import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk


def center_on_parent(parent: tk.Tk, window: tk.Toplevel) -> None:
    window.update_idletasks()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    ww = window.winfo_width()
    wh = window.winfo_height()
    x = px + (pw - ww) // 2
    y = py + (ph - wh) // 2
    window.geometry(f"+{x}+{y}")


def animate_open(window: tk.Toplevel, kind: str = "fade", duration_ms: int = 180) -> None:
    try:
        if kind == "fade":
            window.attributes("-alpha", 0.0)
            steps = max(1, duration_ms // 16)
            delta = 1.0 / steps

            def step(i: int = 0) -> None:
                a = min(1.0, i * delta)
                window.attributes("-alpha", a)
                if a < 1.0:
                    window.after(16, lambda: step(i + 1))

            step()
            return

        if kind == "slide":
            window.update_idletasks()
            x = window.winfo_x()
            y = window.winfo_y()
            start_y = y - 24
            window.geometry(f"+{x}+{start_y}")
            steps = max(1, duration_ms // 16)
            delta = (y - start_y) / steps

            def step(i: int = 0) -> None:
                ny = int(start_y + i * delta)
                if ny >= y:
                    window.geometry(f"+{x}+{y}")
                else:
                    window.geometry(f"+{x}+{ny}")
                    window.after(16, lambda: step(i + 1))

            step()
            return

        if kind == "scale":
            window.update_idletasks()
            w = window.winfo_width()
            h = window.winfo_height()
            x = window.winfo_x()
            y = window.winfo_y()
            steps = max(1, duration_ms // 16)

            def step(i: int = 0) -> None:
                f = max(0.1, i / steps)
                nw = max(1, int(w * f))
                nh = max(1, int(h * f))
                nx = x + (w - nw) // 2
                ny = y + (h - nh) // 2
                window.geometry(f"{nw}x{nh}+{nx}+{ny}")
                if i < steps:
                    window.after(16, lambda: step(i + 1))
                else:
                    window.geometry(f"{w}x{h}+{x}+{y}")

            step()
    except Exception as e:
        logging.error(f"Silent error caught: {str(e)}")
