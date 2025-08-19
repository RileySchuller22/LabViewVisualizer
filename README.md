# LabViewVisualizer

This repository contains Python scripts for working with a load cell and visualizing its output.  
It was originally developed as part of my work at UCI in undergraduate research. LoadCell2.py and LoadCellViewer.py was given to me and my contribution was LoadCellThreaded.py. 

## 📂 Repository Contents
- **LoadCell2.py**  
  Provided code that communicates with a load cell through a National Instruments DAQ.  
  It records:
  - Force in grams  
  - Time (s)  
  - 15-second averaged force (g)  
  The results are written to `data.txt`.  
  > This script is optional — it is mainly kept as reference and for generating `data.txt` directly.

- **LoadCellViewer.py**  
  Provided visualization script that originally used the PySimpleGUI library to plot data from `data.txt`.  
  Superseded by the threaded version.

- **LoadCellThreaded.py**  
  A custom tool developed to **replace the PySimpleGUI viewer**.  
  - Uses **Tkinter** and **Matplotlib** for the GUI.  
  - Uses **threading** so that data collection from the DAQ and visualization run concurrently in a single program.  
  - Still writes to `data.txt`, so the recorded data can be analyzed later or used by other scripts.  

- **data.txt**  
  Example output file containing time-series load cell data (force in grams, time, moving average).
