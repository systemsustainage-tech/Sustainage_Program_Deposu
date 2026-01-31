import requests
import sys

BASE_URL = "http://72.62.150.207"

def verify():
    s = requests.Session()
    
    # Login
    print("Logging in...")
    try:
        r = s.post(f"{BASE_URL}/login", data={'username': 'test_user', 'password': 'Test1234!'})
    except Exception as e:
        print(f"Login failed: {e}")
        return

    if r.url == f"{BASE_URL}/dashboard" or "/dashboard" in r.url:
        print("Login successful.")
    else:
        print("Login failed.")
        return

    # Create Report (Auto-generate)
    print("Creating auto-generated report...")
    report_data = {
        'report_name': 'AutoTestReport',
        'module_code': 'carbon',
        'report_type': 'PDF',
        'reporting_period': '2024',
        'description': 'Auto generated test report'
    }
    
    # Post without file
    try:
        r = s.post(f"{BASE_URL}/reports/add", data=report_data)
        print(f"POST Response URL: {r.url}")
        print(f"POST Response Code: {r.status_code}")
    except Exception as e:
        print(f"POST failed: {e}")
        return
    
    if r.status_code == 200 and "Rapor PDF olarak otomatik oluşturuldu" in r.text:
        print("Report creation success message found.")
    elif r.status_code == 200:
        if "Rapor oluşturulamadı" in r.text:
             print("FAIL: Report creation failed (server likely missing reportlab).")
        else:
             print("Report page loaded (redirected likely). checking list...")
             if "/reports/add" in r.url:
                 print("WARNING: Stayed on add page. Printing content to find error...")
                 print("--- POST Response Content ---")
                 for line in r.text.split('\n'):
                     if "alert" in line or "Hata" in line or "danger" in line:
                         print(line.strip())
                 print("--- End POST Response Content ---")
    else:
        print(f"Report creation failed: {r.status_code}")

    # Check List
    print("Checking report list...")
    r = s.get(f"{BASE_URL}/reports")
    if "AutoTestReport" in r.text:
        print("Report found in list.")
        
        # Extract ID (simple parse)
        try:
            part = r.text.split("AutoTestReport")[1]
            import re
            match = re.search(r'/reports/download/(\d+)', part)
            if match:
                report_id = match.group(1)
                print(f"Report ID: {report_id}")
                
                # Try Download
                print("Attempting download...")
                r_dl = s.get(f"{BASE_URL}/reports/download/{report_id}")
                if r_dl.status_code == 200:
                    if r_dl.headers.get('Content-Type') == 'application/pdf':
                        print(f"Download successful. Size: {len(r_dl.content)} bytes.")
                        if len(r_dl.content) > 100:
                             print("PDF content seems valid.")
                        else:
                             print("PDF content too small.")
                    else:
                        print(f"Download content type mismatch: {r_dl.headers.get('Content-Type')}")
                else:
                    print(f"Download failed: {r_dl.status_code}")
            else:
                print("Could not find download link for report.")
        except Exception as e:
            print(f"Parsing error: {e}")
            
    else:
        print("Report NOT found in list.")
        print("--- Page Content (Search for 'alert', 'Hata', 'danger') ---")
        for line in r.text.split('\n'):
            if "alert" in line or "Hata" in line or "danger" in line:
                print(line.strip())
        print("--- End Page Content ---")

if __name__ == "__main__":
    verify()
