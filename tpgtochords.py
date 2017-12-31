#! /usr/local/bin/python3

import time
import sys
import json

import tpg
import pychords.tochords as tochords

def make_chords_vars(old_hash, new_keys):
    """
    Rename the keys in a hash. If an old key does not 
    exist in the new_keys, remove it.
    """
    new_hash = {}
    for old_key, old_val in old_hash.items():
        if old_key in new_keys:
            new_hash[new_keys[old_key]] = old_val

    # The chords library wants the vars in a separate dict
    new_hash = { "vars": new_hash}
    return new_hash


def timestamp():
    t = time.gmtime()
    ts = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(t[0], t[1], t[2], t[3], t[4], t[5])
    return ts
 
if __name__ == '__main__':

    test_config = """
    {
        "chords": {
            "skey":    "secret_key",
            "host":    "chords_host.com",
            "enabled": true,
            "inst_id": "1",
            "test":    true,
            "sleep_secs": 5
        },
        "tpg": {
            "device":        "/dev/cu.usbserial",
            "baud":          115200,
            "station_name":  "Site 1",
            "auto_time":     "00:00:00",
            "auto_interval": "00:00:15",
            "avg_time":      "1.0"
        }
    }
    """

    new_keys = {
        'time': 'at',
        'precip': 'precip',
        'bucket': 'bucket',
        'rate': 'rate', 
        'temperature': 'temp', 
        'batt': 'battv'
    }

    print("Starting", sys.argv)

    if len(sys.argv) > 2:
        print ("Usage:", sys.argv[0], "[config_file]")
        sys.exit(1)

    if len(sys.argv) == 1:
        config = json.loads(test_config)
    else:
        config = json.loads(open(sys.argv[1]).read())

    # Extract some useful config values
    host = config["chords"]["host"]
    chords_options = {
        "inst_id": config["chords"]["inst_id"],
        "test": config["chords"]["test"],
        "skey": config["chords"]["skey"]
    }
    if "sleep_secs" in config["chords"]:
        sleep_secs = config["chords"]["sleep_secs"]
    else:
        sleep_secs = 5

    # Start the CHORDS sender thread
    tochords.startSender()

    if "baud" in config["tpg"]:
        tpg = tpg.TPG(device=config["tpg"]["device"], baud=config["tpg"]["baud"])
    else:
        tpg = tpg.TPG(device=config["tpg"]["device"])        

    while True:
        # get a reading from the tpg
        tpg_data = tpg.reading()
        # Make a chords variable dict to send to chords
        chords_record = make_chords_vars(tpg_data, new_keys)
        # Merge in the chords options
        chords_record.update(chords_options)
        # create the chords uri
        uri = tochords.buildURI(host, chords_record)
        # Send it to chords
        tochords.submitURI(uri, 720)
        # Flush the outputs
        sys.stdout.flush()
        sys.stderr.flush() 
        # Sleep until the next measurement time
        time.sleep(sleep_secs)
