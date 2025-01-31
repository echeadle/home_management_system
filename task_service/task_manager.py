import json
import argparse
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
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

def add_task(task_type, description, due_date=None, recurrence=None, season=None, db=None):
    if not db:
        db = next(get_db())
    if due_date:
        due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
    else:
        due_datetime = None
    task = Task(task_type=task_type, description=description, due_date=due_datetime, recurrence=recurrence, season=season, completed=False)
    db.add(task)
    db.commit()
    
def list_tasks(task_type, db=None):
    if not db:
        db = next(get_db())
    tasks = db.query(Task).filter(Task.task_type == task_type).all()
    if not tasks:
        return []
    return tasks

def mark_complete(task_type, task_index, db=None):
    if not db:
        db = next(get_db())
    tasks = db.query(Task).filter(Task.task_type == task_type).all()
    try:
        task = tasks[task_index-1]
        task.completed = True
        db.commit()
    except IndexError:
        print("Invalid task index")
        
def mark_incomplete(task_type, task_index, db=None):
    if not db:
        db = next(get_db())
    tasks = db.query(Task).filter(Task.task_type == task_type).all()
    try:
        task = tasks[task_index-1]
        task.completed = False
        db.commit()
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
    
    args = parser.parse_args()

    if args.command == "add":
        add_task(args.task_type, args.description, args.due_date, args.recurrence, args.season)
    elif args.command == "list":
        list_tasks(args.task_type)
    elif args.command == "complete":
        mark_complete(args.task_type, args.task_index)
    elif args.command == "incomplete":
        mark_incomplete(args.task_type, args.task_index)
    

if __name__ == "__main__":
    main()