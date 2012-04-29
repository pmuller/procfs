"""Utilities"""

import sys


def get_module(name):
    """Get a module by its name.

    If it's not already loaded, it imports it.
    """
    if name not in sys.modules:
        try:
            __import__(name)
        except ImportError:
            pass
    return sys.modules.get(name)
