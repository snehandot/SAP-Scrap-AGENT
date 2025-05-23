import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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
from langchain_openai import ChatOpenAI
from langchain import hub

# Global variable for storing unique element information
unique_elements_info = []

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

def initialize_unique_elements_info(driver, hover_limit=5):
    global unique_elements_info
    scroll_and_load(driver, wait_time=4)
    clickable_elements = collect_clickable_elements(driver)
    elements_info = get_elements_info(driver, clickable_elements)

    # Filter out elements without visible text and remove duplicates
    seen_elements = set()
    unique_elements_info = []

    for element_info, element in zip(elements_info, clickable_elements):
        key = (element_info['visibleText'], element_info['tagName'])
        if key not in seen_elements:
            seen_elements.add(key)
            element_info['element'] = element
            unique_elements_info.append(element_info)

    # Check for hover-triggered elements only at the top of the page (limited by hover_limit)
    for element_info in unique_elements_info[:hover_limit]:
        try:
            element = element_info['element']
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            time.sleep(2)  # Give time for hover-triggered elements to appear

            new_elements = collect_clickable_elements(driver)
            new_elements_info = get_elements_info(driver, new_elements)

            for new_element_info, new_element in zip(new_elements_info, new_elements):
                key = (new_element_info['visibleText'], new_element_info['tagName'])
                if key not in seen_elements:
                    seen_elements.add(key)
                    new_element_info['element'] = new_element
                    unique_elements_info.append(new_element_info)
        except:
            continue

@tool("click", return_direct=False)
def click(button_name: str) -> bool:
    """Use to click any button on a website, Input the name or text of the button."""
    global unique_elements_info

    def hover_and_click(element):
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        WebDriverWait(driver, 10).until(EC.visibility_of(element))
        element.click()

    def attempt_click(element):
        try:
            element.click()
        except ElementClickInterceptedException:
            driver.execute_script("document.querySelector('header').style.display = 'none';")
            time.sleep(1)
            element.click()
            driver.execute_script("document.querySelector('header').style.display = 'block';")

    scroll_and_load(driver)

    for element_info in unique_elements_info:
        if button_name.lower() in element_info['visibleText'].lower():
            element = element_info['element']
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(element))
            try:
                attempt_click(element)
            except StaleElementReferenceException:
                # Re-locate the element and try clicking again
                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{button_name}')]")))
                try:
                    attempt_click(element)
                except:
                    hover_and_click(element)
            except:
                hover_and_click(element)

            print(f"Clicked on the element with text: '{button_name}'")
            scroll_and_load(driver, wait_time=2)
            return True

    print(f"Button with name '{button_name}' not found.")
    return False

@tool("buttons", return_direct=False)
def buttons(url: str) -> str:
    """Use to get the visual buttons on a website. Call the function with the URL of the website you want to view."""
    global driver
    driver.get(url)
    initialize_unique_elements_info(driver)
    
    visible_texts = [element_info['visibleText'] for element_info in unique_elements_info if element_info['visibleText']]
    print(",".join(visible_texts))
    return ",".join(visible_texts)

tools = [buttons, click]
tool_executor = ToolExecutor(tools)

# We will set streaming=True so that we can stream tokens
# See the streaming section for more information on this.
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, streaming=True)
prompt = hub.pull("hwchase17/openai-tools-agent")

agent = create_openai_tools_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def call_model(state):
    messages = state["messages"]
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": messages + [response]}

# Define the function to execute tools
def call_tool(state):
    messages = state["messages"]
    # Based on the continue condition
    # we know the last message involves a function call
    last_message = messages[-1]
    # We construct a ToolInvocation from the function_call
    tool_call = buttons
    action = ToolInvocation(
        tool=tool_call.name,
        tool_input={}
    )
    # We call the tool_executor and get back a response
    response = tool_executor.invoke(action)
    # We use the response to create a FunctionMessage
    function_message = ToolMessage(
        content=str(response), name=action.tool, tool_call_id="placeholder_id"
    )
    # We return a list, because this will get added to the existing list
    return {"messages": messages + [function_message]}

##workflow = StateGraph(AgentState)
#workflow.add_node("agent", call_model)
##workflow.add_node("action", call_tool)
#workflow.set_entry_point("agent")
##workflow.add_edge("action", "agent")
#w#orkflow.add_edge("agent", "action")
#app = workflow.compile()

#inputs = {"messages": [HumanMessage(content="navigate to the apple website and click on the iphone section")]}
# result = app.invoke(inputs)
driver = webdriver.Chrome()
website = input("Tell website name: ")
product = input("Product name: ")
agent_executor.invoke(
    {
        "input": f"continuously click only the button obtained from the buttons function in latest web page. don't assume web links, go to {website} and navigate around to find {product}"
    }
)

# Print(result)

