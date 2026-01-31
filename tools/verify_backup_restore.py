import logging
import os
import tkinter as tk
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    try:
        from yonetim.yönetim_gui import YonetimGUI
        yg = YonetimGUI(root)

        name = f"test_yedek_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_opts = {
            'type': 'full',
            'name': name,
            'folder': os.path.join('data', 'backups'),
            'compress': True,
        }
        backup_path = yg._perform_backup(backup_opts)
        logging.info('Backup created at:', backup_path)

        # Restore adımı varsayılan olarak devre dışı; isteğe bağlı olarak çalıştır
        if os.environ.get('RUN_RESTORE') == '1':
            restore_opts = {
                'file': backup_path,
                'type': 'full',
                'backup_current': False,
            }
            result = yg._perform_restore(restore_opts)
            logging.info('Restore result:', result)
        logging.info('OK: backup flow executed')
    except Exception as e:
        logging.error('ERROR:', e)
    finally:
        try:
            root.destroy()
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

if __name__ == '__main__':
    main()
