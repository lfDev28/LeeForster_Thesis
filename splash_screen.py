import tkinter as tk
from tkinter import ttk
import time

def display_splash_screen(duration=5):
    # Create a root window
    root = tk.Tk()
    root.overrideredirect(True)  # This removes the border and title bar

    # Center the splash screen on the user's screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 500
    window_height = 300
    position_x = (screen_width / 2) - (window_width / 2)
    position_y = (screen_height / 2) - (window_height / 2)
    root.geometry(f"{window_width}x{window_height}+{int(position_x)}+{int(position_y)}")

    # Change the background color or add a background image
    root.configure(bg="blue")

    # Add a fabulous message
    label = ttk.Label(
        root,
        text="Elequant Web is starting up!",
        font=("Arial", 16),
        background="hotpink",
        foreground="white"
    )
    label.pack(expand=True)

    # Show the splash screen for a set duration, then destroy
    root.after(duration * 1000, root.destroy)
    root.mainloop()

display_splash_screen()
