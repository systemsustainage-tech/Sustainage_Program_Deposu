import requests
import sys

URL = 'http://72.62.150.207/login'
DASHBOARD_URL = 'http://72.62.150.207/dashboard'

USERNAME = 'test_user' # or 'test@sustainage.com' - web_app.py uses username for lookup: WHERE username=?
# Wait, setup_test_user.py inserted username='test_user'.
# The login form usually asks for username, but sometimes email.
# web_app.py: username = request.form.get('username', '') -> WHERE username=?
# So I must use 'test_user'.
PASSWORD = '123456'

def login():
    session = requests.Session()
    try:
        # Get CSRF token if needed? web_app.py didn't show CSRF logic in login route, but might use Flask-WTF.
        # The code I read: username = request.form.get('username', '')
        # No form validation shown in the snippet (just request.form.get).
        # So maybe no CSRF token needed for this simple login.
        
        print(f"Attempting login to {URL} with user '{USERNAME}'...")
        response = session.post(URL, data={'username': USERNAME, 'password': PASSWORD})
        
        if response.status_code == 200:
            if 'dashboard' in response.url or 'Giriş başarılı' in response.text:
                print("Login successful! Redirected to dashboard.")
                return True
            elif 'Kullanıcı adı veya parola hatalı' in response.text:
                print("Login failed: Invalid credentials.")
            else:
                print(f"Login response: {response.status_code}")
                # print(response.text[:500])
                # Check if we are still on login page
                if '/login' in response.url:
                    print("Still on login page.")
        else:
            print(f"Login failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    if login():
        sys.exit(0)
    else:
        sys.exit(1)