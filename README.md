##
Thanks to bryan3189 for the framework (selenium usage)

#Functions
Currently outputs the current available timeslots as a windows message... might add texting/emailing and support for amazonFresh
Going to handle when page refresh causes display page to change back to cart, or when amazon alerts the user that an item is no longer available

# Amazon WholeFoods/Fresh Delivery Slot Alerts
  - Python 3.7
  - Selenium

### Setup
a p_data.py file needs to be created with the variables EMAIL, PASSWORD, OTP
this file allows separation for your private date... this can be obfuscated farther if need be...

### Run Code
```sh
$ pip install -r requirements/requirements.txt
$ cd service
$ python check_slots.py
```
