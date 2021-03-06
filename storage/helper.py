import os
import time
import requests
from uuid import uuid4
from IPython import embed
from traceback import format_exc
from .models import HandoffQueue, Bucket, File
from cloud.settings import AVAILABLE_NODES, HANDOFF_DIR


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
                print("Error %d: %s" % (r.status_code, r.text))
        except requests.exceptions.RequestException:
            print(format_exc())
            hq = HandoffQueue(node=i['name'], function='create_bucket', name=name)
            hq.save()
        except Exception:
            print(format_exc())

    return count


def replicateDelete(name):
    count = 0
    for i in AVAILABLE_NODES:
        addr = os.path.join(i['address'], 'replicate_delete/')
        data = {'name': name}
        try:
            r = requests.post(addr, data=data)
            if r.ok:
                count += 1
            else:
                print("Error %d: %s" % (r.status_code, r.text))
        except requests.exceptions.RequestException:
            print(format_exc())
            hq = HandoffQueue(node=i['name'], function='delete_bucket', name=name)
            hq.save()
        except Exception:
            print(format_exc())

    return count


def get_address(node):
    for i in AVAILABLE_NODES:
        if i['name'] == node:
            return i['address']


def hinted_handoff(node, stopper):
    time.sleep(2)
    hq = HandoffQueue.objects.filter(node=node)
    for i in hq:
        if i.function == 'create_bucket':
            addr = os.path.join(get_address(node), 'replicate/')
            data = {'name': i.name}
            r = requests.post(addr, data=data)
            if r.ok:
                i.delete()
        elif i.function == 'delete_bucket':
            addr = os.path.join(get_address(node), 'replicate_delete/')
            data = {'name': i.name}
            r = requests.post(addr, data=data)
            if r.ok:
                i.delete()
        elif i.function == 'create_file':
            addr = os.path.join(get_address(node), 'replicatefile/')
            data = {'name': i.name, 'bucket': i.bucket}
            fp = open(i.path, 'rb')
            filedata = {'file': fp}
            r = requests.post(addr, data=data, files=filedata)
            if r.ok:
                fp.close()
                os.remove(i.path)
                i.delete()
        elif i.function == 'delete_file':
            addr = os.path.join(get_address(node), 'replicatedeletefile/')
            data = {'name': i.name, 'bucket': i.bucket}
            r = requests.post(addr, data=data)
            if r.ok:
                i.delete()
        elif i.function == 'update_file':
            addr = os.path.join(get_address(node), 'replicateupdatefile/')
            data = {'name': i.name, 'bucket': i.bucket}
            fp = open(i.path, 'rb')
            filedata = {'file': fp}
            r = requests.post(addr, data=data, files=filedata)
            if r.ok:
                fp.close()
                os.remove(i.path)
                i.delete()
    stopper.set()


def replicateFile(name, bucket, file):
    count = 0
    filepath = os.path.join(HANDOFF_DIR, str(uuid4()))
    delete = True
    clocks = {}
    with open(filepath, 'wb') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    fp = open(filepath, 'rb')
    for i in AVAILABLE_NODES:
        addr = os.path.join(i['address'], 'replicatefile/')
        data = {'name': name, 'bucket': bucket}
        filedata = {'file': fp}
        try:
            r = requests.post(addr, data=data, files=filedata)
            if r.ok:
                clocks[i['name']] = r.json()['vector']
                count += 1
            else:
                print("Error %d: %s" % (r.status_code, r.text))
        except requests.exceptions.RequestException:
            print(i['name'], 'is unreachable')
            delete = False
            hq = HandoffQueue(node=i['name'], function='create_file', name=name, bucket=bucket, path=filepath)
            hq.save()
        except Exception:
            print(format_exc())
    fp.close()
    if delete:
        os.remove(filepath)
    return count, clocks


def replicateDeleteFile(name, bucket):
    count = 0
    for i in AVAILABLE_NODES:
        addr = os.path.join(i['address'], 'replicatedeletefile/')
        data = {'name': name, 'bucket': bucket}
        try:
            r = requests.post(addr, data=data)
            if r.ok:
                count += 1
            else:
                print("Error %d: %s" % (r.status_code, r.text))
        except requests.exceptions.RequestException:
            print(format_exc())
            hq = HandoffQueue(node=i['name'], function='delete_file', name=name, bucket=bucket)
            hq.save()
        except Exception:
            print(format_exc())

    return count


def replicateUpdateFile(name, bucket, file):
    count = 0
    filepath = os.path.join(HANDOFF_DIR, str(uuid4()))
    delete = True
    clocks = {}
    with open(filepath, 'wb') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    fp = open(filepath, 'rb')
    bucket_model = Bucket.objects.get(name=bucket)
    file_model = File.objects.get(name=name, bucket=bucket_model)
    data = {
        'name': name,
        'bucket': bucket,
        'vector': file_model.version,
        'timestamp': file_model.last_modified.timestamp()
    }
    filedata = {'file': fp}
    for i in AVAILABLE_NODES:
        addr = os.path.join(i['address'], 'replicateupdatefile/')
        try:
            r = requests.post(addr, data=data, files=filedata)
            if r.ok:
                clocks[i['name']] = r.json()['vector']
                count += 1
            else:
                print("Error %d: %s" % (r.status_code, r.text))
        except requests.exceptions.RequestException:
            print(i['name'], 'is unreachable')
            delete = False
            hq = HandoffQueue(node=i['name'], function='update_file', name=name, bucket=bucket, path=filepath)
            hq.save()
        except Exception:
            print(format_exc())
    fp.close()
    if delete:
        os.remove(filepath)
    return count, clocks
