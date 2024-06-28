import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

# scans the current working directory for directories that are named with the PROF_ prefix, 
# indicating they are profile directories. It extracts and returns a list of profile names 
# by removing the PROF_ prefix.
def list_profiles() -> "list[str]":
    profiles : list[str] = []  # Initialize an empty list to hold the profile names
    # Loop through each item in the current working directory
    for item in os.listdir(os.path.join(os.getcwd(), 'Profiles')):
        # os.path.isdir checks if the item is a directory
        # The 'item.startswith("PROF_")' checks if the directory name starts with 'PROF_'
        if os.path.isdir(os.path.join(os.getcwd(), 'Profiles', item)) and item.startswith("PROF_"):
            # If both conditions are true, extract the profile name by removing 'PROF_' prefix
            profile_name = item.replace("PROF_", "")
            # Add the extracted profile name to the 'profiles' list
            profiles.append(profile_name)
    return profiles  # Return the list containing all extracted profile names


def on_profile_change(selected_profile):
    # Iterate over each widget (like plots or labels) currently in the 'plot_frame'
    for widget in plot_frame.winfo_children():
        widget.destroy()  # Remove each widget from the 'plot_frame', effectively clearing it

    # Call the 'draw_plots' function to generate and display new plots for the newly selected profile
    draw_plots(selected_profile)

# Responsible for generating and displaying the ECG and EMG plots for a given profile name. 
# It first clears any existing plots, then uses the wave_plot_ECG and wave_plot_EMG functions to 
# generate the plots, and finally embeds these plots into the plot_frame within the Tkinter window.
def draw_plots(profile_name):
    # Similar to 'on_profile_change', clear any existing widgets from 'plot_frame'
    for widget in plot_frame.winfo_children():
        widget.destroy()

    # Generate an ECG plot figure for the selected profile by calling 'wave_plot_ECG'
    fig_ECG = wave_plot_ECG(profile_name)
    if fig_ECG:  # Check if the figure was successfully created
        # Embed the Matplotlib figure in the Tkinter window using FigureCanvasTkAgg
        canvas_ECG = FigureCanvasTkAgg(fig_ECG, master=plot_frame)
        # Convert the canvas into a Tkinter widget
        canvas_widget_ECG = canvas_ECG.get_tk_widget()
        # Position the ECG plot widget in the 'plot_frame' using grid layout
        canvas_widget_ECG.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        canvas_ECG.draw()  # Render the ECG plot onto the canvas

    # Repeat a similar process for the EMG plot
    fig_EMG = wave_plot_EMG(profile_name)
    if fig_EMG:  # Check if the figure was successfully created
        canvas_EMG = FigureCanvasTkAgg(fig_EMG, master=plot_frame)
        canvas_widget_EMG = canvas_EMG.get_tk_widget()
        # Position the EMG plot widget next to the ECG plot using grid layout
        canvas_widget_EMG.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        canvas_EMG.draw()  # Render the EMG plot onto the canvas


# Assuming this variable is global and accessible throughout your application
main_window = None  # Initialize the main window variable
    

def update_option_menu():
    global profile_menu
    # Retrieve the latest list of profiles by scanning the directory for 'PROF_' folders
    updated_profiles = list_profiles()
    
    # Set the first profile in the list as the default selected value in the OptionMenu
    profile_var.set(updated_profiles[0])  
    
    # Access the menu component of the OptionMenu widget to manipulate its entries
    menu = profile_menu['menu']
    
    # Remove all existing entries in the OptionMenu to prepare for updating it with new values
    menu.delete(0, 'end')  
    
    # Loop through the list of updated profiles
    for profile in updated_profiles:
        # For each profile, add a new command to the OptionMenu.
        # The command updates 'profile_var' with the selected profile when the user selects an option.
        # 'tk._setit' is a helper function that creates a command to set a Tkinter variable.
        menu.add_command(label=profile, command=tk._setit(profile_var, profile))
    
    # Once the OptionMenu is updated, redraw the plots based on the currently selected profile
    # This ensures that the UI reflects the current state and data associated with the selected profile
    draw_plots(profile_var.get())


