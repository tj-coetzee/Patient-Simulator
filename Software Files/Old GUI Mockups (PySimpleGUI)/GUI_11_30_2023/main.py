import PySimpleGUI as sg
import time

# Sample data for the table
data = [
    ['John', '123', '2023-11-15 10:30:00'],
    ['Jane', '456', '2023-11-15 11:45:00'],
    ['Bob', '789', '2023-11-25 09:15:00'],
    ['Lou', '818', '2022-11-6 11:30:00'],
    ['Greg', '341', '2021-1-5 01:31:00'],
    ['May', '992', '2023-12-15 08:23:00'],
    # Add more rows as needed
]

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
    return sg.Window('Loading', loading_layout, size=(1200, 800), resizable=True)

# Function to simulate loading
def simulate_loading(window):
    for i in range(101):
        window['-PROGRESS-'].update_bar(i)
        time.sleep(0.05)
        event, values = window.read(timeout=10)
        if event == sg.WIN_CLOSED:
            break

# Function to create the main window
def create_main_window():
    layout = [
        [  
            sg.Button("", image_filename='settings_crop.png', image_size=(80, 80), key='-SETTINGS-', border_width=0),
            sg.Button("", image_filename='qm_crop.png', image_size=(80, 80), key='-QUESTION-', border_width=0),
            sg.Text('Profiles', size=(10, 1), font=('Any', 36), justification='center', key='-PROFILES-', background_color='lightgray', expand_x=True),
        ],
        [
            sg.Column([
                [sg.Table(values=data, headings=['Name', 'Data', 'Last Updated'], auto_size_columns=True, justification='center', num_rows=min(25, len(data)), key='-TABLE-', size=(800, 400))],
            ], justification='center')
        ],
        [
            sg.Button('Profile Manager', font=('Any', 36), size=(15, 2), key='-PROFILE-MANAGER-', pad=((0, 50), 0)),
            sg.Button('Connect to Device', font=('Any', 36), size=(15, 2), key='-CONNECT-DEVICE-', pad=((50, 0), 0), button_color=('white', 'green')),
        ],
    ]

    return sg.Window('main_window', layout, size=(1200, 800), resizable=True)

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

    return sg.Window('Settings', settings_layout, size=(1200, 800), resizable=True)

# Function to create the profile manager window
def create_profile_manager_window():
    profile_manager_layout = [
        [
            sg.Text('Import Profiles', font=('Any', 36), justification='center'),
        ],
        [
            sg.Canvas(size=(800, 5), background_color='black', key='-LINE-'),
        ],
        [
            sg.Column([
                [sg.Text('Import via simulator/profiles folder', font=('Any', 28))],
                [sg.Button('Refresh Profiles', font=('Any', 28), size=(15, 2), key='-REFRESH-')],
                [sg.Canvas(size=(340, 150), background_color='lightgray', key='-EMPTY-BOX-')],
            ], justification='left', size=(400, 500)),
            sg.Column([
                [sg.Button('Create New Profile', font=('Any', 36), size=(15, 2), key='-CREATE-NEW-')],
            ], justification='right', size=(400, 500)),
        ],
        [
            sg.Button('Back', font=('Any', 36), size=(10, 2), key='-BACK-', button_color=('white', 'blue'), pad=((0, 50), 0)),
        ],
    ]

    return sg.Window('Import Profiles', profile_manager_layout, size=(1200, 800), resizable=True)

""" Function to create the create profile window
def create_create_profile_window():
    layout = [
        [
            sg.Text('Create Profile', font=('Any', 36), justification='center'),
        ],
        [
            sg.Canvas(size=(800, 5), background_color='black', key='-LINE-'),
        ],
        [   
            sg.Text('Name of Profile:', font=('Any', 36), justification='left')
        ],
        [
            sg.Text('Insert Data Here:', font=('Any', 36), justification='left')
        ],
        [
            sg.Button('ECG + Respiration Data', font=('Any', 36), size=(15, 2), key='-EMG-', pad=((0, 50), 0)),
            sg.Button('EMG Data', font=('Any', 36), size=(15, 2), key='-ECG-', pad=((0, 50), 0)),
        ],
        [
            sg.Button('Back', font=('Any', 36), size=(10, 2), key='-BACK-', button_color=('white', 'blue')),
        ],
    ]

    return sg.Window('create_create', layout, size=(1200, 800), resizable=True)
"""

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

    return sg.Window('Connect to Device', connect_to_device_layout, size=(1200, 800), resizable=True)

# Create the loading window
loading_window = create_loading_window()

# Simulate Loading for 5 seconds
start_time = time.time()
while time.time() - start_time < 3:
    event, values = loading_window.read(timeout=10)
    if event == sg.WIN_CLOSED:
        break
    simulate_loading(loading_window)

# close loading window
loading_window.close()

# Create the main window
main_window = create_main_window()

# Event loop for the main window
while True:
    main_event, main_values = main_window.read()

    if main_event == sg.WIN_CLOSED:
        break

    if main_event == '-SETTINGS-':
        main_window.hide()
        settings_window = create_settings_window()

        # Event loop for the settings window
        while True:
            settings_event, settings_values = settings_window.read()

            if settings_event == sg.WIN_CLOSED or settings_event == '-BACK-':
                settings_window.close()
                main_window.un_hide()
                break

            # Handle other events in the settings window if needed

    if main_event == '-PROFILE-MANAGER-':
        main_window.hide()
        profile_manager_window = create_profile_manager_window()

        # Event loop for the profile manager window
        while True:
            profile_manager_event, profile_manager_values = profile_manager_window.read()

            if profile_manager_event == sg.WIN_CLOSED or profile_manager_event == '-BACK-':
                profile_manager_window.close()
                main_window.un_hide()
                break
            # commented out below. this is for create profile. back button isnt working.
            #elif profile_manager_event == '-CREATE-NEW-':
                # open the create profile window
                #create_profile_window = create_create_profile_window()
                
                # event loop
                #while True:
                    #event_create, values_create = create_profile_window.read()

                    #if event_create == sg.WIN_CLOSED or event_create == '-BACK-':
                        #break
            # Handle other events in the profile manager window if needed

    if main_event == '-CONNECT-DEVICE-':
        main_window.hide()
        connect_to_device_window = create_connect_to_device_window()

        # Event loop for the connect to device window
        while True:
            connect_to_device_event, connect_to_device_values = connect_to_device_window.read()

            if connect_to_device_event == sg.WIN_CLOSED or connect_to_device_event == '-BACK-':
                connect_to_device_window.close()
                main_window.un_hide()
                break

            # Handle other events in the connect to device window if needed

# Close the main window
main_window.close()
