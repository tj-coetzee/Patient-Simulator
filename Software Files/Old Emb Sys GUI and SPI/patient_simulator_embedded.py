import spidev
import time
import RPi.GPIO as GPIO
import os
import threading 
from read_file import *

# Active low disables for differential converters
# High - not disabled
# Low  - disabled
DIS_A   = 37    # pin 37
DIS_B   = 35    # pin 35

# DAC SYNC pin to determine rising/falling edge
# High - data transferred on rising edge
# Low  - data transferred on falling edge
SYNC    = 15    # pin 15

# Load DAC - used to update DAC registers and analog outputs
# High - dac input register updated, output updates on falling edge of LDAC
# Low  - dac input register updated on rising edge of SYNC
LDAC    = 11    # pin 11

# SPI Connections (used in spidev)
# DO NOT CHANGE
SCLK    = 23    # pin 23 (SCLK)
MOSI    = 19    # pin 19 (MOSI)
MISO    = 21    # pin 21 (MISO)
CE0     = 24    # pin 24 (CE0)
CE1     = 26    # pin 26 (CE1)
CLR     = 13 

DEBUG = False


class RaspPi:

    def __init__(self, cs = 0, profile : str = "") -> None: 
        '''
        Instantiates SPI object and sets Raspberry Pi GPIO pins.

        Inputs:
            • speed - sampling rate (Hz)

            • CS - chip select (0 unless argument is added)

            • profile - profile to be simulated

        '''
        # Setup Raspberry GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)             # Edit out for warning messages
        GPIO.setup(DIS_A, GPIO.OUT)
        GPIO.setup(DIS_B, GPIO.OUT)
        GPIO.setup(SYNC, GPIO.OUT)
        GPIO.setup(LDAC, GPIO.OUT)
        GPIO.setup(CE1, GPIO.OUT)
        GPIO.setup(CLR, GPIO.OUT)

        # Set LDAC (active low) to high to allow for simultaneous output update
        GPIO.output(LDAC, GPIO.HIGH)
        # Set SYNC to low to allow for data transmission
        GPIO.output(SYNC, GPIO.HIGH)

        # Create spidev object
        self.spi = spidev.SpiDev()
        # Open connection to SPI bus and set parameters
        self.spi.open(0, cs) 
        self.spi.max_speed_hz = 5000 # 30 MHz max frequency
        # Set clock polarity and phase (0b00 - min, 0b11 - max)
        self.spi.mode = 0b01

        # Write to output range select register to set ±5 V for DAC A and B registers
        GPIO.output(SYNC, GPIO.LOW)
        self.spi.xfer2([0x0C, 0x00, 0x03])
        GPIO.output(SYNC, GPIO.HIGH)
        # Write to power control register to power up DAC A and B in normal operating mode
        GPIO.output(SYNC, GPIO.LOW)
        self.spi.xfer2([0x10, 0x00, 0x05])
        GPIO.output(SYNC, GPIO.HIGH)
        

        self.EMG_Ts : float = 0.0
        self.ECG_Ts : float = 0.0

        self.profile_name = profile

    def transfer(self, msg):
        GPIO.output(SYNC, GPIO.LOW)
        reply = self.spi.xfer2(msg)
        GPIO.output(SYNC, GPIO.HIGH)
        if DEBUG: print(reply)


    def emg_to_dac(self) -> None:
        '''
        Send EMG data to SPI bus.
        
        Inputs: None
        '''
        # Set sampling rate
        self.EMG_Ts = 1/self.get_emg_sampling_time()
        if self.EMG_Ts == 0.0:
            print(f'EMG scan rate cannot be {self.EMG_Ts}')
            return
        
        # Get binary data from EMG .dat file
        data = get_emg_data()
        # Set DIS_A to high
        GPIO.output(DIS_A, GPIO.HIGH)

        try:
            for value in data:
                # Assuming a 16-bit DAC, split the value into two bytes
                value = int(value)
                
                direction = 0x00            # DAC A
                msb = (value & 0xff) >> 8  # Most significant byte
                lsb = value & 0xff        # Least significant byte

                self.spi.xfer2([direction, msb, lsb])
                time.sleep(self.EMG_Ts)
        except KeyboardInterrupt:
            # Set DIS_A to low
            GPIO.output(DIS_A, GPIO.LOW)
            self.closeBus()

    def ecg_to_dac(self) -> None:
        '''
        Send ECG data to SPI bus.
        
        Inputs:
            speed - sampling rate (Hz)
        '''
        # Set sampling rate
        self.ECG_Ts = 1/self.get_ecg_sampling_time()
        if self.ECG_Ts == 0.0:
            print(f'EMG scan rate cannot be {self.ECG_Ts}')
            return
        
        # Get binary data from ECG .dat file
        data = get_ecg_data()
        # Set DIS_B to high
        GPIO.output(DIS_B, GPIO.HIGH)

        try:
            for value in data:
                # Assuming a 16-bit DAC, split the value into two bytes
                value = int(value)
                
                direction = 0x02            # DAC B
                msb = (value & 0xff) >> 8  # Most significant byte
                lsb = value & 0xff        # Least significant byte

                self.spi.xfer2([direction, msb, lsb])
        except KeyboardInterrupt:
            # Set DIS_B to low
            GPIO.output(DIS_B, GPIO.HIGH)
            self.closeBus()

    def create_threads(self):
        self.emg_thread = threading.Thread(target=self.emg_to_dac)
        self.ecg_thread = threading.Thread(target=self.ecg_to_dac)

    def start_threads(self):
        self.create_threads()
        self.emg_thread.start()
        self.ecg_thread.start()
    
    def join_threads(self):
        self.emg_thread.join()
        self.ecg_thread.join()

    def get_ecg_sampling_time(self) -> float:
        header_file_path = os.path.join(os.getcwd(), 'Profiles', f'PROF_{self.profile_name}', 'ECG', 'header.hdr')

        # Check if the header file exists
        if os.path.exists(header_file_path):
            # Read header file
            with open(header_file_path, 'r') as header_file:
                header_lines = header_file.readlines()

            # Extract relevant information from the header
            scan_rate = float(header_lines[2].split(':')[1].strip())
            return scan_rate
        else:
            return 0.0
    
    def get_emg_sampling_time(self):
        header_file_path = os.path.join(os.getcwd(), 'Profiles', f'PROF_{self.profile_name}', 'EMG', 'header.hdr')

        # Check if the header file exists
        if os.path.exists(header_file_path):
            # Read header file
            with open(header_file_path, 'r') as header_file:
                header_lines = header_file.readlines()

            # Extract relevant information from the header
            scan_rate = float(header_lines[2].split(':')[1].strip())
            return scan_rate
        else:
            return 0.0
        

    def closeBus(self) -> None:
        '''
        Close SPI interface.
        '''
        if DEBUG: print(f'\tClosing SPI interface...')
        # Turn off power to DAC A and B registers
        self.spi.xfer2([0x10, 0x00, 0x00])
        self.spi.close()
        #self.join_threads()
        
       

    def debug(self, act = False) -> None:
        if act: 
            global DEBUG
            DEBUG = True
            print(f'\tDebugging mode is active (DEGUG - {DEBUG})')


    
if __name__ == '__main__':
    test = RaspPi(1, "Capstone")
    test.debug(1)
    test.start_threads()
    test.closeBus()