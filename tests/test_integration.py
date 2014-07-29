
"""
procfs integration tests
~~~~~~~~~~~~~~~~~~~~~~~~

A set of simple tests that are executed against the real /proc directory
"""

import pytest

import procfs
from procfs.exceptions import DoesNotExist, NoParentProcess

@pytest.fixture
def proc():
    return procfs.Proc()

def test_missing_file(proc):
    with pytest.raises(DoesNotExist):
        proc.self.not_a_real_file

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




def test_proc_self_parent(proc):
    assert proc.self.parent
#proc.self.uptime

def test_processes_0(proc):
    p = proc.processes[0]
    assert p.id == 1
    with pytest.raises(NoParentProcess):
        p.parent

def test_processes_cmdline(proc):
    pythons = proc.processes.cmdline('python')
    assert len(pythons)

def test_processes_uid_0(proc):
    uid0p = proc.processes.uid(0)
    assert len(uid0p)

def test_processes_user_root(proc):
    rootp = proc.processes.user('root')
    assert len(rootp)

def test_mounts(proc):
    m = proc.mounts
    assert m
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
    assert len(proc.vmstat.keys()) > 100



