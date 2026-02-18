import json
import os
import re
from datetime import datetime


# Set Paramters:
#model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
#model_id = "claude-sonnet-4-5-20250929"
#model_id = "claude-3-7-sonnet-20250219"
#model_id = "gpt-4o"
model_id = "gpt-3.5-turbo"

import os
from openai import OpenAI
from dotenv import load_dotenv

_ = load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# client = OpenAI(
#     base_url="https://api.anthropic.com",
#     api_key=os.environ.get("ANTHROPIC_API_KEY")
# )

# Define Tools
def calculate_expression(expression):
    """Calculator: Evaluate a mathematical expression"""
    safe_expr = re.sub(r'[^0-9+\-*/(). ]', '', expression)
    if safe_expr.strip() == "":
        return None
    try:
        return eval(safe_expr)
    except:
        return None

def get_weather(location):
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
            return f"Weather in {city.title()}: {weather}"
    return f"Weather information for {location} is not available in simulation."

def get_date(location=None):
    """Get Date: Get the current date"""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    return f"Today's date is: {date_str}"

def get_time(location=None):
    """Get Time: Get the current time"""
    now = datetime.now()
    time_str = now.strftime("%I:%M:%S %p")
    return f"The current time is: {time_str}"

# Agent Core Function:
def call_llm(user_input, system_message, model_id=model_id):
    """Single LLM call function"""
    try:
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
            ],
        response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
            ],
            max_tokens=1024
        )
        #print(json.dumps(response.model_dump(), indent=2, default=str))
        #print(response.model_dump_json(indent=2))
        # Combine both into a single "full dump" dictionary
        full_dump = {
            "request": {
                "model": model_id,
                "messages": messages  # This includes your user message
            },
            "response": response.model_dump()
        }
        
        # Print the entire structure
        print(json.dumps(full_dump, indent=2, default=str))
        
        # Return the the response
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return None

def call_tool(tool_name, tool_input):
    """Execute a tool function based on tool name"""
    if tool_name == "calculator":
        print("🔧 ... ...Tool: calculator")
        result = calculate_expression(tool_input)
        return f"The result is: {result}" if result is not None else "I couldn't compute that."
    elif tool_name == "get_weather":
        print("🔧 ... ...Tool: get_weather")
        return get_weather(tool_input)
    elif tool_name == "get_date":
        print("🔧 ... ...Tool: get_date")
        return get_date(tool_input)
    elif tool_name == "get_time":
        print("🔧 ... ...Tool: get_time")
        return get_time(tool_input)
    else:
        return f"Unknown tool: {tool_name}"

def query_client(user_input):
    # System message for tool selection and general conversation
    system_message = (
        "You're a helpful personal assistant. Based on the user's message, "
        "decide if you need to use a tool or respond directly.\n\n"
        "If you need a tool, respond ONLY with a JSON object:\n"
        "{ \"tool\": \"calculator\", \"input\": \"5 * (4 + 3)\" }\n"
        "or\n"
        "{ \"tool\": \"get_weather\", \"input\": \"New York\" }\n"
        "or\n"
        "{ \"tool\": \"get_date\", \"input\": \"\" }\n"
        "or\n"
        "{ \"tool\": \"get_time\", \"input\": \"\" }\n\n"
        "If no tool is needed, respond naturally with a helpful message (NOT JSON)."
    )
    
    # Single LLM call
    print("🤖 System call")
    content = call_llm(user_input, system_message)
    if content is None:
        return "Error: Could not connect to the LLM."
    
    # Try to extract JSON from response (if a tool is needed)
    tool = None
    tool_input = None
    
    try:
        tool_call = json.loads(content)
        tool = tool_call.get("tool")
        tool_input = tool_call.get("input")
    except:
        # Try to extract JSON if it's wrapped in markdown or other text
        json_match = re.search(r'\{[^}]+\}', content)
        if json_match:
            try:
                tool_call = json.loads(json_match.group())
                tool = tool_call.get("tool")
                tool_input = tool_call.get("input")
            except:
                pass
    
    # Execute tools if a tool was selected
    if tool:
        return call_tool(tool, tool_input)
    else:
        # No tool needed - return the LLM's natural language response
        return content

print("Welcome! I'm your personal assistant. I can tell you the current date, time, and weather. I can also calculate mathematical expressions. Type 'quit' to stop.")
while True:
    user_input = input("👤 You: ")
    if user_input.lower() == "quit":
        print("Agent: Goodbye!")
        break
    print("Agent:", query_client(user_input))

