from os import path
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from subprocess import run, PIPE, CREATE_NO_WINDOW
from time import sleep
from threading import Thread
import chardet
from configparser import ConfigParser
from pystray import Menu, MenuItem, Icon
from PIL.Image import open as open_image
from PIL import ImageTk
import re
import json
import winreg as reg
import webbrowser
from os import path, getcwd 

settings_changed = True          
stop_ping_test = False
settings_window_instance = None

def read_settings():
    registry_path = r'Software\SimplerThread'
    default_settings = {
        "ping_count": "50"
    }

    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, registry_path, 0, reg.KEY_READ) as registry_key:
            settings_str, _ = reg.QueryValueEx(registry_key, 'Settings')
            settings = json.loads(settings_str)  # Deserialize the JSON string to a dictionary
    except (OSError, json.JSONDecodeError):
        print("Registry entry not found or invalid. Using default settings.")
        settings = default_settings  # Use default settings without saving them to the registry

    # Extract individual settings, converting to the appropriate type
    ping_count = int(settings["ping_count"])

    return ping_count

def update_statistics():
    tooltip = (
        f'Sent: {52}\n'
    )
    return tooltip

def ping_test(icon):
    global settings_changed
    global stop_ping_test
    global tray_icon
    global ping_count

    response_time_pattern = re.compile(r'(\d+(?:\.\d+)?)ms')

    while not stop_ping_test:
        if settings_changed:
            ping_count  = read_settings()
            settings_changed = False

        packet_loss = 0
        response_times = []
        response_time = 0

        i = 0
        while i < ping_count and not stop_ping_test:
            result = run(['ping', '-n', '1', '-w', str(250), 'google.com'], stdout=PIPE, creationflags=CREATE_NO_WINDOW)
            encoding = chardet.detect(result.stdout)['encoding']
            decoded_output = result.stdout.decode(encoding)
            match = response_time_pattern.search(decoded_output)
            if match:
                response_time = float(match.group(1))
                response_times.append(response_time)
            else:
                response_times.append(response_time)
                packet_loss += 1
            i += 1

        # Update tooltip with newer statistics
        packet_loss_percentage = (packet_loss / ping_count) * 100
        tooltip = update_statistics()
        tray_icon.title = tooltip

        # Set the system tray accordingly
        if packet_loss_percentage < 9:
            icon_change('Perfect.png')
        elif packet_loss_percentage < 18:
            icon_change('Good.png')
        elif packet_loss_percentage < 25:
            icon_change('Medium.png')
        else:
            icon_change('Bad.png')

def icon_change(name):
    script_folder = getcwd()
    icon_path = path.join(script_folder, "Icons", name)
    image = open_image(icon_path)
    tray_icon.icon = image

def on_right_click_settings(icon, item):
    Thread(target=open_settings_window, args=()).start()    
    
def open_settings_window():
    global settings_window_instance

    # Check if the settings window is already open
    if settings_window_instance is not None:
        settings_window_instance.lift()  # Bring the already open window to the front
        return
    
    # Create the main window and assign it to the global variable
    settings_window_instance = ctk.CTk()

    # Properly handle window closure
    def on_close():
        global settings_window_instance
        settings_window_instance.destroy()
        settings_window_instance = None  # Reset the global variable to allow reopening

    settings_window_instance.protocol("WM_DELETE_WINDOW", on_close)

    # Start the Tkinter event loop
    settings_window_instance.resizable(False, False)
    settings_window_instance.mainloop()
    
def setup_tray_icon():
    global tray_icon
    menu = Menu(MenuItem('Settings', on_right_click_settings))
    icon_path = path.join(path.dirname(path.abspath(__file__)), 'Icons', 'Waiting.png')
    icon = open_image(icon_path)
    tray_icon = Icon('Testing', icon,menu=menu)
    tray_icon.max_tooltip_width = 350
    return tray_icon

if __name__ == "__main__":
    # Start the ping Thread    
    tray_icon = setup_tray_icon()
    Thread(target=ping_test, args=(tray_icon,)).start()
    try:
        tray_icon.run()  # Run the system tray icon     
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
    finally:
        tray_icon.stop()  # Stop the system tray icon