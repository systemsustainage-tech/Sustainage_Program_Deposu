import paramiko
import re

def restore_dashboard():
    local_path = 'c:\\SUSTAINAGESERVER\\dashboard_local.html'
    
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define replacements based on context
    # pattern: (some context) ... (href="{{ '#' }}")
    # We will use regex to find the block and replace the href.
    
    # Mapping of translation key to endpoint
    mapping = {
        "module_carbon": "carbon_module",
        "module_energy": "energy_module",
        "module_waste": "waste_module",
        "module_water": "water_module",
        "module_biodiversity": "biodiversity_module",
        "module_social_impact": "social_module",
        "module_corporate_governance": "governance_module",
        "module_supply_chain": "supply_chain_module",
        "module_economic_value": "economic_module",
        "module_esg_score": "esg_module",
        "module_cbam": "cbam_module",
        "module_csrd": "csrd_module",
        "module_eu_taxonomy": "taxonomy_module",
        "module_gri": "gri_module",
        "module_sdg": "sdg_module",
        "module_tcfd": "tcfd_module",
        "module_tnfd": "tnfd_module",
        "module_cdp": "cdp_module",
        # Quick access
        "create_report_btn": "reports",
        "companies_btn": "companies"
    }
    
    # Also explicitly fix known broken endpoints that might be hardcoded in HTML
    # <a href="{{ url_for('carbon') }}"
    content = content.replace("url_for('carbon')", "url_for('carbon_module')")
    content = content.replace("url_for('energy')", "url_for('energy_module')")
    content = content.replace("url_for('waste')", "url_for('waste_module')")
    content = content.replace("url_for('water')", "url_for('water_module')")
    content = content.replace("url_for('biodiversity')", "url_for('biodiversity_module')")
    content = content.replace("url_for('social')", "url_for('social_module')")
    content = content.replace("url_for('governance')", "url_for('governance_module')")
    content = content.replace("url_for('supply_chain')", "url_for('supply_chain_module')")
    content = content.replace("url_for('economic')", "url_for('economic_module')")
    content = content.replace("url_for('esg')", "url_for('esg_module')")
    content = content.replace("url_for('cbam')", "url_for('cbam_module')")
    content = content.replace("url_for('csrd')", "url_for('csrd_module')")
    content = content.replace("url_for('taxonomy')", "url_for('taxonomy_module')")
    content = content.replace("url_for('gri')", "url_for('gri_module')")
    content = content.replace("url_for('sdg')", "url_for('sdg_module')")
    content = content.replace("url_for('tcfd')", "url_for('tcfd_module')")
    content = content.replace("url_for('tnfd')", "url_for('tnfd_module')")
    content = content.replace("url_for('cdp')", "url_for('cdp_module')")
    
    # Naive approach: Split by card/section and replace
    # But since the structure is consistent: 
    # <h6 class="card-title">{{ _('KEY') }}</h6>\s*<a href="{{ '#' }}"
    # or for buttons:
    # <a href="{{ '#' }}" ...>...{{ _('KEY') }}
    
    # Let's try replacing specific patterns
    
    for key, endpoint in mapping.items():
        # Pattern 1: Card title followed by link
        # <h6 class="card-title">{{ _('module_carbon') }}</h6>\n                <a href="{{ '#' }}"
        pattern1 = f'({{ _(\'{key}\') }})([\\s\\S]*?)href="{{{{" \'#\' }}}}"'
        replacement1 = f'\\1\\2href="{{{{ url_for(\'{endpoint}\') }}}}"'
        
        # Pattern 2: Link containing the text (for buttons)
        # <a href="{{ '#' }}" ...>...{{ _('create_report_btn') }}
        # This is harder because the href comes BEFORE the text.
        # <a href="{{ '#' }}" class="btn ...">\n                            <i ...></i> {{ _('create_report_btn') }}
        
        pattern2 = f'href="{{{{" \'#\' }}}}"([\\s\\S]*?{{{{ _\\(\'{key}\'\\) }}}})'
        replacement2 = f'href="{{{{ url_for(\'{endpoint}\') }}}}"\\1'
        
        # Apply pattern 1
        content = re.sub(pattern1, replacement1, content)
        
        # Apply pattern 2
        content = re.sub(pattern2, replacement2, content)
        
    # Write back locally
    with open(local_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Local file patched.")

    # Upload
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    
    sftp = client.open_sftp()
    remote_path = '/var/www/sustainage/templates/dashboard.html'
    
    print(f"Uploading to {remote_path}...")
    sftp.put(local_path, remote_path)
    print("Upload complete.")
    
    sftp.close()
    client.close()

if __name__ == "__main__":
    restore_dashboard()
