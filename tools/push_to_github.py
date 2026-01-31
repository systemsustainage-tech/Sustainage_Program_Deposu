import os
import subprocess
import sys

# Configuration
TOKEN_FILE = r"c:\SUSTAINAGESERVER\config\github_token.txt"
REPO_USER = "systemsustainage-tech"
REPO_NAME = "Sustainage_Program_Deposu"
REPO_URL = f"https://github.com/{REPO_USER}/{REPO_NAME}.git"

def get_token():
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: Token file not found at {TOKEN_FILE}")
        return None
    with open(TOKEN_FILE, 'r') as f:
        return f.read().strip()

def run_git_command(args):
    try:
        # Hide token in output if possible, but here we just print stdout
        print(f"Running: git {' '.join(args)}")
        result = subprocess.run(['git'] + args, capture_output=True, text=True)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        if result.returncode != 0:
            print(f"Command failed with return code {result.returncode}")
            return False
        return True
    except Exception as e:
        print(f"Error running git {' '.join(args)}:")
        print(str(e))
        return False

def get_current_branch():
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "master"

def main():
    token = get_token()
    if not token:
        return

    # Construct Auth URL
    auth_url = f"https://{token}@{REPO_URL.replace('https://', '')}"

    print(f"Configuring remote 'origin' for {REPO_URL}...")
    
    # Check if remote exists
    result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Remote 'origin' exists. Updating URL...")
        run_git_command(['remote', 'set-url', 'origin', auth_url])
    else:
        print("Remote 'origin' does not exist. Adding...")
        run_git_command(['remote', 'add', 'origin', auth_url])

    # Check status
    print("Checking git status...")
    run_git_command(['status'])

    # Add all files
    print("Adding all files...")
    run_git_command(['add', '.'])

    # Commit if needed
    result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
    if result.returncode != 0:
        print("Committing changes...")
        run_git_command(['commit', '-m', 'Update from Trae session: Automatic sync'])
    else:
        print("No changes to commit.")

    # Get current branch
    branch = get_current_branch()
    print(f"Current branch: {branch}")

    # Push
    print(f"Pushing {branch} to GitHub...")
    
    # Handle master -> main mapping
    remote_branch = branch
    if branch == 'master':
        remote_branch = 'main'
        print(f"Mapping local '{branch}' to remote '{remote_branch}'")

    if run_git_command(['push', '--force', '-u', 'origin', f'{branch}:{remote_branch}']):
        print("Successfully pushed to GitHub!")
    else:
        print("Push failed. Please check credentials and network.")

if __name__ == "__main__":
    main()
