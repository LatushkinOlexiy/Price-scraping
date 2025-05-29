import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

current_dir = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
driver_dir = current_dir + "/chromedriver/chromedriver-win64/chromedriver.exe"

# Create broswer service + insert options so chrome runs headless and doesn't bother user
browser_service = Service(driver_dir)
healless_options = Options()
healless_options.add_argument('--headless')          # Runs Chrome in headless mode.
healless_options.add_argument('--disable-gpu')       # (Optional) for Windows compatibility
healless_options.add_argument('--window-size=1920,1080')  # Optional: ensure full page loads properly

# Function which is going to scrape prices from prom.ua
def scrape_cycle(prompt = ""):
    # Launch browser service
    page_driver = webdriver.Chrome(service=browser_service, options=healless_options)
    url = "https://prom.ua/"
    page_driver.get(url)
    time.sleep(2)
    # If prompt exists search for it on prom.ua (no prompt scenario is prob obsolete and needs to give an error)
    if (prompt != ""):
        site_input = page_driver.find_element(By.NAME, "search_term")
        site_input.send_keys(prompt)
        search_button = page_driver.find_element(By.XPATH, '//button[@data-qaid="search_btn"]')
        print(search_button.get_attribute("name"))
        search_button.click()
        print(site_input.get_attribute("name"))
        print(f"prompt is \"{prompt}\"")
    time.sleep(2)
    # Scrolls window down to load all 1st page items
    page_driver.execute_script("window.scrollTo(0, 1080)")
    time.sleep(2)
    # Tries to get all elements which contain product info and price
    try:
        global prod_names
        prod_names = page_driver.find_elements(By.CSS_SELECTOR, 'a[data-qaid="product_link"]')
    except:
        print("encountered an error")
        time.sleep(10)
    try:
        global prod_prices
        prod_prices = page_driver.find_elements(By.CSS_SELECTOR, '[data-qaid="product_price"]')
    except:
        print("encountered an error")
        time.sleep(10)
    print("scraping succesful")
    # Preparation for cycle which turns raw html objects into workable Pandas dataframe
    global i
    i = 0
    global prod_info
    prod_info = []
    colnames = {"name":[],"price":[],"link":[],"/kg":[]}
    prod_df = pd.DataFrame(colnames)
    # Preparation for quality control of items
    keyword_quality = prompt.split()
    passed_control = False
    for e in keyword_quality:
        e = e[:-1]

    # Cycle which pulls information from html objects and turns them into pd rows
    for prod in prod_names:
        passed_control = False
        product_name = prod.get_attribute('title')
        try:
            price = float(prod_prices[i].get_attribute('data-qaprice'))
        except:
            price = prod_prices[i].get_attribute('data-qaprice')
        new_prod = pd.DataFrame(colnames) 
        kgs_in_prod = get_dosage_from_name(product_name) # tries to get product dosage from item name to calculate per unit cost
        new_prod = [product_name,price,prod.get_attribute('href'),float(kgs_in_prod)]     
        #quality control
        for quality_word_check in keyword_quality:
            if quality_word_check in product_name.split():
                passed_control = True
                break

        if passed_control == True:
            prod_df.loc[len(prod_df)] = new_prod
        i = i + 1
    print("number of items: " + f"{len(prod_names)}")
    print("number of prices: " + f"{len(prod_prices)}")
    # adds pirce per kg columns, sorts them and returns dataframe
    prod_df['price per kg'] = prod_df["price"]/prod_df["/kg"]
    prod_df = prod_df.sort_values(by=['price per kg'])
    page_driver.close()
    print(prod_df.head())
    return(prod_df)

# recieves product name and processes it trying to get unit and amount (returns 0.1 if no unit is found)
def get_dosage_from_name(product_name):
    # tidies product name for following script
    product_name = product_name.replace("."," ")
    product_name = product_name.replace(")"," ")
    product_name = product_name.replace("("," ")
    product_name = product_name.replace(","," ")
    product_name = product_name.replace("kg","кг")
    product_name = product_name.replace("mg","мг")
    product_name = product_name.replace("g","г")
    product_name = product_name.replace("мл","г")
    product_name = product_name.replace("л","кг")
    product_name = product_name + " "
    dosage = 1.0
    quantity = 1.0
    # tries to read the unit
    if " г " in product_name:
        quantity = 0.001
    if "0г" in product_name:
        quantity = 0.001
        unit_index = product_name.index("0г")
        product_name = product_name[:unit_index+1] + " " + product_name[unit_index+1:]
    if "5г" in product_name:
        quantity = 0.001
        unit_index = product_name.index("5г")
        product_name = product_name[:unit_index+1] + " " + product_name[unit_index+1:]
    if " мг " in product_name:
        quantity = 0.001 * 0.001
    if "0мг" in product_name:
        quantity = 0.001 * 0.001
        unit_index = product_name.index("0мг")
        product_name = product_name[:unit_index+1] + " " + product_name[unit_index+1:]
    if "5мг" in product_name:
        quantity = 0.001 * 0.001
        unit_index = product_name.index("5мг")
        product_name = product_name[:unit_index+1] + " " + product_name[unit_index+1:]
    if " кг " in product_name:
        quantity = 1
    if "0кг" in product_name:
        quantity = 1
        unit_index = product_name.index("0кг")
        product_name = product_name[:unit_index+1] + " " + product_name[unit_index+1:]
    if "5кг" in product_name:
        quantity = 1
        unit_index = product_name.index("5кг")
        product_name = product_name[:unit_index+1] + " " + product_name[unit_index+1:]
    # tries to get the dosage
    prodnamelist = product_name.split()
    try:
        unit_number = prodnamelist.index("г")
    except:
        try:
            unit_number = prodnamelist.index("кг")
        except:
            try:
                unit_number = prodnamelist.index("л")
            except:
                return(0.1)
    
    dosage = prodnamelist[unit_number-1]
    result = float(dosage)*quantity
    return(result)


#print(f"the /kg is {get_dosage_from_name('Сульфат магнію (магній сірчанокислий) 500г.')}")
if __name__ == "__main__":
    e = 1
    print(scrape_cycle("калій фосфат").head())

