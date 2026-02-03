import unittest
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import mocks BEFORE web_app
import mocks_for_missing_deps

from web_app import app, DB_PATH
# from config.database import init_db

class TestRateLimitCaptcha(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        self.app_context.pop()

    def test_captcha_trigger(self):
        """Test CAPTCHA trigger after 3 failed attempts"""
        print("\nTesting CAPTCHA Trigger...")
        
        # Clear session first
        with self.client.session_transaction() as sess:
            sess.clear()
            
        # 1st fail
        response = self.client.post('/login', data={'username': 'non_existent', 'password': 'pwd'})
        self.assertNotIn(b'Guvenlik Kodu', response.data)
        
        # 2nd fail
        response = self.client.post('/login', data={'username': 'non_existent', 'password': 'pwd'})
        
        # 3rd fail
        response = self.client.post('/login', data={'username': 'non_existent', 'password': 'pwd'})
        
        # Now CAPTCHA should be required
        # Note: The logic in login() sets captcha_required based on failed_attempts_session >= 3.
        # But it increments AFTER failure.
        # So:
        # 1. Start: 0. Fail -> 1.
        # 2. Start: 1. Fail -> 2.
        # 3. Start: 2. Fail -> 3.
        # 4. Start: 3. Render template with captcha_required=True.
        
        # So the 3rd response MIGHT have it if the template uses the UPDATED value.
        # Let's check the code:
        # ... increment failure ...
        # return render_template(..., captcha_required=session.get(...) >= 3)
        # Yes, it uses the current value.
        
        # Note: Check for 'name="captcha"' as reliable indicator
        if b'name="captcha"' in response.data:
            print("CAPTCHA triggered on 3rd failure response.")
        else:
            print("CAPTCHA NOT triggered on 3rd failure response (Check logic).")
            # If not, maybe it needs one more request to see the form?
            # Let's try 4th request
            response = self.client.get('/login')
            if b'name="captcha"' in response.data:
                print("CAPTCHA triggered on subsequent GET.")
            else:
                self.fail("CAPTCHA not triggered even after 3 failures.")

        # Test Blocking with wrong captcha
        # Set session to require captcha
        with self.client.session_transaction() as sess:
            sess['failed_attempts_session'] = 3
            sess['captcha_code'] = 'ABCDE'
            
        response = self.client.post('/login', data={'username': 'non_existent', 'password': 'pwd', 'captcha': 'WRONG'})
        response_text = response.data.decode('utf-8')
        # Check flash message part
        if 'Güvenlik kodu hatalı' not in response_text:
            print("Response content snippet:", response_text[:500]) # Debug
            self.fail("Flash message 'Güvenlik kodu hatalı' not found")
            
        # Or just check we are still on login page and captcha is there
        self.assertIn('name="captcha"', response_text)
        
        # Test Success with correct captcha (but wrong password)
        response = self.client.post('/login', data={'username': 'non_existent', 'password': 'pwd', 'captcha': 'ABCDE'})
        response_text = response.data.decode('utf-8')
        # Should fail due to password, but NOT captcha error
        self.assertNotIn('Güvenlik kodu hatalı', response_text)
        self.assertIn('Kullanıcı', response_text) # "Kullanıcı adı veya parola hatalı"

if __name__ == '__main__':
    unittest.main()
