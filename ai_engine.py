import os, json, requests, time, re
from cli_utils import log_info, log_error, log_warning, wait_random

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

_cached_models = None

def get_live_free_models():
    """Dynamically discovers free models from OpenRouter. Cached per run."""
    global _cached_models
    if _cached_models is not None:
        return _cached_models

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
            _cached_models = free_list
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

def ask_ai(prompt, sys_msg="You are a professional Western astrologer with 30+ years of experience. You create highly specific, authentic horoscope predictions using real planetary transits, house placements, and aspects. Your predictions always include concrete details — specific planets, house numbers, and aspects. You NEVER give vague motivational advice. You speak with authority and warmth, like a trusted cosmic guide. You always respond in valid JSON only."):
    # 1. Try OpenRouter (Free Models)
    if OPENROUTER_API_KEY:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}

        # Dynamic Model Switching — limit to top 5 models to avoid wasting CI time
        models = get_live_free_models()[:5]
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
    result = ask_google_fallback(prompt, sys_msg)
    if result:
        return result
    
    # 3. EMERGENCY FALLBACK - Return hardcoded script when ALL APIs fail
    log_warning("All AI APIs failed! Using emergency fallback script...")
    return get_emergency_fallback_script()

def get_emergency_fallback_script():
    """Returns a structured horoscope fallback when all AI services are unavailable."""
    import datetime, random
    today = datetime.date.today().strftime("%B %d, %Y")
    
    # Rotate through different fallback scripts to avoid repetition
    scripts = [
        {
            "script_text": f"Stop scrolling! Mercury is making a powerful trine to Jupiter right now, and this is huge for you. Your 10th House of Career is lit up — expect a sudden opportunity from someone in authority. A boss, a mentor, or even a stranger could open a door you didn't know existed. In love, Venus is gliding through your 5th House, making you absolutely magnetic today. If you're single, pay attention to who shows up. If you're taken, tonight is the night for a deep conversation. One warning — avoid signing contracts before Thursday. Mercury's energy is expansive but not detail-oriented right now. Your ruling planet is working overtime for you. Follow for tomorrow's reading and don't miss what's coming this week!",
            "title": f"Daily Cosmic Forecast {today}",
            "youtube_title": "The Stars Are Sending You an Urgent Sign",
            "youtube_description": f"Mercury trine Jupiter is activating your Career house TODAY ({today}). A major opportunity is heading your way — but there's one thing you need to avoid. Comment your sign!",
            "youtube_tags": ["horoscope", "astrology", "zodiac", "daily horoscope", "mercury trine jupiter", "career horoscope", "love horoscope", "horoscope today", "zodiac signs", "spiritual guidance", "manifestation", "cosmic energy", "astrology shorts", "zodiac shorts", "planetary transit", "spiritual awakening", "energy shift", "zodiac prediction", "venus 5th house", "astrology reading"],
            "lucky_numbers": ["7", "11", "22"],
            "lucky_color": "Celestial Gold",
            "monthly_vibe": "Unexpected Opportunity"
        },
        {
            "script_text": f"Wait — before you scroll past this, the Moon is forming an exact opposition to Pluto today, and you need to hear this. Deep emotions are rising to the surface. Your 4th House of Home and Family is activated, which means unresolved tensions could explode — or finally heal. In your career, Mars in your 6th House is pushing you to work harder than ever. Channel that fire into one specific goal today, not ten. Love is intense right now. Venus square Neptune is creating illusions — don't believe everything you see in a new connection. Trust actions over words. The gift today is emotional clarity if you're brave enough to look within. Your power move is honesty. Subscribe so you catch tomorrow's cosmic download!",
            "title": f"Daily Cosmic Forecast {today}",
            "youtube_title": "Something Deep Is Stirring In Your Chart",
            "youtube_description": f"Moon opposite Pluto is bringing buried emotions to the surface ({today}). Your family sector is activated and love is NOT what it seems. Comment your sign!",
            "youtube_tags": ["horoscope", "astrology", "zodiac", "daily horoscope", "moon opposite pluto", "emotional healing", "love horoscope", "horoscope today", "zodiac signs", "spiritual guidance", "manifestation", "cosmic energy", "astrology shorts", "zodiac shorts", "planetary transit", "venus square neptune", "mars 6th house", "zodiac prediction", "deep astrology", "astrology reading"],
            "lucky_numbers": ["3", "16", "33"],
            "lucky_color": "Deep Violet",
            "monthly_vibe": "Emotional Breakthrough"
        }
    ]
    return random.choice(scripts)
