import os
import json
import requests
import time
import re

# Load API Key
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# --- RELIABLE FREE MODEL LIST ---
MODELS_TO_TRY = [
    "google/gemini-2.0-flash-exp:free",         # Best Quality
    "meta-llama/llama-3.2-3b-instruct:free",    # Most Reliable
    "microsoft/phi-3-medium-128k-instruct:free",# Backup
    "huggingfaceh4/zephyr-7b-beta:free",        # Fallback
]

def extract_json(text):
    """Finds JSON inside text if the AI talks too much."""
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

    for model in MODELS_TO_TRY:
        print(f"📡 Connecting to: {model}...")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    clean_json = extract_json(content)
                    if clean_json: return clean_json
            
            print(f"⚠️ {model} failed (Status: {response.status_code}). Switching...")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Error with {model}: {e}")
            time.sleep(1)

    print("❌ FATAL: All AI models failed.")
    return None
