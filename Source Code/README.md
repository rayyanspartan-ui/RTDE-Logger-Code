# RTDE-Logger-Code:

Raspberry Pi based real time logger for robot time and utilization tracking

## Overview:

A system used to track the active time, total powered on time, idle time and utilization of the UR5e cobot used in various production activities. The logger generates accurate monthly reports on robot utilization and uploads it directly to the company server for easy access by the whole company. 



## Architecture/Workflow:

### Robot Timer:

The first step in the logging process is to track the active time of the robot, i.e. the time the robot is actively performing production activities. This is achieved by using the multithreading capability of PolyScope, whereby a separate thread is used to increment a timer tracking the active time. This thread acts as a daemonic thread and terminates when the parent program stops, even though it is NOT a daemonic thread. Note that the active timer is an installation variable and thus does not change on shutdown or reboot. The active time installation variable is then written to output_double_register_0, along with robot mode.  
  
### Pi logger:
Once the active timer data is available at  output_double_register_0, it is read and stored by the Raspberry Pi, along with robot mode. The aggragated data is stored in a CSV file on the Pi's hard drive, with the comma separated values following the format:  
  
>**Timestamp, Robot_Mode, Active_Time**  

- Timestamp: The snapshot of time when the data is recorded.    

- Robot_Mode: A number that signifies the state of the robot. Modes greater than or equal to 4 mean the robot is powered on.

- Active_Time: The current value of the active timer installation variable.

Considering data is aggregated for the purpose of generating a monthly report, the CSV file stores data for each month, at the end of which the data is compiled into an Excel file and the CSV is wiped clean to ensure no storage issues arise and the CSV is free for the next month's data.

### Windows Relay:

In order to 

