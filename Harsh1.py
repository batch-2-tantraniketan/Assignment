import sqlite3
import datetime
import os
import logging
import uuid

# Logging Setup
logging.basicConfig(filename="task_manager.log", level=logging.INFO, format="%(asctime)s %(message)s")

# Database Setup
DB_NAME = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        created_at TEXT,
        due_date TEXT,
        status TEXT
    )''')
    conn.commit()
    conn.close()

# Task Class
class Task:
    def __init__(self, title, description="", due_date=None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.created_at = datetime.datetime.now().isoformat()
        self.due_date = due_date
        self.status = "Pending"

    def save(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?)",
                  (self.id, self.title, self.description, self.created_at, self.due_date, self.status))
        conn.commit()
        conn.close()
        logging.info(f"Task added: {self.title}")

# Task Manager Class
class TaskManager:
    def __init__(self):
        init_db()

    def add_task(self, title, description, due_date):
        task = Task(title, description, due_date)
        task.save()
        print(f"Task '{title}' added.")

    def list_tasks(self, filter_status=None):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        if filter_status:
            c.execute("SELECT * FROM tasks WHERE status = ?", (filter_status,))
        else:
            c.execute("SELECT * FROM tasks")
        rows = c.fetchall()
        conn.close()
        for row in rows:
            print(f"ID: {row[0]}")
            print(f"Title: {row[1]}")
            print(f"Description: {row[2]}")
            print(f"Created: {row[3]}")
            print(f"Due: {row[4]}")
            print(f"Status: {row[5]}")
            print("-" * 40)

    def delete_task(self, task_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        logging.info(f"Task deleted: {task_id}")
        print(f"Task {task_id} deleted.")

    def update_task(self, task_id, field, value):
        if field not in ["title", "description", "due_date", "status"]:
            print("Invalid field.")
            return
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(f"UPDATE tasks SET {field} = ? WHERE id = ?", (value, task_id))
        conn.commit()
        conn.close()
        logging.info(f"Task {task_id} updated field {field} to {value}")
        print("Task updated.")

# CLI Interface
def print_menu():
    print("""
    ==== TASK MANAGER ====
    1. Add Task
    2. List All Tasks
    3. List Pending Tasks
    4. List Completed Tasks
    5. Update Task
    6. Delete Task
    7. Exit
    """)

def main():
    manager = TaskManager()
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            title = input("Title: ")
            description = input("Description: ")
            due = input("Due Date (YYYY-MM-DD) [optional]: ")
            manager.add_task(title, description, due or None)
        elif choice == "2":
            manager.list_tasks()
        elif choice == "3":
            manager.list_tasks(filter_status="Pending")
        elif choice == "4":
            manager.list_tasks(filter_status="Completed")
        elif choice == "5":
            task_id = input("Task ID: ")
            field = input("Field to update (title, description, due_date, status): ")
            value = input("New value: ")
            manager.update_task(task_id, field, value)
        elif choice == "6":
            task_id = input("Task ID to delete: ")
            manager.delete_task(task_id)
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
