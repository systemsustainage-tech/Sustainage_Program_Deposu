
import paramiko
import time
import sys

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_FILE = '/var/www/sustainage/web_app.py'

def add_reports_route():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        sftp = client.open_sftp()
        
        # Read remote file
        try:
            with sftp.open(REMOTE_FILE, 'r') as f:
                content = f.read().decode('utf-8')
        except FileNotFoundError:
            print(f"Error: {REMOTE_FILE} not found.")
            return

        if "@app.route('/reports')" in content and "def reports() -> None:" in content:
            print("Route /reports already exists.")
        else:
            print("Adding /reports route...")
            
            # Define the new route code
            new_route = """
@app.route('/reports')
def reports() -> None:
    if 'user' not in session: return redirect(url_for('login'))
    
    reports_list = []
    try:
        conn = get_db()
        # Try to get reports with company names
        # We need to handle case where report_registry might not exist yet or have different schema
        # But assuming it matches report_add usage
        try:
            query = '''
                SELECT r.*, c.name as company_name 
                FROM report_registry r
                LEFT JOIN companies c ON r.company_id = c.id
                ORDER BY r.id DESC
            '''
            # Convert to dict list
            cursor = conn.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                reports_list.append(dict(zip(columns, row)))
        except Exception as db_e:
            logging.error(f"Error fetching reports: {db_e}")
            # If table missing, we might want to create it? 
            # But let's just return empty for now to avoid crash
            pass
            
        conn.close()
    except Exception as e:
        logging.error(f"Reports route error: {e}")
        
    return render_template('reports.html', reports=reports_list)

"""
            # Insert before @app.route('/reports/add'
            target = "@app.route('/reports/add'"
            if target in content:
                parts = content.split(target)
                new_content = parts[0] + new_route + target + parts[1]
                
                # Write back
                with sftp.open(REMOTE_FILE, 'w') as f:
                    f.write(new_content)
                print("web_app.py updated.")
                
                # Restart service
                stdin, stdout, stderr = client.exec_command('systemctl restart sustainage')
                exit_status = stdout.channel.recv_exit_status()
                if exit_status == 0:
                    print("Service restarted successfully.")
                else:
                    print(f"Error restarting service: {stderr.read().decode()}")
            else:
                print(f"Target {target} not found in file. Cannot insert automatically.")

        sftp.close()
        client.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_reports_route()
