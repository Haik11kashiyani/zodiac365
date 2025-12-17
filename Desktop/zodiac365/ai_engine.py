import os
import json
import requests

# Load API Key from GitHub Secrets
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

def ask_ai(prompt, system_instruction="You are a helpful AI assistant."):
    """
    Sends a prompt to OpenRouter and returns the text response.
    Uses 'google/gemini-2.0-flash-exp:free' because it is fast, smart, and free.
    """
    
    if not OPENROUTER_API_KEY:
        print("❌ ERROR: OPENROUTER_API_KEY is missing in Environment Variables.")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/YourUser/ZodiacVault", # Optional: Required by OpenRouter rules
        "X-Title": "Zodiac Vault Automation"
    }
    
    payload = {
        "model": "google/gemini-2.0-flash-exp:free", # FREE MODEL
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8, # High creativity for Astrology/Tarot
        "response_format": { "type": "json_object" } # Forces strict JSON output
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Check for errors
        
        data = response.json()
        raw_content = data['choices'][0]['message']['content']
        
        # Ensure it's valid JSON before returning
        return json.loads(raw_content)
        
    except Exception as e:
        print(f"❌ AI Generation Failed: {e}")
        if 'response' in locals():
            print(f"Server Response: {response.text}")
        return None