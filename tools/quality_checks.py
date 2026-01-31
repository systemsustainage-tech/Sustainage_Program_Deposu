import logging
import os
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run(cmd):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logging.info(f"$ {cmd}")
        if p.stdout:
            logging.info(p.stdout.strip())
        if p.stderr:
            logging.info(p.stderr.strip())
        return p.returncode
    except Exception as e:
        logging.info(f"Komut çalıştırılamadı: {cmd}\n{e}")
        return 1

def check_exists(name):
    try:
        r = subprocess.run(f"{name} --version", shell=True, capture_output=True, text=True)
        return r.returncode == 0
    except Exception:
        return False

def check_module_exists(module_name):
    try:
        r = subprocess.run(f"\"{sys.executable}\" -m {module_name} --version", shell=True, capture_output=True, text=True)
        return r.returncode == 0
    except Exception:
        return False

def ensure_dev_tools():
    """Eksik geliştirme araçlarını otomatik yükle"""
    to_install = []
    # Lint
    if not (check_exists("ruff") or check_module_exists("ruff")):
        to_install.append("ruff")
    if not (check_exists("flake8") or check_module_exists("flake8")):
        # flake8 opsiyonel; ruff varsa gerekmez, yine de yüklenebilir
        pass
    # Format
    if not (check_exists("black") or check_module_exists("black")):
        to_install.append("black")
    if not (check_exists("isort") or check_module_exists("isort")):
        to_install.append("isort")
    # Typecheck
    if not (check_exists("mypy") or check_module_exists("mypy")):
        to_install.append("mypy")
    if to_install:
        logging.info("\n=== DEV ARAÇLAR KURULUYOR ===")
        for pkg in to_install:
            cmd = f"\"{sys.executable}\" -m pip install {pkg}"
            rc = run(cmd)
            if rc != 0:
                logging.info(f"[UYARI] {pkg} otomatik kurulamadi. Manuel kurulum gerekebilir.")

def main():
    # Geliştirme araçlarını garanti altına al
    ensure_dev_tools()
    logging.info("\n=== PYTHON SÖZDİZİM KONTROLÜ ===")
    try:
        p = subprocess.run([sys.executable, "-m", "compileall", "."], capture_output=True, text=True)
        logging.info(f"$ {sys.executable} -m compileall .")
        if p.stdout:
            logging.info(p.stdout.strip())
        if p.stderr:
            logging.info(p.stderr.strip())
    except Exception as e:
        logging.info(f"Sözdizim kontrolü çalıştırılamadı\n{e}")

    logging.info("\n=== LINT ===")
    # Ruff tercih edilir; yoksa flake8'e düş
    if check_module_exists("ruff") or check_exists("ruff"):
        run(f"\"{sys.executable}\" -m ruff check .")
    elif check_module_exists("flake8") or check_exists("flake8"):
        run(f"\"{sys.executable}\" -m flake8 .")
    else:
        logging.info("Lint aracı bulunamadı (ruff/flake8).")
        ps_script = os.path.join("scripts", "lint.ps1")
        if os.name == 'nt' and os.path.exists(ps_script):
            run(f"powershell -ExecutionPolicy Bypass -File {ps_script} -Path . -ExitZero")

    logging.info("\n=== FORMAT KONTROL ===")
    if check_module_exists("black") or check_exists("black"):
        run(f"\"{sys.executable}\" -m black --check .")
    else:
        logging.info("black bulunamadı.")
    if check_module_exists("isort") or check_exists("isort"):
        run(f"\"{sys.executable}\" -m isort --check-only .")
    else:
        logging.info("isort bulunamadı.")

    logging.info("\n=== TYPECHECK ===")
    if check_module_exists("mypy") or check_exists("mypy"):
        run(f"\"{sys.executable}\" -m mypy . --ignore-missing-imports")
    elif check_exists("pyright"):
        run("pyright .")
    else:
        logging.info("Typecheck aracı bulunamadı (mypy/pyright).")

if __name__ == "__main__":
    main()
