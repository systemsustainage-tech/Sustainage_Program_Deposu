
import os
import re

dashboard_path = r'c:\SUSTAINAGESERVER\templates\dashboard.html'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Map translation keys to module_stats keys
mapping = {
    "module_carbon": "carbon",
    "module_energy": "energy",
    "module_waste": "waste",
    "module_water": "water",
    "module_biodiversity": "biodiversity",
    "module_social_impact": "social",
    "module_corporate_governance": "governance",
    "module_supply_chain": "supply_chain",
    "module_economic_value": "economic",
    "module_esg_score": "esg",
    "module_cbam": "cbam",
    "module_csrd": "csrd",
    "module_eu_taxonomy": "taxonomy",
    "module_gri": "gri",
    "module_sdg": "sdg",
    "module_esrs": "esrs",
    "module_prioritization": "prioritization",
    "module_ifrs": "ifrs",
    "module_tcfd": "tcfd",
    "module_tnfd": "tnfd",
    "module_cdp": "cdp"
}

for trans_key, stats_key in mapping.items():
    pattern = f'<h6 class="card-title">{{{{ _(\'{trans_key}\') }}}}</h6>'
    replacement = f"""<h6 class="card-title">{{{{ _('{trans_key}') }}}}</h6>
                <div class="progress mt-2 mb-1" style="height: 5px;">
                    <div class="progress-bar bg-success" role="progressbar" style="width: {{{{ module_stats.get('{stats_key}', 0) }}}}%" aria-valuenow="{{{{ module_stats.get('{stats_key}', 0) }}}}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
                <small class="text-muted">%{{{{ module_stats.get('{stats_key}', 0) }}}}</small>"""
    
    if pattern in content:
        content = content.replace(pattern, replacement)
    else:
        print(f"Warning: Could not find pattern for {trans_key}")

with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Dashboard updated successfully.")
