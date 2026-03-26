from playwright.sync_api import sync_playwright
import function

p = sync_playwright().start()

browser = p.chromium.launch(headless=False,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
context = browser.new_context()
page = browser.new_page()
page.goto("https://poshmark.ca/login")


function.login(page)
function.navigate_to_following(page)



browser.close()
p.stop()

