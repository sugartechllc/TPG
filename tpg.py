#! /usr/local/bin/python3
"""
TPG abstraction
"""

# pylint: disable=C0103
# pylint: disable=C0325

import re
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
        Configure the tpg for operation.

        NOT CURRENTLY IMPLEMENTED.
        """
        self.ser.reset_input_buffer()
        for l in ('', '', ''):
            self.write(l)
            lines = self.readlines()
            if verbose:
                print(l)
    
    def last(self):
        """
        Return {precip, bucket, rate, temperature}, plus error if the
        tpg reported one.
        """
        self.write('LAST')
        lines = self.readlines(firsttimeout=6)
        if verbose:
            print(lines)
        #
        # Valid returned lines (with blank lines removed):
        # [
        #   'LAST',
        #   'Reading',
        #   'Precip 0.0010 in',
        #   'Precip in bucket 0.6640 in',
        #   'Field Cal Offset -0.6630057 , \tPrecip Rate 0.1692 in/hour',
        #   'Temp In Box 21.84 C',
        #   '>'
        # ]
        #
        # When the tpg flags a problem (for example the bucket is over its
        # capacity), error text is appended to the Precip line, and there may
        # be additional error lines:
        # [
        #   'LAST',
        #   'Last Reading',
        #   'Precip 68.6833 in, Error in reading',
        #   'Precip in bucket 36.5498 in',
        #   ...
        # ]
        # The values are still valid, so find the lines by content rather
        # than position, and pass any error text back as "error".
        #

        retval = {}
        if not lines or lines[0] != 'LAST':
            return retval

        errors = []
        for l in lines[1:]:
            precip = re.match(r'Precip (\S+) \S+(?:, (.*))?$', l)
            bucket = re.match(r'Precip in bucket (\S+) \S+$', l)
            rate = re.search(r'Precip Rate (\S+) \S+$', l)
            temperature = re.match(r'Temp In Box (\S+) \S+$', l)
            if bucket:
                retval["bucket"] = bucket.group(1)
            elif precip:
                retval["precip"] = precip.group(1)
                if precip.group(2):
                    errors.append(precip.group(2))
            elif rate:
                retval["rate"] = rate.group(1)
            elif temperature:
                retval["temperature"] = temperature.group(1)
            elif l not in ('Reading', 'Last Reading', '>'):
                errors.append(l)

        if errors:
            retval["error"] = '; '.join(errors)

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
        retval.update(self.last())
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
