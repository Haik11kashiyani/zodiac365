import os
import json
import requests
import time
import sys

# Load API Key from GitHub Secrets
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# --- UPDATED FREE MODEL LIST (More Reliable) ---
MODELS_TO_TRY = [
    "google/gemini-2.0-flash-lite-preview-02-05:free", # Newest Google model
    "deepseek/deepseek-r1:free",                       # Very smart, currently free
    "meta-llama/llama-3.3-70b-instruct:free",          # High quality Llama
    "qwen/qwen-2.5-coder-32b-instruct:free",           # Good fallback
    "google/gemini-2.0-pro-exp-02-05:free"             # Powerful Google fallback
]

def ask_ai(prompt, system_instruction="You are a helpful AI assistant."):
    """
    Sends a prompt to OpenRouter with robust failover.
    """
    if not OPENROUTER_API_KEY:
        print("❌ CRITICAL ERROR: OPENROUTER_API_KEY is missing.")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ZodiacVault", 
        "X-Title": "Zodiac Automation"
    }

    # LOOP THROUGH MODELS
    for model in MODELS_TO_TRY:
        print(f"📡 Connecting to AI Model: {model}...")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.85, # Slightly higher for creativity
            "response_format": { "type": "json_object" } 
        }
        
        try:
            # Increased timeout to 45s for deepseek
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    raw_content = data['choices'][0]['message']['content']
                    
                    # Clean markdown if model adds it (```json ...)
                    clean_content = raw_content.replace('```json', '').replace('```', '').strip()
                    
                    try:
                        return json.loads(clean_content)
                    except json.JSONDecodeError:
                        print(f"⚠️ Model {model} returned bad JSON. Retrying...")
                        continue
            
            # If we get here, it failed
            print(f"⚠️ Model {model} failed (Status: {response.status_code}). Switching...")
            time.sleep(2) 

        except Exception as e:
            print(f"⚠️ Connection Error with {model}: {e}")
            time.sleep(1)

    print("❌ FATAL ERROR: All AI models are busy or down.")
    return None
