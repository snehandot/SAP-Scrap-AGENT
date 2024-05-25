from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Function to set up the WebDriver
def setup_driver():
    driver = webdriver.Chrome()
    return driver

# Function to open a webpage
def open_webpage(driver, url):
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

# Function to scroll and load all content on the page
def scroll_and_load(driver, wait_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Function to collect clickable elements
def collect_clickable_elements(driver):
    clickable_tags = ["button", "a", "input", "div", "span"]
    elements = []
    for tag in clickable_tags:
        elements.extend(driver.find_elements(By.TAG_NAME, tag))

    # Filter elements to include only visible and enabled ones
    clickable_elements = [el for el in elements if el.is_displayed() and el.is_enabled()]

    # Further filter to ensure they are interactive
    interactive_elements = []
    for el in clickable_elements:
        if el.tag_name == 'button' or el.tag_name == 'a':
            interactive_elements.append(el)
        elif el.tag_name == 'input' and el.get_attribute('type') in ['button', 'submit', 'text', 'search']:
            interactive_elements.append(el)
        elif el.tag_name in ['div', 'span'] and el.get_attribute('role') in ['button', 'link']:
            interactive_elements.append(el)
        else:
            try:
                if el.get_attribute('onclick') or el.find_element(By.XPATH, './/button | .//a | .//input[@type="button" or @type="submit"]'):
                    interactive_elements.append(el)
            except:
                continue

    return interactive_elements

# Function to get event listeners and visible text for each clickable element
def get_elements_info(driver, clickable_elements):
    script = """
    function getVisibleText(element) {
        return element.innerText.trim();
    }
    var elements = arguments[0];
    var result = [];
    elements.forEach(function(element) {
        var elementInfo = {
            tagName: element.tagName,
            outerHTML: element.outerHTML,
            visibleText: getVisibleText(element),
        };
        result.push(elementInfo);
    });
    return result;
    """
    return driver.execute_script(script, clickable_elements)

# Main function to interact with the webpage
def interact_with_page(driver):
    scroll_and_load(driver, wait_time=4)
    clickable_elements = collect_clickable_elements(driver)
    elements_info = get_elements_info(driver, clickable_elements)

    # Filter out elements without visible text
    elements_info = [info for info in elements_info if info['visibleText']]
    clickable_elements = [el for el, info in zip(clickable_elements, elements_info) if info['visibleText']]

    # Display clickable elements and ask the user to select one
    print("Available clickable elements:")
    for index, element_info in enumerate(elements_info):
        print(f"{index}: {element_info['visibleText']} (Tag: {element_info['tagName']})")

    selected_index = int(input("Enter the index of the element you want to click: "))

    # Click the selected element and handle special cases
    if 0 <= selected_index < len(clickable_elements):
        element_to_click = clickable_elements[selected_index]
        visible_text = elements_info[selected_index]['visibleText']
        try:
            if element_to_click.tag_name == 'input' and element_to_click.get_attribute('type') in ['text', 'search']:
                search_query = input(f"Enter your search query for {visible_text}: ")
                element_to_click.send_keys(search_query)
                element_to_click.submit()
            else:
                element_to_click.click()
            time.sleep(5)  # Wait for navigation to complete
            print(f"Clicked on the element: {visible_text}")
        except Exception as e:
            print(f"Error clicking the element directly: {e}")
            driver.execute_script("arguments[0].click();", element_to_click)
            time.sleep(5)
        
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

# Main loop to repeat the process until user decides to close the browser
def main():
    driver = setup_driver()
    open_webpage(driver, 'https://www.aptronixindia.com/iphone')

    while True:
        if not interact_with_page(driver):
            break

if __name__ == "__main__":
    main()
