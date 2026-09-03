#This file holds all the configuration variables for the application. It is used to store settings that can be easily modified without changing the main codebase.
from pathlib import Path

#File pathing variables, for XML recipe and CSV intermediary file
ROBOTCONFIG = Path(r"C:\Users\localadmin\Desktop\RTDE Logger\RTDE-Logger-Code\RobotConfig.XML")
CSV_PATH = Path(r"U:\New Products\Student Files, archive\Rayyan Ashar (May 2026 - December 2026)\RTDE-Logger-Code\Source Code\data.csv")
EXCEL_PATH = Path(r"U:\New Products\Student Files, archive\Rayyan Ashar (May 2026 - December 2026)\RTDE-Logger-Code\Source Code\data.xlsx")

# RTDE connection parameters
HOST = "127.0.0.1"
PORT = 30004
READFREQ = 360 # frequency at which to read data from the robot in seconds
POLLING_FREQUENCY = 125 # in Hz, how often to poll the robot for data
WRITING_FREQUENCY = 360  # Time interval between writes to the CSV file, corresponds to a frequency of every 6 minutes
ROBOTMODE_THRESHOLD = 4  # robot_mode >= this counts as powered on; tune to change which states count
