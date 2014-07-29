"""procfs exceptions"""

class PathNotFoundError(Exception):
    """The path does not exist"""


class PathNotADirectoryError(Exception):
    """The path is not a directory"""


class PathNotAFileError(Exception):
    """The path is not a file"""


class ProcessException(Exception):
    """Exceptions raised by process handling code"""


class UnknownProcessError(ProcessException):
    """The process does not exist"""


class NoParentProcessError(ProcessException):
    """The process has no parent process"""
