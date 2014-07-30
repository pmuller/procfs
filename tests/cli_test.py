import pytest

import procfs
from procfs import cli
from procfs.exceptions import PathNotFoundError

@pytest.fixture
def proc():
    return None

def test_proc_timedata(proc):
    assert cli.find('1/stat', False)

def test_proc_processes(proc):
    assert cli.find('1', False)

def test_proc_itemorattr(proc):
    assert cli.find('loadavg/average/15', False)

def test_proc_badfile(proc):
    with pytest.raises(PathNotFoundError):
        assert cli.find('jbsdabfjasdbfsdafl', False)

def test_proc_cannotlist(proc):
    with pytest.raises(AttributeError):
        assert cli.find('cpuinfo/0/cpu_family', True)

