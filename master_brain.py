import datetime, json, os, random
import generator_zodiac, generator_tarot, choreographer

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def run_empire():
    today = datetime.date.today()
    print(f"🚀 TRIGGERING ALL CHANNELS FOR ULTIMATE TEST...")

    # 1. Daily Tarot Reading
    generator_tarot.generate_reading(str(today))

    # 2. Daily Birthday Secret
    generator_zodiac.generate_zodiac_video('birthday', today.strftime("%B %d"), str(today))

    # 3. Random Compatibility Battle (Viral VS)
    s1, s2 = random.sample(SIGNS, 2)
    generator_zodiac.generate_zodiac_video('compatibility', f"{s1} vs {s2}", str(today))

    # 4. Monthly & Yearly Forecasts (Based on Current Sign)
    current_sign = SIGNS[(today.month - 1)]
    generator_zodiac.generate_zodiac_video('monthly', current_sign, today.strftime("%B %Y"))
    generator_zodiac.generate_zodiac_video('yearly', current_sign, "2026")

    # 5. THE AI WILDCARD (The AI thinks and creates its own topic)
    wildcard_topics = ["Mercury Retrograde Warning", "Full Moon Money Ritual", "Dark Side of the Zodiac", "The 13th Sign Secret"]
    generator_zodiac.generate_zodiac_video('special', random.choice(wildcard_topics), str(today))

if __name__ == "__main__":
    run_empire()
    # Step 3: Polish all plans for maximum "Human Feel"
    for f in [f for f in os.listdir('.') if f.startswith('plan_')]:
        choreographer.polish(f)
