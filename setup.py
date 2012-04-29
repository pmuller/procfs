#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = [l for l in open('procfs/__init__.py')
           if l.startswith('__version__ =')][0].split("'")[1]
LONG_DESCRIPTION = open('README.rst').read()

setup(
    name='procfs',
    version=VERSION,
    packages=find_packages(),
    author='Philippe Muller',
    description='Pythonic API for Linux /proc',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    keywords='linux proc procfs system kernel',
    url='http://packages.python.org/procfs/',
    platforms=['Linux'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Operating System Kernels :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
