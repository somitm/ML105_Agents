import os

# Set Parameters
#model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
model_id = "gpt-3.5-turbo"

import os
from openai import OpenAI
from dotenv import load_dotenv

_ = load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

# Loop until user enters "quit"
while True:
    # Query to send to Claude
    query = input("👤 Enter your query (or 'quit' to exit): ")
    
    # Check if user wants to quit
    if query.lower() == "quit":
        print("Goodbye!")
        break
    
    # Make the API call using Converse API
    try:
        print("🤖 System call")
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=1024
        )
        
        # Extract and print the response
        output = response.choices[0].message.content
        print(f"👤 Query: {query}")
        print(f"\nResponse:\n{output}\n")
        
    except Exception as e:
        print(f"Error calling OpenAI: {e}\n")

