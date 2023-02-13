# -*- coding: utf-8 -*-

from SITCoTmsg import CoTUtility, SITQueuedUDPClient


if __name__ == "__main__":
    import json
    from pathlib import Path

    with open(Path(__file__).parent / "../config/location1/config0.json") as settings:
        wanted_params = json.load(settings)
        with SITQueuedUDPClient('127.0.0.1',1870) as scot:
            while(1):
                if(scot.available()):
                    item, good = scot.getitem()
                    print("Received " + "="*40)
                    print(item)
                    print("Decoded " + "="*40)

                    parsed = CoTUtility.parseData(item[1], wanted_params)
                    print(parsed)