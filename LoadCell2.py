# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 18:45:53 2024

@author: Jason
"""
import time
import nidaqmx
from nidaqmx.errors import DaqError, DaqReadError

def read_data_and_save(device, channel, output_file):
    start_time = time.time()
    thrust_values = []  # Store thrust values for 15-second averaging
    time_intervals = []  # Store corresponding elapsed time values
    
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(f"{device}/{channel}")
        with open(output_file, 'w') as file:
            try:
                while True:
                    
                    AvgThrust = []
                    
                    for _ in range(100):
                        voltage = task.read()
                        Thrust = -(((117.92)*(voltage)) - (556))
    
                        AvgThrust.append(Thrust)
                        time.sleep(0.0025)
                    
                    AvgThrust = sum(AvgThrust) / len(AvgThrust)
                    
                    elapsed_time = (time.time() - start_time) / 60 # Time in minutes
                    
                    thrust_values.append(AvgThrust)
                    time_intervals.append(elapsed_time)
                    
                    # Compute 15-second average if enough data points exist
                    if time_intervals[-1] - time_intervals[0] >= 0.25:
                        avg_15s_thrust = sum(thrust_values) / len(thrust_values)
                        thrust_values.clear()
                        time_intervals.clear()
                    else:
                        avg_15s_thrust = "NA"  # Not enough data yet
                    
                    data_point = f"{elapsed_time}, {AvgThrust}, {avg_15s_thrust}\n"
                    file.write(data_point)
                    file.flush()
                    
            except (DaqError, DaqReadError) as e:
                print(f"DAQ Error: {e}")

if __name__ == "__main__":
    device = "Dev11"  # Change as needed
    channel = "ai1"
    output_file = "data.txt"
    read_data_and_save(device, channel, output_file)
