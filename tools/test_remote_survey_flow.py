import sys
import os

# Add project root to path
sys.path.append('/var/www/sustainage')

def log(msg):
    sys.stderr.write(f"TEST_LOG: {msg}\n")
    sys.stderr.flush()

log("Importing app and managers...")
from web_app import app, get_db
from backend.modules.prioritization.prioritization_manager import PrioritizationManager

def test_flow():
    log("Starting Survey Flow Test...")
    
    # 1. Ensure templates exist
    try:
        log("Initializing PrioritizationManager...")
        pm = PrioritizationManager('/var/www/sustainage/backend/data/sdg_desktop.sqlite')
        templates = pm.get_survey_templates()
        log(f"Found {len(templates)} templates.")
        
        if not templates:
            log("No templates found. Initialization failed?")
            return

        template_id = templates[0]['id']
        log(f"Testing with Template ID: {template_id} ({templates[0]['name']})")
    except Exception as e:
        log(f"Error initializing Manager: {e}")
        return

    # 2. Setup test client
    client = app.test_client()
    
    # 3. Login as test user (or mock session)
    with client.session_transaction() as sess:
        sess['user'] = {'id': 1, 'username': 'test_user'}
        sess['company_id'] = 1
        
    # 4. POST to create survey
    log("Sending POST request to /surveys/add...")
    try:
        response = client.post('/surveys/add', data={
            'survey_title': 'Test Template Survey ' + os.urandom(4).hex(),
            'survey_description': 'Created via automated test',
            'target_groups': 'Test Group',
            'template_id': template_id
        }, follow_redirects=True)
        
        log(f"POST Response: {response.status_code}")
    except Exception as e:
        log(f"Error during POST: {e}")
        return
    
    # 5. Verify survey created and questions copied
    try:
        with app.app_context():
            conn = get_db()
            cursor = conn.execute("SELECT * FROM online_surveys ORDER BY id DESC LIMIT 1")
            survey = cursor.fetchone()
            
            if not survey:
                log("FAIL: Survey not created.")
                return
                
            log(f"Survey Created. ID: {survey['id']} Title: {survey['survey_title']}")
            
            cursor = conn.execute("SELECT count(*) FROM survey_questions WHERE survey_id=?", (survey['id'],))
            count = cursor.fetchone()[0]
            log(f"Questions Copied: {count}")
            
            if count > 0:
                log("SUCCESS: Template questions copied.")
            else:
                log("FAIL: No questions copied.")
                
            # Cleanup
            conn.execute("DELETE FROM online_surveys WHERE id=?", (survey['id'],))
            conn.execute("DELETE FROM survey_questions WHERE survey_id=?", (survey['id'],))
            conn.commit()
            log("Cleanup done.")
    except Exception as e:
        log(f"Error during verification: {e}")

if __name__ == "__main__":
    test_flow()
