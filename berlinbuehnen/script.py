from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
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
from concurrent.futures import ThreadPoolExecutor

import os
CURRENT_DIR = os.path.dirname(__file__)

def remove_duplicated_rows_from_file(file_path):
    # Initialize a set to store unique rows
    unique_rows = set()

    # Read the input file, remove duplicates, and store unique rows
    with open(file_path, 'r') as input_file:
        for line in input_file:
            row = line.strip()
            if row not in unique_rows:
                unique_rows.add(row)

    # Write unique rows back to the input file, overwriting it
    with open(file_path, 'w') as output_file:
        for row in unique_rows:
            output_file.write(row + '\n')

    print(f'Removed duplicates and saved unique rows to {file_path}')

def get_links(driver,url,output_file_path):
    driver.get(url)
    time.sleep(5)
    i = 0
    links = []
    while True:
        print(f"Loading {i}")
        i+=1
        try:
            time.sleep(1)
            cards = driver.find_elements(By.CSS_SELECTOR,"hylo-page-width hylo-router-link[role='listitem']")
            
            for card in cards:
                link = f"https://www.berlin-buehnen.de{card.get_attribute('href')}\n"
                links.append(link)

            next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'.bb-page-list-body .hylo-button')))
            actions = ActionChains(driver)

            # Move the mouse pointer to the button to simulate hover
            actions.move_to_element(next_button).perform()

            next_button.click()
            time.sleep(5)
        except Exception as e:
            print(e)
            break
    with open(output_file_path,'w',encoding='utf-8') as f:
        for link in links:
            f.write(link)

def get_data_from_link(driver,link):    
    try:
        location_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#event_detail_venue hylo-accordion-item-header")))
        location_button.click()
    except Exception:
        print("Location button not found. Continuing without clicking.")
    time.sleep(1)
    try:
        tickets_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#event_detail_tickets hylo-accordion-item-header")))
        tickets_button.click()
    except Exception:
        print("Tickets button not found. Continuing without clicking.")
    time.sleep(1)
    
    try:
        tickets_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".more-button")))
        tickets_button.click()
    except:
        pass
    time.sleep(1)
    try:
        categories = driver.find_element(By.XPATH, '//*[@id="event_detail_info"]/div[1]/div/div[1]').text
    except Exception as e:
        print("no categories")
        categories = ""
    # time.sleep(1)
    try:
        event_name = driver.find_element(By.CSS_SELECTOR, 'hylo-page-width h1').text.replace("\n"," ")
    except Exception as e:
        print("no title")
        event_name = ""

    # time.sleep(1)
    try:
        dates_el = driver.find_elements(By.CSS_SELECTOR, '#event_detail_dates .tw-grid')
        dates = []
        for date in dates_el:
            dates.append(date.text.replace("\nTICKETS","").replace("\n"," - "))
    except Exception as e:
        print("no dates")
        dates = ""
    # time.sleep(1)
    try:
        location_name = driver.find_element(By.CSS_SELECTOR,"#event_detail_venue h5").text
    except:
        location_name = ""
        print("no location")

    try:
        location_adress = driver.find_element(By.CSS_SELECTOR,"#event_detail_venue").text
    except:
        print("no address")
        location_adress = ""
    # time.sleep(1)
    try:
        ticket_prices = driver.find_element(By.CSS_SELECTOR,"#event_detail_tickets hylo-accordion-item-body").text
    except:
        print("price")
        ticket_prices = ""
    # time.sleep(1)
    try:
        description_p = driver.find_elements(By.CSS_SELECTOR,".tw-font-secondary p")
        description = ""
        for p in description_p:
            description+= p.text
    except:
        description = ""
    
    event = {
        "eventname":event_name,
        "dates":dates,
        "categories":categories.replace("\n",", "),
        "location_name":location_name,
        "location_adress":location_adress,
        "geo_location":None,
        "description":description,
        "prices":ticket_prices,
        "source":"berlinbuehnen",
        "event_url":link.replace("\n","")
    }
    return event

