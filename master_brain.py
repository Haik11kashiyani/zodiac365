import datetime, random, generator_zodiac, generator_tarot, json, os, glob

with open("config.json", "r") as f:
    CONFIG = json.load(f)

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def run_empire():
    today = datetime.date.today()
    print(f"🚀 GENERATING EMPIRE CONTENT FOR {today}...")

    # 1. Daily Videos (ALWAYS 12)
    print("--- 🌞 GENERATING DAILY VIDEOS ---")
    for sign in SIGNS:
        generator_zodiac.generate_zodiac_video('daily', sign, today.strftime("%B %d, %Y"))

    # 2. Wildcard Special (ALWAYS 1)
    print("--- 🃏 GENERATING WILDCARD VIDEO ---")
    if random.choice([True, False]):
        # VS Battle
        s1, s2 = random.sample(SIGNS, 2)
        generator_zodiac.generate_zodiac_video('compatibility', f"{s1} vs {s2}", str(today))
    else:
        # Birthday or Topic
        topics = ["Mercury Retrograde", "Full Moon Ritual", "Lucky Numbers", "Spirit Animals"]
        generator_zodiac.generate_zodiac_video('special', random.choice(topics), str(today))

    # 3. Monthly & Yearly Staggered Release (Days 1-12)
    day_of_month = today.day
    if 1 <= day_of_month <= 12:
        target_sign = SIGNS[day_of_month - 1] # Day 1 = Aries (0), Day 12 = Pisces (11)
        
        print(f"--- 📅 GENERATING MONTHLY CONTENT FOR {target_sign.upper()} ---")
        # Monthly Video
        generator_zodiac.generate_zodiac_video('monthly', target_sign, today.strftime("%B %Y"))
        
        # Yearly Video (Only in January)
        if today.month == 1:
            print(f"--- 🎆 GENERATING YEARLY CONTENT FOR {target_sign.upper()} ---")
            generator_zodiac.generate_zodiac_video('yearly', target_sign, "2026")

if __name__ == "__main__": run_empire()
