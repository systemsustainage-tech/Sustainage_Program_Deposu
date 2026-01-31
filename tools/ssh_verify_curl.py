import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def verify_with_curl():
    print("--- Verifying OpenAI with cURL (Direct HTTP) ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    # Get the key from .env to be sure we use the one on server
    stdin, stdout, stderr = ssh.exec_command("grep OPENAI_API_KEY /var/www/sustainage/.env")
    env_line = stdout.read().decode().strip()
    if not env_line:
        print("Could not find OPENAI_API_KEY in .env")
        return
        
    api_key = env_line.split('=', 1)[1].strip()
    
    # Construct curl command
    # We use -s for silent, but show errors.
    curl_cmd = f"""curl https://api.openai.com/v1/chat/completions \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer {api_key}" \
      -d '{{
        "model": "gpt-3.5-turbo",
        "messages": [{{"role": "user", "content": "Say Hello"}}],
        "max_tokens": 5
      }}'"""
      
    print("Executing cURL command to bypass Python libraries...")
    stdin, stdout, stderr = ssh.exec_command(curl_cmd)
    
    response = stdout.read().decode()
    print("\n--- OpenAI API Response ---")
    print(response)
    
    ssh.close()

if __name__ == "__main__":
    verify_with_curl()
