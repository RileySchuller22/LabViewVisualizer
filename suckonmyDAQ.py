# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 22:58:18 2025

@author: riley and gipetee
new code to plot lab data
"""


import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



# Global variables to store the last valid average thrust and time
last_valid_avg_thrust = "0.00"
last_valid_avg_time = 0
t_lower_bound = 0
t_upper_bound = .5
y_lower_bound = 0
y_upper_bound = 100


# Set the time bounds from the entry boxes
def set_time_bounds():
    global t_lower_bound, t_upper_bound
    try:
        t_lower_bound = float(t_lower_entry.get())
        t_upper_bound = float(t_upper_entry.get())
    except ValueError:
        t_lower_bound = 0
        t_upper_bound = 30

# Set the Y-axis bounds from the entry boxes
def set_y_bounds():
    global y_lower_bound, y_upper_bound
    try:
        y_lower_bound = float(y_lower_entry.get())
        y_upper_bound = float(y_upper_entry.get())
    except ValueError:
        y_lower_bound = 0
        y_upper_bound = 50

# Download the plot as a PNG file
def download_plot():
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        fig.savefig(file_path)

# Update the plot with the latest data from the file
def update_plot():
    global last_valid_avg_thrust, last_valid_avg_time
    with open('data.txt', 'r') as file:
        time_data, thrust_data, avg_thrust_data = [], [], []
        
        for line in file:
            if not line.strip():
                continue #skip completely empty lines
            
            parts = line.strip().split(',')
            if len(parts) < 3:
                print(f"Skipping invalid line: {line.strip()}")
                continue #skip lines that dont hace at least 3 values
            
            try:
                time = float(parts[0].strip())
                thrust = float(parts[1].strip())
                avg_thrust = parts[2].strip()
            except ValueError:
                print(f"Skipping line with invalid number: {line.strip()}")
                continue #skip lines with invalid number formats
                
            
            # Handle 'NA' or invalid average thrust entries
            if avg_thrust != 'NA':
                try:
                    avg_thrust = f"{float(avg_thrust):.2f}"
                    last_valid_avg_thrust = avg_thrust
                    last_valid_avg_time = time
                except ValueError:
                    avg_thrust = last_valid_avg_thrust
            else:
                avg_thrust = last_valid_avg_thrust
            
            # Collect time, thrust, and avg_thrust values
            time_data.append(time)
            thrust_data.append(thrust)
            avg_thrust_data.append(avg_thrust)
        
        # Clear the previous plot and update with new data
        ax.clear()
        ax.plot(time_data, thrust_data, 'bo', markersize=3, label="Thrust (g)")
        ax.set_xlabel("Time (Minutes)")
        ax.set_ylabel("Thrust (g)")
        ax.set_xlim(t_lower_bound, t_upper_bound)
        ax.set_ylim(y_lower_bound, y_upper_bound)
        ax.legend()
        ax.grid(True)
        canvas.draw()

    # Update the label with the last valid average thrust and time
    avg_thrust_label.config(text=f"Average Thrust: {last_valid_avg_thrust} g at {last_valid_avg_time} minutes")

# Auto-set the maximum time (T Max) based on the latest time in the data
def auto_set_t_max():
    global t_upper_bound
    times = []
    
    with open('data.txt', 'r') as file:
        for line in file:
            if not line.strip():
                continue  # Skip empty lines

            parts = line.strip().split(',')
            if len(parts) < 1:
                continue  # Skip invalid lines with no time value
            
            try:
                time = float(parts[0].strip())
                times.append(time)
            except ValueError:
                print(f"Skipping line with invalid time: {line.strip()}")
                continue  # Skip if time value isn't a valid float
    
    if times:
        t_upper_bound = max(times)
        t_upper_entry.delete(0, tk.END)
        t_upper_entry.insert(0, str(t_upper_bound))
        update_plot()
    else:
        print("No valid times found in data.")
        
# Auto-refresh the Plot as Data.txt is updated
def auto_refresh():
    
    refreshRate = 500 # refresh set to half a second
    
    set_time_bounds()
    set_y_bounds()
    update_plot()
    window.after(refreshRate, auto_refresh) 

    
    

# Create the main Tkinter window
window = tk.Tk()
window.title("Thrust Data Viewer")

# Create the control panel frame
control_frame = tk.Frame(window)
control_frame.pack(padx=10, pady=10)

# Time control section (for setting T Min and T Max)
time_frame = tk.Frame(control_frame)
time_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

tk.Label(time_frame, text="T Min (Minutes):").pack(side=tk.LEFT, padx=5)
t_lower_entry = tk.Entry(time_frame)
t_lower_entry.pack(side=tk.LEFT, padx=5)
t_lower_entry.insert(0, str(t_lower_bound))

tk.Label(time_frame, text="T Max (Minutes):").pack(side=tk.LEFT, padx=5)
t_upper_entry = tk.Entry(time_frame)
t_upper_entry.pack(side=tk.LEFT, padx=5)
t_upper_entry.insert(0, str(t_upper_bound))

# Y-axis control section (for setting Y Min and Y Max)
y_frame = tk.Frame(control_frame)
y_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

tk.Label(y_frame, text="Y Min (Thrust):").pack(side=tk.LEFT, padx=5)
y_lower_entry = tk.Entry(y_frame)
y_lower_entry.pack(side=tk.LEFT, padx=5)
y_lower_entry.insert(0, str(y_lower_bound))

tk.Label(y_frame, text="Y Max (Thrust):").pack(side=tk.LEFT, padx=5)
y_upper_entry = tk.Entry(y_frame)
y_upper_entry.pack(side=tk.LEFT, padx=5)
y_upper_entry.insert(0, str(y_upper_bound))

# Button controls to auto-set T Max, update the plot, and download the plot
button_frame = tk.Frame(control_frame)
button_frame.pack(side=tk.TOP, pady=5)

tk.Button(button_frame, text="Auto-Set T Max", command=auto_set_t_max).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Update Plot", command=lambda: [set_time_bounds(), set_y_bounds(), update_plot()]).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Download Plot", command=download_plot).pack(side=tk.LEFT, padx=5)

# Label for displaying the latest average thrust and time
avg_thrust_label = tk.Label(control_frame, text=f"Average Thrust: {last_valid_avg_thrust} g at {last_valid_avg_time} minutes")
avg_thrust_label.pack(side=tk.TOP, pady=5)

# Create the plot figure
fig, ax = plt.subplots(figsize=(8, 6))

# Canvas to display the plot in Tkinter
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().pack(padx=10, pady=10)

# Initial plot update
update_plot()

# Refresh the plot every second as data is added
auto_refresh()

# Start the Tkinter main loop
window.mainloop()
