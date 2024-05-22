from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time 
# from utils import *
import json
from selenium.common.exceptions import NoSuchElementException
import json
import re


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
    auto_scroll(driver)
    links = driver.find_elements(By.CSS_SELECTOR,".activity-list__activiti__title")
    with open(output_file,'a',encoding='utf-8') as f:
        for link in links:
            f.write(f"{link.get_attribute('href')}\n")



def get_data_from_link(driver,link):
    try:
        hashtags = [el.text for el in driver.find_elements(By.CSS_SELECTOR, ".category-tags .category-tag")]
    except NoSuchElementException:
        hashtags = []

    try:
        title = driver.find_element(By.CSS_SELECTOR, ".activity__description__header").text
    except NoSuchElementException:
        title = None

    try:
        description = driver.find_element(By.CSS_SELECTOR, ".activity__description__body").text 
    except NoSuchElementException:
        description = None

    try:
        dates_el = driver.find_elements(By.CSS_SELECTOR, ".activity-booking__date div")
        dates = ";".join([date.text for date in dates_el if date.text != ""])
    except NoSuchElementException:
        dates = None


    try:
        prices = " ; ".join([el.text.replace("\n"," ") for el in driver.find_elements(By.CSS_SELECTOR, ".activity-booking__price__info")])
    except NoSuchElementException:
        prices = None

    try:
        location_adress = driver.find_element(By.CSS_SELECTOR, ".activity__org-info__location__address").text
    except NoSuchElementException:
        location_adress = None
    
    try:
        location_name = driver.find_element(By.CSS_SELECTOR, ".activity__org-info__locations__list li > div").text
    except NoSuchElementException:
        location_name = None


    try:
        geo_location = driver.find_element(By.CSS_SELECTOR, ".activity__org-info__map").get_attribute("href").split("/")[5].replace("'","")
    except NoSuchElementException:
        geo_location = None

    event = {
        "title":title,
        "dates":dates,
        "hashtags":hashtags,
        "location_name":location_name,
        "location_adress":location_adress,
        "geo_location":geo_location,
        "description":description,
        "price":prices,
        "link":link.replace("\n",""),
        "source":"kindaling"
    }
    return event

def scrape_from_links(driver,input_file,output_file):
    url = "https://www.kindaling.de/tiere-natur/erlebe-den-zauber-des-selbstpflueckens-auf-unserem-apfelhof/wesendahl"
    driver.get(url)
    time.sleep(10)
    events = []
    count = 1
    with open(input_file,'r',encoding='utf-8') as events_file:
        for link in events_file:
            if count == 101:
                break
            driver.get(link)
            time.sleep(5)

            print(f"Loading {count}")
            count+=1

            event = get_data_from_link(driver,link)
            events.append(event)


    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)
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
if __name__ == "__main__":
    chrome_options = ChromeOptions()
    chrome_options.headless = False
    with Chrome(options=chrome_options) as driver:
        get_links(driver,"https://www.kindaling.de/veranstaltungen/berlin?view=block","00kindaling.txt")
        remove_duplicated_rows_from_file("00kindaling.txt")
        scrape_from_links(driver,"00kindaling.txt","01kindaling.json")




