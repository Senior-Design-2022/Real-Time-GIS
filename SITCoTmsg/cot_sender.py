# -*- coding: utf-8 -*-
"""
"""

from SITCoTmsg import SITQueuedUDPSender,SITQueuedUDPClient,CoTUtility
import time

############################### Testing				
if __name__ == "__main__":
    import random
    print("Debuging module")
    
    this_lat = 42
    this_lon = -74.1
    this_speed_lat = 1/111111
    
    with SITQueuedUDPSender('127.0.0.1',default_destination=("127.0.0.1",1870)) as out:
        out.Debug= False
        while(1):
            time.sleep(.5)
            
            this_lat = this_lat + this_speed_lat
            
            cot_data = {"uid":"test.2", "lat": this_lat, "lon":this_lon,"detail": { "track": { "course":0,"speed":0 } } }
            cot_xml = CoTUtility.toCoT(cot_data)
            
            

            out.putitem(cot_xml)
            print(cot_xml)
                
            
