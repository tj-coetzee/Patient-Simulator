import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
import paramiko
from paramiko import SSHClient
from scp import SCPClient
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import glob # used for finding the first HDR and DAT files in directory
import tkinter.ttk as ttk

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
    print(profiles)
    return profiles  # Return the list containing all extracted profile names

# intended to be called when a different profile is selected from the options menu. 
# It clears the current plots from the plot_frame and redraws them based on the newly selected profile.
def on_profile_change(selected_profile):
    # Iterate over each widget (like plots or labels) currently in the 'plot_frame'
    for widget in plot_frame.winfo_children():
        widget.destroy()  # Remove each widget from the 'plot_frame', effectively clearing it

    # Call the 'draw_plots' function to generate and display new plots for the newly selected profile
    draw_plots(selected_profile)

# responsible for actually generating and displaying the ECG and EMG plots for a given profile name. 
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
        plt.close(fig_ECG)  # Close the figure to free memory

    # Repeat a similar process for the EMG plot
    fig_EMG = wave_plot_EMG(profile_name)
    if fig_EMG:  # Check if the figure was successfully created
        canvas_EMG = FigureCanvasTkAgg(fig_EMG, master=plot_frame)
        canvas_widget_EMG = canvas_EMG.get_tk_widget()
        # Position the EMG plot widget next to the ECG plot using grid layout
        canvas_widget_EMG.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        canvas_EMG.draw()  # Render the EMG plot onto the canvas
        plt.close(fig_EMG)  # Close the figure to free memory

# Assuming this variable is global and accessible throughout application
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
    
    # Change to fix the profiles not updating after profile creation
    # Bind the on_profile_change directly as a callback with the profile as an argument
    for profile in updated_profiles:
        # lambda function defines an inline function that captures the current value of 'profile' for each 
        # iteration through the loop. This ensures that when the menu item is selected, it calls 
        # 'on_profile_change' with the correct profile.
        #  
        # 'p=profile' in the lambda function is crucial because it creates a new lambda function
        # for each loop iteration, each with its own 'p' argument that corresponds to the current
        # 'profile'. Without this, all commands would refer to the last item in 'updated_profiles'
        # because of how closures capture variables in Python.
        #
        # The lambda function sets the 'profile_var' to the selected profile and calls
        # 'on_profile_change' to update the plots and other UI elements based on the new profile.
        menu.add_command(label=profile, command=lambda p=profile: on_profile_change(p))

    # Once the OptionMenu is updated, redraw the plots based on the currently selected profile
    # This ensures that the UI reflects the current state and data associated with the selected profile
    draw_plots(profile_var.get())    
    profile_var.set(profile_var.get())

def create_profile_manager_window():
    # Create a new window on top of the main window for profile management
    profile_manager_window = tk.Toplevel()
    profile_manager_window.title('Profile Manager')  # Set the window title
    profile_manager_window.geometry('600x400')  # Set the window size
    tk.Button(profile_manager_window, text="Close", command=profile_manager_window.destroy).pack(pady=10)

    # Create and display a label asking for the profile name
    tk.Label(profile_manager_window, text="Profile Name:").pack(pady=(20, 0))
    # Create an entry widget for the user to input the profile name
    profile_name_entry = tk.Entry(profile_manager_window)
    profile_name_entry.pack(pady=(0, 20))

    # Nested function to validate input and create the new profile
    def create_profile():
        # Retrieve the text entered by the user in the profile name entry widget
        profile_name = profile_name_entry.get()
        if not profile_name:  # If no name is entered, show an error message
            messagebox.showerror("Error", "Please enter a profile name.")
            return
        
        # Check for invalid characters, length, and starting character
        if any(char in profile_name for char in '!@#$%^&()=+[]\{\}\';<>:"/\\|?*') or len(profile_name) >= 30 or profile_name[0].isdigit():
            messagebox.showerror("Error", "Profile name is not valid.")
            return
        
        # Construct the paths for the new profile's directories
        base_path = os.path.join(os.getcwd(), f'PROF_{profile_name}')
        emg_path = os.path.join(base_path, 'EMG')
        ecg_path = os.path.join(base_path, 'ECG')

        # Check if the profile directory already exists to avoid duplicates
        if os.path.exists(base_path):
            messagebox.showerror("Error", "Profile already exists.")
            return

        # Create the directories for the new profile, including subdirectories for EMG and ECG data
        os.makedirs(emg_path)
        os.makedirs(ecg_path)

        # Define accepted file types for file dialogues when selecting .dat and .hdr files
        filetypes = [("DAT files", "*.dat"), ("HDR files", "*.hdr")]

        # Function to handle the selection and validation of data and header files
        def select_and_copy_files(folder_path, expected_extensions):
            for ext in expected_extensions:
                # Open a file dialog for the user to select the appropriate file, filtering by extension
                file_path = filedialog.askopenfilename(title=f"Select {ext.upper()} file for {folder_path.split('_')[-1]}", filetypes=[(f"{ext.upper()} files", f"*.{ext}")])
                if not file_path or not file_path.endswith(ext):  # Validate file selection
                    # Show error and abort the operation if an invalid file is selected
                    messagebox.showerror("Error", f"Invalid {ext.upper()} file selected. Operation cancelled.")
                    shutil.rmtree(base_path)  # Remove the partially created profile directory
                    return False
                shutil.copy(file_path, folder_path)  # Copy the selected file to the new profile's directory
            return True

        # Attempt to select and copy the required files for both EMG and ECG data
        # Abort profile creation if file selection fails for either
        if not select_and_copy_files(emg_path, ['dat', 'hdr']) or not select_and_copy_files((ecg_path), ['dat', 'hdr']):
            return

        # Show a success message once the profile is successfully created
        messagebox.showinfo("Success", "Profile created successfully.")        

        # Update the option menu in the main window to include the new profile
        update_option_menu()
        # Close the profile manager window
        profile_manager_window.destroy()

    # Create a button in the profile manager window to trigger the profile creation process
    tk.Button(profile_manager_window, text="Create Profile", command=create_profile).pack(pady=20)

    # Add button to delete profiles
    tk.Button(profile_manager_window, text="Delete Profiles", command=delete_profiles).pack(pady=20)

