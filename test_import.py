import json
import instaloader

def import_cookies_from_json(L, cookie_file="ig_cookies.json"):
    try:
        with open(cookie_file, 'r') as f:
            cookies = json.load(f)
        for cookie in cookies:
            L.context._session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))
        
        # In Instaloader, is_logged_in is determined by the presence of a sessionid cookie
        sessionid = L.context._session.cookies.get('sessionid')
        if sessionid:
            L.context.is_logged_in = True
            
        print("Loaded cookies from ig_cookies.json!")
        return True
    except Exception as e:
        print(f"Error loading {cookie_file}: {e}")
        return False
