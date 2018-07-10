#!/usr/bin/python3
'''
    Power monitor main cycle
    - Runs forever
    - reads sensor(s) data from port(s)
    - sends data to emon cms
'''
from datetime import datetime as dt
import requests
from sensors.pzem import Pzem_004
EMONCMS_URL = "http://localhost/emoncms/input/post?node=main&json={{current:{A},voltage:{V},power:{W},energy:{Wh}}}"

if __name__ == "__main__":
    p = Pzem_004()
    p.open()
    data = p.read_all()
    print(dt.now(), ": %s" % data)
    url = EMONCMS_URL.format(**data)
    #print("Sending %s" % url)

    auth = {"Authorization":"Bearer 6c9ee2ec382c16d0e9502a4da215fc7d "}
    r = requests.get(url, headers=auth)
    if not r.ok:
        print(r)
