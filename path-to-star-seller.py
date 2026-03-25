from playwright.sync_api import sync_playwright
import functions

p = sync_playwright().start()

browser = p.chromium.launch(headless=False,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
page = browser.new_page()
page.goto("https://poshmark.ca/login")


functions.login(page)
functions.navigate_to_following(page)
functions.share_1user(page)


input('Closing...')
browser.close()
p.stop()