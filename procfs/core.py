"""\
Base classes to handle an easy /proc navigation.
"""
import os
import re
import pwd
from datetime import datetime
from pprint import pformat

from procfs.exceptions import \
    PathNotFoundError, UnknownProcessError, NoParentProcessError, PathNotADirectoryError, PathNotAFileError
from procfs.utils import get_module


DIGIT = re.compile('^\d+$')


class Dict(dict):
    """A dict with access to its items like if they are attributes.
    """

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class BaseFile(object):

    def __init__(self, filepath):
        if not isinstance(filepath, basestring):
            raise PathNotAFileError(filepath)
        elif not os.path.exists(filepath):
            raise PathNotFoundError(filepath)
        elif not os.path.isfile(filepath):
            raise PathNotAFileError(filepath)
        self._filepath = filepath
        self._file = None

    def _read(self, parse=True):
        """Read and parse file content."""
        if self._file is None:
            self._file = open(self._filepath)
        data = self._file.read()
        self._file.seek(0)
        if parse:
            return self._parse(data)
        else:
            return data

    def __getattr__(self, attr):
        """Provide access to file content."""
        if isinstance(attr, int) or \
           (isinstance(attr, basestring) and not attr.startswith('_')):
            data = self._read()
            if isinstance(data, dict) and attr in data:
                return data[attr]
            if hasattr(data, attr):
                return getattr(data, attr)
            raise AttributeError(attr)
        raise AttributeError(attr)
    __getitem__ = __getattr__

    def _parse(self, data):
        """Override me!"""
        return data

    def __call__(self, parse=True):
        return self._read(parse)

    def __str__(self):
        return pformat(self._read())

    def __repr__(self):
        return str(self)


class File(BaseFile):
    """A /proc virtual file
    """

    def __init__(self, filepath=None):
        if not filepath:
            name = self.__module__[len('procfs.proc.'):]
            filepath = '/proc/%s' % os.path.join(name.replace('.', '/'),
                                                 self.__class__.__name__)
        super(File, self).__init__(filepath)


class ProcessFile(BaseFile):
    """A /proc/<pid> file
    """

    def __init__(self, id, filepath=None):
        if not filepath:
            name = self.__module__[len('procfs.processes.'):]
            filepath = os.path.join(name.replace('.', '/'),
                                    self.__class__.__name__)
        filepath = '/proc/%s/%s' % (id, filepath)
        super(ProcessFile, self).__init__(filepath)


class BaseDirectory(object):
    """Base directory class"""

    # Where to look for file handlers
    _base_module = None
    # How much parts of the directory path to skip when looking for file
    # handlers
    _skip_path_parts = None

    def __init__(self, path):
        if not os.path.exists(path):
            raise PathNotFoundError(path)
        elif not os.path.isdir(path):
            raise PathNotADirectoryError(path)
        self._dir = path

    def __getattr__(self, attr):
        path = os.path.join(self._dir, str(attr))
        if not os.path.exists(path):
            raise PathNotFoundError(path)
        elif os.path.islink(path):
            return self._handle_link(path)
        elif os.path.isdir(path):
            return self._handle_directory(path)
        else:
            return self._handle_file(path)
    __getitem__ = __getattr__

    def _handle_directory(self, path):
        raise NotImplementedError

    def _handle_file(self, path):
        """Try to find a handler or return the raw file"""
        dirname, handler_name = os.path.split(path)

        # Skip /proc/<pid> from the directory path to find sub module name
        dirname_parts = dirname.split('/')
        sub_module_name = '.'.join(dirname_parts[self._skip_path_parts:])

        if sub_module_name:
            module_name = '%s.%s' % (self._base_module, sub_module_name)
        else:
            module_name = self._base_module
        module = get_module(module_name)

        # Use filename as handler name
        if module and hasattr(module, handler_name):
            handler = getattr(module, handler_name)
            return self._call_file_handler(handler)
        else:
            # If no handler is found,
            # returns a ProcessFile object
            return self._handle_raw_file(path)

    def _handle_link(self, path):
        raise NotImplementedError

    def _handle_raw_file(self, path):
        return open(path).read()

    def _call_file_handler(self, handler):
        return handler()

    def __dir__(self):
        return os.listdir(self._dir)


