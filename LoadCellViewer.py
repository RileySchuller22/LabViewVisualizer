# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 16:20:37 2024

@author: Jason
"""

import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg

def read_last_n_lines(file_path, num_lines):
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        buffer = bytearray()
        lines = []
        while end > 0 and len(lines) < num_lines:
            size = min(70*1024, end)  # Increased buffer size
            f.seek(end - size)
            buffer = f.read(size) + buffer
            lines = buffer.decode().split('\n')  # Decode buffer to string
            end -= size
        return [line.strip() for line in lines[-num_lines:] if line.strip()]

def read_last_line(filename):
    with open(filename, 'rb') as f:
        f.seek(-2, 2)  # Move the cursor to the end of the file
        while f.read(1) != b'\n':
            f.seek(-2, 1)  # Move the cursor back one byte
        last_line = f.readline().decode()  # Read the last line
    return last_line.strip()

def update_time_bounds(last_n_minutes):
    global t_lower_bound, t_upper_bound
    latest_time = max(time_data[-1], first_time)  # Get the latest time
    t_upper_bound = (latest_time + (last_n_minutes/(2*60)))  # Add 25% buffer zone to the latest time
    t_lower_bound = (latest_time - last_n_minutes/60)  # Calculate lower bound based on upper bound and specified minutes
    
def update_time_bound_all():
    global t_lower_bound, t_upper_bound
    latest_time = max(time_data[-1], first_time)  # Get the latest time
    t_upper_bound = (latest_time + (latest_time*0.25))  # Add 25% buffer zone to the latest time
    t_lower_bound = 0

def create_input_window():
    layout = [
        [
            sg.Frame("Instrumentation Readings", layout=[
                [sg.Text("Thrust:"), sg.Text(""), sg.Text("", key="-TEMP_T1-", size=(7, 1)), sg.Text("g")],
                ]),
            sg.Frame("Plot Bound Update Buttons", layout=[
                [sg.Button("Time"), sg.Button("(Plot 1)")],
            ]),
            sg.Frame("", layout=[
                [sg.Button("EXIT")],
            ]),
        ],
        [
            sg.Frame("Time Bounds", layout=[
                [sg.Text("T Lower:"), sg.InputText(key="-T_LOWER-", size=(5, 1)), sg.Text("T Upper:"), sg.InputText(key="-T_UPPER-", size=(5, 1))],
                [sg.Button("Last 10m"), sg.Button("Last 60m"), sg.Button("Last 1d"), sg.Button("All")]            
            ]),
            sg.Frame("Plot 1 Y Bounds", layout=[
                [sg.Text("Y Lower:"), sg.InputText(key="-Y_LOWER1-", size=(5, 1)), sg.Text("Y Upper:"), sg.InputText(key="-Y_UPPER1-", size=(5, 1))],
            ]),
        ],
        [
            sg.Column([
                [sg.Canvas(key="-CANVAS1-")],
                [sg.Text("Plot 1")]
            ], size=(400, 300)),
        ],
    ]
    return sg.Window("Enter Input Values", layout)

# Initial bounds for x and y axes for all plots
t_lower_bound = 0
t_upper_bound = 1
y_lower_bound1 = -10
y_upper_bound1 = 100

## Pre-Start Variables
window = None
fig1, ax1 = plt.subplots()  # Plot 1
canvas1 = None
first_time = None  # Store the first time value

## Pre-Start Logic
while True:
    if window is None:
        window = create_input_window()
        
    # Clear the list of out of range values at the beginning of each iteration
    out_of_range_values = []

    event, values = window.read(timeout=50)
    
    if event == sg.WINDOW_CLOSED or event == "EXIT":
        break
    
    if event == "(Plot 1)":
        try:
            y_lower_bound1 = float(values["-Y_LOWER1-"])
            y_upper_bound1 = float(values["-Y_UPPER1-"])
        except ValueError:
            sg.popup("Invalid input. Please enter numerical values for bounds.")
            continue
        
    if event == "Time":
        try:
            t_lower_bound = float(values["-T_LOWER-"])
            t_upper_bound = float(values["-T_UPPER-"])
        except ValueError:
            sg.popup("Invalid input. Please enter numerical values for bounds.")
            continue
        
    if event == "Last 10m":
        update_time_bounds(10)
        continue
    
    if event == "Last 60m":
        update_time_bounds(60)
        continue
    
    if event == "Last 1d":
        update_time_bounds(1440)
        continue
    
    if event == "All":
        update_time_bound_all()
        continue
    
    # Read data from the raw_pressure_data.txt file
    last_line = read_last_line('data.txt')
    parts = last_line.split(',')  # Split the line into parts
    InsideTemperature = round(float(parts[1]), 5)
    
    # Update current values displayed in the interface
    window["-TEMP_T1-"].update(InsideTemperature)
                        
    window.finalize()
          
    # Plotting the pressure data
    ax1.clear()  # Clear previous plot 1
    # Read data from text file and plot it
    with open ('data.txt', 'r') as file1:
        time_data = []
        temperature_data1 = []
        for line1 in file1:
            parts1 = line1.strip().split(',')
            if first_time is None:
                first_time = float(parts1[0])  # Store the first time value
            time_data.append(float(parts1[0]) - first_time)  # Subtract the first time value
            temperature_data1.append(float(parts1[1]))  # Second column data from raw_temp_data.txt
    
        ax1.plot(time_data, temperature_data1, 'bo', markersize=3, label='Inside Temperature')

    ax1.set_xlabel('Time (Minutes)')
    ax1.set_ylabel('Thrust (Grams)')
    ax1.set_xlim(t_lower_bound, t_upper_bound)  # Set x-axis limits for plot 1
    ax1.set_ylim(y_lower_bound1, y_upper_bound1)  # Set y-axis limits for plot 1
    ax1.legend()
    
    if canvas1 is None:
        canvas1 = FigureCanvasTkAgg(fig1, master=window["-CANVAS1-"].TKCanvas)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side='top', fill='both', expand=1)
    else:
        canvas1.draw()
        
    update_time_bound_all()

if window is not None:
    window.close()
## End of Pre-Start Logic