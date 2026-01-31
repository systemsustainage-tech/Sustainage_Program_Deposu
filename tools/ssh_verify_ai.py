import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

def verify_ai():
    print("--- Verifying OpenAI Integration ---")
    
    # Load environment variables
    env_path = '/var/www/sustainage/.env'
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded .env from {env_path}")
    else:
        print(f"ERROR: .env file not found at {env_path}")
        return

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in .env")
        return
    
    # Check if key looks valid (basic check)
    if not api_key.startswith('sk-'):
        print(f"WARNING: API Key format seems incorrect (starts with {api_key[:3]}...)")
    else:
        print("API Key format check: OK")

    try:
        client = OpenAI(api_key=api_key)
        print("Attempting OpenAI API connection...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, are you working?"}
            ],
            max_tokens=10
        )
        
        content = response.choices[0].message.content
        print("Success! OpenAI Response:")
        print(content)
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")

if __name__ == "__main__":
    verify_ai()
