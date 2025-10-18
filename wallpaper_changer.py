import os
import time
import random
import ctypes
import requests
from datetime import datetime
from plyer import notification
from PIL import Image
from io import BytesIO

# ========== CONFIG ==========
SUBREDDITS = [
    "wallpaper",
    "EarthPorn",
    "CityPorn",
    "SpacePorn",
    "MinimalWallpaper",
    "ImaginaryLandscapes"
]

MIN_WIDTH = 1920
MIN_HEIGHT = 1080
CHANGE_INTERVAL = 3600  # seconds (1 hour)
FOLDER = "wallpapers"
SEEN_FILE = "seen.txt"
SKIP_FILE = "skip.txt"
USER_AGENT = "WallpaperChanger by Aryan"

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


def fetch_reddit_images():
    subreddit = random.choice(SUBREDDITS)
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t=day&limit=50"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        posts = [
            p["data"]
            for p in data["data"]["children"]
            if not p["data"]["over_18"]
            and "url_overridden_by_dest" in p["data"]
            and p["data"]["url_overridden_by_dest"].endswith((".jpg", ".png"))
        ]
        log(f"Fetched {len(posts)} SFW wallpapers from r/{subreddit}")
        return posts
    except Exception as e:
        log(f"Error fetching from Reddit: {e}")
        return []


def is_suitable_wallpaper(url):
    """Check if image meets resolution and aspect ratio requirements."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        img = Image.open(BytesIO(response.content))
        width, height = img.size

        aspect_ratio = width / height
        screen_ratio = 16 / 9  # for pc screens

        if width < MIN_WIDTH or height < MIN_HEIGHT:
            return False
        if aspect_ratio < 1.3 or aspect_ratio > 2.0:
            return False  # filters out images with resolution of phones

        return True
    except Exception as e:
        log(f"Error checking resolution: {e}")
        return False


def download_image(url):
    os.makedirs(FOLDER, exist_ok=True)
    filename = os.path.join(FOLDER, os.path.basename(url.split("?")[0]))
    if not os.path.exists(filename):
        img = requests.get(url, timeout=15)
        with open(filename, "wb") as f:
            f.write(img.content)
    return filename


def set_wallpaper(path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(path), 3)


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


def main():
    log("Wallpaper changer started.")
    seen = get_seen()
    wallpapers = []

    while True:
        if not wallpapers:
            wallpapers = fetch_reddit_images()

        if not wallpapers:
            log("No wallpapers found. Retrying in 10 minutes...")
            time.sleep(600)
            continue

        random.shuffle(wallpapers)
        selected = None
        for post in wallpapers:
            url = post["url_overridden_by_dest"]
            if url not in seen and is_suitable_wallpaper(url):
                selected = post
                break

        if not selected:
            log("No suitable wallpapers found. Refreshing list.")
            wallpapers = fetch_reddit_images()
            continue

        url = selected["url_overridden_by_dest"]
        title = selected["title"]
        subreddit = selected["subreddit"]

        log(f"Setting wallpaper: {title} ({subreddit})")
        try:
            file_path = download_image(url)
            set_wallpaper(file_path)
            mark_seen(url)
            seen.add(url)
            notify("Wallpaper Changed!", f"{title} — from r/{subreddit}")
        except Exception as e:
            log(f"Error setting wallpaper: {e}")

        for _ in range(CHANGE_INTERVAL):
            time.sleep(1)
            if check_skip():
                log("Skipping wallpaper...")
                break


if __name__ == "__main__":
    main()
