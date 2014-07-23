import argparse
import json
import os
import sys
import string

from procfs import Proc
from procfs.core import ProcDirectory
from procfs.core import ProcessFile
from procfs.core import File

from procfs.exceptions import DoesNotExist

def find(path, list):
    obj = Proc()
    failed = -1

    for (k, v) in enumerate(path.split('/')):
        try:
            obj = obj.__getitem__(v)
        except (KeyError, DoesNotExist, AttributeError) as e:
            failed = k
            break

    if callable(obj):
        obj = obj()

    if failed != -1:
        for (k, v) in enumerate(path.split('/')):
            if k < failed:
                continue
            try:
                obj = obj.__getitem__(v)
            except (KeyError, DoesNotExist, AttributeError) as e:
                try:
                    obj = obj.__getitem__(int(v))
                except (KeyError, ValueError, DoesNotExist, AttributeError) as e:
                    raise DoesNotExist(path)

    if list:
        if isinstance(obj, dict):
            return json.dumps(obj.keys())
        elif isinstance(obj, ProcDirectory):
            keys = []
            for key in obj.__dir__():
                keys.append(key)
            return json.dumps(keys)
        else:
            raise AttributeError(path)

    if isinstance(obj, ProcDirectory):
        keys = []
        for key in obj.__dir__():
            keys.append(key)
        obj = keys
    return json.dumps(obj)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', metavar='PATH', type=str, nargs='?', default="", help='procfs path')
    parser.add_argument('-l', '--list', help='list all available keys', action='store_true')
    args = parser.parse_args()

    try:
        print find(args.path, args.list)
    except DoesNotExist as e:
        print "couldn't find path %s" % e
        sys.exit(1)
    except AttributeError as e:
        print "%s is not a list!" % e
        sys.exit(1)
    return
