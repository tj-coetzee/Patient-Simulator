import PySimpleGUI as sg
import time
import os
import numpy as np
import matplotlib.pyplot as plt

# Sample data for the table
windowsize_x = 1200
windowsize_y = 800

# Function to create the loading window
def create_loading_window():
    loading_layout = [
        [
            sg.Column([ # using column to center the image. cant just center images on their own
                [sg.Image(filename='BST_crop.png', size=(600, 600), key='-LOGO-')],
            ], justification='center')
        ],
        [
            sg.Text('Patient Simulator', font=('Any', 36), justification='center'),
        ],
        [
            sg.ProgressBar(100, size=(40, 20), key='-PROGRESS-', bar_color=('green', 'black')),
        ],
    ]
    return sg.Window('Loading', loading_layout, size=(windowsize_x, windowsize_y), resizable=True)

# Function to create the main window
def generate_prof_entries():
        prof_entries = []
        for folder in os.listdir(os.getcwd()):
            if folder.startswith('PROF_') and os.path.isdir(folder):
                # this is a folder that contains profile data.
                # extract name
                prof_name = folder[5:]

                # check for DAT and HDR file presence
                HDR_exists = os.path.exists(os.path.join(folder, 'header.hdr'))
                DAT_exists = os.path.exists(os.path.join(folder, 'data.dat'))

                # create f string to display information
                table_text = f'{prof_name} - HDR: {"Yes" if HDR_exists else "No"}, DAT: {"Yes" if DAT_exists else "No"}'
                
                # Create a button next to each profile entry
                prof_entries.append([
                    sg.Text(table_text, font=('Any', 14)),
                    sg.Button('Plot', key=f'-PLOT-{prof_name}-', size=(8, 1))  # Button to plot the corresponding profile
                ])
        return prof_entries

def create_main_window():
    layout = [
        [  
            sg.Button("", image_filename='settings_crop.png', image_size=(80, 80), key='-SETTINGS-', border_width=0),
            sg.Button("", image_filename='qm_crop.png', image_size=(80, 80), key='-QUESTION-', border_width=0),
            sg.Text('Profiles', size=(10, 1), font=('Any', 36), justification='center', key='-PROFILES-', background_color='lightgray', expand_x=True),
        ],
        [
            sg.Column([*generate_prof_entries(),], justification='center', key='-PROFILE-ENTRIES-'),
        ],
        [
            sg.Button('Profile Manager', font=('Any', 36), size=(15, 2), key='-PROFILE-MANAGER-', pad=((0, 50), 0)),
            sg.Button('Connect to Device', font=('Any', 36), size=(15, 2), key='-CONNECT-DEVICE-', pad=((50, 0), 0), button_color=('white', 'green')),
        ],
        [
            #[sg.Listbox(values=[], size=(40, 10), key='-PROFILE-LIST-', enable_events=True)],
        ],
    ]

    return sg.Window('main_window', layout, size=(windowsize_x, windowsize_y), resizable=True)

# Function to create the settings window
def create_settings_window():
    settings_layout = [
        [
            sg.Button('Network Settings', font=('Any', 36), size=(15, 2), key='-NETWORK-SETTINGS-', pad=((0, 50), 0)),
            sg.Button('Data Management', font=('Any', 36), size=(15, 2), key='-DATA-MANAGEMENT-', pad=((50, 0), 0)),
        ],
        [
            sg.Button('Back', font=('Any', 36), size=(10, 2), key='-BACK-', button_color=('white', 'blue'), pad=((0, 50), 0)),
        ],
    ]

    return sg.Window('Settings', settings_layout, size=(windowsize_x, windowsize_y), resizable=True)

# Function to create the profile manager window
def create_profile_manager_window():
    profile_manager_layout = [
        [
            sg.Text('Profile Manager', font=('Any', 36), justification='center'),
        ],
        [
            sg.Canvas(size=(800, 5), background_color='black', key='-LINE-'),
        ],
        [
            sg.Button('Create New Profile', font=('Any', 36), size=(15, 2), key='-CREATE-NEW-')
        ],
        [
            sg.Button('Back', font=('Any', 36), size=(10, 2), key='-BACK-', button_color=('white', 'blue'), pad=((0, 50), 0)),
        ],
    ]

    return sg.Window('Profile Manager', profile_manager_layout, size=(windowsize_x, windowsize_y), resizable=True)

