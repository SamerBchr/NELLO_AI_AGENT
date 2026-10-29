
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
    "You are NELLO, an AI Chief of Staff and executive assistant. "
    "Be professional for work-related questions and friendly otherwise. "
    "Respond in the language the user is currently using unless asked otherwise. "
    "Use available tools when necessary. "
    "Never invent task details, documents, or information. "
    "Keep task IDs internal unless the user explicitly asks for them. "
    "Only claim to have completed actions when a tool has successfully performed them. "
    "Never offer to modify tasks, send reminders, or update documents unless the required tools are available. "
    "You may suggest drafting text, but clearly distinguish drafting from executing an action. "
    "Use conversation context to understand follow-up questions."
)


# 5. Track conversation context
previous_response_id = None


# 6. Greet the user ONCE when NELLO starts
print(f"\nNELLO: Good {get_greeting()}! How can I help you today?")


# 7. Interactive chat loop
while True:

    user_message = input("\nYou: ")

    if user_message.strip().lower() == "exit":
        print("\nNELLO: See you later!")
        break

    if not user_message.strip():
        continue

    # 8. Prepare the first API request
    request = {
        "model": "gpt-5-nano",
        "instructions": instructions,
        "input": user_message,
        "tools": tools,
        "reasoning": {"effort": "minimal"},
        "max_output_tokens": 1000
    }

    # Link this request to the previous conversation
    if previous_response_id is not None:
        request["previous_response_id"] = previous_response_id

    # 9. Send the user's message to OpenAI
    try:
        response = client.responses.create(**request)

    except Exception as error:
        print("\nNELLO: I couldn't connect to the AI service. Please try again.")
        print(f"Technical details: {error}")
        continue

    # 10. Handle tool calls
    api_failed = False
    max_tool_rounds = 5
    tool_rounds = 0

    while True:

        tool_outputs = []

        for item in response.output:

            if item.type == "function_call":

                if item.name == "get_overdue_tasks":
                    print("NELLO requested:", item.name)

                    try:
                        result = get_overdue_tasks()

                    except Exception as error:
                        result = {
                            "error": str(error)
                        }

                else:
                    result = {
                        "error": f"Unknown function: {item.name}"
                    }

                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps(result)
                })

        # No more tool calls: the AI has finished
        if not tool_outputs:
            break

        # Prevent endless tool-calling loops
        if tool_rounds >= max_tool_rounds:
            print("\nNELLO: I reached the tool-processing limit. Please try again.")
            api_failed = True
            break

        tool_rounds += 1

        # 11. Send tool results back to OpenAI
        try:
            response = client.responses.create(
                model="gpt-5-nano",
                instructions=instructions,
                previous_response_id=response.id,
                input=tool_outputs,
                tools=tools,
                reasoning={"effort": "minimal"},
                max_output_tokens=1000
            )

        except Exception as error:
            print("\nNELLO: Something went wrong while processing the task results.")
            print(f"Technical details: {error}")
            api_failed = True
            break

    # Return to the user prompt if tool processing failed
    if api_failed:
        continue

    # 12. Handle empty or incomplete responses
    if not response.output_text:
        print("\nNELLO: I couldn't generate an answer. Please try again.")
        continue

    # 13. Display NELLO's final answer
    print("\nNELLO:", response.output_text)

    # 14. Save conversation context for the next question
    previous_response_id = response.id
