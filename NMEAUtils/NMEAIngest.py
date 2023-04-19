import serial
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)
sys.path.append(parent_directory)
from pynmeagps import NMEAReader
from SocketUtils.SocketUtils import SITQueuedUDPSender
from CoTUtils.CoTUtility import CoTUtility


def start_formatter(baud, host_ip, host_port):
    ser = serial.Serial('COM5', baud, timeout=1)
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
    host_ip = "127.0.0.1"
    host_port = 1870
    baud = 9600

    start_formatter(baud, host_ip, host_port)


            
    
    
    
    
