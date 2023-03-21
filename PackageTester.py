from os import path
from subprocess import run, PIPE, CREATE_NO_WINDOW
from time import sleep
from threading import Thread
import chardet
from configparser import ConfigParser
from pystray import Menu, MenuItem, Icon
from PIL.Image import open as open_image
import re
from os import path, getcwd 

# Set flags for ping_test
settings_changed = True          
stop_ping_test = False

#Open settings file
def open_settings():
    global settings_changed
    run(["notepad.exe", "Settings.txt"])
    settings_changed = True

# Change system tray icon
def icon_change(name):
    script_folder = getcwd()
    icon_path = path.join(script_folder, "Icons", name)
    image = open_image(icon_path)
    tray_icon.icon = image

# Stop ping test and icon main thread thread when click on exit
def on_right_click(icon, item):
        global stop_ping_test
        stop_ping_test = True
        icon.stop()

#Create a third thread when settings is opened
def on_right_click_settings(icon, item):
        Thread(target=open_settings, args=()).start()

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
    global perfect_threshold
    global good_threshold
    global medium_threshold

    # Compile the regular expression pattern to extract the response time
    response_time_pattern = re.compile(r'(\d+(?:\.\d+)?)ms')

    while not stop_ping_test:
        # Reload settings if modified
        if settings_changed:
            ping_count, seconds_between_pings, time_until_lost, server_to_ping, perfect_threshold, good_threshold, medium_threshold  = read_settings()
            settings_changed = False

        # Initialize statistics variables
        successful_pings = 0
        packet_loss = 0
        response_times = []
        response_time = 0

        # Run ping command x amount of times 3 times per second.
        i = 0
        while i < ping_count and not stop_ping_test:
            result = run(['ping', '-n', '1', '-w', str(time_until_lost), server_to_ping], stdout=PIPE, creationflags=CREATE_NO_WINDOW)
            
            encoding = chardet.detect(result.stdout)['encoding']
            decoded_output = result.stdout.decode(encoding)
            print(decoded_output)
            match = response_time_pattern.search(decoded_output)
            sleep(10)
            if match:
                successful_pings += 1
                response_time = float(match.group(1))
                response_times.append(response_time)
            else:
                response_times.append(response_time)
                packet_loss += 1
            sleep(seconds_between_pings)

            i += 1

        # Update tooltip with newer statistics
        packet_loss_percentage = (packet_loss / ping_count) * 100
        tooltip = update_statistics(successful_pings, packet_loss, response_times)
        tray_icon.title = tooltip

        # Set the system tray accordingly
        if packet_loss_percentage < perfect_threshold:
            icon_change('Perfect.png')
        elif packet_loss_percentage < good_threshold:
            icon_change('Good.png')
        elif packet_loss_percentage < medium_threshold:
            icon_change('Medium.png')
        else:
            icon_change('Bad.png')

#Reads the current settings from the Settings.txt file.
def read_settings():
    config = ConfigParser()
    config_file = "Settings.txt"
    if not path.exists(config_file):
        config["Settings"] = {
            "ping_count": "40",
            "seconds_between_pings": "0.33",
            "max_response_time": "150",
            "server_to_ping": "google.com",
            "perfect_threshold": "9",
            "good_threshold": "18",
            "medium_threshold": "28"
        }
        with open(config_file, "w") as file:
            config.write(file)
    config.read(config_file)
    ping_count = int(config["Settings"]["ping_count"])
    seconds_between_pings = float(config["Settings"]["seconds_between_pings"])
    max_response_time = int(config["Settings"]["max_response_time"])
    server_to_ping = config["Settings"]["server_to_ping"]
    perfect_threshold = int(config["Settings"]["perfect_threshold"])
    good_threshold = int(config["Settings"]["good_threshold"])
    medium_threshold = int(config["Settings"]["medium_threshold"])

    return ping_count, seconds_between_pings, max_response_time, server_to_ping, perfect_threshold, good_threshold, medium_threshold

# Set up system tray icon and context menu
def setup_tray_icon():
    global tray_icon
    menu = Menu(MenuItem('Settings', on_right_click_settings),
                MenuItem('Exit', on_right_click))

    ping_count, seconds_between_pings, max_response_time, server_to_ping, perfect_threshold, good_threshold, medium_threshold = read_settings()
    estimated_test_time = ping_count * seconds_between_pings
    ftooltip = (
            f'[Performing test]\n'
            f'To: {server_to_ping}\n'
            f'Pings: {ping_count}\n'
            f'Interval: {seconds_between_pings}s\n'
            f'Timeout: {max_response_time}ms\n'
            f'Est. test time: {estimated_test_time:.1f}s '
        )
    icon_path = path.join(path.dirname(path.abspath(__file__)), 'Icons', 'Waiting.png')
    icon = open_image(icon_path)
    tray_icon = Icon('Testing', icon, ftooltip, menu=menu)
    tray_icon.max_tooltip_width = 350

    return tray_icon

# Global variables
settings_changed = True
stop_ping_test = False

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

    
    
