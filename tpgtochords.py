#! /usr/local/bin/python3

import time

import pychords.tochords as tochords

def timestamp():
    t = time.localtime()
    ts = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(t[0], t[1], t[2], t[3], t[4], t[5])
    return ts
 
if __name__ == '__main__':

    # Start the CHORDS sender thread
    tochords.startSender()

    while True:
        print(timestamp(), "Queue length: {:05}".format(tochords.waiting()))
        time.sleep(1)