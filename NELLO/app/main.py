
from tools import get_overdue_tasks
from llm import generate_briefing

def main():
    print("NELLO — Your AI Chief of Staff")
    print("------------------------------")

    overdue_tasks = get_overdue_tasks()

    print(f"Found {len(overdue_tasks)} overdue tasks.")

    if not overdue_tasks:
        print("No overdue tasks!")
        return

    print("\nGenerating AI briefing...\n")

    briefing = generate_briefing(overdue_tasks)

    print(briefing)


if __name__ == "__main__":
    main()
