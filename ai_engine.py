import os
import json
import requests
import time
import re

# Load API Key
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# --- SAFEST FREE MODEL LIST (No 404s) ---
MODELS_TO_TRY = [
    "google/gemini-2.0-flash-exp:free",         # Often busy, but best
    "meta-llama/llama-3.2-3b-instruct:free",    # Very reliable
    "microsoft/phi-3-medium-128k-instruct:free",# Good fallback
    "huggingfaceh4/zephyr-7b-beta:free",        # Classic fallback
    "mistralai/mistral-7b-instruct:free"        # Standard fallback
]

def extract_json(text):
    """
    Extracts JSON from text if the AI adds extra words.
    """
    try:
        # Try to find JSON block between ```json and ```
        match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        
        # Try to find just the first { and last }
        match = re.search(r'(\{.*\})', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
            
        return json.loads(text) # Try raw
    except:
        return None

def ask_ai(prompt, system_instruction="You are a helpful AI assistant."):
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
            "temperature": 0.8,
            # REMOVED 'response_format' to fix Error 400
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    raw_content = data['choices'][0]['message']['content']
                    
                    # Manual Cleanup using our helper function
                    clean_json = extract_json(raw_content)
                    
                    if clean_json:
                        return clean_json
                    else:
                        print(f"⚠️ Model {model} returned invalid JSON structure. Retrying...")
                        continue
            
            print(f"⚠️ Model {model} failed (Status: {response.status_code}). Switching...")
            time.sleep(2) 

        except Exception as e:
            print(f"⚠️ Connection Error with {model}: {e}")
            time.sleep(1)

    print("❌ FATAL ERROR: All AI models are busy or down.")
    return None
