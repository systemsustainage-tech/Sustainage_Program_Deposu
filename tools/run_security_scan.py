import os
import subprocess
import sys
import json

def run_bandit():
    print("--- Running Bandit (SAST) ---")
    # -ll means Medium and High severity
    # We exclude tests, tools, venv, and hidden folders
    cmd = [sys.executable, "-m", "bandit", "-r", ".", "-x", "./tests,./tools,./venv,./.trae", "-ll", "-f", "txt"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("Bandit passed (no medium/high severity issues found).")
        else:
            print("Bandit found issues (see above).")
    except Exception as e:
        print(f"Error running bandit: {e}")

def run_pylint():
    print("\n--- Running Pylint (Code Quality) ---")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + os.path.join(os.getcwd(), "backend")
    
    cmd = [sys.executable, "-m", "pylint", "web_app.py", "backend/modules", "--errors-only"]
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print("Pylint passed (no errors).")
        else:
            print("Pylint found errors.")
                
    except Exception as e:
        print(f"Error running pylint: {e}")

def check_dependencies():
    print("\n--- Running Dependency Vulnerability Scan (OWASP Top 10) ---")
    # Using pip-audit if available, otherwise fallback to simple check
    try:
        # Try running pip-audit
        cmd = [sys.executable, "-m", "pip_audit"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
             print("pip-audit passed: No known vulnerabilities found.")
        else:
             if "No module named pip_audit" in result.stderr:
                 print("pip-audit not installed. Performing basic check...")
                 _basic_dependency_check()
             else:
                 print("Vulnerabilities found:")
                 print(result.stdout)
                 print(result.stderr)
    except Exception as e:
        print(f"Error running dependency check: {e}")
        _basic_dependency_check()

def _basic_dependency_check():
    # Simple check against a known bad list (Mocking OWASP check)
    print("Scanning installed packages against known vulnerable versions...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"], capture_output=True, text=True)
        packages = json.loads(result.stdout)
        
        # Example vulnerable versions (Mock DB)
        known_vulnerabilities = {
            "flask": ["0.12", "1.0"],
            "requests": ["2.20.0"],
            "jinja2": ["2.10"]
        }
        
        issues = []
        for pkg in packages:
            name = pkg['name'].lower()
            version = pkg['version']
            
            if name in known_vulnerabilities:
                if version in known_vulnerabilities[name]:
                    issues.append(f"{name} {version} is known to be vulnerable.")
        
        if issues:
            print("WARNING: Vulnerable packages found:")
            for i in issues:
                print(f" - {i}")
        else:
            print("No obvious vulnerable packages found (Basic Check).")
            
    except Exception as e:
        print(f"Failed to list packages: {e}")

def check_quality_thresholds():
    print("\n--- Verifying Quality Thresholds ---")
    try:
        subprocess.run([sys.executable, "tools/check_quality.py"], check=False)
    except Exception as e:
        print(f"Error running quality check: {e}")

if __name__ == "__main__":
    print("Starting Security and Quality Scan...")
    run_bandit()
    run_pylint()
    check_dependencies()
    check_quality_thresholds()
    print("\nScan Completed.")