class ProcDirectory(BaseDirectory):
    """/proc and its sub-directories
    """

    _base_module = 'procfs.proc'
    _skip_path_parts = 2

    def _handle_link(self, path):
        target = os.readlink(path)
        obj = self
        for attr in target.split('/'):
            obj = getattr(obj, attr)
        return obj

    def _handle_directory(self, path):
        return ProcDirectory(path)

    def _handle_raw_file(self, path):
        return File(path)

    def __repr__(self):
        return '<ProcDirectory: %s>' % self._dir


class Proc(ProcDirectory):
    """/proc"""

    def __init__(self):
        super(Proc, self).__init__('/proc')

    def _handle_link(self, path):
        if path == '/proc/self':
            pid = os.readlink(path)
            return Process(pid)
        else:
            return super(Proc, self)._handle_link(path)

    @property
    def processes(self):
        """List running processes' IDs
        """
        return Processes()

    def __repr__(self):
        return '<Proc>'


class Processes(object):
    """Process interface"""

    def __init__(self):
        self.__processes = None

    def __call__(self, id):
        return Process(id)

    def __getitem__(self, item):
        return self.all[item]

    def __len__(self):
        return len(self.all)

    @property
    def all(self):
        if self.__processes is None:
            return [Process(pid) for pid in os.listdir('/proc')
                    if DIGIT.match(pid)]
        else:
            return self.__processes

    def uid(self, uid=None):
        """Filter processes by uid"""
        if uid is None:
            uid = os.getuid()
        processes = []
        for process in self.all:
            status_uid = process.status.Uid
            if uid in (status_uid.real, status_uid.effective):
                processes.append(process)
        self.__processes = processes
        return self

    def user(self, name=None):
        """Filter processes by username"""
        if name:
            uid = pwd.getpwnam(name).pw_uid
        else:
            uid = None
        return self.uid(uid)

    def cmdline(self, pattern):
        """Filter processes by applyinf a regexp ``pattern`` to
           /proc/<pid>/cmdline
        """
        if isinstance(pattern, basestring):
            pattern = re.compile(pattern)
        processes = []
        for process in self.all:
            cmdline = ' '.join(process.cmdline())
            if pattern.search(cmdline):
                processes.append(process)
        self.__processes = processes
        return self

    def __repr__(self):
        count = len(self)
        processes = str(self.all[:10])
        if count > 10:
            processes = processes[:-1] + ', ...]'
        return '<Processes: %s>' % processes


class ProcessDirectory(BaseDirectory):
    """/proc/<pid>/<path>
    """

    _base_module = 'procfs.processes'
    _skip_path_parts = 3

    def __init__(self, id, path):
        self._id = int(id)
        super(ProcessDirectory, self).__init__(path)

    def _handle_directory(self, path):
        return ProcessDirectory(self._id, path)

    def _handle_raw_file(self, path):
        path = os.path.join(*path.split('/')[3:])
        return ProcessFile(self._id, path)

    def _call_file_handler(self, handler):
        return handler(self._id)

    def __repr__(self):
        return '<ProcessDirectory: %s>' % self._dir


class Process(ProcessDirectory):
    """Process information from /proc/<pid>
    """

    def __init__(self, id):
        path = '/proc/%s' % id
        if not os.path.isdir(path):
            raise UnknownProcessError(id)
        super(Process, self).__init__(id, path)

    def __repr__(self):
        return '<Process %s: %s>' % (self._id, self.status.Name)

    @property
    def id(self):
        return self._id

    @property
    def parent(self):
        """The process' parent
        """
        ppid = self.stat.ppid
        if ppid == 0:
            raise NoParentProcessError(id)
        return Process(ppid)

    @property
    def started_at(self):
        """The time at which the process was started
        """
        stat = os.stat(self._dir)
        return datetime.fromtimestamp(stat.st_atime)

    @property
    def uptime(self):
        return datetime.now() - self.started_at

    def _handle_link(self, path):
        return os.readlink(path)
