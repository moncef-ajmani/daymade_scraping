from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
import json
import time
import collections
from bs4 import BeautifulSoup
import time



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

categories_links = {
    "Art & Culture":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=521",
    "Career & Business":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=405",
    "Community & Environment":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=604",
    "Dancing":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=612",
    "Games":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=535",
    "Health & Wellbeing":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=511",
    "Hobbies & Passions":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=571",
    "Identity & Language":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=622",
    "Movements & Politics":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=642",
    "Music":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=395",
    "Parents & Family":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=673",
    "Pets & Animals":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=701",
    "Religion & Spirituality":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=593",
    "Science & Education":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=436",
    "Social Activities":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=652",
    "Sports & Fitness":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=482",
    "Support & Coaching":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=449",
    "Technology":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=546",
    "Travel & Outdoor":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=684",
    "Writing":"https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=467",
}

def get_categories_link(output_file):
    chrome_options = ChromeOptions()
    chrome_options.headless = False 
    with Chrome(options=chrome_options) as driver:
        with open(output_file,"w",encoding="utf-8") as f:
            for category,link in categories_links.items():
                print(f"Category: {category}")
                driver.get(link)
                time.sleep(2)
                auto_scroll(driver)
                time.sleep(1)
                event_cards = driver.find_elements(By.CSS_SELECTOR,"div[data-element-name='categoryResults-eventCard'] #event-card-in-search-results")
                
                for link in event_cards:
                    f.write(f"{category};{link.get_attribute('href')}\n")


def get_data_from_links(input_file,output_file):
    events = []
    chrome_options = ChromeOptions()
    chrome_options.headless = False
    try:
        with open(input_file,"r",encoding="utf-8") as f:
            with Chrome(options=chrome_options) as driver:
                count = 1
                driver.get("https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=521")
                # time.sleep(60)
                print("start")

                for row in f:
                    time.sleep(2)
                    if count == 100:
                        break

                    if count%50 == 0:
                        with open(f"{output_file}_{count}", 'w', encoding='utf-8') as file:
                            json.dump(events, file, ensure_ascii=False, indent=4)
                    
                    event = collections.defaultdict(None)
                    print(f"Loading {count}")
                    count+=1
                    
                    category,url = row.split(";")
                    event["category"] = category
                    source = url.replace("\n","")
                    event["source"] = source
                    driver.get(source)
                    time.sleep(2)
                    try:
                        script_element = driver.find_elements(By.CSS_SELECTOR,"script[type='application/ld+json']")[1]
                        data_script = json.loads(script_element.get_attribute("innerHTML"))
                    except Exception as e:
                        print(e)
                        data_script = None
                    print(data_script)  

                    try:
                        event["title"] = driver.find_element(By.CSS_SELECTOR,"#main h1").text
                    except Exception as e:
                        print(e)
                        event["title"] = None
                    
                    try:
                        event["startDate"] = data_script['startDate']
                    except:
                        event["startDate"] = None
                    
                    try:
                        event["endDate"] = data_script['endDate']
                    except:
                        event["endDate"] = None
                    
                    try:
                        event["datetime"] = driver.find_element(By.CSS_SELECTOR,'div[data-event-label="action-bar"] time').text
                    except:
                        event["datetime"] = None
                    
                    
                    try:
                        event["price"] = driver.find_elements(By.CSS_SELECTOR,'div[data-event-label="action-bar"] .font-semibold')[1].text
                    except Exception as e:
                        print(e)
                        event["price"] = None
                    time.sleep(1)
                    try:
                        # location = driver.find_element(By.CSS_SELECTOR,'#event-info a[data-testid="venue-name-link"]').text
                        adress = driver.find_element(By.CSS_SELECTOR,'#event-info .mt-5.flex').text
                        event["locationText"] = adress
                        # print("Adress: ",adress)
                    except Exception as e:
                        print(e)
                        event["locationText"] = None

                    try:
                        event["description"] = driver.find_element(By.CSS_SELECTOR,'#event-details').text
                    except:
                        event["description"] = None
                    event["link"] = source
                    print(event)
                    events.append(event)
    except Exception as e:
        print(e)

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)

def get_data_from_links_proxy(input_file,output_file):
    events = []
    # SBR_WEBDRIVER = 'https://brd-customer-hl_52e1a5fd-zone-scraping_browser:b33ehiwuk4nt@brd.superproxy.io:9515'
    chrome_options = ChromeOptions()
    chrome_options.headless = False
    with open(input_file,"r",encoding="utf-8") as f:
        with Chrome(options=chrome_options) as driver:

            count = 1
            # driver.get("https://www.meetup.com/find/?source=EVENTS&location=de--Berlin&categoryId=521")
            # # time.sleep(60)
            # print("start")

            for row in f:
                # sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
                # with Remote(sbr_connection, options=ChromeOptions()) as driver:
                    
                if count%50 == 0:
                    with open(f"{output_file}_{count}", 'w', encoding='utf-8') as file:
                        json.dump(events, file, ensure_ascii=False, indent=4)
                event = collections.defaultdict(None)
                print(f"Loading {count}")
                count+=1
                
                category,url = row.split(";")
                event["category"] = category
                link = url.replace("\n","")
                event["source"] = "meetup"
                driver.get(link)


                try:
                    event["title"] = driver.find_element(By.CSS_SELECTOR,"#main h1").text
                except Exception as e:
                    print(e)
                    event["title"] = None
                
                try:
                    event["datetime"] = driver.find_element(By.CSS_SELECTOR,'div[data-event-label="action-bar"] time').text
                except:
                    event["datetime"] = None
                
                try:
                    event["price"] = driver.find_elements(By.CSS_SELECTOR,'div[data-event-label="action-bar"] .font-semibold')[1].text
                except Exception as e:
                    print(e)
                    event["price"] = None
                try:
                    # location = driver.find_element(By.CSS_SELECTOR,'#event-info a[data-testid="venue-name-link"]').text
                    event["locationText"] = driver.find_element(By.CSS_SELECTOR,'#event-info .mt-5.flex').text
                
                    # print("Adress: ",adress)
                except Exception as e:
                    print(e)
                    event["locationText"] = None

                try:
                    event["description"] = driver.find_element(By.CSS_SELECTOR,'#event-details').text
                except:
                    event["description"] = None
                event["link"] = link
                print(event)
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
    get_categories_link("00meetup.txt")
    remove_duplicated_rows_from_file("00meetup.txt")
    get_data_from_links("00meetup.txt","01meetup.json")