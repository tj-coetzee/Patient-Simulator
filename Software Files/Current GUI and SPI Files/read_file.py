import os
import numpy as np


def get_emg_data(profile_name = "Capstone"):
    data_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'EMG', '*.dat')
    if os.path.exists(data_file_path):
        # Read data from channel one
        with open(data_file_path, 'rb') as data_file:
            # Skip to the start of channel one data
            data_file.seek(0)  # Assuming data format starts at the beginning of the file
            # Read the data from channel one
            emg_data = np.fromfile(data_file, dtype=np.int16)  # Assuming data type is float64

        return emg_data
    
def get_ecg_data(profile_name = "Capstone"):
    data_file_path = os.path.join(os.getcwd(), f'PROF_{profile_name}', 'ECG', 'data.dat')
    if os.path.exists(data_file_path):
        # Read data from channel one
        with open(data_file_path, 'rb') as data_file:
            # Skip to the start of channel one data
            data_file.seek(0)  # Assuming data format starts at the beginning of the file
            # Read the data from channel one
            ecg_data = np.fromfile(data_file, dtype=np.int16)  # Assuming data type is float64

        return ecg_data


if __name__ == '__main__':
    get_emg_data()
    get_ecg_data()