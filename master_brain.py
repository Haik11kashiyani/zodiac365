import datetime, random, generator_zodiac, generator_tarot

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def run_empire():
    today = datetime.date.today()
    print(f"🚀 GENERATING GOD-MODE SAMPLER PACK...")

    # 1. Tarot
    generator_tarot.generate_reading(str(today))
    # 2. Birthday
    generator_zodiac.generate_zodiac_video('birthday', today.strftime("%B %d"), str(today))
    # 3. Compatibility
    s1, s2 = random.sample(SIGNS, 2)
    generator_zodiac.generate_zodiac_video('compatibility', f"{s1} vs {s2}", str(today))
    # 4. Monthly/Yearly
    target = SIGNS[today.month - 1]
    generator_zodiac.generate_zodiac_video('monthly', target, today.strftime("%B %Y"))
    generator_zodiac.generate_zodiac_video('yearly', target, "2026")
    # 5. Wildcard AI Insight
    topics = ["Mercury Retrograde Warning", "Full Moon Money Ritual", "Dark Secrets"]
    generator_zodiac.generate_zodiac_video('special', random.choice(topics), str(today))

if __name__ == "__main__": run_empire()
