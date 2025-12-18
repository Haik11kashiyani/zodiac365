import os, requests
DIRS = ["assets/music", "assets/fonts"]
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/cinzel/Cinzel-Bold.ttf"
MUSIC_URL = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Virtutes%20Instrumenti.mp3"
def main():
    for d in DIRS:
        if not os.path.exists(d): os.makedirs(d)
    for url, path in [(FONT_URL, "assets/fonts/Cinzel-Bold.ttf"), (MUSIC_URL, "assets/music/mystical_bg.mp3")]:
        if not os.path.exists(path):
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            with open(path, 'wb') as f: f.write(r.content)
if __name__ == "__main__": main()
