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


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', metavar='PATH', type=str, nargs='?', default="", help='procfs path')
    parser.add_argument('-l', '--list', help='list all available keys', action='store_true')
    args = parser.parse_args()

    obj = Proc()
    path = args.path
    failed = -1

    for (k, v) in enumerate(path.split('/')):
        try:
            obj = obj.__getitem__(v)
        except (DoesNotExist, AttributeError) as e:
            failed = k
            break

    if callable(obj):
        obj = obj()

    if failed != -1:
        for (k, v) in enumerate(path.split('/')):
            if k < failed:
                continue
            try:
                obj = obj.__getattr__(v)
            except (KeyError, DoesNotExist, AttributeError) as e:
                try:
                    obj = obj.__getattr__(int(v))
                except (KeyError, ValueError, DoesNotExist, AttributeError) as e:
                    sys.stderr.write('no such attribute %s\n' % v)
                    sys.exit(1)

    if args.list:
        if isinstance(obj, dict):
            print json.dumps(obj.keys())
        elif isinstance(obj, ProcDirectory):
            keys = []
            for key in obj.__dir__():
                keys.append(key)
            print json.dumps(keys)
        else:
            sys.stderr.write('requested path does not hold a dictionary!\n')
            sys.exit(1)
    else:
        if isinstance(obj, ProcDirectory):
            keys = []
            for key in obj.__dir__():
                keys.append(key)
            obj = keys
        print json.dumps(obj)
    return
