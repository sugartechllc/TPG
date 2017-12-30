#! /usr/local/bin/python3
"""
TPG abstraction
"""

# pylint: disable=C0103
# pylint: disable=C0325

import sys
import argparse
import serial

verbose = False

class TPG(object):
    """
    A Sutron Total Precipitation Guage.
    """
    def __init__(self, device, baud=115200):
        """
        """
        self.device = device
        self.baud = baud

        # Configure and open the terminal
        self.ser = serial.Serial()
        self.ser.port = self.device
        self.ser.baudrate = self.baud
        self.ser.open()
        self.config()

    def write(self, data):
        """
        Write to tpg
        """
        if verbose:
            print("write <" + data +">")
        self.ser.write((data+'\r').encode('UTF-8'))
        self.ser.flush()

    def config(self):
        """
        Configure the tpg for operation
        """
        self.ser.reset_input_buffer()
        for l in ('', '', ''):
            self.write(l)
            lines = self.readlines()
            if verbose:
                print(l)
    
    def meas(self):
        """
        Return {precip, rate, temperature}
        """
        self.write('MEAS')
        lines = self.readlines(firsttimeout=6)
        if verbose:
            print(lines)
        #
        # Valid returned lines (with blank lines removed):
        # [
        #   'MEAS',
        #   'Reading',
        #   'Precip 0.0010 in',
        #   'Precip in bucket 0.6640 in',
        #   'Field Cal Offset -0.6630057 , \tPrecip Rate 0.1692 in/hour',
        #   'Temp In Box 21.84 C',
        #   '>'
        # ]
        #

        retval = {}
        if len(lines) != 7:
            return retval
        if lines[0] != 'MEAS':
            return retval

        precip = lines[2].split(' ')
        if len(precip) == 3:
            retval["precip"] = precip[1]

        bucket = lines[3].split(' ')
        if len(bucket) == 5:
            retval["bucket"] = bucket[3]

        rate = lines[4].split(' ')
        if len(rate) == 9:
            retval["rate"] = rate[7]

        temperature = lines[5].split(' ')
        if len(temperature) == 5:
            retval["temperature"] = temperature[3]

        return retval

    def batt(self):
        """
        return battery voltage
        """

        self.write('BATT')
        lines = self.readlines()
        if verbose:
            print(lines)
        #
        # Valid returned lines (with blank lines removed):
        # [
        #   'BATT',
        #   'Battery 11.8V',
        #   '>'
        # ]

        retval = {}
        if len(lines) != 3:
            return retval
        if lines[0] != 'BATT':
            return retval

        batt = lines[1].split(' ')
        if len(batt) == 2:
            retval["batt"] = batt[1].replace('V','')

        return retval

    def time(self):
        """
        return the logger time
        """
        self.write('TIME')
        lines = self.readlines()
        if verbose:
            print(lines)
        #
        # Valid returned lines (with blank lines removed):
        # [
        #   'TIME', 
        #   'System time 2017/12/29 02:25:35', 
        #   '>'
        # ]
        retval = {}
        if len(lines) != 3:
            return retval
        if lines[0] != 'TIME':
            return retval

        timestamp = lines[1].split(' ')
        if len(timestamp) == 4:
            date = timestamp[2].split('/')
            retval["time"] = date[0]+"-"+date[1]+"-"+date[2]+'T'+timestamp[3]+'Z'

        return retval
    def reading(self):
        """
        return the combination of meas(), time() and batt()
        """
        retval = {}

        retval.update(self.time())
        retval.update(self.meas())
        retval.update(self.batt())
        
        return retval

    def readline(self, timeout=1):
        """
        Return the next available line, converted to a string.
        Leading and trailing whitespace is stripped.
        """
        self.ser.timeout = timeout
        l = self.ser.readline()
        l = l.decode('UTF-8').strip()
        return(l)

    def readlines(self, timeout=1, firsttimeout=None):
        """
        Specify firsttimeout if you want a longet timeoput for the first line. This is
        useful for reading back from commands that take a while to execute, such as the MEAS
        command.
        """
        lines = []
        lineno = 0
        while True:
            if lineno == 0:
                if firsttimeout:
                    t = firsttimeout
                else:
                    t = timeout
            else:
                t = timeout
            l = self.readline(timeout=t)
            if l != '':
                lines.append(l)
            if l == '>':
                break
            lineno = lineno + 1

        return lines

def parse_args(myargs):
    """
    Parse arguments.

    Return a dictionary of arguments.
    """
    global verbose

    parser = argparse.ArgumentParser(description='Test tpg.py.')
    parser.add_argument('--device', '-d', type=str, required=True,
                        help='serial device')
    parser.add_argument('--baud', '-b', type=int, default=115200,
                        help='baud rate')
    parser.add_argument('--verbose', '-v', default=False, action='store_true',
                        help='verbose')

    tpg_args = vars(parser.parse_args(myargs))

    verbose = tpg_args["verbose"]

    return tpg_args

if __name__ == '__main__':

    args = parse_args(sys.argv[1:])

    try:
        tpg = TPG(device=args['device'], baud=args['baud'])
    except serial.serialutil.SerialException as ex:
        print(ex)
        exit(1)

    while True:
        print(tpg.reading())
