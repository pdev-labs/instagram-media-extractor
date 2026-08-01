import json
import instaloader
L = instaloader.Instaloader()
with open("ig_cookies.json", 'r') as f:
    cookies = json.load(f)
for cookie in cookies:
    if 'instagram.com' in cookie.get('domain', ''):
        L.context._session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))
L.context.username = "dummy"
print("Logged in:", L.context.is_logged_in)
try:
    L.download_profile("instagram", profile_pic_only=True)
    print("Success")
except Exception as e:
    print("Error:", e)
