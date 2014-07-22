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
	args = parser.parse_args()

	if len(args.path) == 0:
		sys.stderr.write('no arguments specified - run with -h for help.\n')
		return

	obj = Proc()
	path = args.path
	failed = -1
	
	for (k, v) in enumerate(path.split('/')):
		try:
			obj = obj.__getitem__(v)
		except DoesNotExist:
			failed = k
			break
		except AttributeError:
			failed = k
			break
	
	obj = obj()
	
	if failed != -1:
		for (k, v) in enumerate(path.split('/')):
			if k < failed:
				continue
			try:
				obj = obj.__getattr__(v)
			except KeyError:
				try:
					obj = obj.__getattr__(int(v))
				except ValueError:
					sys.stderr.write('failed to get specific path; getting parent(s)\n')
					break
				except AttributeError:
					sys.stderr.write('failed to get specific path; getting parent(s)\n')
					break
			except AttributeError:
				sys.stderr.write('failed to get specific path; getting parent(s)\n')
				break
	
	print obj
	return
