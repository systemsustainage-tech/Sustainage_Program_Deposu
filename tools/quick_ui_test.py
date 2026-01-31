import logging
import tkinter as tk

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    try:
        # LoginScreen import and init
        from app.login_screen import LoginScreen
        root = tk.Tk()
        root.withdraw()
        LoginScreen(root)
        # Destroy login children to avoid interference before loading MainApp
        for child in root.winfo_children():
            try:
                child.destroy()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        # MainApp classic dashboard
        from app.main_app import MainApp
        user = (1, '__super__', 'Admin')
        app = MainApp(root, user)
        app.show_dashboard_classic()

        root.destroy()
        logging.info('OK: modules imported and basic UI creation executed.')
    except Exception as e:
        logging.error('ERROR:', e)

if __name__ == '__main__':
    main()
