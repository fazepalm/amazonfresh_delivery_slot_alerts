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

def select_delivery_day(time_slot_btn_list):
    selected_time_slot_btn_dict = {}
    for time_slot_btn in time_slot_btn_list:
        dow_text_ele = time_slot_btn.find_element_by_class_name('ufss-date-select-toggle-text-day-of-week')
        dow_text = dow_text_ele.text
        print ("Current dow_text: %s" % (str(dow_text)))
        time.sleep(click_wait)

        month_day_text_ele = time_slot_btn.find_element_by_class_name('ufss-date-select-toggle-text-month-day')
        month_day_text = month_day_text_ele.text
        print ("Current month_day_text: %s" % (str(month_day_text)))
        time.sleep(click_wait)

        aval_text_ele = time_slot_btn.find_element_by_class_name('ufss-date-select-toggle-text-availability')
        aval_text = aval_text_ele.text
        print ("Current aval_text: %s" % (str(aval_text)))
        time.sleep(click_wait)

        if not re.search("not available", aval_text, re.IGNORECASE):
            time_slot_btn.click
            selected_time_slot_btn_dict["btn_element"] = time_slot_btn
            selected_time_slot_btn_dict["btn_dow"] = dow_text
            selected_time_slot_btn_dict["btn_month_day"] = month_day_text
            selected_time_slot_btn_dict["btn_aval"] = aval_text

    return selected_time_slot_btn_dict

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
            slot_time_dict = {}
            slot_time_list = []

            time.sleep(click_wait)
            time_delivery_div = driver.find_element_by_class_name('ufss-date-select-container')
            #print ("Current time_delivery_div: %s" % (str(time_delivery_div)))
            time_slot_btn_list = time_delivery_div.find_elements_by_tag_name('button')
            #print ("Current aval_text_div_list: %s" % (str(aval_text_div_list)))
            selected_time_slot_btn_dict = select_delivery_day(time_slot_btn_list)
            print ("Current selected_time_slot_btn_dict: %s" % (str(selected_time_slot_btn_dict)))

            if selected_time_slot_btn_dict != {}:
                time_slot_btn = selected_time_slot_btn_dict.get("btn_element", None)
                dow_text = selected_time_slot_btn_dict.get("btn_dow", None)
                month_day_text = selected_time_slot_btn_dict.get("btn_month_day", None)
                aval_text = selected_time_slot_btn_dict.get("btn_aval", None)

                slot_select_div = driver.find_element_by_class_name('ufss-slotselect-container')
                print ("Current slot_select_div: %s" % (str(slot_select_div)))
                slot_time_div_list = slot_select_div.find_elements_by_class_name('ufss-slotgroup-container')
                print ("Current slot_time_div_list: %s" % (str(slot_time_div_list)))
                for slot_time_div in slot_time_div_list:
                    slot_time_header = slot_time_div.find_element_by_class_name('ufss-slotgroup-heading-container')
                    slot_time_header_text = slot_time_div.find_element_by_tag_name('h4').text
                    print ("Current slot_time_header_text: %s" % (str(slot_time_header_text)))
                    slot_time_text_list = slot_time_div.find_elements_by_class_name('ufss-slot-time-window-text')
                    for slot_time_text in slot_time_text_list:
                        print ("Current slot_time_text: %s" % (str(slot_time_text.text)))
                        slot_time_list.append(slot_time_text)
                    slot_time_dict[slot_time_header_text] = slot_time_list
                slots_available = True
                win32ui.MessageBox("%s; %s Delivery Times: \n %s; %s" % (dow_text, month_day_text, ",".join(slot_time_dict.keys()), ",".join(slot_time_dict.values())), "%s; %s Delivery Times" % (dow_text, month_day_text), MB_SYSTEMMODAL)
                print ("Current slot_time_dict: %s" % (slot_time_dict))
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
