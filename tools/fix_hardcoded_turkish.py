import logging
import os
import re
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of files to process
files = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'modules', 'ungc', 'ungc_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'modules', 'surveys', 'web_survey_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'modules', 'quality', 'data_quality_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'modules', 'mapping', 'mapping_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'modules', 'automation', 'automated_reporting_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'modules', 'auto_tasks', 'auto_task_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'modules', 'ai', 'ai_module_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'yonetim', 'policy_library', 'policy_library_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'yonetim', 'licensing', 'gui', 'license_management_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'yonetim', 'forms', 'forms_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'yonetim', 'company', 'company_management_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'water', 'water_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tasks', 'task_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tasks', 'admin_dashboard_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tasks', 'task_template_gui.py'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts', 'tests', 'test_password_reset_gui.py')
]

replacements = [
    ('text="İptal"', 'text=self.lm.tr("btn_cancel", "İptal")'),
    ("text='İptal'", "text=self.lm.tr('btn_cancel', 'İptal')"),
    ('text="Kaydet"', 'text=self.lm.tr("btn_save", "Kaydet")'),
    ("text='Kaydet'", "text=self.lm.tr('btn_save', 'Kaydet')"),
    ('text="Sil"', 'text=self.lm.tr("btn_delete", "Sil")'),
    ("text='Sil'", "text=self.lm.tr('btn_delete', 'Sil')"),
    ('text="Düzenle"', 'text=self.lm.tr("btn_edit", "Düzenle")'),
    ("text='Düzenle'", "text=self.lm.tr('btn_edit', 'Düzenle')"),
    ('text="Güncelle"', 'text=self.lm.tr("btn_update", "Güncelle")'),
    ("text='Güncelle'", "text=self.lm.tr('btn_update', 'Güncelle')"),
    ('text="Kapat"', 'text=self.lm.tr("btn_close", "Kapat")'),
    ("text='Kapat'", "text=self.lm.tr('btn_close', 'Kapat')"),
    ('text="Geri"', 'text=self.lm.tr("back", "Geri")'),
    ("text='Geri'", "text=self.lm.tr('back', 'Geri')"),
    ('text="İleri"', 'text=self.lm.tr("next", "İleri")'),
    ("text='İleri'", "text=self.lm.tr('next', 'İleri')"),
    ('text="Yenile"', 'text=self.lm.tr("btn_refresh", "Yenile")'),
    ("text='Yenile'", "text=self.lm.tr('btn_refresh', 'Yenile')"),
    ('text="Ekle"', 'text=self.lm.tr("btn_add", "Ekle")'),
    ("text='Ekle'", "text=self.lm.tr('btn_add', 'Ekle')"),
    ('text="Yeni Anket"', 'text=self.lm.tr("btn_new_survey", "Yeni Anket")'),
    ('text="E-posta Gönder"', 'text=self.lm.tr("btn_send_email", "E-posta Gönder")'),
    ('text="Yanıtları Çek"', 'text=self.lm.tr("btn_fetch_responses", "Yanıtları Çek")'),
    ('text="Yanıtları İşle"', 'text=self.lm.tr("btn_process_responses", "Yanıtları İşle")'),
    ('text="Duraklat"', 'text=self.lm.tr("btn_pause", "Duraklat")'),
    ('text="Aktifleştir"', 'text=self.lm.tr("btn_activate", "Aktifleştir")'),
    ('text="Rapor Merkezi"', 'text=self.lm.tr("btn_report_center", "Rapor Merkezi")'),
]

for file_path in files:
    if not os.path.exists(file_path):
        logging.info(f"File not found: {file_path}")
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    modified = False
    new_content = content
    
    # Check if we need to add LanguageManager
    needs_lm = False
    for old, new in replacements:
        if old in content:
            new_content = new_content.replace(old, new)
            modified = True
            needs_lm = True
            
    if modified:
        # Add import if missing
        if "from utils.language_manager import LanguageManager" not in new_content:
            # Find last import
            lines = new_content.splitlines()
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    last_import_idx = i
            
            lines.insert(last_import_idx + 1, "from utils.language_manager import LanguageManager")
            new_content = "\n".join(lines) + "\n"
            
        # Initialize lm in __init__ if missing
        if "self.lm = LanguageManager()" not in new_content and "class " in new_content:
            # Simple heuristic: find __init__ and add after it
            # We look for "def __init__(self...):"
            # And insert self.lm = LanguageManager() at the beginning of the function
            
            # Find indentation of the __init__ body
            init_match = re.search(r"def __init__\(self.*?\):\s*\n(\s+)", new_content, re.DOTALL)
            if init_match:
                indent = init_match.group(1)
                end_pos = init_match.end()
                
                # Check if super().__init__ exists close by, if so, put after it
                super_match = re.search(r"super\(\).__init__\(.*?\)", new_content[end_pos:])
                if super_match and super_match.start() < 200: # heuristic: super call is near start
                     # Insert after super
                     insert_pos = end_pos + super_match.end()
                     new_content = new_content[:insert_pos] + f"\n{indent}self.lm = LanguageManager()" + new_content[insert_pos:]
                else:
                    # Insert at start of __init__
                    new_content = new_content[:end_pos] + f"self.lm = LanguageManager()\n{indent}" + new_content[end_pos:]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        logging.info(f"Updated {file_path}")
