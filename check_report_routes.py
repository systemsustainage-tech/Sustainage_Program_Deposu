import paramiko

def check_report_routes():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Grepping routes in web_app.py...")
        stdin, stdout, stderr = client.exec_command("grep \"@app.route\" /var/www/sustainage/web_app.py")
        routes = stdout.read().decode()
        
        print("Grepping defs in web_app.py...")
        stdin, stdout, stderr = client.exec_command("grep \"def \" /var/www/sustainage/web_app.py")
        defs = stdout.read().decode()
        
        print("--- Routes ---")
        print(routes)
        print("--- Defs ---")
        print(defs)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_report_routes()
