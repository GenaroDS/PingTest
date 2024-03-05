from os import path
import tkinter as tk
import sys
import os
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
from CTkMessagebox import CTkMessagebox
import json
import winreg as reg
import webbrowser
from os import path, getcwd 


def set_value_in_file(key, value):
    config_file = "settings.json"
    config = {}
    if path.exists(config_file):
        with open(config_file, "r") as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError:
                pass  # If there's an error, just overwrite with new settings

    config[key] = value

    with open(config_file, "w") as file:
        json.dump(config, file)

def create_or_open_key():
    registry_path = r'Software\PingTester'  # Fixed path for the registry key
    try:
        # Try to open the key if it already exists
        registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, registry_path, 0, reg.KEY_WRITE)
    except FileNotFoundError:
        # If the key does not exist, create it
        registry_key = reg.CreateKey(reg.HKEY_CURRENT_USER, registry_path)
    return registry_key

def get_reg_value(key, default):
    registry_path = r'Software\PingTester'  # Use a more unique path to avoid conflicts
    try:
        with reg.OpenKey(reg.HKEY_CURRENT_USER, registry_path, 0, reg.KEY_READ) as registry_key:
            value, _ = reg.QueryValueEx(registry_key, key)
            return value
    except OSError as e:
        print(f"OSError while reading from registry: {e}")
        print("Falling back on default settings")
        # Fallback to a local file if registry access fails        
        return get_value_from_file(key, default)

def get_value_from_file(key, default):
    config_file = "settings.json"  # Local configuration file
    if path.exists(config_file):
        with open(config_file, "r") as file:
            try:
                config = json.load(file)
                return config.get(key, default)
            except json.JSONDecodeError as e:
                print(f"Error reading from config file: {e}")
    return default

def set_reg_value(key, value):
    try:
        with create_or_open_key() as registry_key:
            reg.SetValueEx(registry_key, key, 0, reg.REG_SZ, json.dumps(value))
    except WindowsError:
        pass

def safe_update(callable, *args):
    if 'settings_window_instance' in globals() and settings_window_instance is not None and settings_window_instance.winfo_exists():
        settings_window_instance.after(0, callable, *args)

def apply_changes(entries):
    def apply_changes_inner():
        config_to_save = {}
        for key in entries:
            config_to_save[key] = entries[key].get()

        try:
            set_reg_value('Settings', config_to_save)
            print("Changes applied to registry")
            global settings_changed
            settings_changed = True
            
        except OSError as e:
            print(f"Failed to write to registry: {e}, saving to file instead.")
            for key, value in config_to_save.items():
                set_value_in_file(key, value)
            print("Changes applied to file")

    safe_update(apply_changes_inner)
        
def update_tray_tooltip_safe(tooltip):
    if 'tray_icon' in globals() and tray_icon is not None:
        tray_icon.title = tooltip

def icon_change_safe(name):
    if 'tray_icon' in globals() and tray_icon is not None:
        icon_change(name)

