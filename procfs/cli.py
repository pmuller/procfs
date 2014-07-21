import argparse
import json
import os

from procfs import Proc 
from procfs.core import ProcDirectory
from procfs.core import ProcessFile
from procfs.core import File


def run():
	parser = argparse.ArgumentParser()
	parser.add_argument('path', metavar='PATH', type=str, nargs='?', default="", help='procfs path')
	args = parser.parse_args()

	proc = Proc()

	# this is the cheap way, but shouldn't use eval
	# this also doesn't work for numeric indexes like cpuinfo/0/cpu_family
	obj = eval("proc."+args.path.replace("/", "."))
	if callable(obj):
		obj = obj()
	try:
		print json.dumps(obj)
	except TypeError, e:
		print obj.__class__
		raise e
	return
