import function

UA_LIST = function.generate_ua()

browser, page, p = function.open_stealth(UA_LIST)
function.login(page)
function.navigate_to_following(page)

function.close_browser(browser, p)

#<span aria-live="polite" aria-labelledby="recaptcha-accessible-status"></span>
#<div class="recaptcha-checkbox-checkmark" role="presentation" style=""></div>