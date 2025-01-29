from flask import Flask, render_template, request, redirect, url_for
from task_manager import add_task, list_tasks, mark_complete, mark_incomplete, delete_task, get_db
from datetime import datetime
import logging
import os

app = Flask(__name__)
#we will configure the logger using the base app object instead of the python logger.
app.logger.setLevel(logging.DEBUG)
log_dir = "/app/logs"
if not os.path.exists(log_dir):
  os.makedirs(log_dir)
log_file="/app/logs/app.log"

@app.route("/")
def index():
    app.logger.info("index")
    db = next(get_db()) #Get the session
    tasks = {}
    for task_type in ["one_time_tasks", "recurring_tasks", "seasonal_tasks"]:
        tasks[task_type] = list_tasks(task_type, db=db, log_file=log_file) #Pass the session into list_tasks
    app.logger.info(f"tasks: {tasks}")
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add():
    task_type = request.form["task_type"]
    description = request.form["description"]
    due_date = request.form.get("due_date")
    recurrence = request.form.get("recurrence")
    season = request.form.get("season")
    add_task(task_type, description, due_date, recurrence, season, log_file=log_file)
    return redirect(url_for("index"))

@app.route("/complete/<task_type>/<int:task_index>", methods=["POST"])
def complete(task_type, task_index):
    mark_complete(task_type, task_index, log_file=log_file)
    return redirect(url_for("index"))

@app.route("/incomplete/<task_type>/<int:task_index>", methods=["POST"])
def incomplete(task_type, task_index):
    mark_incomplete(task_type, task_index, log_file=log_file)
    return redirect(url_for("index"))

@app.route("/delete/<task_type>/<int:task_index>", methods=["POST"])
def delete(task_type, task_index):
    delete_task(task_type, task_index, log_file=log_file)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")