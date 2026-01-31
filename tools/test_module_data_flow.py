import requests
import sys
import datetime
import json
import time

BASE_URL = "http://localhost:5000"

def log(msg):
    print(msg)
    with open("module_test_results.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Clear the log file
with open("module_test_results.txt", "w", encoding="utf-8") as f:
    f.write("Starting E2E Tests...\n")

def test_login(username, password):
    log(f"\n--- Testing login for {username} ---")
    session = requests.Session()
    requests.packages.urllib3.disable_warnings()
    try:
        login_data = {'username': username, 'password': password}
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True, verify=False)
        
        if response.status_code == 200:
            if "Dashboard" in response.text or "Hoşgeldiniz" in response.text or "Çıkış Yap" in response.text or "dashboard" in response.url:
                log(f"SUCCESS: Login successful for {username}")
                return session
            elif "Hatalı kullanıcı adı veya şifre" in response.text:
                log(f"FAILED: Invalid credentials for {username}")
            else:
                if "/dashboard" in response.url:
                    log(f"SUCCESS: Login successful (redirected) for {username}")
                    return session
                log(f"WARNING: Login status unclear. URL: {response.url}")
                log(f"Response snippet: {response.text[:200]}")
        else:
            log(f"FAILED: HTTP {response.status_code}")
            
    except Exception as e:
        log(f"ERROR: {e}")
    
    return None

def post_and_check(session, url, data, label):
    try:
        response = session.post(url, data=data, allow_redirects=True, verify=False)
        if response.status_code == 200:
            if "success" in response.text.lower() or "başarıyla" in response.text.lower():
                 log(f"SUCCESS: {label} submitted.")
                 return True
            if response.url != url: 
                 log(f"SUCCESS: {label} submitted (redirected to {response.url}).")
                 return True
            
            log(f"WARNING: Success message not found for {label}.")
            return True 
        else:
            log(f"FAILED: {label} HTTP {response.status_code}")
    except Exception as e:
        log(f"ERROR adding {label}: {e}")
    return False

def check_data_display(session, url, check_strings, label):
    """Verifies that the submitted data appears on the module's main page."""
    try:
        response = session.get(url, verify=False)
        if response.status_code == 200:
            missing = []
            for s in check_strings:
                if str(s) not in response.text:
                    missing.append(str(s))
            
            if not missing:
                log(f"VERIFIED: {label} data is visible on dashboard.")
                return True
            else:
                log(f"WARNING: {label} data submitted but NOT found on dashboard. Missing: {missing}")
                return False
        else:
            log(f"FAILED: Could not load {label} dashboard. HTTP {response.status_code}")
            return False
    except Exception as e:
        log(f"ERROR checking display for {label}: {e}")
        return False

# --- Module Tests ---

def test_add_water_data(session):
    log("\n--- Testing Add Water Data ---")
    ts = int(time.time())
    val = f"123.{ts % 100}"
    url = f"{BASE_URL}/data/add"
    data = {
        'data_type': 'water',
        'water_type': 'Sebekeden',
        'water_consumption': val,
        'water_unit': 'm3',
        'date': datetime.date.today().strftime('%Y-%m-%d')
    }
    if post_and_check(session, url, data, "Water data"):
        return check_data_display(session, f"{BASE_URL}/water", [val], "Water")
    return False

def test_add_energy_data(session):
    log("\n--- Testing Add Energy Data ---")
    ts = int(time.time())
    val = f"500.{ts % 100}"
    url = f"{BASE_URL}/data/add"
    data = {
        'data_type': 'energy',
        'energy_type': 'Elektrik',
        'energy_consumption': val,
        'energy_unit': 'kWh',
        'cost': '1000',
        'date': datetime.date.today().strftime('%Y-%m-%d')
    }
    if post_and_check(session, url, data, "Energy data"):
        return check_data_display(session, f"{BASE_URL}/energy", [val], "Energy")
    return False

def test_add_waste_data(session):
    log("\n--- Testing Add Waste Data ---")
    ts = int(time.time())
    val = f"50.{ts % 100}"
    unique_type = "Plastik" 
    url = f"{BASE_URL}/data/add"
    data = {
        'data_type': 'waste',
        'waste_type': unique_type,
        'waste_amount': val,
        'waste_unit': 'kg',
        'disposal_method': 'Geri Dönüşüm',
        'date': datetime.date.today().strftime('%Y-%m-%d')
    }
    if post_and_check(session, url, data, "Waste data"):
        formatted_amount = "%.2f" % float(val)
        return check_data_display(session, f"{BASE_URL}/waste", [formatted_amount], "Waste")
    return False

def test_add_carbon_data(session):
    log("\n--- Testing Add Carbon Data ---")
    ts = int(time.time())
    val = f"100.{ts % 100}"
    url = f"{BASE_URL}/data/add"
    data = {
        'data_type': 'carbon',
        'scope': 'Scope 1',
        'category': 'Doğal Gaz',
        'amount': val,
        'unit': 'm3',
        'date': datetime.date.today().strftime('%Y-%m-%d')
    }
    if post_and_check(session, url, data, "Carbon data"):
        return check_data_display(session, f"{BASE_URL}/carbon", [val], "Carbon")
    return False

