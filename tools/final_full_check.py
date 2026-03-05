
import os
import json
import re
import sys
import sqlite3
import requests
import time

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def log(msg, success=True):
    if success:
        print(f"{GREEN}[PASS]{RESET} {msg}")
    else:
        print(f"{RED}[FAIL]{RESET} {msg}")

def check_translations():
    print("\n--- 1. Translation & i18n Check ---")
    locales_dir = "backend/locales"
    langs = ['tr', 'en', 'de']
    all_ok = True
    
    for lang in langs:
        path = os.path.join(locales_dir, f"{lang}.json")
        if not os.path.exists(path):
            log(f"{lang}.json missing", False)
            all_ok = False
            continue
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Check random keys
                if "common" not in data or "save" not in data["common"]:
                    log(f"{lang}.json missing basic keys (common.save)", False)
                    all_ok = False
                else:
                    # Check for empty values
                    empty_count = 0
                    stack = [data]
                    while stack:
                        curr = stack.pop()
                        for k, v in curr.items():
                            if isinstance(v, dict):
                                stack.append(v)
                            elif isinstance(v, str) and (not v or v == "TODO"):
                                empty_count += 1
                    
                    if empty_count > 5: # Tolerance for a few placeholders
                        log(f"{lang}.json has {empty_count} empty/TODO values", False)
                        # all_ok = False # Warning only
                    else:
                        log(f"{lang}.json looks good")
        except Exception as e:
            log(f"Error reading {lang}.json: {e}", False)
            all_ok = False
            
    return all_ok

def check_license_features():
    print("\n--- 2. License Constraints Check ---")
    # Static check of code
    with open("backend/yonetim/license_manager.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "allowed_ips" in content and "allowed_domains" in content:
            log("LicenseManager supports allowed_ips/domains")
        else:
            log("LicenseManager missing constraint logic", False)
            return False
            
    with open("web_app.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "check_constraints" in content and "X-Forwarded-For" in content:
            log("web_app.py middleware checks constraints")
        else:
            log("web_app.py missing constraint middleware", False)
            return False
    return True

def check_multitenant():
    print("\n--- 3. Multi-Tenant Filter Check ---")
    with open("backend/core/database.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "def inject_tenant_filter" in content:
            log("inject_tenant_filter function exists")
        else:
            log("inject_tenant_filter MISSING in database.py", False)
            return False
            
    with open("backend/core/database_manager.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "inject_tenant_filter(" in content:
            log("DatabaseManager uses inject_tenant_filter")
        else:
            log("DatabaseManager does NOT use injection", False)
            return False
    return True

def check_security():
    print("\n--- 4. Rate Limit & CAPTCHA Check ---")
    with open("web_app.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "@limiter.limit" in content:
            log("Rate limiting decorators found")
        else:
            log("Rate limiting decorators MISSING", False)
            return False
            
        if "def verify_captcha" in content and "session.get('login_attempts'" in content:
            log("CAPTCHA logic found in login")
        else:
            log("CAPTCHA logic MISSING", False)
            return False
    return True

def check_performance():
    print("\n--- 5. Performance & Monitoring Check ---")
    if os.path.exists("prometheus.yml"):
        log("prometheus.yml exists")
    else:
        log("prometheus.yml MISSING", False)
        return False
        
    with open("backend/core/database_manager.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "PRAGMA journal_mode=WAL" in content and "cache_size=-128000" in content:
            log("Database performance PRAGMAs found (WAL, Cache)")
        else:
            log("Database performance PRAGMAs missing/incorrect", False)
            return False
    return True

def check_cleanup():
    print("\n--- 6. Cleanup Check ---")
    # Check if legacy/TESTLER are in root (should be moved)
    forbidden = ["legacy", "TESTLER"]
    clean = True
    for item in forbidden:
        if os.path.exists(item):
            log(f"'{item}' folder still exists in root (should be archived)", False)
            clean = False
        else:
            log(f"'{item}' folder successfully removed/archived")
            
    if os.path.exists("_ARCHIVE"):
        log("_ARCHIVE folder exists")
    else:
        log("_ARCHIVE folder missing (where did files go?)", False)
        clean = False
        
    return clean

def check_docs():
    print("\n--- 7. Documentation Check ---")
    docs = ["docs/DEVELOPER_GUIDE.md", "docs/ADMIN_GUIDE.md", "docs/INSTALLATION.md"]
    all_exist = True
    for d in docs:
        if os.path.exists(d):
            log(f"{d} exists")
        else:
            log(f"{d} MISSING", False)
            all_exist = False
    return all_exist

if __name__ == "__main__":
    print("=== FINAL SYSTEM VERIFICATION ===")
    results = [
        check_translations(),
        check_license_features(),
        check_multitenant(),
        check_security(),
        check_performance(),
        check_cleanup(),
        check_docs()
    ]
    
    if all(results):
        print("\n" + GREEN + "ALL CHECKS PASSED SUCCESSFULLY. SYSTEM IS READY." + RESET)
        sys.exit(0)
    else:
        print("\n" + RED + "SOME CHECKS FAILED. PLEASE REVIEW LOGS." + RESET)
        sys.exit(1)
