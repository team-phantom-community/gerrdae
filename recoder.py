import multiprocessing as mp
import serial
import time
import numpy as np
from datetime import datetime
from scipy.fft import fft, fftfreq
from scipy.signal import windows
import pandas as pd
import os
import keyboard

# Parameters
extract_length = 5000
error_threshold = 3
error_count = 3
fft_bound = 100
directory = './test'

def record_data(data_queue, stop_event):
    ser = serial.Serial("COM5", 115200)
    time.sleep(3)  # Wait for the serial connection to initialize

    avr = 1000  # Initialize the average value
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # filename = f"{timestamp}_log.csv"

    # if os.path.exists(filename):
    #     os.remove(filename)

    start = time.time()
    try:
        while not stop_event.is_set():
            try:
                # Read data from serial port
                data1 = float(ser.readline().rstrip().decode(encoding='utf-8'))

                # Calculate the threshold for ignoring data
                threshold = avr / 3

                # with open(filename, 'a', newline='') as f:
                    # writer = csv.writer(f)

                    # Check if data1 is within the acceptable range
                if abs(data1 - avr) <= threshold:
                        # Write data and average to CSV file
                        # writer.writerow([data1])
                    data_queue.put(data1)  # Send data to the queue
                else:
                    print(f"Data {data1} ignored: outside acceptable range")

                    # Update the average value
                avr = (avr * 9999 + data1) / 10000
                #print(data1)

            except ValueError:
                print("Conversion error: Skipping data")

            # time.sleep(0.01)  # Simulate some delay

    except KeyboardInterrupt:
        pass
    finally:
        ser.close()

def fft_processing(data_queue, stop_event):
    print("FFT processing started")
    data_list = []
    start_index = -1*extract_length
    while not stop_event.is_set() or not data_queue.empty():
        if not data_queue.empty():
            data1 = data_queue.get()
            data_list.append(data1)

            if len(data_list) >= 10:
                recent_data = data_list[-10:]
                avr = np.mean(recent_data)
                lower_bound = avr * (1 - error_threshold / 100)
                upper_bound = avr * (1 + error_threshold / 100)

                if start_index >= len(data_list) - extract_length:
                    # Ensure there is enough data for extraction
                    if len(data_list) >= start_index + extract_length:
                        segment = data_list[start_index:start_index + extract_length]
                        del data_list[start_index:start_index + extract_length]  # Remove processed data from the list
                        segment_mean = np.mean(segment)
                        adjusted_segment = segment - segment_mean

                        # Perform FFT
                        hanning_window = windows.hann(len(adjusted_segment))
                        fft_data = fft(adjusted_segment * hanning_window)
                        fft_data[0:3] = 0  # Remove DC component

                        fft_data_half = np.abs(fft_data[0:len(fft_data) // 2])
                        fft_output_file_path = f'{directory}/fft_data/fft_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                        pd.DataFrame(fft_data_half[0:fft_bound]).to_csv(fft_output_file_path, index=False, header=False)
                        print(f'FFT data saved -> {fft_output_file_path}')
                        # Clear the data_list to release memory
                        data_list.clear()
                        start_index = -1*extract_length
                
                elif np.sum((recent_data < lower_bound) | (recent_data > upper_bound)) >= error_count:
                    print(f"Data segment found: {recent_data}")
                    # start_index = 0
                    # Find the start index where the condition is first met
                    # start_index = next(i for i, x in enumerate(recent_data) if x < lower_bound or x > upper_bound)
                    start_index = len(data_list) - 10 + next(i for i, x in enumerate(recent_data) if x < lower_bound or x > upper_bound)
                # print(f"Start index: {start_index - len(data_list) + extract_length}")

if __name__ == "__main__":
    if not os.path.exists(f'{directory}/fft_data'):
        os.makedirs(f'{directory}/fft_data')

    data_queue = mp.Queue()
    stop_event = mp.Event()

    process1 = mp.Process(target=record_data, args=(data_queue, stop_event))
    process2 = mp.Process(target=fft_processing, args=(data_queue, stop_event))

    process1.start()
    time.sleep(10)
    process2.start()

    try:
        while True:
            # Check for 's' key to stop recording
            if keyboard.is_pressed('s'):
                stop_event.set()
                break
    except KeyboardInterrupt:
        stop_event.set()

    process1.join()
    process2.join()

    print