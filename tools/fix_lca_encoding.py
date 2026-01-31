
import os

file_path = r'c:\SUSTAINAGESERVER\web_app.py'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Fixes
fixes = {
    9358: "    flash('Ürün başarıyla eklendi.', 'success')\n",
    9374: "        flash('Ürün bulunamadı.', 'error')\n",
    9388: "    flash('Analiz oluşturuldu.', 'success')\n",
    9398: "        flash('Analiz bulunamadı.', 'error')\n"
}

# Adjust line numbers (0-indexed in list)
for line_num, content in fixes.items():
    idx = line_num - 1
    # Verify we are replacing the correct line roughly (check indentation or keyword)
    if 'flash' in lines[idx]:
        print(f"Replacing line {line_num}: {lines[idx].strip()} -> {content.strip()}")
        lines[idx] = content
    else:
        print(f"Warning: Line {line_num} does not contain 'flash'. Skipping. Content: {lines[idx]}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("File updated.")
