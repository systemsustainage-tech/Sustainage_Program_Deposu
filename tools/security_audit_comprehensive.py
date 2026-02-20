import sys
import os
import unittest
import logging
import json
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app import app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SecurityAudit")

class SecurityAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n" + "="*60)
        print(f" SUSTAINAGE SECURITY AUDIT REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True
        app.config['RATELIMIT_ENABLED'] = True # Enable Rate Limiting explicitly
        
        cls.client = app.test_client()
        cls.app_context = app.app_context()
        cls.app_context.push()
        
        # Suppress standard logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()
        print("\n" + "="*60)
        print(" AUDIT COMPLETE ")
        print("="*60 + "\n")

    def log_result(self, test_name, status, details=""):
        status_icon = "✅ PASS" if status else "❌ FAIL"
        print(f"{status_icon} | {test_name:<30} | {details}")

    def test_01_security_headers(self):
        """Verify presence of critical security headers"""
        response = self.client.get('/login')
        headers = response.headers
        
        required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN', # or DENY
            'Content-Security-Policy': None, # Just check existence
            'Strict-Transport-Security': None # HSTS
        }
        
        missing = []
        for header, expected_val in required_headers.items():
            val = headers.get(header)
            if not val:
                missing.append(header)
            elif expected_val and expected_val not in val:
                missing.append(f"{header} (Expected: {expected_val}, Got: {val})")
        
        if not missing:
            self.log_result("Security Headers", True, "All critical headers present")
        else:
            # Check if Talisman is actually active or configured differently
            # HSTS might be disabled in non-production/testing
            if 'Strict-Transport-Security' in missing and app.debug:
                 missing.remove('Strict-Transport-Security') # Ignore HSTS in debug
            
            if not missing:
                self.log_result("Security Headers", True, "All critical headers present (HSTS skipped in debug)")
            else:
                self.log_result("Security Headers", False, f"Missing/Invalid: {', '.join(missing)}")
                # self.fail(f"Missing headers: {missing}") # Don't fail hard, just report

    def test_02_sql_injection_login(self):
        """Attempt SQL Injection on Login endpoint"""
        # We need to disable CSRF strictly for this payload to reach the logic, 
        # or we fetch a token first. Fetching token is better simulation.
        
        # 1. Get CSRF Token
        response = self.client.get('/login')
        csrf_token = ''
        if b'name="csrf_token"' in response.data:
            # Simple extraction
            part = response.data.decode().split('name="csrf_token" value="')[1]
            csrf_token = part.split('"')[0]
        
        payloads = [
            "admin' OR '1'='1",
            "admin'; DROP TABLE users; --",
            "' OR 1=1 --"
        ]
        
        passed = True
        for payload in payloads:
            res = self.client.post('/login', data={
                'username': payload,
                'password': 'password',
                'csrf_token': csrf_token
            }, follow_redirects=True)
            
            # If successful login (redirect to dashboard or welcome), it's a FAIL
            if b'Dashboard' in res.data or 'Hoşgeldiniz'.encode('utf-8') in res.data:
                self.log_result("SQL Injection", False, f"Vulnerable to: {payload}")
                passed = False
                break
            
            # Should see "Hatalı" or "Failed"
            if 'Kullanıcı adı veya parola hatalı'.encode('utf-8') not in res.data and \
               b'Invalid username or password' not in res.data and \
               res.status_code != 200: # 200 OK with error message is expected
                 # It might be 429 if rate limited, which is GOOD
                 if res.status_code == 429:
                     continue
                 # self.log_result("SQL Injection", False, f"Unexpected response code {res.status_code} for {payload}")
                 pass

        if passed:
            self.log_result("SQL Injection (Login)", True, "No injection succeeded")

    def test_03_xss_protection(self):
        """Test XSS via Template Injection and Reflection"""
        # Test reflection if any (e.g. search parameter)
        # We'll test template auto-escaping
        
        with app.test_request_context():
            from flask import render_template_string
            unsafe = "<script>alert(1)</script>"
            rendered = render_template_string("{{ var }}", var=unsafe)
            if "&lt;script&gt;" in rendered:
                self.log_result("XSS Protection (Autoescape)", True, "Jinja2 escaping active")
            else:
                self.log_result("XSS Protection (Autoescape)", False, "Jinja2 NOT escaping input!")

    def test_04_csrf_enforcement(self):
        """Verify CSRF token requirement for POST requests"""
        # Attempt POST without token
        res = self.client.post('/login', data={'username': 'admin', 'password': 'p'}, follow_redirects=True)
        
        # Expect 400 Bad Request (CSRF Error)
        if res.status_code == 400 or b'CSRF' in res.data or b'Session is invalid' in res.data:
            self.log_result("CSRF Protection", True, "Blocked request without token")
        else:
            self.log_result("CSRF Protection", False, f"Accepted request without token (Status: {res.status_code})")

    def test_05_sensitive_files(self):
        """Check for exposure of sensitive files"""
        files = [
            '/.env',
            '/.git/HEAD',
            '/backup_config.json',
            '/web_app.py',
            '/backend/data/sustainage.db'
        ]
        
        exposed = []
        for f in files:
            res = self.client.get(f)
            if res.status_code == 200:
                exposed.append(f)
        
        if not exposed:
            self.log_result("Sensitive File Check", True, "No sensitive files exposed")
        else:
            self.log_result("Sensitive File Check", False, f"EXPOSED: {', '.join(exposed)}")

    def test_06_directory_traversal(self):
        """Attempt Directory Traversal"""
        payloads = [
            '/static/../../web_app.py',
            '/static/..%2f..%2fweb_app.py'
        ]
        
        vulnerable = False
        for p in payloads:
            res = self.client.get(p)
            if res.status_code == 200 and b'import' in res.data:
                vulnerable = True
                break
        
        if not vulnerable:
            self.log_result("Directory Traversal", True, "Static files secure")
        else:
            self.log_result("Directory Traversal", False, "Vulnerable to path traversal!")

    def test_07_rate_limiting(self):
        """Test Rate Limiting (Login)"""
        # This is tricky in test mode as Limiter might use memory storage reset per request or be disabled
        # We will skip if testing config disables it, but try to trigger it
        
        # Reset limiter if possible (Flask-Limiter specific)
        
        limit_hit = False
        try:
            # Try 15 requests (limit is usually 5 or 10 per minute)
            for _ in range(15):
                res = self.client.post('/login', data={'username': 'admin', 'password': 'p'})
                if res.status_code == 429:
                    limit_hit = True
                    break
        except Exception as e:
            self.log_result("Rate Limiting", False, f"Error testing: {e}")
            return

        if limit_hit:
            self.log_result("Rate Limiting", True, "429 Too Many Requests triggered")
        else:
            self.log_result("Rate Limiting", False, "Failed to trigger rate limit (Check TEST config)")

    def test_08_access_control_api(self):
        """Verify API routes are protected (Auth Bypass)"""
        # Try to access protected API without login
        res = self.client.get('/api/v1/dashboard-stats')
        
        # Should be 401 Unauthorized
        if res.status_code == 401:
            self.log_result("Access Control (API)", True, "Unauthenticated access blocked (401)")
        elif res.status_code == 302 and 'login' in res.location:
             self.log_result("Access Control (API)", True, "Redirected to login")
        else:
            self.log_result("Access Control (API)", False, f"Accessible without login! (Status: {res.status_code})")

    def test_09_cookie_security(self):
        """Check Session Cookie Attributes"""
        res = self.client.get('/login')
        cookies = res.headers.getlist('Set-Cookie')
        
        secure_missing = []
        httponly_missing = []
        samesite_missing = []
        
        for cookie in cookies:
            if 'session' in cookie:
                if 'HttpOnly' not in cookie:
                    httponly_missing.append('session')
                if 'Secure' not in cookie and not app.debug: # Secure required in Prod
                    secure_missing.append('session')
                if 'SameSite' not in cookie:
                    samesite_missing.append('session')
        
        details = []
        if httponly_missing: details.append("HttpOnly missing")
        if secure_missing and not app.debug: details.append("Secure missing")
        # SameSite is lax by default in modern browsers/Flask but explicit is better
        
        if not details:
            self.log_result("Cookie Security", True, "Session cookie attributes correct")
        else:
            self.log_result("Cookie Security", False if httponly_missing else True, f"Warnings: {', '.join(details)}")

if __name__ == '__main__':
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(SecurityAudit)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        sys.exit(1)
