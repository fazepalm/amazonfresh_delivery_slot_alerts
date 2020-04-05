import sys, os, re, requests, time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from twilio.rest import Client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
chromedriver = ROOT_DIR + "/chromedriver"

# amazon credentials
amazon_username = "first.last@email.com"
amazon_password = "secret_password"

# twilio configuration
to_mobilenumber = "+18888888888"
from_mobilenumber = "+19999999999"
account_sid = "fake_account_sid"
auth_token = "fake_auth_token"
client = Client(account_sid, auth_token)

def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
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
        password_field = driver.find_element_by_css_selector('#ap_password')
        password_field.send_keys(amazon_password)
        driver.find_element_by_css_selector('#signInSubmit').click()
        time.sleep(1.5)

        print('Redirecting to AmazonFresh ...')
        driver.get('https://www.amazon.com/alm/storefront?almBrandId=QW1hem9uIEZyZXNo')
        time.sleep(1.5)
        print('Checkout Step One ...')
        driver.find_element_by_name('proceedToFreshCheckout').click()
        time.sleep(1.5)
        print('Checkout Step Two ...')
        driver.find_element_by_name('proceedToCheckout').click()

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

                next_button = driver.find_element_by_css_selector('#nextButton')
                more_dows = not next_button.get_property('disabled')
                if more_dows: next_button.click()

            if slots_available: 
                client.messages.create(to=to_mobilenumber, 
                       from_=from_mobilenumber, 
                       body=available_slots)
                print('Slots Available!')
            else:
                print('No slots available. Sleeping ...')
                more_dows = True
                time.sleep(300)
                driver.refresh()
        
        terminate(driver)
    except Exception as e:
        terminate(driver)
        raise ValueError(str(e))

if __name__ == "__main__":
    check_slots()
