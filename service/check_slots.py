import sys, os, re, requests, time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import p_data
import datetime
import win32gui, win32com.client, win32ui
import random
import re
import traceback
from collections import defaultdict
import ctypes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
chromedriver = ROOT_DIR + "/chromedriver"
print ("Current Chrome Driver: %s" % (str(chromedriver)))

# amazon credentials
amazon_username = p_data.EMAIL
amazon_password = p_data.PASSWORD
amazon_otp = p_data.OTP

#int vars
refresh_wait = random.randint(200, 400)
click_wait = random.randint(1, 3)

def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

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

def get_delivery_times(driver):
    time_delivery_div = driver.find_element_by_class_name('ufss-date-select-container')
    #print ("Current time_delivery_div: %s" % (str(time_delivery_div)))
    time_slot_btn_list = time_delivery_div.find_elements_by_tag_name('button')
    #print ("Current aval_text_div_list: %s" % (str(aval_text_div_list)))
    selected_time_slot_btn_dict = select_delivery_day(time_slot_btn_list)
    print ("Current selected_time_slot_btn_dict: %s" % (str(selected_time_slot_btn_dict)))
    return selected_time_slot_btn_dict

def checkout_WF(driver):
    print ("Checkout WholeFoods! \n")
    time.sleep(click_wait)
    driver.find_element_by_name('proceedToALMCheckout-VUZHIFdob2xlIEZvb2Rz').click()
    time.sleep(click_wait)
    driver.find_element_by_name('proceedToCheckout').click()
    time.sleep(click_wait)
    driver.find_element_by_id('subsContinueButton').click()
    time.sleep(click_wait)

def check_slots():
    try:
        window_name = "amazon_delivery_slot_alerts"
        ctypes.windll.kernel32.SetConsoleTitleW(window_name)
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
        checkout_WF(driver)

        slots_available = False
        available_slots = ""
        delivery_time_ele_list = []

        while not slots_available:
            slot_time_dict = defaultdict(list)
            slot_time_list = []
            top_windows = []

            time.sleep(click_wait)
            try:
                selected_time_slot_btn_dict = get_delivery_times(driver)
            except:
                try:
                    checkout_WF(driver)
                    selected_time_slot_btn_dict = get_delivery_times(driver)
                    continue
                except:
                    traceback.print_exc(file=sys.stdout)
                    terminate(driver)

            if selected_time_slot_btn_dict != {}:
                time_slot_btn = selected_time_slot_btn_dict.get("btn_element", None)
                dow_text = selected_time_slot_btn_dict.get("btn_dow", None)
                month_day_text = selected_time_slot_btn_dict.get("btn_month_day", None)
                aval_text = selected_time_slot_btn_dict.get("btn_aval", None)

                slot_select_div = driver.find_element_by_class_name('ufss-slotselect-container')
                #print ("Current slot_select_div: %s" % (str(slot_select_div)))
                slot_time_div_list = slot_select_div.find_elements_by_class_name('ufss-slotgroup-container')
                #print ("Current slot_time_div_list: %s" % (str(slot_time_div_list)))
                for slot_time_div in slot_time_div_list:
                    slot_time_header = slot_time_div.find_element_by_class_name('ufss-slotgroup-heading-container')
                    slot_time_header_text = slot_time_div.find_element_by_tag_name('h4').text
                    print ("Current slot_time_header_text: %s" % (str(slot_time_header_text)))
                    slot_time_text_list = slot_time_div.find_elements_by_class_name('ufss-slot-time-window-text')
                    for slot_time_text in slot_time_text_list:
                        print ("Current slot_time_text: %s" % (str(slot_time_text.text)))
                        slot_time_dict[slot_time_header_text].append(slot_time_text.text)
                slots_available = True
                print ("Current slot_time_dict: %s" % (slot_time_dict))
                if slot_time_dict != {}:
                    slot_time_dict_values = list(slot_time_dict.values())[0]
                    #print ("Current slot_time_dict.keys: %s" % (str(slot_time_dict.keys())))
                    #print ("Current slot_time_dict.values: %s" % (str(slot_time_dict_values)))
                    current_time = datetime.datetime.now()
                    current_time_fmt = current_time.strftime("%I:%M:%S%p")
                    print ("Found Delivery Time At: %s" % (str(current_time_fmt)))
                    win32gui.EnumWindows(windowEnumerationHandler, top_windows)
                    console_win = [win for win in top_windows if re.search(window_name, str(win), re.IGNORECASE)]
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shell.SendKeys('%')
                    win32gui.ShowWindow(console_win[0][0], 9)
                    win32gui.SetForegroundWindow(console_win[0][0])
                    shot_time_key_str = ",".join(slot_time_dict.keys())
                    shot_time_values_str = ",".join(slot_time_dict_values)
                    win32ui.MessageBox(
                                        "%s; %s Delivery Times: \n %s; %s" % (dow_text, month_day_text, shot_time_key_str, shot_time_values_str),
                                        "%s; %s Delivery Times" % (dow_text, month_day_text),
                                        0x40000
                                        )
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

        raise ValueError(str(e))

if __name__ == "__main__":
    check_slots()

    check_slots()
