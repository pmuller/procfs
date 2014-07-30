procfs
------


.. image:: https://secure.travis-ci.org/pmuller/procfs.png?branch=master
    :target: http://travis-ci.org/pmuller/procfs
    :alt: Build status

.. image:: https://pypip.in/download/procfs/badge.png
    :target: https://pypi.python.org/pypi//procfs/
    :alt: Downloads

.. image:: https://pypip.in/version/procfs/badge.png
    :target: https://pypi.python.org/pypi/procfs/
    :alt: Latest Version

.. image:: https://pypip.in/license/procfs/badge.png
    :target: https://pypi.python.org/pypi/procfs/
    :alt: License



Easy to use
```````````

::

    >>> from procfs import Proc
    >>> proc = Proc()

    >>> proc.loadavg
    {'average': {1: 0.0, 5: 0.0, 15: 0.0},
     'entities': {'current': 1, 'total': 117},
     'last_pid': 3068}

    >>> proc.net.dev.eth1.receive.bytes
    117997558

    >>> proc.meminfo.MemFree
    57044

    >>> proc.net.snmp.Udp
    {'InDatagrams': 3394, 'OutDatagrams': 3399, 'RcvbufErrors': 0,
     'InErrors': 0, 'SndbufErrors': 0, 'NoPorts': 4}


Process information
```````````````````

::

    >>> proc.self
    <Process 3068: python>

    >>> proc.self.parent
    <Process 17423: bash>

    >>> proc.self.uptime
    datetime.timedelta(0, 346, 380262)

    >>> proc.processes
    <Processes: [<Process 1: init>, <Process 2: kthreadd>, <Process 3: migration/0>, <Process 4: ksoftirqd/0>, <Process 5: watchdog/0>, <Process 6: migration/1>, <Process 7: ksoftirqd/1>, <Process 8: watchdog/1>, <Process 9: events/0>, <Process 10: events/1>, ...]>
    >>> len(proc.processes)
    110

    >>> proc.processes.cmdline('(vim|ssh)')
    <Processes: [<Process 2956: vim>, <Process 3044: vim>, <Process 3136: vim>, <Process 10422: sshd>, <Process 10440: sshd>, <Process 10504: sshd>]>

    >>> proc.processes.uid(1000) 
    <Processes: [<Process 1120: bash>, <Process 2593: bash>, <Process 2956: vim>, <Process 3044: vim>, <Process 3093: python>, <Process 10504: sshd>, <Process 10505: bash>, <Process 10875: screen>, <Process 10876: screen>, <Process 12908: bash>, ...]>

    >>> proc.processes.user('pmuller').cmdline('python')[0]
    <Process 3093: python>


Links
`````

* `documentation <http://packages.python.org/procfs/>`_
* `github <http://github.com/pmuller/procfs>`_


.. image:: https://d2weczhvl823v0.cloudfront.net/pmuller/procfs/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