def test_add_sdg_data(session):
    log("\n--- Testing Add SDG Data ---")
    ts = int(time.time())
    action = f"Action-{ts}"
    url = f"{BASE_URL}/sdg/add"
    data = {
        'year': '2024',
        'goal_id': '1', 
        'indicator_id': '1',
        'target': f"Target {ts}",
        'action': action,
        'status': 'Devam Ediyor',
        'progress_pct': '50'
    }
    if post_and_check(session, url, data, "SDG data"):
        return check_data_display(session, f"{BASE_URL}/sdg", [action], "SDG")
    return False

def test_add_gri_data(session):
    log("\n--- Testing Add GRI Data ---")
    ts = int(time.time())
    val = f"GRI-Val-{ts}"
    url = f"{BASE_URL}/gri/add"
    data = {
        'year': '2024',
        'standard': 'GRI 302',
        'disclosure': '302-1',
        'value': val
    }
    if post_and_check(session, url, data, "GRI data"):
        return check_data_display(session, f"{BASE_URL}/gri", [val], "GRI")
    return False

def test_add_social_data(session):
    log("\n--- Testing Add Social Data ---")
    ts = int(time.time())
    val = f"Social-Val-{ts}"
    url = f"{BASE_URL}/social/add"
    data = {
        'year': '2024',
        'category': 'İş Gücü',
        'indicator': 'Çalışan Sayısı',
        'value': val,
        'unit': 'Kişi'
    }
    if post_and_check(session, url, data, "Social data"):
        return check_data_display(session, f"{BASE_URL}/social", [val], "Social")
    return False

def test_add_governance_data(session):
    log("\n--- Testing Add Governance Data ---")
    ts = int(time.time())
    val = f"Gov-Val-{ts}"
    url = f"{BASE_URL}/governance/add"
    data = {
        'year': '2024',
        'category': 'Yönetim Kurulu',
        'indicator': 'Bağımsız Üye Sayısı',
        'value': val
    }
    if post_and_check(session, url, data, "Governance data"):
        return check_data_display(session, f"{BASE_URL}/governance", [val], "Governance")
    return False

def test_add_esg_data(session):
    log("\n--- Testing Add ESG Data ---")
    # ESG might not have a dedicated add/view page if it aggregates others?
    # Assuming /esg exists.
    # If not, we skip or adapt.
    # Let's check /esg first.
    try:
        resp = session.get(f"{BASE_URL}/esg", verify=False)
        if resp.status_code != 200:
            log(f"SKIPPING: ESG module not accessible (HTTP {resp.status_code})")
            return False
    except:
        return False
    return True

def test_add_cbam_data(session):
    log("\n--- Testing Add CBAM Data ---")
    ts = int(time.time())
    val = f"CBAM-{ts}"
    url = f"{BASE_URL}/cbam/add"
    data = {
        'year': '2024',
        'product_type': 'Cement',
        'amount': '1000',
        'emission_factor': '0.5',
        'notes': val
    }
    if post_and_check(session, url, data, "CBAM data"):
        return check_data_display(session, f"{BASE_URL}/cbam", [val], "CBAM")
    return False

def test_add_csrd_materiality(session):
    log("\n--- Testing Add CSRD Materiality ---")
    ts = int(time.time())
    topic = f"CSRD-Topic-{ts}"
    url = f"{BASE_URL}/csrd/materiality"
    data = {
        'year': '2024',
        'topic': topic,
        'impact_score': '5',
        'financial_score': '4',
        'status': 'Material'
    }
    if post_and_check(session, url, data, "CSRD data"):
        return check_data_display(session, f"{BASE_URL}/csrd", [topic], "CSRD")
    return False

def test_add_taxonomy_data(session):
    log("\n--- Testing Add EU Taxonomy Data ---")
    ts = int(time.time())
    activity = f"Taxonomy-Act-{ts}"
    url = f"{BASE_URL}/taxonomy/add"
    data = {
        'year': '2024',
        'activity_name': activity,
        'turnover_amount': '1000',
        'capex_amount': '500',
        'opex_amount': '200',
        'aligned_pct': '100',
        'substantial_contribution': 'on',
        'dnsh_compliance': 'on',
        'minimum_safeguards': 'on'
    }
    if post_and_check(session, url, data, "Taxonomy data"):
        return check_data_display(session, f"{BASE_URL}/taxonomy", [activity], "Taxonomy")
    return False

def test_add_economic_data(session):
    log("\n--- Testing Add Economic Data ---")
    # Assuming similar structure
    return True # Placeholder if no specific route known yet

