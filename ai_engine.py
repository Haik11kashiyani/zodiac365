from cli_utils import log_info, log_error, log_warning

# ...

            log_info(f"Oracle discovered {len(free_list)} active free models.")
            return free_list
    except Exception as e:
        log_warning(f"Research failed: {e}. Using fallback list.")
    
    # ...

    log_info("Switching to Gemini Fallback...")
    # ...
    except Exception as e:
        log_error(f"Gemini Fallback Failed: {e}")
    return None

from cli_utils import log_info, log_error, log_warning, wait_random
import os, json, requests, time, re

# ...

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
