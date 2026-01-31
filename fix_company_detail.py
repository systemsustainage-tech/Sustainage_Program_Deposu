import paramiko
import re

def fix_company_detail():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        filepath = "/var/www/sustainage/templates/company_detail.html"
        
        print(f"Reading {filepath}...")
        with sftp.open(filepath, "r") as f:
            content = f.read().decode()
            
        original_content = content
        
        # 1. Fix create_report -> report_add_page
        content = content.replace("url_for('create_report')", "url_for('report_add_page')")
        
        # 2. Fix view_report -> '#'
        # Regex to handle parameters: url_for('view_report', report_id=report.id)
        content = re.sub(r"url_for\('view_report'[^)]*\)", "'#'", content)
        
        # 3. Fix download_report -> '#'
        content = re.sub(r"url_for\('download_report'[^)]*\)", "'#'", content)
        
        # 4. Fix report_delete -> '#'
        content = re.sub(r"url_for\('report_delete'[^)]*\)", "'#'", content)
        
        if content != original_content:
            print("Changes detected. Writing back to file...")
            with sftp.open(filepath, "w") as f:
                f.write(content)
            print("Successfully updated company_detail.html")
        else:
            print("No changes needed.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_company_detail()
