from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import re
# from utils import auto_scroll

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

def get_links(driver,output_file):
    url = "https://www.museumsportal-berlin.de/de/programm/"
    
    driver.get(url)
    time.sleep(2)
    auto_scroll(driver)
    time.sleep(1)
    cards = driver.find_elements(By.CSS_SELECTOR,".mp-page-list-grid hylo-router-link")
    with open(output_file,"w",encoding="utf-8") as f:
        for card in cards:
            url = card.get_attribute("href")
            try:
                categories = card.find_element(By.CSS_SELECTOR,".labels").text.replace("\n","")
            except:
                categories = None
            
            f.write(f"{categories};{url}\n")
    f.close()



def get_data_from_links(driver,input_file,output_file):
    events = []
    try:
        with open(input_file,"r",encoding="utf-8") as f:
            
            count = 1
            driver.get("https://www.museumsportal-berlin.de/de/programm/")
            time.sleep(5)
            cookie_element = driver.find_element(By.CSS_SELECTOR,"hylo-cookie-banner")
            if cookie_element:
                print("Cookie Present")
                cookie_btn = driver.find_element(By.CSS_SELECTOR,".hylo-cookie-banner-accept")
                cookie_btn.click()
            for row in f:
                if count == 102:
                    break
                if count%50 == 0:
                    with open(f"{count}.json", 'w', encoding='utf-8') as file_:
                        json.dump(events, file_, ensure_ascii=False, indent=4)
                category,url = row.split(";")
                url = url.replace("\n","")
                print(f"Loading {count} - Source: {url}")
                
                source = f"https://www.museumsportal-berlin.de{url}"
                driver.get(source)
                time.sleep(5)
                
                driver.execute_script(f"window.scrollBy(0, 700);")
                try:
                    script_element = driver.find_element(By.CSS_SELECTOR,"script[type='application/ld+json']")
                    data_script = json.loads(script_element.get_attribute("innerHTML"))
                except Exception as e:
                    print(e)
                    data_script = None
                if category == "None":
                    category = None
                try:
                    category = driver.find_element(By.CSS_SELECTOR,".mp-page-detail-header-content-categories").text
                except:
                    category = None
                
                try:
                    dt = [span.text for span in driver.find_elements(By.CSS_SELECTOR,".mp-page-detail-header-content-sub span")] 
                except:
                    dt = None
                try:
                    title = driver.find_element(By.CSS_SELECTOR,".mp-page-detail-header-content-p h1").text
                except:
                    title = None
                    print("no title")
                time.sleep(1)
                try:
                    description = driver.find_element(By.CSS_SELECTOR,".mp-page-detail-main .columns .column-2-3").text
                except:
                    description = None
                    print("no descrition")
                time.sleep(1)
                
                try:
                    locationText = driver.find_element(By.CSS_SELECTOR,".detail-block-location").text
                except: 
                    locationText = None
                    print("no locationText")
                time.sleep(1)

                try:
                    price = " ".join([p.text for p in driver.find_elements(By.CSS_SELECTOR,".detail-block-tickets p")])
                except:
                    price = None
                    print("no price")
                
                try:
                    title = data_script["name"]
                except:
                    # title = None
                    pass
                try:
                    city = data_script["location"]["address"]["addressLocality"]
                except:
                    city = None
                try:
                    address = data_script["location"]["address"]["streetAddress"]
                except:
                    address = None
                try:
                    zipCode = data_script["location"]["address"]['postalCode']
                except:
                    zipCode = None
                
                try:
                    venue = data_script["location"]['name']
                except:
                    venue = None
                
                try:
                    description = data_script["description"]
                except:
                    # description = None
                    pass
                
                try:
                    startDate = data_script["startDate"]
                except:
                    startDate = None
                try:
                    endDate = data_script["endDate"]
                except:
                    endDate = None

                
                try:
                    more_button = driver.find_element(By.CSS_SELECTOR,".detail-block-opening button")
                    more_button.click()
                    time.sleep(1)
                except:
                    pass                   
                
                # try:
                #     time.sleep(2)
                #     dates = [d.text for d in driver.find_elements(By.CSS_SELECTOR,".detail-block-opening ul li")]
                #     print(f"Dates Count ==> ({len(dates)})")
                #     # dates_more = [d.text for d in driver.find_elements(By.CSS_SELECTOR,".detail-block-opening ul li.hylo-link-more-item")]
                #     # for date in dates:
                #     #     print(date.replace("\n", " "))
                #     #     event = {
                #     #         "title":title,
                #     #         "category":category,
                #     #         "source":"meseumsport",
                #     #         "price":price,
                #     #         "datetime":date,
                #     #         "locationText":locationText,
                #     #         "duration":None,
                #     #         "description":description,
                #     #         "link":source,
                #     #         "geo_location":None
                #     #     } 
                #     #     events.append(event)
                #     event = {
                #         "title":title,
                #         "category":category,
                #         "source":"meseumsport",
                #         "price":price,
                #         "datetime":None,
                #         "locationText":locationText,
                #         "duration":None,
                #         "description":description,
                #         "link":source,
                #         "geo_location":None
                #     } 

                events.append({
                    "title":title,
                    "description":description,
                    "category":category,
                    "city":city,
                    "address":address,
                    "zipCode":zipCode,
                    "venue":venue,
                    "startDate":startDate,
                    "endDate":endDate,
                    "price":price,
                    "durationInMinutes":None,
                    "locationText":locationText,
                    "source":"museumsportal",
                    "link":source,
                    "datetime":dt
                })
                count +=1
    except Exception as e:
        print(e)
    with open(output_file, 'w', encoding='utf-8') as file_:
        json.dump(events, file_, ensure_ascii=False, indent=4)
if __name__ == "__main__":
    chrome_options = ChromeOptions()
    chrome_options.headless = False
    with Chrome(options=chrome_options) as driver:
        # get_links(driver,"links_museumsportal.txt")
        # remove_duplicated_rows_from_file("links_museumsportal.txt")
        get_data_from_links(driver,"links_museumsportal.txt","01museumsportal.json")
    
    driver.close()