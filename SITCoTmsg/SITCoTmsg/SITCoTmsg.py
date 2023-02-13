# -*- coding: utf-8 -*-
"""
Utility for sending/receiving the UDP messages in Python
as well as formatting and parsing CoT


@author: A.Sedunov
"""
import struct
import queue
import time
import socket
import threading
import re




import datetime as dt
import uuid
import xml.etree.ElementTree as ET



ID = {
    "pending": "p",
    "unknown": "u",
    "assumed-friend": "a",
    "friend": "f",
    "neutral": "n",
    "suspect": "s",
    "hostile": "h",
    "joker": "j",
    "faker": "f",
    "none": "o",
    "other": "x"
}
DIM = {
    "space": "P",
    "air": "A",
    "land-unit": "G",
    "land-equipment": "G",
    "land-installation": "G",
    "sea-surface": "S",
    "sea-subsurface": "U",
    "subsurface": "U",
    "other": "X"
}

unit_defaults = {
        "identity": "none",
        "dimension": "air",
        "type": "C",
        "lat": 0,
        "lon": 0,
        "hae": 0,
        "ce": 10,
        "le": 10
        }

# expected types and their mapping to python types
types = {
    'str': str, # expected parameter is a string so cast to python str type
    'float': float, # expectedf parameter is a floating point number so cast to float type
    #####
    # COMMENTED OUT FOR NOW BECAUSE DATETIME IS NOT JSON SERIALIZABLE
    #'datetime': lambda att : dt.datetime.strptime(CoTUtility.cleantime(att), "%Y-%m-%d %H:%M:%S.%f")
    'datetime': str
}

DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"

