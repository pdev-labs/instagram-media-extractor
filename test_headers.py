import instaloader
import json

L = instaloader.Instaloader()
with open("ig_user_agent.txt", "r") as f:
    L.context.user_agent = f.read().strip()
    L.context._session.headers.update({'User-Agent': L.context.user_agent})

with open("ig_cookies.json", 'r') as f:
    cookies = json.load(f)

csrf = ""
for cookie in cookies:
    if 'instagram.com' in cookie.get('domain', ''):
        L.context._session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))
        if cookie['name'] == 'csrftoken':
            csrf = cookie['value']

L.context.username = "session_user"

L.context._session.headers.update({
    'X-IG-App-ID': '936619743392459',
    'X-ASBD-ID': '198387',
    'X-CSRFToken': csrf,
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.instagram.com/'
})

try:
    L.download_profile("instagram", profile_pic_only=True)
    print("Success")
except Exception as e:
    print("Error:", e)
