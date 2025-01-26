import json
import argparse
from datetime import datetime, timedelta

TASK_FILE = "tasks.json"

def load_tasks():
    try:
        with open(TASK_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"one_time_tasks": [], "recurring_tasks": [], "seasonal_tasks": []}

def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def add_task(task_type, description, due_date=None, recurrence=None, season=None):
    tasks = load_tasks()
    task = {"description": description, "completed": False}
    if due_date:
        task["due_date"] = due_date
    if recurrence:
        task["recurrence"] = recurrence
    if season:
        task["season"] = season
    
    tasks[task_type].append(task)
    save_tasks(tasks)
    print(f"Added {task_type} task: {description}")
    
def list_tasks(task_type):
    tasks = load_tasks()
    if not tasks[task_type]:
        print(f"No {task_type} tasks.")
        return
    print(f"{task_type.title()} Tasks:")
    for index, task in enumerate(tasks[task_type]):
        print(f"  {index+1}. [ {'x' if task['completed'] else ' '} ] {task['description']}", end="")
        if 'due_date' in task:
            print(f" (Due: {task['due_date']})", end="")
        if 'recurrence' in task:
            print(f" (Every: {task['recurrence']})", end="")
        if 'season' in task:
            print(f" (Season: {task['season']})", end="")
        print("")

def mark_complete(task_type, task_index):
    tasks = load_tasks()
    try:
        task = tasks[task_type][task_index-1]
        task["completed"] = True
        save_tasks(tasks)
        print(f"Marked task {task_index} as complete.")
    except IndexError:
        print("Invalid task index")
        
def mark_incomplete(task_type, task_index):
    tasks = load_tasks()
    try:
        task = tasks[task_type][task_index-1]
        task["completed"] = False
        save_tasks(tasks)
        print(f"Marked task {task_index} as incomplete.")
    except IndexError:
        print("Invalid task index")

def delete_task(task_type, task_index):
    tasks = load_tasks()
    try:
        del tasks[task_type][task_index-1]
        save_tasks(tasks)
        print(f"Deleted task {task_index}.")
    except IndexError:
        print("Invalid task index")
        

def main():
    parser = argparse.ArgumentParser(description="Home Management System")
    subparsers = parser.add_subparsers(title="commands", dest="command")
    
    # Add Task Parser
    add_parser = subparsers.add_parser("add", help="Add a task")
    add_parser.add_argument("task_type", choices=["one_time_tasks", "recurring_tasks", "seasonal_tasks"], help="Type of task")
    add_parser.add_argument("description", help="Task description")
    add_parser.add_argument("--due", dest="due_date", help="Due date for one time tasks (YYYY-MM-DD)")
    add_parser.add_argument("--recurrence", help="Recurrence for recurring tasks (e.g., daily, weekly)")
    add_parser.add_argument("--season", help="Season for seasonal tasks (e.g., spring, summer, fall, winter)")

    # List Task Parser
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("task_type", choices=["one_time_tasks", "recurring_tasks", "seasonal_tasks"], help="Type of task to list")
    
    # Mark Task as Complete Parser
    complete_parser = subparsers.add_parser("complete", help="Mark task as complete")
    complete_parser.add_argument("task_type", choices=["one_time_tasks", "recurring_tasks", "seasonal_tasks"], help="Type of task to complete")
    complete_parser.add_argument("task_index", type=int, help="Index of task to complete")

    # Mark Task as Incomplete Parser
    incomplete_parser = subparsers.add_parser("incomplete", help="Mark task as incomplete")
    incomplete_parser.add_argument("task_type", choices=["one_time_tasks", "recurring_tasks", "seasonal_tasks"], help="Type of task to complete")
    incomplete_parser.add_argument("task_index", type=int, help="Index of task to incomplete")

    # Delete Task Parser
    delete_parser = subparsers.add_parser("delete", help="Delete task")
    delete_parser.add_argument("task_type", choices=["one_time_tasks", "recurring_tasks", "seasonal_tasks"], help="Type of task to delete")
    delete_parser.add_argument("task_index", type=int, help="Index of task to delete")
    
    args = parser.parse_args()

    if args.command == "add":
        add_task(args.task_type, args.description, args.due_date, args.recurrence, args.season)
    elif args.command == "list":
        list_tasks(args.task_type)
    elif args.command == "complete":
        mark_complete(args.task_type, args.task_index)
    elif args.command == "incomplete":
        mark_incomplete(args.task_type, args.task_index)
    elif args.command == "delete":
        delete_task(args.task_type, args.task_index)
    

if __name__ == "__main__":
    main()