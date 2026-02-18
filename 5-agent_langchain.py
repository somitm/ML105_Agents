import os
import re
from datetime import datetime
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model

from openai import OpenAI
from dotenv import load_dotenv

_ = load_dotenv()

# Initialize the OpenAI
api_key=os.environ.get("OPENAI_API_KEY")

# Initialize the LLM 

# This single line can return a ChatOpenAI, ChatAnthropic, or ChatBedrock object
llm = init_chat_model("gpt-4o", model_provider="openai", temperature=0)

# To switch to Bedrock, you'd only change the parameters:
# llm = init_chat_model("anthropic.claude-3-sonnet-20240229-v1:0", model_provider="amazon_bedrock")

# Define Tools
@tool
def calculate_expression(expression: str) -> str:
    """Calculator: Evaluate a mathematical expression"""
    safe_expr = re.sub(r'[^0-9+\-*/(). ]', '', expression)
    if safe_expr.strip() == "":
        return "I couldn't compute that."
    try:
        result = eval(safe_expr)
        print("🔧 ... ...Tool: calculator")
        return f"The result is: {result}"
    except:
        return "I couldn't compute that."

@tool
def get_weather(location: str) -> str:
    """Weather: Get weather information for a location"""
    weather_data = {
        "new york": "Sunny, 72°F",
        "london": "Cloudy, 58°F",
        "tokyo": "Rainy, 65°F",
        "paris": "Partly cloudy, 68°F"
    }
    location_lower = location.lower()
    for city, weather in weather_data.items():
        if city in location_lower:
            print("🔧 ... ...Tool: get_weather")
            return f"Weather in {city.title()}: {weather}"
    return f"Weather information for {location} is not available in simulation."

@tool
def get_date() -> str:
    """Get Date: Get the current date"""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    print("🔧 ... ...Tool: get_date")
    return f"Today's date is: {date_str}"

@tool
def get_time() -> str:
    """Get Time: Get the current time"""
    now = datetime.now()
    time_str = now.strftime("%I:%M:%S %p")
    print("🔧 ... ...Tool: get_time")
    return f"The current time is: {time_str}"

# Create agent with tools
tools = [calculate_expression, get_weather, get_date, get_time]
#agent = create_openai_tools_agent(llm, tools, prompt)

# Create the agent
# LangGraph treats the 'llm' as a black box that supports tool-calling
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="You are a helpful personal assistant."
    )

print("Welcome! I'm your personal assistant. I can tell you the current date, time, and weather. I can also calculate mathematical expressions. Type 'quit' to stop.")
while True:
    user_input = input("👤 You: ")
    if user_input.lower() == "quit":
        print("Agent: Goodbye!")
        break
    print("🤖 System call")
    # Capture the result of the invocation
    #agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    #response = agent_executor.invoke({"input": user_input})
    #print("Agent:", response["output"])

    #response = agent.invoke({"input": user_input})

    response = agent.invoke(
        {"messages": [("user", user_input)]} 
    )


    # Access the content of the LAST message in the response
    # In LangGraph, the final AI response is always at the end of the messages list
    print("Agent:", response["messages"][-1].content)