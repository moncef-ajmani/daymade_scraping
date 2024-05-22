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
from bs4 import BeautifulSoup
# from clean_json_data import clean
import sys
sys.path.append('../../../')

import os
CURRENT_DIR = os.path.dirname(__file__)


def get_links(driver,url,output_file_path):
    driver.get(url)
    time.sleep(5)
    count = 1 
    events = []
    while True:
        print(f"Loading {count}")
        titles = driver.find_elements(By.CSS_SELECTOR,".modul-accordion .title")
        accordions = driver.find_elements(By.CSS_SELECTOR,".modul-accordion .js-accordion")
        for i in range(0,len(titles)):
            location_name = titles[i] 
            accordion = accordions[i]
            sous_accordion = accordion.find_elements(By.CSS_SELECTOR,"li")
            
            for sa in sous_accordion:
                try:
                    sa.click()
                    time.sleep(3)
                    event_name = sa.find_element(By.CSS_SELECTOR,".js-accordion__heading").text
                    datetimes = sa.find_elements(By.CSS_SELECTOR,"tr")[1:]
                    dates = []
                    for datetime in datetimes:
                        date_,time_ = datetime.find_elements(By.CSS_SELECTOR,"td")
                        datetime_str = f"{date_.text} {time_.text}"
                        if datetime_str == "":
                            print(f"Page: {count} => Empty")
                        dates.append(datetime_str)
                    event_url,cenima_url = sa.find_elements(By.CSS_SELECTOR,"a")

                    event = {
                        "title":event_name,
                        "dates":dates,
                        "location_name":location_name.text,
                        "event_url":event_url.get_attribute("href"),
                        "cenima_url":cenima_url.get_attribute("href")
                    }
                    events.append(event)
                except:
                    pass
        try:
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".pagination li:last-child a")))
            next_button.click()
            time.sleep(1)
            count+=1
        except:
            break

    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)
    

def get_data_event(driver,input_file,output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    events = []
    for index,event in enumerate(data):
        if index+1 == 101:
            break
        print(f"Loading {index+1}/{len(data)}")
        event_url = event["event_url"]
        driver.get(event_url)
        time.sleep(1)
        try:
            event_image = driver.find_element(By.CSS_SELECTOR,".swiper-slide-active img").get_attribute("src")
            time.sleep(0.5)
        except:
            event_image = None
        try:
            description = driver.find_element(By.CSS_SELECTOR,"#layout-grid__area--maincontent > p").text
            time.sleep(0.5)
        except:
            description = None
        try:
            deep_link = driver.find_element(By.CSS_SELECTOR, ".article-attributes dd a").get_attribute("href")
        except:
            deep_link = None
        try:
            attributes = driver.find_element(By.CSS_SELECTOR, ".article-attributes dl").text.replace("\n",",")
            # Use regular expressions to find the genre and time information
            genre_match = re.search(r'Genre:,(.*?),', attributes)
            time_match = re.search(r'Länge:,(.*?),', attributes)

            # Check if the matches were found
            if genre_match and time_match:
                genre = genre_match.group(1).strip()
                duree = time_match.group(1).strip()
            else:
                genre = None
                duree = None
        except:
            genre = None
            duree = None
            
        event["event_image"] = event_image
        event["description"] = description
        event["deep_link"] = deep_link
        event["categories"] = genre
        event["duree"] = duree
        events.append(event)
        print(event)
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)


def get_data_cinema(driver,input_file,output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    events = []

    for index,event in enumerate(data):
        print(f"Loading {index+1}/{len(data)}")
        cenima_url = event["cenima_url"]
        driver.get(cenima_url)
        time.sleep(1)
        try:
            location_adress = driver.find_element(By.CSS_SELECTOR,".article-attributes dd").text.replace("Stadtplan","")
            time.sleep(0.5)
        except:
            location_adress = ""
        
        try:
            ticket_prices = driver.find_element(By.CSS_SELECTOR,".article-attributes .block").text
            time.sleep(0.5)
        except:
            ticket_prices = ""
        # print(location_adress)
        # print(ticket_prices)
        # print("=============")
        event["location_adress"] = location_adress
        event["ticket_prices"] = ticket_prices
        event["geo_location"] = ""
        print(event)
        events.append(event)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    chrome_options = ChromeOptions()
    chrome_options.headless = False
    webite_name = "berkin-kino"
    url_links = "https://www.berlin.de/kino/_bin/trefferliste.php?freitext=&kino=&datum=&genre=&stadtteil=&suche=1"
    # clean_links_path = f"links_{webite_name}.txt"
    txt_file_path = f"{webite_name}.txt"
    json_file_path = f"{webite_name}.json"
    clean_json_file_path = f"clean_{webite_name}.json"

    with Chrome(options=chrome_options) as driver:
        get_links(driver,url_links,f"00berlinkino.json")
        get_data_event(driver,"00berlinkino.json","output.json")
        get_data_cinema(driver,"output.json","01berlinkino.json")

# From the last Sunday in October to the last Sunday in March, the time zone is UTC+1 (CET).
#     From the last Sunday in March to the last Sunday in October, the time zone is UTC+2 (CEST).