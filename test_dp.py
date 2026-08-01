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
driver.get("https://www.instagram.com/aadarsh_6379/")
time.sleep(4)
imgs = driver.find_elements(By.TAG_NAME, 'img')
for i in imgs:
    print("SRC:", i.get_attribute('src'))
    print("ALT:", i.get_attribute('alt'))
driver.quit()
