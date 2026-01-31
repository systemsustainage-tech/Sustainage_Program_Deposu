
import os
import subprocess
import sys

# Configuration
# Please create this file with your GitLab Personal Access Token
TOKEN_FILE = r"c:\SUSTAINAGESERVER\config\gitlab_token.txt"
# Update these if needed
REPO_USER = "systemsustainage-tech" 
REPO_NAME = "sustainage"
# Default to GitLab.com, change if using self-hosted
GITLAB_HOST = "gitlab.com" 
REPO_URL = f"https://{GITLAB_HOST}/{REPO_USER}/{REPO_NAME}.git"

def get_token():
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: GitLab Token file not found at {TOKEN_FILE}")
        print("Please create this file with your GitLab Personal Access Token to enable automatic pushing.")
        return None
    with open(TOKEN_FILE, 'r') as f:
        return f.read().strip()

def run_git_command(args):
    try:
        result = subprocess.run(['git'] + args, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running git {' '.join(args)}:")
        print(e.stderr)
        return False

def get_current_branch():
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "master"

def main():
    print("--- GitLab Push Tool ---")
    token = get_token()
    if not token:
        print("Skipping GitLab push due to missing token.")
        return

    # Construct Auth URL
    auth_url = f"https://oauth2:{token}@{GITLAB_HOST}/{REPO_USER}/{REPO_NAME}.git"

    print(f"Configuring remote 'gitlab' for {REPO_URL}...")
    
    # Check if remote exists
    result = subprocess.run(['git', 'remote', 'get-url', 'gitlab'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Remote 'gitlab' exists. Updating URL...")
        run_git_command(['remote', 'set-url', 'gitlab', auth_url])
    else:
        print("Remote 'gitlab' does not exist. Adding...")
        run_git_command(['remote', 'add', 'gitlab', auth_url])

    # Get current branch
    branch = get_current_branch()
    print(f"Current branch: {branch}")

    # Push
    print(f"Pushing {branch} to GitLab...")
    if run_git_command(['push', '-u', 'gitlab', branch]):
        print("Successfully pushed to GitLab!")
    else:
        print("Push failed. You might need to pull first or check permissions.")

if __name__ == "__main__":
    main()
