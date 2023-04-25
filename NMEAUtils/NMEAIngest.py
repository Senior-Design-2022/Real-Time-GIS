import serial
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)
from pynmeagps import NMEAReader
from SocketUtils.SocketUtils import SITQueuedUDPSender
from CoTUtils.CoTUtility import CoTUtility

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def start_formatter(com, baud, host_ip, host_port):
    ser = serial.Serial(com, baud, timeout=1)
    reader = NMEAReader(ser)

    with SITQueuedUDPSender(host_ip, default_destination=(host_ip, host_port)) as out:
        out.Debug = False

        while True:
            # read data from serial port using NMEA parser
            (raw_data, parsed_data) = reader.read()
            
            # only ingest GPRMC messages
            if parsed_data.msgID == 'RMC':
                # check if message is valid
                if parsed_data.status == 'A':
                    # parse out lat, lon
                    lat = parsed_data.lat
                    lon = parsed_data.lon

                    # convert to CoT and send over UTPSender
                    cot_data = { 'uid': 'GPRMC', 'identity': 'friend', 'dimension': 'land-unit', 'type': 'C', 'lat': lat, 'lon': lon, 'detail': { 'track': { 'course': 0, 'speed': parsed_data.spd }}}
                    print(cot_data)
                    cot_xml = CoTUtility.toCoT(cot_data)
                    out.putitem(cot_xml)


# starter code
if __name__ == '__main__':

    #check command line args
    if len(sys.argv) != 5 or not sys.argv[2].isdigit() or not sys.argv[3].isdigit():
        print(f'{bcolors.FAIL}Usage: python NMEAIngest.py <ip_addr> <port> <baud> <COM>')

    # get command line arguments
    host_ip = sys.argv[1]           #"127.0.0.1"
    host_port = int(sys.argv[2])    # 1870
    baud = int(sys.argv[3])         # 9600
    com = sys.argv[4].upper()       # COM5

    print(f'{bcolors.OKBLUE}Starting NMEA Formatter on... \nIP: {host_ip} PORT: {host_port} COM: {com} BAUD: {baud}')
    start_formatter(com, baud, host_ip, host_port)
    


            
    
    
    
    
