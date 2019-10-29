import os
import requests
from traceback import format_exc
from cloud.settings import AVAILABLE_NODES
from .models import HandoffQueue


def replicateBucket(name):
    count = 0
    for i in AVAILABLE_NODES:
        addr = os.path.join(i['address'], 'replicate/')
        data = {'name': name}
        try:
            r = requests.post(addr, data=data)
            if r.ok:
                count += 1
            else:
                hq = HandoffQueue(node=i['name'], function='create_bucket', name=name)
                hq.save()
        except Exception:
            print(format_exc())
            hq = HandoffQueue(node=i['name'], function='create_bucket', name=name)
            hq.save()

    return count


def get_address(node):
    for i in AVAILABLE_NODES:
        if i['name'] == node:
            return i['address']
