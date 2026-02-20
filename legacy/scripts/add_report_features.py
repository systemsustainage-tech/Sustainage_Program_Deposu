import paramiko

def add_report_features():
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
            
        # 1. Add send_file to imports if not present
        if 'send_file' not in content:
            print("Adding send_file to imports...")
            content = content.replace(
                'from flask import Flask, render_template, redirect, url_for, session, request, flash',
                'from flask import Flask, render_template, redirect, url_for, session, request, flash, send_file'
            )
            
        # 2. Add new routes if not present
        if 'report_download' not in content:
            print("Adding report routes...")
            
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
            # Find a good insertion point. After report_add_page.
            # report_add_page seems to end with flash(f'Hata: {e}', 'danger') ... return render_template(...)
            # But in the snippet I read, it ends with return render_template('company_detail.html'...) no that was company_detail.
            # report_add_page ends around line 651 with return redirect(url_for('reports')) or flash.
            
            # Let's verify the end of report_add_page using grep/find.
            # Or just append it after the last route if I can find a unique string.
            # The snippet showed:
            # 648:             return redirect(url_for('reports'))
            # 649:         except Exception as e:
            # 650:             logging.error(f"Error adding report: {e}")
            # 651:             flash(f'Hata: {e}', 'danger')
            
            # I will append after the flash line.
            
            target = "flash(f'Hata: {e}', 'danger')"
            # Note: There might be multiple occurrences. The one in report_add_page is indented.
            
            # Better strategy: Find "@app.route('/reports/add'" and then find the next "@app.route" or end of function.
            # Or just append to the end of the file? No, it has other routes.
            # I can insert it before "@app.route('/users')" which is line 372 in my read, but lines shifted.
            # Wait, line 372 is BEFORE report routes in the read output?
            # No, in my read output:
            # 595: @app.route('/reports')
            # 608: @app.route('/reports/add'...)
            # And /users is line 372?
            # Ah, the file content I read was truncated or I read sections.
            # The first read was lines 1-1000.
            # /users was at 372.
            # /reports was at 595.
            # So /users is BEFORE /reports in the file?
            # Let's check line numbers again.
            # Yes, 372 comes before 595.
            
            # So I should look for what comes AFTER /reports/add.
            # I haven't seen what's after 651.
            # I will assume it's safe to insert after line 651.
            # But I need to be precise.
            
            # Let's append it after the `report_add_page` function.
            # I will use a regex or string search to find the end of `report_add_page`.
            # It ends with `return render_template('report_add.html'...)` ?
            # Wait, the snippet showed:
            # 648: return redirect(url_for('reports'))
            # 651: flash(f'Hata: {e}', 'danger')
            # It likely has a `return render_template` at the end of function (unindented to def level).
            
            # I will search for `@app.route` after `/reports/add`.
            # If none, it's the last route?
            # Let's check if there are other routes after reports.
            # I'll check line 650+
            pass

        else:
            print("Routes already exist.")
            
        # Writing logic needs to be robust.
        # I'll append it before the next known route or at the end if it's the last one.
        # Let's read 650-800 to see what's next.
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Just printing context to decide insertion point
    import sys
    # I will modify this script to actually perform the read first to confirm insertion point
    pass
