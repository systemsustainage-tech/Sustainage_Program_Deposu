import paramiko
import re
import sys
import os

def fix_remaining_translations():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    translations = {
        'company_edit_title': 'Şirket Düzenle',
        'company_new_title': 'Yeni Şirket',
        'company_add_title': 'Şirket Ekle',
        'user_edit_title': 'Kullanıcı Düzenle',
        'user_new_title': 'Yeni Kullanıcı',
        'user_add_title': 'Kullanıcı Ekle',
        'lbl_password_hint': 'En az 8 karakter, büyük/küçük harf ve rakam içermelidir.',
        'manager_failed': 'Yönetici bilgileri yüklenemedi.',
        'module_active': 'Modül Aktif',
        'module_active_badge': 'Aktif',
        'scope_1': 'Kapsam 1',
        'scope_2': 'Kapsam 2',
        'scope_3': 'Kapsam 3',
        'tnfd_col_rec': 'Öneri'
    }

    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Get list of html files
        stdin, stdout, stderr = client.exec_command("ls /var/www/sustainage/templates/*.html")
        files = stdout.read().decode().splitlines()
        
        for remote_path in files:
            filename = remote_path.split('/')[-1]
            
            # Download
            local_path = f"c:\\SUSTAINAGESERVER\\temp_{filename}"
            sftp.get(remote_path, local_path)
            
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            original_content = content
            
            # Replace keys with more granular regex targeting _('key')
            for key, text in translations.items():
                # Matches _('key') or _("key")
                # We replace it with 'text' (quoted string)
                pattern = r"_\(\s*['\"]" + re.escape(key) + r"['\"]\s*\)"
                # Ensure text doesn't break quotes. Assuming text doesn't contain single quotes for now.
                replacement = f"'{text}'"
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                print(f"Patched {filename}")
                with open(local_path, "w", encoding="utf-8") as f:
                    f.write(content)
                sftp.put(local_path, remote_path)
            
            # Cleanup
            if os.path.exists(local_path):
                os.remove(local_path)

        sftp.close()
        print("Remaining translations patched.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_remaining_translations()
