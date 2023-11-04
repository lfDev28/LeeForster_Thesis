import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import webbrowser
import os
import threading

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

def start_celery_on_thread():
    try:
        thread = threading.Thread(target=start_celery)
        thread.start()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Celery. Exception: {e}")
        return
    

def start_celery():
    try:

        # using os.system
        os.system(os.path.join(PROJECT_ROOT, "scripts", "celery_start.bat"))

    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Celery. Exception: {e}")
        return



def start_services():
    services = {
        "backend": [os.path.join(PROJECT_ROOT, "scripts", "backend_start.bat")],
        "frontend": [os.path.join(PROJECT_ROOT, "scripts", "frontend_start.bat")],
    }
    
    start_celery_on_thread()
    
    for service_name, command in services.items():
        try:
            print(f"Starting {service_name}...")
            process = subprocess.Popen(command, cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)

            # Note: We removed the process.communicate() as the process may run indefinitely.
            if process.returncode and process.returncode != 0:  # Only raise an error if we have a return code and it's non-zero
                messagebox.showerror("Error", f"Failed to start {service_name}. Check the console for details.")
                return
            else:
                print(f"{service_name} started successfully.")


        except Exception as e:
            print(f"Exception while starting {service_name}: {e}")
            messagebox.showerror("Error", f"Failed to start {service_name}. Exception: {e}")
            return
    
    webbrowser.open("http://localhost:3000/")
    messagebox.showinfo("Info", "Services Started!")



    



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
