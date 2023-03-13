import subprocess
import time

ping_count = 2
ping_interval = 1
minutes_between_pings = 1

while True:
    successful_pings = 0
    packet_loss = 0

    for i in range(ping_count):
        result = subprocess.run(['ping', '-n', '1', '-w', '1000', 'google.com'], stdout=subprocess.PIPE)
        if 'Reply from' in str(result.stdout):
            successful_pings += 1
        else:
            packet_loss += 1

        time.sleep(ping_interval)

    packet_loss_percentage = (packet_loss / ping_count) * 100

    print(f'Successful pings: {successful_pings}/{ping_count}, Packet loss: {packet_loss_percentage}%')

    packet_loss = 0

    time.sleep(minutes_between_pings * 60)