def open_settings_window():
    global settings_window_instance

    if settings_window_instance is not None:
        settings_window_instance.deiconify()
        settings_window_instance.lift()
        return

    
    ctk.set_appearance_mode("Dark")
    settings_window_instance = ctk.CTk()
    settings_window_instance.title("Settings")
    icon_path = get_icon_path('Perfect.ico')
    settings_window_instance.after(201, lambda: settings_window_instance.iconbitmap(icon_path))

    entries = {}
    default_config = {
        "ping_count": 10,
        "seconds_between_pings": 0.33,
        "max_response_time": 150,
        "server_to_ping": "google.com",
        "perfect_threshold": 9,
        "good_threshold": 18,
        "medium_threshold": 28
    }

    try:
        stored_config_str = get_reg_value('Settings', '{}')
        stored_config = json.loads(stored_config_str) if stored_config_str else default_config
    except json.JSONDecodeError:
        print("Error loading configuration from registry. Using default configuration.")
        stored_config = default_config

    for i, (key, default) in enumerate(default_config.items()):
        label = ctk.CTkLabel(settings_window_instance, text=key.replace('_', ' ').capitalize() + ":")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        value = stored_config.get(key, default)
        entry = ctk.CTkEntry(settings_window_instance, textvariable=ctk.StringVar(value=str(value)))
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[key] = entry

    apply_button = ctk.CTkButton(settings_window_instance, text="Apply changes", command=lambda: apply_changes(entries))
    apply_button.grid(row=len(default_config), column=0, columnspan=2, pady=(5, 9))

    settings_window_instance.update_idletasks()
    window_width = settings_window_instance.winfo_reqwidth()
    window_height = settings_window_instance.winfo_reqheight()
    screen_width = settings_window_instance.winfo_screenwidth()
    screen_height = settings_window_instance.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2) - 40
    settings_window_instance.geometry(f'+{center_x}+{center_y}')


    def on_close():
        # Instead of destroying the window, just hide it
        settings_window_instance.withdraw()


    settings_window_instance.protocol("WM_DELETE_WINDOW", on_close)
    settings_window_instance.resizable(False, False)
    settings_window_instance.mainloop()

# Change system tray icon
def icon_change(name):
    script_folder = getcwd()
    icon_path = path.join(script_folder, "Icons", name)
    image = open_image(icon_path)
    tray_icon.icon = image
    
def icon_change_safe(name):
    if 'tray_icon' in globals() and tray_icon is not None:
        icon_path = get_icon_path(name)
        image = open_image(icon_path)
        tray_icon.icon = image
        
