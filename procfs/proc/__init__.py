from datetime import datetime, timedelta

from procfs.core import Dict, File


class cpuinfo(File):
    """/proc/cpuinfo
    """

    def __len__(self):
        return len(self.read())

    def _parse(self, content):
        lines = content.splitlines()
        count = 0
        data = Dict()
        for line in lines:
            if line:
                if line.startswith('processor\t:'):
                    data[count] = Dict()
                else:
                    key, value = line.split(':', 1)
                    key = key.strip().replace(' ', '_').lower()
                    parser_name = '_parse_' + key
                    if hasattr(self, parser_name):
                        parser = getattr(self, parser_name)
                        value = parser(value)
                    data[count][key] = value
            else:
                count += 1
        return data

    def _parse_address_sizes(self, value):
        physical, virtual = value.split(',', 1)
        physical = int(physical[1:3])
        virtual = int(virtual[1:3])
        return Dict(physical=physical, virtual=virtual)

    def _parse__split(self, value):
        return value.split()
    _parse_flags = _parse__split

    def _parse__int(self, value):
        return int(value)
    _parse_apicid = _parse__int
    _parse_cache_alignment = _parse__int
    _parse_clflush_size = _parse__int
    _parse_core_id = _parse__int
    _parse_cpu_cores = _parse__int
    _parse_cpu_family = _parse__int
    _parse_cpuid_level = _parse__int
    _parse_initial_apicid = _parse__int
    _parse_model = _parse__int
    _parse_physical_id = _parse__int
    _parse_siblings = _parse__int
    _parse_stepping = _parse__int

    def _parse__float(self, value):
        return float(value)
    _parse_bogomips = _parse__float
    _parse_cpu_mhz = _parse__float

    def _parse__KB(self, value):
        return int(value.split(' KB', 1)[0])
    _parse_cache_size = _parse__KB

    def _parse__yes_no(self, value):
        value = value.strip().lower()
        if value == 'yes':
            return True
        else:
            return False
    _parse_fpu = _parse__yes_no
    _parse_fpu_exception = _parse__yes_no
    _parse_wp = _parse__yes_no

    def _parse__strip(self, value):
        return value.strip()
    _parse_model_name = _parse__strip
    _parse_vendor_id = _parse__strip


class uptime(File):
    """/proc/uptime"""

    def _parse(self, content):
        uptime, idle = content.split()
        return Dict(uptime=timedelta(seconds=float(uptime)),
                    idle=timedelta(seconds=float(idle)))


class stat(File):
    """/proc/stat
    """

    def _parse(self, content):
        lines = content.splitlines()
        result = Dict(cpu=Dict())

        cpu_lines, other_lines = [], []
        for line in lines:
            if line.startswith('cpu'):
                cpu_lines.append(line)
            else:
                other_lines.append(line)

        cpu_keys = ('user', 'nice', 'system', 'idle', 'iowait', 'irq',
                    'softirq', 'steal', 'guest', 'total')
        for line in cpu_lines:
            str_values = line.split()
            cpu = str_values.pop(0)
            values = []
            total = 0
            for value in str_values:
                value = int(value)
                total += value
                value = timedelta(seconds=value / 100.)
                values.append(value)
            values.append(timedelta(seconds=total / 100.))
            result[cpu] = Dict(zip(cpu_keys, values))

        for line in other_lines:
            key, value = line.split(' ', 1)
            if ' ' in value:
                result[key] = map(int, value.split())
            else:
                result[key] = int(value)

        parsers = {
            'intr': lambda value: self.__parse_list_with_total(value),
            'softirq': lambda value: self.__parse_list_with_total(value),
            'btime': datetime.fromtimestamp
        }

        for key, parser in parsers.iteritems():
            value = result.get(key)
            if value is not None:
                result[key] = parser(value)

        return result

    def __parse_list_with_total(self, list):
        total = list.pop(0)
        result = Dict(zip(xrange(1, len(list) + 1), list))
        result.total = total
        return result


