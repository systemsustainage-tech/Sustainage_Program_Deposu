
import os

file_path = 'c:\\SUSTAINAGESERVER\\web_app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# We want to remove the first block of supply_chain routes
# Based on my analysis, it starts at @app.route('/supply_chain') around line 6446
# And ends before @app.route('/issb') around line 6519

start_marker = "@app.route('/supply_chain')"
end_marker = "@app.route('/issb')"

# Find the first occurrence of start_marker
start_index = -1
for i, line in enumerate(lines):
    if start_marker in line:
        # We need to make sure this is the *first* occurrence (the wrong one)
        # The second occurrence is much later (around 9440)
        # Since we are iterating from 0, this should be the first one.
        if i < 8000: # Safety check
            start_index = i
            break

if start_index == -1:
    print("Could not find the first supply_chain route block.")
    exit(1)

# Find the next route definition after start_index to define the end of the block
end_index = -1
for i in range(start_index + 1, len(lines)):
    if end_marker in line or "@app.route('/issb')" in lines[i]:
        end_index = i
        break

if end_index == -1:
    print("Could not find the end of the supply_chain route block (issb).")
    exit(1)

print(f"Removing lines {start_index+1} to {end_index} (exclusive of end_index)")
print(f"Start line content: {lines[start_index]}")
print(f"End line content: {lines[end_index]}")

# Keep lines before start_index and from end_index onwards
new_lines = lines[:start_index] + lines[end_index:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully removed the duplicate supply_chain routes.")
