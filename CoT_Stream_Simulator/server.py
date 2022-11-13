# Beginning stages of a backend

import socket

class CoTServer:

    # initiate a server with given ip and port
    def __init__(self, ip, port, data_holder) -> None:
        # init port and ip
        self.ip = ip
        self.port = port
        self.data = data_holder # passthrough variable from flask

    def create_server(self):
        host_ip = self.ip
        host_port = self.port

        #attempt to create socket
        try: 
            # AF_INET = ipv4
            # SOCK_STREAM = TCP
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #allows to ctrl+c out of a socket
            print("socket successfully created")
        except socket.error as err:
            print("socket creation failed with error %s" %(err))
            return

        # bind socket to ip and port
        try:
            s.bind((host_ip, host_port))
            print (f"socket binded to: {host_ip}:{host_port}")
        except socket.error as err:
            print(f"bind failed with error: {err}")
            return

        allowed_connections = 5 #number of connections to allow
        s.listen(allowed_connections)
        print(f"socket now listening")

        client, addr = s.accept() #accept incoming connections
        print(f"recieved connection from address: {addr}")
        client.send('connection established with server'.encode())

        #
        # CURRENTLY WILL CLOSE SOCKET AFTER ONE DATA STREAM -- WILL CHANGE TO ALLOW MULTIPLE STREAMS
        #
        with client:
            while True:
                data = client.recv(1024)
                
                #
                #   THIS NEEDS TO BE HANDLED DIFFERENTLY. NEED TO GRACEFULLY CLOSE THE CONNECTION AND ALLOW FOR OTHER CONNECTIONS
                #
                if not data:
                    break

                data_parsed = data.decode("utf-8") # parse data into string format
                data_parsed = data_parsed.replace('(', '').replace(')', '').replace(' ', '') # remove the parenthesis and spaces from the formatted string
                data_lst = data_parsed.split(',') # split by comma isolating each data field
                # index ||  field
                #   0   ||  timestamp
                #   1   ||  id
                #   2   ||  latitude
                #   3   ||  longitude 
                #   4   ||  altitude

                # assign to CoT passthrough with proper elements cast to their proper types
                
                self.data.time = data_lst[0]
                self.data.id = data_lst[1]
                self.data.lat = float(data_lst[2])
                self.data.lon = float(data_lst[3])
                self.data.alt = float(data_lst[4])

                
                print(self.data) # this line will be changed