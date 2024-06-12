# import logging
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
# import time

# # Configure logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

# # Function to initialize the WebDriver


# def initialize_driver():
#     logging.info("Initializing WebDriver")
#     options = webdriver.ChromeOptions()
#     options.add_argument('--start-maximized')
#     options.add_argument('--disable-extensions')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-notifications')  # Disable notifications
#     options.add_argument('--disable-infobars')  # Disable infobars
#     # Disable translate infobar
#     options.add_argument('--disable-features=TranslateUI')
#     # Disable side navigation
#     options.add_argument('--disable-browser-side-navigation')
#     options.add_argument('--disable-popup-blocking')  # Disable popup blocking
#     driver = webdriver.Chrome(options=options)
#     logging.info("WebDriver initialized")
#     return driver

# # Function to perform search on Google Maps


# def perform_maps_search(driver, query):
#     logging.info(f"Performing Google Maps search for: {query}")
#     driver.get('https://www.google.com/maps')
#     search_box = WebDriverWait(driver, 20).until(
#         EC.presence_of_element_located(
#             (By.XPATH, "//input[@id='searchboxinput']"))
#     )
#     search_box.send_keys(query)
#     search_button = WebDriverWait(driver, 20).until(
#         EC.element_to_be_clickable(
#             (By.XPATH, "//button[@id='searchbox-searchbutton']"))
#     )
#     search_button.click()
#     logging.info("Search performed")

# # Function to extract shop names and click each one to scrape additional data


