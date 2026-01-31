
import paramiko
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        # 1. Try running web_app.py manually to catch immediate python errors
        logging.info("--- Running web_app.py manually ---")
        stdin, stdout, stderr = client.exec_command("cd /var/www/sustainage && python3 web_app.py")
        # We expect it to hang/run server, so we might need a timeout or just check stderr
        # But actually web_app.py usually starts a server. 
        # However, since it's CGI, if it has no `if __name__ == '__main__': app.run()`, it might just exit.
        # Let's see what happens.
        
        # Actually, for CGI, it might just exit if not configured to run as standalone.
        # But if there are import errors, they will appear in stderr immediately.
        
        # We'll give it a short timeout or just read what we can. 
        # Better: run it and check exit code.
        
        # Note: web_app.py usually has app.run() at the bottom. 
        # If it runs, it will block. So we send a timeout.
        
        # Wait a bit? No, let's just inspect stderr.
        # If it's blocking, we can't easily wait for it without a timeout.
        # Let's try running with a timeout or check syntax.
        
        # Let's just check syntax/imports first without running the server loop
        stdin, stdout, stderr = client.exec_command("cd /var/www/sustainage && python3 -c 'import web_app; print(\"Import Successful\")'")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if "Import Successful" in out:
            logging.info("Import Check: SUCCESS")
        else:
            logging.error(f"Import Check: FAILED\nSTDOUT: {out}\nSTDERR: {err}")
            
        # 2. Check Apache Error Logs
        logging.info("--- Checking Apache Error Logs ---")
        # Try common locations
        log_files = ["/var/log/apache2/error.log", "/var/log/httpd/error_log", "/var/log/httpd/error.log"]
        found_log = False
        for log_file in log_files:
            stdin, stdout, stderr = client.exec_command(f"tail -n 20 {log_file}")
            log_content = stdout.read().decode()
            if log_content:
                logging.info(f"Found log at {log_file}:\n{log_content}")
                found_log = True
                break
        
        if not found_log:
            logging.warning("Could not find standard Apache error logs.")

        # 3. Check logs directory permissions
        logging.info("--- Checking Logs Directory ---")
        stdin, stdout, stderr = client.exec_command("ls -ld /var/www/sustainage/logs")
        logging.info(stdout.read().decode())
        
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
