
import requests
import sys
import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

BASE_URL = "http://localhost:5000"
DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def test_user_registration_and_login():
    session = requests.Session()
    
    # 1. Create a unique username
    import time
    timestamp = int(time.time())
    username = f"testuser_{timestamp}"
    email = f"test_{timestamp}@example.com"
    password = "Password123!"
    
    print(f"\n--- Testing User Registration: {username} ---")
    
    # Simulate user_add POST
    # Note: In web_app.py, user_add route is likely protected or is the registration route.
    # Looking at previous context, there is a '/user/add' or similar for admin, 
    # but usually there is a register page? 
    # The user said "Yeni bir kullanıcı tanımladım", possibly via admin panel or registration.
    # Let's check web_app.py for registration route.
    # If no public registration, we'll assume admin creation.
    # But wait, if I can't login, I can't create user as admin.
    # The user might be talking about the initial setup or a registration page.
    # Let's assume we use the 'admin' user (which we fixed) to create a new user, then try to login as that new user.
    
    # Login as admin first
    print("Logging in as admin...")
    login_payload = {
        "username": "admin",
        "password": "Admin_2025!" 
    }
    resp = session.post(f"{BASE_URL}/login", data=login_payload)
    print(f"Login Response URL: {resp.url}")
    print(f"Login Response Status: {resp.status_code}")
    
    if "dashboard" in resp.url:
        print("Admin login successful (Redirected to dashboard).")
    elif "verify" in resp.url:
         print("Redirected to 2FA/Verify page.")
    else:
        print("Admin login might have failed. Current URL: " + resp.url)
        if "Kullanıcı adı veya parola hatalı" in resp.text:
             print("Error Message: Invalid credentials.")
    
    # Let's verify if we are logged in by accessing a protected route
    resp = session.get(f"{BASE_URL}/dashboard")
    print(f"Dashboard Access URL: {resp.url}")
    
    if "login" in resp.url and "dashboard" not in resp.url:
        print("FAILURE: Admin login failed. Redirected to login page.")
        return
    else:
        print("SUCCESS: Admin login verified (Dashboard accessible).")

    # 2. Create New User via Admin
    print(f"Creating new user {username} via /users/add...", flush=True)
    new_user_payload = {
        "username": username,
        "password": password,
        "email": email,
        "full_name": "Test User",
        "role": "User", 
        "department": "Test Dept",
        "is_active": "on" 
    }
    
    resp = session.post(f"{BASE_URL}/users/add", data=new_user_payload)
    print(f"User Add Response URL: {resp.url}", flush=True)
    print(f"User Add Status: {resp.status_code}", flush=True)

    if "Kullanıcı başarıyla oluşturuldu" in resp.text or resp.status_code == 200:
        # Note: Flash messages might appear in the redirected page
        # If we are redirected to /users, it's a good sign
        if resp.url.endswith("/users"):
            print("User creation request redirected to /users (Likely Success).")
        else:
            print("User creation response code: " + str(resp.status_code))
            if "Kullanıcı başarıyla oluşturuldu" in resp.text:
                 print("SUCCESS: User creation message found.")
            else:
                 print("WARNING: User creation message NOT found. Checking DB...")
    
    # 3. Verify User in DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, is_active FROM users WHERE username=?", (username,))
    user_row = cursor.fetchone()
    conn.close()
    
    if user_row:
        print(f"SUCCESS: User {username} found in DB. ID: {user_row[0]}, Active: {user_row[2]}")
    else:
        print("FAILURE: User NOT found in DB.")
        return

    # 4. Login as New User
    print(f"Logging in as new user {username}...")
    # New session for new user
    user_session = requests.Session()
    login_payload = {
        "username": username,
        "password": password
    }
    resp = user_session.post(f"{BASE_URL}/login", data=login_payload)
    
    if "Giriş başarılı" in resp.text or "dashboard" in resp.url or "Giriş Yap" not in resp.text:
         # Need a better check. If redirected to dashboard, we are good.
         resp_dash = user_session.get(f"{BASE_URL}/dashboard")
         if "Giriş Yap" in resp_dash.text:
             print("FAILURE: New user login failed.")
         else:
             print("SUCCESS: New user login successful!")
    else:
        print("FAILURE: New user login failed (Response check).")
        print(resp.text[:500])

if __name__ == "__main__":
    test_user_registration_and_login()
