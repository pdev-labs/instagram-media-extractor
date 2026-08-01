import instaloader
L = instaloader.Instaloader(dirname_pattern="{profile}/{date_utc:%Y-%m-%d_%H-%M-%S}")
try:
    L.download_profile("instagram", profile_pic_only=True)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
