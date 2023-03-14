# PingTest

PingTest is a simple and clean system tray icon that displays the status of your internet connection using colored icons and data. It utilizes multithreading to continuously perform a ping test in the background and updates the system tray icon with the current status of the test after each iteration.
It should be noted that a packet that takes longer than 150ms to arrive is considered lost. The purpose of this application is to inform the user if their connection is stable enough for activities that require constant and reliable data transfer, such as competitive gaming and other similar activities.

## What is a Ping Test?
A ping test is a method used to measure the speed and stability of an internet connection. It works by sending a small packet of data from your computer to a specific server and measuring the time it takes for the server to respond. The result is a measurement of the time it takes for your computer to communicate with the server, which can help identify issues with your internet connection.

## Screenshots
Below are some screenshots showcasing the program's system tray colour changing depending on your internet stability:

<img src="Screenshots/Blue circle.jpg" alt="BlueCricle"> <img src="Screenshots/Green circle.jpg" alt="GreenCircle"> <img src="Screenshots/Yellow circle.jpg" alt="YellowCircle"> <img src="Screenshots/Red circle.jpg" alt="RedCircle"> <img src="Screenshots/Testing.jpg" alt="Testing...">

Each colour represents a different state. Blue means less than 9% of packet loss, green less than 18%, yellow less than 28%, and red more than that. The little clock is the first icon to appear, waiting for the results.

## Conclusion
By using PingTest, you can quickly and easily check the stability of your internet connection and identify any issues that may be affecting your connection speed. The program runs in the background, so you can continue using your computer as normal while PingTest works to keep you connected. 
