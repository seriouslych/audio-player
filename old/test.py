import tkinter as tk
from tkinter import ttk

# Global variables to track times
last_user_change_time = None
last_programmatic_change_time = None

def on_slider_change(value):
    global last_user_change_time, last_programmatic_change_time
    current_time = root.tk.call('clock', 'clicks')
    if last_programmatic_change_time and current_time - last_programmatic_change_time < 1000:
        # If the last change was within the last second, it's probably programmatic
        print("Slider changed programmatically:", value)
    else:
        print("Slider changed by user:", value)
    last_user_change_time = current_time

def update_timer():
    global last_programmatic_change_time
    current_time = root.tk.call('clock', 'clicks')
    last_programmatic_change_time = current_time
    root.after(1000, update_timer)

def set_slider_value(value):
    global last_programmatic_change_time
    last_programmatic_change_time = root.tk.call('clock', 'clicks')
    slider.set(value)

# Create the main application window
root = tk.Tk()
root.title("Slider Example")

# Create the slider widget
slider = ttk.Scale(root, from_=0, to=100, orient='horizontal', command=on_slider_change)
slider.pack()

# Start the timer to update the programmatic change time
update_timer()

# Simulate a programmatic change
root.after(1000, lambda: set_slider_value(50))

# Run the Tkinter main loop
root.mainloop()
