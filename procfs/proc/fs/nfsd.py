"""/proc/fs/nfsd handlers"""

from procfs.core import File, Dict


class pool_stats(File):
    """/proc/fs/nfsd/pool_stats
    """

    def _parse(self, content):
        header, values = content.splitlines()
        keys = header[2:].replace('-', '_').split()
        values = (int(i) for i in values.split())
        return Dict(zip(keys, values))
