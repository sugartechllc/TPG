# Mtn King TPG Field Notes

## 2024-11-23
- Annual maintenance:
  - Emptied bucket.
  - Cleaned instrument.
  - Added 1 gal. 50/50 green antifreeze.
  - Add 1/4 gal. mineral oil.
  - Reset PRECIP = 136.3346"


## 2023-03-11
- Annual maintenance:
  - Emptied bucket.
  - Cleaned instrument.
  - Added 1 gal. 50/50 green antifreeze.
  - Add 3/4 gal. mineral oil.
  - Reset PRECIP = 96.33"

## 2018-02-23
 - Rebooted the tpg pi, and got data flowing again.
 - Downloaded the February csv data from the TPG data logger.
 - Wrote cvstochords.py, and submitted the missing TPG data to CHORDS.

## 2018-02-02
 - TPG system stopped connecting to CHORDS; probably due to flakey internet repeater "kitchen".

## 2018-01-20
 - Added 2 qts. mineral to stop the evaporation that has been happening over the last week
 - Changed the autosample interval from 15s to 1min.
 - Changed tpg.py to use the LAST command rather than the MEAS command. 
   This command doesn't have the time lag of the MEAS command, and perhaps it will save a 
   little on power draw.
 - Reset the precip reading to 0.
 
