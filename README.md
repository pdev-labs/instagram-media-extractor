# Instagram Media Extractor

A powerful, pure-Selenium and yt-dlp based Instagram Media Extractor designed to natively bypass the notorious `429 Too Many Requests` API blocks. 

This tool perfectly mimics a real headless Google Chrome browser to physically scroll through user profiles and natively extract high-resolution Posts, Reels, Images, and Profile Pictures directly from the DOM—completely bypassing Instagram's aggressive GraphQL rate limiters.

## Features
- **Anti-429 Architecture**: Uses full headless Selenium scraping to emulate real human scrolling. Does not ping restricted API endpoints.
- **yt-dlp Video Integration**: Automatically parses your browser cookies into Netscape format to download maximum quality video streams from Reels and Video posts.
- **Cross-Platform Compatibility**: Fully automated setup on Windows, macOS, Linux, and even Termux (Android)*!
- **Auto-Organization**: Downloads are dynamically sorted into `/username/date_and_time/image/` and `/video/` based on your system's default Downloads folder.
- **Persistent Sessions**: Captures your real Chrome `User-Agent` and cookies during an initial interactive login, and permanently reuses them to avoid bot-detection.

## Installation

You can seamlessly install this on any operating system using the provided bootstrap scripts. It will automatically create an isolated Python virtual environment and install all dependencies.

### Linux / macOS
```bash
./install.sh
```

### Windows
```cmd
install.bat
```

## Usage

Simply run the main Python script:
```bash
./ig_media_extractor.py
```

An interactive terminal menu will appear:
```text
=== Instagram Media Extractor (Selenium Engine) ===
1. Download Post / Reel
2. Download Full Profile
3. Settings
4. Login (Generate Session)
5. Exit
```

**Step 1:** Select `4` to securely log in to your Instagram account via an automated browser window. This generates a safe, reusable session cookie locally.  
**Step 2:** Select `1` or `2` to start downloading media!

### 📱 Special Instructions for Termux (Android) Users
Because Termux cannot open a native browser window for the automated login step, you must manually provide your session cookies:
1. Download **Kiwi Browser** from the Play Store (it supports desktop extensions on Android).
2. Install a cookie exporter extension (e.g., "EditThisCookie" or "Get cookies.txt LOCALLY").
3. Log into Instagram inside Kiwi Browser, and use the extension to export your cookies in JSON format.
4. Save the exported text into a file named exactly `ig_cookies.json` in the same directory as this script.
5. The script will automatically detect your session—you can now directly select **Option 1 or 2** to start downloading!

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
