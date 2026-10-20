
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from tools import get_overdue_tasks


# 1. Load API key and initialize OpenAI
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 2. Register NELLO's available tools
tools = [
    {
        "type": "function",
        "name": "get_overdue_tasks",
        "description": "Get all overdue, incomplete tasks, sorted by priority.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    }
]


# 3. Determine the greeting
def get_greeting():
    hour = datetime.now().hour

    if hour < 12:
        return "morning"
    elif hour < 17:
        return "afternoon"
    else:
        return "evening"


# 4. Instructions for NELLO
instructions = (
    "You are NELLO, an executive Chief of Staff AI assistant. "
    "Be professional for work-related questions and friendly otherwise. "
    "Use the available tools when necessary. "
    "Never invent task details or claim access to unavailable documents. "
    "Use conversation context to understand follow-up questions."
)


# 5. Track the previous AI response
previous_response_id = None


# 6. Interactive chat loop
while True:

    greeting = get_greeting()
    user_message = input(f"\nGood {greeting}! Ask NELLO: ")

    if user_message.strip().lower() == "exit":
        print("NELLO: See you later!")
        break

    if not user_message.strip():
        continue

    # 7. Send the user's question to OpenAI
    request = {
        "model": "gpt-4.1-nano",
        "instructions": instructions,
        "input": user_message,
        "tools": tools,
        "max_output_tokens": 300
    }

    # Link to the previous response when available
    if previous_response_id is not None:
        request["previous_response_id"] = previous_response_id

    response = client.responses.create(**request)

    # 8. Handle tool calls
    # Continue until the AI produces a final answer
    while True:

        tool_outputs = []

        for item in response.output:

            if item.type == "function_call":

                if item.name == "get_overdue_tasks":
                    print("NELLO requested:", item.name)

                    result = get_overdue_tasks()

                    tool_outputs.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    })

                else:
                    tool_outputs.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps({
                            "error": "Unknown function"
                        })
                    })

        # No tool requests means the AI has finished answering
        if not tool_outputs:
            break

        # Send the tool results back to the AI
        response = client.responses.create(
            model="gpt-4.1-nano",
            instructions=instructions,
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools,
            max_output_tokens=300
        )

    # 9. Display NELLO's final answer
    print("\nNELLO:", response.output_text)

    # 10. Remember the last response for the next question
    previous_response_id = response.id
