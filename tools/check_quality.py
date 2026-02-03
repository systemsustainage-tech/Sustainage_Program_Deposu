import sys
import os
import subprocess
import re

# Configuration: File/Directory -> Minimum Score
THRESHOLDS = {
    'web_app.py': 4.5,
    'web_app_remote.py': 4.0,
    'backend/': 7.0,
    'tools/': 7.0,
}

def get_pylint_score(target):
    """Runs pylint on the target and returns the score."""
    print(f"Running Pylint on {target}...")
    try:
        # Run pylint and capture output
        # We ignore the exit code because pylint returns non-zero for any issue
        result = subprocess.run(
            [sys.executable, "-m", "pylint", target],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        output = result.stdout
        
        # Extract score using regex
        match = re.search(r'Your code has been rated at (\-?[0-9.]+)/10', output)
        if match:
            return float(match.group(1))
        else:
            print(f"Could not parse Pylint score for {target}.")
            return 0.0
    except Exception as e:
        print(f"Error running Pylint on {target}: {e}")
        return 0.0

def main():
    """Main function to check quality thresholds."""
    print("Starting Quality Threshold Check...")
    print("=" * 40)
    
    failed = False
    
    for target, threshold in THRESHOLDS.items():
        # Check if target exists
        if not os.path.exists(target):
            print(f"Skipping {target}: File or directory not found.")
            continue
            
        score = get_pylint_score(target)
        status = "PASS" if score >= threshold else "FAIL"
        
        print(f"Target: {target}")
        print(f"Score:  {score:.2f}/10")
        print(f"Limit:  {threshold:.2f}/10")
        print(f"Status: {status}")
        print("-" * 40)
        
        if score < threshold:
            failed = True
            
    if failed:
        print("\nQuality Check FAILED: Some modules are below the quality threshold.")
        sys.exit(1)
    else:
        print("\nQuality Check PASSED: All modules meet the quality threshold.")
        sys.exit(0)

if __name__ == "__main__":
    main()