def get_icon_path(icon_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Si estamos ejecutando el archivo .exe empaquetado
        base_path = sys._MEIPASS
    else:
        # Si estamos ejecutando el script .py
        base_path = script_dir
    icon_path = os.path.join(base_path, 'Icons', icon_name)
    return icon_path

# Stop ping test and icon main thread thread when click on exit
def on_right_click_exit(icon, item):
    global stop_ping_test
    stop_ping_test = True
    icon.stop()

def on_right_click_settings(icon, item):
    Thread(target=open_settings_window).start()

#Updates tooltip statstics
def update_statistics(successful_pings, packet_loss, response_times):
    if successful_pings > 0:
        average_response_time = sum(response_times) / successful_pings
        min_response_time = min(response_times)
        max_response_time = max(response_times)
    else:
        average_response_time = 0
        min_response_time = 0
        max_response_time = 0

    packet_loss_percentage = (packet_loss / (successful_pings + packet_loss)) * 100
    tooltip = (
        f'[Packet statistics]\n'
        f'Sent: {successful_pings + packet_loss}\n'
        f'Lost: {packet_loss} ({packet_loss_percentage:.2f}%)\n'
        f'Avg. RTT: {average_response_time:.2f}ms\n'
        f'Min. RTT: {min_response_time:.2f}ms\n'
        f'Max. RTT: {max_response_time:.2f}ms'
    )
    return tooltip

def update_statistics_safe(successful_pings, packet_loss, response_times):
    if successful_pings > 0:
        average_response_time = sum(response_times) / successful_pings
        min_response_time = min(response_times)
        max_response_time = max(response_times)
    else:
        average_response_time = 0
        min_response_time = 0
        max_response_time = 0

    packet_loss_percentage = (packet_loss / (successful_pings + packet_loss)) * 100
    tooltip = (
        f'[Packet statistics]\n'
        f'Sent: {successful_pings + packet_loss}\n'
        f'Lost: {packet_loss} ({packet_loss_percentage:.2f}%)\n'
        f'Avg. RTT: {average_response_time:.2f}ms\n'
        f'Min. RTT: {min_response_time:.2f}ms\n'
        f'Max. RTT: {max_response_time:.2f}ms'
    )
    update_tray_tooltip_safe(tooltip)

#Define ping test
def ping_test(icon):
    
    global settings_changed, stop_ping_test, tray_icon
    global ping_count, seconds_between_pings, time_until_lost
    global server_to_ping, perfect_threshold, good_threshold, medium_threshold

    response_time_pattern = re.compile(r'(\d+(?:\.\d+)?)ms')

    while not stop_ping_test:
        if settings_changed:
            ping_count, seconds_between_pings, time_until_lost, server_to_ping, perfect_threshold, good_threshold, medium_threshold = read_settings()
            settings_changed = False

        successful_pings = 0
        packet_loss = 0
        response_times = []

        i = 0
        while i < ping_count and not stop_ping_test:
            result = run(['ping', '-n', '1', '-w', str(time_until_lost), server_to_ping], stdout=PIPE, creationflags=CREATE_NO_WINDOW)
            encoding = chardet.detect(result.stdout)['encoding']
            decoded_output = result.stdout.decode(encoding)
            match = response_time_pattern.search(decoded_output)
            sleep(seconds_between_pings)
            print(decoded_output + "Pinging to: " +server_to_ping)
            if match:
                successful_pings += 1
                response_time = float(match.group(1))
                response_times.append(response_time)
            else:
                packet_loss += 1
            i += 1

        packet_loss_percentage = (packet_loss / ping_count) * 100
        if packet_loss_percentage < perfect_threshold:
            icon_change_safe('Perfect.png')
        elif packet_loss_percentage < good_threshold:
            icon_change_safe('Good.png')
        elif packet_loss_percentage < medium_threshold:
            icon_change_safe('Medium.png')
        else:
            icon_change_safe('Bad.png')
        update_statistics_safe(successful_pings, packet_loss, response_times)

#Reads the current settings from the Settings.txt file.
def read_settings():
    registry_path = r'Software\PingTester'
    default_settings = {
        "ping_count": "10",
        "seconds_between_pings": "0.33",
        "max_response_time": "150",
        "server_to_ping": "google.com",
        "perfect_threshold": "9",
        "good_threshold": "18",
        "medium_threshold": "28"
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
    seconds_between_pings = float(settings["seconds_between_pings"])
    max_response_time = int(settings["max_response_time"])
    server_to_ping = settings["server_to_ping"]
    perfect_threshold = int(settings["perfect_threshold"])
    good_threshold = int(settings["good_threshold"])
    medium_threshold = int(settings["medium_threshold"])

    return ping_count, seconds_between_pings, max_response_time, server_to_ping, perfect_threshold, good_threshold, medium_threshold


def on_right_click_coffe(_=None):
    ko_fi_url = 'https://ko-fi.com/gdsdev'
    webbrowser.open(ko_fi_url)
# Set up system tray icon and context menu

# Reading settings and on_right_click_coffee function unchanged

def setup_tray_icon():
    global tray_icon
    menu = Menu(
        MenuItem('Like the app? Buy me a coffee!', on_right_click_coffe),
        MenuItem('Settings', on_right_click_settings),
        MenuItem('Exit', on_right_click_exit)
    )

    ping_count, seconds_between_pings, max_response_time, server_to_ping, perfect_threshold, good_threshold, medium_threshold = read_settings()
    estimated_test_time = ping_count * seconds_between_pings
    ftooltip = (
        f'[Performing test]\n'
        f'To: {server_to_ping}\n'
        f'Pings: {ping_count}\n'
        f'Interval: {seconds_between_pings}s\n'
        f'Timeout: {max_response_time}ms\n'
        f'Est. test time: {estimated_test_time:.1f}'
    )
    icon_path = path.join(path.dirname(path.abspath(__file__)), 'Icons', 'Waiting.png')
    icon = open_image(icon_path)
    tray_icon = Icon('Testing', icon, ftooltip, menu=menu)
    tray_icon.max_tooltip_width = 350

    return tray_icon

settings_changed = True
stop_ping_test = False
settings_window_instance = None

if __name__ == "__main__":
    tray_icon = setup_tray_icon()
    Thread(target=lambda: ping_test(tray_icon)).start()
    try:
        tray_icon.run()
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
    finally:
        tray_icon.stop()

    
    