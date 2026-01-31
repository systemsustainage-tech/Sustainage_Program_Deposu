import paramiko
import re
import sys
import os

def fix_dashboard_final():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        filename = 'dashboard.html'
        remote_path = f"/var/www/sustainage/templates/{filename}"
        local_path = f"c:\\SUSTAINAGESERVER\\temp_fix_{filename}"
        
        print(f"Downloading {filename}...")
        sftp.get(remote_path, local_path)
        
        with open(local_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        original_content = content
        
        # Fix Rapor Oluştur Link line by line
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if 'Rapor Oluştur' in line:
                if 'href="{{ \'#\' }}"' in line:
                    line = line.replace('href="{{ \'#\' }}"', 'href="{{ url_for(\'report_add_page\') }}"')
                elif 'href="#"' in line:
                    line = line.replace('href="#"', 'href="{{ url_for(\'report_add_page\') }}"')
            new_lines.append(line)
        content = '\n'.join(new_lines)
        
        # Fix Scope Translations
        translations = {
            'scope_1': 'Kapsam 1',
            'scope_2': 'Kapsam 2',
            'scope_3': 'Kapsam 3'
        }
        
        for key, text in translations.items():
            # Replace {{ _('key') }}
            pattern1 = r"\{\{\s*_\(\s*['\"]" + key + r"['\"]\s*\)\s*\}\}"
            content = re.sub(pattern1, text, content)
            # Replace _('key') inside other blocks
            pattern2 = r"_\(\s*['\"]" + key + r"['\"]\s*\)"
            content = re.sub(pattern2, f"'{text}'", content)
            
        if content != original_content:
            print(f"Patching {filename}...")
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(content)
            sftp.put(local_path, remote_path)
            print("Upload complete.")
        else:
            print("No changes needed.")
            
        # Cleanup
        if os.path.exists(local_path):
            os.remove(local_path)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_dashboard_final()
