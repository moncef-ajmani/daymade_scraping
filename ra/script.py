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

def auto_scroll(driver):
    # Get the initial page height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Define the duration of the scroll in seconds (e.g., 5 seconds)
    scroll_duration = 5

    # Define the number of intervals for the scroll
    num_intervals = 100  # Adjust as needed
    while True:
        # Smoothly scroll down the page
        page_height = driver.execute_script("return document.body.scrollHeight")
        scroll_distance = page_height / num_intervals
        for _ in range(num_intervals):
            driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
            time.sleep(scroll_duration / num_intervals)

        # Wait for a short period to allow new content to load (you can adjust the time)
        time.sleep(5)

        # Get the new page height after scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")

        # Check if we have reached the end of the page
        if new_height == last_height:
            break

        # Update the last height
        last_height = new_height


def get_links(driver,url,output_file):
    driver.get(url)
    time.sleep(10)
    links = []

    try:

        # Get the initial page height
        last_height = driver.execute_script("return document.body.scrollHeight")

        # Define the duration of the scroll in seconds (e.g., 5 seconds)
        scroll_duration = 5

        # Define the number of intervals for the scroll
        num_intervals = 100  # Adjust as needed
        while True:
            links = driver.find_elements(By.CSS_SELECTOR,".fgZjqQ .gbSlff > a")
            print(len(links))
            
            with open(output_file,'a',encoding='utf-8') as f:
                for link in links:
                    link = link.get_attribute('href')
                    f.write(f"{link}\n")

            # Smoothly scroll down the page
            page_height = driver.execute_script("return document.body.scrollHeight")
            scroll_distance = page_height / num_intervals
            for _ in range(num_intervals):
                driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(scroll_duration / num_intervals)

            # Wait for a short period to allow new content to load (you can adjust the time)
            time.sleep(5)

            # Get the new page height after scrolling
            new_height = driver.execute_script("return document.body.scrollHeight")

            # Check if we have reached the end of the page
            if new_height == last_height:
                break

            # Update the last height
            last_height = new_height

        try:
            next_button = driver.find_element(By.CSS_SELECTOR,".WtJet a")
            next_button.click()
        except:
            pass
    except:
        pass


        


def get_data_from_link(driver,link):
    # print(driver.page_source)
   
    # try:
    #     eventname = driver.find_element(By.CSS_SELECTOR, '.kLTSYd').text.replace("\n"," ")
    # except Exception as e:
    #     print("event_name")
    #     eventname = ""
    
    # try:
    #     dates = driver.find_element(By.CSS_SELECTOR, ".fsWAfG").text.replace("\n"," ")
        
    # except Exception as e:
    #     print("dates")
    #     dates = ""
    
    
    # try:
    #     location_name = driver.find_element(By.CSS_SELECTOR, 'span[data-pw-test-id="event-venue-link"]').text.replace("\n"," ")
    # except Exception as e:
    #     print("location_name")
    #     location_name = ""
       
    # try:
    #     location_adress = driver.find_element(By.CSS_SELECTOR, '.jCDohq').text.replace("\n"," ")
    # except Exception as e:
    #     print("location_adress")
    #     location_adress = ""
    
    
    
    # try:
    #     description = ""
    #     description = driver.find_element(By.CSS_SELECTOR, '.dSbrUc').text
        
    #     lineup = ", ".join([x.text for x in driver.find_elements(By.CSS_SELECTOR,'div[data-tracking-id="event-detail-lineup"] a')])
    #     description+="\nLINEUP\n\n"+lineup
        
    # except Exception as e:
    #     print("description - lineup")
    #     description = ""
    # time.sleep(1)

    # try:
    #     iframe = driver.find_element(By.XPATH, '//iframe[@id="#tickets-iframe-m"]')
    #     driver.switch_to.frame(iframe)

    #     prices_el = driver.find_elements(By.CSS_SELECTOR, '#ticket-types li')  # Replace with the actual XPath
    #     prices = []
    #     for price in prices_el:
    #         prices.append(price.text)
    #     ticket_prices = " ".join(prices)
    # except Exception as e:
    #     print("prices")
    #     ticket_prices = ""
    try:
        categories = ",".join([category.text for category in driver.find_elements(By.CSS_SELECTOR, '.bKhJyQ')])
    except Exception as e:
        print("categories")
        categories = None
        
    try:
        cost = driver.find_element(By.CSS_SELECTOR, '.kZveGy .hmnVrp').text
    except Exception as e:
        print("Cost")
        cost = None
    
    try:
        script_element = driver.find_elements(By.CSS_SELECTOR,"script[type='application/ld+json']")[0]
        data_script = json.loads(script_element.get_attribute("innerHTML"))
        print(data_script)
    except Exception as e:
        print(e)
        data_script = None

    try:
        title = data_script["name"]
    except:
        title = None
    
    try:
        description = data_script["description"]
    except:
        description = None
    
    try:
        startDate = data_script["startDate"]
    except:
        startDate = None
    
    try:
        endDate = data_script["endDate"]
    except:
        endDate = None
    
    try:
        price = data_script["offers"]["price"]
    except:
        price = None
    
    try:
        venue = data_script["location"]["name"]
    except:
        venue = None
    
    try:
        locationText = data_script["location"]["address"]["streetAddress"]
    except:
        locationText = None

    event = {
        "title":title,
        "startDate":startDate,
        "endDate":endDate,
        "categories":categories,
        "venue":venue,
        "locationText":locationText,
        "description":description,
        "price":price,
        "source":"ra",
        "link":link,
        "cost":cost
    }
    print("=======================================================")
    time.sleep(2)
    return event

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0"
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"

]

# Choose a random user agent
random_user_agent = random.choice(user_agents)

def get_data_from_links(input_file,output_file):
    events = []
    count = 1
    with open(input_file,"r",encoding='utf-8') as f:
        for event_link in f:
            if count == 101:
                break
            if count%50 == 0:
                with open(f"{count}.json", 'w', encoding='utf-8') as file_:
                    json.dump(events, file_, ensure_ascii=False, indent=4)
            event_link = event_link.replace('\n',"")
            print(f"Loading {count} - Source: {event_link}")
            count+=1
            
            try:
                chrome_options = ChromeOptions()
                chrome_options.headless = False
                # chrome_options.add_argument(f"user-agent={random_user_agent}")
                driver = Chrome(options=chrome_options)
                driver.get(event_link)
                time.sleep(1)
                event = get_data_from_link(driver,event_link)
                events.append(event)
                driver.close()
            except Exception as e:
                print("links",e)
                
            
    
    with open(output_file, 'w', encoding='utf-8') as file_:
        json.dump(events, file_, ensure_ascii=False, indent=4)


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

if __name__ == "__main__":
    chrome_options = ChromeOptions()
    chrome_options.headless = False
    with Chrome(options=chrome_options) as driver:
        get_links(driver,"https://de.ra.co/events/de/berlin","00ra.txt")
        remove_duplicated_rows_from_file("00ra.txt")
    get_data_from_links("00ra.txt","01ra.json")
        
    # driver.close()
    