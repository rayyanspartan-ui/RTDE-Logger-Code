import csv
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from rtde import rtde_config as conf
from rtde.rtde import RTDE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config_file = Path(r"C:\Users\localadmin\Desktop\RTDE Logger\RTDE-Logger-Code\RobotConfig.XML")

path = Path(r"C:\Users\localadmin\Desktop\RTDE Logger\RTDE-Logger-Code\data.csv")
is_new = not path.exists()
count = 0

config = conf.ConfigFile(config_file)         #instantiate the config file
names, types = config.get_recipe("out")       #get the names and types of the output recipe

# RTDE connection parameters
host = "127.0.0.1"
port = 30004

# Establish RTDE connection
con = RTDE(host, port)

init = con.connect()   #Initialize the connection to the robot


con.get_controller_version()          #Establish internal handshake with the robot controller
channel_status = con.send_output_setup(names, types, frequency=125) #Set up output channel with the specified names and types, and set the frequency to 1 Hz

if channel_status == False:
    sys.exit("Unable to configure RTDE output")

if not con.send_start():
    sys.exit("Unable to start RTDE stream")


def get_sample():
    info = con.receive()  # Receive data from the RTDE stream
    mode = info.robot_mode  # Get the robot mode
    a_time = info.output_double_register_0  # Get the active time
    return (mode, a_time)  # Return the sample as a tuple

def log_data(writer, file, sample):
   
    current_time = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")  # Get current UTC time
    mode, a_time = sample  # Unpack the sample
    writer.writerow([current_time, mode, a_time])  # Write data to CSV
    file.flush()


try: 
    with open(path, 'a', newline='') as file:
        writer = csv.writer(file)

        if is_new:
            writer.writerow(['Timestamp','Robot Mode', 'Active Time'])  # Write header if file is new

        sample_count = 0

        while (True):
            sample = get_sample()  # Get robot mode and active time
            if  sample is None:
                logger.warning("No data received from RTDE stream.")
                continue
            sample_count += 1
            if sample_count % 125 == 0:  # Log every 1 second (125 samples at 125 Hz)
                log_data(writer, file, sample)  # Write data to CSV

except KeyboardInterrupt:
    print("Data logging stopped by user.")

finally:
    con.send_pause()  # Pause the RTDE stream
    con.disconnect() # Ensure the connection is closed
