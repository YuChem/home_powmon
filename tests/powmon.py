'''
    Power monitor main cycle
    - Runs forever
    - reads sensor(s) data from port(s)
    - sends data to emon cms
'''
from sensors.pzem import Pzem_004
EMONCMS_URL = ""

if __name__ == "__main__":
    p = Pzem_004()
    data = p.read_all()

    url = EMONCMS_URL.format(data)
    httplib2.get(url)