class CoTUtility:
    """Utility class with methods for CoT message formatting and parsing

    """
    @staticmethod
    def toCoT(unit):
        """convert unit to CoT message

        :param unit: unit with all fields to convert
        :type unit: dict
        :return: cot message
        :rtype: str
        """
        if("time" in unit.keys()):
            now = unit["time"]
        else:    
            now = dt.datetime.utcnow()
        zulu = now.strftime(DATETIME_FMT)

        stale_now = now + dt.timedelta(minutes=1)
        stale = stale_now.strftime(DATETIME_FMT)
        
        # ensure all the defaults are set
        for k in unit_defaults.keys():
            unit.setdefault(k,unit_defaults[k])

        unit_id = ID[unit["identity"]]
    
        cot_type = "a-" + unit_id + "-" + DIM[unit["dimension"]]

        if "type" in unit:
          cot_type = cot_type + "-" + unit["type"]

        if "uid" in unit:
          cot_id = unit["uid"]
        else:
            # create a random unique ID
          cot_id = str(uuid.uuid4())

        evt_attr = {
            "version": "2.0",
            "uid": cot_id,
            "time": zulu,
            "start": zulu,
            "stale": stale,
            "type": cot_type
        }
        

        pt_attr = {
            "lat": str(unit["lat"]),
            "lon":  str(unit["lon"]),
            "hae": str(unit["hae"]),
            "ce": str(unit["ce"]),
            "le": str(unit["le"])
        }
    
        cot = ET.Element('event', attrib=evt_attr)
        detail1 = ET.SubElement(cot, 'detail')
        
        if('detail' in unit):
            detelements = unit["detail"]
            for k in detelements.keys():
                e = detelements[k]
                es = {kk: str(v) for kk, v in e.items()}
                ET.SubElement(detail1, k, attrib=es)
                
                
                
            
        
        ET.SubElement(cot,'point', attrib=pt_attr)
    
        cot_xml = (
                (ET.tostring(cot, encoding='utf8', method='xml')).decode('utf8')
                )
        return cot_xml
    
    @staticmethod
    def cleantime(timeanyformat):
        """clean time string

        :param timeanyformat: time string with any separators
        :type timeanyformat: str"""
        dtsrc = [float(t) for t in re.split('[\-:ZT]',timeanyformat.strip())[:6]]
        dtclean = '%04d-%02d-%02d %02d:%02d:%.3f' % tuple(dtsrc)
        return dtclean
        
    @staticmethod
    def parseCoT(cot_xml):
        """parse CoT message

        :param cot_xml: CoT message
        :type cot_xml: str
        :return: parsed CoT message
        :rtype: dict
        """
        unit = {}
        parsed = ET.fromstring(cot_xml)
        pointdata = parsed.find("point")
        if(parsed.attrib):
            for k in parsed.attrib.keys():
                if(k in ['time','start','stale']):
                    dtclean = CoTUtility.cleantime(parsed.attrib[k])
                    unit[k] = dt.datetime.strptime(
                            dtclean, "%Y-%m-%d %H:%M:%S.%f")
                else:
                    unit[k] = parsed.attrib[k]
        if(pointdata.attrib):
            for k in pointdata.attrib.keys():
                unit[k] = float(pointdata.attrib[k])
        if("type" in unit.keys()):
            tt = unit["type"]
            idatom = tt[2]
            if(len(tt)>=4):
                dimatom = tt[2+2];
                if(dimatom in DIM.values()):
                    unit["dimension"] = list(DIM.keys()) [list(DIM.values()).index(dimatom)]
            if(idatom in ID.values()):
                unit["identity"] = list(ID.keys()) [list(ID.values()).index(idatom)]
                
        detail_data = parsed.find("detail")
        detail_ch = list(detail_data) #.getchildren()
        if(detail_ch):
            unit['detail'] = {}
            for c in detail_ch:
                unit['detail'][c.tag] = c.attrib
                # convert all numeric fields to float
                for a in unit['detail'][c.tag].keys():
                    if(unit['detail'][c.tag][a].replace('.','',1).isdigit()):
                        unit['detail'][c.tag][a] = float(unit['detail'][c.tag][a])
       
        return unit
    
    @staticmethod
    def parseData(raw_data, wanted_params):
        """
            Parses incoming xml data from the socket into the desired fields in json format.

            :param raw_data: the raw input xml
            :type raw_data: str
            :param wanted_params: mapping of parameter names and their types
            :type wanted_params: dict
            :return: parsed data
            rtype: dict
        """
        # parse the incoming xml data 
        parsed = ET.fromstring(raw_data)

        # This is a recurisive helper function which recreates the desired structure from wanted_params
        # with the data from the incoming xml cast to proper types
        def createStructure(wanted_dict):
            result = {} # accumulating result dictionary
            for param, val in wanted_dict.items(): # loop through wanted parameters
                if isinstance(val, dict): # if we encounter a nested parameter we want to unpack the nested data
                    result[param] = createStructure(val) # maintain the wanted structure while unpacking the nested xml data
                else: # if there is nothing to unpack we can find the data in the xml and convert it to its proper type
                    xpath = wanted_params['xpaths'][param] # get the associated xpath for the parameter
                    elem = parsed.find(xpath) # find the data in the parsed xml

                    # if the data is found from the xpath we can add it to our formatted dictionary cast to its proper type
                    if elem is not None:
                        result[param] = types[val](elem.attrib.get(param))
                    else:
                        result[param] = None
            return result

        return createStructure(wanted_params['output'])




    
    @staticmethod
    def pushUDP(ip_address, port, cot_xml):
        """push CoT message to UDP server
        
        :param ip_address: IP address of UDP server
        :type ip_address: str
        :param port: port of UDP server
        :type port: int
        :param cot_xml: CoT message
        :type cot_xml: str
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sent = sock.sendto(cot_xml, (ip_address, port))
        return sent










class SITUDPThreadedClient:
    
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
    
###############################################################################
class SITQueuedUDPClient(SITUDPThreadedClient):
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
                
                
###############################################################################
class SITQueuedUDPSender(SITUDPThreadedClient):
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
                





############################### Testing				
if __name__ == "__main__":
    if True:
        cot_xml = CoTUtility.toCoT({"uid":"test.1", "detail": { "track": { "course":0,"speed":0 } } })
        print(cot_xml,'\n\n')
        from_cot = CoTUtility.parseCoT(cot_xml)
        print(from_cot)
    if False:
        import random
        print("Debuging module")
        with SITQueuedUDPSender('localhost',default_destination=("localhost",15005)) as out:
            out.Debug= False
            with SITQueuedUDPClient('',15005) as scot:
                scot.Debug = True;
                while(1):
                    time.sleep(.1)
                    if(random.randint(1,4)==1):
                        out.putitem("test "+ str(random.randint(0,100)))
                        
                    
                    if(scot.available()):
                        item, good = scot.getitem()
                        print(item)
    if False:
        with SITQueuedUDPClient('',15005) as scot:
            scot.Debug = True
            print(scot)
            while(1):
                item, good = scot.getitem()
                if good:
                    cot_xml = item[1]
                    from_cot = CoTUtility.parseCoT(cot_xml)
                    print(from_cot)
