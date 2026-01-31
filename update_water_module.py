import paramiko

def update_water_module():
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
            
        old_route = """@app.route('/water')
def water_module():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('water.html', title='Su Yönetimi', manager_available=bool(MANAGERS.get('water')))"""

        new_route = """@app.route('/water')
def water_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    stats = {'total_water': 0, 'by_source': {}, 'recent': []}
    try:
        conn = get_db()
        # Total
        total = conn.execute("SELECT SUM(consumption_amount) FROM water_consumption").fetchone()[0]
        stats['total_water'] = round(total, 2) if total else 0
        
        # By Source
        rows = conn.execute("SELECT source_type, SUM(consumption_amount) as total FROM water_consumption GROUP BY source_type").fetchall()
        stats['by_source'] = {row['source_type']: round(row['total'], 2) for row in rows}
        
        # Recent
        stats['recent'] = conn.execute("SELECT * FROM water_consumption ORDER BY created_at DESC LIMIT 10").fetchall()
        conn.close()
    except Exception as e:
        logging.error(f"Water stats error: {e}")
        
    return render_template('water.html', title='Su Yönetimi', manager_available=bool(MANAGERS.get('water')), stats=stats)"""

        if old_route in content:
            content = content.replace(old_route, new_route)
            with sftp.open(remote_path, 'w') as f:
                f.write(content)
            print("web_app.py updated.")
        else:
            # Fallback regex
            import re
            pattern = r"@app\.route\('/water'\)\s+def water_module\(\):.+?return render_template\('water\.html'.+?\)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                print("Found via regex, replacing...")
                content = content.replace(match.group(0), new_route)
                with sftp.open(remote_path, 'w') as f:
                    f.write(content)
                print("web_app.py updated via regex.")
            else:
                print("Failed to update web_app.py: Route not found.")

        # 2. Update water.html
        print("Updating water.html...")
        html_path = '/var/www/sustainage/templates/water.html'
        
        new_html = """{% extends "base.html" %}

{% block title %}Su Yönetimi - SDG Platform{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-12">
        <div class="d-flex justify-content-between align-items-center">
            <h1><i class="fas fa-tint me-2" style="color: #0dcaf0;"></i>Su Yönetimi</h1>
            <div>
                <a href="{{ url_for('data_add', type='water') }}" class="btn btn-primary">
                    <i class="fas fa-plus-circle me-1"></i> Su Verisi Ekle
                </a>
            </div>
        </div>
        <p class="lead text-muted">Su tüketimini ve ayak izinizi yönetin.</p>
    </div>
</div>

{% if manager_available %}

<!-- Stats Cards -->
<div class="row mb-4">
    <div class="col-md-4">
        <div class="card bg-light border-0 shadow-sm h-100">
            <div class="card-body text-center">
                <h5 class="text-muted mb-3">Toplam Su Tüketimi</h5>
                <h2 class="display-4 fw-bold text-info">{{ stats.total_water }}</h2>
                <p class="text-muted">m³ (Toplam)</p>
            </div>
        </div>
    </div>
    <div class="col-md-8">
        <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white">
                <h5 class="mb-0">Kaynak Türüne Göre Dağılım</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    {% for source, amount in stats.by_source.items() %}
                    <div class="col-md-4 mb-3">
                        <div class="p-3 border rounded bg-light text-center">
                            <strong class="d-block text-truncate" title="{{ source }}">{{ source }}</strong>
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
                        <th>Kaynak Türü</th>
                        <th>Miktar</th>
                        <th>Birim</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in stats.recent %}
                    <tr>
                        <td>{{ row['created_at'][:10] if row['created_at'] else row['year']|string + '-' + row['month']|string }}</td>
                        <td>{{ row['source_type'] }}</td>
                        <td class="fw-bold">{{ row['consumption_amount'] }}</td>
                        <td>{{ row['unit'] }}</td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="4" class="text-center py-4 text-muted">Henüz veri girişi yapılmamış.</td>
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
    <p>Su yönetimi modülü şu anda kullanılamıyor. Lütfen sistem yöneticisi ile iletişime geçin.</p>
</div>
{% endif %}
{% endblock %}
"""
        with sftp.open(html_path, 'w') as f:
            f.write(new_html)
        print("water.html updated.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    update_water_module()
