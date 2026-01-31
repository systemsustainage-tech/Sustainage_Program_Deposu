import paramiko
import sys

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def read_result():
    with open("c:/SUSTAINAGESERVER/remote_verification_output.txt", "w", encoding="utf-8") as f:
        f.write("Starting...\n")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            f.write(f"Connecting to {hostname}...\n")
            client.connect(hostname, username=username, password=password)
            f.write("Connected. Reading file...\n")
            stdin, stdout, stderr = client.exec_command('cat /var/www/sustainage/verification_result.txt')
            content = stdout.read().decode()
            if content:
                f.write("--- FILE CONTENT ---\n")
                f.write(content)
                f.write("\n--- END CONTENT ---\n")
            else:
                f.write("File is empty.\n")
                err = stderr.read().decode()
                if err:
                    f.write(f"Stderr: {err}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
        finally:
            client.close()

if __name__ == "__main__":
    read_result()