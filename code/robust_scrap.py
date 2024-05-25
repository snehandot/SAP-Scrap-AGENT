from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize global variables
global start_time, end_time1, end_time2, end_time3

def collect_from_url(url):
    global start_time, end_time1, end_time2, end_time3
    
    driver.get(url)
    print("Content loaded")
    end_time1 = time.time()

    # Wait for the initial page to fully load
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "//button"))
    )

    # Function to scroll to the bottom of the page and wait for new content to load
    def scroll_and_load(driver, wait_time=2):
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(wait_time)  # Wait for new content to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    # Scroll to the bottom of the page and load all content
    scroll_and_load(driver, wait_time=2)

    # JavaScript to detect event listeners and visible text, including inline handlers
    script = """
    function getEventListeners(element) {
        var listeners = [];
        var allEvents = Object.keys(window).filter(function(k) { return k.indexOf("on") === 0 });
        allEvents.forEach(function(eventName) {
            var listenersForElement = getEventListenersForElement(element, eventName.slice(2));
            if (listenersForElement.length > 0) {
                listeners.push({event: eventName.slice(2), listeners: listenersForElement});
            }
        });
        return listeners;
    }

    function getEventListenersForElement(element, eventName) {
        var listeners = [];
        if (typeof jQuery !== 'undefined') {
            var events = jQuery._data(element, "events");
            if (events && events[eventName]) {
                events[eventName].forEach(function(event) {
                    listeners.push(event.handler.toString());
                });
            }
        }
        if (element["on" + eventName]) {
            listeners.push(element["on" + eventName].toString());
        }
        return listeners;
    }

    // Function to check for inline event handlers
    function getInlineEventHandlers(element) {
        var inlineHandlers = [];
        var allEvents = Object.keys(window).filter(function(k) { return k.indexOf("on") === 0 });
        allEvents.forEach(function(event) {
            if (element.hasAttribute(event)) {
                inlineHandlers.push({event: event.slice(2), handler: element.getAttribute(event)});
            }
        });
        return inlineHandlers;
    }

    // Function to get visible text from an element, including nested elements
    function getVisibleText(element) {
        return element.innerText.trim();
    }

    var elements = arguments[0];
    var result = [];
    elements.forEach(function(element) {
        if (element.tagName.toLowerCase() === 'button') {
            var elementInfo = {
                tagName: element.tagName,
                outerHTML: element.outerHTML,
                visibleText: getVisibleText(element),
                listeners: getEventListeners(element),
                inlineHandlers: getInlineEventHandlers(element)
            };
            result.push(elementInfo);
        }
    });
    return result;
    """

    # Function to find all button elements
    def find_button_elements(driver):
        return driver.find_elements(By.TAG_NAME, 'button')

    button_elements = find_button_elements(driver)
    button_elements_info = driver.execute_script(script, button_elements)

    end_time2 = time.time()
    
    return button_elements_info

start_time = time.time()
driver = webdriver.Chrome()
end_time4 = time.time()
url ='https://www.tatagreenbattery.com/'
buttons_info = collect_from_url(url)

# Print the visible text of each button on a new line
for button in buttons_info:
    print(button['visibleText'])

end_time3 = time.time()

init_time = end_time4 - start_time
load_time = end_time1 - end_time4
scrap_time = end_time2 - end_time1
print_time = end_time3 - end_time2

print("Time to init: ", init_time)
print("Time to load: ", load_time)
print("Time to scrape: ", scrap_time)
print("Total time: ", print_time)

driver.quit()