def create_main_window():
    # Initialize the main application window
    main_window = tk.Tk()
    #main_window.attributes('-fullscreen',True)
    main_window.title('Patient Simulator Home')  # Set the title of the window
    main_window.geometry('1200x800')  # Set the dimensions of the window

    main_window_welcome_message = 'Welcome to the BioSim Tech Patient Simulator!\n'
    main_window_instruction_message = 'Press the "Simulation" button to begin.'
    main_window_str : tk.StringVar = tk.StringVar(value=main_window_welcome_message+main_window_instruction_message)
    main_window_label : tk.Label = tk.Label(main_window, 
                                            textvariable=main_window_str, 
                                            width=100, 
                                            font=17
                                            )
    main_window_label.pack(pady=20)

    global profile_var
    # Initialize a StringVar to hold the value of the currently selected profile in the OptionMenu
    profile_var = tk.StringVar(main_window)
    
    # Retrieve the list of available profiles
    profile_names = list_profiles()
    # Set the default selected profile in the OptionMenu
    profile_var.set(profile_names[0] if profile_names else "No Profiles")

    # Create a "Simulation" button
    sim_button = tk.Button(main_window, 
                           text="Simulation",
                           background='green1',
                           width=8,
                           height=5, 
                           command=create_simulation_window
                           )
    sim_button.place(relx=0.89, rely=0.95, anchor='se')  # Position the button at the bottom right
    # Add a "Quit" button to exit program
    quit_btn = tk.Button(main_window, 
                         background='firebrick1',
                         text="Quit", 
                         width= 5,
                         height= 5,
                         command=lambda : quit_program(main_window)
                         )
    quit_btn.place(relx=0.10, rely = 0.95, anchor="sw") # Position the button at the top right

    main_window.mainloop()  # Start the Tkinter event loop to make the window responsive


# Boolean variable used in create_simulation_window()
# Determines state of simulation (on/off)
is_running = False

def create_simulation_window():
    # Simulation button
    simulation_btn : tk.Button = None
    # Create a new top-level window for the simulation window
    simulation_window = tk.Toplevel()
    simulation_window.title('Patient Simulator')  # Set the window title
    simulation_window.geometry('1200x800')  # Set the window size

    # Initialize 'plot_frame' as a global variable to make it accessible in other functions
    global plot_frame
    # Create a Frame widget that will contain the plot widgets
    plot_frame = tk.Frame(simulation_window)
    plot_frame.pack(fill=tk.BOTH, expand=True)  # Pack the frame to fill the available space and allow expansion

    # Configure the grid layout of 'plot_frame' to have two equally sized columns for ECG and EMG plots
    plot_frame.grid_columnconfigure(0, weight=1)
    plot_frame.grid_columnconfigure(1, weight=1)

    # Draw the initial plots based on the default or first profile in the list
    draw_plots(profile_var.get())

    # Create StringVar object that will update based on state of simulation (running/off)
    simulation_window_str : tk.StringVar = tk.StringVar(value="Select a profile with the dropdown menu and press \"Run\" to start simulation.")
    simulation_label : tk.Label = tk.Label(simulation_window, 
                                           textvariable=simulation_window_str, 
                                           width=100,
                                           font=30
                                           )
    simulation_label.pack(pady=20)

    # Retrieve the list of available profiles
    profile_names = list_profiles()
    # Declare 'profile_menu' as a global variable to access it in other functions
    global profile_menu
    # Create an OptionMenu widget for profile selection, with 'profile_var' as the associated variable
    profile_menu = tk.OptionMenu(simulation_window, 
                                 profile_var, 
                                 *profile_names, 
                                 command=on_profile_change
                                 )
    profile_menu.pack(pady=20)  # Pack the OptionMenu in the main window

    # Create a 'Back' button to close the simulation window
    back_btn : tk.Button = tk.Button(simulation_window,text="Back", 
                                     width=3, 
                                     heigh=3, 
                                     command=simulation_window.destroy
                                     )
    back_btn.pack(pady=10)
    back_btn.place(relx=0.10, rely=0.95, anchor='sw')

    simulation_btn_str = tk.StringVar(value='Run')
    simulation_btn = tk.Button(simulation_window, 
                               activebackground="green4", 
                               bg='green', 
                               textvariable=simulation_btn_str, 
                               command=lambda : update_simulation_window(is_running),
                               height=5,
                               width=5
                               )
    simulation_btn.pack()


    def update_simulation_window(status : bool) -> None:
        # Global variable is_running
        global is_running, profile_var
        # Switch button and label text based on simulation state
        if not status:
            is_running = True
            simulation_window_str.set(f'Simulating {profile_var.get()}...')
            simulation_btn_str.set('Stop')
            simulation_btn.configure(activebackground='red3', bg='red', textvariable=simulation_btn_str) 
            start_simulation()
        else:
            is_running = False
            end_simulation()
            time.sleep(1)
            simulation_window_str.set('Select a profile with the dropdown menu and press "Run" to start simulation.')
            simulation_btn_str.set('Run')
            simulation_btn.configure(activebackground="green4", bg='green', textvariable=simulation_btn_str) 
            
            
            
        simulation_label.configure(textvariable=simulation_window_str)
        

