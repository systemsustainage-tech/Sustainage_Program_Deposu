import paramiko
import os

def implement_report_features():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        remote_path = '/var/www/sustainage/web_app.py'
        print(f"Reading {remote_path}...")
        with sftp.open(remote_path, 'r') as f:
            content = f.read().decode()
            
        # 1. Add send_file to imports
        if 'send_file' not in content:
            print("Adding send_file to imports...")
            content = content.replace(
                'from flask import Flask, render_template, redirect, url_for, session, request, flash',
                'from flask import Flask, render_template, redirect, url_for, session, request, flash, send_file'
            )
            
        # 2. Add new routes
        new_routes = """
@app.route('/reports/download/<int:report_id>')
def report_download(report_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db()
        report = conn.execute("SELECT * FROM report_registry WHERE id=?", (report_id,)).fetchone()
        conn.close()
        
        if not report:
            flash('Rapor bulunamadı.', 'warning')
            return redirect(url_for('reports'))
            
        file_path = report['file_path']
        if not file_path or not os.path.exists(file_path):
            flash('Dosya sunucuda bulunamadı.', 'danger')
            return redirect(url_for('reports'))
            
        return send_file(file_path, as_attachment=True, download_name=report['report_name'] + os.path.splitext(file_path)[1])
        
    except Exception as e:
        logging.error(f"Error downloading report: {e}")
        flash(f'Hata: {e}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/delete/<int:report_id>', methods=['POST'])
def report_delete(report_id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    try:
        conn = get_db()
        report = conn.execute("SELECT file_path FROM report_registry WHERE id=?", (report_id,)).fetchone()
        
        if report and report['file_path'] and os.path.exists(report['file_path']):
            try:
                os.remove(report['file_path'])
            except Exception as e:
                logging.error(f"Error deleting file: {e}")
        
        conn.execute("DELETE FROM report_registry WHERE id=?", (report_id,))
        conn.commit()
        conn.close()
        flash('Rapor silindi.', 'success')
        
    except Exception as e:
        logging.error(f"Error deleting report: {e}")
        flash(f'Hata: {e}', 'danger')
        
    return redirect(url_for('reports'))

"""
        if 'def report_download' not in content:
            print("Inserting new routes...")
            # Insert before # --- Module Routes ---
            insertion_marker = "# --- Module Routes ---"
            if insertion_marker in content:
                content = content.replace(insertion_marker, new_routes + insertion_marker)
            else:
                print("Could not find insertion marker '# --- Module Routes ---'. Appending to end.")
                content += new_routes
                
            print("Writing updated web_app.py...")
            with sftp.open(remote_path, 'w') as f:
                f.write(content)
            print("web_app.py updated.")
        else:
            print("Routes already exist.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    implement_report_features()
