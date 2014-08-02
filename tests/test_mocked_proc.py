
"""
procfs integration tests
~~~~~~~~~~~~~~~~~~~~~~~~

A set of simple tests that are executed against the real /proc directory
"""

from os import readlink, listdir
from os.path import exists, isdir, isfile
import os
import pytest

import procfs
from procfs.exceptions import PathNotFoundError, NoParentProcessError


SkipTest = pytest.mark.skipif(True, reason='skipped')


# fixtures


@pytest.fixture(autouse=True)
def mock_os(monkeypatch):
    for x in ('environ', 'getcwdu', 'getegid', 'getenv',
              'geteuid', 'getgroups', 'getloadavg', 'getlogin',
              'getpgid', 'getpgrp', 'getpid', 'getppid', 'getresgid',
              'getresuid', 'getsid', 'getuid'):

        # monkeypatch.setattr(procfs.core.os, x, )
        monkeypatch.delattr(procfs.core.os, x)


@pytest.fixture(autouse=True)
def mock_getpid(monkeypatch):
    monkeypatch.setattr(procfs.core.os, 'getpid', '_mockpid_')


@pytest.fixture(autouse=True)
def mock_listdir(monkeypatch):

    def mock_listdir(d):
        if d.startswith('/proc'):
            d = os.path.join('data', d[1:])
            return listdir(d)

        if d.startswith('data'):
            return listdir(d)

        raise RuntimeError(d)

    monkeypatch.setattr(procfs.core.os, 'listdir', mock_listdir)


@pytest.fixture(autouse=True)
def mock_readlink(monkeypatch):

    def mock_readlink(path):

        if path == '/proc/self':
            return 1

        if path.startswith('/proc'):
            path = os.path.join('data', path[1:])

        # assert path.startswith('data')
        print 'READLINK', path
        return readlink(path)

    monkeypatch.setattr(procfs.core.os, 'readlink', mock_readlink)


@pytest.fixture(autouse=True)
def mock_isdir(monkeypatch):

    def mock_isdir(path):
        if path.startswith('/proc'):
            path = os.path.join('data', path[1:])

        return isdir(path)

    monkeypatch.setattr(procfs.core.os.path, 'isdir', mock_isdir)


@pytest.fixture(autouse=True)
def mock_isfile(monkeypatch):

    def mock_isfile(path):
        if path.startswith('/proc'):
            path = os.path.join('data', path[1:])

        # print 'isfile', path
        return isfile(path)

    monkeypatch.setattr(procfs.core.os.path, 'isfile', mock_isfile)


@pytest.fixture(autouse=True)
def mock_exists(monkeypatch):

    def mock_exists(path):
        if path.startswith('/proc'):
            path = os.path.join('data', path[1:])

        assert path.startswith('data')
        # print 'exists', path
        return exists(path)

    monkeypatch.setattr(procfs.core.os.path, 'exists', mock_exists)


@pytest.fixture(autouse=True)
def mock_readfile(monkeypatch, request):
    """Record/replay reads to/from file"""

    def __record(fn):
        data = open(fn).read()

        q = os.path.join('data', fn.lstrip('/'))
        d = os.path.dirname(q)
        try:
            os.makedirs(d)
        except OSError:
            pass

        with open(q, 'w') as out:
            out.write(data)

        return data

    def replay(fn):
        fn = fn.lstrip('/')
        fn = os.path.join('data', fn)
        print "USING", fn
        return open(fn).read()

    monkeypatch.setattr(procfs.core, 'readfile', replay)


@pytest.fixture
def proc():
    return procfs.Proc()


@pytest.fixture
def proc():
    return procfs.Proc()


@pytest.fixture
def first(proc):
    """Return the first process"""
    return procfs.Proc().processes[0]


# tests

@SkipTest
def test_processes_0(first):
    assert first.id == 1, repr(first.id)
    with pytest.raises(NoParentProcessError):
        first.parent


def test_missing_file(first):
    with pytest.raises(PathNotFoundError):
        first.not_a_real_file


def test_first_process_id(first):
    assert first.id


def test_first_process_net_dev(first):
    assert first.net.dev['lo']['transmit']['bytes'] >= 0


def test_first_process_route(first):
    assert len(first.net.route.keys())


def test_first_process_net_netstat(first):
    assert first.net.netstat['IpExt']['OutOctets'] >= 0


def test_first_process_snmp(first):
    assert first.net.snmp['Tcp']['CurrEstab'] >= 0


def test_first_process_net_tcp(first):
    assert first.net.tcp.keys()


def test_first_process_net_udp(first):
    assert first.net.udp.keys()


def test_first_process_net_sockstat(first):
    assert first.net.sockstat['TCP']['alloc'] >= 0


def test_first_process_net_dev_mcast(first):
    assert len(first.net.dev_mcast.keys()) >= 0


@SkipTest
def test_first_process_environ(first):
    assert first.environ['USER']


def test_first_process_statm(first):
    assert first.statm['size']


@pytest.mark.xfail(reason="Probably a bug")
def test_first_process_smaps(first):
    assert first.smaps.keys()


# tests on proc.self


def test_proc_self_id(proc):
    assert proc.self.id


def test_proc_self_net_dev(proc):
    assert proc.self.net.dev['lo']['transmit']['bytes'] >= 0


def test_proc_self_route(proc):
    assert len(proc.self.net.route.keys())


def test_proc_self_net_netstat(proc):
    assert proc.self.net.netstat['IpExt']['OutOctets'] >= 0


def test_proc_self_snmp(proc):
    assert proc.self.net.snmp['Tcp']['CurrEstab'] >= 0


def test_proc_self_net_tcp(proc):
    assert proc.self.net.tcp.keys()


def test_proc_self_net_udp(proc):
    assert proc.self.net.udp.keys()


def test_proc_self_net_sockstat(proc):
    assert proc.self.net.sockstat['TCP']['alloc'] >= 0


def test_proc_self_net_dev_mcast(proc):
    assert len(proc.self.net.dev_mcast.keys()) >= 0


def test_proc_self_environ(proc):
    assert proc.self.environ['USER']


def test_proc_self_statm(proc):
    assert proc.self.statm['size']


@pytest.mark.xfail(reason="Probably a bug")
def test_proc_self_smaps(proc):
    assert proc.self.smaps.keys()


@SkipTest
def test_proc_self_parent(proc):
    assert proc.self.parent


def test_processes_cmdline(proc):
    matches = proc.processes.cmdline('systemd')
    assert len(matches) == 1


def test_processes_uid_0(proc):
    uid0p = proc.processes.uid(0)
    assert len(uid0p) == 55


def test_processes_user_root(proc):
    rootp = proc.processes.user('root')
    assert len(rootp) == 55


@SkipTest
def test_mounts(proc):
    m = proc.mounts
    assert m.keys()


def test_cpuinfo(proc):
    c = proc.cpuinfo
    assert len(c.keys())
    assert 'cpu_family' in c[0]


def test_uptime(proc):
    assert 'uptime' in proc.uptime.keys()


def test_stat(proc):
    assert 'processes' in proc.stat.keys()
    assert 'cpu' in proc.stat.keys()


def test_loadavg(proc):
    assert 'average' in proc.loadavg.keys()


def test_partitions(proc):
    assert len(proc.partitions.keys())


def test_softirqs(proc):
    assert proc.softirqs['SCHED']


def test_interrupts(proc):
    assert proc.interrupts['NMI']


def test_meminfo(proc):
    assert proc.meminfo['MemTotal']


def test_diskstats(proc):
    assert len(proc.diskstats.keys())


def test_vmstat(proc):
    assert len(proc.vmstat.keys()) > 70