# def extract_and_click_shops(driver):
#     logging.info("Extracting and clicking shop names")
#     shop_names = []
#     s_url = []
#     seen_names = set()
#     try:
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_all_elements_located(
#                 (By.XPATH, "//a[contains(@class, 'hfpxzc')]"))
#         )

#         shop_elements = driver.find_elements(
#             By.XPATH, "//a[contains(@class, 'hfpxzc')]")

#         for shop in shop_elements:
#             try:
#                 shop_name = shop.get_attribute('aria-label')
#                 if shop_name and shop_name not in seen_names:
#                     seen_names.add(shop_name)
#                     shop_names.append(shop_name)
#                     shop.click()
#                     time.sleep(2)  # Wait for the pop-up to appear
#                     url = scrape_shop_details(driver)
#                     s_url.append(url)
#                     driver.back()
#                     WebDriverWait(driver, 20).until(
#                         EC.presence_of_all_elements_located(
#                             (By.XPATH, "//a[contains(@class, 'hfpxzc')]"))
#                     )  # Wait for the search results to reappear
#             except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
#                 logging.error(f"An error occurred while processing shop: {e}")

#         logging.info(f"Extracted shop names: {shop_names}")
#         return shop_names, s_url
#     except Exception as e:
#         logging.error(f"An error occurred while extracting shop names: {e}")
#         return [], []

# # Function to scrape details from the pop-up


# def scrape_shop_details(driver):
#     logging.info("Scraping shop details")
#     try:
#         shop_details = WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located(
#                 (By.XPATH, "//div[contains(@class, 'm6QErb')]"))
#         )

#         detail_divs = shop_details.find_elements(
#             By.XPATH, "//div[contains(@class, 'rogA2c ITvuef')]")

#         if len(detail_divs) > 0:
#             web = detail_divs[0]
#             detail_text = web.text
#         else:
#             detail_text = "No details available"

#         logging.info(f"Scraped detail text: {detail_text}")
#         return detail_text

#     except (NoSuchElementException, TimeoutException) as e:
#         logging.error(f"An error occurred while scraping shop details: {e}")
#         return "Error occurred"

# # Main function to run the entire process with retries
# def scroll_down(driver, max_shops):
    
#     try:
#         shop_count = 0
#         while shop_count < max_shops:

#             scrollable_div = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
#             )
#             driver.execute_script("arguments[0].scrollBy(0, 1000);", scrollable_div)
#             time.sleep(2)  # Wait for the page to load more results
#             shop_count+=1
#             # Count the number of shop elements currently visible
#             # shop_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'hfpxzc Io6YTe fontBodyMedium kR99db ')]")
            
#     except TimeoutException:
#         print("Unable to locate the scrollable element")




# def main():
#     logging.info("Starting main process")
#     retries = 3
#     max_shops = 1
#     for attempt in range(retries):
#         driver = None
#         try:
#             driver = initialize_driver()  # Initialize the driver first
#             query = "iphone shops in bengaluru"  # Then define the query

#             perform_maps_search(driver, query)
#             scroll_down(driver, max_shops)
#             shop_names, s_url = extract_and_click_shops(driver)
            
#             if not shop_names or not s_url:
#                 raise ValueError("No shop names or URLs found")

#             for index, name in enumerate(shop_names, start=1):
#                 url = s_url[index - 1] if index - 1 < len(s_url) else "No URL"
#                 print(f"{index}. {name}: {url}")

#             break  # If successful, exit the loop

#         except WebDriverException as e:
#             logging.error(
#                 f"WebDriver error occurred: {e}. Attempt {attempt + 1} of {retries}.")
#             if attempt == retries - 1:
#                 logging.error("Max retries reached. Exiting.")
#             else:
#                 time.sleep(5)  # Wait before retrying

#         except ValueError as ve:
#             logging.error(f"Value error occurred: {ve}. Exiting.")
#             break

#         finally:
#             if driver:
#                 try:
#                     driver.quit()
#                 except Exception as e:
#                     logging.error(f"Error quitting driver: {e}")

#     logging.info("Main process completed")


# # Entry point of the script
# if __name__ == "__main__":
#     main()





# import logging
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
# import time

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Function to initialize the WebDriver
# def initialize_driver():
#     logging.info("Initializing WebDriver")
#     options = webdriver.ChromeOptions()
#     options.add_argument('--start-maximized')
#     options.add_argument('--disable-extensions')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-notifications')  # Disable notifications
#     options.add_argument('--disable-infobars')  # Disable infobars
#     options.add_argument('--disable-features=TranslateUI')  # Disable translate infobar
#     options.add_argument('--disable-browser-side-navigation')  # Disable side navigation
#     options.add_argument('--disable-popup-blocking')  # Disable popup blocking
#     driver = webdriver.Chrome(options=options)
#     logging.info("WebDriver initialized")
#     return driver

# # Function to perform search on Google Maps
# def perform_maps_search(driver, query):
#     logging.info(f"Performing Google Maps search for: {query}")
#     driver.get('https://www.google.com/maps')
#     search_box = WebDriverWait(driver, 20).until(
#         EC.presence_of_element_located((By.XPATH, "//input[@id='searchboxinput']"))
#     )
#     search_box.send_keys(query)
#     search_button = WebDriverWait(driver, 20).until(
#         EC.element_to_be_clickable((By.XPATH, "//button[@id='searchbox-searchbutton']"))
#     )
#     search_button.click()
#     logging.info("Search performed")

# # Function to scroll down the results panel using JavaScript
# def scroll_down(driver, max_shops):
#     shop_count = 0
#     try:
#         while shop_count < max_shops:
#             scrollable_div = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
#             )
#             driver.execute_script("arguments[0].scrollBy(0, 1000);", scrollable_div)
#             time.sleep(2)  # Wait for the page to load more results

#             # Count the number of shop elements currently visible
#             shop_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'hfpxzc')]")
#             shop_count = len(shop_elements)
#             if shop_count >= max_shops:
#                 break
#     except TimeoutException:
#         logging.error("Unable to locate the scrollable element")

# # Function to extract shop names and click each one to scrape additional data
# def extract_and_click_shops(driver, max_shops):
#     logging.info("Extracting and clicking shop names")
#     shop_names = []
#     s_url = []
#     seen_names = set()
#     try:
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'hfpxzc')]"))
#         )

#         shop_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'hfpxzc')]")

#         for shop in shop_elements:
#             try:
#                 shop_name = shop.get_attribute('aria-label')
#                 if shop_name and shop_name not in seen_names:
#                     seen_names.add(shop_name)
#                     shop_names.append(shop_name)
#                     shop.click()
#                     time.sleep(2)  # Wait for the pop-up to appear
#                     url = scrape_shop_details(driver)
#                     s_url.append(url)
#                     driver.back()
#                     WebDriverWait(driver, 20).until(
#                         EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'hfpxzc')]"))
#                     )  # Wait for the search results to reappear
#                     if len(shop_names) >= max_shops:
#                         break
#             except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
#                 logging.error(f"An error occurred while processing shop: {e}")

