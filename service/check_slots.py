import sys, os, re, requests, time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import p_data
import datetime
import win32ui

#from twilio.rest import Client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
chromedriver = ROOT_DIR + "/chromedriver"
print ("Current Chrome Driver: %s" % (str(chromedriver)))

# amazon credentials
amazon_username = p_data.EMAIL
amazon_password = p_data.PASSWORD
amazon_otp = p_data.OTP

#int vars
refresh_wait = 300

# # twilio configuration
# to_mobilenumber = "+18888888888"
# from_mobilenumber = "+19999999999"
# account_sid = "fake_account_sid"
# auth_token = "fake_auth_token"
# client = Client(account_sid, auth_token)

def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.binary_location = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
    driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
    return driver

def terminate(driver):
    driver.quit()

def check_slots():
    try:
        print('Creating Chrome Driver ...')
        driver = create_driver()

        print('Logging into Amazon ...')
        driver.get('https://www.amazon.com/gp/sign-in.html')
        email_field = driver.find_element_by_css_selector('#ap_email')
        email_field.send_keys(amazon_username)
        driver.find_element_by_css_selector('#continue').click()
        time.sleep(1.5)
        password_check = driver.find_element_by_name('rememberMe').click()
        time.sleep(1.5)
        password_field = driver.find_element_by_css_selector('#ap_password')
        password_field.send_keys(amazon_password)
        driver.find_element_by_css_selector('#signInSubmit').click()
        time.sleep(1.5)
        OTP_enter = driver.find_element_by_id('auth-mfa-otpcode')
        OTP_enter.send_keys(amazon_otp)
        OTP_check = driver.find_element_by_name('rememberDevice').click()
        driver.find_element_by_id('auth-signin-button').click()


        print('Redirecting to Whole Food Market ...')
        driver.get('https://www.amazon.com/gp/browse.html?node=17235386011&ref_=nav_em_0_2_25_2__explore_wf')
        time.sleep(1.5)
        print ("Navigate to Cart! \n")
        driver.find_element_by_id('nav-cart').click()
        time.sleep(1.5)
        print ("Checkout WholeFoods! \n")
        driver.find_element_by_name('proceedToALMCheckout-VUZHIFdob2xlIEZvb2Rz').click()
        time.sleep(1.5)
        driver.find_element_by_name('proceedToCheckout').click()
        time.sleep(1.5)
        driver.find_element_by_id('subsContinueButton').click()
        time.sleep(1.5)


        # print('Checkout Step One ...')
        # driver.find_element_by_name('proceedToFreshCheckout').click()
        # time.sleep(1.5)
        # print('Checkout Step Two ...')
        # driver.find_element_by_name('proceedToCheckout').click()

        more_dows = True
        slots_available = False
        available_slots = ""
        while not slots_available:
            while more_dows:
                time.sleep(1.5)
                slots = driver.find_elements_by_css_selector('.ss-carousel-item')
                for slot in slots:
                    if slot.value_of_css_property('display') != 'none':
                        slot.click()
                        date_containers = driver.find_elements_by_css_selector('.Date-slot-container')
                        for date_container in date_containers:
                            if date_container.value_of_css_property('display') != 'none':
                                unattended_slots = date_container.find_element_by_css_selector('#slot-container-UNATTENDED')
                                if 'No doorstep delivery' not in unattended_slots.text:
                                    available_slots = unattended_slots.text.replace('Select a time', '').strip()
                                    slots_available = True
                                else:
                                    print(unattended_slots.text.replace('Select a time', '').strip())
                try:
                    next_button = driver.find_element_by_css_selector('#nextButton')
                    more_dows = not next_button.get_property('disabled')
                    if more_dows: next_button.click()
                except Exception as e:
                    print ("Next Button Not Found!: %s" % (str(e)))
                    break

            if slots_available:
                # client.messages.create(to=to_mobilenumber,
                #        from_=from_mobilenumber,
                #        body=available_slots)
                win32ui.MessageBox("%s" % (available_slots), "Slot Found!", MB_SYSTEMMODAL)
                print('Slots Available: %s' % (available_slots))
            else:
                print('No slots available. Sleeping ...')
                more_dows = True
                current_time = datetime.datetime.now()
                refresh_time = current_time + datetime.timedelta(minutes = (refresh_wait/60))
                refresh_time_fmt = refresh_time.strftime("%H:%M:%S")
                print ('Will Try Again At: %s' % (str(refresh_time_fmt)))
                time.sleep(refresh_wait)
                driver.refresh()

        terminate(driver)
    except Exception as e:
        terminate(driver)
        raise ValueError(str(e))

if __name__ == "__main__":
    check_slots()
