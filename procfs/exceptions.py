"""procfs exceptions"""


class BaseException(Exception):
    """Base exception"""


class DoesNotExist(BaseException):
    """The path does not exist"""


class NotDirectory(BaseException):
    """The path is not a directory"""


class NotFile(BaseException):
    """The path is not a file"""


class ProcessException(BaseException):
    """Exceptions raised by process handling code"""


class UnknownProcess(ProcessException):
    """The process does not exist"""


class NoParentProcess(ProcessException):
    """The process has no parent process"""
