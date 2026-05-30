import os
import json
import datetime
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# YouTube API tag limits (see Video.snippet.tags in Data API v3 docs)
MAX_TAG_LENGTH = 30
# Stay under documented 500 — spaced tags cost extra (quotes + commas)
MAX_TAGS_CHAR_BUDGET = 480


def _youtube_tag_char_budget(tags):
    """Total characters YouTube counts for tags (commas + quote overhead for spaces)."""
    length = 0
    for tag in tags:
        length += len(tag) + 1  # comma separator between tags
        if ' ' in tag:
            length += 2  # API wraps spaced tags in quotes
    return length


def sanitize_youtube_tags(tags):
    """Normalize tags and trim to fit YouTube's per-tag and total character limits."""
    cleaned = []
    seen = set()

    for t in tags:
        if not t or not isinstance(t, str):
            continue
        tag = t.strip().lower().replace('#', '')
        tag = ''.join(c for c in tag if c.isalnum() or c.isspace() or c == '-')
        tag = ' '.join(tag.split())
        if not tag or len(tag) < 2:
            continue
        if len(tag) > MAX_TAG_LENGTH:
            tag = tag[:MAX_TAG_LENGTH].rstrip()
        if tag in seen:
            continue
        seen.add(tag)
        cleaned.append(tag)

    result = []
    for tag in cleaned:
        candidate = result + [tag]
        if _youtube_tag_char_budget(candidate) <= MAX_TAGS_CHAR_BUDGET:
            result.append(tag)
        else:
            break

    if len(result) < len(cleaned):
        dropped = len(cleaned) - len(result)
        print(f"[Tags] Trimmed {dropped} tag(s) to stay within {MAX_TAGS_CHAR_BUDGET} char budget "
              f"(budget={_youtube_tag_char_budget(result)})")

    return result


