import function


# function.day_limit()
function.initialize()


UA_LIST = function.generate_ua()

browser, page, p = function.open_stealth(UA_LIST,function.setting['path'])

function.login(page)

if function.setting['li'] == 'following':
    function.navigate_to_following(page)
elif function.setting['li'] == 'followers':
    function.navigate_to_followers(page)
else:
    print('Something went wrong with the settings. Please delete the settings.json file and try again.')


input('closing...')

function.close_browser(browser, p)

