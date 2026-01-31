import requests
import re
import sys

BASE_URL = "http://localhost:5000"  # Localhost on the server
LOGIN_URL = f"{BASE_URL}/login"
SDG_URL = f"{BASE_URL}/sdg"

USERNAME = "__super__"
PASSWORD = "Sustainage2024!"

def run_simulation():
    session = requests.Session()
    
    # 1. Login
    print(f"Attempting login to {LOGIN_URL} with user {USERNAME}...")
    try:
        # Get CSRF token first if needed (assuming Flask-WTF) - usually in login page
        # For simplicity, trying direct POST first, assuming CSRF might be disabled or handled via cookie
        # If CSRF is strictly enforced, we need to scrape it from GET /login first.
        
        # Let's get the login page first to get cookies/csrf
        r_get = session.get(LOGIN_URL)
        if r_get.status_code != 200:
            print(f"Failed to load login page. Status: {r_get.status_code}")
            return
            
        # Extract CSRF token if present
        csrf_token = None
        match = re.search(r'name="csrf_token" value="([^"]+)"', r_get.text)
        if match:
            csrf_token = match.group(1)
            print("CSRF token found.")
        
        data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        if csrf_token:
            data['csrf_token'] = csrf_token
            
        r_post = session.post(LOGIN_URL, data=data)
        
        if r_post.status_code == 200 and "Hoşgeldiniz" in r_post.text or "/dashboard" in r_post.url or "Çıkış Yap" in r_post.text:
            print("Login SUCCESSFUL.")
        elif r_post.status_code == 302:
            # Follow redirect
            print("Redirect detected, following...")
            r_redirect = session.get(r_post.headers['Location'])
            if "Çıkış Yap" in r_redirect.text or "Hoşgeldiniz" in r_redirect.text:
                 print("Login SUCCESSFUL after redirect.")
            else:
                 print("Login FAILED after redirect.")
                 # Print a snippet of the page to diagnose
                 print(r_redirect.text[:500])
                 return
        else:
            print("Login FAILED.")
            print(f"Status: {r_post.status_code}")
            if "Kullanıcı adı veya şifre hatalı" in r_post.text:
                print("Reason: Invalid credentials.")
            elif "Hesabınız kilitli" in r_post.text:
                print("Reason: Account locked.")
            else:
                print(r_post.text[:500])
            return

    except Exception as e:
        print(f"Login Error: {e}")
        return

    # 2. Check SDG Page
    print(f"\nAccessing SDG Module at {SDG_URL}...")
    r_sdg = session.get(SDG_URL)
    if r_sdg.status_code == 200:
        print("SDG Page loaded.")
    else:
        print(f"Failed to load SDG Page. Status: {r_sdg.status_code}")
        return

    # 3. Check Images
    print("\nChecking SDG Images...")
    # Find all image sources
    images = re.findall(r'src="([^"]+)"', r_sdg.text)
    sdg_images = [img for img in images if 'static/images' in img and ('.png' in img or '.jpg' in img)]
    
    if not sdg_images:
        print("No SDG images found in the page source.")
        print("Page source snippet:")
        print(r_sdg.text[:1000])
    
    for img_path in sdg_images:
        # Construct full URL. If path starts with /, append to host.
        if img_path.startswith('/'):
            img_url = f"{BASE_URL}{img_path}"
        else:
            img_url = f"{BASE_URL}/{img_path}"
            
        r_img = session.get(img_url)
        if r_img.status_code == 200:
            print(f"[OK] {img_path}")
        else:
            print(f"[FAIL] {img_path} - Status: {r_img.status_code}")

if __name__ == "__main__":
    run_simulation()
