import os
import time
import random
import ctypes
import requests
from datetime import datetime
from plyer import notification
from PIL import Image
from io import BytesIO
import json

# ========== CONFIG ==========
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"[Config Error] Could not read {CONFIG_FILE}: {e}")
        return {
            "subreddits": [
                "wallpaper", "EarthPorn", "CityPorn",
                "SpacePorn", "MinimalWallpaper", "ImaginaryLandscapes"
            ],
            "min_width": 1920,
            "min_height": 1080,
            "change_interval": 3600
        }

config = load_config()

SUBREDDITS = config["subreddits"]
MIN_WIDTH = config["min_width"]
MIN_HEIGHT = config["min_height"]
CHANGE_INTERVAL = config["change_interval"]
FOLDER = "wallpapers"
SEEN_FILE = "seen.txt"
SKIP_FILE = "skip.txt"
USER_AGENT = "WallpaperChanger by Aryan"
MAX_RETRIES = 8

# =============================

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def notify(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Wallpaper Changer",
            timeout=5,
        )
    except Exception as e:
        log(f"Notification failed: {e}")

def get_local_filename(url):
    """Generates the local filename based on the URL."""
    return os.path.join(FOLDER, os.path.basename(url.split("?")[0]))

def fetch_reddit_images(subreddit, sort="top", limit=100):
    """
    Fetches images from a specific subreddit with specific sort and limit.
    Sort options: 'top', 'hot'
    """
    if sort == "top":
        url = f"https://www.reddit.com/r/{subreddit}/top.json?t=all&limit={limit}"
    else:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            log(f"Failed to fetch r/{subreddit} ({sort}): Status {response.status_code}")
            return []
            
        data = response.json()
        posts = [
            p["data"]
            for p in data["data"]["children"]
            if not p["data"]["over_18"]
            and "url_overridden_by_dest" in p["data"]
            and p["data"]["url_overridden_by_dest"].endswith((".jpg", ".png", ".jpeg"))
        ]
        return posts
    except Exception as e:
        log(f"Error fetching from r/{subreddit}: {e}")
        return []

def is_suitable_wallpaper(url):
    """Check if image meets resolution and aspect ratio requirements."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        img = Image.open(BytesIO(response.content))
        width, height = img.size

        aspect_ratio = width / height
        
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            return False
        if aspect_ratio < 1.3 or aspect_ratio > 2.5:
            return False 

        return True
    except Exception as e:
        log(f"Error checking resolution: {e}")
        return False

def download_image(url):
    os.makedirs(FOLDER, exist_ok=True)
    filename = get_local_filename(url)
    if not os.path.exists(filename):
        img = requests.get(url, timeout=15)
        with open(filename, "wb") as f:
            f.write(img.content)
    return filename

def set_wallpaper(path):
    if os.path.exists(path):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(path), 3)
    else:
        log(f"Error: Wallpaper file not found at {path}")

def get_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def mark_seen(url):
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

def check_skip():
    if os.path.exists(SKIP_FILE):
        with open(SKIP_FILE) as f:
            content = f.read().strip().lower()
        if "skip" in content:
            open(SKIP_FILE, "w").close()
            return True
    return False

def get_fallback_wallpaper(seen_set):
    """Finds a random wallpaper that was previously used and exists locally."""
    log("Trying to fallback to a previously used wallpaper...")
    seen_list = list(seen_set)
    random.shuffle(seen_list)
    
    for url in seen_list:
        local_path = get_local_filename(url)
        if os.path.exists(local_path):
            return local_path, url
    
    return None, None

def main():
    log("Wallpaper changer started.")
    seen = get_seen()

    while True:
        selected_post = None
        new_wallpaper_found = False

        # --- RETRY LOGIC (Try 8 times for a NEW wallpaper) ---
        for attempt in range(1, MAX_RETRIES + 1):
            # 3. Pick a random subreddit from list
            subreddit = random.choice(SUBREDDITS)
            
            # 1. Try Top 100
            log(f"[Attempt {attempt}/{MAX_RETRIES}] Checking r/{subreddit} (Top 100)...")
            posts = fetch_reddit_images(subreddit, sort="top", limit=100)
            
            random.shuffle(posts)

            for post in posts:
                url = post["url_overridden_by_dest"]
                if url not in seen and is_suitable_wallpaper(url):
                    selected_post = post
                    new_wallpaper_found = True
                    break
            
            if new_wallpaper_found:
                break

            # 2. If Top failed, Try Hot 5
            log(f"[Attempt {attempt}/{MAX_RETRIES}] Top failed. Checking r/{subreddit} (Hot 5)...")
            posts = fetch_reddit_images(subreddit, sort="hot", limit=5)
            
            for post in posts:
                url = post["url_overridden_by_dest"]
                if url not in seen and is_suitable_wallpaper(url):
                    selected_post = post
                    new_wallpaper_found = True
                    break
            
            if new_wallpaper_found:
                break
            
            time.sleep(2)

        # --- SETTING THE WALLPAPER ---
        
        if new_wallpaper_found and selected_post:
            # Case A: We found a fresh wallpaper from Reddit
            url = selected_post["url_overridden_by_dest"]
            title = selected_post["title"]
            sub = selected_post["subreddit"]
            
            log(f"Success! Downloading: {title}")
            try:
                file_path = download_image(url)
                set_wallpaper(file_path)
                mark_seen(url)
                seen.add(url)
                notify("New Wallpaper", f"{title} — r/{sub}")
            except Exception as e:
                log(f"Error setting new wallpaper: {e}")
                
        else:
            # Case B: We failed 8 times. Use Fallback.
            # 4. Use seen.txt wallpaper
            log("Max retries reached. Falling back to seen list.")
            fallback_path, fallback_url = get_fallback_wallpaper(seen)
            
            if fallback_path:
                log(f"Restoring old wallpaper: {fallback_path}")
                set_wallpaper(fallback_path)
                notify("Fallback Wallpaper", "Could not find new image. Restored old one.")
            else:
                log("Critical: No new wallpapers found AND no local fallback available.")

        # --- WAIT LOOP ---
        log(f"Sleeping for {CHANGE_INTERVAL} seconds...")
        for _ in range(CHANGE_INTERVAL):
            time.sleep(1)
            if check_skip():
                log("Skip command detected. Changing now...")
                break

if __name__ == "__main__":
    main()
