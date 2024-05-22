from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import re
import collections

def get_categories_links(driver):
    url = "https://www.eventbrite.de/d/germany--berlin/all-events/"
    driver.get(url)
    time.sleep(5)
    read_more_cat = driver.find_element(By.CSS_SELECTOR,"button[aria-controls='view-more-kategorie']")
    read_more_cat.click()
    time.sleep(2)
    categories = driver.find_elements(By.CSS_SELECTOR,"#view-more-kategorie li")
    with open("categories_links.txt","w",encoding="utf-8") as f:
        for cat in categories:
            try:
                category_name = cat.find_element(By.CSS_SELECTOR,".NestedCategoryFilters-module__categoryOption___20a21").text
                print(category_name)
                # radio_button = WebDriverWait(cat, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"label")))
                # radio_button.click()
                # time.sleep(1)
                url = cat.find_element(By.CSS_SELECTOR,'.eds-link').get_attribute("href")
                f.write(f"{category_name};{url}\n")
            except Exception as e:
                print(e)
        

def get_events_links_from_categories_links(driver,input_file,output_file):
    with open(input_file,"r",encoding='utf-8') as f:
        
        events = []
        count = 1
        for row in f:
            print(f"Loading Category: {count}")
            count+=1
            category,link = row.split(";")
            link = link.replace("\n","")
            # https://www.eventbrite.de/d/germany--berlin/business--events/?page=1
            
            driver.get(f"{link}?page=1")
            time.sleep(1)
            pages_count = eval(driver.find_element(By.CSS_SELECTOR,".eds-pagination__results li[data-spec='pagination-parent']").text.split("von")[1])
            # print(f"{category} : {pages_count}")

            pattern = r'\?page=\d+'
            new_link = re.sub(pattern, '', link)
            
            for page in range(1,pages_count+1):
                print(f"Page: {page}")
                url = f"{new_link}?page={page}"
                driver.get(url)
                time.sleep(2)
                cards = driver.find_elements(By.CSS_SELECTOR,".discover-search-desktop-card")
                for card in cards:
                    try:
                        link = card.find_element(By.CSS_SELECTOR,"a.event-card-link").get_attribute("href")
                        events.append({
                            "category":category,
                            "link":link
                        })
                    except Exception as e:
                        print(e)
            
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(events, file, ensure_ascii=False, indent=4)
                

