import os

WEB_APP_PATH = r"c:\SUSTAINAGESERVER\web_app.py"

HEALTH_CHECK_CODE = """

# --- SYSTEM HEALTH CHECK ROUTE ---
@app.route('/system/health')
def system_health_check():
    results = {
        'status': 'ok',
        'checks': {}
    }
    
    # 1. Database Check
    try:
        conn = get_db()
        cursor = conn.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        results['checks']['database'] = 'ok'
    except Exception as e:
        results['checks']['database'] = str(e)
        results['status'] = 'error'

    # 2. Template Folder Check
    template_dir = os.path.join(BASE_DIR, 'templates')
    if os.path.exists(template_dir) and os.path.isdir(template_dir):
         results['checks']['templates_dir'] = 'ok'
    else:
         results['checks']['templates_dir'] = 'missing'
         results['status'] = 'error'

    # 3. Critical Tables Check
    required_tables = ['users', 'companies', 'online_surveys', 'survey_questions']
    try:
        conn = get_db()
        cursor = conn.cursor()
        existing_tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        conn.close()
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            results['checks']['missing_tables'] = missing_tables
            results['status'] = 'error'
        else:
            results['checks']['tables'] = 'ok'
    except Exception:
        pass

    return jsonify(results)
"""

def add_health_check():
    with open(WEB_APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if '/system/health' in content:
        print("Health check route already exists.")
        return

    # Append to end or before app.run
    if "if __name__ == '__main__':" in content:
        parts = content.split("if __name__ == '__main__':")
        new_content = parts[0] + HEALTH_CHECK_CODE + "\nif __name__ == '__main__':" + parts[1]
    else:
        new_content = content + HEALTH_CHECK_CODE
        
    with open(WEB_APP_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Health check route added.")

if __name__ == "__main__":
    add_health_check()
