import os
import sys

DESKTOP_MODULES_PATH = r'c:\sdg\modules'
WEB_ROOT = r'c:\SUSTAINAGESERVER'
TEMPLATES_PATH = os.path.join(WEB_ROOT, 'templates')

def get_desktop_modules():
    if not os.path.exists(DESKTOP_MODULES_PATH):
        print(f"Error: {DESKTOP_MODULES_PATH} does not exist.")
        return []
    return [d for d in os.listdir(DESKTOP_MODULES_PATH) if os.path.isdir(os.path.join(DESKTOP_MODULES_PATH, d)) and not d.startswith('__')]

def create_template(module_name):
    template_path = os.path.join(TEMPLATES_PATH, f'{module_name}.html')
    if os.path.exists(template_path):
        print(f"Template exists: {module_name}")
        return

    content = f"""{{% extends "base.html" %}}

{{% block title %}}{{{{ _('{module_name}_title', '{module_name.replace('_', ' ').title()}') }}}} - SDG{{% endblock %}}

{{% block content %}}
<div class="mb-3">
    <a href="{{{{ url_for('dashboard') }}}}" class="btn btn-sm btn-outline-secondary">
        <i class="bi bi-arrow-left"></i> {{{{ _('btn_back') }}}}
    </a>
</div>
<div class="row mb-4">
    <div class="col-md-12">
        <div class="d-flex justify-content-between align-items-center">
            <h1><i class="fas fa-cube me-2"></i>{{{{ _('{module_name}_title', '{module_name.replace('_', ' ').title()}') }}}}</h1>
            <div>
                <span class="badge bg-{{{{ 'success' if manager_available else 'secondary' }}}}">
                    {{{{ _('module_active_badge') if manager_available else _('module_passive_badge') }}}}
                </span>
            </div>
        </div>
        <p class="lead text-muted">{{{{ _('{module_name}_desc', 'Module description for {module_name.replace('_', ' ').title()}') }}}}</p>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card shadow-sm border-0">
            <div class="card-body">
                <div class="text-center py-5">
                    <i class="bi bi-cone-striped display-1 text-warning mb-3"></i>
                    <h3>{{{{ _('module_under_construction') }}}}</h3>
                    <p class="text-muted">{{{{ _('module_coming_soon_desc', 'Bu modülün web arayüzü entegrasyonu devam etmektedir.') }}}}</p>
                </div>
            </div>
        </div>
    </div>
</div>
{{% endblock %}}
"""
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created template: {module_name}")
    except Exception as e:
        print(f"Error creating template for {module_name}: {e}")

def main():
    modules = get_desktop_modules()
    print(f"Found {len(modules)} modules.")
    for mod in modules:
        create_template(mod)

if __name__ == "__main__":
    main()
