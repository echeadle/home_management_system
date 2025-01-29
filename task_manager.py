import json
import argparse
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
from flask import current_app
import os

# Database Configuration
DATABASE_URL = "sqlite:///tasks.db"

#Base for declarative models
Base = declarative_base()
# Define the Task Model
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    task_type = Column(String)
    description = Column(String)
    due_date = Column(DateTime)
    recurrence = Column(String)
    season = Column(String)
    completed = Column(Boolean)

# Create database Engine and session
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine) #Creates tables if needed.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency Injection for the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_task(task_type, description, due_date=None, recurrence=None, season=None, db=None, log_file=None):
    if not db:
        db = next(get_db())
    if due_date:
        due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
    else:
        due_datetime = None
    task = Task(task_type=task_type, description=description, due_date=due_datetime, recurrence=recurrence, season=season, completed=False)
    db.add(task)
    db.commit()
    if log_file:
        with open(log_file, "a") as f:
            f.write(f"Added {task_type} task: {description}\n")
        
def list_tasks(task_type, db=None, log_file=None):
    if not db:
        db = next(get_db())
    tasks = db.query(Task).filter(Task.task_type == task_type).all()
    if log_file:
        with open(log_file, "a") as f:
             f.write(f"list_tasks: {task_type}\n")
             f.write(f"tasks: {tasks}\n")
    if not tasks:
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"No {task_type} tasks.\n")
        return []
    if log_file:
        with open(log_file, "a") as f:
             f.write(f"{task_type.title()} Tasks:\n")
    for index, task in enumerate(tasks):
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"  {index+1}. [ {'x' if task.completed else ' '} ] {task.description}")
                if task.due_date:
                   f.write(f" (Due: {task.due_date.strftime('%Y-%m-%d')})")
                if task.recurrence:
                   f.write(f" (Every: {task.recurrence})")
                if task.season:
                   f.write(f" (Season: {task.season})\n")
    return tasks

def mark_complete(task_type, task_index, db=None, log_file=None):
    if not db:
        db = next(get_db())
    tasks = db.query(Task).filter(Task.task_type == task_type).all()
    try:
        task = tasks[task_index-1]
        task.completed = True
        db.commit()
        if log_file:
             with open(log_file, "a") as f:
                 f.write(f"Marked task {task_index} as complete.\n")
    except IndexError:
        if log_file:
            with open(log_file, "a") as f:
                 f.write(f"Invalid task index\n")
        
def mark_incomplete(task_type, task_index, db=None, log_file=None):
    if not db:
        db = next(get_db())
    tasks = db.query(Task).filter(Task.task_type == task_type).all()
    try:
        task = tasks[task_index-1]
        task.completed = False
        db.commit()
        if log_file:
            with open(log_file, "a") as f:
               f.write(f"Marked task {task_index} as incomplete.\n")
    except IndexError:
        if log_file:
            with open(log_file, "a") as f:
               f.write(f"Invalid task index\n")

def delete_task(task_type, task_index, db=None, log_file=None):
    if not db:
        db = next(get_db())
    tasks = db.query(Task).filter(Task.task_type == task_type).all()
    try:
        task = tasks[task_index-1]
        db.delete(task)
        db.commit()
        if log_file:
            with open(log_file, "a") as f:
                f.write(f"Deleted task {task_index}.\n")
    except IndexError:
       if log_file:
          with open(log_file, "a") as f:
             f.write(f"Invalid task index\n")
        
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
    log_dir = "/app/logs"
    if not os.path.exists(log_dir):
      os.makedirs(log_dir)

    if args.command == "add":
        add_task(args.task_type, args.description, args.due_date, args.recurrence, args.season, log_file="/app/logs/app.log")
    elif args.command == "list":
        list_tasks(args.task_type, log_file="/app/logs/app.log")
    elif args.command == "complete":
        mark_complete(args.task_type, args.task_index, log_file="/app/logs/app.log")
    elif args.command == "incomplete":
        mark_incomplete(args.task_type, args.task_index, log_file="/app/logs/app.log")
    elif args.command == "delete":
        delete_task(args.task_type, args.task_index, log_file="/app/logs/app.log")
    

if __name__ == "__main__":
    main()