def delete_profiles():
    # Create a window to handle profile deletion
    delete_window = tk.Toplevel()
    delete_window.title("Delete Profile")
    delete_window.geometry('400x200')

    tk.Label(delete_window, text="Select a profile to delete:").pack(pady=10)

    # Fetch profiles for deletion
    profiles = list_profiles()
    profile_var = tk.StringVar(delete_window)
    profile_var.set(profiles[0])  # Set default value

    profile_dropdown = ttk.Combobox(delete_window, textvariable=profile_var, values=profiles)
    profile_dropdown.pack(pady=10)

    def confirm_deletion():
        selected_profile = profile_var.get()
        dir_path = os.path.join(os.getcwd(), f'PROF_{selected_profile}')
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {selected_profile}?"):
            shutil.rmtree(dir_path)
            messagebox.showinfo("Deleted", f"Profile {selected_profile} has been deleted.")
            delete_window.destroy()
            update_option_menu()  # Update the menu in the main window if necessary

    tk.Button(delete_window, text="Delete", command=confirm_deletion).pack(pady=20)

def create_connection_window():
    connection_window = tk.Toplevel()
    connection_window.title('Connect to Raspberry Pi')
    connection_window.geometry('400x300')

    # Label and entry for SSH username
    tk.Label(connection_window, text="Username:").pack(pady=(10, 0))
    username_entry = tk.Entry(connection_window)
    username_entry.pack()

    # Label and entry for SSH password, with masked input
    tk.Label(connection_window, text="Password:").pack(pady=(10, 0))
    password_entry = tk.Entry(connection_window, show="*")
    password_entry.pack()

    # Label for displaying connection status
    status_label = tk.Label(connection_window, text="")
    status_label.pack(pady=(10, 0))

    # Function to handle the connection and file transfer
    def connect_and_transfer():
        # Retrieve the username and password from the entries
        username = username_entry.get()
        password = password_entry.get()
        hostname = 'raspberrypi.local'  # Default hostname for Raspberry Pi; replace with IP if necessary

        # Update the status label to show that the connection is in progress
        status_label.config(text="Connecting...")
        connection_window.update_idletasks()  # Force update of window to reflect the label change

        # Verify validity function before transferring files to the embedded system
        def verify_validity(directory_path):
            required_subdirs = {'EMG', 'ECG'}
            required_files = {'.hdr', '.dat'}
            
            # Check for required subdirectories 'EMG' and 'ECG'
            subdirs = {d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))}
            if subdirs != required_subdirs:
                return False
            
            # Check each required subdirectory for the required files
            for subdir in required_subdirs:
                files = set(os.listdir(os.path.join(directory_path, subdir)))
                file_extensions = {os.path.splitext(f)[1] for f in files}
                print(file_extensions)
                if file_extensions != required_files:
                    return False
            return True

        try:
            # Create an SSH client instance
            ssh = SSHClient()
            # SSH client is instructed to automatically accept the host key of the server without any verification or prior knowledge
            # Could pose a problem for MitM attacks, but our implementation is fine.
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, username=username, password=password)

            # Create an SCP client linked to the SSH session
            scp = SCPClient(ssh.get_transport())

            # Execute a command over SSH to list directories in the remote path
            stdin, stdout, stderr = ssh.exec_command('ls /home/pi/')
            existing_directories = stdout.read().decode().split()

            # Updating status label
            status_label.config(text="Connected. Transfering files...")

            # Lists to track the status of each profile being transferred
            transferred = []
            skipped_due_to_invalid = []

            # Iterate over items in the current working directory
            for item in os.listdir(os.getcwd()):
                item_path = os.path.join(os.getcwd(), item)
                if os.path.isdir(os.path.join(os.getcwd(), item)) and item.startswith("PROF_"):
                    if verify_validity(item_path):  # Verify the directory's validity before transferring
                        # If the item is a directory starting with 'PROF_', transfer it. recursive=True makes sure it includes all the subdirectories and files contained
                        scp.put(item_path, recursive=True, remote_path='/home/pi/')
                        transferred.append(item)
                    else:
                        skipped_due_to_invalid.append(item)

            # Close SCP and SSH sessions cleanly
            scp.close()
            ssh.close()

            status_label.config(text="Files transferred successfully!")

            # Build the summary message
            summary_message = "Transfer Summary:\n"
            summary_message += "Successfully transferred: " + ", ".join(transferred) + "\n"
            summary_message += "Skipped (invalid structure): " + ", ".join(skipped_due_to_invalid) + "\n"

            # Display the summary message
            messagebox.showinfo("Transfer Summary", summary_message)
            status_label.config(text="Files transferred successfully!")

        except Exception as e:
            # Display an error message if something goes wrong
            status_label.config(text="Connection Failed: " + str(e))

    # Button to initiate the connection and file transfer process
    tk.Button(connection_window, text="Connect and Transfer", command=connect_and_transfer).pack(pady=20)

