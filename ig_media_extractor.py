#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import platform

def _bootstrap_env():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(base_dir, "venv")
    
    if os.name == 'nt':
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        
    if sys.executable == venv_python or sys.prefix == venv_dir:
        return

    print("--- Instagram Media Extractor Setup ---")
    if not os.path.exists(venv_python):
        print("Creating virtual environment (venv) for isolation...")
        import venv
        venv.create(venv_dir, with_pip=True)
        
        print("Installing dependencies...")
        req_file = os.path.join(base_dir, "requirements.txt")
        if os.path.exists(req_file):
            subprocess.check_call([venv_python, "-m", "pip", "install", "-r", req_file, "--quiet"])
        else:
            subprocess.check_call([venv_python, "-m", "pip", "install", "requests", "selenium", "yt-dlp", "--quiet"])
        
        print("Environment ready! Starting extractor...\n")
    
    sys.exit(subprocess.call([venv_python] + sys.argv))

_bootstrap_env()

import argparse
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import shutil
import re
import datetime
import requests
import yt_dlp

CONFIG_FILE = "config.json"

def get_default_downloads_folder():
    if "com.termux" in os.environ.get("PREFIX", ""):
        return os.path.join(os.path.expanduser("~"), "storage", "downloads", "ig_media")
    elif platform.system() == "Windows":
        return os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Downloads", "ig_media")
    else:
        return os.path.join(os.path.expanduser("~"), "Downloads", "ig_media")

def load_config():
    default_config = {"download_directory": get_default_downloads_folder()}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except Exception:
            pass
    return default_config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def reorganize_downloads(target_dir, date_folder_name):
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for file in files:
            parent_dir = os.path.basename(root)
            if parent_dir in ['image', 'video', 'dp', 'metadata', 'other']:
                continue
            
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if 'profile_pic' in file:
                media_type = 'dp'
            elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                media_type = 'image'
            elif ext in ['.mp4', '.mov']:
                media_type = 'video'
            elif ext in ['.txt', '.json', '.xz']:
                media_type = 'metadata'
            else:
                media_type = 'other'
                
            dest_dir = os.path.join(root, date_folder_name, media_type)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(file_path, os.path.join(dest_dir, file))

def login():
    print("Launching browser for login...")
    print("Please log in to your Instagram account in the opened browser window.")
    print("Once you are fully logged in and can see your feed, return to this terminal and press Enter.")
    
    try:
        options = Options()
        options.add_argument("--window-size=1200,800")
        options.add_argument("--disable-notifications")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.instagram.com/accounts/login/")
        
        input("\n[Press Enter here once you are logged in...]")
        
        user_agent = driver.execute_script("return navigator.userAgent;")
        with open("ig_user_agent.txt", "w") as f:
            f.write(user_agent)
            
        cookies = driver.get_cookies()
        if cookies:
            with open("ig_cookies.json", "w") as f:
                json.dump(cookies, f, indent=4)
            print("Login successful! Cookies and User-Agent saved.")
        else:
            print("No cookies found. Login might have failed.")
            
        driver.quit()
    except Exception as e:
        print(f"Browser login failed: {e}")

