import pandas as pd
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
import csv

def scroll_and_load(driver, wait_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait_time)
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
        href: element.href ? element.href : ""
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
        
        if element.tag_name == "a":
            href = element.get_attribute("href")
            if href:
                driver.get(href)
                time.sleep(5)
                return True
        
        try:
            element.click()
        except ElementClickInterceptedException:
            driver.execute_script("document.querySelector('header').style.display = 'none';")
            time.sleep(1)
            element.click()
            driver.execute_script("document.querySelector('header').style.display = 'block';")
        time.sleep(5)
        return True
    except (StaleElementReferenceException, ElementNotInteractableException, NoSuchElementException, JavascriptException) as e:
        print(f"Error interacting with the element: {e}")
    except Exception as e:
        print(f"Exception: {e}")
    return False

def collect_and_click_buttons(driver, url, button_texts):
    driver.get(url)
    scroll_and_load(driver, wait_time=4)
    results = []

    for button_text in button_texts:
        clickable_elements = collect_clickable_elements(driver)
        elements_info = get_elements_info(driver, clickable_elements)

        seen_elements = set()
        unique_elements_info = []
        unique_clickable_elements = []

        for element_info, element in zip(elements_info, clickable_elements):
            key = (element_info['visibleText'], element_info['tagName'])
            if key not in seen_elements:
                seen_elements.add(key)
                unique_elements_info.append(element_info)
                unique_clickable_elements.append(element)

        buttons_info = [{"index": i, "text": info['visibleText'], "tag": info['tagName'], "href": info.get("href", "")} for i, info in enumerate(unique_elements_info)]

        element_to_click = next((element for info, element in zip(unique_elements_info, unique_clickable_elements) if info['visibleText'] == button_text), None)
        
        if element_to_click:
            if click_element(driver, element_to_click):
                time.sleep(2)
                new_clickable_elements = collect_clickable_elements(driver)
                new_elements_info = get_elements_info(driver, new_clickable_elements)
                new_buttons_info = [{"index": i, "text": info['visibleText'], "tag": info['tagName'], "href": info.get("href", "")} for i, info in enumerate(new_elements_info)]
                results.append({
                    "url": url,
                    "clicked_button": button_text,
                    "buttons_info": new_buttons_info
                })
            else:
                print(f"Failed to click the button: {button_text}")
        else:
            print(f"Button with text '{button_text}' not found.")
            results.append({
                "url": url,
                "clicked_button": button_text,
                "buttons_info": []
            })

    return results

def process_csv_and_collect_buttons(input_csv_path, output_csv_path):
    driver = webdriver.Chrome()
    df = pd.read_csv(input_csv_path)
    all_results = []

    for index, row in df.iterrows():
        url = row.iloc[0]  # Assuming the first column contains the URL
        button_texts = row.iloc[1:].dropna().tolist()  # Subsequent columns contain button texts
        results = collect_and_click_buttons(driver, url, button_texts)
        all_results.extend(results)

    driver.quit()

    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["url", "clicked_button", "buttons_info"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in all_results:
            writer.writerow(result)



# Example usage
input_csv_path = '/home/snehan/Documents/sap/dataset/set1.csv'
output_csv_path = '/home/snehan/Documents/sap/dataset/done.csv'
process_csv_and_collect_buttons(input_csv_path, output_csv_path)

