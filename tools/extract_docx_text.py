import logging
import os

from docx import Document

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FILES = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '1-YAPILACAKLAR', 'Copilot_Sustainage değerlendirmesi.docx')),
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '1-YAPILACAKLAR', 'CoPilot Sustainage Değerlendirmesi.docx')),
]

def read_docx(path: str) -> str:
    doc = Document(path)
    parts = []
    for p in doc.paragraphs:
        if p.text:
            parts.append(p.text)
    return "\n".join(parts)

def main() -> None:
    for p in FILES:
        if os.path.exists(p):
            logging.info("===== " + os.path.basename(p) + " =====")
            txt = read_docx(p)
            logging.info(txt[:20000])

if __name__ == "__main__":
    main()