def get_authenticated_driver():
    options = Options()
    options.add_argument("--headless") # Run headless for downloading
    options.add_argument("--window-size=1200,800")
    options.add_argument("--disable-notifications")
    
    if os.path.exists("ig_user_agent.txt"):
        with open("ig_user_agent.txt", "r") as f:
            options.add_argument(f"user-agent={f.read().strip()}")
            
    service = None
    if "com.termux" in os.environ.get("PREFIX", ""):
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        from selenium.webdriver.chrome.service import Service
        termux_bin = "/data/data/com.termux/files/usr/bin"
        if os.path.exists(f"{termux_bin}/chromium-browser"):
            options.binary_location = f"{termux_bin}/chromium-browser"
        elif os.path.exists(f"{termux_bin}/chromium"):
            options.binary_location = f"{termux_bin}/chromium"
            
        if os.path.exists(f"{termux_bin}/chromedriver"):
            service = Service(f"{termux_bin}/chromedriver")
            
    try:
        if service:
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"\n[!] Error launching Chrome: {e}")
        print("Please ensure you have Google Chrome installed on your system.")
        print("If you are using Termux (Android), running full Selenium requires a proot environment or termux-x11.")
        print("Run: pkg install x11-repo && pkg install chromium")
        sys.exit(1)
    
    # Must visit domain before injecting cookies
    driver.get("https://www.instagram.com/favicon.ico")
    
    if os.path.exists("ig_cookies.json"):
        with open("ig_cookies.json", "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                # Selenium requires strict domain matching
                if 'instagram.com' in cookie.get('domain', ''):
                    # fix strictness issues
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
    return driver

def convert_cookies_for_ytdlp():
    # yt-dlp doesn't natively parse our JSON. Let's write them to a netscape cookie file temporarily
    if not os.path.exists("ig_cookies.json"):
        return None
        
    netscape_file = "ig_cookies.txt"
    with open("ig_cookies.json", "r") as f:
        cookies = json.load(f)
        
    with open(netscape_file, "w") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for c in cookies:
            domain = c.get('domain', '')
            if not domain.startswith('.'):
                domain = '.' + domain
            flag = "TRUE" if domain.startswith('.') else "FALSE"
            path = c.get('path', '/')
            secure = "TRUE" if c.get('secure', False) else "FALSE"
            expiry = str(int(c.get('expiry', time.time() + 31536000)))
            name = c.get('name', '')
            value = c.get('value', '')
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")
            
    return netscape_file

def download_image(url, output_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

def extract_post_media(driver, url, target_dir, shortcode):
    print(f"Scraping post: {url}")
    driver.get(url)
    time.sleep(3) # wait for load
    
    # Check for video via yt-dlp first
    cookie_file = convert_cookies_for_ytdlp()
    class SilentLogger(object):
        def debug(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass

    ydl_opts = {
        'outtmpl': os.path.join(target_dir, f'{shortcode}_%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'logger': SilentLogger(),
    }
    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file
        
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info and info.get('ext') in ['mp4', 'webm', 'm4a', 'none']:
                print("Found video/audio stream, downloading...")
                ydl.download([url])
    except Exception as e:
        pass # yt-dlp failed or not a video

    # Always scrape images (handles mixed carousels and photo highlights where yt-dlp only grabbed videos)

    # Scrape images
    img_urls = set()
    
    def extract_current_images():
        imgs = driver.find_elements(By.TAG_NAME, 'img')
        for img in imgs:
            src = img.get_attribute('src')
            if not src:
                continue
                
            # Ignore explicit profile pictures and tiny resolutions (avatars)
            if 'profile_pic' in src:
                continue
                
            is_small_avatar = any(sz in src for sz in ['s150x150', 's200x200', 's206x206', 's320x320', 's480x480'])
            if is_small_avatar:
                continue
                
            # Main images usually contain stp= or are standard .jpg/.webp
            if 'stp=' in src or '.jpg' in src or '.webp' in src:
                img_urls.add(src)

    # Initial extraction
    extract_current_images()
    
    # Click Next button for carousels to load remaining images into DOM
    while True:
        try:
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
            except:
                next_btn = driver.find_element(By.CSS_SELECTOR, "button._afxw")
            next_btn.click()
            time.sleep(1)
            extract_current_images()
        except:
            break
                
    if img_urls:
        img_urls_list = list(img_urls)
        print(f"Found {len(img_urls_list)} unique high-res image(s), downloading...")
        for i, img_url in enumerate(img_urls_list):
            output_path = os.path.join(target_dir, f"{shortcode}_{i}.jpg")
            download_image(img_url, output_path)
    else:
        print("No high-res media found for this post.")

def download_post(url, config):
    try:
        path = urlparse(url).path
        parts = [p for p in path.split('/') if p]
        shortcode = parts[1] if len(parts) > 1 else "unknown"
    except:
        print("Invalid URL")
        return
        
    current_time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_dir = os.path.join(config["download_directory"], "single_posts")
    os.makedirs(target_dir, exist_ok=True)
    
    driver = get_authenticated_driver()
    try:
        extract_post_media(driver, url, target_dir, shortcode)
        reorganize_downloads(target_dir, current_time_str)
        print("Download complete and organized.")
    finally:
        driver.quit()

stop_scrolling = False

def check_for_stop():
    global stop_scrolling
    try:
        input()
        input()
        stop_scrolling = True
    except:
        pass

def download_profile(username, config):
    global stop_scrolling
    current_time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_dir = os.path.join(config["download_directory"], username)
    os.makedirs(target_dir, exist_ok=True)
    
    driver = get_authenticated_driver()
    try:
        print(f"Loading profile {username}...")
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(4)
        
        # Download Profile Pic
        try:
            imgs = driver.find_elements(By.TAG_NAME, 'img')
            for img in imgs:
                src = img.get_attribute('src')
                alt = img.get_attribute('alt') or ''
                if src and (f"{username.lower()}'s profile picture" in alt.lower() or 'profile_pic' in src):
                    download_image(src, os.path.join(target_dir, f"profile_pic.jpg"))
                    print("Downloaded profile picture.")
                    break
        except:
            pass

        print("Scrolling profile to collect posts (this bypasses 429 API blocks!)...")
        print("\n*** PRESS [ENTER] TWICE TO STOP SCROLLING EARLY AND BEGIN DOWNLOADING ***\n")
        
        stop_scrolling = False
        import threading
        t = threading.Thread(target=check_for_stop, daemon=True)
        t.start()
        
        post_urls = set()
        no_new_posts = 0
        while not stop_scrolling:
            links = driver.find_elements(By.TAG_NAME, 'a')
            current_count = len(post_urls)
            for link in links:
                href = link.get_attribute('href')
                if href and ('/p/' in href or '/reel/' in href):
                    post_urls.add(href.split('?')[0])
                    
            print(f"Collected {len(post_urls)} posts so far...")
            if len(post_urls) == current_count:
                no_new_posts += 1
            else:
                no_new_posts = 0
                
            if no_new_posts >= 3:
                print("Finished scrolling profile (no new posts found).")
                break
                
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
        if stop_scrolling:
            print(f"\nScrolling manually stopped by user! Extracting {len(post_urls)} collected posts...\n")
            
        print(f"Found {len(post_urls)} total posts/highlights. Extracting media...")
        for url in post_urls:
            try:
                parts = [p for p in urlparse(url).path.split('/') if p]
                if 'highlights' in parts:
                    shortcode = f"highlight_{parts[-1]}"
                else:
                    shortcode = parts[1]
            except:
                shortcode = "unknown"
            extract_post_media(driver, url, target_dir, shortcode)
            
        reorganize_downloads(target_dir, current_time_str)
        print("Profile download complete and organized.")
    finally:
        driver.quit()

def interactive_menu():
    config = load_config()
    while True:
        print("\n=== Instagram Media Extractor (Selenium Engine) ===")
        print("1. Download Post / Reel")
        print("2. Download Full Profile")
        print("3. Settings")
        print("4. Login (Generate Session)")
        print("5. Exit")
        
        choice = input("Select an option (1-5): ").strip()
        
        if choice == '1':
            url = input("Enter Post/Reel URL: ").strip()
            download_post(url, config)
        elif choice == '2':
            username = input("Enter Instagram Username: ").strip()
            download_profile(username, config)
        elif choice == '3':
            print(f"Current Download Directory: {config['download_directory']}")
            new_dir = input("Enter new directory (or press Enter to keep current): ").strip()
            if new_dir:
                config['download_directory'] = new_dir
                save_config(config)
                print("Settings saved.")
        elif choice == '4':
            login()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Instagram Media Extractor")
    parser.add_argument("url", nargs="?", help="URL of the post or username of profile")
    parser.add_argument("--profile", action="store_true", help="Download full profile instead of single post")
    parser.add_argument("--login", action="store_true", help="Interactive login before downloading")
    
    args = parser.parse_args()
    
    if args.url:
        if args.login:
            login()
        config = load_config()
        if args.profile:
            download_profile(args.url, config)
        else:
            download_post(args.url, config)
    else:
        try:
            interactive_menu()
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
