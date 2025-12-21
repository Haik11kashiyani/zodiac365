import os, requests
DIRS = ["assets/music", "assets/fonts"]
# Mystical, Dark, and Orchestral options
MUSIC_FILES = {
    "mystical_main.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Virtutes%20Instrumenti.mp3",
    "dark_ambient.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Deep%20Haze.mp3",
    "cosmic_vibe.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Gathering%20Darkness.mp3"
}
# Fonts
FONTS = {
    "Cinzel-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel-Bold.ttf",
    "Montserrat-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf"
}

def main():
    for d in DIRS:
        if not os.path.exists(d): os.makedirs(d)
    
    # Download fonts
    for font_name, font_url in FONTS.items():
        font_path = os.path.join("assets/fonts", font_name)
        if not os.path.exists(font_path):
            print(f"📥 Downloading {font_name}...")
            r = requests.get(font_url, headers={'User-Agent': 'Mozilla/5.0'})
            with open(font_path, 'wb') as f: f.write(r.content)
    
    # Download music
    for name, url in MUSIC_FILES.items():
        path = os.path.join("assets/music", name)
        if not os.path.exists(path):
            print(f"📥 Downloading {name}...")
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            with open(path, 'wb') as f: f.write(r.content)
            
if __name__ == "__main__": main()
