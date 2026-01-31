import os
import glob

TEMPLATE_DIR = r'c:\SUSTAINAGESERVER\templates'
SEARCH_STR = '{{ _(\'module_under_construction\') }}'

NEW_CONTENT = """
                    {% if stats or records %}
                        <!-- Dashboard View -->
                        <div class="row mb-4">
                            {% if stats %}
                            <div class="col-12 mb-4">
                                <div class="card">
                                    <div class="card-header">
                                        <h5 class="mb-0">{{ _('statistics', 'İstatistikler') }}</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            {% for key, value in stats.items() %}
                                            <div class="col-md-3 mb-3">
                                                <div class="border rounded p-3 text-center bg-light">
                                                    <h6 class="text-muted text-uppercase small">{{ key|replace('_', ' ')|title }}</h6>
                                                    <h3 class="mb-0 text-primary">{{ value }}</h3>
                                                </div>
                                            </div>
                                            {% endfor %}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endif %}

                            {% if records %}
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header d-flex justify-content-between align-items-center">
                                        <h5 class="mb-0">{{ _('records', 'Kayıtlar') }}</h5>
                                        <button class="btn btn-sm btn-primary">
                                            <i class="fas fa-plus"></i> {{ _('add_new', 'Yeni Ekle') }}
                                        </button>
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-hover">
                                                <thead>
                                                    <tr>
                                                        {% if columns %}
                                                            {% for col in columns %}
                                                            <th>{{ col|replace('_', ' ')|title }}</th>
                                                            {% endfor %}
                                                        {% else %}
                                                            <th>{{ _('details', 'Detaylar') }}</th>
                                                        {% endif %}
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {% for record in records %}
                                                    <tr>
                                                        {% if columns %}
                                                            {% for col in columns %}
                                                                {% if record is mapping %}
                                                                    <td>{{ record[col] }}</td>
                                                                {% else %}
                                                                    <td>{{ record }}</td>
                                                                {% endif %}
                                                            {% endfor %}
                                                        {% else %}
                                                            <td>{{ record }}</td>
                                                        {% endif %}
                                                    </tr>
                                                    {% endfor %}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endif %}
                        </div>
                    {% else %}
                        <!-- Fallback to Under Construction if no data -->
                        <div class="text-center py-5">
                            <i class="bi bi-cone-striped display-1 text-warning mb-3"></i>
                            <h3>{{ _('module_under_construction') }}</h3>
                            <p class="text-muted">{{ _('module_coming_soon_desc', 'Bu modülün web arayüzü entegrasyonu devam etmektedir.') }}</p>
                            <p class="small text-muted">{{ _('no_data_msg', 'Veri bulunamadı veya modül henüz aktif değil.') }}</p>
                        </div>
                    {% endif %}
"""

def update_templates():
    files = glob.glob(os.path.join(TEMPLATE_DIR, '*.html'))
    count = 0
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if SEARCH_STR in content and 'Stats' not in content:
            # Simple heuristic to find the div containing the under construction message
            # We'll replace the inner content of the card-body or the specific div
            
            # Find the block to replace
            start_marker = '<div class="text-center py-5">'
            end_marker = '</div>'
            
            if start_marker in content:
                # We need to be careful about matching the correct closing div
                # Instead, let's just replace the specific text block if possible
                # But we want to inject the IF check around it.
                
                # Let's replace the whole "text-center py-5" div
                # This is a bit risky with simple string replacement if nested divs exist
                # But looking at ungc.html, it seems simple.
                
                # Let's try to locate the specific segment
                idx = content.find(start_marker)
                if idx != -1:
                    # Find the closing div for this one. 
                    # Assuming standard indentation or simple structure.
                    # It closes at the next </div> usually in these templates.
                    
                    # Actually, let's just replace the whole card-body content if it looks like the template
                    card_body_start = '<div class="card-body">'
                    if card_body_start in content:
                         parts = content.split(card_body_start)
                         if len(parts) > 1:
                             # Check if "module_under_construction" is in the second part
                             if 'module_under_construction' in parts[1]:
                                 # We found the right place. 
                                 # Now let's reconstruct.
                                 # We will replace the content inside card-body.
                                 # But we need to find where card-body ends.
                                 # It usually ends with </div> on a new line.
                                 
                                 # A safer approach: Replace the known under construction block
                                 old_block = """<div class="text-center py-5">
                    <i class="bi bi-cone-striped display-1 text-warning mb-3"></i>
                    <h3>{{ _('module_under_construction') }}</h3>
                    <p class="text-muted">{{ _('module_coming_soon_desc', 'Bu modülün web arayüzü entegrasyonu devam etmektedir.') }}</p>
                </div>"""
                                 # Normalizing whitespace might be needed
                                 
                                 # Let's try regex or just simple replacement if exact match
                                 # The file content I read has indentation.
                                 
                                 import re
                                 # Regex to match the under construction div
                                 pattern = re.compile(r'<div class="text-center py-5">.*?</div>', re.DOTALL)
                                 
                                 if pattern.search(content):
                                     new_file_content = pattern.sub(NEW_CONTENT, content)
                                     with open(file_path, 'w', encoding='utf-8') as f_out:
                                         f_out.write(new_file_content)
                                     print(f"Updated {os.path.basename(file_path)}")
                                     count += 1
                                 else:
                                     print(f"Pattern not found in {os.path.basename(file_path)}")
    
    print(f"Total updated: {count}")

if __name__ == '__main__':
    update_templates()
