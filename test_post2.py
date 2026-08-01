from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get("https://www.instagram.com/favicon.ico")
with open("ig_cookies.json", "r") as f:
    cookies = json.load(f)
    for c in cookies:
        if 'sameSite' in c: del c['sameSite']
        try: driver.add_cookie(c)
        except: pass
driver.get("https://www.instagram.com/aadarsh_6379/p/DZhnD1wjEgd/")
time.sleep(5)
imgs = driver.find_elements(By.TAG_NAME, 'img')
for i in imgs:
    src = i.get_attribute('src')
    if src and "profile_pic" not in src and "stp=" not in src:
        print("POSSIBLE MAIN IMG:", src)
        print("STYLE:", i.get_attribute('style'))
        print("CLASS:", i.get_attribute('class'))
driver.quit()
