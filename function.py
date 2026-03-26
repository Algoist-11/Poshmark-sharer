import sys
import json
import pathlib
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from faker import Faker
import random

#to limit sharing to 8k per day
#to add try/except when following/followers list is empty
#export to exe? pip install?
#add choose following or follower
#add custom browser path
#maybe release async version in the future

def generate_ua():
    fake = Faker()
    UA_LIST = []
    for i in range(10):
        UA_LIST.append(fake.user_agent())
    return UA_LIST


def open_stealth(UA_LIST):
    p = sync_playwright().start()

    #open in stealth mode
    browser = p.chromium.launch(headless=False,executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                ])
    context = browser.new_context(user_agent=random.choice(UA_LIST))

    page = browser.new_page()

    page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Remove other automation traces
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """)

    page.goto("https://poshmark.ca/login")
    return browser,page,p

def login(page):
    #create credentials.json if not exist, and store the credentials for future use
    global user, credentials
    if not pathlib.Path('credentials.json').exists() or pathlib.Path('credentials.json').stat().st_size == 0:
        user = input('Please enter your username or email: ')
        pwd = input('Please enter your password: ')
        with open('credentials.json', 'w') as f:
            json.dump({'username': user, 'password': pwd}, f)
    else:
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)
            user = credentials['username']
            pwd = credentials['password']
        page.wait_for_timeout(5015)

    #————————————————————————————————————————————————————————
    
    try:
        page.locator('#login_form_username_email').fill(user)
        page.locator('#login_form_password').fill(pwd)
          
        # page.locator('button[type="submit"]').click()
        page.get_by_role("button", name="Login").click()

        error_banner = page.locator('div.error_banner')
        try:
            error_banner.wait_for(timeout=2000)
            raise ValueError('Login failed. Please check your credentials, then restart the program.')
        except PlaywrightTimeoutError:
            print('No error banner detected, checking for captcha...')
        
            
        recaptcha = page.get_by_role('status', name='recaptcha-accessible-status')
        try:
            recaptcha.wait_for(timeout=2000)
            print('Captcha detected. Please solve the captcha manually.')
            checkmark = page.locator('.recaptcha-checkbox-checkmark')
            try:
                checkmark.wait_for(timeout=30000)
                page.get_by_role("button", name="Login").click()
            except PlaywrightTimeoutError:
                print('Captcha timed out.')
                sys.exit(1)
            
        except PlaywrightTimeoutError:
            print('No captcha detected, proceeding to verify...')
        
            
    except ValueError as e:
        print(e)
        sys.exit(1)
                
    
    page.locator('input[name="otp"]').fill(input('Enter the verification code: '))
    # page.locator('button[data-et-on-name="otp_request"]').click()
    page.get_by_role("button", name="Done").click()
    page.wait_for_url("https://poshmark.ca/feed?login=true")

    # If the user input email, extract the username from the email————————————————————————
    if '@' in user:
        credentials['user'] = page.locator('//img[@class="user-image"]/@alt').inner_text()
        json.dump(credentials, open('credentials.json', 'w'))
        



def navigate_to_following(page):
    
    class selectFollowing(object):
        def __init__(self, page):
            self.page = page
            self.count = 0
            page.goto(f"https://poshmark.ca/user/{user}/following")
        def __iter__(self):
            return self
        def __next__(self):
            self.accounts = self.page.locator('p.follow__action__follower')
            self.current = self.accounts.nth(self.count)
            # if self.current == self.accounts.last:
            #     self.page.locator("footer").scroll_into_view_if_needed()
            if self.count >= self.accounts.count()-1:
                raise StopIteration
            self.current.click(delay=500)
            share_1user(page)
            self.count+=1
            page.goto(f"https://poshmark.ca/user/{user}/following")

    for i in selectFollowing(page):
        pass

#————————————————————————————————————————————————————————————————————
def navigate_to_follower(page):
    
    class selectFollower(object):
        def __init__(self, page):
            self.page = page
            self.count = 0
            page.goto(f"https://poshmark.ca/user/{user}/followers")
        def __iter__(self):
            return self
        def __next__(self):
            self.accounts = self.page.locator('p.follow__action__follower')
            self.current = self.accounts.nth(self.count)
            # if self.current == self.accounts.last:
            #     self.page.locator("footer").scroll_into_view_if_needed()
            if self.count >= self.accounts.count()-1:
                raise StopIteration
            self.current.click(delay=500)
            share_1user(page)
            self.count+=1
            page.goto(f"https://poshmark.ca/user/{user}/followers")

    for i in selectFollower(page):
        pass

def share_1user(page):
    class sharer(object):
        def __init__(self, page):
            self.page = page
            self.count = 0
        def __iter__(self):
            return self
        def __next__(self):
            self.items = self.page.locator('.share-gray-large')
            self.current = self.items.nth(self.count)
            print('count:',self.count)
            print('items count:',self.items.count()-1)
            
            if self.count >= self.items.count()-1:
                print('No more items to share')
                raise StopIteration
            self.current.click(delay=500)
            self.page.locator('//li[@class="internal-share"]/a[@data-et-name="share_poshmark"]').click(delay=1000)
            self.count+=1

    for i in sharer(page):
        pass
    print('Finished sharing all items of this user')

def close_browser(browser, p):
    browser.close()
    p.stop()