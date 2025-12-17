import os
import json
import requests
import sys

# Load API Key from GitHub Secrets
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

def ask_ai(prompt, system_instruction="You are a helpful AI assistant."):
    """
    Sends a prompt to OpenRouter and returns the text response.
    Includes detailed error logging for debugging.
    """
    
    # 1. CHECK API KEY
    if not OPENROUTER_API_KEY:
        print("❌ CRITICAL ERROR: OPENROUTER_API_KEY is missing in Environment Variables.")
        print("   -> Did you add it to GitHub Secrets?")
        print("   -> Did you include 'env: OPENROUTER_API_KEY' in the YAML file?")
        return None

    print("📡 Connecting to OpenRouter AI...")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ZodiacVault", 
        "X-Title": "Zodiac Automation"
    }
    
    # Using the free Gemini 2.0 Flash model
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8, 
        "response_format": { "type": "json_object" } 
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # 2. CHECK HTTP STATUS
        if response.status_code != 200:
            print(f"❌ API REQUEST FAILED. Status Code: {response.status_code}")
            print(f"⚠️ Server Response: {response.text}")
            return None
            
        data = response.json()
        
        # 3. CHECK CONTENT
        if 'choices' not in data or len(data['choices']) == 0:
            print(f"❌ EMPTY RESPONSE FROM AI: {data}")
            return None

        raw_content = data['choices'][0]['message']['content']
        
        # 4. PARSE JSON
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            print(f"❌ AI returned invalid JSON: {raw_content}")
            return None
        
    except Exception as e:
        print(f"❌ AI ENGINE EXCEPTION: {e}")
        return None
