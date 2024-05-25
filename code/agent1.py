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


@tool("buttons", return_direct=False)
def buttons() -> str:
    """This function will return the string of all buttons in a website, call this function directly without arguments."""
    driver = webdriver.Chrome()
    url = 'https://www.apple.com'
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

    # Display clickable elements and ask the user to select one
    print("Buttons Returned")
    return "\n".join(["--".join([str(value) for value in element_info.values()]) for element_info in unique_elements_info])


tools = [buttons]
tool_executor = ToolExecutor(tools)

# We will set streaming=True so that we can stream tokens
# See the streaming section for more information on this.
model = ChatOpenAI(temperature=0, streaming=True)
model = model.bind_tools(tools)


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


workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_edge("action", "agent")
workflow.add_edge("agent", "action")
app = workflow.compile()

inputs = {"messages": [HumanMessage(content="use your functions and at least once and tell me what they do")]}
result = app.invoke(inputs)

print(result)

