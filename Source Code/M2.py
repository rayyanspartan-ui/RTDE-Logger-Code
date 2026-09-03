import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class UtilizationData:
    powered_on_time: float
    active_time: float
    idle_time: float
    
    utilization: float | None

def read_samples(path:Path) -> list[tuple[datetime, int, float]]:
    samples = []
    with open(path, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            timestamp = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")  # Parse timestamp  # noqa: DTZ007
            robot_mode = int(row[1])
            active_time = float(row[2])
            samples.append((timestamp, robot_mode, active_time))
    return samples

def calculate_utilization(samples: list[tuple[datetime, int, float]], powered_on_threshold:int = 4, readinterval:int = 360) -> UtilizationData:
    powered_on_time = 0.0
    for i in range(len(samples)):
        mode = samples[i][1]
        if mode >= powered_on_threshold:  # Assuming mode >= powered_on_threshold indicates ON state
            powered_on_time += readinterval\
    
    active_readings = [s[2] for s in samples if s[2]>0]  #Reading all active time values to calculate true active time, fileering out 0 values for inactivity of the robot

    if active_readings:         #Active time only calculated if the list is not empty

        startA_time = min(active_readings)
        endA_time = max(active_readings)
        active_time = endA_time - startA_time

    else: #empty list results in active time being 0
        
        active_time = 0
    
    idle_time = powered_on_time - active_time

    utilization = (active_time / powered_on_time) * 100 if powered_on_time > 0 else None

    return UtilizationData(powered_on_time, active_time, idle_time, utilization)