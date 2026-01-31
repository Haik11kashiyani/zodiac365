import os, json, requests, time, re
from cli_utils import log_info, log_error, log_warning, wait_random

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

def get_live_free_models():
    """Dynamically researches OpenRouter to find currently active free models."""
    try:
        url = "https://openrouter.ai/api/v1/models"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get('data', [])
            # Filter: pricing must be 0 for both prompt and completion
            free_list = [
                m['id'] for m in data 
                if float(m.get('pricing', {}).get('prompt', 1)) == 0 
                and float(m.get('pricing', {}).get('completion', 1)) == 0
            ]
            log_info(f"Oracle discovered {len(free_list)} active free models.")
            return free_list
    except Exception as e:
        log_warning(f"Research failed: {e}. Using fallback list.")
    
    # Fallback if the web research fails
    return ["google/gemini-2.0-flash-lite-preview-02-05:free", "meta-llama/llama-3.3-70b-instruct:free"]

def ask_google_fallback(prompt, sys_msg):
    """Fallback to Google Gemini Free Tier via REST"""
    google_key = os.environ.get("GOOGLE_API_KEY")
    if not google_key: return None
    
    log_info("Switching to Gemini Fallback...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={google_key}"
    headers = {"Content-Type": "application/json"}
    
    # Gemini valid payload
    payload = {
        "contents": [{
            "parts": [{"text": f"{sys_msg}\n\n{prompt}"}] 
        }]
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return json.loads(data['candidates'][0]['content']['parts'][0]['text'].replace("```json", "").replace("```", ""))
    except Exception as e:
        log_error(f"Gemini Fallback Failed: {e}")
    return None

def ask_ai(prompt, sys_msg="You are a mystical video director."):
    # 1. Try OpenRouter (Free Models)
    if OPENROUTER_API_KEY:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

        # Dynamic Model Switching
        models = get_live_free_models()
        for model_id in models:
            try:
                log_info(f"Consulting: {model_id}...")
                
                # Rate Limit Protection
                wait_random(2, 5, "Syncing with Oracle...")
                
                payload = {"model": model_id, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]}
                r = requests.post(url, headers=headers, json=payload, timeout=45)
                
                if r.status_code == 200:
                    content = r.json()['choices'][0]['message']['content']
                    # Helper to extract JSON from raw text
                    match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                    return json.loads(match.group(1)) if match else json.loads(content)
                elif r.status_code == 429: # Too Many Requests
                    log_warning(f"Rate Limit Hit on {model_id}. Cooling down...")
                    wait_random(10, 20, "Rate Limit Cooldown...")
                    continue
                    
                log_warning(f"{model_id} is busy (Status {r.status_code}). Rotating...")
                wait_random(1, 3, "Rotating satellite...")
            except Exception as e: 
                log_warning(f"Error on {model_id}: {e}")
                continue
            
    # 2. Try Google Gemini Fallback
    wait_random(3, 7, "Summoning Gemini...")
    return ask_google_fallback(prompt, sys_msg)
