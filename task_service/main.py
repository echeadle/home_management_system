from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from task_manager import add_task, list_tasks, mark_complete, mark_incomplete, get_db
from datetime import datetime

app = FastAPI()

class TaskCreate(BaseModel):
    task_type: str
    description: str
    due_date: Optional[str] = None
    recurrence: Optional[str] = None
    season: Optional[str] = None

class Task(BaseModel):
    id: int
    task_type: str
    description: str
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None
    season: Optional[str] = None
    completed: bool
    
@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    add_task(task.task_type, task.description, task.due_date, task.recurrence, task.season)
    return {"message": "Task created"}
    

@app.get("/tasks/{task_type}")
def read_tasks(task_type: str):
    tasks = list_tasks(task_type)
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    return tasks

@app.post("/tasks/{task_type}/{task_index}/complete")
def complete_task(task_type:str, task_index:int):
    mark_complete(task_type, task_index)
    return {"message": f"task {task_index} marked as complete"}

@app.post("/tasks/{task_type}/{task_index}/incomplete")
def incomplete_task(task_type:str, task_index:int):
    mark_incomplete(task_type, task_index)
    return {"message": f"task {task_index} marked as incomplete"}