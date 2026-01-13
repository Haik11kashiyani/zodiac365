import os
import requests
import json
import random
import time

# --- CONFIG ---
CACHE_DIR = "assets/stock_videos"
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

# Hardcoded fallback videos if API fails (using reliable public URLs or placeholder logic)
# Ideally user provides API Key.
FALLBACK_MAP = {
    "Fire": ["assets/stock_videos/fallback_fire.mp4"],
    "Water": ["assets/stock_videos/fallback_water.mp4"],
    "Air": ["assets/stock_videos/fallback_air.mp4"],
    "Earth": ["assets/stock_videos/fallback_earth.mp4"]
}

def ensure_cache_dir(theme):
    path = os.path.join(CACHE_DIR, theme)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def search_pexel_video(query, per_page=5):
    if not PEXELS_API_KEY:
        print("⚠️ No PEXELS_API_KEY found. Cannot search stock videos.")
        return []
    
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&orientation=portrait&size=medium"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            videos = []
            for v in data.get('videos', []):
                # Get best vertical file
                files = v.get('video_files', [])
                # Filter for HD vertical files. 
                # Pexels 'link' is usually the page, we need 'video_files'.
                # Sort by width/height. We want 1080x1920 roughly.
                best_file = None
                for vf in files:
                    if vf.get('width', 0) < vf.get('height', 0) and vf.get('width') >= 720:
                        best_file = vf.get('link')
                        break
                
                if best_file:
                    videos.append({
                        "id": v['id'],
                        "url": best_file,
                        "image": v['image'] 
                    })
            return videos
    except Exception as e:
        print(f"❌ Pexels Search Failed: {e}")
    return []

def download_video(url, save_path):
    if os.path.exists(save_path) and os.path.getsize(save_path) > 100000:
        return True # Already exists
    
    try:
        print(f"⬇️ Downloading Stock Video: {os.path.basename(save_path)}...")
        r = requests.get(url, stream=True, timeout=60)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
            return True
    except Exception as e:
        print(f"❌ Download Failed: {e}")
    return False

def get_video_background(script_text, sign, theme=None):
    """
    Returns a path to a valid MP4 file.
    1. Checks cache for Theme (Money/Love).
    2. If missing, searches Pexels.
    3. If Pexels fails, searches Element (Fire/Water).
    4. Downloads and returns path.
    5. Returns None if absolute failure (caller handles fallback).
    """
    
    # 1. Determine Search Query
    query = f"{sign} zodiac aesthetic"
    category = "General"
    
    if theme:
        category = theme
        if theme == 'Love': query = "romantic hearts abstract vertical"
        elif theme == 'Career': query = "luxury gold coins vertical"
        elif theme == 'Health': query = "peaceful nature vertical"
        elif theme == 'Travel': query = "travel adventure vertical"
    
    # Or Element Based
    element_map = {
        "Aries":"Fire", "Leo":"Fire", "Sagittarius":"Fire",
        "Taurus":"Nature", "Virgo":"Nature", "Capricorn":"Nature",
        "Gemini":"Clouds", "Libra":"Clouds", "Aquarius":"Galaxy",
        "Cancer":"Ocean", "Scorpio":"Dark Water", "Pisces":"Ocean"
    }
    
    # If no specific theme, use Element
    if not theme and sign in element_map:
        base = element_map[sign]
        query = f"{base} aesthetic vertical wallpaper"
        category = base

    # 2. Check Cache
    save_dir = ensure_cache_dir(category)
    cached_files = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.endswith('.mp4')]
    
    # If we have cached videos, 80% chance to reuse one (Save API)
    if cached_files and random.random() > 0.2:
        return random.choice(cached_files)

    # 3. Search & Download (if no cache or random refresh)
    hits = search_pexel_video(query, per_page=3)
    
    if hits:
        # Pick one random hit
        hit = random.choice(hits)
        fname = f"v_{hit['id']}.mp4"
        save_path = os.path.join(save_dir, fname)
        
        if download_video(hit['url'], save_path):
            return save_path
            
    # 4. Fallback search (General Galaxy) logic could go here
    # If search failed (no key), return a random cached file if any exist
    if cached_files:
        return random.choice(cached_files)

    return None

def get_b_roll_sequence(script_text, sign, count=3):
    """
    Returns a LIST of video paths for dynamic scene changing.
    Analyses script for multiple keywords if possible.
    """
    videos = []
    
    # 1. Determine Categories based on script analysis
    categories = []
    script_lower = script_text.lower()
    
    if any(w in script_lower for w in ['love', 'romance', 'partner', 'heart']): categories.append("Love")
    if any(w in script_lower for w in ['money', 'wealth', 'career', 'job']): categories.append("Career")
    if any(w in script_lower for w in ['health', 'healing', 'energy']): categories.append("Health")
    if any(w in script_lower for w in ['travel', 'trip', 'adventure']): categories.append("Travel")
    
    # Fill remaining slots with Element or General Zodiac
    element_map = {
        "Aries":"Fire", "Leo":"Fire", "Sagittarius":"Fire",
        "Taurus":"Nature", "Virgo":"Nature", "Capricorn":"Nature",
        "Gemini":"Clouds", "Libra":"Clouds", "Aquarius":"Galaxy",
        "Cancer":"Ocean", "Scorpio":"Dark Water", "Pisces":"Ocean"
    }
    
    base_element = element_map.get(sign, "Galaxy")
    
    # Construct sequence strategy
    # If we have a theme, maybe: [Theme, Element, Theme] or [Element, Theme, Element]
    # Let's try to get unique videos.
    
    target_queries = []
    
    # Scene 1: Hook (Element or Abstract)
    target_queries.append(f"{base_element} aesthetic vertical")
    
    # Scene 2: Theme Main (if exists)
    if categories:
        cat = categories[0]
        if cat == 'Love': target_queries.append("romantic vertical")
        elif cat == 'Career': target_queries.append("luxury gold vertical")
        elif cat == 'Health': target_queries.append("peaceful nature vertical")
        elif cat == 'Travel': target_queries.append("travel adventure vertical")
    else:
        target_queries.append(f"{sign} zodiac vertical")
        
    # Scene 3: Element Variation or Second Theme
    if len(categories) > 1:
        cat = categories[1]
        target_queries.append(f"{cat} aesthetic vertical")
    else:
        target_queries.append(f"mystical {base_element} vertical")
        
    # Ensure we have enough queries
    while len(target_queries) < count:
        target_queries.append(f"abstract particle vertical")

    # Fetch
    used_ids = set()
    for q in target_queries[:count]:
        hits = search_pexel_video(q, per_page=5)
        found = False
        for hit in hits:
            if hit['id'] not in used_ids:
                fname = f"v_{hit['id']}.mp4"
                # Save dir based on query/category approximation or just 'mixed'
                # Simplest is to just use 'b_roll_cache'
                save_dir = ensure_cache_dir("mixed_b_roll")
                save_path = os.path.join(save_dir, fname)
                
                if download_video(hit['url'], save_path):
                    videos.append(save_path)
                    used_ids.add(hit['id'])
                    found = True
                    break
        
        if not found:
            # Fallback to local element cache if search fails
            # (Reusing get_video_background logic internally or simplifying)
            fallback = get_video_background(script_text, sign) # This tries cache
            if fallback and fallback not in videos:
                videos.append(fallback)
    
    # If we still don't have enough, pad with duplicates (better than crash) or single video
    if not videos:
        return None
        
    return videos