def wave_plot_ECG(profile_name):
    # Construct path to the header file
    # getcwd is current working directory
    header_file_path = os.path.join(os.getcwd(), 'Profiles', f'PROF_{profile_name}', 'ECG', 'header.hdr')

    # Check if the header file exists
    if os.path.exists(header_file_path):
        # Read header file
        with open(header_file_path, 'r') as header_file:
            header_lines = header_file.readlines()

        # Extract relevant information from the header
        frontend_gain = float(header_lines[1].split(':')[1].strip())
        scan_rate = float(header_lines[2].split(':')[1].strip())

        # Read binary data file
        data_file_path = os.path.join(os.getcwd(), 'Profiles', f'PROF_{profile_name}', 'ECG', 'data.dat')
        if os.path.exists(data_file_path):
            # Read data from channel one
            with open(data_file_path, 'rb') as data_file:
                # Skip to the start of channel one data
                data_file.seek(0)  # Assuming data format starts at the beginning of the file
                # Read the data from channel one
                ecg_data = np.fromfile(data_file, dtype=np.float64)  # Assuming data type is float64

            # Apply gain to the data
            ecg_data = ecg_data * frontend_gain

            # Create time axis
            time = np.arange(0, len(ecg_data) / scan_rate, 1 / scan_rate)

            # Plot ECG waveform
            plt.figure(figsize=(5, 4))
            plt.plot(time[:8000], ecg_data[:8000], color='blue', linestyle='-', linewidth=0.5)  # Adjust line style and color
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (mV)')
            plt.title('ECG Waveform for ' + profile_name)
            plt.grid(True)
            return plt.gcf()
    else:
        print(f"Header file not found for profile '{profile_name}'.")

def wave_plot_EMG(profile_name):
    # Construct path to the header file
    # getcwd is current working directory
    header_file_path = os.path.join(os.getcwd(), 'Profiles', f'PROF_{profile_name}', 'EMG', 'header.hdr')

    # Check if the header file exists
    if os.path.exists(header_file_path):
        # Read header file
        with open(header_file_path, 'r') as header_file:
            header_lines = header_file.readlines()

        # Extract relevant information from the header
        frontend_gain = float(header_lines[1].split(':')[1].strip())
        scan_rate = float(header_lines[2].split(':')[1].strip())

        # Read binary data file
        data_file_path = os.path.join(os.getcwd(), 'Profiles', f'PROF_{profile_name}', 'EMG', 'data.dat')
        if os.path.exists(data_file_path):
            # Read data from channel one
            with open(data_file_path, 'rb') as data_file:
                # Skip to the start of channel one data
                data_file.seek(0)  # Assuming data format starts at the beginning of the file
                # Read the data from channel one
                emg_data = np.fromfile(data_file, dtype=np.float64)  # Assuming data type is float64

            # Apply gain to the data
            emg_data = emg_data * frontend_gain

            # Create time axis
            time = np.arange(0, len(emg_data) / scan_rate, 1 / scan_rate)

            # Plot ECG waveform
            plt.figure(figsize=(5, 4))
            plt.plot(time[:8000], emg_data[:8000], color='blue', linestyle='-', linewidth=0.5)  # Adjust line style and color
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (mV)')
            plt.title('EMG Waveform for ' + profile_name)
            plt.grid(True)
            return plt.gcf()
    else:
        print(f"Header file not found for profile '{profile_name}'.")

def start_simulation() -> None:
    pass

def end_simulation() -> None:
    pass

# Delete tk.Tk window object and exit program
def quit_program(window : tk.Tk) -> None:
    # Pop up message to check if user wants to exit program
    end_program : bool = messagebox.askyesno(title='End Program', message='Are you sure you want to quit BST Simulator?')
    if end_program:
        print("Closing program...")
        #time.sleep(1.5)
        window.quit()
        time.sleep(0.1)
        quit()