def get_data_from_links(driver,input_file,output_file):
    events = []
    count = 1
    with open(input_file,'r',encoding='utf-8') as links:
        # links = json.load(f)

        for link in links:
            try:
                if count == 101:
                    break
                if count%100 == 0:
                    with open(f"data/{count}.json", 'w', encoding='utf-8') as file:
                        json.dump(events, file, ensure_ascii=False, indent=4)
                    break
                print(f"Loading {count}")
                count+=1
                driver.get(link)
                time.sleep(1)
                # event = get_data_from_link(driver,link)
                # try:
                #     location_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#event_detail_venue hylo-accordion-item-header")))
                #     location_button.click()
                # except Exception:
                #     print("Location button not found. Continuing without clicking.")
                # time.sleep(1)

                script_element = driver.find_element(By.CSS_SELECTOR,"script[type='application/ld+json']")	
                data_script = json.loads(script_element.get_attribute("innerHTML"))
                print(data_script)

                try:
                    address = data_script["location"]["address"]["streetAddress"]
                except:
                    address = None
                
                try:
                    city = data_script["location"]["address"]["addressLocality"]
                except:
                    city = None
                
                try:
                    zipCode = data_script["location"]["address"]["postalCode"]
                except:
                    zipCode = None
                
                try:
                    venue = data_script["location"]["name"]
                except:
                    venue = None
                
                try:
                    description = data_script['description']
                except:
                    description = None
                    

                try:
                    tickets_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#event_detail_tickets hylo-accordion-item-header")))
                    tickets_button.click()
                except Exception:
                    print("Tickets button not found. Continuing without clicking.")
                time.sleep(1)
                
                try:
                    tickets_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".more-button")))
                    tickets_button.click()
                except:
                    pass
                time.sleep(1)
                try:
                    categories = driver.find_element(By.XPATH, '//*[@id="event_detail_info"]/div[1]/div/div[1]').text
                except Exception as e:
                    print("no categories")
                    categories = None
                # time.sleep(1)
                try:
                    event_name = driver.find_element(By.CSS_SELECTOR, 'hylo-page-width h1').text.replace("\n"," ")
                except Exception as e:
                    print("no title")
                    event_name = None

                # time.sleep(1)
                

                # try:
                #     locationText = driver.find_element(By.CSS_SELECTOR,"#event_detail_venue").text
                # except:
                #     print("no address")
                #     locationText = None
                # time.sleep(1)
                try:
                    ticket_prices = driver.find_element(By.CSS_SELECTOR,"#event_detail_tickets hylo-accordion-item-body").text
                except:
                    print("price")
                    ticket_prices = None
                # time.sleep(1)
                # try:
                #     description_p = driver.find_elements(By.CSS_SELECTOR,".tw-font-secondary p")
                #     description = ""
                #     for p in description_p:
                #         description+= p.text
                # except:
                #     description = None
                try:
                    # script_content = driver.execute_script("return document.querySelector('script[type=\"application/ld+json\"]').innerText")
                    # script_data = json.loads(script_content)
                    # print(script_data)
                    dates_el = driver.find_elements(By.CSS_SELECTOR, '#event_detail_dates .tw-grid')
                    for date in dates_el:
                        date_link  = date.find_element(By.CSS_SELECTOR,"hylo-router-link").get_attribute("href")
                        date_str = date.text.replace("\nTICKETS","")
                        event = {
                            "title":event_name,
                            "date":date_str.replace("\n"," "),
                            "categories":categories.replace("\n",","),
                            "venue":venue,
                            "address":address,
                            "city":city,
                            "zipCode":zipCode,
                            "description":description,
                            "price":ticket_prices.replace("\nTickets",""),
                            "source":"berlinbuehnen",
                            "link":f"https://www.berlin-buehnen.de{date_link}"
                        }
                        events.append(event)
                        
                except Exception as e:
                    print(e)
                    dates = ""
            except:
                pass
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)


def get_data_from_links_01():
    pass


def clean_links(input_file,output_file):
    links = set()
    with open(input_file,"r",encoding="utf-8") as f:
        for row in f:
            link = row.split("/events")[0]
            print(link)
            links.add(link)
    
    links_dict = [{"link":link} for link in links]

    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(links_dict, json_file, indent=4)

    


if __name__ == "__main__":
    # clean_links("00berlinbuehnen.txt","links.json")
    chrome_options = ChromeOptions()
    chrome_options.headless =  False
    with Chrome(options=chrome_options) as driver:
        get_links(driver,"https://www.berlin-buehnen.de/de/spielplan/",f"00berlinbuehnen.txt") # Phase 1
        remove_duplicated_rows_from_file("00berlinbuehnen.txt")
        get_data_from_links(driver,"00berlinbuehnen.txt","01berlinbuehnen.json") # Phase 1
        # get_data_from_links_01("01berlinbuehnen.json","02berlinbuehnen.json")

# def close_cookie(driver):
#     cookie_btn = driver.find_element(By.CSS_SELECTOR,".hylo-cookie-banner-accept")
#     if cookie_btn:
#         cookie_btn.click()
# def scrape_event_data(link):
#     try:
#         chrome_options = ChromeOptions()
#         with Chrome(options=chrome_options) as driver:
#             driver.get(link)
#             time.sleep(1)
            
#             close_cookie(driver)
#             event = get_data_from_link(driver, link)
#             print(event["event_url"])
#         return event
#     except Exception as e:
#         print(f"Error scraping data from {link}: {e}")
#         return None
#     finally:
#         try:
#             driver.quit()
#         except NameError:
#             pass  # Handle the case where 'driver' is not defined

# def get_data_from_links_parallel(input_file, output_file):
#     events = []
#     with open(input_file, 'r', encoding='utf-8') as events_file:
#         links = [link.strip() for link in events_file]

#     with ThreadPoolExecutor(max_workers=5) as executor:
#         events = list(executor.map(scrape_event_data, links))

#     # Remove None values (failed scrapes) from the list
#     events = [event for event in events if event is not None]

#     with open(output_file, 'w', encoding='utf-8') as file:
#         json.dump(events, file, ensure_ascii=False, indent=4)

# if __name__ == "__main__":
#     chrome_options = ChromeOptions()

#     with Chrome(options=chrome_options) as driver:
#         get_links(driver, "https://www.berlin-buehnen.de/de/spielplan/", "00berlinbuehnen.txt")
# #         # remove_duplicated_rows_from_file("00berlinbuehnen.txt")
# #         get_data_from_links_parallel("00berlinbuehnen.txt", "01berlinbuehnen.json")