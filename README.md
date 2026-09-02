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
> - **config.py**: Stores all configuration values for the logger program, such as file paths, robot IP, port number and constant values  
>
> - **RobotConfig.XML**: XML recipe that details to the Pi what information to grab from the RTDE port on the robot. 

## Operational Considerations:  
  
- ### Active Timer:   
     The active timer installation variable is integrated into each production program using two program variables, **base** and **Running_Time**. **base** takes the value of the active timer when the program variables are first initiated, meaning it stores the baseline value of the active timer before the production program has started, and **Running_Time** is a timer that tracks how long the production program runs. Each second, the value of running time is added to the baseline value stored in **base**, and the total value is assigned to the installation variable **Active_Time**. 
     
     >**IMPORTANT**: When implementing the **Running_Time** timer in other programs, the timer must always be set to Start and not Reset in order for it to increment. If set to Reset, the timer will not increment and **Active_Time** will stay constant, meaning the program will be logged as idle.

- ### Timer Coverage:
    Only programs that have the active timer integrated are logged as active programs. Programs without the active timer are logged as idle, meaning overall utilization data is undereported and thus inaccurate.
- ### Manual report firing:
    **DO NOT** run the report.py service manually at any point of time, as it will cause the CSV to be wiped and will result in loss of production data. Use dummy values and change the Excel path in **config.py** in order to test any changes to the code. In addition, any subsequent data will add a duplicate row of the same month into the Excel file.
- ### config.py git version:
    In order to keep the security of the company server intact, the version of **config.py** on GitHub contains dummy paths. If cloning the repo, make sure to change the path and constant values in **config.py** before implementation. Alternatively, make sure to only push/pull code files, never **config.py**.
- ### Data interpretation considerations:
    The robot is only authorized to be run between 7:00 am and 3:30 pm, the working hours of co-op students, as co-ops are mainly responsible to troubleshoot and tune programs. As such, utilization data should be compared to a total work time (absolute hours) of roughly 40 hours a week, rather than a full 24/7 operational window. The total powered on time reflects the 40 hour limited operating window, not a full 24/7 hour week.  
  
## Further Extensions/Current Limitations:
- **Separation of timers**:  
    Currently, there is only one active timer, meaning all production activities are lumped into one active time, without any specific details on which production activity is being carried out. Separation of active time by program or production activity can provide a more detailed picture of how the robot is being utilised. Implementation of segregated timers is scheduled to be rolled out over September 2026.   

    >#### Implementation of separate timers is as follows:
    > - **Polyscope**:   
        A similar integration of base + Running_Time must be implemented for each timer. The naming of different **base** and **Running_Time** variables is left to the discretion of the co-op student. In addition, separate installation variables must be created for each distinct timer. Timer data must be written to output registers 24-47, as further explained in **"Register use for further expansion"**.      
    >
    > - **Logger.py**:   
        The new data obtained from the additional output registers must be parsed using the sampling function (see program documentation comments in code) and a column with the new data must be added to each CSV row. The header row must also be updated.  
    >  
    > - **Utilization.py**:   
        Compute the active time, idle time, and utilization for each new timer added.  
    >    
    >- **Report.py**:  
        Add a column to the Excel report for each new timer and compile the data obtained from Utilization.py for each new timer. 
    >
    >### **Important**: 
    > The register number and column order MUST match between Polyscope, Logger.py, Utilization.py and Report.py. If the columns are misaligned, the system logs zero and DOES NOT throw an error. Make sure to test after adding a new timer to ensure the data is actually being read and logged.  
    > 

- **Idle time abstraction**:   
    At present, much like the active time, idle time does not separate true idle time (when the robot is sitting still while powered on) and testing time (when the co-op students are tuning or testing a program, but the program itself is not running a production activity). An accurate way of tracking testing time and true idle time is one way to make the report more detailed.  

- **Register use for further expansion**:  
    If any other timers or functionalities are to be introduced, register numbers 24-47 must be used, as registers 0-23 are reserved for Fieldbus activities. While Fieldbus is not currently being used, it is good practice to use registers meant for external data transfers, leaving Fieldbus capability free.
    > **Note**: If additional timers are used to segregate active time based on production activity, the XML recipe must be changed to read the new registers holding separate active time data, as mentioned previously.

- **Relay user restrictions**:  
    The current relay setup requires a user to be logged into the 3D computer in order for the relay to fire. A workaround where the Windows Task Scheduler is tied to the machine rather than the user account will simplify firing the windows relay greatly.

