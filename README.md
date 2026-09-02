# RTDE-Logger-Code:

Raspberry Pi based real time logger for robot time and utilization tracking

## Overview:

A system used to track the active time, total powered on time, idle time and utilization of the UR5e cobot used in various production activities. The logger generates accurate monthly reports on robot utilization and uploads it directly to the company server for easy access by the whole company. 



## Architecture/Workflow:

### Robot Timer:

The first step in the logging process is to track the active time of the robot, i.e. the time the robot is actively performing production activities. This is achieved by using the multithreading capability of PolyScope, whereby a separate thread is used to increment a timer tracking the active time. This thread acts as a daemonic thread and terminates when the parent program stops, even though it is NOT a daemonic thread. Note that the active timer is an installation variable and thus does not change on shutdown or reboot. The active time installation variable is then written to output_double_register_0, along with robot mode.  
  
### Pi logger:
Once the active timer data is available at  output_double_register_0, it is read and stored by the Raspberry Pi, along with robot mode. The raw data is stored in a CSV file on the Pi's hard drive, with the comma separated values following the format:  
  
>**Timestamp, Robot_Mode, Active_Time**  

Each value represents the following:
- Timestamp: The snapshot of time when the data is recorded.    

- Robot_Mode: A number that signifies the state of the robot. Modes greater than or equal to 4 mean the robot is powered on.

- Active_Time: The current value of the active timer installation variable.

Considering data is aggregated for the purpose of generating a monthly report, the CSV file stores data for each month, at the end of which the data is compiled into an Excel file  and the CSV is wiped clean to ensure no storage issues arise and the CSV is free for the next month's data.   
>**Note that the CSV is only wiped once the program verifies that the data has landed in the Excel file.**  

This compilation of data into the monthly Excel report is executed using the systemd service on the Pi and is scheduled to fire at 12:05 AM on the 1st of every month.

If the Pi is not powered on at the time of the compilation task (as could be the case if the Pi loses power or reboots at 12:05 AM) the compilation task is fired as soon as the Pi reboots and gains power again.

### Windows Relay:

In order to transfer the monthly data from the Pi's storage drive to the company server, a relay between the Pi and the server was to be set up, due to restrictions around direct file transfer from the Pi.  

As such, the 3D printing computer on the factory floor acts as a middle ground for the transfer of the monthly Excel report to the shared server. The 3D printer computer pulls the data file from the Pi at the end of each month using an SCP pull, saving a copy on the local drive as a backup and copying the monthly report onto the shared server. This is possible as the 3D printer computer is already authorized in the security system and has full access to the engineering drive. The SCP pull and copy task is run using Windows scheduler on the 2nd of every month. 

>**Note that the computer must be powered on and logged into the 3D printing user profile in order for the SCP pull and copy task to execute**

If the computer is not powered on or logged in at the time of the pull and copy task (as could be the case if the 2nd  of the month falls on a statutory holiday or a weekend) the pull task is fired as soon as possible when the computer is active and logged into.

## Code Components:

The code consists of 3 components:   

> - **Logger.py**: Connects to the UR5e cobot arm using the RTDE python client library. Reads from the RTDE port every 6 minutes to grab data. Runs continuously as a systemd service.  
>
> - **Utilization.py**: Calculates the monthly utilization, active time, powered on time and idle time by reading the CSV file with the monthly raw data.
>
> - **Report.py**: Aggregates the raw CSV data by calling the functions in Utilization.py and processing the data into an Excel file. Writes the finished file to the Pi's SD card (internal storage). Executes on the first of the month as a systemd service at 12:05 am.

### Additional supporting documents:
> - **config.py**: Stores all configuration values for the logger program, such as file paths, robot IP port number and constant values  
>
> - **RobotConfig.XML**: XML recipe that details to the Pi what information to grab from the RTDE port on the robot. 



