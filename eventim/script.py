from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
import time 
import json
import sys
import re

def get_links(page,driver):
    print("Start Scarping!!!")
    cards = driver.find_elements(By.CSS_SELECTOR,".search-result-content product-group-item")
    i = 0
    links = []
    with open(f"links_{page}.txt",'a',encoding='utf-8') as f:
        while i < len(cards):
            try:
                print(f"\rPage: {page} - Loading {i+1}/{len(cards)}")
                card = cards[i]
                
                card_clickable = card.find_element(By.CSS_SELECTOR, "article")
                card_clickable.click()
                # image url: listing-image-wrapper
                # Print the URL of the new page
                new_page_url = driver.current_url
                
                f.write(f"{new_page_url}\n")
                links.append({"link":new_page_url})
                # print(f"URL of the {i+1} page: {new_page_url}")
                
                # After interacting with elements, you can navigate back to the main page
                driver.back()
                time.sleep(1)
                i+=1
                cards = driver.find_elements(By.CSS_SELECTOR,".search-result-content product-group-item")
            except Exception as e:
                print(e)
        print(end="\n")
    # print(end="\n")
    with open(f"links_{page}.json", 'w', encoding='utf-8') as file_:
        json.dump(links, file_, ensure_ascii=False, indent=4)
    print("End Scarping!!!")


