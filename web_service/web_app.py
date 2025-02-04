from flask import Flask, render_template, request, redirect, url_for
import logging
import requests
import os

app = Flask(__name__)
task_service_url = "http://task_service:8000"
manual_service_url = "http://manual_reader_service:8001"

def get_tasks(task_type):
    try:
        response = requests.get(f"{task_service_url}/tasks/{task_type}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting tasks: {e}")
        return []
    

def add_task(task_type, description, due_date=None, recurrence=None, season=None):
    try:
        data = {"task_type": task_type, "description": description}
        if due_date:
            data["due_date"] = due_date
        if recurrence:
            data["recurrence"] = recurrence
        if season:
            data["season"] = season
        response = requests.post(f"{task_service_url}/tasks", json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error adding tasks: {e}")
        return False

def complete_task(task_type, task_index):
    try:
        response = requests.post(f"{task_service_url}/tasks/{task_type}/{task_index}/complete")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error completing task: {e}")
        return False

def incomplete_task(task_type, task_index):
    try:
        response = requests.post(f"{task_service_url}/tasks/{task_type}/{task_index}/incomplete")
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error incompleting task: {e}")
        return False

def add_manual(appliance_name, file_path):
     try:
          data = {"appliance_name": appliance_name, "file_path": file_path}
          response = requests.post(f"{manual_service_url}/manuals", json=data)
          response.raise_for_status()
          return True
     except requests.exceptions.RequestException as e:
          print(f"Error adding manual: {e}")
          return False
      
def query_manual(appliance_name, query):
    try:
        data = {"query": query}
        response = requests.post(f"{manual_service_url}/query/{appliance_name}", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying manual: {e}")
        return None


@app.route("/", methods=["GET", "POST"])
def index():
    tasks = {}
    for task_type in ["one_time_tasks", "recurring_tasks", "seasonal_tasks"]:
        tasks[task_type] = get_tasks(task_type)
    results = None
    if request.method == "POST":
        if "manual" in request.files:
            manual = request.files["manual"]
            if manual.filename != "":
                manual_path = os.path.join("/app/manuals", manual.filename)
                manual.save(manual_path)
                add_manual(request.form["appliance_name"], manual_path)
        elif "query" in request.form:
             results = query_manual(request.form["appliance_name"], request.form["query"])
    return render_template("index.html", tasks=tasks, results=results)


@app.route("/add", methods=["POST"])
def add():
    task_type = request.form["task_type"]
    description = request.form["description"]
    due_date = request.form.get("due_date")
    recurrence = request.form.get("recurrence")
    season = request.form.get("season")
    add_task(task_type, description, due_date, recurrence, season)
    return redirect(url_for("index"))

@app.route("/complete/<task_type>/<int:task_index>", methods=["POST"])
def complete(task_type, task_index):
    complete_task(task_type, task_index)
    return redirect(url_for("index"))

@app.route("/incomplete/<task_type>/<int:task_index>", methods=["POST"])
def incomplete(task_type, task_index):
    incomplete_task(task_type, task_index)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")