#         logging.info(f"Extracted shop names: {shop_names}")
#         return shop_names, s_url
#     except Exception as e:
#         logging.error(f"An error occurred while extracting shop names: {e}")
#         return [], []

# # Function to scrape details from the pop-up
# def scrape_shop_details(driver):
#     logging.info("Scraping shop details")
#     try:
#         shop_details = WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'm6QErb')]"))
#         )

#         detail_divs = shop_details.find_elements(By.XPATH, "//div[contains(@class, 'rogA2c ITvuef')]")

#         if len(detail_divs) > 0:
#             web = detail_divs[0].find_element(By.TAG_NAME, 'a').get_attribute('href')
#         else:
#             web = "No URL available"

#         logging.info(f"Scraped URL: {web}")
#         return web

#     except (NoSuchElementException, TimeoutException) as e:
#         logging.error(f"An error occurred while scraping shop details: {e}")
#         return "Error occurred"

# # Main function to run the entire process with retries
# def main():
#     logging.info("Starting main process")
#     retries = 3
#     max_shops = 15  # Set the number of shops to scroll and click
#     for attempt in range(retries):
#         driver = None
#         try:
#             driver = initialize_driver()  # Initialize the driver first
#             query = "iPhone shops near Chennai"  # Then define the query

#             perform_maps_search(driver, query)
#             scroll_down(driver, max_shops)  # Scroll down until at least max_shops are obtained
#             shop_names, s_url = extract_and_click_shops(driver, max_shops)

#             if len(shop_names) < max_shops or len(s_url) < max_shops:
#                 raise ValueError("Not enough shop names or URLs found")

#             for index, name in enumerate(shop_names, start=1):
#                 url = s_url[index - 1] if index - 1 < len(s_url) else "No URL"
#                 print(f"{index}. {name}: {url}")

#             break  # If successful, exit the loop

#         except WebDriverException as e:
#             logging.error(f"WebDriver error occurred: {e}. Attempt {attempt + 1} of {retries}.")
#             if attempt == retries - 1:
#                 logging.error("Max retries reached. Exiting.")
#             else:
#                 time.sleep(5)  # Wait before retrying

#         except ValueError as ve:
#             logging.error(f"Value error occurred: {ve}. Exiting.")
#             break

#         finally:
#             if driver:
#                 try:
#                     driver.quit()
#                 except Exception as e:
#                     logging.error(f"Error quitting driver: {e}")

#     logging.info("Main process completed")

# # Entry point of the script
# if __name__ == "__main__":
#     main()








# import logging
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
# import time

# # Configure logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

# # Function to initialize the WebDriver
# def initialize_driver():
#     logging.info("Initializing WebDriver")
#     options = webdriver.ChromeOptions()
#     options.add_argument('--start-maximized')
#     options.add_argument('--disable-extensions')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-notifications')  # Disable notifications
#     options.add_argument('--disable-infobars')  # Disable infobars
#     # Disable translate infobar
#     options.add_argument('--disable-features=TranslateUI')
#     # Disable side navigation
#     options.add_argument('--disable-browser-side-navigation')
#     options.add_argument('--disable-popup-blocking')  # Disable popup blocking
#     driver = webdriver.Chrome(options=options)
#     logging.info("WebDriver initialized")
#     return driver

# # Function to perform search on Google Maps
# def perform_maps_search(driver, query):
#     logging.info(f"Performing Google Maps search for: {query}")
#     search_url = f"https://www.google.com/maps/search/{query}"
#     driver.get(search_url)
#     logging.info("Search performed")

