#! /usr/local/bin/python3
"""
Read a tpg data logger CSV file, and send to CHORDS.

The CSV file is fetched from the Sutron TPG datalogger,
using the LOG N command via minicom. 
"""

# pylint: disable=C0103

import time
import sys
import json
import csv
import argparse

import pychords.tochords as tochords

def parseargs():
    '''
    Parse and check the arguments. 
    
    Print an error message if required
    arguments are missing.
    '''
    parser = argparse.ArgumentParser(description='Send TPG CSV data to CHORDS.')
    parser.add_argument('-c', '--config', type=str, nargs=1,
                        help='CHORDS configuration file')
    parser.add_argument('-f', '--file', type=str, nargs=1,
                        help='TPG csv data file')
    args = vars(parser.parse_args())

    if (args['config']==None) or (args['file']==None):
        print('Config and file arguments are required.')
        parser.print_usage()
        sys.exit(1)

    return(args)

def fetchcsv(tpgcsvfile):
    '''
    Read the csv file, and return a list contain dictionaries of samples.

    Each dictionary will contain:
    {
        'time': '2018-01-31T06:23:01Z',
        'name': 'Temp In Box',
        'value': '0.44'
    }

    The data in the TPG csv file looks like:
    02/06/2018,01:56:00,Precip,0.6638,in
    02/06/2018,01:56:00,Temp In Box,0.44,C
    02/06/2018,01:56:00,Batt Voltage,13.0,V
    02/06/2018,01:57:01,Precip Rate,0.0000

    There may be some superfluous lines, which this routine tries to ignore.

    '''

    retval = []
    with open(tpgcsvfile, newline='') as csvfile:
        reader = csv.DictReader(f=csvfile, fieldnames=['date', 'time', 'name', 'value', 'units'])
        for row in reader:
            if (row['date']!=None) and (row['time']!=None) and (row['name']!=None) and (row['value']!=None):
                    date = row['date']
                    time = row['time']
                    if len(date)==10 and len(time)==8:
                        iso8061 = date[6:10] + '-' + date[0:2] + '-' + date[3:5] + \
                                  'T' + \
                                  time + \
                                  'Z'
                        sample={}
                        sample['time'] = iso8061
                        sample['name'] = row['name']
                        sample['value']= row['value']
                        retval.append(sample)
                    else:
                        print('Timestamp error:', row)
    return(retval)

def process(chords_options, tpgdata):
    '''
    Process the TPG data and send it to CHORDS.

    tpgdata is an array of samples. Each sample is a dictionary, containing {'name', 'time', and 'value'}.
    sample['time'] is in iso8061 format.
    '''

    # Map TPG csv line 
    chords_keys = {
        'Precip': 'precip',
        'Precip Rate': 'rate',
        'Temp In Box': 'temp',
        'Batt Voltage': 'battv'
    }

    for sample in tpgdata:
        if sample['name'] in chords_keys:
            # collect the chords parameters
            uri_params = {}
            uri_params['inst_id'] = chords_options['inst_id']
            uri_params['skey'] = chords_options['skey']
            uri_params['test'] = chords_options['test']
            uri_params['vars'] = {
                    'at': sample['time'],
                    chords_keys[sample['name']]: sample['value']
                }
            # create the chords uri
            uri = tochords.buildURI(chords_options['host'], uri_params)
            # Send it to chords
            tochords.submitURI(uri, 1440)
            print(uri)
            time.sleep(0.5)

        else:
            print('Unknown sample:', sample)

if __name__ == '__main__':

    # The config file needs to contain at least:
    # {
    #    "skey":    "secret_key",
    #    "host":    "chords_host.com",
    #    "inst_id": "1",
    #    "test":    false
    # }

    args = parseargs()
    configfile = args['config'][0]
    tpgcsvfile = args['file'][0]

    # Start the CHORDS sender thread
    tochords.startSender()

    # Load the CHORDS configuration.
    config = json.loads(open(configfile).read())
    chords_options = config['chords']

    # Open and load the CSV file into a list
    tpgdata = fetchcsv(tpgcsvfile=tpgcsvfile)

    process(chords_options=chords_options, tpgdata=tpgdata)


