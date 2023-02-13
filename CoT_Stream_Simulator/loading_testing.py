# for load testing

import sqlite3
import os.path
import socket
import time
import threading

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

def simulate_CoT_stream(data, host_ip, host_port):
        
        # init socket
        # AF_INET = ipv4
        # SOCK_STREAM = TCP
        try:
            s = socket.socket()
            s.connect((host_ip, host_port))
        except socket.error as err:
            print("socket creation failed with error %s" %(err))
            return
        
        print(s.recv(1024).decode()) # receive test message from server to confirm connection

        # for each CoT object
        for row in data:
            # convert to string -- has to be done to send over socket
            row_as_string = f"({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]})"
            #print(f"sending: {row_as_string}")
            s.send(row_as_string.encode()) # send CoT
            time.sleep(1)
            
        s.close() # disconnect from socket
        print('disconnected')
        return


if __name__ == "__main__":
    table_name = "ToCoTData"
    src = "20220901ADSB.sq3"
    host_ip = "127.0.0.1"
    host_port = 1870
    target_id = "11279804.N88ZA"

    #
    # set this variable to the number of streams you want to be sent
    #
    desired_number_of_targets = 100

    data = get_CoT_from_db(table_name, src, target_id)

    generated_targets = []

    print(f"generating {desired_number_of_targets} targets...")
    for i in range(0,desired_number_of_targets):
        current_target = []
        for row in data:
            x = list(row)
            x[1] = f"LT_TARGET_{i}"
            current_target.append(tuple(x))
        generated_targets.append(current_target)
    print('done')

    for i in range(0, desired_number_of_targets):
        print(f"creating stream #{i}")
        thread = threading.Thread(target=simulate_CoT_stream, args=(generated_targets[i], host_ip, host_port), daemon=True)
        thread.start()
    
    while True:
        continue
