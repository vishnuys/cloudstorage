import os
import requests
from traceback import format_exc
from cloud.settings import AVAILABLE_NODES


def replicateBucket(name):
    count = 0
    for i in AVAILABLE_NODES:
        addr = os.path.join(i['address'], 'replicate/')
        data = {'name': name}
        try:
            r = requests.post(addr, data=data)
            if r.ok:
                count += 1
        except Exception:
            print(format_exc())
