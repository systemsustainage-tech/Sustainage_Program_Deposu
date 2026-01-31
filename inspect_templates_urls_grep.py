import paramiko
import re
import sys

def inspect_urls_grep():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    valid_endpoints = {
        'static', 'index', 'login', 'logout', 'forgot_password', 'dashboard', 
        'data', 'data_add', 'users', 'user_add', 'user_edit', 'user_delete', 
        'companies', 'company_add', 'company_detail', 'reports', 'report_add_page', 
        'sdg_module', 'gri_module', 'social_module', 'social_add', 
        'governance_module', 'governance_add', 'carbon_module', 'energy_module', 
        'esg_module', 'cbam_module', 'csrd_module', 'taxonomy_module', 
        'waste_module', 'water_module', 'biodiversity_module', 
        'economic_module', 'economic_add', 'supply_chain_module', 
        'cdp_module', 'issb_module', 'iirc_module', 'esrs_module', 
        'tcfd_module', 'tnfd_module'
    }

    try:
        client.connect(hostname, username=username, password=password)
        
        print("Grepping url_for in templates...")
        # -r: recursive, -o: only matching, -h: no filename (wait, I want filename)
        # Actually just grep normally to see context
        cmd = "grep -r \"url_for\" /var/www/sustainage/templates"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        output = stdout.read().decode()
        lines = output.split('\n')
        
        print(f"Found {len(lines)} lines with url_for.")
        
        issues = []
        checked_count = 0
        
        for line in lines:
            if not line.strip(): continue
            
            # Line format: /path/to/file: content
            parts = line.split(':', 1)
            if len(parts) < 2: continue
            
            filename = parts[0].split('/')[-1]
            content = parts[1]
            
            # Find matches
            matches = re.finditer(r"url_for\(['\"]([\w_]+)['\"]", content)
            
            for match in matches:
                endpoint = match.group(1)
                checked_count += 1
                if endpoint not in valid_endpoints:
                    issues.append(f"{filename}: Unknown endpoint '{endpoint}' in line: {content.strip()}")

        print(f"Checked {checked_count} url_for calls.")
        
        if issues:
            print("\nFound potential issues:")
            for issue in issues:
                print(issue)
        else:
            print("\nNo unknown endpoints found!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_urls_grep()
