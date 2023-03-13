import subprocess
import time
import sys
import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu

#System tray icon method
def icon_change(name):
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    icon = QIcon(icon_path)
    tray_icon.setIcon(icon)

ping_count = 100
ping_interval = 1
minutes_between_pings = 1
app = QApplication(sys.argv)

# set the application icon
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Icons/Waiting.svg')
icon = QIcon(icon_path)
app.setWindowIcon(icon)

# create a system tray icon
tray_icon = QSystemTrayIcon(icon, app)
tray_icon.setVisible(True)
tray_icon.setToolTip('Testing...')


while True:
    successful_pings = 0
    packet_loss = 0
    total_response_time = 0
    response_times = []

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

        time.sleep(ping_interval/3)

    packet_loss_percentage = (packet_loss / ping_count) * 100


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
    tray_icon.setToolTip(tooltip)

    if packet_loss_percentage < 9:
        icon_change('Icons/Perfect.svg')
    elif packet_loss_percentage < 18:
        icon_change('Icons/Good.svg')
    elif packet_loss_percentage < 28:        
        icon_change('Icons/Medium.svg')
    else:
        icon_change('Icons/Bad.svg')

    packet_loss = 0
    total_response_time = 0



sys.exit(app.exec_())