# Function to create the create profile window
def create_new_profile_window():
    layout = [
        [
            sg.Text('Create Profile', font=('Any', 36), justification='center'),
        ],
        [
            sg.Canvas(size=(800, 5), background_color='black', key='-LINE-'),
        ],
        [   
            sg.Text('Name of Profile:', font=('Any', 36), justification='left'),
            sg.InputText(key='-PROFILE-NAME-', font=('Any', 36)),
        ],
        [
            sg.Text('Insert Data Here:', font=('Any', 36), justification='left'),
        ],
        [
            sg.Button('HDR File', font=('Any', 36), size=(15, 2), key='-HDR-', pad=((0, 50), 0)),
            sg.Text('', size=(20, 1), key='-HDR-FILE-PATH-', font=('Any', 20)),
            sg.FileBrowse('Browse', font=('Any', 20), key='-HDR-FILE-', target='-HDR-FILE-PATH-', file_types=(("HDR Files", "*.hdr"),)),
        ],
        [
            sg.Button('DAT File', font=('Any', 36), size=(15, 2), key='-DAT-', pad=((0, 50), 0)),
            sg.Text('', size=(20, 1), key='-DAT-FILE-PATH-', font=('Any', 20)),
            sg.FileBrowse('Browse', font=('Any', 20), key='-DAT-FILE-', target='-DAT-FILE-PATH-', file_types=(("DAT Files", "*.DAT"),)),
        ],
        [
            sg.Button('Back', font=('Any', 36), size=(10, 2), key='-BACK-', button_color=('white', 'blue')),
            sg.Button('Save', font=('Any', 36), size=(10, 2), key='-SAVE-', button_color=('white', 'blue')),        
        ],
    ]

    return sg.Window('create_new_profile', layout, size=(windowsize_x, windowsize_y), resizable=True)

# Function to create the connect to device window
def create_connect_to_device_window():
    connect_to_device_layout = [
        [
            sg.Text('Connected!', font=('Any', 36)),
        ],
        [
            sg.Button('Back', font=('Any', 36), size=(10, 2), key='-BACK-', button_color=('white', 'blue')),
        ],
    ]

    return sg.Window('Connect to Device', connect_to_device_layout, size=(windowsize_x, windowsize_y), resizable=True)

# Function to simulate loading
def simulate_loading(window):
    for i in range(101):
        window['-PROGRESS-'].update_bar(i)
        time.sleep(0.05)
        event, values = window.read(timeout=10)
        if event == sg.WIN_CLOSED:
            break

def wave_plot(profile_name):
    # Construct the path to the header file
    header_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'header.hdr')

    # Check if the header file exists
    if os.path.exists(header_file_path):
        # Read header file
        with open(header_file_path, 'r') as header_file:
            header_lines = header_file.readlines()

        # Extract relevant information from the header
        frontend_gain = float(header_lines[1].split(':')[1].strip())
        scan_rate = float(header_lines[2].split(':')[1].strip())
        channels_used = [line.split(':')[0].strip() for line in header_lines[4:]]

        # Read binary data file
        data_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'data.dat')
        if os.path.exists(data_file_path):
            data = np.fromfile(data_file_path, dtype=np.float64)  # Assuming data type is int16

            # Apply gain to the data
            data = data * frontend_gain

            # Create time axis
            time = np.arange(0, len(data) / scan_rate, 1 / scan_rate)

            # Plot ECG and EMG waveforms
            plt.figure(figsize=(10, 6))
            plt.plot(time[:100], data[:100], color='blue', linestyle='-', linewidth=0.5)  # Adjust line style and color
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (mV)')
            plt.title('ECG and EMG Waveforms (First 100 points)')
            plt.grid(True)
            plt.show()
    else:
        print(f"Header file not found for profile '{profile_name}'.")