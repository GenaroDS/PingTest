import ctypes
import os
import win32process
import subprocess
import time
import threading
import sys
import configparser
import pystray
from PIL import Image

# Set flags for ping_test
settings_changed = True          
stop_ping_test = False

#Open settings file
def open_settings():
    global settings_changed
    subprocess.run(["notepad.exe", "Settings.txt"])
    settings_changed = True

# Change system tray icon
def icon_change(name):
    icon_path = os.path.join(sys._MEIPASS, name) if hasattr(sys, '_MEIPASS') else name
    image = Image.open(icon_path)
    tray_icon.icon = image

# Stop ping test and icon main thread thread when click on exit
def on_right_click(icon, item):
        global stop_ping_test
        stop_ping_test = True
        icon.stop()

#Create a third thread when settings is opened
def on_right_click_settings(icon, item):        
        threading.Thread(target=open_settings, args=()).start()

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

#Define ping test
def ping_test(icon):        
    global settings_changed
    global stop_ping_test
    global tray_icon
    global ping_count
    global seconds_between_pings
    global time_until_lost
    global server_to_ping        

    while not stop_ping_test:
        #Reaload settings if modified
        if settings_changed:
            ping_count, seconds_between_pings, time_until_lost, server_to_ping = read_settings()
            settings_changed = False

        # Initialize statistics variables                
        successful_pings = 0
        packet_loss = 0
        response_times = []
        response_time = 0  

        #Run ping command x amount of times 3 times per second.
        for i in range(ping_count):
            print(threading.enumerate())
            result = subprocess.run(['ping', '-n', '1', '-w', str(time_until_lost), server_to_ping], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)            
            if 'Reply from' in str(result.stdout):
                successful_pings += 1
                # extract the response time from the output
                response_time = float(result.stdout.decode('utf-8').split('time=')[1].split('ms')[0])
                response_times.append(response_time)
            else:
                response_times.append(response_time)
                packet_loss += 1            
            time.sleep(seconds_between_pings)
        

        # Update tooltip with newer statistick
        packet_loss_percentage = (packet_loss / ping_count) * 100
        tooltip = update_statistics(successful_pings, packet_loss, response_times)
        tray_icon.title = tooltip

        #Set the system tray accordingly
        if packet_loss_percentage < 9: 
            icon_change('Icons/Perfect.png')
        elif packet_loss_percentage < 18:
            icon_change('Icons/Good.png')
        elif packet_loss_percentage < 28:        
            icon_change('Icons/Medium.png')
        else:
            icon_change('Icons/Bad.png')
     

#Reads the current settings from the Settings.txt file.
def read_settings():
    config = configparser.ConfigParser()
    if hasattr(sys, '_MEIPASS'):
        # If running from PyInstaller executable, use sys._MEIPASS to find Settings.txt
        config.read(os.path.join(sys._MEIPASS, 'Settings.txt'))
    else:
        # If running from source code, use relative path to Settings.txt
        config.read('Settings.txt')

    # Parse the settings
    ping_count = config.getint('Settings', 'ping_count')

    try:
        seconds_between_pings = config.getfloat('Settings', 'seconds_between_pings')
    except ValueError:
        # If an error occurs while parsing seconds_between_pings, set its value to 0.33
        seconds_between_pings = 0.33
        config.set('Settings', 'seconds_between_pings', str(seconds_between_pings))
        with open('Settings.txt', 'w') as configfile:
            config.write(configfile)

    time_until_lost = config.getint('Settings', 'time_until_lost')
    server_to_ping = config.get('Settings', 'server_to_ping')

    # Return tuple
    return ping_count, seconds_between_pings, time_until_lost, server_to_ping


# Set up system tray icon and context menu
menu = pystray.Menu(pystray.MenuItem('Settings', on_right_click_settings),
                    pystray.MenuItem('Exit', on_right_click))
icon_path = os.path.join(sys._MEIPASS, 'Icons', 'Waiting.png') if hasattr(sys, '_MEIPASS') else 'Icons/Waiting.png'
icon = Image.open(icon_path)
tray_icon = pystray.Icon('Testing', icon, 'Testing...', menu=menu)
tray_icon.max_tooltip_width = 350

# Start the ping Thread
threading.Thread(target=ping_test, args=(tray_icon,)).start()

# Run icon on main thread
try:
    tray_icon.run()  # Run the system tray icon     
except Exception as e:
    print(f"Unexpected error occurred: {e}")
finally:
    tray_icon.stop()  # Stop the system tray icon
