# Total Precipitation Gauge

A python module for interacting with the Sutron Total Precipitation Gauge (TPG).

The TPG onboard logger is configured and controlled by commands sent via the RS-232 port.

The configuration is establisehd by setting TPG variables. tpg.py sets a few of these at
startup, to insure that the gauge measurement behavior is always consistent. It uses 
a default set of values, but these may be overriden by values in the tpg.py configuration:

|TPG variable|tpg.py default|tpg.py config key|
|---------------------|---------|-------------|
|Station Name         |  n/a    |station_name |
|Automeasure Interval |00:01:00 |auto_time    |
|Automeasure Time     |00:00:00 |auto_interval|
|Averaging Time       |1.0      |avg_time     |
|Auto Output          |0        |             |


TPG readings are obtained by sending commands to the gauge, and parsing the returned output.
The two key commands are `MEAS` (perform a measurement) and `TIME` (return the system time).

Example output from `MEAS`:
```
MEAS 
Reading
        Precip 0.0018 in

        Precip in bucket 0.6648 in
        Field Cal Offset -0.6630057 ,   Precip Rate 0.0038 in/hour


Temp In Box 21.62 C

>
```

Example output from `TIME`:
```
TIME
System time 2017/12/28 22:45:33
```

