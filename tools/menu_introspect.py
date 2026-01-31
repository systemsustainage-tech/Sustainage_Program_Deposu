import logging
import tkinter as tk

from app.main_app import MainApp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    user = (1021, 'admin', 'System Administrator')
    app = MainApp(root, user, company_id=1)

    # Menü butonları
    buttons = getattr(app, 'menu_buttons', [])
    logging.info('MENU_BUTTONS:', len(buttons))
    for btn in buttons:
        try:
            logging.info(f"{str(btn.cget('text'))} | state={str(btn.cget('state'))}")
        except Exception as e:
            logging.error('ERROR_BTN', e)

    # Lazy import testleri
    logging.info('LAZY_IMPORTS:')
    codes = ['sdg','gri','yonetim','raporlama','mapping','tsrs','skdm','tasks','admin_dashboard','innovation','quality','digital_security','emergency','strategic']
    for code in codes:
        try:
            cls = app._lazy_import_module(code)
            status = 'OK' if cls is not None else 'MISSING'
        except Exception as e:
            import traceback
            status = f'ERROR:{e.__class__.__name__}'
            logging.info(f"TRACE for {code}:")
            traceback.print_exc()
        logging.info(f"{code}: {status}")

    root.destroy()

if __name__ == '__main__':
    main()
