from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
import os
import math
import requests
import random
# from utils import *
import pyautogui
import json
import re
import collections
import os

# from clean_json_data import clean
chrome_options = ChromeOptions()
chrome_options.headless = False


CURRENT_DIR = os.path.dirname(__file__)


def get_links(driver,output_file):
    # categories = ["ausstellung","bewegung","theater","ferienkurse","fest","kino-film-events","flohmarkt","museum","outdoor","potsdam","sonstiges","natur","umgebung","weihnachtsmarkte","technik","workshop"]
    # categories = ["ausstellung","bewegung","outdoor"]
    categories = ["bewegung"]

    events = collections.defaultdict(list)
    for category in categories:
        print(f"Scraping {category}...")
        url = f"https://berlinmitkind.de/veranstaltungskalender/?rubrik%5B%5D={category}&ort=&suche="
        driver.get(url)
        while True:
        
            cards = driver.find_elements(By.CSS_SELECTOR,".events .em-event")
            print(len(cards))
            with open(output_file,'a',encoding='utf-8') as f:
                for card in cards:
                    title = card.find_element(By.CSS_SELECTOR,".entry-title a").text
                    link = card.find_element(By.CSS_SELECTOR,".entry-title a").get_attribute('href')
                    if title not in events:
                        events[title] = {
                            "categories":[],
                            "link":""
                        }
                        f.write(f"{link};{category}\n")
                    if category not in events[title]["categories"]:
                        events[title]["categories"].append(category)
                        events[title]["link"] = link
                    
            
            try:
                driver.find_element(By.CSS_SELECTOR,"a.next")
            except:    
                break

            try:
                js_click = """
                var element = document.querySelector('a.next');
                if (element) {
                    element.click();
                }
                """
                driver.execute_script(js_click)
                time.sleep(5)
            except Exception as e:
    
                break
    
    with open("00berlinmitkind.json", 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)

def combine_categories(input_file):
    events = {}
    with open(input_file,'r',encoding='utf-8') as events_file:
        for row in events_file:
            link, category = row.split(";")
            if link not in events:
                events[link] = set()
            events[link].add(category.replace("\n",""))
    print(events)
    # with open(input_file,'w',encoding='utf-8') as _file:
    #     for key,value in events.items():
    #         # print(key,value)
    #         categories = ";".join(list(value))
    #         _file.write(f"{key};{categories}\n")




def get_data_from_link(driver,link,categories):
    driver.get(link)
    time.sleep(1)
    try:
        title = driver.find_element(By.CSS_SELECTOR, '.entry-header .entry-title').text
    except Exception as e:
        print("no title")
        title = None

    try:
        dates = []
        date1 = driver.find_element(By.CSS_SELECTOR, '.em-list-header').text
        dates.append(date1)
        additional_dates_el = driver.find_elements(By.CSS_SELECTOR,'.more-events p')
        
        for date in additional_dates_el:
            dates.append(date.text)
    except Exception as e:
        print("no dates")
        dates = None
    
    try:
        location = driver.find_element(By.CSS_SELECTOR, '.local-info ').text
    except Exception as e:
        print("no location")
        location = None
    
    try:
        description = driver.find_element(By.CSS_SELECTOR, '.excerpt').text
    except Exception as e:
        print("no dates")
        description = None
    
    try:
        iframe = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe.em-location-map')))
        driver.switch_to.frame(iframe)
        geo_location_element = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.google-maps-link a')))
        geo_location = geo_location_element.get_attribute('href')
        driver.switch_to.default_content()
    except Exception as e:
        print("no geolocation")
        driver.switch_to.default_content()
        geo_location = None
    
    event = {
        "title":title,
        "dates":dates,
        "categories":",".join(categories),
        "locationText":location,
        "geoLocation":geo_location,
        "description":description,
        "price":None,
        "source":"berlinmitkind",
        "link":link,
    }
    
    return event
            
def get_data_from_links(driver,input_file,output_file):
    events = []
    count = 0
    with open(input_file,"r",encoding="utf-8") as f:
        data = json.load(f)
    
    for key in data.keys():
        if count == 101:
            break
        print(f"Loading {count}")
        count+=1
        link = data[key]["link"]
        categories = data[key]["categories"]

        event = get_data_from_link(driver,link,categories)
        events.append(event)
        
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    with Chrome(options=chrome_options) as driver:
        # get_links(driver,f"00berlinmitkind.txt")
        # combine_categories("00berlinmitkind.txt")
        get_data_from_links(driver,"00berlinmitkind.json","01berlinmitkind.json")
