import tkinter as tk  # Import Tkinter module for GUI development
from tkinter import ttk  # Import themed Tkinter for additional widgets and styling
import time 
from functions_tkinter import * 

def show_main_window():
    loading_window.destroy()  # destroys loading window, effectively closing it
    create_main_window()  # Calls a function to create and display the main application window

def update_progress():
    for i in range(10):
        time.sleep(0.2)  # Pauses the program for 0.2 second, simulating a loading process
        progress_bar['value'] += 20  # Increases the progress bar value by 20 on each iteration
        loading_window.update_idletasks()  # Processes any pending tasks, updates the progress bar visually
    show_main_window()  # Once the loop is done, calls the function to show the main application window

# Create a new Tkinter window for loading
loading_window = tk.Tk()
loading_window.title('Loading')  # title of the window
loading_window.geometry('1200x800')  # size of the window

# Load and display the logo
logo_image = tk.PhotoImage(file="BST.png")  # Loads the logo image
logo_label = tk.Label(loading_window, image=logo_image)  # Creates a label widget for displaying the image within the loading window
logo_label.pack(pady=20)  # Packs the label into the window, with some padding on the vertical axis for spacing

# Initialize a progress bar
progress_bar = ttk.Progressbar(loading_window, orient='horizontal', length=280, mode='determinate')
# 'orient': orientation of the progress bar (horizontal/vertical)
# 'length': length of the progress bar
# 'mode' set to 'determinate': progress bar shows the amount of work completed

progress_bar.pack(pady=20)  # Packs progress bar into the window, with vertical padding
progress_bar['value'] = 0  # Initialize progress bar value to 0

loading_window.after(100, update_progress)  # After 100 milliseconds, call the update_progress function to start simulating the loading process

def on_close():
    print("Loading window closed")  # Optional: Confirm the window is closing
    loading_window.quit()  # Ends the mainloop
    loading_window.destroy()  # Destroys the window, freeing up resources

loading_window.protocol("WM_DELETE_WINDOW", on_close)  # Bind the closing event

loading_window.mainloop()  # Starts the Tkinter event loop, which is necessary for the window to display and interact with the user

