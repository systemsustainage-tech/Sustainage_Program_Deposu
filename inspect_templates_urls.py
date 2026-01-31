import paramiko
import re
import sys

def inspect_urls():
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
        sftp = client.open_sftp()
        
        # Get list of templates
        templates = sftp.listdir('/var/www/sustainage/templates')
        html_files = [f for f in templates if f.endswith('.html')]
        
        print(f"Scanning {len(html_files)} templates...")
        sys.stdout.flush()
        
        issues = []
        found_count = 0
        
        for i, template in enumerate(html_files):
            print(f"Checking {template} ({i+1}/{len(html_files)})...")
            sys.stdout.flush()
            try:
                # Use get instead of open
                local_temp = f"c:\\SUSTAINAGESERVER\\temp_inspect_{template}"
                sftp.get(f"/var/www/sustainage/templates/{template}", local_temp)
                
                with open(local_temp, "r", encoding="utf-8") as f:
                    content = f.read()
                
                import os
                if os.path.exists(local_temp):
                    os.remove(local_temp)
                
                # Find all url_for calls
                matches = re.finditer(r"url_for\(['\"]([\w_]+)['\"]", content)
                
                for match in matches:
                    endpoint = match.group(1)
                    found_count += 1
                    if endpoint not in valid_endpoints:
                        issues.append(f"{template}: Unknown endpoint '{endpoint}'")
                        
            except Exception as e:
                print(f"Error reading {template}: {e}")

        print(f"Total url_for calls checked: {found_count}")

        if issues:
            print("\nFound potential issues:")
            for issue in issues:
                print(issue)
        else:
            print("\nNo unknown endpoints found!")
            
        print("Done.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_urls()
