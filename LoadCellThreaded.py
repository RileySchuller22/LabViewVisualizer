import time
import threading
import nidaqmx
from nidaqmx.errors import DaqError, DaqReadError
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global config
DEVICE = "Dev11"
CHANNEL = "ai1"
OUTPUT_FILE = "data.txt"
REFRESH_RATE_MS = 500

# Globals for DAQ threading
daq_running = True

# GUI state
last_valid_avg_thrust = "0.00"
last_valid_avg_time = 0
t_lower_bound = 0
t_upper_bound = 0.5
y_lower_bound = 0
y_upper_bound = 100

# =========================
# DAQ Reader Thread
# =========================
def read_data_and_save():
    global daq_running
    start_time = time.time()
    thrust_values = []
    time_intervals = []

    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(f"{DEVICE}/{CHANNEL}")
        with open(OUTPUT_FILE, 'w') as file:
            try:
                while daq_running:
                    avg_thrust_list = []
                    for _ in range(100):
                        voltage = task.read()
                        thrust = -((117.92 * voltage) - 556)
                        avg_thrust_list.append(thrust)
                        time.sleep(0.0025)
                    avg_thrust = sum(avg_thrust_list) / len(avg_thrust_list)
                    elapsed_time = (time.time() - start_time) / 60  # in minutes
                    thrust_values.append(avg_thrust)
                    time_intervals.append(elapsed_time)

                    if time_intervals[-1] - time_intervals[0] >= 0.25:
                        avg_15s_thrust = sum(thrust_values) / len(thrust_values)
                        thrust_values.clear()
                        time_intervals.clear()
                    else:
                        avg_15s_thrust = "NA"

                    line = f"{elapsed_time}, {avg_thrust}, {avg_15s_thrust}\n"
                    file.write(line)
                    file.flush()

            except (DaqError, DaqReadError) as e:
                print(f"DAQ Error: {e}")
                daq_running = False

# =========================
# GUI Plotting Functions
# =========================
def set_time_bounds():
    global t_lower_bound, t_upper_bound
    try:
        t_lower_bound = float(t_lower_entry.get())
        t_upper_bound = float(t_upper_entry.get())
    except ValueError:
        t_lower_bound, t_upper_bound = 0, 30

def set_y_bounds():
    global y_lower_bound, y_upper_bound
    try:
        y_lower_bound = float(y_lower_entry.get())
        y_upper_bound = float(y_upper_entry.get())
    except ValueError:
        y_lower_bound, y_upper_bound = 0, 50

def update_plot():
    global last_valid_avg_thrust, last_valid_avg_time
    try:
        with open(OUTPUT_FILE, 'r') as file:
            time_data, thrust_data, avg_thrust_data = [], [], []
            for line in file:
                if not line.strip():
                    continue
                parts = line.strip().split(',')
                if len(parts) < 3:
                    continue
                try:
                    time_val = float(parts[0].strip())
                    thrust_val = float(parts[1].strip())
                    avg_thrust_val = parts[2].strip()
                except ValueError:
                    continue

                if avg_thrust_val != 'NA':
                    try:
                        avg_thrust_val = f"{float(avg_thrust_val):.2f}"
                        last_valid_avg_thrust = avg_thrust_val
                        last_valid_avg_time = time_val
                    except ValueError:
                        avg_thrust_val = last_valid_avg_thrust
                else:
                    avg_thrust_val = last_valid_avg_thrust

                time_data.append(time_val)
                thrust_data.append(thrust_val)
                avg_thrust_data.append(avg_thrust_val)

            ax.clear()
            ax.plot(time_data, thrust_data, 'bo', markersize=3, label="Thrust (g)")
            ax.set_xlabel("Time (Minutes)")
            ax.set_ylabel("Thrust (g)")
            ax.set_xlim(t_lower_bound, t_upper_bound)
            ax.set_ylim(y_lower_bound, y_upper_bound)
            ax.legend()
            ax.grid(True)
            canvas.draw()

            avg_thrust_label.config(
                text=f"Average Thrust: {last_valid_avg_thrust} g at {last_valid_avg_time:.2f} minutes"
            )
    except FileNotFoundError:
        pass

def auto_set_t_max():
    global t_upper_bound
    try:
        with open(OUTPUT_FILE, 'r') as file:
            times = []
            for line in file:
                if not line.strip():
                    continue
                parts = line.strip().split(',')
                if len(parts) < 1:
                    continue
                try:
                    time_val = float(parts[0].strip())
                    times.append(time_val)
                except ValueError:
                    continue
        if times:
            t_upper_bound = max(times)
            t_upper_entry.delete(0, tk.END)
            t_upper_entry.insert(0, str(t_upper_bound))
            update_plot()
    except FileNotFoundError:
        pass

def auto_refresh():
    set_time_bounds()
    set_y_bounds()
    update_plot()
    window.after(REFRESH_RATE_MS, auto_refresh)

def download_plot():
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        fig.savefig(file_path)

# =========================
# Start GUI
# =========================
window = tk.Tk()
window.title("DAQ Thrust Viewer")

# --- Control Panel ---
control_frame = tk.Frame(window)
control_frame.pack(padx=10, pady=10)

# Time Range
time_frame = tk.Frame(control_frame)
time_frame.pack()
tk.Label(time_frame, text="T Min (Min):").pack(side=tk.LEFT)
t_lower_entry = tk.Entry(time_frame, width=5)
t_lower_entry.pack(side=tk.LEFT)
t_lower_entry.insert(0, str(t_lower_bound))
tk.Label(time_frame, text="T Max (Min):").pack(side=tk.LEFT)
t_upper_entry = tk.Entry(time_frame, width=5)
t_upper_entry.pack(side=tk.LEFT)
t_upper_entry.insert(0, str(t_upper_bound))

# Y Range
y_frame = tk.Frame(control_frame)
y_frame.pack()
tk.Label(y_frame, text="Y Min (g):").pack(side=tk.LEFT)
y_lower_entry = tk.Entry(y_frame, width=5)
y_lower_entry.pack(side=tk.LEFT)
y_lower_entry.insert(0, str(y_lower_bound))
tk.Label(y_frame, text="Y Max (g):").pack(side=tk.LEFT)
y_upper_entry = tk.Entry(y_frame, width=5)
y_upper_entry.pack(side=tk.LEFT)
y_upper_entry.insert(0, str(y_upper_bound))

# Buttons
button_frame = tk.Frame(control_frame)
button_frame.pack()
tk.Button(button_frame, text="Auto-Set T Max", command=auto_set_t_max).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Download Plot", command=download_plot).pack(side=tk.LEFT, padx=5)

# Avg Thrust Display
avg_thrust_label = tk.Label(control_frame, text="Average Thrust: -- g at -- minutes")
avg_thrust_label.pack()

# --- Plot Area ---
fig, ax = plt.subplots(figsize=(8, 6))
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().pack(padx=10, pady=10)

# Start DAQ in background
daq_thread = threading.Thread(target=read_data_and_save, daemon=True)
daq_thread.start()

# Start auto-refresh of plot
auto_refresh()

# Close cleanly
def on_closing():
    global daq_running
    daq_running = False
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
