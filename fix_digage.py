import os

path = '/var/www/DIGAGETRANSFER/main.py'
with open(path, 'r') as f:
    lines = f.readlines()

# Find the line with uvicorn.run
for i, line in enumerate(lines):
    if 'uvicorn.run(app' in line:
        print(f"Found line {i}: {line.strip()}")
        lines[i] = '    uvicorn.run(app, host="0.0.0.0", port=8002, proxy_headers=True, forwarded_allow_ips="*")\n'
        break

with open(path, 'w') as f:
    f.writelines(lines)
print("Updated main.py")
