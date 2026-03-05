import os
import sys
import glob
import re

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def scan_tenant_compliance():
    print("Scanning codebase for TenantAwareModel compliance...")
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_dir = os.path.join(root_dir, 'backend')
    
    # Files to ignore (e.g. base classes, scripts)
    ignore_list = [
        'base_manager.py',
        'database_manager.py',
        '__init__.py',
        'tests',
        'tools'
    ]
    
    # Regex to find classes inheriting from BaseTenantManager
    manager_pattern = re.compile(r'class\s+(\w+)\s*\((.*?)\):')
    
    # Regex to find direct SQL execution
    sql_pattern = re.compile(r'\.(execute|execute_query|execute_update)\s*\(')
    
    # Regex to check if company_id is used in WHERE clause
    where_company_pattern = re.compile(r'WHERE.*company_id', re.IGNORECASE)
    
    compliance_issues = []
    
    for root, dirs, files in os.walk(backend_dir):
        if any(ignored in root for ignored in ['__pycache__', 'tests', 'tools']):
            continue
            
        for file in files:
            if not file.endswith('.py') or file in ignore_list:
                continue
                
            filepath = os.path.join(root, file)
            
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check inheritance
            if 'class ' in content:
                for match in manager_pattern.finditer(content):
                    class_name = match.group(1)
                    base_classes = match.group(2)
                    
                    if 'Manager' in class_name and 'BaseTenantManager' not in base_classes:
                        # Skip some known non-tenant managers
                        if class_name not in ['DatabaseManager', 'LanguageManager', 'EmailService', 'Icons']:
                            compliance_issues.append(f"⚠️ {file}: Class '{class_name}' might not be inheriting BaseTenantManager (Inherits: {base_classes})")

            # Check raw SQL queries for manual filtering
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if sql_pattern.search(line):
                    # Check context (next few lines) for company_id filter
                    context = " ".join(lines[i:i+5])
                    
                    # If it's calling self.execute_query, it might be auto-filtered by BaseTenantManager
                    # But if it calls db.execute_query directly, it needs manual check
                    
                    if 'self.db.execute' in line or 'cursor.execute' in line:
                        if 'company_id' not in context and 'skip_tenant_filter' not in context and 'CREATE TABLE' not in context:
                             compliance_issues.append(f"⚠️ {file}:{i+1}: Raw SQL execution without explicit 'company_id' in context. Please verify.")

    if compliance_issues:
        print(f"\nFound {len(compliance_issues)} potential compliance issues:")
        for issue in compliance_issues:
            print(issue)
    else:
        print("\n✅ No obvious tenant compliance issues found.")

if __name__ == "__main__":
    scan_tenant_compliance()
