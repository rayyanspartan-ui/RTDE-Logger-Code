import csv
from pathlib import Path
import time
from datetime import datetime, timezone

path = Path(r"U:\New Products\Student Files, archive\Rayyan Ashar (May 2026 - December 2026)\RTDE Logger\RTDE Logger Code\data.csv")
is_new = not path.exists()
count = 0

def get_sample():
    mode = 7  # Example robot mode
    global count
    sample = (mode, count)
    count += 1  # Increment count for each sample
    return sample

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

        while (True):
            sample = get_sample()  # Get robot mode and active time
            log_data(writer, file, sample)  # Write data to CSV
            time.sleep(1)  # Simulate some delay

except KeyboardInterrupt:
    print("Data logging stopped by user.")
