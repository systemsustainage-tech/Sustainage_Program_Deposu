
import os

# List of templates identified as missing routes
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

print("# --- GENERATED ROUTES FOR MISSING PAGES ---")
print("# Paste this into web_app.py before the final 'if __name__ == ...'")
print("")

for t in missing_templates:
    route_name = t.replace('.html', '')
    # Convert underscores to hyphens for URL if preferred, but let's stick to simple mapping first
    # Or keep underscores to match template name
    
    # Function name must be valid python identifier
    func_name = route_name
    
    print(f"@app.route('/{route_name}')")
    print("@require_company_context")
    print(f"def {func_name}():")
    print(f"    return render_template('{t}')")
    print("")