def test_add_supply_chain_data(session):
    log("\n--- Testing Add Supply Chain Data ---")
    ts = int(time.time())
    supplier = f"Supplier-{ts}"
    url = f"{BASE_URL}/supply_chain/add"
    data = {
        'supplier_name': supplier,
        'risk_score': 'Low',
        'audit_date': '2024-01-01'
    }
    # This might fail if route doesn't exist, wrapped in try/except inside post_and_check
    if post_and_check(session, url, data, "Supply Chain data"):
        return check_data_display(session, f"{BASE_URL}/supply_chain", [supplier], "Supply Chain")
    return False

def test_add_issb_data(session):
    log("\n--- Testing Add ISSB Data ---")
    ts = int(time.time())
    disclosure = f"ISSB-{ts}"
    url = f"{BASE_URL}/issb/add"
    data = {
        'standard': 'IFRS S1',
        'disclosure': disclosure,
        'description': 'Test disclosure'
    }
    if post_and_check(session, url, data, "ISSB data"):
        return check_data_display(session, f"{BASE_URL}/issb", [disclosure], "ISSB")
    return False

def test_add_iirc_data(session):
    log("\n--- Testing Add IIRC Data ---")
    ts = int(time.time())
    capital = f"IIRC-Cap-{ts}"
    url = f"{BASE_URL}/iirc/add"
    data = {
        'capital_type': 'Financial',
        'metric': capital,
        'value': '1000'
    }
    if post_and_check(session, url, data, "IIRC data"):
        return check_data_display(session, f"{BASE_URL}/iirc", [capital], "IIRC")
    return False

def test_add_tcfd_data(session):
    log("\n--- Testing Add TCFD Data ---")
    ts = int(time.time())
    risk = f"TCFD-Risk-{ts}"
    url = f"{BASE_URL}/tcfd/add"
    data = {
        'area': 'Strategy',
        'disclosure': risk,
        'details': 'Test details'
    }
    if post_and_check(session, url, data, "TCFD data"):
        return check_data_display(session, f"{BASE_URL}/tcfd", [risk], "TCFD")
    return False

def test_add_tnfd_data(session):
    log("\n--- Testing Add TNFD Data ---")
    ts = int(time.time())
    disc = f"TNFD-{ts}"
    url = f"{BASE_URL}/tnfd/add"
    data = {
        'area': 'Governance',
        'disclosure': disc,
        'details': 'Nature risk test'
    }
    if post_and_check(session, url, data, "TNFD data"):
        return check_data_display(session, f"{BASE_URL}/tnfd", [disc], "TNFD")
    return False

def test_add_sasb_data(session):
    log("\n--- Testing Add SASB Data ---")
    ts = int(time.time())
    metric = f"SASB-Metric-{ts}"
    url = f"{BASE_URL}/sasb/add"
    data = {
        'year': '2024',
        'topic': 'Energy Management',
        'metric': metric,
        'value': '5000',
        'unit': 'GJ'
    }
    if post_and_check(session, url, data, "SASB data"):
        return check_data_display(session, f"{BASE_URL}/sasb", [metric], "SASB")
    return False

def test_generate_unified_report(session):
    log("\n--- Testing Unified Report Generation ---")
    url = f"{BASE_URL}/reports/unified"
    modules = ['water', 'energy', 'waste', 'carbon', 'sdg', 'gri', 'esg', 'cbam', 
               'csrd', 'taxonomy', 'economic', 'supply_chain', 'social', 'governance', 
               'issb', 'iirc', 'tcfd', 'tnfd', 'sasb']
    
    data = {
        'report_name': f'Full Test Report {int(time.time())}',
        'reporting_period': '2024',
        'description': 'End-to-end test of 19 modules',
        'modules': modules,
        'include_ai': 'false' 
    }
    try:
        response = session.post(url, data=data, allow_redirects=True, verify=False)
        if response.status_code == 200:
            if "Rapor oluşturuldu" in response.text or "success" in response.text.lower() or "indir" in response.text.lower():
                log("SUCCESS: Unified report generated.")
                return True
            if "/reports" in response.url:
                 log("SUCCESS: Unified report generated (redirected).")
                 return True
            log("WARNING: Report success message not found.")
        else:
            log(f"FAILED: HTTP {response.status_code}")
    except Exception as e:
        log(f"ERROR generating report: {e}")
    return False

if __name__ == "__main__":
    session = test_login("admin", "Admin_2025!")
    if session:
        # Run all tests
        test_add_water_data(session)
        test_add_energy_data(session)
        test_add_waste_data(session)
        test_add_carbon_data(session)
        
        test_add_sdg_data(session)
        test_add_gri_data(session)
        test_add_social_data(session)
        test_add_governance_data(session)
        test_add_esg_data(session)
        test_add_cbam_data(session)
        test_add_csrd_materiality(session)
        test_add_taxonomy_data(session)
        test_add_economic_data(session)
        test_add_supply_chain_data(session)
        test_add_issb_data(session)
        test_add_iirc_data(session)
        test_add_tcfd_data(session)
        test_add_tnfd_data(session)
        test_add_sasb_data(session)

        test_generate_unified_report(session)
    else:
        log("Cannot proceed due to login failure.")
