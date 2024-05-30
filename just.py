from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
import time

# Function to initialize the WebDriver
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-notifications')  # Disable notifications
    options.add_argument('--disable-infobars')  # Disable infobars
    options.add_argument('--disable-features=TranslateUI')  # Disable translate infobar
    options.add_argument('--disable-browser-side-navigation')  # Disable side navigation
    options.add_argument('--disable-popup-blocking')  # Disable popup blocking
    driver = webdriver.Chrome(options=options)
    return driver

# Function to perform search on Google Maps
def perform_maps_search(driver, query):
    driver.get('https://www.google.com/maps')
    search_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@id='searchboxinput']"))
    )
    search_box.send_keys(query)
    search_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@id='searchbox-searchbutton']"))
    )
    search_button.click()

# Function to scroll down the results panel using JavaScript
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
#     except TimeoutException:
#         print("Unable to locate the scrollable element")

# Function to extract shop names
def extract_shop_names(driver):
    shop_names = []
    seen_names = set()
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'hfpxzc')]"))
        )

        shop_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'hfpxzc')]")
        
        for shop in shop_elements:
            try:
                shop_name = shop.get_attribute('aria-label')
                if shop_name and shop_name not in seen_names:
                    seen_names.add(shop_name)
                    shop_names.append(shop_name)
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                print(f"An error occurred while processing shop: {e}")

        return shop_names
    except Exception as e:
        print(f"An error occurred while extracting shop names: {e}")
        return []

# Main function to run the entire process with retries
def main():
    retries = 3
    max_shops = 15  # Desired minimum number of shops
    for attempt in range(retries):
        try:
            driver = initialize_driver()  # Initialize the driver first
            query = "iPhone shops near Chennai"  # Then define the query

            perform_maps_search(driver, query)
            # scroll_down(driver, max_shops)  # Scroll down until at least 15 shops are obtained
            
            shop_names = extract_shop_names(driver)
            
            for index, name in enumerate(shop_names, start=1):
                print(f"{index}. {name}")

            break  # If successful, exit the loop

        except WebDriverException as e:
            print(f"WebDriver error occurred: {e}. Attempt {attempt + 1} of {retries}.")
            if attempt == retries - 1:
                print("Max retries reached. Exiting.")
            else:
                time.sleep(5)  # Wait before retrying

        # finally:
        #     try:
        #         # driver.quit()
        #     except:
        #         pass

# Entry point of the script
if __name__ == "__main__":
    main()
