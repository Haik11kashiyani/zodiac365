import os, requests
DIRS = ["assets/music", "assets/fonts"]
# Mystical, Dark, and Orchestral options
MUSIC_FILES = {
    "mystical_main.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Virtutes%20Instrumenti.mp3",
    "dark_ambient.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Deep%20Haze.mp3",
    "cosmic_vibe.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Gathering%20Darkness.mp3"
}
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel-Bold.ttf"

def main():
    for d in DIRS:
        if not os.path.exists(d): os.makedirs(d)
    if not os.path.exists("assets/fonts/Cinzel-Bold.ttf"):
        r = requests.get(FONT_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with open("assets/fonts/Cinzel-Bold.ttf", 'wb') as f: f.write(r.content)
    for name, url in MUSIC_FILES.items():
        path = os.path.join("assets/music", name)
        if not os.path.exists(path):
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            with open(path, 'wb') as f: f.write(r.content)
            
if __name__ == "__main__": main()
