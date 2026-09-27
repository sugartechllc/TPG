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

Set the time:
```
TIME 2017/12/28 22:45:33
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

Do this at least once a year, and before the bucket reading nears the configured bucket
capacity. The gauge flags an error above 1.01 x the capacity, and `LAST` then appends
"Error in reading" to the Precip line. Choose dry weather.

**Two people are needed to empty a full bucket**, so that the load cell never takes a
sideways or lifting load.

### Before touching the bucket

```sh
    ssh tpg
    sudo systemctl stop tpgtochords
    minicom -D /dev/ttyUSB0 -b 115200
```

Capture the state and keep a record of it: `MEAS` (three times), `DIAG`, `CERT`, `TIME`
and `BATT`.

```sh
# Enter the MEAS command to see what the current 
# precip measurement is.
>MEAS
Reading
        Precip 96.3228 in

        Precip in bucket 33.1649 in
        Field Cal Offset 63.1579132 ,   Precip Rate 0.0000 in/hour


Temp In Box 11.80 C
```

 - **Write down the Precip value (the running total) before emptying anything.** It is
   the value to restore at the end. If the total is missing, take the last good value
   from the data or the gauge log.
 - `TIME` reports UTC. The clock drifts by about 2 minutes a month. If it is off by
   more than a minute, set it with `TIME yyyy/mm/dd hh:mm:ss`.
 - The gauge keeps only about 50 days of its own log. Download it with `LOG` (Ymodem
   in minicom) if it is wanted.

Look at the hardware before disturbing it. The plate must have a visible gap all round
from the top of the data logger (a sheet of paper slides freely), the load cell bolts
are snug (do not overtighten), the bubble level is centered, the cable is not pulled
tight, and nothing touches the bucket or plate. A plate bearing on the logger makes
part of any added weight bypass the load cell, giving a low and noisy reading.

### Empty and clean

   1. Remove cover
   1. Remove the liquid with the bucket in place (bailing cup or pump into a container).
      Never slide, tilt, pour or lift a full bucket.
   1. Lift out the nearly empty bucket straight up, pour out the rest, and dispose of the
      antifreeze and oil properly (not on the ground)
   1. Clean and dry the bucket
   1. Put the bucket back flat on the plate, not on the alignment bumps, and wait 10 minutes

### Check the calibration

With the empty, dry bucket, `MEAS` three times: the reading should be about 0 in with the
current calibration. Note it, since a change is a zero drift.

Then check with known weights (1 in of precipitation = 0.8236 kg; see the calibration
table in the TPG manual). Convert the mass in grams to inches by dividing by 823.6.

   1. `MEAS` three times with no weights (N1)
   1. Put the weights in the bucket, stacked and centered, wait 2 minutes, `MEAS` three
      times (W)
   1. Remove the weights, wait 2 minutes, `MEAS` three times (N2)

The delta is mean(W) - mean(N1, N2), and should agree with the expected value within 0.1%.
The readings within each set should agree to about 0.001 in.

If the check fails, first look for problems with the mount (plate clearance, bolts, the
bucket seating, how the weights sit) and repeat. Only recalibrate if it still fails on a
sound mount. Use the `CAL` command as described in the TPG manual: empty dry bucket,
wait 10 minutes, units `0` (in), the bucket capacity, and the known weight in inches
(wait 2 minutes after placing it before pressing the key). The manual expects a slope of
3.8 to 4.6 and an offset of -6.5 to -8.7 (inches). Then repeat the weight check. Any
`CAL`, even an aborted one, resets the Field Cal Offset, so `PRECIP` must be set afterwards.

### Refresh the antifreeze and mineral oil

   1. Add the antifreeze first
   1. Add the mineral oil on top, to stop evaporation (the manual suggests about 1/2 in of
      oil, roughly 2 L)
   1. Replace cover

The amount of antifreeze needed depends on the expected precipitation, since it is diluted
as the bucket fills (see the freezing point tables in the manual). Wait 10 minutes for the
reading to settle and `MEAS` once more.

### Set the precip and restart

Back to minicom:
```sh
# Set the precip measurement to the value from before the service:
>PRECIP = 96.3228
# Check it:
>MEAS
# Exit minicom:
ctrl-A Z X

sudo systemctl start tpgtochords
journalctl -f -u tpgtochords
```

Finally, confirm that data is arriving and that the total continues from the value that
was set, and check the solar panel, cable glands and battery voltage (`BATT`) at the
enclosure.

