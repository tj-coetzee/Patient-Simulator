import numpy as np
import matplotlib.pyplot as plt

# Read header file
with open('tam_022503_racap.hdr', 'r') as header_file:
    header_lines = header_file.readlines()

# Extract relevant information from the header
frontend_gain = float(header_lines[1].split(':')[1].strip())
scan_rate = float(header_lines[2].split(':')[1].strip())
channels_used = [line.split(':')[0].strip() for line in header_lines[4:]]

# Read binary data file
data = np.fromfile('tam_022503_racap.dat', dtype=np.float64)  # Assuming data type is int16

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
