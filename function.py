import sys
import json
import pathlib
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from faker import Faker
import random
import time

#add auto follow people
#add when verification code is wrong
#export to exe for easy use
#maybe release async version in the future

def day_limit():
    global total_count
    if not pathlib.Path('time.json').exists() or pathlib.Path('time.json').stat().st_size == 0:
        current_time = time.localtime()
        with open('time.json', 'w') as f:
            json.dump({'last_time_day': current_time.tm_yday,'last_time_year': current_time.tm_year, 'count': 0}, f)
        total_count = 0
    else:
        with open('time.json', 'r') as f:
            data = json.load(f)
            total_count = data['count']
            last_time_day = data['last_time_day']
            last_time_year = data['last_time_year']
        
        current_time = time.localtime()
        if total_count >= 8000:
            if current_time.tm_yday == last_time_day and current_time.tm_year == last_time_year:
                print('You have reached the daily sharing limit of 8000. Please try again tomorrow.')
                sys.exit(1)
            else:
                total_count = 0
                with open('time.json', 'w') as f:
                    json.dump({'last_time_day': current_time.tm_yday,'last_time_year': current_time.tm_year, 'count': 0}, f)
        

def initialize():
    
    global setting
    print('Welcome! This program will help you bulk share items from your following/followers on Poshmark. Please make sure you have installed the Google Chrome browser and have stable internet connection.')
    
    if not pathlib.Path('settings.json').exists() or pathlib.Path('settings.json').stat().st_size == 0:
        print("To use this program, let's first initialize your settings. You can always change these settings later.")
        settings()
    else:
        use_default = input("Settings already exist. Do you want to use the existing settings? (y/n): ")
        if use_default.lower() == 'y':
            with open('settings.json', 'r') as f:
                setting = json.load(f)
        else:
            settings()



def settings():
        
    while True:
        try:
            li = input("Do you want to share your following or followers? (Enter 'following' or 'followers'): ")
            if li.lower() not in ['following', 'followers']:
                raise ValueError("Invalid input. Please enter one of the available options.")
            else:
                break
        except ValueError as e:
            print(e)
    
    while True:
        try:
            browse = input("Is your chrome browser installed in the default path? (y/n): ")
            if browse.lower() not in ['y', 'n']:
                raise ValueError("Invalid input. Please enter 'y' or 'n'.")
            else:
                if browse.lower() == 'n':
                    path = input("Please enter the full path to your chrome executable (e.g., C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe): ")
                    if not pathlib.Path(path).exists():
                        raise ValueError("The specified path does not exist. Please check the path and try again.")
                    else:
                        break
                elif browse.lower() == 'y':
                    path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                    break
        except ValueError as e:
            print(e)
    

    with open('settings.json', 'w') as f:
        setting = {'li': li.lower(), 'path': path}
        json.dump(setting, f)
    


def generate_ua():
    fake = Faker()
    UA_LIST = []
    for i in range(10):
        UA_LIST.append(fake.user_agent())
    return UA_LIST


def open_stealth(UA_LIST,path):
    p = sync_playwright().start()

    #open in stealth mode
    browser = p.chromium.launch(headless=False,executable_path=path,
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
    global user, pwd
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
        page.wait_for_timeout(3015)


    
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

    # If the user input email, extract the username from the email
    if '@' in user:
        user = page.locator('img.user-image').get_attribute('alt')
        with open('credentials.json', 'w') as f:
            json.dump({'username': user, 'password': pwd}, f)
        
        

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
            if self.count >= self.accounts.count()-1:
                if self.accounts.count() == 0:
                    print('No following accounts found. Please check your account and try again.')
                raise StopIteration
            self.current = self.accounts.nth(self.count)
            
            self.current.click(delay=500)
            share_1user(page)
            self.count+=1
            page.goto(f"https://poshmark.ca/user/{user}/following")

    for i in selectFollowing(page):
        pass


def navigate_to_followers(page):
    
    class selectFollower(object):
        def __init__(self, page):
            self.page = page
            self.count = 0
            page.goto(f"https://poshmark.ca/user/{user}/followers")
        def __iter__(self):
            return self
        def __next__(self):
            self.accounts = self.page.locator('p.follow__action__follower')
            if self.count >= self.accounts.count()-1:
                if self.accounts.count() == 0:
                    print('No follower accounts found. Please check your account and try again.')
                raise StopIteration
            self.current = self.accounts.nth(self.count)
            self.current.click(delay=500)
            share_1user(page)
            self.count+=1
            page.goto(f"https://poshmark.ca/user/{user}/followers")

    for i in selectFollower(page):
        pass




def share_1user(page):
    global total_count
    class sharer(object):
        def __init__(self, page):
            self.page = page
            self.count = 0
        def __iter__(self):
            return self
        def __next__(self):
            self.items = self.page.locator('.share-gray-large')
            if self.count >= self.items.count()-1:
                print('No more items to share')
                raise StopIteration
            self.current = self.items.nth(self.count)
            # print('count:',self.count)
            # print('items count:',self.items.count()-1)
            
            self.current.click(delay=500)
            self.page.locator('//li[@class="internal-share"]/a[@data-et-name="share_poshmark"]').click(delay=1000)
            self.count+=1

    
    for i in sharer(page):
        if total_count >= 8000:
            print('Reached daily limit, shutting down program.')
            sys.exit(1)
        else:
            total_count += 1
            pass
    print('Finished sharing all items of this user')
    

def close_browser(browser, p):
    global total_count
    
    current_time = time.localtime()
    with open('time.json', 'w') as f:
        json.dump({'last_time_day': current_time.tm_yday,'last_time_year': current_time.tm_year, 'count': total_count}, f)
    browser.close()
    p.stop()
    sys.exit(1)