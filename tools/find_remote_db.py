import os
import sys

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f.endswith('.db') or f.endswith('.sqlite'):
                print('{}{}'.format(subindent, f))

if __name__ == "__main__":
    print("Searching for database files in /var/www/sustainage...")
    list_files('/var/www/sustainage')