def get_data_from_links(input_file,output_file):
    with open(input_file) as json_file:
        data = json.load(json_file)

    # print(len(data))
    chrome_options = ChromeOptions()
    chrome_options.headless = False

    events = []
    with Chrome(options=chrome_options) as driver:
        driver.get("https://www.eventim.de/artist/kulturbrauerei-berlin")
        time.sleep(5)
        # close_cookie(driver)
        count = 1
        for index,event in enumerate(data[:101]):
            try:
                if (index+1) %100 == 0:
                    with open(f"{output_file}_{index+1}.json", 'w', encoding='utf-8') as file_:
                        json.dump(events, file_, ensure_ascii=False, indent=4)
                count+=1
            except Exception as e:
                print(e)
                pass

            print(f"Loading {index+1}/{len(data)} - Source: {event['link']}")
            driver.get(event["link"])
            time.sleep(1)
            try:
                # show data as list
                try:
                    is_list = driver.find_element(By.CSS_SELECTOR,"a[data-switcher-content='list']").get_attribute("aria-selected")
                    if is_list == "false":
                        list_btn = driver.find_element(By.CSS_SELECTOR,"a[data-switcher-content='list']")
                        list_btn.click()
                        time.sleep(1)
                except Exception as e:
                    # print(e)
                    pass
                try:
                    # filter data by berlin
                    filter_btn = driver.find_element(By.CSS_SELECTOR,'button[data-qa="filter-button"]')
                    filter_btn.click()
                    time.sleep(1)
                except Exception as e:
                    # print(e)
                    pass
                try:
                    filter_select_btn = driver.find_element(By.CSS_SELECTOR,"#city_select")
                    filter_select_btn.click()
                    time.sleep(1)
                

                    berlin_btn = driver.find_element(By.CSS_SELECTOR,'li[data-tracking-label="Berlin"]')
                    berlin_btn.click()
                    time.sleep(1)
                except Exception as e:
                    # print(e)
                    pass

                try:
                    price = driver.find_element(By.CSS_SELECTOR,".stage-price").text
                except Exception as e:
                    print("no price")
                    price = ""
                try:
                    description = driver.find_element(By.CSS_SELECTOR,"section[data-qa='stageteasertext-component'] .external-content").text
                except Exception as e:
                    print("no description")
                    description = ""

                script_element = driver.find_elements(By.CSS_SELECTOR,"head script")

                
                for script in script_element:
                    script_content = script.get_attribute("innerHTML")
                    if "window.dataLayer.push" in script_content:
                        # Use regular expressions to extract the JSON data
                        json_match = re.search(r'window.dataLayer.push\((.*?)\);', script_content)
                        if json_match:
                            json_data = json_match.group(1)
                            data_s = json.loads(json_data)
                            # print(data_s)
                            # Access and print the desired information from the JSON object
                            if data_s["event_series_name"]:
                                title = data_s["event_series_name"]
                            else:
                                title = None

                            if data_s["event_series_genre"]:
                                category = ",".join(data_s["event_series_genre"])
                            else:
                                category = None
                            
                            break
                try:
                    try:
                        time.sleep(5)
                        # events_pages_count = math.ceil(eval(driver.find_element(By.CSS_SELECTOR,".eventlisting-eventcount").text.replace("Events",""))/20)
                        events_pages_count = eval(driver.find_elements(By.CSS_SELECTOR,".js-tab-a-list-group .pagination-block li.pagination-item")[-2].text)
                        # print(driver.find_elements(By.CSS_SELECTOR,".js-tab-a-list-group .pagination-block li.pagination-item"))
                        print("Total Pages:",events_pages_count)
                    except Exception as e:
                        print(e)
                        events_pages_count = 1
                    for city_page in range(1,events_pages_count+1):
                        events_cards = driver.find_elements(By.CSS_SELECTOR,".listing-item-wrapper-inside-card")
                        if len(events_cards) == 0:
                            continue
                        print(f"Page: {city_page} - Count: ({len(events_cards)})")
                        for event_card in events_cards:
                            obj = {
                                "title":title,
                                "category":category
                            }
                            # {"@context":"https://schema.org","@type":"Event","description":"BLUE MAN GROUP ist wie der Puls von Berlin: knallbunt, innovativ und kreativ.","endDate":"2024-05-05T15:00:00.000+02:00","image":["https://www.eventim.de/obj/media/DE-eventim/teaser/222x222/2024/blue-man-group-tickets-2024.jpg","https://www.eventim.de/obj/media/DE-eventim/teaser/222x222/2024/blue-man-group-tickets-2024.jpg","https://www.eventim.de/obj/media/DE-eventim/teaser/artworks/2024/blue-man-group-tickets-header.jpg"],"location":{"name":"Stage Bluemax Theater","sameAs":"https://www.eventim.de/city/berlin-1/venue/bluemax-theater-berlin-3442/","address":{"streetAddress":"Marlene-Dietrich-Platz 4","postalCode":"10785","addressLocality":"Berlin","addressRegion":"","addressCountry":"DE","@type":"PostalAddress"},"@type":"Place"},"name":"BLUE MAN GROUP in Berlin - Die Show-Sensation ","offers":{"category":"primary","price":45.99,"priceCurrency":"EUR","availability":"InStock","url":"https://www.eventim.de/event/blue-man-group-in-berlin-die-show-sensation-stage-bluemax-theater-17990233/","validFrom":"2023-12-07T15:00:00.000+01:00","@type":"Offer"},"performer":{"name":"Blue Man Group – Berlin","@type":"PerformingGroup"},"startDate":"2024-05-05T15:00:00.000+02:00","url":"https://www.eventim.de/event/blue-man-group-in-berlin-die-show-sensation-stage-bluemax-theater-17990233/"}
                            script_element = event_card.find_element(By.CSS_SELECTOR,"script[type='application/ld+json']")	
                            data_script = json.loads(script_element.get_attribute("innerHTML"))
                            print(data_script)
                            
                            try:
                                obj['address'] = data_script['location']['address']['streetAddress']
                            except:
                                obj['address'] = None
                            try:
                                obj['city'] = data_script['location']['address']['addressLocality']
                            except:
                                obj['city'] = None
                            try:
                                obj['zipCode'] = data_script['location']['address']['postalCode']
                            except:
                                obj['zipCode'] = None
                            try:
                                obj['venue'] = data_script['location']['name']
                            except:
                                obj['venue'] = None
                            try:
                                obj['title'] = data_script['name']
                            except:
                                obj["title"] = None

                            try:
                                obj['url'] = data_script['offers']['url']
                            except:
                                obj["url"] = None
                            try:
                                obj['startDate'] = data_script['startDate']
                            except:
                                obj["startDate"] = None
                            try:
                                obj['endDate'] = data_script['endDate']
                            except:
                                obj['endDate'] = None
                            

                            # event["date"] = date
                            # event["location"] = location
                            print(obj["startDate"])
                            obj["description"] = description
                            obj["price"] = price
                            obj["source"] = "eventim"
                            
                            events.append(obj)
                            
                        driver.get(f'{event["link"]}?cityname=Berlin&pnum={city_page}')
                except Exception as e:
                    print(e)
                    with open("errors","a",encoding="utf-8") as f:
                        f.write(f"{e}\n")
                    print(e)
            except Exception as e:
                print(e)

    print("=====================================================")
    for el in events:
        print(el["startDate"])

    with open(output_file, 'w', encoding='utf-8') as file_:
        json.dump(events, file_, ensure_ascii=False, indent=4)

    driver.close()

def close_cookie(driver):
    btn = driver.find_element(By.CSS_SELECTOR,"#cmpwelcomebtnyes a")
    btn.click()
    time.sleep(1)

if __name__ == "__main__":
    page_start = int(sys.argv[1])
    page_end = int(sys.argv[2])
    print(f"Pages: {page_start} - {page_end}")
    url = "https://www.eventim.de/city/berlin-1/?shownonbookable=true"
    for i in range(page_start,page_end+1):
        chrome_options1 = ChromeOptions()
        chrome_options1.headless = False
        driver = Chrome(options = chrome_options1)
        driver.get(f"{url}&page={i}")
        time.sleep(5)
        time.sleep(1)
        get_links(i,driver)
        driver.close()
    get_data_from_links("00eventim.json","01eventim.json")
