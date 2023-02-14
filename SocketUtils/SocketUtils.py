"""
@author: A.Sedunov
"""

import queue
import struct
import time
import socket
import threading

class UDPThreadedClient:
    
    def __init__(self,UDPIP, UDPPORT,enable,queuesize):
        self.setsource(UDPIP, UDPPORT)
        self.enabled = enable
        self.connected = False
        self.Quit = False
        self.Queue1 = queue.Queue(queuesize)
        self.Debug = False
        self.LastSource = None
        self.default_destination = None
        
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.stop()
        return False
    
    def __del__(self):
        self.stop()
        
    def setsource(self,UDPIP, UDPPORT):
        """ Change the destination

        :param UDPIP: IP address of UDP server
        :type UDPIP: str
         """
        
        self.UDPIP = UDPIP;
        self.UDPPORT = UDPPORT;
        
    def connect(self):
        """ Enable the connection 
        
        :return: True if connection is enabled
        :rtype: bool"""
        self.enabled = True
        
    def disconnect(self):
        """ Disable the connection """
        self.enabled=False
        
    def stop(self):
        """ terminate the thread, prepare to quit  """
        self.disconnect()
        self.Quit = True
        try:
            self.socket1.close()
        except:
            pass
        self.w_thread.join()
        self.Queue1 = None
        
    def available(self):
        """Check if an item is received"""
        return not self.Queue1.empty()
    
    def putitem(self,item,address=None):
        """Put an item in the queue

        :param item: item to put
        :type item: tuple
        :param address: tuple address for the destination (ip,port)
        :type address: tuple, optional
        """
        if(not address):
            address = self.default_destination;
        
        if(not self.Queue1.full()):
            self.Queue1.put_nowait((address, item))
        
    
    def getitem(self,timeout1=1):
        """ Get a message item from the thread with timeout

        :param timeout1: timeout in seconds
        :type timeout1: int, optional
        :return: (message item, bool true if item was available)
        :rtype: tuple
         """
        good = True
        try:
            if(timeout1>0):
                item1 = self.Queue1.get(timeout=timeout1)
            else:
                item1 = self.Queue1.get_nowait()
        except queue.Empty:
            item1 = []
            good = False
        
        return item1, good

class QueuedUDPSender(UDPThreadedClient):
    """Sender for UDP messages

    :param UDPIP: IP address of UDP server
    :type UDPIP: str
    :param UDPPORT: UDP port number
    :type UDPPORT: int
    :param enable: enable the connection
    :type enable: bool, optional
    :param queuesize: size of the queue
    :type queuesize: int, optional
    :param onconnect: callback function
    :type onconnect: function, optional
    :param mcast_group: multicast group
    :type mcast_group: str, optional
    :param default_destination: default destination
    :type default_destination: tuple, optional
    :param mcast_ttl: multicast TTL
    :type mcast_ttl: int, optional
    """

    def __init__(self, UDPIP, UDPPORT=0,enable=True,queuesize = 100,
                 onconnect=None,    mcast_group=None, default_destination=None, mcast_ttl=2):
        super().__init__(UDPIP, UDPPORT,enable,queuesize)

        self.OnConnectFunction = onconnect
        self.mcast_group = mcast_group
        self.default_destination = default_destination
        self.mcast_ttl = mcast_ttl
        ###########
        self.w_thread = threading.Thread(target=self.connection_thread)
        self.w_thread.daemon = True
        self.w_thread.start()
  


    def connection_thread(self):
        """ Worker thread"""
        
        while(not self.Quit):
            self.connected = False
            if self.enabled:
                try:
                    self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                    self.socket1.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.mcast_ttl)
                    self.socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.socket1.settimeout(0.5);
                    dest_IP = socket.gethostbyname(self.UDPIP);
                    
                    if(self.Debug):      print("Resolved host: %s" % dest_IP)
                    
                    if(self.UDPPORT):
                        self.socket1.bind((self.UDPIP, self.UDPPORT))
                    else:
                        self.socket1.bind((self.UDPIP,0))
                    
                    if(self.mcast_group):
                        # Tell the operating system to add the socket to the multicast group
                        # on all interfaces.
                        group = socket.inet_aton(self.mcast_group)
                        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
                        self.socket1.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                    
                    
                    self.connected = True;
                    self.LastSource = (self.UDPIP, self.UDPPORT);
                    if(self.Debug):   print('Connected ');
                    try:
                        """ execute a callback """
                        if(self.OnConnectFunction):
                            if(self.Debug):   print('Callback executing');
                            self.OnConnectFunction(self)
                        
                        while(not self.Quit and self.enabled):
                            
                            
                            try:
                                item, good = self.getitem(.5);
                                if good:
                                    (addr,body) = item
                                    if(self.Debug):   print(item[0]);
                                    if(type(body) == str):
                                        body = bytearray(body,'utf8')
    
                                    self.socket1.sendto(body,addr)
                                    
                                    if(self.LastSource !=(self.UDPIP, self.UDPPORT)):
                                        break;
                            except(socket.timeout):
                                pass
                    except Exception as e:
                        if(self.Debug): print(e);
                        pass
                    
                    self.socket1.close()
                    if(self.Debug):      print('Closing socket')
                
                except(socket.error,socket.gaierror):
                    print('Socket error')
                    pass
                    
            else:
                time.sleep(.1)                

