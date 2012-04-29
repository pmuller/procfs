"""/proc/<pid> handlers"""

import re
from datetime import timedelta

from procfs.core import ProcessFile, Dict


class io(ProcessFile):
    """/proc/<pid>/io
    """

    def _parse(self, data):
        result = Dict()
        for line in data.splitlines():
            if ': ' in line:
                key, value = line.split(': ', 1)
                result[key] = int(value)
        return result


class mounts(ProcessFile):
    """/proc/mounts
    """

    __keys = ('device', 'mount_point', 'type', 'options',  'dump', 'passno')

    def _parse(self, content):
        lines = content.splitlines()
        result = {}
        for line in lines:
            values = line.split()
            data = Dict(zip(self.__keys, values))
            data['passno'] = int(data['passno'])
            data['dump'] = int(data['dump'])
            options = data['options'].split(',')
            data['options'] = Dict()
            for option in options:
                option = option.split('=', 1)
                data['options'][option[0]] = True if len(option) == 1 \
                                                  else option[1]
            mount_point = data.pop('mount_point')
            result[mount_point] = data
        return result


class cmdline(ProcessFile):
    """/proc/<pid>/cmdline
    """

    def _parse(self, data):
        return filter(bool, data.split('\x00'))


class environ(ProcessFile):
    """/proc/<pid>/environ
    """

    def _parse(self, data):
        lines = filter(bool, data.split('\x00'))
        env = {}
        for line in lines:
            name, _, value = line.partition('=')
            env[name] = value
        return Dict(env)


class status(ProcessFile):
    """/proc/<pid>/status
    """

    def _parse(self, content):
        data = Dict()
        for line in content.splitlines():
            name, value = line.split(':\t')
            value = value.strip()
            if name.startswith('Vm'):
                value = int(value.split(' kB')[0])
            elif name in ('Uid', 'Gid'):
                keys = ('real', 'effective', 'saved_set', 'fs')
                values = map(int, value.split())
                value = Dict(zip(keys, values))
            elif name == 'SigQ':
                queued, max_ = value.split('/', 1)
                value = Dict(queued=int(queued), max=int(max_))
            elif name == 'Groups':
                groups = value.split()
                value = map(int, groups)
            elif name in ('Tgid', 'PPid', 'TracerPid', 'FDSize', 'Threads',
                          'Pid', 'nonvoluntary_ctxt_switches',
                          'voluntary_ctxt_switches'):
                value = int(value)
            data[name] = value
        return data


class stat(ProcessFile):
    """/proc/<pid>/stat
    """

    def _parse(self, data):
        header = """pid tcomm state ppid pgrp sid tty_nr tty_pgrp
        flags min_flt cmin_flt maj_flt cmaj_flt utime stime cutime 
        cstime priority nice num_threads _ start_time vsize rss
        rsslim start_code end_code start_stack esp eip pending 
        blocked sigign sigcatch wchan _ _ exit_signal task_cpu
        rt_priority policy blkio_ticks gtime cgtime"""
        header = header.split()
        data = Dict(zip(header, data.split()))
        del data['_']
        for key, value in data.items():
            if key.endswith('time'):
                data[key] = timedelta(seconds=int(value))
            elif key not in ('state', 'tcomm'):
                data[key] = int(value)
        return data


class statm(ProcessFile):
    """/proc/<pid>/statm
    """

    def _parse(self, data):
        header = "size resident shared trs _ drs _".split()
        data = Dict(zip(header, data.split()))
        del data['_']
        for key, value in data.items():
            data[key] = int(value)
        return data


class smaps(ProcessFile):
    """/proc/<pid>/smaps
    """

    __re_section = re.compile(r'^(?P<start>[0-9a-f]+)\-(?P<end>[0-9a-f]+) '
                              r'(?P<perms>[r\-][w\-][x\-][sp]) '
                              r'(?P<offset>[0-9a-f]{8}) '
                              r'(?P<device>[0-9a-f]{2}:[0-9a-f]{2}) '
                              r'(?P<inode>\d+)\s+(?P<pathname>.*)')

    def _parse(self, data):
        result = Dict()
        capture_values = False
        for line in data.splitlines():
            #print 'line', line
            match = self.__re_section.match(line)
            #print 'match', match.groupdict() if match else None
            if match:
                data = match.groupdict()
                pathname = data.pop('pathname')
                if pathname:
                    if pathname[1:-1] in ('heap', 'stack', 'vdso', 'vsyscall'):
                        pathname = pathname[1:-1]
                        #print 'pathname: "%s"' % pathname, 'start'
                        for key in ('start', 'end', 'offset'):
                            data[key] = int(data[key], 16)
                        dev_major, dev_minor = data['device'].split(':', 1)
                        data['device'] = Dict(major=int(dev_major, 16),
                                              minor=int(dev_minor, 16))
                        result[pathname] = Dict(data)
                        capture_values = True
                    else:
                        #print 'pathname: "%s"' % pathname, 'stop'
                        capture_values = False
                else:
                    capture_values = False
            elif capture_values:
                key, value = line.split(':', 1)
                #print 'capture', pathname, key, value
                value = int(value.split(' kB', 1)[0].strip())
                #print 'capture', pathname, key, value
                result[pathname][key] = value
        return result
