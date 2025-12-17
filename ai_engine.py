import os
import json
import requests
import time
import re

# Load API Key
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# --- NEWEST FREE MODELS (Less Traffic) ---
MODELS_TO_TRY = [
    "google/gemini-2.0-flash-lite-preview-02-05:free", # Brand new, fast
    "google/gemini-2.0-pro-exp-02-05:free",            # Brand new, smart
    "meta-llama/llama-3.3-70b-instruct:free",          # Reliable
    "google/gemini-2.0-flash-exp:free",                # Standard
    "sophosympatheia/midnight-rose-70b:free"           # Creative/Storyteller
]

def extract_json(text):
    """Finds JSON even if the AI talks too much."""
    try:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match: return json.loads(match.group(1))
        match = re.search(r'(\{.*\})', text, re.DOTALL)
        if match: return json.loads(match.group(1))
        return json.loads(text)
    except:
        return None

def ask_ai(prompt, system_instruction="You are a helpful AI assistant."):
    if not OPENROUTER_API_KEY:
        print("❌ CRITICAL: OPENROUTER_API_KEY is missing.")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ZodiacVault", 
        "X-Title": "Zodiac Automation"
    }

    # RETRY LOGIC: Try the whole list 2 times
    for attempt in range(2): 
        print(f"🔄 Attempt {attempt + 1} of 2...")
        
        for model in MODELS_TO_TRY:
            print(f"📡 Connecting to: {model}...")
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.85
            }
            
            try:
                # 30s timeout is enough
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        clean_json = extract_json(content)
                        if clean_json: return clean_json
                
                elif response.status_code == 429:
                    print(f"⚠️ {model} is Busy (429). Waiting 5s...")
                    time.sleep(5) # Wait before switching
                else:
                    print(f"⚠️ {model} failed (Status: {response.status_code}). Switching...")
                
            except Exception as e:
                print(f"⚠️ Connection Error: {e}")
                
            time.sleep(1) # Short pause between models

    print("❌ FATAL: All AI models failed after multiple attempts.")
    return None
