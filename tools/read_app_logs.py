import os

ACCESS_LOG = '/var/www/sustainage/logs/access.log'
ERROR_LOG = '/var/www/sustainage/logs/error.log'

def read_tail(path, lines=50):
    if not os.path.exists(path):
        print(f"{path} not found.")
        return
        
    print(f"--- {path} (last {lines} lines) ---")
    try:
        with open(path, 'r') as f:
            content = f.readlines()
            for line in content[-lines:]:
                print(line, end='')
    except Exception as e:
        print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    read_tail(ACCESS_LOG)
    print("\n")
    read_tail(ERROR_LOG)
