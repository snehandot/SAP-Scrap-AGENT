from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException, 
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    JavascriptException
)
import time

def scroll_and_load(driver, wait_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_time)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def find_elements(driver, tags):
    elements = []
    for tag in tags:
        elements.extend(driver.find_elements(By.TAG_NAME, tag))
    return elements

def collect_shadow_dom_elements(driver, tags):
    # Add implementation to collect elements from shadow DOMs if necessary
    return []

def collect_clickable_elements(driver):
    tags = ["button", "input", "a"]
    elements = find_elements(driver, tags)
    elements.extend(collect_shadow_dom_elements(driver, tags))
    return elements

# JavaScript to detect event listeners and visible text, including inline handlers
script = """
function getVisibleText(element) {
    return element.innerText.trim();
}
var elements = arguments[0];
var result = [];
elements.forEach(function(element) {
    var elementInfo = {
        tagName: element.tagName,
        visibleText: getVisibleText(element),
    };
    result.push(elementInfo);
});
return result;
"""

def get_elements_info(driver, elements):
    return driver.execute_script(script, elements)

def click_element(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))

        try:
            element.click()
        except ElementClickInterceptedException:
            # Temporarily hide obstructing elements
            driver.execute_script("document.querySelector('header').style.display = 'none';")
            time.sleep(1)
            element.click()
            # Restore obstructing elements
            driver.execute_script("document.querySelector('header').style.display = 'block';")
        
        time.sleep(5)  # Wait for navigation to complete
        return True
    except (StaleElementReferenceException, ElementNotInteractableException, NoSuchElementException) as e:
        print(f"Error interacting with the element: {e}")
    except JavascriptException as e:
        print(f"JavascriptException: {str(e)}")
    except Exception as e:
        print(f"Exception: {str(e)}")

    return False

def interact_with_page():
    #driver = webdriver.Chrome()
    #url = 'https://www.apple.com'
    #driver.get(url)
    scroll_and_load(driver, wait_time=4)
    clickable_elements = collect_clickable_elements(driver)
    elements_info = get_elements_info(driver, clickable_elements)

    # Filter out elements without visible text and remove duplicates
    seen_elements = set()
    unique_elements_info = []
    unique_clickable_elements = []

    for element_info, element in zip(elements_info, clickable_elements):
        key = (element_info['visibleText'], element_info['tagName'])
        if key not in seen_elements:
            seen_elements.add(key)
            unique_elements_info.append(element_info)
            unique_clickable_elements.append(element)

    # Display clickable elements and ask the user to select one
    print("Available clickable elements:")
    for index, element_info in enumerate(unique_elements_info):
        print(f"{element_info['visibleText']},{index}",end="--")

    selected_index = int(input("Enter the index of the element you want to click: "))

    # Click the selected element and handle special cases
    if 0 <= selected_index < len(unique_clickable_elements):
        element_to_click = unique_clickable_elements[selected_index]
        visible_text = unique_elements_info[selected_index]['visibleText']
        if click_element(driver, element_to_click):
            print(f"Clicked on the element: {visible_text}")
        else:
            print("Failed to click the element.")
        
        # After clicking, prompt to close or continue
        close_browser = input("Do you want to close the browser? (yes/no): ").strip().lower()
        if close_browser == 'yes':
            driver.quit()
            return False
        else:
            return True
    else:
        print("Invalid selection.")
        return True

# Main interaction loop
start_time = time.time()
driver = webdriver.Chrome()
url = 'https://www.reliancedigital.in/'
driver.get(url)

while interact_with_page():
    pass

# Close the WebDriver
driver.quit()

end_time = time.time()
print("Total time taken:", end_time - start_time)

