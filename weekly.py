import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime

# Database setup
conn = sqlite3.connect('work_tracker.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        minutes INTEGER NOT NULL,
        date TEXT NOT NULL
    )
''')
conn.commit()

# Functions to handle GUI actions
def add_task():
    description = description_entry.get()
    try:
        minutes = int(minutes_entry.get())
        date = datetime.date.today().isoformat()
        cursor.execute("INSERT INTO tasks (description, minutes, date) VALUES (?, ?, ?)",
                       (description, minutes, date))
        conn.commit()
        refresh_task_list()
    except ValueError:
        messagebox.showerror("Invalid Input", "Minutes must be an integer.")

def edit_task():
    try:
        selected_item = task_tree.selection()[0]
        task_id = task_tree.item(selected_item)['values'][0]
        new_description = description_entry.get()
        new_minutes = int(minutes_entry.get())
        
        cursor.execute("UPDATE tasks SET description = ?, minutes = ? WHERE id = ?",
                       (new_description, new_minutes, task_id))
        conn.commit()
        refresh_task_list()
    except (IndexError, ValueError):
        messagebox.showerror("Invalid Input", "Select a task and provide valid inputs.")

def fetch_tasks_by_week(week_offset):
    start_date = datetime.date.today() - datetime.timedelta(days=(week_offset * 7 + datetime.date.today().weekday()))
    end_date = start_date + datetime.timedelta(days=6)
    
    cursor.execute("SELECT * FROM tasks WHERE date BETWEEN ? AND ?", 
                   (start_date.isoformat(), end_date.isoformat()))
    return cursor.fetchall()

def refresh_task_list(week_offset=0):
    task_tree.delete(*task_tree.get_children())
    tasks = fetch_tasks_by_week(week_offset)
    for task in tasks:
        task_tree.insert("", tk.END, values=(task[0], task[1], task[2], task[3]))

def next_week():
    global current_week
    current_week += 1
    refresh_task_list(current_week)

def prev_week():
    global current_week
    if current_week > 0:
        current_week -= 1
        refresh_task_list(current_week)

# GUI setup
root = tk.Tk()
root.title("Work Tracker")

current_week = 0

# Description input
tk.Label(root, text="Task Description:").grid(row=0, column=0, padx=10, pady=10)
description_entry = tk.Entry(root, width=40)
description_entry.grid(row=0, column=1, padx=10, pady=10)

# Time spent input
tk.Label(root, text="Time Spent (minutes):").grid(row=1, column=0, padx=10, pady=10)
minutes_entry = tk.Entry(root, width=10)
minutes_entry.grid(row=1, column=1, padx=10, pady=10)

# Buttons
add_button = tk.Button(root, text="Add Task", command=add_task)
add_button.grid(row=2, column=0, padx=10, pady=10)

edit_button = tk.Button(root, text="Edit Task", command=edit_task)
edit_button.grid(row=2, column=1, padx=10, pady=10)

# Task list display
columns = ("ID", "Description", "Minutes", "Date")
task_tree = ttk.Treeview(root, columns=columns, show='headings')
for col in columns:
    task_tree.heading(col, text=col)
task_tree.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Week navigation
prev_button = tk.Button(root, text="Previous Week", command=prev_week)
prev_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

next_button = tk.Button(root, text="Next Week", command=next_week)
next_button.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

# Start the GUI loop
refresh_task_list()
root.mainloop()

# Close database connection when done
conn.close()
