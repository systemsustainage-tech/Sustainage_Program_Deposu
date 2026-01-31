import os
import re

TEMPLATE_DIR = r"c:\SUSTAINAGESERVER\templates"
SKIP_FILES = [
    "base.html", "login.html", "register.html", "forgot_password.html", 
    "reset_password.html", "verify_code.html", "survey_public.html", 
    "survey_success.html", "index.html", "email_new_user.html"
]

def analyze_templates():
    files_to_fix = []
    missing_back = []
    
    for root, dirs, files in os.walk(TEMPLATE_DIR):
        if "includes" in root or "supplier_portal" in root:
            continue
            
        for file in files:
            if file in SKIP_FILES or not file.endswith(".html"):
                continue
                
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            # Check for Back button
            has_back = "history.back()" in content or "btn_back" in content or "Geri" in content
            
            if not has_back:
                missing_back.append(file)
            else:
                # Check alignment (heuristic)
                # Look for back button pattern
                # Usually: <button ... onclick="history.back()">...
                # Check if it is inside a right-aligned container
                # We look for the button code and see if it's near 'justify-content-between' or 'btn-toolbar'
                
                # Simple check: is it in btn-toolbar?
                if "btn-toolbar" in content and "history.back()" in content:
                    # Likely ok, but let's see if the button is actually INSIDE it.
                    # This is hard with regex, but usually if both exist, it's likely fine or I put it there.
                    pass
                elif "d-flex justify-content-between" in content and "history.back()" in content:
                    pass
                else:
                    # Suspicious
                    files_to_fix.append(file)

    print("Missing Back Button:")
    for f in missing_back:
        print(f)
        
    print("\nPotentially Left Aligned or Misplaced:")
    for f in files_to_fix:
        print(f)

if __name__ == "__main__":
    analyze_templates()
