import requests
import sys

TOKEN = sys.argv[1]
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

def list_repos():
    try:
        response = requests.get("https://api.github.com/user/repos?sort=updated&per_page=10", headers=HEADERS)
        if response.status_code == 200:
            repos = response.json()
            print(f"Successfully authenticated. Found {len(repos)} recent repositories:")
            for repo in repos:
                print(f"- {repo['name']} ({repo['html_url']})")
        else:
            print(f"Failed to authenticate: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_repos()
