import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verify_remote_login():
    # url = "https://sustainage.cloud/login"
    # url = "http://72.62.150.207:5000/login" 
    # url = "http://72.62.150.207/login" # Try port 80 via Nginx
    url = "https://72.62.150.207/login" # Try HTTPS directly to avoid redirect
    
    users = [
        ('admin', 'admin'),
        ('__super__', 'super_admin')
    ]
    
    for username, password in users:
        print(f"Testing login for {username} at {url}...")
        session = requests.Session()
        try:
            # First get the page to set cookies/CSRF if needed
            print("GET request...")
            session.get(url, timeout=10, verify=False)
            
            # Post login
            print("POST request...")
            payload = {'username': username, 'password': password}
            response = session.post(url, data=payload, allow_redirects=True, timeout=10, verify=False)
            
            print(f"Status: {response.status_code}")
            print(f"URL after login: {response.url}")
            
            if "dashboard" in response.url or "Giriş başarılı" in response.text:
                print("LOGIN SUCCESSFUL!")
            else:
                print("LOGIN FAILED.")
                if "Kullanıcı adı veya parola hatalı" in response.text:
                    print("Reason: Invalid credentials.")
                else:
                    # Print snippet of body to diagnose
                    print(response.text[:500])
                    
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 30)

if __name__ == "__main__":
    verify_remote_login()
