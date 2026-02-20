import paramiko

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def patch_dashboard():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        # Read the file
        print("Reading dashboard.html...")
        sftp = client.open_sftp()
        remote_path = '/var/www/sustainage/templates/dashboard.html'
        with sftp.open(remote_path, 'r') as f:
            content = f.read().decode('utf-8')
        
        # Replace broken routes with '#' to prevent 500 errors
        replacements = [
            ("url_for('carbon')", "url_for('carbon_module')"),
            ("url_for('energy')", "url_for('energy_module')"),
            ("url_for('water')", "url_for('water_module')"),
            ("url_for('waste')", "url_for('waste_module')"),
            # ("url_for('companies')", "url_for('companies')"), # Seems correct
            # ("url_for('reports')", "url_for('reports')"), # Seems correct
            ("url_for('messages')", "'#'"), # Not found
            ("url_for('help_page')", "'#'"), # Not found
            ("url_for('biodiversity')", "url_for('biodiversity_module')"),
            ("url_for('economic')", "url_for('economic_module')"),
            ("url_for('supply_chain')", "url_for('supply_chain_module')"),
            ("url_for('cdp')", "url_for('cdp_module')"),
            ("url_for('issb')", "url_for('issb_module')"),
            ("url_for('iirc')", "url_for('iirc_module')"),
            ("url_for('esrs')", "url_for('esrs_module')"),
            ("url_for('tcfd')", "url_for('tcfd_module')"),
            ("url_for('tnfd')", "url_for('tnfd_module')"),
            ("url_for('social')", "url_for('social_module')"),
            ("url_for('governance')", "url_for('governance_module')"),
            ("url_for('esg')", "url_for('esg_module')"),
            ("url_for('cbam')", "url_for('cbam_module')"),
            ("url_for('csrd')", "url_for('csrd_module')"),
            ("url_for('taxonomy')", "url_for('taxonomy_module')"),
            ("url_for('gri')", "url_for('gri_module')"),
            ("url_for('sdg')", "url_for('sdg_module')"),
            ("url_for('ifrs')", "'#'") # Not found
        ]
        
        new_content = content
        for old, new in replacements:
            if old in new_content:
                print(f"Patching {old} -> {new}")
                new_content = new_content.replace(old, new)
            else:
                print(f"Skipping {old} (not found)")
        
        # Write back
        print("Writing patched dashboard.html...")
        with sftp.open(remote_path, 'w') as f:
            f.write(new_content.encode('utf-8'))
            
        print("Patch complete.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    patch_dashboard()