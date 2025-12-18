import os, json, requests, time, re

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODELS_TO_TRY = [
    "google/gemini-2.0-flash-lite-preview-02-05:free",
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
    if not OPENROUTER_API_KEY: return None
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    for model in MODELS_TO_TRY:
        try:
            payload = {"model": model, "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}], "temperature": 0.8}
            r = requests.post(url, headers=headers, json=payload, timeout=45)
            if r.status_code == 200:
                clean = extract_json(r.json()['choices'][0]['message']['content'])
                if clean: return clean
            time.sleep(2)
        except: continue
    return None
