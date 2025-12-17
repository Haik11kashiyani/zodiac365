import json
import os
import sys
from ai_engine import ask_ai

def polish_script(plan_file):
    print(f"🧐 Choreographer is reviewing: {plan_file}")
    
    # 1. READ THE DRAFT
    with open(plan_file, 'r', encoding='utf-8') as f:
        draft = json.load(f)

    # 2. THE DIRECTOR'S PROMPT
    # We ask the AI to act like a Video Editor/Director
    prompt = f"""
    You are a Master Viral Video Choreographer for YouTube Shorts.
    I have a draft script for a Tarot reading video. It is too boring.
    
    YOUR JOB: Reword the script to make it 'Dark, Mystical, and High-Retention'.
    
    CURRENT DRAFT:
    Title: {draft['title']}
    Script: {draft['script_text']}
    Cards: {draft['card_names']}
    
    INSTRUCTIONS:
    1. HOOK (0-3s): Rewrite the first sentence to be a "Scroll Stopper". (e.g., "Do NOT scroll past this...", "Your enemies are watching...")
    2. PACING: Remove fluff words. Make it sound punchy like a TikTok narration.
    3. TONE: The tone must be 'Urgent' and '8th House Scorpionic'.
    4. TITLE: Write a new Clickbait Title (Max 6 words, UPPERCASE).
    
    OUTPUT FORMAT (Strict JSON):
    {{
        "title": "NEW VIRAL TITLE",
        "script_text": "New viral script text...",
        "visual_notes": "Specific mood instructions"
    }}
    """
    
    print("🎬 Polishing script with AI Director...")
    polished_data = ask_ai(prompt, system_instruction="You are a Viral Content Editor. You hate boring content.")
    
    if polished_data:
        # 3. MERGE & UPDATE
        # We keep the technical file names (cards/audio) but update the creative text
        draft['title'] = polished_data['title']
        draft['script_text'] = polished_data['script_text']
        draft['choreography_notes'] = polished_data.get('visual_notes', '')
        
        # Save it back to the same file (Overwrite with better version)
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(draft, f, indent=4)
            
        print(f"✨ Script Polished! New Title: {draft['title']}")
    else:
        print("⚠️ Choreographer failed. Using original draft.")

if __name__ == "__main__":
    # Find the newest plan file
    files = [f for f in os.listdir('.') if f.startswith('plan_tarot') and f.endswith('.json')]
    if files:
        latest = max(files, key=os.path.getctime)
        polish_script(latest)
    else:
        print("❌ No plan to polish.")
