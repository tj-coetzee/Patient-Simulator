import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# scans the current working directory for directories that are named with the PROF_ prefix, 
# indicating they are profile directories. It extracts and returns a list of profile names 
# by removing the PROF_ prefix.
def list_profiles():
    profiles = []  # Initialize an empty list to hold the profile names
    # Loop through each item in the current working directory
    for item in os.listdir(os.getcwd()):
        # os.path.isdir checks if the item is a directory
        # The 'item.startswith("PROF_")' checks if the directory name starts with 'PROF_'
        if os.path.isdir(os.path.join(os.getcwd(), item)) and item.startswith("PROF_"):
            # If both conditions are true, extract the profile name by removing 'PROF_' prefix
            profile_name = item.replace("PROF_", "")
            # Add the extracted profile name to the 'profiles' list
            profiles.append(profile_name)
    return profiles  # Return the list containing all extracted profile names

# intended to be called when a different profile is selected from the options menu. 
# It clears the current plots from the plot_frame and redraws them based on the newly selected profile.
def on_profile_change(selected_profile):
    # Iterate over each widget (like plots or labels) currently in the 'plot_frame'
    for widget in plot_frame.winfo_children():
        widget.destroy()  # Remove each widget from the 'plot_frame', effectively clearing it

    # Call the 'draw_plots' function to generate and display new plots for the newly selected profile
    draw_plots(selected_profile)

# esponsible for actually generating and displaying the ECG and EMG plots for a given profile name. 
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
    main_window.title('Main Window')  # Set the title of the window
    main_window.geometry('1200x800')  # Set the dimensions of the window

    # Declare 'profile_var' as a global variable to ensure it is accessible throughout the application
    global profile_var
    # Initialize a StringVar to hold the value of the currently selected profile in the OptionMenu
    profile_var = tk.StringVar(main_window)
    
    # Retrieve the list of available profiles
    profile_names = list_profiles()
    # Set the default selected profile in the OptionMenu
    profile_var.set(profile_names[0] if profile_names else "No Profiles")

    # Create a label widget for the "Profiles" section and pack it in the main window
    tk.Label(main_window, text="Profiles", font=('Helvetica', 16)).pack(pady=10)

    # Initialize 'plot_frame' as a global variable to make it accessible in other functions
    global plot_frame
    # Create a Frame widget that will contain the plot widgets
    plot_frame = tk.Frame(main_window)
    plot_frame.pack(fill=tk.BOTH, expand=True)  # Pack the frame to fill the available space and allow expansion

    # Configure the grid layout of 'plot_frame' to have two equally sized columns for ECG and EMG plots
    plot_frame.grid_columnconfigure(0, weight=1)
    plot_frame.grid_columnconfigure(1, weight=1)

    # Draw the initial plots based on the default or first profile in the list
    draw_plots(profile_var.get())

    # Declare 'profile_menu' as a global variable to access it in other functions
    global profile_menu
    # Create an OptionMenu widget for profile selection, with 'profile_var' as the associated variable
    profile_menu = tk.OptionMenu(main_window, profile_var, *profile_names, command=on_profile_change)
    profile_menu.pack(pady=20)  # Pack the OptionMenu in the main window

    # Create a "Profile Manager" button that opens the profile manager window when clicked
    profile_manager_btn = tk.Button(main_window, text="Profile Manager", command=create_profile_manager_window)
    profile_manager_btn.place(relx=0.01, rely=0.95, anchor='sw')  # Position the button at the bottom left

    # Create a "Connect to Device" button for future functionality
    connect_btn = tk.Button(main_window, text="Connect to Device", command=create_connection_window)
    connect_btn.place(relx=0.99, rely=0.95, anchor='se')  # Position the button at the bottom right

    main_window.mainloop()  # Start the Tkinter event loop to make the window responsive


