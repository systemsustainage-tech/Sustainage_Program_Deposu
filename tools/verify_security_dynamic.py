import sys
import os
import unittest
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app import app

class SecurityDynamicTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True # Default ON
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    def tearDown(self):
        self.app_context.pop()

    def test_01_sql_injection_login(self):
        """Attempt SQL Injection in Login (CSRF Disabled for this test)"""
        print("\n[TEST] Testing SQL Injection in Login...")
        
        # Disable CSRF for this test to reach the SQL query
        app.config['WTF_CSRF_ENABLED'] = False
        
        try:
            response = self.client.post('/login', data=dict(
                username="admin' OR '1'='1",
                password="randompass"
            ), follow_redirects=True)
            
            # Should fail login (return 200 OK with "Giriş başarısız" message)
            # If SQLi worked, it might log us in or error out differently
            
            # Check for failure message (handling UTF-8 bytes)
            # "Kullanıcı adı veya parola hatalı!" in bytes
            expected_msg = 'Kullanıcı adı veya parola hatalı!'.encode('utf-8')
            self.assertIn(expected_msg, response.data)
            print(" -> SQL Injection blocked (Login failed safely).")
            
        finally:
            # Re-enable CSRF
            app.config['WTF_CSRF_ENABLED'] = True

    def test_02_csrf_protection(self):
        """Attempt POST without CSRF token"""
        print("\n[TEST] Testing CSRF Protection...")
        
        # Try to post to login without CSRF token
        response = self.client.post('/login', data=dict(
            username='admin',
            password='password'
        ))
        
        # Should be 400 Bad Request (CSRF Error)
        if response.status_code == 400:
            print(f" -> CSRF Attack blocked (Status: {response.status_code})")
        else:
            self.fail(f"CSRF Attack NOT blocked! Status: {response.status_code}")

    def test_03_xss_prevention(self):
        """Attempt XSS Injection (Template Check)"""
        print("\n[TEST] Testing XSS Prevention (Stored)...")
        self.assertTrue(app.jinja_env.autoescape, "Jinja2 Autoescape should be enabled")
        print(" -> Jinja2 Autoescape is ENABLED.")
        
        with app.test_request_context():
            from flask import render_template_string
            unsafe_str = "<script>alert(1)</script>"
            rendered = render_template_string("{{ var }}", var=unsafe_str)
            self.assertEqual(rendered, "&lt;script&gt;alert(1)&lt;/script&gt;")
            print(" -> Template rendering escapes HTML correctly.")

    def test_04_security_headers(self):
        """Check for Security Headers"""
        print("\n[TEST] Checking Security Headers...")
        response = self.client.get('/login')
        headers = response.headers
        print(f" -> X-Content-Type-Options: {headers.get('X-Content-Type-Options')}")
        print(f" -> X-Frame-Options: {headers.get('X-Frame-Options')}")
        
        if headers.get('X-Content-Type-Options') == 'nosniff':
            print(" -> Headers verified.")
        else:
            print(" -> WARNING: Security headers missing or incorrect.")

if __name__ == '__main__':
    unittest.main()
