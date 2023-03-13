import subprocess
import time
import os
import threading
import sys

from PIL import Image
import pystray

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
            result = subprocess.run(['ping', '-n', '1', '-w', '150', 'google.com'], stdout=subprocess.PIPE)
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
            time.sleep(0.33)

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
        tooltip = f'Packet loss: {packet_loss_percentage:.2f}%\nAverage: {average_response_time:.2f}ms\nMin: {min_response_time:.2f}ms\nMax: {max_response_time:.2f}ms\nSent: {successful_pings + packet_loss}'
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


# Set up system tray menu
menu = pystray.Menu(pystray.MenuItem('Exit', on_right_click))

#Amount of pings
ping_count = 100

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
