import csv
import logging
import sys
from datetime import datetime, timezone

from rtde import rtde_config as conf
from rtde.rtde import RTDE

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def get_sample(con: RTDE) -> tuple[int, float] | None:
    info = con.receive()  # Receive data from the RTDE stream
    if info is None:
        logger.warning("No data received from RTDE stream.")
        return None
    mode = info.robot_mode  # Get the robot mode
    a_time = info.output_double_register_0  # Get the active time
    return (mode, a_time)  # Return the sample as a tuple

def log_data(writer, file, sample):
    
    current_time = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")  # Get current UTC time
    mode, a_time = sample  # Unpack the sample
    writer.writerow([current_time, mode, a_time])  # Write data to CSV
    file.flush()




if __name__ == "__main__":
    config_file = config.ROBOTCONFIG  # Use the ROBOTCONFIG path from config.py

    path = config.CSV_PATH  # Use the CSV_PATH from config.py
    is_new = not path.exists()
    count = 0

    Robot_conf = conf.ConfigFile(config_file)         #instantiate the config file object
    names, types = Robot_conf.get_recipe("out")       #get the names and types of the output variables provieded through the XML recipe

    # RTDE connection parameters
    host = config.HOST
    port = config.PORT

    # Establish RTDE connection
    con = RTDE(host, port)         

    init = con.connect()   #Initialize the connection to the robot


    con.get_controller_version()          #Establish internal handshake with the robot controller
    channel_status = con.send_output_setup(names, types, frequency=config.POLLING_FREQUENCY) #Set up output channel with the specified names and types, and set the frequency to specififed value

    if channel_status == False:
        sys.exit("Unable to configure RTDE output")

    if not con.send_start():
        sys.exit("Unable to start RTDE stream")

    try: 
        with open(path, 'a', newline='') as file:
            writer = csv.writer(file)

            if is_new:
                writer.writerow(['Timestamp','Robot Mode', 'Active Time'])  # Write header if file is new

            sample_count = 0

            while (True):
                sample = get_sample(con)  # Get robot mode and active time
                if sample is None:
                    logger.warning("Sample is None, skipping this iteration.")
                    continue
                sample_count += 1
                if sample_count % (config.POLLING_FREQUENCY * config.WRITING_FREQUENCY) == 0:  # Log every 6 minutes (125 * 360 samples at 125 Hz)
                    log_data(writer, file, sample)  # Write data to CSV

    except KeyboardInterrupt:
        logger.info("Data logging stopped by user.")

    finally:
        con.send_pause()  # Pause the RTDE stream
        con.disconnect() # Ensure the connection is closed
