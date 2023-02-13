# -*- coding: utf-8 -*-
"""
"""

from SITCoTmsg import SITQueuedUDPSender,SITQueuedUDPClient,CoTUtility
import time

############################### Testing				
if __name__ == "__main__":
    import random
    import json
    from pathlib import Path
    print("Debuging module")

    with open(Path(__file__).parent / "../config/location1/config0.json") as settings:
        wanted_params = json.load(settings)
        with SITQueuedUDPSender('localhost',default_destination=("localhost",15005)) as out:
            out.Debug= False
            with SITQueuedUDPClient('',15005) as scot:
                scot.Debug = True;
                while(1):
                    time.sleep(.1)
                    
                    cot_data = {"uid":"test.1", "lat": 41, "lon":-74,"detail": { "track": { "course":0,"speed":0 } } }
                    cot_xml = CoTUtility.toCoT(cot_data)
                    
                    
                    if(random.randint(1,4)==1):
                        out.putitem(cot_xml)
                        
                    
                    if(scot.available()):
                        item, good = scot.getitem()
                        print("Received " + "="*40)
                        print(item)
                        print("Decoded " + "="*40)
                        cot_xml = item[1]
                        print(CoTUtility.parseData(item[1], wanted_params))
