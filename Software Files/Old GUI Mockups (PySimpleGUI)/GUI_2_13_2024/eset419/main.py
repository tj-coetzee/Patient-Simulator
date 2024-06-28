import PySimpleGUI as sg
import time
import os
import shutil
from functions import *
import numpy as np
import matplotlib.pyplot as plt

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
# once loading window has finished, main window will open up.
main_window = create_main_window()

# Event loop for the main window
while True:
    main_event, main_values = main_window.read()
    # main_window.read() = function that waits for event ot occur in main_window. (button click, etc.)
    # main_event holds the type of event that occured (button click, window close)
    # main_values holds any values associated with the event.
    

    if main_event == sg.WIN_CLOSED:
        break
    
    # Ensure only directories starting with 'PROF_' are considered as profile directories
    for prof_name in os.listdir(os.getcwd()):
        if prof_name.startswith('PROF_') and os.path.isdir(prof_name):
            # Extract the profile name from the directory name
            profile_name = prof_name[5:]  # Remove 'PROF_' prefix
            print("prof name: " + profile_name + ". main_event = " + main_event)
            if main_event == f'-PLOT-{profile_name}-':
                # Call wave_plot function with the corresponding profile name
                wave_plot(profile_name)
                break

    if main_event == '-SETTINGS-':  # does main_event var hold event correspondding to settings button
        main_window.hide()  
        # if so, hide main screen. this is common to creating multi-window interface.. allows for other windows to be displayed and keeps main window accessible.
        settings_window = create_settings_window()
        #

        # Event loop for the settings window
        while True:
            settings_event, settings_values = settings_window.read()
            # settings_window.read() = function that waits for event ot occur in settings_window. (button click, etc.)
            # settings_event holds the type of event that occured (button click, window close)
            # settings_values holds any values associated with the event.

            if settings_event == sg.WIN_CLOSED or settings_event == '-BACK-':
                # if window is closed or back button pressed.
                settings_window.close()
                main_window.un_hide()
                break

            # Handle other events in the settings window if needed

    if main_event == '-PROFILE-MANAGER-':
        main_window.hide()
        # hides main window. common practice, still accessible later.
        profile_manager_window = create_profile_manager_window()
        # opens create_profile_manager window

        # Event loop for the profile manager window
        while True:
            profile_manager_event, profile_manager_values = profile_manager_window.read()
            # profile_manager_event.read() = function that waits for event ot occur in settings_window. (button click, etc.)
            # profile_manager_event holds the type of event that occured (button click, window close)
            # profile_manager_values holds any values associated with the event.
            
            if profile_manager_event == sg.WIN_CLOSED or profile_manager_event == '-BACK-':
                profile_manager_window.close()
                main_window.un_hide()
                break
            
            elif profile_manager_event == '-CREATE-NEW-':
                profile_manager_window.hide()
                # open the create profile window
                create_profile_window = create_new_profile_window()
                
                # event loop
                while True:
                    create_event, create_values = create_profile_window.read()
                    # create_event.read() = function that waits for event ot occur in settings_window. (button click, etc.)
                    # create_event holds the type of event that occured (button click, window close)
                    # create_values holds any values associated with the event.

                    if create_event == sg.WIN_CLOSED or create_event == '-BACK-':
                        create_profile_window.close()
                        profile_manager_window.un_hide()
                        break
                    
                    elif create_event == '-SAVE-':
                        # this needs to save the files into a folder.
                        # Retrieve the input values
                        
                        prof_name = create_values['-PROFILE-NAME-']
                        # -PROFILE-NAME- is key from create_values that holds profile name information.
                        
                        HDR_file = create_values['-HDR-FILE-']
                        # -EMG-FILE-PATH- is key from create_values that holds EMG file information.
                        
                        DAT_file = create_values['-DAT-FILE-']
                        # -ECG-FILE-PATH- is key from create_values that holds ECG file information.
                    
                        # Create the folder name
                        folder_name = f'PROF_{prof_name}'
                        # f string. 'PROF_' is fixed part of string. whatever is inside {} is added to name.

                        # Create the folder in the same directory as the script
                        folder_path = os.path.join(os.path.dirname(__file__), folder_name)
                        # stores path in folder_path.
                        # os.path.join = function that joins together parts of path.
                        # in this case, it is joining the path that the script is located with folder name
                        
                        os.makedirs(folder_path, exist_ok=True)
                        # this creates the folder. exist_ok=True makes it not raise error if folder already exists.

                        # Copy the CSV files to the folder using shell utility, file operations module.
                        if HDR_file:
                            shutil.copy(HDR_file, os.path.join(folder_path, 'header.hdr'))
                        if DAT_file:
                            shutil.copy(DAT_file, os.path.join(folder_path, 'data.dat'))
                        # copying file specified in file path to folder with a new name
                        
                        # Inform the user that the profile has been saved
                        sg.popup(f'Profile "{prof_name}" saved in folder "{folder_path}"', title='Profile Saved')

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

    if main_event == '-TOUR-':
        break

# Close the main window
main_window.close()
