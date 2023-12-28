import serial
import numpy as np
import time
import tkinter as tk
import requests
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.ttk as ttk

NODEMCU_IP = "192.168.1.1"  # IP address of the NodeMCU in the local network
def turn_relay_on():
    url = f"http://{NODEMCU_IP}/relay"
    response = requests.post(url, data="TurnOnRelay")
    if response.status_code == 200:
        print("Relay turned on")
    else:
        print("Failed to turn on relay")
def turn_relay_off():
    url = f"http://{NODEMCU_IP}/relay"
    response = requests.post(url, data="TurnOffRelay")
    if response.status_code == 200:
        print("Relay turned off")
    else:
        print("Failed to turn on relay")

def get_temperature_readings():
    global time_to_reach_max
    url = f"http://{NODEMCU_IP}"
    response = requests.get(url)
    if response.status_code == 200:
        readings = response.text.split(',')
        temperatures = [float(reading) for reading in readings[1:100]]
        print(readings)
        print("Temperature Readings:")
        max_temperature = float('-inf')  # Initialize with lowest possible value
        time_array = []  # Initialize empty time array
        for i, reading in enumerate(readings[1:100]):
            temperature = float(reading)
            print(f"Reading {i+1}: {reading}")
            if temperature > max_temperature:
                max_temperature = temperature
                max_temperature_index = i + 1
            time_array.append((i + 1) / 10)  # Append index/1000 to time array
        print("Maximum Temperature:", max_temperature)
        time_to_reach_max = max_temperature_index / 10  # Calculate time to reach maximum temperature
        print("Time to reach maximum temperature:", time_to_reach_max, "seconds")   
        fig, ax = plt.subplots()
        ax.plot(time_array,temperatures)
        ax.set_xlabel('Time')
        ax.set_ylabel('Temperature (C)')

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=2, columnspan=2, padx=10, pady=10)

    else:
        print(response.status_code)
        print("Failed to retrieve temperature readings")
def clear():
    url = f"http://{NODEMCU_IP}"
    response = requests.post(url, data="")
    if response.status_code == 200:
        print("Cleared")
    else:
        print("Failed to clear")
def update_progress(progress, start_time, top):
    current_time = time.time()
    elapsed_time = current_time - start_time
    progress_value = elapsed_time / 15 * 100  # Calculate progress percentage
    progress["value"] = progress_value
    if elapsed_time < 15:
        root.after(100, update_progress, progress, start_time, top)
    else:
        progress.stop()
        progress.destroy()  # Destroy the progress bar widget
        get_temperature_readings()
        clear()
        top.destroy()

def button_click():
    turn_relay_on()
    #time.sleep(2)
    #turn_relay_off()
    top = tk.Toplevel(root)
    #top.title("Loading...")
    #top.geometry("200x80")

    progress = ttk.Progressbar(top, length=180, mode="determinate")
    progress.pack()

    start_time = time.time()
    root.after(100, update_progress, progress, start_time, top)
    
def calculate_diffusivity():
    global time_to_reach_max  # Reference the global variable
    global alpha

    # Get input values
    L = float(entry_thickness.get())

    # Calculate T_inf as half of the time to reach maximum temperature
    T_inf = float(time_to_reach_max / 2)

    alpha = 0.14325 * pow(L, 2) / T_inf
    print(alpha)
    label_diffusivity = tk.Label(root, text="The thermal diffusivity of rubber is: {:.7e} m^2/s".format(alpha), font=("Arial", 12))
    label_diffusivity.grid(row=3, column=2, padx=10, pady=5, sticky= "nsew")

def calculate_conductivity():
    global alpha
    rho = float(entry_density.get())
    c = float(entry_Cp.get())
    # Calculate thermal conductivity using formula k = alpha * rho * c
    k = alpha * rho * c
    conductivity_label = tk.Label(root, text="The thermal conductivity of the material is: {:.4f} W/mK".format(k), font=("Arial", 12))
    conductivity_label.grid(row =7, column =2, padx=10, pady=5, sticky= "nsew")

global root
root = tk.Tk()
root.title("Laser Flash Machine")
def on_closing():
    root.destroy()  # Close the Tkinter window and stop the code execution

# Load the image
image_path = "images/WhatsApp Image 2023-03-12 at 14.02.44.png"
image = Image.open(image_path)
image.thumbnail((300, 300))  # Resize the image to fit the window
image_tk = ImageTk.PhotoImage(image)

# Create a canvas
canvas = tk.Canvas(root, width=image.width, height=image.height)
canvas.grid(row=0, column=0, columnspan=2)

# Display the image on the canvas
canvas.create_image(0, 0, anchor="nw", image=image_tk)
# Create a button 
button = tk.Button(root, text="Start", command=button_click, font=("Arial", 16))
button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

# Create labels and text entry for sample thickness
label_thickness = tk.Label(root, text="Sample Thickness:", font=("Arial", 12))
label_thickness.grid(row=2, column=0, padx=10, pady=5, sticky="e")

entry_thickness = tk.Entry(root, font=("Arial", 12))
entry_thickness.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Create a button to calculate thermal diffusivity
button_diffusivity = tk.Button(root, text="Calculate Diffusivity", command=calculate_diffusivity, font=("Arial", 12))
button_diffusivity.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

# Create labels and text entry for sample density
label_density = tk.Label(root, text="Sample Density:", font=("Arial", 12),)
label_density.grid(row=5, column=0, padx=10, pady=5, sticky="e")

entry_density = tk.Entry(root, font=("Arial", 12))
entry_density.grid(row=5, column=1, padx=10, pady=5, sticky="w")

# Create labels and text entry for sample specific heat capacity
label_Cp = tk.Label(root, text="Sample Specific Heat Capacity:", font=("Arial", 12),)
label_Cp.grid(row=6, column=0, padx=10, pady=5, sticky="e")

entry_Cp = tk.Entry(root, font=("Arial", 12))
entry_Cp.grid(row=6, column=1, padx=10, pady=5, sticky="w")

# Create a button to calculate thermal conductivity
button_conductivity = tk.Button(root, text="Calculate Conductivity", command=calculate_conductivity, font=("Arial", 12))
button_conductivity.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

root.protocol("WM_DELETE_WINDOW", on_closing)  # Call on_closing() when the window is closed
root.mainloop()