class QueuedUDPClient(UDPThreadedClient):
    """SIT UDP client with queue

    :param UDPIP: IP address of UDP server
    :type UDPIP: str
    :param UDPPORT: port of UDP server
    :type UDPPORT: int
    :param enable: enable the connection
    :type enable: bool
    :param queuesize: size of the queue
    :type queuesize: int
    :param onconnect: callback function when connection is enabled with the prototype: onconnect(self)
    :type onconnect: function
    :param mcast_group: multicast group
    :type mcast_group: str

    
    """

    def __init__(self, UDPIP, UDPPORT,enable=True,queuesize = 100,
                 onconnect=None,    mcast_group=None):
        super().__init__(UDPIP, UDPPORT,enable,queuesize)

        self.OnConnectFunction = onconnect
        self.mcast_group = mcast_group
        
        self.w_thread = threading.Thread(target=self.connection_thread)
        self.w_thread.daemon = True
        self.w_thread.start()
  


    def connection_thread(self):
        """ Worker thread"""
        
        while(not self.Quit):
            self.connected = False
            if self.enabled:
                try:
                    # setup the UDP socket
                    self.socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                    self.socket1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    if hasattr(self.socket1, "SO_REUSEPORT"):
                        self.setsockopt(self.socket1.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                    self.socket1.settimeout(0.5);
                    dest_IP = socket.gethostbyname(self.UDPIP);
                    if(self.Debug):      print("Resolved host: %s" % dest_IP)
                    
                    self.socket1.bind((self.UDPIP, self.UDPPORT))
                    
                    if(self.mcast_group):
                        # Tell the operating system to add the socket to the multicast group
                        # on all interfaces.
                        group = socket.inet_aton(self.mcast_group)
                        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
                        self.socket1.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                    
                    
                    self.connected = True;
                    self.LastSource = (self.UDPIP, self.UDPPORT);
                    if(self.Debug):   print('Connected ');
                    try:
                        """ execute a callback """
                        if(self.OnConnectFunction):
                            if(self.Debug):   print('Callback executing');
                            self.OnConnectFunction(self)
                        
                        while(not self.Quit and self.enabled):
                            
                            
                            try:
                                (body, src_addr) = self.socket1.recvfrom(65535);
                                if(body):
                                    self.putitem(body,src_addr);
                                if(self.LastSource !=(self.UDPIP, self.UDPPORT)):
                                    break;
                            except(socket.timeout):
                                pass
                    except:
                        pass
                    
                    self.socket1.close()
                    if(self.Debug):      print('Closing socket')
                
                except(socket.error,socket.gaierror):
                    print('Socket error')
                    pass
                    
            else:
                time.sleep(.1)