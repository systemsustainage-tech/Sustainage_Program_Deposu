import os

def read_file_segment():
    path = '/var/www/sustainage/web_app.py'
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Print lines around 40-60
        for i in range(40, 60):
            if i < len(lines):
                print(f"{i+1}: {lines[i].rstrip()}")

if __name__ == "__main__":
    read_file_segment()
