"""
Replays previous input streams

@author: R.Clark
"""

import sys
import threading
import time
import sqlite3
import os.path
import time
from SocketUtils.SocketUtils import QueuedUDPSender
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

class StreamSimulator:

    def __init__(self, host_ip, host_port, target_id, table_name, src, debug) -> None:

        self.host_ip = host_ip
        self.host_port = host_port
        self.target_id = target_id
        self.table_name = table_name
        self.src = src
        self.debug = debug

    # gets CoT data from the database file
    def get_CoT_from_db(self, table_name, src, target_id):
        
        if debug: print("attempting to access db")

        # use absolute path to get db file location
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, src)

        #try to connect to database
        try:
            con = sqlite3.connect(db_path)
            cur = con.cursor()
        except:
            print(f"Error connecting to source: '{db_path}'")
            return

        if debug: print("connected to db")

        #define query
        if target_id == "all":
            # will get all CoT data from the database
            query = f"SELECT * FROM \"{table_name}\""
        else:
            # gets only data from specific target
            query = f"SELECT * FROM \"{table_name}\" WHERE Report_TargetNum=\'{target_id}\'"

        #try to execute query
        res = None
        try:
            res = cur.execute(query)
        except:
            print("Failed to execute query")
            return

        # gets all data from given query as tuples with schema
        # (Measurement_DateTime, Report_TargetNum, Target_PositionLatitude, Target_PositionLongitude, Target_PositionAltitude)
        rows = cur.fetchall()

        if debug:
            for row in rows:
                print(row)

        return rows


    def create_UDP_sender(self, data, host_ip, host_port):
        if debug: print("in create_UDP_sender")

        with QueuedUDPSender(host_ip, default_destination=(host_ip, host_port)) as out:
            out.Debug= False
            
            if debug: print("created a QueuedUDPSender")

            if data[0]:
                print(f"{bcolors.OKBLUE}Now replaying {data[0][1]} starting at {data[0][0]}{bcolors.ENDC}")
            

            # will run through each point
            for data_point in data:
                time.sleep(0.5)

                # (Measurement_DateTime, Report_TargetNum, Target_PositionLatitude, Target_PositionLongitude, Target_PositionAltitude)
                cot_data = { "uid": data_point[1], "lat": data_point[2], "lon": data_point[3], "detail": { "track": { "course": 0, "speed": 0 } } }
                cot_xml = CoTUtility.toCoT(cot_data)
                out.putitem(cot_xml)
                print(cot_xml)

        return


def create_stream(host_ip, host_port, target_id, table_name, src, debug):
    if debug: print("creating a stream")
    stream = StreamSimulator(host_ip, host_port, target_id, table_name, src, debug)
    stream.create_UDP_sender(stream.get_CoT_from_db(table_name, src, target_id), host_ip, host_port)


if __name__ == "__main__":

    # check command line input
    if (len(sys.argv) != 2 or not sys.argv[1].isdigit()):
        print(f"{bcolors.FAIL}Usage: python3 stream_simulator.py <number of streams>{bcolors.ENDC}") 
    else:
        table_name = "ToCoTData"
        src = "20220901ADSB.sq3"
        host_ip = "127.0.0.1"
        host_port = 1870

        # Some sample targets for testing
        target_ids = [  
                        "11279804.N88ZA",
                        "10531224.N144AM",
                        "10797116.N405LP",
                        "11329446.N929AN",
                        "11133841.N736YX",
                        "11124112.N727AC",
                        "11123333.N726H"
                    ]

        number_of_streams = int(sys.argv[1])
        debug = False

        if (number_of_streams > len(target_ids)):
            print(f'{bcolors.FAIL}Error: Invalid number of streams. Must be greater than 0 and less than {len(target_ids)}.{bcolors.ENDC}')
        else:
            print(f"{bcolors.OKGREEN }Simulating {number_of_streams} streams...{bcolors.ENDC}")
            print(f"{bcolors.OKGREEN }Press CTRL + C to stop simulating{bcolors.ENDC}")
            print(f"{bcolors.WARNING}Initializing the threads may take some time{bcolors.ENDC}")

            for i in range(0, number_of_streams):
                thread = threading.Thread(target=create_stream, args=(host_ip, host_port, target_ids[i], table_name, src, debug), daemon=True)
                thread.start()

            while True:
                continue

        
    