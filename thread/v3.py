import os
import time
import threading
from queue import Queue
from multiprocessing import Process, Queue as MPQueue, Lock
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
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolExecutor
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.prebuilt import ToolInvocation
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph
from langchain_core.tools import tool

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub

import logging

# Environment setup
os.environ["OPENAI_API_KEY"] = "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"
os.environ["LANGCHAIN_API_KEY"] = "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"

# URLs to scrape
urls = [
    "https://flipkart.com",
    "https://ajio.com",
    "https://myntra.com"
    ]
    


# Queue to store button values
button_queue = Queue()

# Global variable to store the currently active WebDriver instance
active_webdriver = None
# Lock for synchronizing access to the global variable
webdriver_lock = Lock()

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

def scrape_buttons(url, queue, unique_id, driver_instances):
    try:
        driver = webdriver.Chrome()
        driver_instances[unique_id] = driver
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
        
        # Put the collected button values into the queue
        queue.put((unique_id, visible_texts))
    except Exception as e:
        print(f"Error scraping {url}: {e}")

@tool("click", return_direct=False)
def click(button_name: str) -> bool:
    """Use to click any button on a website, Input the name or text of the button."""
    global active_webdriver
    try:
        with webdriver_lock:
            driver = active_webdriver
            scroll_and_load(driver)

            # Locate the button by its visible text using XPath
            button_xpath = f"//button[text()='{button_name}'] | //a[text()='{button_name}']"
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))

            # Scroll to the element and click
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
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
            print(f"Clicked on the element with text: '{button_name}'")
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

            # Collect visible text of interest for final output
            visible_texts = [element_info['visibleText'] for element_info in unique_elements_info if element_info['visibleText']]
            return ",".join(visible_texts)
    except (NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException) as e:
        print(f"Error interacting with the element: {e}")
        return False
    except JavascriptException as e:
        print(f"JavascriptException: {str(e)}")
        return False
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def process_buttons(mp_queue, driver_instances):
    global active_webdriver
    while True:
        if not mp_queue.empty():
            unique_id, button = mp_queue.get()
            print(f"Processing button '{button}' for WebDriver Instance: {unique_id}")

            with webdriver_lock:
                active_webdriver = driver_instances.get(unique_id)

            if active_webdriver:
                tools = [click]
                tool_executor = ToolExecutor(tools)
                
                # Use the tool executor to perform the click
                tool_executor.invoke_tool("click", button_name=button)
                # For simplicity, simulate LLM processing with a placeholder result
                result = (unique_id, button)  # Simulate processing result
                print(f"Processed result for {unique_id}: {result}")
            else:
                print(f"No WebDriver instance found for {unique_id}")

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Multiprocessing queue to communicate with LLM process
    mp_queue = MPQueue()
    
    # Dictionary to store WebDriver instances by unique ID
    driver_instances = {}

    # Create and start threads for each WebDriver instance
    threads = []
    for i, url in enumerate(urls):
        unique_id = f"driver_{i}"
        thread = threading.Thread(target=scrape_buttons, args=(url, mp_queue, unique_id, driver_instances))
        threads.append(thread)
        thread.start()
        logging.info(f"Started scraping thread for {url} with ID {unique_id}")

    # Start the LLM processing function in a separate process
    llm_process = Process(target=process_buttons, args=(mp_queue, driver_instances))
    llm_process.start()
    logging.info("Started LLM processing process")

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
        logging.info(f"Completed scraping thread for {thread.name}")

    # Ensure LLM process is terminated after processing
    llm_process.terminate()
    llm_process.join()
    logging.info("LLM processing process terminated")

if __name__ == "__main__":
    main()

