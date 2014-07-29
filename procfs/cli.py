import argparse
import json
import os
import sys
import string

from datetime import timedelta

from procfs import Proc
from procfs.core import ProcDirectory
from procfs.core import ProcessDirectory
from procfs.core import ProcessFile
from procfs.core import File

from procfs.exceptions import DoesNotExist

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, timedelta):
            return ((obj.microseconds + 
                     (obj.seconds + obj.days * 24 * 3600) * 10**6) / 10**6)
        return json.JSONEncoder.default(self, obj)

def find(path, list):
    obj = Proc()

    for (k, v) in enumerate(path.split('/')):
        if k == 0 and v.isdigit():
            obj = obj.processes(int(v))
            continue
        try:
            obj = obj.__getattr__(v)
        except (KeyError, DoesNotExist, AttributeError) as e:
            try:
                obj = obj.__getattr__(int(v))
            except (KeyError, ValueError, DoesNotExist, AttributeError) as e:
                try:
                    obj = obj.__getitem__(v)
                except (KeyError, DoesNotExist, AttributeError) as e:
                    try:
                        obj = obj.__getitem__(int(v))
                    except (KeyError, ValueError, DoesNotExist, AttributeError) as e:
                        raise DoesNotExist(path)
        if callable(obj):
            obj = obj()

    if list:
        if isinstance(obj, dict):
            return json.dumps(obj.keys(), cls=CustomEncoder)
        elif isinstance(obj, ProcDirectory) or isinstance(obj, ProcessDirectory):
            keys = []
            for key in obj.__dir__():
                keys.append(key)
            return json.dumps(keys, cls=CustomEncoder)
        else:
            raise AttributeError(path)

    if isinstance(obj, ProcDirectory) or isinstance(obj, ProcessDirectory):
        keys = []
        for key in obj.__dir__():
            keys.append(key)
        obj = keys
    return json.dumps(obj, cls=CustomEncoder)

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
