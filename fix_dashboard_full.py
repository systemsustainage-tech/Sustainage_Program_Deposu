import paramiko
import re

def fix_dashboard():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        filepath = "/var/www/sustainage/templates/dashboard.html"
        
        print(f"Reading {filepath}...")
        with sftp.open(filepath, "r") as f:
            content = f.read().decode()
            
        original_content = content
        
        # Fix Rapor Oluştur link
        # Pattern matches: href="{{ '#' }}" followed by class/attributes, then the icon, then "Rapor Oluştur"
        # We need to be careful with newlines/spaces
        pattern_report = r'href="\{\{ \'#\' \}\}"([^>]*>\s*<i[^>]*></i>\s*Rapor Oluştur)'
        content = re.sub(pattern_report, r'href="{{ url_for(\'report_add_page\') }}"\1', content)
        
        # Also try with double quotes for '#' just in case
        pattern_report_dq = r'href="\{\{ "#" \}\}"([^>]*>\s*<i[^>]*></i>\s*Rapor Oluştur)'
        content = re.sub(pattern_report_dq, r'href="{{ url_for(\'report_add_page\') }}"\1', content)

        # Fix Şirketler link
        pattern_companies = r'href="\{\{ \'#\' \}\}"([^>]*>\s*<i[^>]*></i>\s*Şirketler)'
        content = re.sub(pattern_companies, r'href="{{ url_for(\'companies\') }}"\1', content)
        
        pattern_companies_dq = r'href="\{\{ "#" \}\}"([^>]*>\s*<i[^>]*></i>\s*Şirketler)'
        content = re.sub(pattern_companies_dq, r'href="{{ url_for(\'companies\') }}"\1', content)
        
        if content != original_content:
            print("Changes detected. Writing back to file...")
            with sftp.open(filepath, "w") as f:
                f.write(content)
            print("Successfully updated dashboard.html")
        else:
            print("No changes needed or patterns did not match.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_dashboard()
