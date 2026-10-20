
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load API key
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is missing!")

client = OpenAI(api_key=api_key)


def generate_briefing(tasks):
    # Convert our tasks into JSON text
    task_data = json.dumps(tasks, indent=2)

    # Ask the LLM to analyze the tasks
    response = client.responses.create(
        model="gpt-4.1-nano",
        instructions=(
            "You are NELLO, an executive Chief of Staff assistant. "
            "Analyze the provided overdue tasks and recommend next actions. "
            "Distinguish verified facts from suggested actions. "
            "Do not invent facts or assume people or teams exist. "
            "Keep the briefing concise and professional."
        ),
        input=f"Generate an executive briefing from these tasks:\n{task_data}",
        max_output_tokens=300,
    )

    return response.output_text
