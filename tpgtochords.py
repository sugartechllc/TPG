#! /usr/local/bin/python3

import time
import json

import tpg
import pychords.tochords as tochords

def timestamp():
    t = time.gmtime()
    ts = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(t[0], t[1], t[2], t[3], t[4], t[5])
    return ts
 
if __name__ == '__main__':

    config_json = """
    {
        "chords": {
            "skey":    "secret_key",
            "host":    "chords_host.com",
            "enabled": true,
            "test":    false
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

    config = json.loads(config_json)

    # Start the CHORDS sender thread
    tochords.startSender()

    if "baud" in config["tpg"]:
        tpg = tpg.TPG(device=config["tpg"]["device"], baud=config["tpg"]["baud"])
    else:
        tpg = tpg.TPG(device=config["tpg"]["device"])        

    while True:
        print (tpg.reading())
        print(timestamp(), "Queue length: {:05}".format(tochords.waiting()))
        time.sleep(1)