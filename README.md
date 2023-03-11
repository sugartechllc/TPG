# Total Precipitation Gauge
## Overview
A python module for interacting with the Sutron Total Precipitation Gauge (TPG). The
tpgtochords module is provided, which will send tpg readings and other system
health metrics to a [CHORDS portal](https://github.com/ncar/chords).

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

## RS-232 Interaction
The TPG prompts with `>` after any command. The typical interaction will be to send
a command, and read back lines until one containing just `>` is received.

Since the line with the prompt does not have a line terminator, the readline() will be issued with 
a timeout, so that the prompt line can be detected.

The text returned from the TPG is 'pretty formatted', and tpg.py has to dig through all of it
to extract the desired values. This is not really too hard; the approach will be to create a list 
of tokens, search for matching tupples such as `("Precip", "0.0018")` or 
`("System", "time", "2017/12/28", "22:45:33")`, and capture the desired readings.

## TPG Commands
These are the TPG commands used by tpg.py, and the associated output.

```
MEAS 
Reading
        Precip 0.0018 in

        Precip in bucket 0.6648 in
        Field Cal Offset -0.6630057 ,   Precip Rate 0.0038 in/hour


Temp In Box 21.62 C

>
```

```
TIME
System time 2017/12/28 22:45:33
```

```
BATT
Battery 11.8V


>
```

## tpgtochords
This module matches a custom data system buit around a Raspberry Pi Zero W, which performs the 
following:
 - Once per minute:
   - Read the TPG measurement.
   - Read pressure, temperature and humidity from a BME280 sensor.
   - Read power information from an INA_219 sensor.
   - Transmit to CHORDS.

### INA_219
 - Uses this [INA_219 package](https://github.com/chrisb2/pi_ina219).

## Annual Maintenance

```sh
    ssh tpg
    sudo systemctl stop tpgtochords
    minicom -D /dev/ttyUSB0
```

```sh
# Enter the DIAG command to see what the current 
# precip measurement is.
>DIAG
Resets total 0086
        0072 powerup, 0000 monitor
        0000 illegal,  0000 watchdog
        0000 unimplem, 0012 upgrade
        0000 unknown,  0002 soft


Sensor: 1
Precip: 33.1652
Min:    33.1647
Max:    33.1656
StdDev: 0.0001
Good:   8
Total:  8
mV:     9.6319
   Type "DIAG 0" to clear counts
```

Perform the maintenance:

   1. Remove cover
   1. Empty the bucket
   1. Clean the bucket
   1. Add 1 gal. of Green antifreeze
   1. Add 1 gal. of mineral oil
   1. Replace cover

Back to minicom:
```sh
# Set the precip measurement to the current value:
PRECIP = 33.1652
# Exit minicom:
ctrl-A ctrl-Z

sudo systemctl start tpgtochords
journalctl -f -u tpgtochords
```