def get_data_from_links(driver,input_file,output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    events = [] 

    # {"startDate":"2024-05-20T18:30:00+02:00","endDate":"2024-05-20T20:00:00+02:00","name":"Berlin Big Business Tech And Entrepreneur Professional Networking Soiree","url":"https://www.eventbrite.com/e/berlin-big-business-tech-and-entrepreneur-professional-networking-soiree-tickets-764024055517","image":"https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F528465679%2F1587896518563%2F1%2Foriginal.20230603-152256?w=1000\u0026auto=format%2Ccompress\u0026q=75\u0026sharp=10\u0026rect=0%2C0%2C1200%2C600\u0026s=54b6714926652dee33f51ba5e8f026db","eventStatus":"https://schema.org/EventScheduled","offers":[{"availabilityEnds":"2024-06-10T16:00:00Z","priceCurrency":"USD","url":"https://www.eventbrite.com/e/berlin-big-business-tech-and-entrepreneur-professional-networking-soiree-tickets-764024055517","lowPrice":0.0,"highPrice":161.9,"@type":"AggregateOffer","availabilityStarts":"2023-11-12T23:00:00Z","validFrom":"2023-11-12T23:00:00Z","availability":"InStock"},{"inventoryLevel":0,"name":"I Will Attend ( Free Admission )","priceCurrency":"USD","url":"https://www.eventbrite.com/e/berlin-big-business-tech-and-entrepreneur-professional-networking-soiree-tickets-764024055517","price":0,"@type":"Offer","availability":"SoldOut"},{"name":"Regular Admission (Secure $ Eventbrite Checkout)","priceCurrency":"USD","url":"https://www.eventbrite.com/e/berlin-big-business-tech-and-entrepreneur-professional-networking-soiree-tickets-764024055517","price":12.51,"@type":"Offer","availability":"InStock"},{"name":"SPONSOR TABLE","priceCurrency":"USD","url":"https://www.eventbrite.com/e/berlin-big-business-tech-and-entrepreneur-professional-networking-soiree-tickets-764024055517","price":161.9,"@type":"Offer","availability":"InStock"}],"location":{"address":{"addressCountry":"DE","addressLocality":"Berlin","addressRegion":"BE","streetAddress":"Budapester Str. 40, 10787 Berlin, Germany","postalCode":"10787","@type":"PostalAddress"},"@type":"Place","name":"Monkey Bar"},"eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode","@context":"http://schema.org","organizer":{"url":"https://www.eventbrite.com/o/startup-gamechanger-66792456113","@type":"Organization","name":"Startup Gamechanger"},"@type":"SocialEvent","description":"Berlin Biggest Business Tech \u0026 Entrepreneur Professional Networking Soiree"}
    
    try:
        for index,event in enumerate(data[:101]): 
            try:
                print(f"Loading {index+1}/{len(data)}")

                if (index+1)%50 == 0:
                        with open(f"eventbrite{index+1}.json", 'w', encoding='utf-8') as file:
                            json.dump(events, file, ensure_ascii=False, indent=4)
                            
                driver.get(event["link"])
                
                script_element = driver.find_element(By.CSS_SELECTOR,"script[type='application/ld+json']")	
                data_script = json.loads(script_element.get_attribute("innerHTML"))
                if "startDate" in data:
                    print(data_script['startDate'])
                    
                
                try:
                    event['description'] = data_script['description']
                except:
                    event['description'] = None
                try:
                    event['address'] = data_script['location']['address']['streetAddress']
                except:
                    event['address'] = None
                try:
                    event['city'] = data_script['location']['address']['addressLocality']
                except:
                    event['city'] = None
                try:
                    event['zipCode'] = data_script['location']['address']['postalCode']
                except:
                    event['zipCode'] = None
                try:
                    event['venue'] = data_script['location']['name']
                except:
                    event['venue'] = None
                try:
                    event['title'] = data_script['name']
                except:
                    event["title"] = None
                try:
                    event['price'] = data_script['offers'][0]['lowPrice']
                except:
                    event["price"] = None
                try:
                    event['startDate'] = data_script['startDate']
                except:
                    event["startDate"] = None
                try:
                    event['endDate'] = data_script['endDate']
                except:
                    event['endDate'] = None
                # try:
                #     event["locationText"] = driver.find_element(By.CSS_SELECTOR,".location-info__address").text
                #     time.sleep(0.3)
                # except:
                #     event["locationText"] = ""
                try:
                    event["duration"] = driver.find_element(By.CSS_SELECTOR,"ul[data-testid='highlights'] > li").text
                    time.sleep(0.3)
                except:
                    event["duration"] = ""
                # try:
                #     event["description"] = driver.find_element(By.CSS_SELECTOR,".has-user-generated-content").text
                #     time.sleep(0.3)
                # except:
                #     event["description"] = ""
                
                event["source"] = "eventbrite"
                # if event["price"] == "":
                #     try:
                #         # get data from inside iframe if the price doesnt exist in simple way
                #         iframe = driver.find_element(By.CSS_SELECTOR,"#ticket-selection-iframe-container iframe")
                #         driver.switch_to.frame(iframe)

                #         price1 = driver.find_element(By.CSS_SELECTOR,".ticket-card-compact-size__price").text
                #         event["price"] = price1
                #         print(price1)
                #     except:
                #         event["price"] = ""
                print(event)
                events.append(event)
            except:
                pass
    except Exception as e:
        print(e)
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(events, file, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    chrome_options = ChromeOptions()
    chrome_options.headless = False

    with Chrome(options=chrome_options) as driver:
        get_categories_links(driver)
        get_events_links_from_categories_links(driver,"categories_links.txt","links_category.json")
        get_data_from_links(driver,"links_category.json","01eventbrite.json")