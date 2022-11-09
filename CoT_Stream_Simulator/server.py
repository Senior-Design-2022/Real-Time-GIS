# Beginning stages of a backend

import socket

class CoTServer:

    # initiate a server with given ip and port
    def __init__(self, ip, port, data_list) -> None:
        # init port and ip
        self.ip = ip
        self.port = port
        self.data = data_list

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
                if not data:
                    break
                print(data.decode("utf-8")) # this line will be changed
                                            # this is currently a string -- will need to convert to a tuple
                self.data.append(data.decode("utf-8"))
                


# if __name__ == "__main__":
#     host_ip = "127.0.0.1"
#     host_port = 1870
#     create_server(host_ip, host_port)