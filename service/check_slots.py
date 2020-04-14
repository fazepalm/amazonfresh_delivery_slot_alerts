import sys, os, re, requests, time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import p_data
import datetime
import win32ui
import random
import re
import traceback

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
click_wait = random.randint(1, 3)

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
        time.sleep(click_wait)
        driver.find_element_by_css_selector('#continue').click()
        time.sleep(click_wait)
        password_check = driver.find_element_by_name('rememberMe').click()
        time.sleep(click_wait)
        password_field = driver.find_element_by_css_selector('#ap_password')
        time.sleep(click_wait)
        password_field.send_keys(amazon_password)
        time.sleep(click_wait)
        driver.find_element_by_css_selector('#signInSubmit').click()
        time.sleep(click_wait)
        OTP_enter = driver.find_element_by_id('auth-mfa-otpcode')
        time.sleep(click_wait)
        OTP_enter.send_keys(amazon_otp)
        time.sleep(click_wait)
        OTP_check = driver.find_element_by_name('rememberDevice').click()
        time.sleep(click_wait)
        driver.find_element_by_id('auth-signin-button').click()
        time.sleep(click_wait)


        print('Redirecting to Whole Food Market ...')
        driver.get('https://www.amazon.com/gp/browse.html?node=17235386011&ref_=nav_em_0_2_25_2__explore_wf')
        time.sleep(click_wait)
        print ("Navigate to Cart! \n")
        time.sleep(click_wait)
        driver.find_element_by_id('nav-cart').click()
        time.sleep(click_wait)
        print ("Checkout WholeFoods! \n")
        time.sleep(click_wait)
        driver.find_element_by_name('proceedToALMCheckout-VUZHIFdob2xlIEZvb2Rz').click()
        time.sleep(click_wait)
        driver.find_element_by_name('proceedToCheckout').click()
        time.sleep(click_wait)
        driver.find_element_by_id('subsContinueButton').click()
        time.sleep(click_wait)

        slots_available = False
        available_slots = ""
        delivery_time_ele_list = []

        while not slots_available:
            aval_text_div_list = []
            delivery_time_ele_list = []

            time.sleep(click_wait)
            time_delivery_div = driver.find_element_by_class_name('ufss-date-select-container')
            #print ("Current time_delivery_div: %s" % (str(time_delivery_div)))
            aval_text_div_list = time_delivery_div.find_elements_by_class_name('ufss-date-select-toggle-text-container')
            #print ("Current aval_text_div_list: %s" % (str(aval_text_div_list)))

            for aval_text_div in aval_text_div_list:
                dow_text_ele = aval_text_div.find_element_by_class_name('ufss-date-select-toggle-text-day-of-week')
                dow_text = dow_text_ele.text
                print ("Current dow_text: %s" % (str(dow_text)))
                time.sleep(click_wait)

                month_day_text_ele = aval_text_div.find_element_by_class_name('ufss-date-select-toggle-text-month-day')
                month_day_text = month_day_text_ele.text
                print ("Current month_day_text: %s" % (str(month_day_text)))
                time.sleep(click_wait)

                aval_text_ele = aval_text_div.find_element_by_class_name('ufss-date-select-toggle-text-availability')
                aval_text = aval_text_ele.text
                print ("Current aval_text: %s" % (str(aval_text)))
                time.sleep(click_wait)

            if not re.search("not available", aval_text, re.IGNORECASE):
                delivery_time_div_class = delivery_time_div.get_attribute("class")
                if re.search("ufss-available", delivery_time_div_class, re.IGNORECASE):
                    delivery_time_li_list = delivery_time_div.find_elements_by_class_name("ufss-slot-container")
                    for delivery_time_li in delivery_time_li_list:
                        delivery_time_ele = delivery_time_li.find_element_by_class_name("ufss-slot-time-window-text")
                        delivery_time_ele_list.append(delivery_time_ele)
                        print ("%s; %s Delivery Times: %s" % (dow_text, month_day_text, delivery_time_ele.text))

                    win32ui.MessageBox("%s; %s Delivery Times: \n %s" % (dow_text, month_day_text, ",".join(today_delivery_time_ele_list)), "%s; %s Delivery Times" % (dow_text, month_day_text), MB_SYSTEMMODAL)
                    print ("%s; %s Slots Available!" % (dow_text, month_day_text))
                    slots_available = True
                    terminate(driver)

            else:
                print ('No slots available. Sleeping ...')
                more_dows = True
                current_time = datetime.datetime.now()
                refresh_time = current_time + datetime.timedelta(minutes = (refresh_wait/60))
                refresh_time_fmt = refresh_time.strftime("%I:%M:%S%p")
                print ('Will Try Again At: %s' % (str(refresh_time_fmt)))
                time.sleep(refresh_wait)
                driver.refresh()

    except Exception as e:
        #terminate(driver)
        raise ValueError(str(e))

if __name__ == "__main__":
    check_slots()
