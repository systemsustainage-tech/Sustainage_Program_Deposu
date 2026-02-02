
import requests
import sys
import os
import sqlite3

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from web_app import app, DB_PATH
except ImportError:
    try:
        from app import app, DB_PATH
    except ImportError:
        print("Could not import app or web_app.")
        sys.exit(1)

def setup_test_data():
    """Create necessary test data in the database"""
    print("Setting up test data...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure Supplier 1 exists
    cursor.execute("SELECT id FROM supplier_profiles WHERE id = 1")
    if not cursor.fetchone():
        print("Creating test supplier (ID 1)...")
        cursor.execute("""
            INSERT INTO supplier_profiles (id, company_id, name, industry, country, risk_score, status)
            VALUES (1, 1, 'Test Supplier', 'Manufacturing', 'Turkey', 50, 'Active')
        """)
    
    # Ensure User 1 exists and has super_admin role (or similar)
    # The test uses role='__super__' in session, so DB user role might not matter for session mock,
    # but good to have user in DB.
    cursor.execute("SELECT id FROM users WHERE id = 1")
    if not cursor.fetchone():
        print("Creating test user (ID 1)...")
        cursor.execute("""
            INSERT INTO users (id, company_id, username, email, password_hash, role)
            VALUES (1, 1, 'admin', 'admin@example.com', 'hash', 'admin')
        """)

    # Ensure tables for ISO 26000 exist (handled by app, but good to check if needed)
    
    conn.commit()
    conn.close()

def test_routes():
    setup_test_data()
    print("Testing improved routes...")
    
    # Create a test client
    with app.test_client() as client:
        # Mock session
        with client.session_transaction() as sess:
            sess['user'] = 'admin'
            sess['user_id'] = 1
            sess['role'] = '__super__'
            sess['company_id'] = 1
            sess['logged_in'] = True

        routes_to_test = [
            '/human_rights',
            '/labor',
            '/consumer',
            '/community',
            '/companies?page=1',
            '/reports?page=1&type=sustainability',
            '/supply_chain?search=test&risk_level=High',
            '/users?search=admin&role=admin',
            '/supply_chain/profile/1',
            '/surveys',
            '/super_admin/audit_logs?search=admin',
            '/super_admin/audit_logs?start_date=2024-01-01',
            '/fair_operating'
        ]

        for route in routes_to_test:
            try:
                print(f"Testing {route}...", end=" ")
                response = client.get(route, follow_redirects=True)
                if response.status_code == 200:
                    print("OK")
                elif response.status_code == 404:
                    print("404 (Not Found)")
                elif response.status_code == 302:
                     print(f"302 (Redirect to {response.headers.get('Location', 'unknown')})")
                else:
                    print(f"FAILED ({response.status_code})")
            except Exception as e:
                print(f"ERROR: {e}")

        # Test POST for Fair Operating
        print("Testing POST /fair_operating...", end=" ")
        try:
            response = client.post('/fair_operating', data={
                'date': '2024-01-01',
                'practice_area': 'Anti-corruption',
                'activity_type': 'Policy',
                'description': 'Test Policy'
            }, follow_redirects=True)
            if response.status_code == 200:
                print("OK")
            else:
                print(f"FAILED ({response.status_code})")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_routes()
