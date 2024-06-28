import tkinter as tk
import os
import tkinter.ttk as ttk

def list_profiles():
    # Scan the current directory for folders starting with 'PROF_' and return their names without this prefix.
    # Useful for displaying a cleaner profile name in the GUI.
    return [d.replace('PROF_', '') for d in os.listdir('.') if os.path.isdir(d) and d.startswith('PROF_')]

def on_profile_select():
    # Callback function for when a profile is selected in the listbox.
    # It updates a tkinter variable with the selected profile's name.
    selected_index = profile_listbox.curselection()  # Get the index of the selected item.
    selected_profile = profile_listbox.get(selected_index)  # Retrieve the profile name from the listbox using the index.
    profile_var.set(selected_profile)  # Update the tkinter variable to reflect the current selection.

def start_simulation():
    # Start the simulation, ensuring a profile is selected first.
    if not profile_listbox.curselection():
        # If no profile is selected, display an error message on the status label.
        status_label.config(text="Please select a profile before you begin simulating.", fg='red', font=('Helvetica', 24, 'bold'))
        return
    selected_profile = profile_listbox.get(profile_listbox.curselection())
    profile_var.set(selected_profile)  # Update the variable with the selected profile
    status_label.config(text=f"Running simulation for {selected_profile}.", fg='black', font=('Helvetica', 24, 'bold'))
    # simulation_start(selected_profile)  # Call the simulation start function with the profile name

def end_simulation():
    # End the simulation and update the status label.
    if not profile_listbox.curselection():
        status_label.config(text="Please select a profile to end simulation.", fg='red', font=('Helvetica', 24, 'bold'))
        return
    selected_profile = profile_listbox.get(profile_listbox.curselection())
    status_label.config(text="Simulation stopped.", font=('Helvetica', 24, 'bold'))
    #simulation_stop(selected_profile)  # Call the simulation stop function with the profile name

# Main application window setup
main_window = tk.Tk()
main_window.title("Patient Simulator")
main_window.attributes('-fullscreen', True)  # Set the application to full screen.

# Title label
title_label = tk.Label(main_window, text="Patient Simulator", font=('Helvetica', 32, 'bold'))
title_label.pack(pady=10)  # Pack the title label at the top of the window with padding.

# Instruction label below the title
instruction_label = tk.Label(main_window, text="Select a profile and select 'Begin Simulation' to start the simulation. Once done simulating, select 'End Simulation' to stop.", font=('Helvetica', 16))
instruction_label.pack(pady=10)  # Provide instructions for the user.

# Frame to contain the Listbox and Scrollbar for profile selection
frame = tk.Frame(main_window)
frame.pack(fill='both', expand=True)  # Pack the frame to fill and expand within the main window for dynamic resizing.

# Listbox for selecting profiles
profile_var = tk.StringVar(main_window)  # Tkinter variable to store the selected profile name.
profiles = list_profiles()  # Get profile names to populate the listbox.
profile_listbox = tk.Listbox(frame, height=6, width=50, font=('Helvetica', 28), justify='center')
profile_listbox.pack(side='left', fill='both', expand=True)  # Pack the Listbox to the left and allow it to fill and expand horizontally.
for profile in profiles:
    profile_listbox.insert(tk.END, profile)  # Populate the Listbox with profile names.
profile_listbox.bind('<<ListboxSelect>>', on_profile_select)  # Bind the selection event to the callback function.

# Scrollbar for the Listbox
scrollbar = ttk.Scrollbar(frame, command=profile_listbox.yview)  # Associate the scrollbar with the Listbox's vertical scroll.
scrollbar.pack(side="left", fill="both", expand='0')  # Pack the scrollbar next to the Listbox, filling vertically.

profile_listbox.config(yscrollcommand=scrollbar.set)  # Link the Listbox's scroll command to the scrollbar.

# Status label to display messages about the simulation state
status_label = tk.Label(main_window, text="", font=('Helvetica', 12))
status_label.pack(pady=5)  # Pack the status label below the Listbox.

# Frame for control buttons (start and end simulation)
buttons_frame = tk.Frame(main_window)
buttons_frame.pack(fill='x', side='bottom')  # Pack the buttons frame at the bottom of the window.

# Start and end simulation buttons
start_button = tk.Button(buttons_frame, text="Begin Simulation", command=start_simulation, font=('Helvetica', 32), bg='green', fg='white')
start_button.pack(side='left', fill='x', expand=True, padx=10, pady=10)  # Start button on the left.

end_button = tk.Button(buttons_frame, text="End Simulation", command=end_simulation, font=('Helvetica', 32), bg='red', fg='white')
end_button.pack(side='right', fill='x', expand=True, padx=10, pady=10)  # End button on the right.

main_window.mainloop()  # Start the Tkinter event loop to keep the application running.
