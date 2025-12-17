import os
import json
import requests
import time
import sys

# Load API Key from GitHub Secrets
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# --- THE MODEL ROTATION LIST ---
# If one fails, the script automatically tries the next one.
# These are all currently FREE on OpenRouter.
MODELS_TO_TRY = [
    "google/gemini-2.0-flash-exp:free",        # Option 1: Smartest & Fastest
    "google/gemini-2.0-flash-thinking-exp:free", # Option 2: Smart Alternative
    "meta-llama/llama-3.2-3b-instruct:free",   # Option 3: Very Reliable
    "microsoft/phi-3-mini-128k-instruct:free", # Option 4: Backup
    "huggingfaceh4/zephyr-7b-beta:free"        # Option 5: Last Resort
]

def ask_ai(prompt, system_instruction="You are a helpful AI assistant."):
    """
    Sends a prompt to OpenRouter. 
    Implements 'Model Rotation' to handle 429 Rate Limits.
    """
    
    # 1. CHECK API KEY
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

    # 2. LOOP THROUGH MODELS
    for model in MODELS_TO_TRY:
        print(f"📡 Connecting to AI Model: {model}...")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            # We request JSON, but some free models might ignore this. 
            # Our prompt text also demands JSON, so it usually works.
            "response_format": { "type": "json_object" } 
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # SUCCESS CHECK (Status 200)
            if response.status_code == 200:
                data = response.json()
                
                if 'choices' in data and len(data['choices']) > 0:
                    raw_content = data['choices'][0]['message']['content']
                    
                    # Try to parse JSON immediately to ensure quality
                    try:
                        clean_json = json.loads(raw_content)
                        return clean_json # SUCCESS! Return the data.
                    except json.JSONDecodeError:
                        print(f"⚠️ Model {model} returned invalid JSON. Retrying...")
                        # If JSON is bad, we treat it as a failure and try next model
                        continue
            
            # FAILURE HANDLING (429, 500, 503)
            print(f"⚠️ Model {model} failed (Status: {response.status_code}). Switching...")
            print(f"   Server Message: {response.text[:200]}") # Print first 200 chars of error
            
            # Wait 2 seconds before hitting the next model to be polite
            time.sleep(2) 

        except Exception as e:
            print(f"⚠️ Connection Error with {model}: {e}")
            time.sleep(1)

    # 3. FATAL ERROR (If loop finishes and nothing worked)
    print("❌ FATAL ERROR: All AI models are busy, down, or returning bad data.")
    return None
