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

# Change system tray icon
def icon_change(name):
    icon_path = os.path.join(sys._MEIPASS, name) if hasattr(sys, '_MEIPASS') else name
    image = Image.open(icon_path)
    tray_icon.icon = image

# Handle right click on the system tray icon
def on_right_click(icon, item):
        global stop_ping_test
        stop_ping_test = True
        icon.stop()

#Define ping test
def ping_test():
    while not stop_ping_test:
        successful_pings = 0
        packet_loss = 0
        total_response_time = 0
        response_times = []
        response_time = 0  # set default value
        
        #Run ping command x amount of times 3 times per second.
        for i in range(ping_count):
            result = subprocess.run(['ping', '-n', '1', '-w', str(time_until_lost), server_to_ping], stdout=subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
            if 'Reply from' in str(result.stdout):
                successful_pings += 1
                # extract the response time from the output
                response_time = float(result.stdout.decode('utf-8').split('time=')[1].split('ms')[0])
                total_response_time += response_time
                response_times.append(response_time)
            else:
                total_response_time += response_time
                response_times.append(response_time)
                packet_loss += 1            
            time.sleep(seconds_between_pings)

        packet_loss_percentage = (packet_loss / ping_count) * 100

        #Add packets data to the variables
        if successful_pings > 0:
            average_response_time = total_response_time / successful_pings
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            average_response_time = 0
            min_response_time = 0
            max_response_time = 0

        # update the tooltip of the system tray icon with the statistics
        tooltip = f'[Packet statistics]\nSent: {successful_pings + packet_loss}\nLost: {packet_loss} ({packet_loss_percentage:.2f}%)\nAvg. RTT: {average_response_time:.2f}ms\nMin. RTT: {min_response_time:.2f}ms\nMax. RTT: {max_response_time:.2f}ms'
        tray_icon.title = tooltip

        #Set the system tray icon depending on packet loss percentages
        if packet_loss_percentage < 9:
            icon_change('Icons/Perfect.png')
        elif packet_loss_percentage < 18:
            icon_change('Icons/Good.png')
        elif packet_loss_percentage < 28:        
            icon_change('Icons/Medium.png')
        else:
            icon_change('Icons/Bad.png')

        #Restart Variables
        packet_loss = 0
        total_response_time = 0

#Start the ping test thread
def start_thread(icon):
    t = threading.Thread(target=ping_test)
    t.start()

#Reads the current settings from the Settings.txt file.
def read_settings():
    config = configparser.ConfigParser()
    config.read('Settings.txt')

    # Parse the settings
    ping_count = config.getint('Settings', 'ping_count')
    seconds_between_pings = config.getfloat('Settings', 'seconds_between_pings')
    time_until_lost = config.getint('Settings', 'time_until_lost')
    server_to_ping = config.get('Settings', 'server_to_ping')

    # Return tuple
    return ping_count, seconds_between_pings, time_until_lost, server_to_ping

# Set up system tray menu
menu = pystray.Menu(pystray.MenuItem('Exit', on_right_click))

# Fill variables with settings.txt
ping_count, seconds_between_pings, time_until_lost, server_to_ping = read_settings()

# Set up system tray icon
icon_path = os.path.join(sys._MEIPASS, 'Icons', 'Waiting.png') if hasattr(sys, '_MEIPASS') else 'Icons/Waiting.png'
icon = Image.open(icon_path)
tray_icon = pystray.Icon('Testing', icon, 'Testing...', menu=menu)

# flag to signal the ping_test thread to exit the loop
stop_ping_test = False

# Start the system tray icon
threading.Thread(target=start_thread, args=(tray_icon,)).start()

# Run 
try:
    tray_icon.run()  # Run the system tray icon loop
except Exception as e:
    print(f"Unexpected error occurred: {e}")
finally:
    tray_icon.stop()  # Stop the system tray icon loop
