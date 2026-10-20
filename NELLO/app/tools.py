
import json
from pathlib import Path
from datetime import date

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_tasks.json"

def get_overdue_tasks():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        tasks = json.load(file)

    today = date.today()
    overdue_tasks = []

    for task in tasks:
        deadline = date.fromisoformat(task["deadline"])

        if task["status"] != "completed" and deadline < today:
            days_overdue = (today - deadline).days
            task["days_overdue"] = days_overdue
            overdue_tasks.append(task)

    priority_rank = {"high": 3, "medium": 2, "low": 1}

    overdue_tasks.sort(
        key=lambda task: (
            priority_rank.get(task["priority"], 0),
            task["days_overdue"]
        ),
        reverse=True
    )

    return overdue_tasks
