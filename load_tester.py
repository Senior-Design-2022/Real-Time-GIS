"""
Creates specified number of stream inputs at the same time

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


def get_CoT_from_db(table_name, src, target_id):
        
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

        return rows


def create_UDP_sender(data, host_ip, host_port):

    with QueuedUDPSender(host_ip, default_destination=(host_ip, host_port)) as out:
        out.Debug= False

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


if __name__ == "__main__":

    # check command line input
    if (len(sys.argv) != 2 or not sys.argv[1].isdigit()):
        print(f"{bcolors.FAIL}Usage: python3 load_tester.py <number of streams>{bcolors.ENDC}") 
    else:
        table_name = "ToCoTData"
        src = "20220901ADSB.sq3"
        host_ip = "127.0.0.1"
        host_port = 1870
        target_id = "11279804.N88ZA"

        desired_number_of_targets = int(sys.argv[1])

        data = get_CoT_from_db(table_name, src, target_id)

        generated_targets = []

        print(f"{bcolors.OKGREEN }Press CTRL + C to stop simulating{bcolors.ENDC}")

        # creates unique target id's
        print(f"{bcolors.HEADER}generating {desired_number_of_targets} targets...{bcolors.ENDC}")
        for i in range(0,desired_number_of_targets):
            current_target = []
            for row in data:
                x = list(row)
                x[1] = f"LT_TARGET_{i}"
                current_target.append(tuple(x))
            generated_targets.append(current_target)
        print(f"{bcolors.HEADER}done{bcolors.ENDC}")

        # send each individual target
        for i in range(0, desired_number_of_targets):
            print(f"{bcolors.BOLD}creating stream #{i}{bcolors.ENDC}")
            thread = threading.Thread(target=create_UDP_sender, args=(generated_targets[i], host_ip, host_port), daemon=True)
            thread.start()
        
        while True:
            continue

    
