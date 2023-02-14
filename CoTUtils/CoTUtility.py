"""
@author: A.Sedunov
"""

import socket
import re
import datetime as dt
import uuid
import xml.etree.ElementTree as ET

DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"

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

types = {
    'str': str, # expected parameter is a string so cast to python str type
    'float': float, # expectedf parameter is a floating point number so cast to float type
    #####
    # COMMENTED OUT FOR NOW BECAUSE DATETIME IS NOT JSON SERIALIZABLE
    #'datetime': lambda att : dt.datetime.strptime(CoTUtility.cleantime(att), "%Y-%m-%d %H:%M:%S.%f")
    'datetime': str
}

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