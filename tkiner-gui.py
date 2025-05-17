import multiprocessing as mp
import serial
import time
import numpy as np
from datetime import datetime
from scipy.fft import fft
from scipy.signal import windows
import pandas as pd
import os
import tensorflow as tf
import tkinter as tk

# Parameters
extract_length = 5000
error_threshold = 1
error_count = 3
fft_bound = 200
directory = './test'

# Ensure the directory exists
if not os.path.exists(f'{directory}/fft_data'):
    os.makedirs(f'{directory}/fft_data')

# Recording data from the serial port
def record_data(data_queue, stop_event):
    ser = serial.Serial("COM5", 115200)
    time.sleep(3)  # Wait for the serial connection to initialize
    avr = 1000  # Initialize the average value
    try:
        while not stop_event.is_set():
            try:
                data1 = float(ser.readline().rstrip().decode(encoding='utf-8'))
                threshold = avr / 3
                if abs(data1 - avr) <= threshold:
                    data_queue.put(data1)
                avr = (avr * 9999 + data1) / 10000
            except ValueError:
                print("Conversion error: Skipping data")
    finally:
        ser.close()

def fft_processing(data_queue, fft_queue,stop_event):
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

                        # Send FFT data to the tensorflow processing queue
                        fft_queue.put(fft_data_half[0:fft_bound].tolist())
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

# TensorFlow processing function
def tensorflow_processing(fft_queue, stop_event, result_queue):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(fft_bound,)),
        tf.keras.layers.Dense(50, activation='sigmoid'),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Dense(50, activation='relu'),
        tf.keras.layers.Dense(100, activation='relu'),
        tf.keras.layers.Dense(100, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(10, activation='relu'),#ピラミッド（とてもでかい）
        tf.keras.layers.Dense(2, activation=tf.nn.softmax)
    ])
    model.load_weights('./savedweight_len200-331.weights.h5')
    model.summary()

    section = ["non-walk", "walk"]
    while not stop_event.is_set():
        if not fft_queue.empty():
            fft_data = fft_queue.get()
            if len(fft_data) > 0:
                fft_data = np.array([fft_data])
                data_normalized = fft_data / np.amax(fft_data)
                prediction = model.predict(data_normalized, verbose=0)
                result_a = section[round(prediction[0][1])]
                result_queue.put(result_a)
                fft_queue.put([])

# Main GUI function
def main_gui():
    def on_button_press():
        """Handles Start button press."""
        start_event.set()  # Signal that the button has been pressed
        start_button.config(state=tk.DISABLED)  # Disable Start button
        label.config(text="Processing started...")

    def update_label():
        """Updates the label with the latest TensorFlow results."""
        if not result_queue.empty():
            next_result = result_queue.get()  # Get the latest result from the queue
            if next_result != "":
                label.config(text=next_result)  # Update the label with the result
                # Clear the remaining items in the queue (if any)
                result_queue.put("")  # Put an empty string to clear the queue
        
            root.after(2000, lambda: label.config(text="Waiting for data..."))  # Update after 2 seconds
        if not stop_event.is_set():
            root.after(500, update_label)  # Schedule next label update


    # GUI initialization
    root = tk.Tk()
    root.title("Human Activity Recognition")
    root.geometry("800x500")

    # Create Label
    label = tk.Label(root, text="Initializing...", font=("Arial", 56))
    label.pack(pady=50)

    # Create Start Button
    start_button = tk.Button(root, text="Start", command=on_button_press, font=("Arial", 56))
    start_button.pack(pady=50)

    # Multiprocessing setup
    data_queue = mp.Queue()
    fft_queue = mp.Queue()
    result_queue = mp.Queue()
    stop_event = mp.Event()
    start_event = mp.Event()

    process1 = mp.Process(target=record_data, args=(data_queue, stop_event))
    process2 = mp.Process(target=fft_processing, args=(data_queue, fft_queue, stop_event))
    process3 = mp.Process(target=tensorflow_processing, args=(fft_queue, stop_event, result_queue))

    # Start the processes
    process1.start()
    process3.start()

    # Wait for initialization
    time.sleep(5)
    label.config(text="Press the Start button")
    start_button.config(state=tk.NORMAL)

    # Wait for Start button to be pressed
    while not start_event.is_set():
        root.update_idletasks()
        root.update()

    # Start FFT processing once the Start button is pressed
    process2.start()

    # Start updating the label
    update_label()

    # Graceful shutdown
    def on_close():
        """Handle closing the application."""
        stop_event.set()
        process1.terminate()
        process2.terminate()
        process3.terminate()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

    # Wait for all processes to terminate
    process1.join()
    process2.join()
    process3.join()
    print("All processes terminated.")

if __name__ == "__main__":
    main_gui()
