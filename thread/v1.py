import time
import threading
from queue import Queue
from selenium import webdriver
from selenium.webdriver.common.by import By

# URLs to scrape
urls = [
    "https://example.com",
    "https://example2.com",
    "https://example3.com",
    "https://example4.com",
    "https://example5.com"
]

# Queue to store button values
button_queue = Queue()

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

def collect_clickable_elements(driver):
    tags = ["button", "input", "a"]
    elements = find_elements(driver, tags)
    return elements

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

def scrape_buttons(url, queue, unique_id):
    driver = webdriver.Chrome()
    driver.get(url)
    scroll_and_load(driver, wait_time=4)
    clickable_elements = collect_clickable_elements(driver)
    elements_info = get_elements_info(driver, clickable_elements)
    
    # Filter out elements without visible text and remove duplicates
    seen_elements = set()
    unique_elements_info = []

    for element_info in elements_info:
        key = (element_info['visibleText'], element_info['tagName'])
        if key not in seen_elements:
            seen_elements.add(key)
            unique_elements_info.append(element_info)
    
    visible_texts = [element_info['visibleText'] for element_info in unique_elements_info if element_info['visibleText']]
    driver.quit()
    
    # Put the collected button values into the queue
    queue.put((unique_id, visible_texts))

# Create threads for each WebDriver instance
threads = []
for i, url in enumerate(urls):
    unique_id = f"driver_{i}"
    thread = threading.Thread(target=scrape_buttons, args=(url, button_queue, unique_id))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

# Print the contents of the queue
while not button_queue.empty():
    unique_id, buttons = button_queue.get()
    print(f"WebDriver Instance: {unique_id}, Buttons: {buttons}")
