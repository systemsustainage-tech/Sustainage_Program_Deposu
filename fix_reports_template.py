import paramiko
import re

def fix_reports_template():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # 1. Fix reports.html
        print("Fixing reports.html...")
        remote_path = '/var/www/sustainage/templates/reports.html'
        with sftp.open(remote_path, 'r') as f:
            content = f.read().decode()
            
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if "title=\"Görüntüle\"" in line and ("href=\"'#'\"" in line or "href=\"\'#\'\"" in line):
                line = line.replace("href=\"'#'\"", "href=\"{{ url_for('report_download', report_id=report['id']) }}\"")
            elif "title=\"İndir\"" in line and ("href=\"'#'\"" in line or "href=\"\'#\'\"" in line):
                line = line.replace("href=\"'#'\"", "href=\"{{ url_for('report_download', report_id=report['id']) }}\"")
            elif "action=\"'#'\"" in line:
                line = line.replace("action=\"'#'\"", "action=\"{{ url_for('report_delete', report_id=report['id']) }}\"")
            
            new_lines.append(line)
            
        new_content = '\n'.join(new_lines)
        if new_content != content:
            with sftp.open(remote_path, 'w') as f:
                f.write(new_content)
            print("reports.html updated.")
        else:
            print("reports.html no changes needed (or pattern mismatch).")
            
        # 2. Fix dashboard.html
        print("Fixing dashboard.html...")
        remote_path = '/var/www/sustainage/templates/dashboard.html'
        with sftp.open(remote_path, 'r') as f:
            content = f.read().decode()
            
        # Replace href="{{ '#' }}" with href="#"
        # Using double quotes for outer string to handle single quotes inside
        new_content = content.replace("href=\"{{ '#' }}\"", "href=\"#\"")
        new_content = new_content.replace("href=\"{{ \'#\' }}\"", "href=\"#\"")
        
        if new_content != content:
            with sftp.open(remote_path, 'w') as f:
                f.write(new_content)
            print("dashboard.html updated.")
        else:
            print("dashboard.html no changes needed.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_reports_template()
