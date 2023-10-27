import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import webbrowser
import os

CONFIG_FILE = "config.txt"

def get_project_root():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return f.read().strip()
    else:
        root = filedialog.askdirectory(title="Select ElEquant_Web Project Root Directory")
        with open(CONFIG_FILE, "w") as f:
            f.write(root)
        return root

PROJECT_ROOT = get_project_root()

def start_services():
    # Try starting backend service
    try:
        subprocess.Popen([os.path.join(PROJECT_ROOT, "scripts", "backend_start.bat")], shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


        # Try starting frontend services
        subprocess.Popen([os.path.join(PROJECT_ROOT, "scripts", "frontend_start.bat")], shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    

        # Try starting celery service
        subprocess.Popen([os.path.join(PROJECT_ROOT, "scripts", "celery_start.bat")], shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        messagebox.showinfo("Info", "Services Started!")
        webbrowser.open("http://localhost:3000/")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start a service. Error: {e}")

def stop_services():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"])
        subprocess.run(["taskkill", "/F", "/IM", "node.exe", "/T"])
        messagebox.showinfo("Info", "Services Stopped!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to stop a service. Error: {e}")

app = tk.Tk()
app.title("Service Controller")

frame = tk.Frame(app)
frame.pack(padx=10, pady=10)


# Directory text for debugging
dir_text = tk.StringVar()
dir_text.set(PROJECT_ROOT)
start_btn = tk.Button(frame, text="Start All Services", command=start_services)
start_btn.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

stop_btn = tk.Button(frame, text="Stop All Services", command=stop_services)
stop_btn.pack(fill=tk.BOTH, expand=True)

app.mainloop()
