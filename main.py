import gspread
from google.oauth2.service_account import Credentials
from time import sleep
import random
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import FirefoxOptions
# from openpyxl import Workbook
import datetime




# Load credentials from JSON file
# creds = Credentials.from_service_account_file('/home/dany/Desktop/autogreens/autogreens-key.json')
creds = Credentials.from_service_account_file('autogreens-key.json')


# Define the scope
scope = [
   'https://spreadsheets.google.com/feeds',
   'https://www.googleapis.com/auth/spreadsheets',
   'https://www.googleapis.com/auth/drive.file',
   'https://www.googleapis.com/auth/drive'
]
creds = creds.with_scopes(scope)


# Authorize the client
client = gspread.authorize(creds)





# Higher order functions, taking sheet as an argument

def create_row(sheet, data):
   sheet.append_row(data)

def read_data(sheet):
   return sheet.get_all_records()

def update_cell(sheet, row, col, new_value):
    sheet.update_cell(row, col, new_value)

def delete_row(sheet, row):
    sheet.delete_rows(row)
  

GREENYARD_PRICE_COL = 4
VP_COL = 5
MARGE_COL = 6
LAST_UPDATE_COL = 7


import json


# Load the JSON file
# with open('/home/dany/Desktop/autogreens/config.json', 'r') as file:
#    config = json.load(file)
with open('config.json', 'r') as file:
   config = json.load(file)


# Access the parameters
BROWSER_DRIVER_PATH = config.get('browser_driver_path')
GY_USERNAME_MARKET = config.get('gy_username_market')
GY_PASSWORD_MARKET = config.get('gy_password_market')


def human_sleep(min_time=1, max_time=3):
   sleep_time = random.uniform(min_time, max_time)
   sleep(sleep_time)




opts = FirefoxOptions()
# opts.add_argument('--headless')
opts.binary_location = 'C:/Program Files/Mozilla Firefox/firefox.exe'


def init_eos(username, password):


   service = webdriver.FirefoxService(executable_path=BROWSER_DRIVER_PATH)
   driver = webdriver.Firefox(service=service, options=opts)




   # Step 1: Log in to the website
   driver.get("https://eos.firstinfresh.be/login")
   human_sleep(2, 4)


   # Enter username
   username_input = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/form/div[1]/div[1]/input")
   ActionChains(driver).move_to_element(username_input).click().perform()
   human_sleep(1, 2)
   username_input.send_keys(username)  # Replace with your username
   human_sleep(1, 3)


   # Enter password
   password_input = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/form/div[1]/div[2]/input")
   ActionChains(driver).move_to_element(password_input).click().perform()
   human_sleep(1, 2)
   password_input.send_keys(password)  # Replace with your password
   human_sleep(1, 3)


   # Submit the form
   login_button = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div/form/div[2]/input")
   ActionChains(driver).move_to_element(login_button).click().perform()
   human_sleep(3, 5)
  
   return driver


import re

def extract_price(input_string):
    # Regular expression to match the price pattern (e.g., "€ 1,79")
    price_pattern = r"€\s*\d+[.,]\d{2}"
    
    # Search for the price in the input string
    match = re.search(price_pattern, input_string)
    
    # Return the price if found, otherwise return None
    return match.group(0) if match else None


def run_eos(username, password, sheet):
    driver = init_eos(username, password)
    data = read_data(sheet)
    i = 2
    for e in data:
        print(e)
        # Step 2: Navigate to the desired page
        driver.get(f"https://eos.firstinfresh.be/shop/item/{e.get('GY-REF')}")
        human_sleep(2, 4)


        # Step 3: Scrape the required information
        #Try or skip
        
        try:
         vp_data_element = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[2]/div[6]/table/tbody/tr[4]/td[2]")
         scraped_data = vp_data_element.text
         scraped_data = extract_price(scraped_data)
         print(scraped_data)
         update_cell(sheet, i, VP_COL, scraped_data)
         data_element = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[2]/div[6]/table/tbody/tr[2]/td[2]")
         scraped_data = data_element.text
         print(scraped_data)
         update_cell(sheet, i, GREENYARD_PRICE_COL, scraped_data)
         ct = datetime.datetime.now()
         update_cell(sheet, i, LAST_UPDATE_COL, str(ct))
        except:
         print("Error")
         update_cell(sheet, i, GREENYARD_PRICE_COL, "Error")
         
        i+=1


    driver.quit()  



# SHEET WITH NAME "MARKET" AND "EXPRESS"
sheet_market = client.open('PRIX-GREENYARD').get_worksheet(0)
run_eos(GY_USERNAME_MARKET, GY_PASSWORD_MARKET, sheet_market)
# sheet_express.sort((PRIJS_VERSHIL_COL, 'des'))






