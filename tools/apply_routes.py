
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

WEB_APP_PATH = 'web_app.py'

missing_templates = [
    'advanced_calculation.html', 'advanced_inventory.html', 'advanced_reporting.html', 'ai.html', 'ai_reports.html',
    'analysis.html', 'audit_logs.html', 'auditor.html', 'automation.html', 'benchmark.html',
    'cbam.html', 'community.html', 'company_stakeholder_survey.html', 'consumer.html',
    'data_collection.html', 'data_import.html', 'data_provenance.html', 'database.html',
    'digital_security.html', 'document_processing.html', 'emergency.html', 'emission_reduction.html',
    'environmental.html', 'erp_integration.html', 'esg_settings.html', 'eu_taxonomy.html',
    'fair_operating.html', 'file_manager.html', 'forms.html', 'framework_mapping.html',
    'human_rights.html', 'innovation.html', 'integration.html', 'labor.html',
    'lca.html', 'lca_assessment.html', 'lca_product.html', 'mapping.html',
    'notifications.html', 'policy_library.html', 'product_technology.html', 'quality.html',
    'realtime.html', 'realtime_device.html', 'regulation.html', 'reporting.html',
    'risk_management.html', 'sasb.html', 'scenario_analysis.html', 'scope3.html',
    'security.html', 'skdm.html', 'stakeholder.html', 'stakeholder_portal.html',
    'stakeholder_survey.html', 'standards.html', 'strategic.html',
    'supply_chain_profile.html', 'survey_public.html', 'tracking.html', 'training.html',
    'tsrs.html', 'ungc.html', 'unified_report.html', 'user_experience.html',
    'validation.html', 'workflow.html'
]

def generate_routes_code():
    code = []
    code.append("\n# --- AUTO-GENERATED ROUTES FOR MISSING PAGES ---")
    for t in missing_templates:
        route_name = t.replace('.html', '')
        func_name = route_name
        
        code.append(f"@app.route('/{route_name}')")
        code.append("@require_company_context")
        code.append(f"def {func_name}():")
        code.append(f"    return render_template('{t}')")
        code.append("")
    return "\n".join(code)

def apply_routes():
    with open(WEB_APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "# --- AUTO-GENERATED ROUTES FOR MISSING PAGES ---" in content:
        print("Routes seem to be already applied.")
        return

    # Find insertion point: before if __name__ == '__main__':
    if "if __name__ == '__main__':" in content:
        parts = content.split("if __name__ == '__main__':")
        new_content = parts[0] + generate_routes_code() + "\nif __name__ == '__main__':" + parts[1]
        
        with open(WEB_APP_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully added routes to web_app.py")
    else:
        print("Could not find insertion point in web_app.py")

if __name__ == '__main__':
    apply_routes()