def create_profile_manager_window():
    profile_manager_window = tk.Toplevel()
    profile_manager_window.title('Profile Manager')
    profile_manager_window.geometry('600x400')

    tk.Label(profile_manager_window, text="Profile Name:").pack(pady=(20, 0))
    profile_name_entry = tk.Entry(profile_manager_window)
    profile_name_entry.pack(pady=(0, 20))

    # Function to validate and create the profile
    def create_profile():
        profile_name = profile_name_entry.get()
        if not profile_name:
            messagebox.showerror("Error", "Please enter a profile name.")
            return

        # Create the profile directory structure
        base_path = os.path.join(os.getcwd(), f'PROF_{profile_name}')
        emg_path = os.path.join(base_path, 'EMG')
        ecg_path = os.path.join(base_path, 'ECG')

        # Check if profile already exists
        if os.path.exists(base_path):
            messagebox.showerror("Error", "Profile already exists.")
            return

        os.makedirs(emg_path)
        os.makedirs(ecg_path)

        # Define file dialog options
        filetypes = [("DAT files", "*.dat"), ("HDR files", "*.hdr")]

        # Function to handle file selection and validation
        def select_and_copy_files(folder_path, expected_extensions):
            for ext in expected_extensions:
                file_path = filedialog.askopenfilename(title=f"Select {ext.upper()} file for {folder_path.split('_')[-1]}", filetypes=[(f"{ext.upper()} files", f"*.{ext}")])
                if not file_path or not file_path.endswith(ext):
                    messagebox.showerror("Error", f"Invalid {ext.upper()} file selected. Operation cancelled.")
                    shutil.rmtree(base_path)  # Remove the profile directory if there's an error
                    return False
                shutil.copy(file_path, folder_path)
            return True

        # Select and copy EMG and ECG files
        if not select_and_copy_files(emg_path, ['dat', 'hdr']) or not select_and_copy_files(ecg_path, ['dat', 'hdr']):
            return

        messagebox.showinfo("Success", "Profile created successfully.")
        update_option_menu()  # Update the options menu in the main window

        profile_manager_window.destroy()
        #create_main_window()

    tk.Button(profile_manager_window, text="Create Profile", command=create_profile).pack(pady=20)

def create_connection_window():
    connection_window = tk.Toplevel()
    connection_window.title('Connection')
    connection_window.geometry('1200x800')
    tk.Label(connection_window, text="Device successfully connected").pack(pady=20)
    tk.Button(connection_window, text="Back", command=connection_window.destroy).pack(pady=10)

def wave_plot_ECG(profile_name):
    # Construct path to the header file
    # getcwd is current working directory
    header_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'ECG', 'header.hdr')

    # Check if the header file exists
    if os.path.exists(header_file_path):
        # Read header file
        with open(header_file_path, 'r') as header_file:
            header_lines = header_file.readlines()

        # Extract relevant information from the header
        frontend_gain = float(header_lines[1].split(':')[1].strip())
        scan_rate = float(header_lines[2].split(':')[1].strip())

        # Read binary data file
        data_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'ECG', 'data.dat')
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
            plt.figure(figsize=(5, 3))
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
    header_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'EMG', 'header.hdr')

    # Check if the header file exists
    if os.path.exists(header_file_path):
        # Read header file
        with open(header_file_path, 'r') as header_file:
            header_lines = header_file.readlines()

        # Extract relevant information from the header
        frontend_gain = float(header_lines[1].split(':')[1].strip())
        scan_rate = float(header_lines[2].split(':')[1].strip())

        # Read binary data file
        data_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'EMG', 'data.dat')
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
            plt.figure(figsize=(5, 3))
            plt.plot(time[:8000], emg_data[:8000], color='blue', linestyle='-', linewidth=0.5)  # Adjust line style and color
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (mV)')
            plt.title('EMG Waveform for ' + profile_name)
            plt.grid(True)
            return plt.gcf()
    else:
        print(f"Header file not found for profile '{profile_name}'.")

