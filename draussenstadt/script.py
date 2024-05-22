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
# from clean_json_data import clean



def get_links(driver,url,output_file):
    driver.get(url)
    time.sleep(10)
    while True:
        try:
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".dsb-events-list-button")))
            next_button.click()
            time.sleep(5)
        except:
            break
    # links = driver.find_elements(By.CSS_SELECTOR,".dsb-events-list-list hylo-router-link a")
    cards = driver.find_elements(By.CSS_SELECTOR,".dsb-events-list-list hylo-router-link")


    with open(output_file,'w',encoding='utf-8') as f:
        for card in cards:
            link = card.find_element(By.CSS_SELECTOR,'a').get_attribute('href')
            event_image = card.find_element(By.CSS_SELECTOR,'dsb-card-event').get_attribute('image-xl-lg')
            f.write(f"{link};{event_image}\n")
    print("Links scraped")

def get_data_from_link(driver,link):
    driver.get(link)
    time.sleep(1)
    event_name = ""   
    additional_date = ""
    categories = ""
    location = ""
    location_adress = ""
    geo_location = ""
    description = ""
    prices = ""
    website = ""
    
    # try:
    #     categories = driver.find_element(By.CSS_SELECTOR, ".dsb-event-category").text
    # except Exception as e:
    #     categories = ""
    # time.sleep(1)

    # try:
    #     event_name = driver.find_element(By.CSS_SELECTOR, ".dsb-event-top h1").text
    # except Exception as e:
    #     event_name = ""
    
    # time.sleep(1)

    # try:
    #     event_organizer = driver.find_element(By.CSS_SELECTOR, ".dsb-event-top h2").text
    # except Exception as e:
    #     event_organizer = ""
    # time.sleep(1)

    # try:
    #     dates_times_el = driver.find_elements(By.CSS_SELECTOR, '.dsb-event-top-date time')
    #     dates_times = []
    #     for el in dates_times_el:
    #         dates_times.append({"date":el.get_attribute("datetime"),"text":el.text})

    # except Exception as e:
    #     dates_times = []
    # time.sleep(1)

    # try:
    #     location = driver.find_element(By.CSS_SELECTOR, '.dsb-event-top-venue').text
    # except Exception as e:
    #     location = ""
    # time.sleep(1)
    
    sections = driver.find_elements(By.CSS_SELECTOR,'.dsb-event-sections .section')

    
    for section in sections:
        section_name = section.find_element(By.CSS_SELECTOR,'.page-menu-item').get_attribute("data-name")
        if section_name == "Info":
            try:
                description = section.find_element(By.CSS_SELECTOR, '.section-content > p').text
                # website = section.find_element(By.CSS_SELECTOR, '.section-content .section-info-website a').get_attribute("href")
            except:
                description = ""
                # website = ""
        if section_name == "Ort":
            try:
                location_adress = section.find_element(By.CSS_SELECTOR, '.section-content > p').text
                geo = section.find_element(By.CSS_SELECTOR,'.section hylo-map-location')
                geo_location = f"{geo.get_attribute('latitude')},{geo.get_attribute('longitude')}"
            except Exception as e:
                location_adress = ""
                geo_location = ""
        elif section_name == "Tickets":
            if "Eintritt frei" in section.text:
                prices = "Eintritt frei"
            else:
                try:
                    prices_spans = section.find_elements(By.CSS_SELECTOR, '.section-tickets-price span')
                    prices = []
                    for price in prices_spans:
                        prices.append(price.text)
                except Exception as e:
                    prices = ""
    
    event = {
        "location_adress":location_adress,
        "geo_location":geo_location,
        "description":description,
        "ticket_prices":prices
    }
  
    return event

def get_data_from_links(driver,input_file,output_file):
    events = []
    with open(input_file,"r",encoding="utf-8") as f:
        data = json.load(f)

    

    for index,event in enumerate(data[:101]):
        print(f"Loading {index+1}/{len(data)}")
        driver.get(event["link"])
        time.sleep(2)

        sections = driver.find_elements(By.CSS_SELECTOR,'.dsb-event-sections .section')
        for section in sections:
            section_name = section.find_element(By.CSS_SELECTOR,'.page-menu-item').get_attribute("data-name")
            if section_name == "Info":
                try:
                    event["description"] = section.find_element(By.CSS_SELECTOR, '.section-content > p').text
                except:
                    event["description"] = ""
            if section_name == "Ort":
                try:
                    event["locationText"] = section.find_element(By.CSS_SELECTOR, '.section-content > p').text
                except Exception as e:
                    event["locationText"] = None
                try:
                    geo = section.find_element(By.CSS_SELECTOR,'.section hylo-map-location')
                    event["geoLocation"] = f"{geo.get_attribute('latitude')},{geo.get_attribute('longitude')}"
                except Exception as e:
                    event["geoLocation"] = None
            elif section_name == "Tickets":
                if "Eintritt frei" in section.text:
                    event["price"] = "Eintritt frei"
                else:
                    try:
                        prices_spans = section.find_elements(By.CSS_SELECTOR, '.section-tickets-price span')
                        prices = []
                        for price in prices_spans:
                            prices.append(price.text)
                        event["price"] = "\n".join(prices)
                    except Exception as e:
                        event["price"] = None
        print(event)
        events.append(event)

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)


def get_data_00(driver,url,output_file):
    driver.get(url)
    time.sleep(10)
    events = []
    while True:
        try:
            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".dsb-events-list-button")))
            next_button.click()
            time.sleep(5)
        except:
            break
    # links = driver.find_elements(By.CSS_SELECTOR,".dsb-events-list-list hylo-router-link a")
    cards = driver.find_elements(By.CSS_SELECTOR,".dsb-events-list-list hylo-router-link")



    for card in cards:
        event={}
        event["link"] = card.find_element(By.CSS_SELECTOR,'a').get_attribute('href')
        event["title"] = card.find_element(By.CSS_SELECTOR,".dsb-card-event-main-top h2").text
        event["categories"] = card.find_element(By.CSS_SELECTOR,".dsb-card-event-category").text
        event["start_date"] = card.find_element(By.CSS_SELECTOR,"dsb-card-event").get_attribute("start-date") 
        event["end_date"] = card.find_element(By.CSS_SELECTOR,"dsb-card-event").get_attribute("end-date") 
        print(event)
        events.append(event)

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    chrome_options = ChromeOptions()
    chrome_options.headless = False
    with Chrome(options=chrome_options) as driver:
        # get_data_00(driver,"https://www.draussenstadt.berlin/de/kalender/","00draussenstadt.json")
        get_data_from_links(driver,"00draussenstadt.json","01draussenstadt.json")



# venue
# address
# zipCode city