# # Function to extract shop names and click each one to scrape additional data
# def extract_and_click_shops(driver):
#     logging.info("Extracting and clicking shop names")
#     shop_names = []
#     s_url = []
#     seen_names = set()
#     try:
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_all_elements_located(
#                 (By.XPATH, "//a[contains(@class, 'hfpxzc')]"))
#         )

#         shop_elements = driver.find_elements(
#             By.XPATH, "//a[contains(@class, 'hfpxzc')]")

#         for shop in shop_elements:
#             try:
#                 shop_name = shop.get_attribute('aria-label')
#                 if shop_name and shop_name not in seen_names:
#                     seen_names.add(shop_name)
#                     shop_names.append(shop_name)
#                     shop.click()
#                     time.sleep(2)  # Wait for the pop-up to appear
#                     url = scrape_shop_details(driver)
#                     s_url.append(url)
#                     driver.back()
#                     WebDriverWait(driver, 20).until(
#                         EC.presence_of_all_elements_located(
#                             (By.XPATH, "//a[contains(@class, 'hfpxzc')]"))
#                     )  # Wait for the search results to reappear
#             except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
#                 logging.error(f"An error occurred while processing shop: {e}")

#         logging.info(f"Extracted shop names: {shop_names}")
#         return shop_names, s_url
#     except Exception as e:
#         logging.error(f"An error occurred while extracting shop names: {e}")
#         return [], []

# # Function to scrape details from the pop-up
# def scrape_shop_details(driver):
#     logging.info("Scraping shop details")
#     try:
#         shop_details = WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located(
#                 (By.XPATH, "//div[contains(@class, 'm6QErb')]"))
#         )

#         detail_divs = shop_details.find_elements(
#             By.XPATH, "//div[contains(@class, 'Io6YTe')]")

#         if len(detail_divs) > 0:
#             web = detail_divs[0]
#             detail_text = web.text
#         else:
#             detail_text = "No details available"

#         logging.info(f"Scraped detail text: {detail_text}")
#         return detail_text

#     except (NoSuchElementException, TimeoutException) as e:
#         logging.error(f"An error occurred while scraping shop details: {e}")
#         return "Error occurred"

# # Function to scroll down and load more shops
# def scroll_down(driver, max_shops):
#     try:
#         shop_count = 0
#         while shop_count < max_shops:
#             scrollable_div = WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.XPATH, "//div[@role='feed']"))
#             )
#             driver.execute_script("arguments[0].scrollBy(0, 1000);", scrollable_div)
#             time.sleep(2)  # Wait for the page to load more results
#             shop_count += 1
#     except TimeoutException:
#         logging.error("Unable to locate the scrollable element")

# # Main function to run the entire process with retries
# def main():
#     logging.info("Starting main process")
#     retries = 1
#     max_shops = 5
#     for attempt in range(retries):
#         driver = None
#         try:
#             driver = initialize_driver()  # Initialize the driver first
#             query = "iphone shops in bengaluru"  # Then define the query

#             perform_maps_search(driver, query)
#             scroll_down(driver, max_shops)
#             shop_names, s_url = extract_and_click_shops(driver)

#             if not shop_names or not s_url:
#                 raise ValueError("No shop names or URLs found")

#             for index, name in enumerate(shop_names, start=1):
#                 url = s_url[index - 1] if index - 1 < len(s_url) else "No URL"
#                 print(f"{index}. {name}: {url}")

#             break  # If successful, exit the loop

#         except WebDriverException as e:
#             logging.error(
#                 f"WebDriver error occurred: {e}. Attempt {attempt + 1} of {retries}.")
#             if attempt == retries - 1:
#                 logging.error("Max retries reached. Exiting.")
#             else:
#                 time.sleep(5)  # Wait before retrying

#         except ValueError as ve:
#             logging.error(f"Value error occurred: {ve}. Exiting.")
#             break

#         finally:
#             if driver:
#                 try:
#                     driver.quit()
#                 except Exception as e:
#                     logging.error(f"Error quitting driver: {e}")

#     logging.info("Main process completed")

# # Entry point of the script
# if __name__ == "__main__":
#     main()
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
import time

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Function to initialize the WebDriver
def initialize_driver():
    logging.info("Initializing WebDriver")
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')  # Disable infobars
    options.add_argument('--disable-features=TranslateUI')  # Disable translate infobar
    options.add_argument('--disable-browser-side-navigation')  # Disable side navigation
    options.add_argument('--disable-popup-blocking')  # Disable popup blocking
    driver = webdriver.Chrome(options=options)
    logging.info("WebDriver initialized")
    return driver

# Function to perform Google search and navigate to Google Maps link
def perform_google_search(driver, query):
    logging.info(f"Performing Google search for: {query}")
    driver.get('https://www.google.com')
    search_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.NAME, 'q'))
    )
    search_box.send_keys(query)
    search_box.submit()

    maps_link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.PARTIAL_LINK_TEXT, 'Maps'))
    )
    maps_link.click()
    logging.info("Navigated to Google Maps link from search results")

