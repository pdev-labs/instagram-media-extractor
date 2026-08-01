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
time.sleep(5)
print(driver.find_element(By.TAG_NAME, 'body').text)
driver.quit()
