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
click_wait = random.randint(1, 6)

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
        time.sleep(click_wait)
        password_check = driver.find_element_by_name('rememberMe').click()
        time.sleep(click_wait)
        password_field = driver.find_element_by_css_selector('#ap_password')
        password_field.send_keys(amazon_password)
        driver.find_element_by_css_selector('#signInSubmit').click()
        time.sleep(click_wait)
        OTP_enter = driver.find_element_by_id('auth-mfa-otpcode')
        OTP_enter.send_keys(amazon_otp)
        OTP_check = driver.find_element_by_name('rememberDevice').click()
        driver.find_element_by_id('auth-signin-button').click()
        time.sleep(click_wait)


        print('Redirecting to Whole Food Market ...')
        driver.get('https://www.amazon.com/gp/browse.html?node=17235386011&ref_=nav_em_0_2_25_2__explore_wf')
        time.sleep(click_wait)
        print ("Navigate to Cart! \n")
        driver.find_element_by_id('nav-cart').click()
        time.sleep(click_wait)
        print ("Checkout WholeFoods! \n")
        driver.find_element_by_name('proceedToALMCheckout-VUZHIFdob2xlIEZvb2Rz').click()
        time.sleep(click_wait)
        driver.find_element_by_name('proceedToCheckout').click()
        time.sleep(click_wait)
        driver.find_element_by_id('subsContinueButton').click()
        time.sleep(click_wait)

        #more_dows = True
        slots_available = False
        available_slots = ""
        tomm_delivery_time_ele_list = []
        today_delivery_time_ele_list = []


        while not slots_available:
            time.sleep(click_wait)
            today_btn = driver.find_element_by_name('20200413')
            today_btn_ele_aval = today_btn.find_element_by_class_name("ufss-date-select-toggle-text-availability")
            today_btn_ele_aval_val = today_btn_ele_aval.text
            #print ("Current today_btn_ele_aval_val: %s" % (today_btn_ele_aval_val))

            tomm_btn = driver.find_element_by_name('20200414')
            tomm_btn_ele_aval = tomm_btn.find_element_by_class_name("ufss-date-select-toggle-text-availability")
            tomm_btn_ele_aval_val = today_btn_ele_aval.text
            #print ("Current tomm_btn_ele_aval_val: %s" % (tomm_btn_ele_aval_val))

            delivery_time_div = driver.find_element_by_id("20200413")
            #attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', delivery_time_div)
            #print ("delivery_time_div, attrs: %s" % (attrs))

            if not re.search("not available", today_btn_ele_aval_val, re.IGNORECASE):
                today_delivery_time_div_class = delivery_time_div.get_attribute("class")
                if re.search("ufss-available", today_delivery_time_div_class, re.IGNORECASE):
                    today_delivery_time_li_list = delivery_time_div.find_elements_by_class_name("ufss-slot-container")
                    for today_delivery_time_li in today_delivery_time_li_list:
                        today_delivery_time_ele = today_delivery_time_li.find_element_by_class_name("ufss-slot-time-window-text")
                        today_delivery_time_ele_list.append(today_delivery_time_ele)
                        print ("Today Delivery Times: %s" % (today_delivery_time_ele.text))

                    win32ui.MessageBox("Today Delivery Times: \n %s" % (",".join(today_delivery_time_ele_list)), "Today Delivery Times", MB_SYSTEMMODAL)
                    print ("Today Slots Available!")
                    slots_available = True

            elif not re.search("not available", tomm_btn_ele_aval_val, re.IGNORECASE):
                tomm_btn.click()
                tomm_delivery_time_div_class = delivery_time_div.get_attribute("class")
                if re.search("ufss-available", tomm_delivery_time_div_class, re.IGNORECASE):
                    tomm_delivery_time_li_list = delivery_time_div.find_elements_by_class_name("ufss-slot-container")
                    for tomm_delivery_time_li in tomm_delivery_time_li_list:
                        tomm_delivery_time_ele = tomm_delivery_time_li.find_element_by_class_name("ufss-slot-time-window-text")
                        tomm_delivery_time_ele_list.append(tomm_delivery_time_ele)
                        print ("Tommorrow Delivery Times: %s" % (tomm_delivery_time_ele.text))

                    win32ui.MessageBox("Tommorrow Delivery Times: \n %s" % (",".join(tomm_delivery_time_ele_list)), "Tommorrow Delivery Times", MB_SYSTEMMODAL)
                    print ("Tommorow Slots Available!")
                    slots_available = True

            else:
                print ('No slots available. Sleeping ...')
                more_dows = True
                current_time = datetime.datetime.now()
                refresh_time = current_time + datetime.timedelta(minutes = (refresh_wait/60))
                refresh_time_fmt = refresh_time.strftime("%I:%M:%S%p")
                print ('Will Try Again At: %s' % (str(refresh_time_fmt)))
                time.sleep(refresh_wait)
                driver.refresh()

        terminate(driver)
    except Exception as e:
        terminate(driver)
        raise ValueError(str(e))

if __name__ == "__main__":
    check_slots()
