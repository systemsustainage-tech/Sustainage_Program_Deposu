import os

# 1. Create social_edit.html
social_edit_content = """{% extends "base.html" %}

{% block title %}{{ title }} - SDG{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card shadow-sm border-0">
            <div class="card-body p-4">
                <h3 class="mb-4"><i class="bi bi-plus-circle-fill text-primary"></i> {{ title }}</h3>
                
                <form method="post" class="needs-validation" novalidate>
                    <input type="hidden" name="data_type" value="{{ data_type }}">
                    
                    {% if data_type == 'employee' %}
                    <h5 class="mb-3 text-muted">Çalışan Profili Verisi</h5>
                    <div class="mb-3">
                        <label class="form-label">Çalışan Sayısı</label>
                        <input type="number" class="form-control" name="employee_count" required min="1">
                    </div>
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label">Cinsiyet</label>
                            <select class="form-select" name="gender">
                                <option value="Kadın">Kadın</option>
                                <option value="Erkek">Erkek</option>
                                <option value="Diğer">Diğer</option>
                                <option value="Toplam">Toplam (Belirtilmemiş)</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Departman</label>
                            <input type="text" class="form-control" name="department" placeholder="Örn. Üretim, ofis...">
                        </div>
                    </div>
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label">Yaş Grubu</label>
                            <select class="form-select" name="age_group">
                                <option value="18-30">18-30</option>
                                <option value="30-50">30-50</option>
                                <option value="50+">50+</option>
                                <option value="Tümü">Tümü</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Yıl</label>
                            <input type="number" class="form-control" name="year" value="2024" required>
                        </div>
                    </div>

                    {% elif data_type == 'ohs' %}
                    <h5 class="mb-3 text-muted">İSG Olay/Kaza Kaydı</h5>
                    <div class="mb-3">
                        <label class="form-label">Olay Tipi</label>
                        <select class="form-select" name="incident_type" required>
                            <option value="İş Kazası">İş Kazası</option>
                            <option value="Meslek Hastalığı">Meslek Hastalığı</option>
                            <option value="Ramak Kala">Ramak Kala</option>
                            <option value="Tehlikeli Durum">Tehlikeli Durum</option>
                        </select>
                    </div>
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label">Tarih</label>
                            <input type="date" class="form-control" name="date" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Ciddiyet</label>
                            <select class="form-select" name="severity">
                                <option value="Düşük">Düşük</option>
                                <option value="Orta">Orta</option>
                                <option value="Yüksek">Yüksek</option>
                            </select>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Kayıp İş Günü</label>
                        <input type="number" class="form-control" name="lost_time_days" value="0" min="0">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Açıklama</label>
                        <textarea class="form-control" name="description" rows="3"></textarea>
                    </div>

                    {% elif data_type == 'training' %}
                    <h5 class="mb-3 text-muted">Eğitim Kaydı</h5>
                    <div class="mb-3">
                        <label class="form-label">Eğitim Adı</label>
                        <input type="text" class="form-control" name="training_name" required>
                    </div>
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label">Süre (Saat)</label>
                            <input type="number" class="form-control" name="hours" step="0.5" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Katılımcı Sayısı</label>
                            <input type="number" class="form-control" name="participants" required min="1">
                        </div>
                    </div>
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label">Tarih</label>
                            <input type="date" class="form-control" name="date" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Kategori</label>
                            <input type="text" class="form-control" name="category" placeholder="Örn. İSG, Teknik...">
                        </div>
                    </div>
                    {% endif %}

                    <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                        <a href="{{ url_for('social_module') }}" class="btn btn-light me-md-2">İptal</a>
                        <button type="submit" class="btn btn-primary"><i class="bi bi-save"></i> Kaydet</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

with open(r"c:\SUSTAINAGESERVER\templates\social_edit.html", "w", encoding="utf-8") as f:
    f.write(social_edit_content)
print("social_edit.html created.")

# 2. Update social.html
social_html_content = """{% extends "base.html" %}