def wave_plot_ECG(profile_name):
    # Construct path to the header file
    header_file_path = glob.glob(os.path.join(os.getcwd(), f'PROF_{profile_name}', 'ECG', '*.hdr'))[0]

    # Check if the header file exists
    if os.path.exists(header_file_path):
        # Read header file
        with open(header_file_path, 'r') as header_file:
            header_lines = header_file.readlines()

        # Extract relevant information from the header
        frontend_gain = float(header_lines[1].split(':')[1].strip())
        scan_rate = float(header_lines[2].split(':')[1].strip())
        
        # Read binary data file
        data_file_path = glob.glob(os.path.join(os.getcwd(), f'PROF_{profile_name}', 'ECG', '*.dat'))[0]

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
            plt.figure(figsize=(4.5, 4))
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
    # header_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'EMG', 'header.hdr')

    header_file_path = glob.glob(os.path.join(os.getcwd(), f'PROF_{profile_name}', 'EMG', '*.hdr'))[0]

    # Check if the header file exists
    if os.path.exists(header_file_path):
        # Read header file
        with open(header_file_path, 'r') as header_file:
            header_lines = header_file.readlines()

        # Extract relevant information from the header
        frontend_gain = float(header_lines[1].split(':')[1].strip())
        scan_rate = float(header_lines[2].split(':')[1].strip())

        # Read binary data file
        # data_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'EMG', 'data.dat')
        data_file_path = glob.glob(os.path.join(os.getcwd(), f'PROF_{profile_name}', 'EMG', '*.dat'))[0]

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
            plt.figure(figsize=(4.5, 4))
            plt.plot(time[:8000], emg_data[:8000], color='blue', linestyle='-', linewidth=0.5)  # Adjust line style and color
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (mV)')
            plt.title('EMG Waveform for ' + profile_name)
            plt.grid(True)
            return plt.gcf()
    else:
        print(f"Header file not found for profile '{profile_name}'.")

# Initialize the main application window
main_window = tk.Tk()
main_window.title('Main Window')  # Set the title of the window
main_window.geometry('1400x600')  # Set the dimensions of the window

# Properly handle the window close event. Fix for bug that requires restarting VSCode everytime I run the GUI.
def on_close():
    print("Cleaning up resources...")
    main_window.destroy()  # Properly destroy the window

main_window.protocol("WM_DELETE_WINDOW", on_close)

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
profile_menu.pack(pady=15)  # Pack the OptionMenu in the main window

# Create a "Profile Manager" button that opens the profile manager window when clicked
profile_manager_btn = tk.Button(main_window, text="Profile Manager", command=create_profile_manager_window)
profile_manager_btn.place(relx=0.01, rely=0.95, anchor='sw')  # Position the button at the bottom left

# Create a "Connect to Device" button for future functionality
connect_btn = tk.Button(main_window, text="Connect to Device", command=create_connection_window)
connect_btn.place(relx=0.99, rely=0.95, anchor='se')  # Position the button at the bottom right

main_window.mainloop()  # Start the Tkinter event loop to make the window responsive
