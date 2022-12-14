#
# Class to simulate sending multiple data streams to the server
#

import sqlite3
import os
import socket
import time

import json

class StreamSimulator:

    def __init__(self, host_ip, host_port, target_id, table_name, src, config_filename) -> None:

        self.host_ip = host_ip
        self.host_port = host_port
        self.target_id = target_id
        self.table_name = table_name
        self.src = src
        self.load_config_dict(config_filename)

    def load_config_dict(self, config_filename):
        path = os.path.join(os.getcwd(), config_filename)
        with open(path) as fi:
            self.config_dict = json.load(fi)

    # gets CoT data from the database file
    def get_CoT_from_db(self, table_name, src, target_id):
        
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

        #
        # for testing
        #
        #for row in rows:
        #    print(row)

        print(f"got the rows!!!!! ({target_id}")

        table_description = cur.description
        header_row = [col[0] for col in table_description]  # idk why desc is in that format.

        return rows, header_row


    # simulates a client sending data to the server
    # server must be open on host_ip:host_port to run
    def simulate_CoT_stream(self, data, header_row, host_ip, host_port):
        
        # init socket
        # AF_INET = ipv4
        # SOCK_STREAM = TCP
        try:
            s = socket.socket()
            s.connect((host_ip, host_port))
        except socket.error as err:
            print("socket creation failed with error %s" %(err))
            return
        
        header_idx2name = {}
        for c, el in enumerate(header_row):
            header_idx2name[el] = c
        
        print(s.recv(1024).decode()) # receive test message from server to confirm connection

        # for each CoT object
        for row in data:
            # socket can send bytes.
            row_as_string = f"({row[0]}, {row[1]}, {row[2]}, {row[3]}, {row[4]})"
            #print(f"sending: {row_as_string}")
            #s.send(row_as_string.encode()) # send CoT

            to_send = {}
            for key, val in self.config_dict["col_names"]["to_send"].items():
                to_send[key] = row[header_idx2name[val]]

            #to_send["data"] = row
            json_string = json.dumps(to_send)
            print("sending " + json_string)
            s.send(json_string.encode())

            time.sleep(1)
            
        s.close() # disconnect from socket
        return