class loadavg(File):
    """/proc/loadavg
    """

    def _parse(self, content):
        la1mn, la5mn, la15mn, entities, last_pid = content.split()
        # Kernel scheduling entities (ie. Process/Thread)
        current, total = map(int, entities.split('/', 1))
        return Dict(average={1: float(la1mn),
                             5: float(la5mn),
                             15: float(la15mn)},
                    entities=Dict(current=current, total=total),
                    last_pid=int(last_pid))


class partitions(File):
    """/proc/partitions
    """

    def _parse(self, content):
        lines = content.splitlines()
        lines = lines[2:]  # skip header
        result = Dict()
        for line in lines:
            major, minor, blocks, name = line.split()
            major, minor, blocks = int(major), int(minor), int(blocks)
            result[name] = Dict(major=major, minor=minor, block_count=blocks)
        return result


class softirqs(File):
    """/proc/softirqs
    """

    def _parse(self, content):
        lines = content.splitlines()
        cpus = [int(cpu.split('CPU', 1)[1]) for cpu in lines.pop(0).split()]
        keys = cpus + ['total']
        result = Dict()
        for line in lines:
            parts = line.split()
            handler = parts.pop(0)[:-1]
            values = map(int, parts)
            values.append(sum(values))
            result[handler] = Dict(zip(keys, values))
        return result


class interrupts(File):
    """/proc/interrupts
    """

    def _parse(self, content):
        lines = content.splitlines()
        cpus = [int(cpu.split('CPU', 1)[1]) for cpu in lines.pop(0).split()]
        keys = cpus + ['total', 'info']
        result = Dict()
        for line in lines:
            parts = line.split()
            interrupt = parts.pop(0)[:-1]
            try:
                interrupt = int(interrupt)
            except ValueError:
                pass
            if interrupt not in ('ERR', 'MIS'):
                values = parts[:len(cpus)]
                values = map(int, values)
                values.append(sum(values))
                info = ' '.join(parts[len(cpus):])
                values.append(info)
                data = Dict(zip(keys, values))
            else:
                data = int(parts[0])
            result[interrupt] = data
        return result


class meminfo(File):
    """/proc/meminfo
    """

    def _parse(self, content):
        lines = content.splitlines()
        result = Dict()
        for line in lines:
            key, value = line.split(':', 1)
            value = int(value.split(' kB', 1)[0])
            result[key] = value
        return result


class diskstats(File):
    """/proc/diskstats
    """

    __keys = ('read__completed', 'read__merged', 'read__sectors',
              'read__milliseconds', 'write__completed', 'write__merged',
              'write__sectors', 'write__milliseconds', 'io__in_progress',
              'io__milliseconds', 'io__weighted_milliseconds')

    def _parse(self, content):
        lines = content.splitlines()
        result = Dict()
        for line in lines:
            values = line.split()
            major, minor, device = values[:3]
            major, minor = int(major), int(minor)
            values = map(int, values[3:])
            result[device] = Dict(read=Dict(), write=Dict(), io=Dict())
            for index, value in enumerate(values):
                key1, key2 = self.__keys[index].split('__', 1)
                result[device][key1][key2] = value
        return result


class slabinfo(File):
    """/proc/slabinfo
    """

    __keys = ('active_objs', 'num_objs', 'objsize', 'objperslab',
              'pagesperslab', 'limit', 'batchcount', 'sharedfactor',
              'active_slabs', 'num_slabs', 'sharedavail')

    def _parse(self, content):
        lines = content.splitlines()[2:]  # skip header
        result = Dict()
        for line in lines:
            parts = line.split()
            name = parts[0]
            values = map(int, parts[1:6])
            values += map(int, parts[8:11])
            values += map(int, parts[13:16])
            result[name] = Dict(zip(self.__keys, values))
        return result


class vmstat(File):
    """/proc/vmstat"""

    def _parse(self, content):
        result = Dict()
        for line in content.splitlines():
            key, value = line.split()
            result[key] = int(value)
        return result
