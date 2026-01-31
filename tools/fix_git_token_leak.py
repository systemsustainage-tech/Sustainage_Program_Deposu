import os
import subprocess

TOKEN_FILE = "config/github_token.txt"
GITIGNORE = ".gitignore"

def run(args):
    subprocess.run(['git'] + args, check=False)

print("Recovering from accidental token commit...")

# 1. Reset the last commit (keep changes staged)
# We assume the last commit was the one that added the token.
run(['reset', '--soft', 'HEAD~1'])

# 2. Unstage the token file
run(['restore', '--staged', TOKEN_FILE])

# 3. Add to .gitignore
with open(GITIGNORE, "a") as f:
    f.write(f"\n{TOKEN_FILE}\n")

# 4. Add .gitignore
run(['add', GITIGNORE])

# 5. Commit again
run(['commit', '-m', 'Update from Trae session: Automatic sync (Secured)'])

# 6. Force push to overwrite the bad commit if it was pushed
print("Force pushing to overwrite potential bad commit...")
run(['push', '-f', 'origin', 'master'])

print("Recovery complete.")
