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

def calculate_utilization(samples: list[tuple[datetime, int, float]], powered_on_threshold:int = 4, readinterval:int = 4) -> UtilizationData:
    powered_on_time = 0.0
    for i in range(len(samples)-1):
        mode = samples[i][1]
        modecount = 0
        if mode >= powered_on_threshold:  # Assuming mode >= powered_on_threshold indicates ON state
            modecount +=1
            powered_on_time += modecount*readinterval

    startA_time = samples[0][2] if samples else 0.0
    endA_time = samples[-1][2] if samples else 0.0

    active_time = endA_time - startA_time

    idle_time = powered_on_time - active_time

    utilization = (active_time / powered_on_time) * 100 if powered_on_time > 0 else None

    return UtilizationData(powered_on_time, active_time, idle_time, utilization)