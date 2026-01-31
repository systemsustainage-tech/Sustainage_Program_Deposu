import logging
import tkinter as tk
from tkinter import ttk

ui_theme = {
    'primary': '#2F6DB2',
    'primary_light': '#DDEAFB',
    'accent': '#8A2B2B',
    'border': '#C7D3E5',
    'text': '#2C3E50',
    'text_muted': '#6B7A90',
    'control_bg': '#FFFFFF',
    'control_hover': '#F6FAFF',
    'disabled': '#EEF2F7',
}

def apply_theme(root: tk.Misc) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception as e:
        logging.error(f"Silent error caught: {str(e)}")
    style.configure('TLabel', font=('Segoe UI', 10), foreground=ui_theme['text'])
    style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#FFFFFF', background=ui_theme['primary'])
    style.configure('Section.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#FFFFFF', background=ui_theme['primary'])
    style.configure('TButton', font=('Segoe UI', 10), padding=(10,6), relief='raised', borderwidth=2)
    style.map('TButton', background=[('active', ui_theme['control_hover'])], relief=[('pressed','sunken'),('!pressed','raised')])
    style.configure('Toolbar.TFrame', background=ui_theme['primary'])
    style.configure('Content.TFrame', background=ui_theme['control_bg'])
    style.configure('Muted.TLabel', foreground=ui_theme['text_muted'])
    style.configure('Custom.Treeview', rowheight=26, font=('Segoe UI', 10))
    style.configure('Custom.Treeview.Heading', font=('Segoe UI', 10, 'bold'))
    style.configure('TNotebook', background=ui_theme['primary_light'])
    style.configure('TNotebook.Tab', font=('Segoe UI', 12, 'bold'), padding=6)
    style.map('TNotebook.Tab', background=[('selected', ui_theme['primary'])], foreground=[('selected', '#FFFFFF')])
    style.configure('Primary.TButton', font=('Segoe UI', 10), foreground='#FFFFFF', background='#007bff', padding=(10,6), relief='raised', borderwidth=2)
    style.map('Primary.TButton', background=[('active', '#0056b3')], foreground=[('disabled', ui_theme['text_muted'])], relief=[('pressed','sunken'),('!pressed','raised')])
    style.configure('Menu.TButton', font=('Segoe UI', 11), foreground='#FFFFFF', background='#1E4B8A', padding=(16,8), borderwidth=2, relief='raised', anchor='w')
    style.map('Menu.TButton', background=[('active', '#24569C'), ('pressed', '#153B70')], foreground=[('disabled', ui_theme['text_muted'])])
    style.configure('Accent.TButton', font=('Segoe UI', 10), foreground='#FFFFFF', background=ui_theme['accent'], padding=6)
    style.map('Accent.TButton', background=[('active', '#B24343')])
    style.configure('Error.TEntry', fieldbackground='#FFE5E5')
    style.configure('Toast.TLabel', font=('Segoe UI', 10), foreground='#FFFFFF', background=ui_theme['primary'])
    try:
        root.option_add('*Button.font', '{Segoe UI} 10')
        root.option_add('*Button.background', '#007bff')
        root.option_add('*Button.foreground', '#FFFFFF')
        root.option_add('*Button.relief', 'raised')
        root.option_add('*Button.borderWidth', 2)
        root.option_add('*Button.activeBackground', '#0056b3')
        root.option_add('*Button.activeForeground', '#FFFFFF')
        root.option_add('*Button.padx', 10)
        root.option_add('*Button.pady', 6)
    except Exception as e:
        logging.error(f"Silent error caught: {str(e)}")
    try:
        standardize_buttons(root)
    except Exception as e:
        logging.error(f"Silent error caught: {str(e)}")

def create_scrollable(parent: tk.Misc, bg: str = 'white'):
    """Standart scrollable container oluştur: (canvas, inner_frame, scrollbar)
    Windows/Mac/Linux için mousewheel destekleri eklenir.
    """
    container = tk.Frame(parent, bg=bg)
    container.pack(fill='both', expand=True)
    canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)
    inner = tk.Frame(canvas, bg=bg)
    canvas.create_window((0, 0), window=inner, anchor='nw')

    def _on_configure(_):
        try:
            canvas.configure(scrollregion=canvas.bbox('all'))
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
    inner.bind('<Configure>', _on_configure)

    def _on_mousewheel(event):
        try:
            delta = event.delta
            if delta == 0:
                return
            canvas.yview_scroll(int(-1*(delta/120)), 'units')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
    def _on_scroll_up(_):
        try:
            canvas.yview_scroll(-1, 'units')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
    def _on_scroll_down(_):
        try:
            canvas.yview_scroll(1, 'units')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
    canvas.bind('<MouseWheel>', _on_mousewheel)
    container.bind('<MouseWheel>', _on_mousewheel)
    inner.bind('<MouseWheel>', _on_mousewheel)
    # Linux
    canvas.bind('<Button-4>', _on_scroll_up)
    canvas.bind('<Button-5>', _on_scroll_down)
    inner.bind('<Button-4>', _on_scroll_up)
    inner.bind('<Button-5>', _on_scroll_down)
    return canvas, inner, scrollbar

def standardize_buttons(root: tk.Misc) -> None:
    try:
        def _apply(widget):
            if isinstance(widget, tk.Button):
                try:
                    widget.configure(relief=tk.RAISED, bd=2)
                    widget.configure(font=('Segoe UI', 10))
                    widget.configure(bg='#007bff', fg='#FFFFFF', activebackground='#0056b3', activeforeground='#FFFFFF')
                    if 'padx' in widget.keys():
                        val = str(widget.cget('padx'))
                        widget.configure(padx=min(10, int(val) if val and val.isdigit() else 10))
                    if 'pady' in widget.keys():
                        val = str(widget.cget('pady'))
                        widget.configure(pady=min(6, int(val) if val and val.isdigit() else 6))
                    def _press(_):
                        try:
                            widget.configure(relief=tk.SUNKEN)
                        except Exception as e:
                            logging.error(f"Silent error caught: {str(e)}")
                    def _release(_):
                        try:
                            widget.configure(relief=tk.RAISED)
                        except Exception as e:
                            logging.error(f"Silent error caught: {str(e)}")
                    widget.bind('<ButtonPress-1>', _press, add='+')
                    widget.bind('<ButtonRelease-1>', _release, add='+')
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            if isinstance(widget, ttk.Button):
                try:
                    current_style = str(widget.cget('style'))
                    if not current_style:
                        widget.configure(style='Primary.TButton')
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            try:
                for child in widget.winfo_children():
                    _apply(child)
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        _apply(root)
    except Exception as e:
        logging.error(f"Silent error caught: {str(e)}")
