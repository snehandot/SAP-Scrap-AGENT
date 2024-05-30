import os
import time
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


# Environment setup
os.environ["OPENAI_API_KEY"] = "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"
os.environ["LANGCHAIN_API_KEY"] = "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"



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

@tool("click", return_direct=False)
def click(button_name: str) -> bool:
    """Use to click any button on a website, Input the name or text of the button."""
    try:
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









def buttons(url: str) -> str:
    driver.get(url)
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


    print(",".join(visible_texts))
    return ",".join(visible_texts)



tools = [click]
tool_executor = ToolExecutor(tools)

# We will set streaming=True so that we can stream tokens

model = ChatOpenAI(model="gpt-3.5-turbo",temperature=0, streaming=True)

prompt = hub.pull("hwchase17/openai-tools-agent")

agent = create_openai_tools_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

driver = webdriver.Chrome()
website=input("Tell website name:")
product=input("Product name")
init_buttons=buttons(website)
agent_executor.invoke(
    {
        "input":f" You are product search engine , Click the buttons shown to you of the website {website},Buttons:{init_buttons} with the click tool , navigate around and find {product} and its price"   }
)


