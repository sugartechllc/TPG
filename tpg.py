#! /usr/local/bin/python3
# pylint: disable=C0103
# pylint: disable=C0325

import sys
import argparse
import serial

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
        self.ser.write(data.encode('UTF-8'))
        self.ser.flush()

    def config(self):
        """
        Configure the tpg for operation
        """
        print('Configuring')
        self.ser.reset_input_buffer()
        for l in ('\n', 'BATT\n', 'Exit\n'):
            self.write(l)
            print('>>>', self.readline())

    def readline(self):
        """
        Return the next avaiable line, converted to a string.
        Leading and trailing whitespace is stripped.
        """
        l = self.ser.readline()
        l = l.decode('UTF-8').strip()
        return(l)
        
    def print_lines(self):
        """
          Readlines and print them. 
          Function does not return.
        """
        while(True):
            print(self.readline())

def parse_args(myargs):
    """
    Parse arguments.

    Return a dictionary of arguments.
    """
    parser = argparse.ArgumentParser(description='Test tpg.py.')
    parser.add_argument('--device', '-d', type=str, required=True,
                        help='serial device')
    parser.add_argument('--baud', '-b', type=int, default=115200,
                        help='baud rate')
    parser.add_argument('--test', '-t', type=bool, default=False,
                        help='test mode')

    tpg_args = vars(parser.parse_args(myargs))
    return tpg_args

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    try:
        tpg = TPG(device=args['device'], baud=args['baud'])
    except serial.serialutil.SerialException as ex:
        print(ex)
        exit(1)

    tpg.print_lines()
