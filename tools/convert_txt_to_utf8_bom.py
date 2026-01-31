import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def convert_file(path: str):
    try:
        # Read as UTF-8 (fallback to Windows-1254 if needed)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, 'r', encoding='cp1254') as f:
                content = f.read()

        # Write with UTF-8 BOM to help auto-detection in browsers/editors
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(content)
        logging.info(f"Converted: {path}")
    except Exception as e:
        logging.error(f"Skip (error): {path} -> {e}")


def convert_all(root: str):
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith('.txt'):
                convert_file(os.path.join(dirpath, name))


if __name__ == '__main__':
    # Run from repository root: python tools/convert_txt_to_utf8_bom.py
    convert_all(os.getcwd())
