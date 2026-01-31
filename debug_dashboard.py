import os
import sys
import unittest
from flask import session

# Add root to path
sys.path.insert(0, os.getcwd())

from remote_web_app import app

app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'debug_key'
client = app.test_client()

def debug_dashboard():
    with client.session_transaction() as sess:
        sess['user'] = 'saas_test_user'
        sess['user_id'] = 123
        sess['company_id'] = 999
        sess['role'] = 'admin'

    print("Requesting /dashboard...")
    response = client.get('/dashboard')
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    # print(f"Data: {response.data.decode('utf-8')[:500]}") # Print first 500 chars

if __name__ == "__main__":
    debug_dashboard()