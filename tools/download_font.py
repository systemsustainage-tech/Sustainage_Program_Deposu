import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)

def download_font():
    url = "https://raw.githubusercontent.com/dejavu-fonts/dejavu-fonts/master/ttf/DejaVuSans.ttf"
    target_dir = os.path.join('backend', 'static', 'fonts')
    target_file = os.path.join(target_dir, 'DejaVuSans.ttf')

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        logging.info(f"Created directory: {target_dir}")

    logging.info(f"Downloading font from {url}...")
    try:
        urllib.request.urlretrieve(url, target_file)
        logging.info(f"Font downloaded successfully to {target_file}")
    except Exception as e:
        logging.error(f"Failed to download font: {e}")

if __name__ == "__main__":
    download_font()
