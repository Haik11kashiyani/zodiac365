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

def ask_ai(prompt, sys_msg="You are a mystical video director."):
    # ...
        for model_id in models:
            try:
                log_info(f"Consulting: {model_id}...")
                # ...
                log_warning(f"{model_id} is busy. Rotating...")
            except: continue
            
    # 2. Try Google Gemini Fallback
    return ask_google_fallback(prompt, sys_msg)
