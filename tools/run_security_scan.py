import os
import subprocess
import sys

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
            # We don't exit with error here to allow pylint to run
    except Exception as e:
        print(f"Error running bandit: {e}")

def run_pylint():
    print("\n--- Running Pylint (Code Quality) ---")
    # Setting PYTHONPATH to include backend to resolve imports
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + os.path.join(os.getcwd(), "backend")
    
    # Analyze web_app.py and backend/modules
    # We limit to errors only for console output to avoid noise, but full report can be generated if needed
    cmd = [sys.executable, "-m", "pylint", "web_app.py", "backend/modules", "--errors-only"]
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print("Pylint passed (no errors).")
        else:
            print("Pylint found errors.")
            
        # Also run a score check (non-error mode)
        print("\nCalculating Pylint Score for web_app.py...")
        cmd_score = [sys.executable, "-m", "pylint", "web_app.py", "--disable=all", "--enable=F,E,W,R,C"] 
        # Actually just running it normally gives the score at the end
        cmd_score = [sys.executable, "-m", "pylint", "web_app.py"]
        result_score = subprocess.run(cmd_score, env=env, capture_output=True, text=True)
        for line in result_score.stdout.splitlines():
            if "Your code has been rated at" in line:
                print(line)
                
    except Exception as e:
        print(f"Error running pylint: {e}")

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
    check_quality_thresholds()
    print("\nScan Completed.")
