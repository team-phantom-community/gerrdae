import multiprocessing as mp
import serial
import time
import numpy as np
from datetime import datetime
from scipy.fft import fft, fftfreq
from scipy.signal import windows
import pandas as pd
import os

# Parameters
extract_length = 5000
error_threshold = 1
error_count = 3
fft_bound = 100
directory = './0314/walk'

def record_data(data_queue, stop_event):
    ser = serial.Serial("COM5", 115200)
    time.sleep(3)  # Wait for the serial connection to initialize
    avr = 1000  # Initialize the average value

    try:
        while not stop_event.is_set():
            data1 = float(ser.readline().rstrip().decode(encoding='utf-8'))
            data_queue.put(data1)
            # time.sleep(0.01)  # Simulate some delay
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()

def fft_processing(data_queue, stop_event):
    data_array = [0] * 10  # Initialize with 10 elements
    while not stop_event.is_set() or not data_queue.empty():
        if not data_queue.empty():
            data1 = data_queue.get()
            data_array.pop()  # Remove the oldest data (last element)
            data_array.insert(0, data1)  # Insert the newest data at the beginning

            if len(data_array) == 10:
                avr = np.mean(data_array)
                lower_bound = avr * (1 - error_threshold / 100)
                upper_bound = avr * (1 + error_threshold / 100)

                if np.sum((data_array < lower_bound) | (data_array > upper_bound)) >= error_count:
                    if len(data_array) >= extract_length:
                        segment = data_array[:extract_length]
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

if __name__ == "__main__":
    if not os.path.exists(f'{directory}/fft_data'):
        os.makedirs(f'{directory}/fft_data')

    data_queue = mp.Queue()
    stop_event = mp.Event()

    process1 = mp.Process(target=record_data, args=(data_queue, stop_event))
    process2 = mp.Process(target=fft_processing, args=(data_queue, stop_event))

    process1.start()
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

    print("All processes finished.")
