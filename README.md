# PingTest
PingTest is a clean, lightweight system tray app that monitors your internet connection quality using colored icons and data. It employs multithreading for continuous background ping tests, updating the system tray icon with real-time results. Users can customize the ping test, changing the host, amount of pings, and other settings to tailor the monitoring to their specific needs.  
The ping test is easily customizable through the settings options available in the context menu of the system tray icon.

## What is a Ping Test?
A ping test measures the speed and stability of an internet connection by sending data packets between your computer and a server. This helps identify connection issues that impact activities requiring stable data transfer, like competitive gaming.

## Screenshots
The system tray icon changes color based on connection stability:

<img src="Screenshots/Blue circle.jpg" alt="BlueCricle">&nbsp;
<img src="Screenshots/Green circle.jpg" alt="GreenCircle">&nbsp;
<img src="Screenshots/Yellow circle.jpg" alt="YellowCircle">&nbsp;
<img src="Screenshots/Red circle.jpg" alt="RedCircle">&nbsp;&nbsp;
<img src="Screenshots/Testing.jpg" alt="Testing...">

Colors represent different packet loss percentages: blue (<9%), green (<18%), yellow (<28%), and red (>=28%).  
Through the settings window, you can customize each threshold to your preference.  
The clock icon appears initially, awaiting results.

## Conclusion
PingTest allows you to effortlessly monitor your internet connection's stability, identifying potential issues while you use your computer normally.

## Instalation

1 - Clone the repository or download the project files:
```git clone https://github.com/GenaroDS/PingTest.git```  
2 - Install Python, if not already installed, download the Python installer from the official website:
``` https://www.python.org/downloads/ ```  
3 - Install the required dependencies: Open a terminal or command prompt, navigate to the project folder, and run the following command:
```pip install chardet pystray pillow configparser```   
4 - Install pyinstaller: If the user hasn't installed pyinstaller already, they can do so by running the following command in the terminal or command prompt:
```pip install pyinstaller```  
5 - Create the executable:
In the terminal or command prompt, navigate to the folder containing the PackageTester.py script and run the following command to create a standalone executable file along with the required resources:
```pyinstaller --noconsole --add-data "Icons/*;Icons/" --add-data "Settings.txt;." PackageTester.py ```
6 - Locate the excecutable inside the dist folder and excecute it.