{% block title %}{{ _('social_title') }} - SDG{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-12">
        <div class="card shadow-sm border-0">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h2 class="mb-0"><i class="bi bi-people text-primary"></i> {{ _('social_title') }}</h2>
                        <p class="text-muted mt-2 mb-0">{{ _('social_desc') }}</p>
                    </div>
                </div>

                <!-- İstatistik Kartları -->
                <div class="row mt-4">
                    <div class="col-md-4 mb-3">
                        <div class="card h-100 shadow-sm border-start border-4 border-primary">
                            <div class="card-body text-center">
                                <i class="bi bi-people-fill display-4 text-primary mb-3"></i>
                                <h5>{{ _('social_employee_profile') }}</h5>
                                <h3 class="fw-bold">{{ stats.employees }}</h3>
                                <p class="text-muted small">{{ _('social_total_employees') }}</p>
                                <a href="{{ url_for('social_add', type='employee') }}" class="btn btn-sm btn-outline-primary w-100">{{ _('btn_add_data') }}</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card h-100 shadow-sm border-start border-4 border-danger">
                            <div class="card-body text-center">
                                <i class="bi bi-heart-pulse-fill display-4 text-danger mb-3"></i>
                                <h5>{{ _('social_ohs') }}</h5>
                                <h3 class="fw-bold">{{ stats.incidents }}</h3>
                                <p class="text-muted small">{{ _('social_incidents') }}</p>
                                <a href="{{ url_for('social_add', type='ohs') }}" class="btn btn-sm btn-outline-danger w-100">{{ _('btn_add_data') }}</a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4 mb-3">
                        <div class="card h-100 shadow-sm border-start border-4 border-success">
                            <div class="card-body text-center">
                                <i class="bi bi-mortarboard-fill display-4 text-success mb-3"></i>
                                <h5>{{ _('social_training') }}</h5>
                                <h3 class="fw-bold">{{ stats.training_hours | round(1) }}</h3>
                                <p class="text-muted small">{{ _('social_total_hours') }}</p>
                                <a href="{{ url_for('social_add', type='training') }}" class="btn btn-sm btn-outline-success w-100">{{ _('btn_add_data') }}</a>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Son Kayıtlar Tablosu -->
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="card border-0 shadow-sm">
                            <div class="card-header bg-light">
                                <h5 class="mb-0"><i class="bi bi-clock-history"></i> Son Aktiviteler</h5>
                            </div>
                            <div class="card-body p-0">
                                <div class="table-responsive">
                                    <table class="table table-hover mb-0">
                                        <thead class="table-light">
                                            <tr>
                                                <th>Tür</th>
                                                <th>Detay</th>
                                                <th>Tarih/Yıl</th>
                                                <th>Değer</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {% for item in recent_data %}
                                            <tr>
                                                <td>
                                                    {% if item.type == 'employee' %}
                                                    <span class="badge bg-primary">Çalışan</span>
                                                    {% elif item.type == 'ohs' %}
                                                    <span class="badge bg-danger">İSG</span>
                                                    {% elif item.type == 'training' %}
                                                    <span class="badge bg-success">Eğitim</span>
                                                    {% endif %}
                                                </td>
                                                <td>{{ item.detail }}</td>
                                                <td>{{ item.date }}</td>
                                                <td>{{ item.value }}</td>
                                            </tr>
                                            {% else %}
                                            <tr>
                                                <td colspan="4" class="text-center text-muted py-3">Henüz veri girişi yapılmamış.</td>
                                            </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

with open(r"c:\SUSTAINAGESERVER\templates\social.html", "w", encoding="utf-8") as f:
    f.write(social_html_content)
print("social.html updated.")

# 3. Update web_app.py
web_app_path = r"c:\SUSTAINAGESERVER\web_app.py"
with open(web_app_path, "r", encoding="utf-8") as f:
    content = f.read()

# New social_module logic
new_social_module = """@app.route('/social')
def social_module():
    if 'user' not in session: return redirect(url_for('login'))
    
    stats = {'employees': 0, 'incidents': 0, 'training_hours': 0}
    recent_data = []
    
    try:
        conn = get_db()
        # Employees
        try:
            row = conn.execute("SELECT SUM(employee_count) FROM hr_employees").fetchone()
            if row and row[0]: stats['employees'] = row[0]
        except: pass
        
        # OHS
        try:
            row = conn.execute("SELECT COUNT(*) FROM ohs_incidents").fetchone()
            if row and row[0]: stats['incidents'] = row[0]
        except: pass
        
        # Training
        try:
            row = conn.execute("SELECT SUM(hours) FROM training_records").fetchone()
            if row and row[0]: stats['training_hours'] = row[0]
        except: pass
        
        # Recent Data Fetch
        try:
            # HR
            hr_rows = conn.execute("SELECT 'employee' as type, department || ' (' || gender || ')' as detail, year as date, employee_count as value, created_date FROM hr_employees ORDER BY created_date DESC LIMIT 5").fetchall()
            for r in hr_rows: recent_data.append(dict(r))
            
            # OHS
            ohs_rows = conn.execute("SELECT 'ohs' as type, incident_type as detail, date, severity as value, created_date FROM ohs_incidents ORDER BY created_date DESC LIMIT 5").fetchall()
            for r in ohs_rows: recent_data.append(dict(r))
            
            # Training
            tr_rows = conn.execute("SELECT 'training' as type, training_name as detail, date, hours || ' saat' as value, created_date FROM training_records ORDER BY created_date DESC LIMIT 5").fetchall()
            for r in tr_rows: recent_data.append(dict(r))
            
            # Sort all by created_date desc
            recent_data.sort(key=lambda x: x['created_date'], reverse=True)
            recent_data = recent_data[:10]
            
        except Exception as e:
            logging.error(f"Error fetching social recent data: {e}")
            
        conn.close()
    except Exception as e:
        logging.error(f"Error in social stats: {e}")
        
    return render_template('social.html', title='Sosyal Etki', stats=stats, recent_data=recent_data)
"""

# New social_add logic
new_social_add = """@app.route('/social/add', methods=['GET', 'POST'])
def social_add():
    if 'user' not in session: return redirect(url_for('login'))
    
    data_type = request.args.get('type', 'employee')
    
    if request.method == 'POST':
        try:
            dtype = request.form.get('data_type')
            conn = get_db()
            
            if dtype == 'employee':
                count = request.form.get('employee_count')
                gender = request.form.get('gender')
                dept = request.form.get('department')
                age = request.form.get('age_group')
                year = request.form.get('year')
                conn.execute("INSERT INTO hr_employees (employee_count, gender, department, age_group, year, created_date) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (count, gender, dept, age, year))
                
            elif dtype == 'ohs':
                itype = request.form.get('incident_type')
                date = request.form.get('date')
                severity = request.form.get('severity')
                desc = request.form.get('description')
                lost = request.form.get('lost_time_days')
                conn.execute("INSERT INTO ohs_incidents (incident_type, date, severity, description, lost_time_days, created_date) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (itype, date, severity, desc, lost))
                
            elif dtype == 'training':
                name = request.form.get('training_name')
                hours = request.form.get('hours')
                parts = request.form.get('participants')
                date = request.form.get('date')
                cat = request.form.get('category')
                conn.execute("INSERT INTO training_records (training_name, hours, participants, date, category, created_date) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", (name, hours, parts, date, cat))
            
            conn.commit()
            conn.close()
            flash('Veri başarıyla eklendi.', 'success')
            return redirect(url_for('social_module'))
            
        except Exception as e:
            logging.error(f"Error adding social data: {e}")
            flash(f'Hata: {e}', 'danger')
            
    return render_template('social_edit.html', title='Sosyal Veri Girişi', data_type=data_type)
"""

# Replace existing functions
# Use simple string replacement assuming the original code structure matches what we read
old_social_module_str = """@app.route('/social')
def social_module():
    if 'user' not in session: return redirect(url_for('login'))
    stats = {'employees': 0, 'incidents': 0, 'training_hours': 0}
    return render_template('social.html', title='Sosyal Etki', manager_available=bool(MANAGERS.get('social')), stats=stats)"""

old_social_add_str = """@app.route('/social/add')
def social_add():
    flash('Bu özellik henüz aktif değil.', 'info')
    return redirect(url_for('social_module'))"""

if old_social_module_str in content:
    content = content.replace(old_social_module_str, new_social_module)
    print("social_module replaced.")
else:
    print("Warning: social_module not found for exact replacement. Trying regex or fuzzy match not implemented yet.")

if old_social_add_str in content:
    content = content.replace(old_social_add_str, new_social_add)
    print("social_add replaced.")
else:
    print("Warning: social_add not found for exact replacement.")

with open(web_app_path, "w", encoding="utf-8") as f:
    f.write(content)
print("web_app.py updated.")
