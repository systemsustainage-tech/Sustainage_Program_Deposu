import sys
import os
sys.path.append('/var/www/sustainage')

def verify_translation():
    print("--- Verifying Translation API ---")
    try:
        from utils.language_manager import LanguageManager
        lm = LanguageManager()
        
        print(f"Google Cloud Available: {lm.translate_client is not None}")
        
        if lm.translate_client:
            print("Attempting translation...")
            try:
                # Using the client directly or a method if available
                # LanguageManager doesn't seem to have a direct translate method exposed in __init__
                # but let's check the client.
                text = "Merhaba Dünya"
                result = lm.translate_client.translate(text, target_language='en')
                print(f"Original: {text}")
                print(f"Translated: {result['translatedText']}")
                print("Translation API SUCCESS")
            except Exception as e:
                print(f"Translation API Error: {e}")
        else:
            print("Translation API NOT initialized.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_translation()
