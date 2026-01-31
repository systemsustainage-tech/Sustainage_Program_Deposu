import paramiko

def update_waste_module():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # 1. Update web_app.py
        print("Updating web_app.py...")
        remote_path = '/var/www/sustainage/web_app.py'
        with sftp.open(remote_path, 'r') as f:
            content = f.read().decode()
            
        old_route = """@app.route('/waste')
def waste_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('waste.html', title='Atık Yönetimi', manager_available=bool(MANAGERS.get('waste')))"""

        new_route = """@app.route('/waste')
def waste_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    stats = {'total_waste': 0, 'by_type': {}, 'recent': []}
    try:
        conn = get_db()
        # Total
        total = conn.execute("SELECT SUM(amount) FROM waste_generation").fetchone()[0]
        stats['total_waste'] = round(total, 2) if total else 0
        
        # By Type
        rows = conn.execute("SELECT waste_type, SUM(amount) as total FROM waste_generation GROUP BY waste_type").fetchall()
        stats['by_type'] = {row['waste_type']: round(row['total'], 2) for row in rows}
        
        # Recent
        stats['recent'] = conn.execute("SELECT * FROM waste_generation ORDER BY date DESC LIMIT 10").fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Waste stats error: {e}")
        
    return render_template('waste.html', title='Atık Yönetimi', manager_available=bool(MANAGERS.get('waste')), stats=stats)"""

        if old_route in content:
            content = content.replace(old_route, new_route)
            with sftp.open(remote_path, 'w') as f:
                f.write(content)
            print("web_app.py updated.")
        else:
            print("Could not find exact match for old route. Trying regex/manual check might be needed.")
            # Fallback: Find by signature if exact match fails (due to whitespace)
            import re
            pattern = r"@app\.route\('/waste'\)\s+def waste_module\(\):.+?return render_template\('waste\.html'.+?\)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                print("Found via regex, replacing...")
                content = content.replace(match.group(0), new_route)
                with sftp.open(remote_path, 'w') as f:
                    f.write(content)
                print("web_app.py updated via regex.")
            else:
                print("Failed to update web_app.py: Route not found.")

        # 2. Update waste.html
        print("Updating waste.html...")
        html_path = '/var/www/sustainage/templates/waste.html'
        
        new_html = """{% extends "base.html" %}

{% block title %}Atık Yönetimi - SDG Platform{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-12">
        <div class="d-flex justify-content-between align-items-center">
            <h1><i class="fas fa-trash-alt me-2"></i>Atık Yönetimi</h1>
            <div>
                <a href="{{ url_for('data_add', type='waste') }}" class="btn btn-primary">
                    <i class="fas fa-plus-circle me-1"></i> Atık Verisi Ekle
                </a>
            </div>
        </div>
        <p class="lead text-muted">Atık oluşumunu ve geri dönüşümü takip edin.</p>
    </div>
</div>

{% if manager_available %}

<!-- Stats Cards -->
<div class="row mb-4">
    <div class="col-md-4">
        <div class="card bg-light border-0 shadow-sm h-100">
            <div class="card-body text-center">
                <h5 class="text-muted mb-3">Toplam Atık</h5>
                <h2 class="display-4 fw-bold text-primary">{{ stats.total_waste }}</h2>
                <p class="text-muted">kg/ton (Karma)</p>
            </div>
        </div>
    </div>
    <div class="col-md-8">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white">
                <h5 class="mb-0">Atık Türüne Göre Dağılım</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for type, amount in stats.by_type.items() %}
                    <div class="col-md-4 mb-3">
                        <div class="p-3 border rounded bg-light text-center">
                            <strong class="d-block text-truncate" title="{{ type }}">{{ type }}</strong>
                            <span class="fs-4 text-dark">{{ amount }}</span>
                        </div>
                    </div>
                    {% else %}
                    <div class="col-12 text-center text-muted">Henüz veri yok.</div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Recent Data Table -->
<div class="card border-0 shadow-sm">
    <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Son Kayıtlar</h5>
        <a href="{{ url_for('data') }}" class="btn btn-sm btn-outline-secondary">Tümünü Gör</a>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
                <thead class="bg-light">
                    <tr>
                        <th>Tarih</th>
                        <th>Atık Türü</th>
                        <th>Miktar</th>
                        <th>Birim</th>
                        <th>Bertaraf Yöntemi</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in stats.recent %}
                    <tr>
                        <td>{{ row['date'] }}</td>
                        <td>{{ row['waste_type'] }}</td>
                        <td class="fw-bold">{{ row['amount'] }}</td>
                        <td>{{ row['unit'] }}</td>
                        <td><span class="badge bg-secondary">{{ row['disposal_method'] }}</span></td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="5" class="text-center py-4 text-muted">Henüz veri girişi yapılmamış.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

{% else %}
<div class="alert alert-warning">
    <h4 class="alert-heading">Modül Yükleme Hatası</h4>
    <p>Atık modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.</p>
</div>
{% endif %}
{% endblock %}
"""
        with sftp.open(html_path, 'w') as f:
            f.write(new_html)
        print("waste.html updated.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    update_waste_module()
