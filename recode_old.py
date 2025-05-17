# -*- coding: utf-8 -*-
import csv
import serial
import os
import time
from datetime import datetime
import keyboard

# Set up the serial connection (Adjust COM port and baud rate as needed)
ser = serial.Serial("COM5", 115200)

# Wait for the serial connection to initialize
time.sleep(3)

# Create a filename with the current timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{timestamp}_log.csv"

# Function to remove the log file if it exists
if os.path.exists(filename):
    os.remove(filename)

# Initialize the average value
avr = 1000

# Function to record data
def record_data():
    global avr  # Access the global avr variable
    start = time.time()
    
    try:
        while True:
            # Check for 's' key to stop recording
            if keyboard.is_pressed('s'):
                break
            with open(filename, 'a', newline='') as f:
                writer = csv.writer(f)  # Create and open CSV file
                try:
                    # Read data from serial port
                    data1 = float(ser.readline().rstrip().decode(encoding='utf-8'))
                    # Calculate the threshold for ignoring data
                    threshold = avr / 3
                    # Check if data1 is within the acceptable range
                    if abs(data1 - avr) <= threshold:
                        # Write data and average to CSV file
                        writer.writerow([data1])
                    else:
                        print(f"Data {data1} ignored: outside acceptable range")
                    # Update the average value
                    avr = (avr * 9999 + data1) / 10000
                    # print(data1)
                except ValueError:
                    # Skip the data if conversion fails
                    print("Conversion error: Skipping data")
            # Check for 's' key to stop recording within the loop
            if keyboard.is_pressed('s'):
                break
    except KeyboardInterrupt:
        pass

# Main loop to start and stop recording with key presses
try:
    while True:
        # Wait for 'r' key to start recording
        if keyboard.is_pressed('r'):
            print("Recording started...")
            record_data()
            print("Recording stopped.")
            break  # Exit the loop after stopping the recording
except KeyboardInterrupt:
    pass

# Close the serial port
ser.close()
print("End")