# Function to perform search on Google Maps
def perform_maps_search(driver, query):
    logging.info(f"Performing Google Maps search for: {query}")
    search_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@id='searchboxinput']"))
    )
    search_box.send_keys(query)
    search_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='searchbox-searchbutton']"))
    )
    search_button.click()
    logging.info("Search performed")

# Function to scroll the Google Maps page
def scroll_maps_page(driver):
    logging.info("Scrolling Google Maps page")
    scroll_pause_time = 2
    max_scrolls = 10
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(scroll_pause_time)

# Function to extract shop names and click each one to scrape additional data
def extract_and_click_shops(driver):
    logging.info("Extracting and clicking shop names")
    shop_names = []
    s_url = []
    seen_names = set()
    max_shops = 10
    scroll_maps_page(driver)  # Scroll to load more shops
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@class, 'hfpxzc')]"))
        )

        shop_elements = driver.find_elements(
            By.XPATH, "//a[contains(@class, 'hfpxzc')]")

        for shop in shop_elements:
            if len(shop_names) >= max_shops:
                break
            try:
                shop_name = shop.get_attribute('aria-label')
                if shop_name and shop_name not in seen_names:
                    seen_names.add(shop_name)
                    shop_names.append(shop_name)
                    shop.click()
                    time.sleep(2)  # Wait for the pop-up to appear
                    url = scrape_shop_details(driver)
                    s_url.append(url)
                    driver.back()
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, "//a[contains(@class, 'hfpxzc')]"))
                    )  # Wait for the search results to reappear
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                logging.error(f"An error occurred while processing shop: {e}")

        logging.info(f"Extracted shop names: {shop_names}")
        return shop_names, s_url
    except Exception as e:
        logging.error(f"An error occurred while extracting shop names: {e}")
        return [], []

# Function to scrape details from the pop-up
def scrape_shop_details(driver):
    logging.info("Scraping shop details")
    try:
        shop_details = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'm6QErb')]"))
        )
        
        detail_divs = shop_details.find_elements(
            By.XPATH, "//div[contains(@class, 'rogA2c ITvuef')]")

        if len(detail_divs) > 0:
            web = detail_divs[0]
            detail_text = str(web.text) + str(len(detail_divs))
        else:
            detail_text = "No details available +" + str(shop_details)

        logging.info(f"Scraped detail text: {detail_text}")
        return detail_text

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"An error occurred while scraping shop details: {e}")
        return "Error occurred"

# Main function to run the entire process with retries
def main():
    logging.info("Starting main process")
    retries = 3
    for attempt in range(retries):
        driver = None
        try:
            driver = initialize_driver()  # Initialize the driver first
            query = "Apple Phone shops in Bahrain"  # Define the query

            perform_google_search(driver, query)  # Perform Google search
            perform_maps_search(driver, query)  # Perform Maps search
            shop_names, s_url = extract_and_click_shops(driver)

            if not shop_names or not s_url:
                raise ValueError("No shop names or URLs found")

            for index, name in enumerate(shop_names, start=1):
                url = s_url[index - 1] if index - 1 < len(s_url) else "No URL"
                print(f"{index}. {name}: {url}")

            break  # If successful, exit the loop

        except WebDriverException as e:
            logging.error(
                f"WebDriver error occurred: {e}. Attempt {attempt + 1} of {retries}.")
            if attempt == retries - 1:
                logging.error("Max retries reached. Exiting.")
            else:
                time.sleep(5)  # Wait before retrying

        except ValueError as ve:
            logging.error(f"Value error occurred: {ve}. Exiting.")
            break

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logging.error(f"Error quitting driver: {e}")

    logging.info("Main process completed")

# Entry point of the script
if __name__ == "__main__":
    main()
