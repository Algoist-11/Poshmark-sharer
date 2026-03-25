import random

#to add try & exception for login failure
def login(page):
    global user,pwd
    user = input('Please enter your username (do NOT use email): ')
    pwd = input('Please enter your password: ')
    

    page.locator('#login_form_username_email').fill(user)
    page.locator('#login_form_password').fill(pwd)      
    # page.locator('button[type="submit"]').click()
    page.get_by_role("button", name="Login").click()

    page.locator('input[name="otp"]').fill(input('Enter the verification code: '))
    # page.locator('button[data-et-on-name="otp_request"]').click()
    page.get_by_role("button", name="Done").click()

def navigate_to_following(page):
    page.wait_for_url("https://poshmark.ca/feed?login=true")
    page.goto(f"https://poshmark.ca/user/{user}/following")
    page.locator('p.follow__action__follower').first.click()

def share_1user(page):
    class sharer(object):
        def __init__(self, page):
            self.page = page
            self.count = 0
        def __iter__(self):
            return self
        def __next__(self):
            self.item = self.page.locator('.share-gray-large')
            self.current = self.item.nth(self.count)
            if self.current == self.item.last:
                self.page.locator("footer").scroll_into_view_if_needed()
                if self.count == self.item.count():
                    raise StopIteration
            self.current.click(delay=random.randint(1000,2000))
            self.page.locator('//li[@class="internal-share"]/a[@data-et-name="share_poshmark"]').click(delay=random.randint(1000,2000))
            self.count+=1

    for i in sharer(page):
        pass