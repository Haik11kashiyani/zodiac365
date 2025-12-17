import os
import json
import requests
import time
import re

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Newest models
MODELS_TO_TRY = [
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "google/gemini-2.0-pro-exp-02-05:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free"
]

def extract_json(text):
    try:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match: return json.loads(match.group(1))
        match = re.search(r'(\{.*\})', text, re.DOTALL)
        if match: return json.loads(match.group(1))
        return json.loads(text)
    except: return None

def ask_ai(prompt, system_instruction="You are a helpful AI assistant."):
    if not OPENROUTER_API_KEY:
        print("❌ CRITICAL: OPENROUTER_API_KEY is missing.")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/ZodiacVault", "X-Title": "Zodiac Automation"}

    # RETRY LOOP (2 Attempts per model)
    for attempt in range(2):
        print(f"🔄 Attempt {attempt+1}...")
        for model in MODELS_TO_TRY:
            print(f"📡 Connecting to {model}...")
            try:
                payload = {"model": model, "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}], "temperature": 0.85}
                r = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if r.status_code == 200:
                    data = r.json()
                    if 'choices' in data:
                        clean = extract_json(data['choices'][0]['message']['content'])
                        if clean: return clean
                elif r.status_code == 429:
                    print("⚠️ Busy (429). Waiting 5s...")
                    time.sleep(5)
                else:
                    print(f"⚠️ Error {r.status_code}")
            except Exception as e:
                print(f"⚠️ Exception: {e}")
            time.sleep(1)

    print("❌ FATAL: All AI models failed.")
    return None
