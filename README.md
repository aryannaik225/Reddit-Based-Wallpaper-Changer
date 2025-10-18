# 🖼️ Reddit Based Wallpaper Changer

A lightweight **Python-based dynamic wallpaper changer** that automatically fetches beautiful wallpapers from your favorite **Reddit subreddits**, filters them by resolution, and sets them as your desktop background.
It also notifies you every time your wallpaper changes — and you can even skip to the next wallpaper instantly.

---

## 🚀 Features

* 🧠 **Smart Selection** – Fetches top wallpapers from multiple subreddits.
* 🖥️ **Quality Filtering** – Automatically skips low-resolution or portrait images.
* 🕒 **Automatic Rotation** – Changes wallpaper at a user-defined interval.
* ⚡ **Skip Anytime** – Instantly skip to the next wallpaper by typing “skip” into a text file.
* 🔔 **Desktop Notifications** – Get notified when your wallpaper updates.
* 🧹 **Seen Image Tracking** – Avoids repeating wallpapers you've already used.
* 💾 **Offline Cache** – Saves wallpapers locally for reuse.
* 🧾 **Easy Configuration** – Edit settings via `config.json`, no code changes needed.

---

## 🧰 Requirements

### Python Version

* Python **3.8 or above**

### Dependencies

Install dependencies using pip:

```bash
pip install requests pillow plyer
```

---

## 📦 Installation

1. **Clone or download** this repository.
   ```bash
   git clone https://github.com/aryannaik225/Reddit-Based-Wallpaper-Changer.git
   ```

2. {Optional) **Place `wallpaper_changer.py`** in any folder you prefer (for example, `C:\Users\<YourName>\Documents\`).

3. **Move the config file** named `config.json` in the same folder (details below).

4. (Optional) **Test it manually**:
   ```bash
   python wallpaper_changer.py
   ```
   You should see console logs and a desktop notification once the wallpaper changes.

---

## ⚙️ Configuration (Using `config.json`)

All customization is handled through a simple `config.json` file located in the same directory as `wallpaper_changer.py`.

### 🧾 Example `config.json`

```json
{
  "subreddits": [
    "wallpaper",
    "EarthPorn",
    "CityPorn",
    "SpacePorn",
    "MinimalWallpaper",
    "ImaginaryLandscapes"
  ],
  "min_width": 1920,
  "min_height": 1080,
  "change_interval": 3600
}
```

### ✏️ How to Customize

* **Change Subreddits:**
  Modify the `subreddits` list to include your favorites.
  ```json
  "subreddits": ["wallpaper", "NaturePics", "Cyberpunk"]
  ```

* **Change Minimum Resolution:**
  To only allow 4K wallpapers:
  ```json
  "min_width": 3840,
  "min_height": 2160
  ```

* **Change Interval (seconds):**

  * 1800 → every 30 minutes
  * 3600 → every hour
  * 86400 → once a day

---

## 🪄 Optional: Skip Wallpaper Instantly

To skip the current wallpaper early:

1. Open the file named `skip.txt` (it will be auto-created).
2. Type:
   ```
   skip
   ```
3. Save the file — the script will detect it and instantly move to the next wallpaper.

---

## 🔄 Add to Startup (Windows)

Make the wallpaper changer **run automatically every time your PC boots up**.

### 🧱 Step 1: Create a Shortcut

1. Locate your `wallpaper_changer.py` file.
2. Right-click → **Create shortcut**.

### ⚙️ Step 2: Edit Shortcut Target

1. Right-click the shortcut → **Properties**.
2. In the **Target** field, enter:
   ```
   pythonw "C:\Path\To\wallpaper_changer.py"
   ```

   * Use **`pythonw`** (not `python`) to run it silently (no console window).
   * Adjust the path as needed.

### 🪟 Step 3: Move Shortcut to Startup Folder

1. Press **Win + R**, type:
   ```
   shell:startup
   ```
   and hit **Enter**.
2. Move your shortcut into this folder.

✅ Done! It will now run automatically when your PC starts.

---

## 🧭 Folder Structure

```
wallpaper_changer.py
config.json
│
├── wallpapers/        # Downloaded wallpapers stored here
├── seen.txt           # Tracks already-used images
└── skip.txt           # Type "skip" here to skip wallpaper
```

---

## 🧩 Example Output

```
[14:23:45] Wallpaper changer started.
[14:23:46] Fetched 48 SFW wallpapers from r/EarthPorn
[14:23:59] Setting wallpaper: Golden Sunset (EarthPorn)
[14:24:00] Wallpaper changed! Notification sent.
```

---

## 🧠 Tips

* Stop the script anytime via **Task Manager → End Python process**.
* If Reddit fails to load, it retries automatically after 10 minutes.
* The app only downloads **SFW (Safe For Work)** wallpapers.
* You can manually delete `seen.txt` if you want it to re-use old wallpapers.

---

## 🛠️ Troubleshooting

| Issue                           | Possible Fix                                                             |
| ------------------------------- | ------------------------------------------------------------------------ |
| ❌ Script doesn’t start at login | Check shortcut path & ensure `pythonw.exe` exists in your Python folder. |
| 🖼️ Wallpaper doesn’t change    | Verify that wallpapers meet your resolution filter.                      |
| ⚠️ “Notification failed”        | Reinstall `plyer` or run the script as administrator.                    |
| 🧱 Nothing happens              | Run manually with `python wallpaper_changer.py` to view logs.            |

---

## 📜 License

This project is released under the **MIT License** — you’re free to use, modify, and distribute it as long as attribution is given.

---

## ✨ Author

**Aryan Naik**
💡 “Automating beauty, one wallpaper at a time.”
🔗 [GitHub](https://github.com/aryannaik225)

---

> *“Every desktop deserves a view worth waking up to.”*

---