def get_authenticated_service():
    """
    Authenticate with YouTube API using token.json or environment variables.
    Supports automatic token refresh using CLIENT_ID and CLIENT_SECRET.
    """
    token_file = os.path.join(os.path.dirname(__file__), 'token.json')
    print(f"🔍 [Upload Debug] Looking for token at: {token_file}")
    
    # Get client credentials from environment (for token refresh)
    client_id = os.environ.get('YOUTUBE_CLIENT_ID')
    client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
    
    if not os.path.exists(token_file):
        print("⚠️ [Upload Debug] No token.json found. Cannot upload to YouTube.")
        return None

    try:
        if os.path.getsize(token_file) == 0:
             print("❌ [Upload Debug] token.json is empty!")
             return None

        with open(token_file, 'r') as f:
            token_content = f.read().strip()
            # Clean up accidental prefixes (like typing a '1' before pasting the JSON in GitHub UI)
            if token_content and not token_content.startswith('{'):
                start_idx = token_content.find('{')
                if start_idx != -1:
                    print(f"🔧 [Upload Debug] Stripped invalid prefix from token (found {{ at index {start_idx})")
                    token_content = token_content[start_idx:]
            
            token_data = json.loads(token_content)
            print(f"✅ [Upload Debug] Token loaded. Keys present: {list(token_data.keys())}")
        
        # Add client_id and client_secret if not in token (needed for refresh)
        if client_id and 'client_id' not in token_data:
            token_data['client_id'] = client_id
        if client_secret and 'client_secret' not in token_data:
            token_data['client_secret'] = client_secret
            
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        
        # Check if token is expired and refresh if possible
        if creds and creds.expired and creds.refresh_token:
            print("🔄 [Upload Debug] Token expired, attempting refresh...")
            try:
                creds.refresh(Request())
                print("✅ [Upload Debug] Token refreshed successfully!")
                
                # Save refreshed token back to file
                with open(token_file, 'w') as f:
                    json.dump({
                        'token': creds.token,
                        'refresh_token': creds.refresh_token,
                        'token_uri': creds.token_uri,
                        'client_id': creds.client_id,
                        'client_secret': creds.client_secret,
                        'scopes': list(creds.scopes)
                    }, f)
            except Exception as refresh_error:
                print(f"⚠️ [Upload Debug] Token refresh failed: {refresh_error}")
        
        return googleapiclient.discovery.build('youtube', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Error loading YouTube token: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_metadata(data):
    """Generate Viral Title, Description, Tags optimized for YouTube Shorts algorithm."""
    
    # 1. Prefer AI-Generated Metadata if available
    ai_title = data.get('youtube_title')
    ai_desc = data.get('youtube_description')
    ai_tags = data.get('youtube_tags') or data.get('tags')
    
    target = data.get('target', 'Zodiac')
    mode = data.get('type', 'daily')
    date_str = data.get('date', 'Today')
    emoji = get_emoji(target)
    current_year = datetime.datetime.now().year
    
    # --- TITLE STRATEGY ---
    # YouTube Shorts: Keep under 70 chars, #Shorts MUST be exact casing
    # Format: Emoji + Hook + Sign + #Shorts
    if ai_title:
        # Strip any existing hashtags from AI title, we'll add our own
        clean_ai = ai_title.replace('#shorts', '').replace('#Shorts', '').replace('#viral', '').replace('#SHORTS', '').strip()
        # Ensure it's punchy and short
        if len(clean_ai) > 55:
            clean_ai = clean_ai[:54].strip() + '…'
        final_title = f"{clean_ai} #Shorts"
    else:
        # Fallback Dynamic Templates — short, punchy, curiosity-driven
        if mode == 'daily':
            hooks = [
                f"{emoji} {target} — The Stars Are WARNING You Today",
                f"{emoji} {target} — Don't Ignore This Sign",
                f"{emoji} {target} — Today Changes Everything",
                f"{emoji} {target} — Urgent Cosmic Message",
            ]
            import hashlib
            idx = int(hashlib.md5(f"{target}{date_str}".encode()).hexdigest(), 16) % len(hooks)
            final_title = f"{hooks[idx]} #Shorts"
        elif mode == 'weekly':
            final_title = f"{emoji} {target} Weekly — This Week Is Critical #Shorts"
        elif mode == 'monthly':
            final_title = f"{emoji} {target} {date_str} — Month of Destiny #Shorts"
        elif mode == 'yearly':
            final_title = f"{emoji} {target} {current_year} — Your Year Revealed #Shorts"
        elif mode == 'compatibility':
            final_title = f"{emoji} {target} — Who Wins in Love? #Shorts"
        else:
            final_title = f"{emoji} {data.get('title', 'Cosmic Message')} #Shorts"

    # Hard limit: YouTube title max 100 chars
    if len(final_title) > 100:
        suffix = " #Shorts"
        limit = 100 - len(suffix)
        final_title = final_title[:limit-1].rstrip() + "…" + suffix

    # --- DESCRIPTION STRATEGY ---
    # YouTube Shorts: First 2 lines visible in feed. Hook HARD.
    # Only 3 hashtags at bottom (YouTube surfaces first 3 above the title)
    if ai_desc:
        description_body = ai_desc.strip()
    else:
        description_body = f"The cosmos has an urgent message for {target} today. This is the sign you've been waiting for."

    # Pick the 3 best hashtags — YouTube shows exactly 3 above the title
    primary_hashtags = f"#{target.lower()} #astrology #horoscope"

    # Zodiac sign finding instructions
    zodiac_finder = (
        "\n---\n"
        "🌟 Find Your Zodiac Sign & Prediction Below! 🌟\n"
        "Just scroll down to the section with your sign name in ALL CAPS (e.g. ARIES, TAURUS, etc). Each section is clearly labeled so you can quickly find your personalized prediction!\n"
        "If you don't know your sign, search for your birthday here: https://www.astrology-zodiac-signs.com/\n"
        "---\n"
    )

    # All zodiac sign sections (for SEO and user navigation)
    all_signs_section = (
        "\nZODIAC SIGNS INDEX:\n"
        "ARIES | TAURUS | GEMINI | CANCER | LEO | VIRGO | LIBRA | SCORPIO | SAGITTARIUS | CAPRICORN | AQUARIUS | PISCES\n"
        "---\n"
    )

    # Viral/clickbait tags (for SEO, appended after zodiac section)
    viral_tags = "#viral #trending #fyp #explore #shorts #astrologytiktok #zodiacsigns #manifestation #spiritual #cosmicenergy #horoscopetoday #astrologyshorts #zodiacshorts #destiny #future #prediction #luck #love #success #universe #energy #spiritualawakening"

    description = f"""{description_body}

🔮 Sign: {target} | 📅 {date_str}

👇 Subscribe for your DAILY cosmic guidance:
https://www.youtube.com/@Zodiac365?sub_confirmation=1

💬 Drop your sign in the comments!
❤️ Like if this resonated with you.

{zodiac_finder}{all_signs_section}{viral_tags}\n\n{primary_hashtags}"""

    # --- TAGS STRATEGY ---
    # YouTube tags (hidden metadata) — mix broad + niche + trending
    final_tags = []
    
    # Must-have discovery tags (short tags to preserve character budget)
    mode_label = mode if mode in ('daily', 'weekly', 'monthly', 'yearly') else 'daily'
    base_tags = [
        "shorts", "astrology", "horoscope", "zodiac",
        target.lower(), f"{target.lower()} horoscope",
        f"{mode_label} horoscope", "zodiac signs",
    ]
    final_tags.extend(base_tags)
    
    # AI-generated tags (high relevance) — added before niche so niche fills remaining budget
    if ai_tags and isinstance(ai_tags, list):
        for t in ai_tags:
            if isinstance(t, str) and t.strip():
                final_tags.append(t)

    # Trending niche tags for reach (shorter tags first to maximize count within budget)
    niche_tags = [
        f"{target.lower()} {current_year}",
        f"{mode} horoscope",
        f"{target.lower()} today",
        "horoscope today",
        "astrology shorts",
        "zodiac shorts",
        "manifestation",
        "cosmic energy",
    ]
    for t in niche_tags:
        final_tags.append(t)

    tags = sanitize_youtube_tags(final_tags)

    return final_title, description, tags

def get_emoji(sign):
    emojis = {
        "Aries":"♈","Taurus":"♉","Gemini":"♊","Cancer":"♋","Leo":"♌","Virgo":"♍",
        "Libra":"♎","Scorpio":"♏","Sagittarius":"♐","Capricorn":"♑","Aquarius":"♒","Pisces":"♓"
    }
    # Simple check if sign name is in target string
    for k,v in emojis.items():
        if k in sign: return v
    return "🔮"

def build_safe_fallback_tags(target, mode='daily'):
    """Minimal tags guaranteed to fit YouTube API limits."""
    sign = target.lower().split(' vs ')[0].strip()
    return sanitize_youtube_tags([
        'shorts', 'astrology', 'horoscope', 'zodiac', sign,
        f'{sign} horoscope', f'{mode} horoscope',
    ])


def upload_video(file_path, data):
    youtube = get_authenticated_service()
    if not youtube:
        return False

    title, description, tags = generate_metadata(data)
    target = data.get('target', 'zodiac')
    mode = data.get('type', 'daily')
    tag_sets = [tags, build_safe_fallback_tags(target, mode)]

    print(f"📺 Uploading to YouTube: {title}")

    for attempt, tag_list in enumerate(tag_sets):
        tag_budget = _youtube_tag_char_budget(tag_list)
        label = 'primary' if attempt == 0 else 'fallback'
        print(f"[Tags] {label}: {len(tag_list)} tags, budget={tag_budget}/{MAX_TAGS_CHAR_BUDGET}")

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tag_list,
                'categoryId': '24',
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False,
            },
        }

        try:
            media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media,
            )
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"   Uploaded {int(status.progress() * 100)}%")

            print(f"✅ Upload Complete! Video ID: {response.get('id')}")
            return True
        except googleapiclient.errors.HttpError as e:
            if attempt == 0 and 'invalidTags' in str(e):
                print("[Tags] invalidTags from YouTube — retrying with safe fallback tags...")
                continue
            print(f"❌ Upload Failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Upload Failed: {e}")
            return False

    return False
