"""/proc/<pid>/net handlers"""

from procfs.core import ProcessFile, Dict


class dev(ProcessFile):
    """/proc/<pid>/net/dev
    """

    def _parse(self, data):
        lines = data.splitlines()
        lines.pop(0) 
        header = lines.pop(0)
        _, rcv_header, tx_header = header.split('|')
        rcv_keys = rcv_header.split()
        tx_keys = tx_header.split()
        limit = len(rcv_keys)
        result = Dict()
        for line in lines:
            interface, str_values = line.split(':', 1)
            interface = interface.strip()
            values = map(int, str_values.split())
            rcv = Dict(zip(rcv_keys, values[:limit]))
            tx = Dict(zip(tx_keys, values[limit:]))
            result[interface] = Dict(receive=rcv, transmit=tx)
        return result


class route(ProcessFile):
    """/proc/<pid>/net/route
    """

    def _parse(self, data):
        lines = data.splitlines()
        header = lines.pop(0)
        header = header.lower()
        keys = header.split()
        keys.pop(1)
        result = Dict()
        for line in lines:
            values = line.split()
            destination = values.pop(1)
            entry = Dict(zip(keys, values))
            if destination == "00000000":
                if result.has_key(destination):
                    result[destination].append(entry)
                else:
                    result[destination] = [entry]
            else:
                result[destination] = entry

        return result


class _BaseStats(ProcessFile):
    """Parser for /proc/<pid>/net/snmp and /proc/<pid>/net/netstat
    """

    def _parse(self, data):
        lines = data.splitlines()
        result = Dict()
        for index, line in enumerate(lines):
            data_type, data = line.split(': ', 1)
            if not index % 2:
                # This is a header line
                header = data.split()
            else:
                # This is a values line
                values = map(int, data.split())
                result[data_type] = Dict(zip(header, values))
        return result


class snmp(_BaseStats):
    """/proc/<pid>/net/snmp
    """


class netstat(_BaseStats):
    """/proc/<pid>/net/netstat
    """


class _TcpUdpBase(ProcessFile):
    """Helpers for parsing /proc/<pid>/net/tcp and /proc/<pid>/net/udp
    """

    def _parse_addr(self, addr):
        hex_addr, hex_port = addr.split(':', 1)
        ipaddr = '.'.join(map(lambda x: str(int(x, 16)), 
                              (addr[6:8], addr[4:6], addr[2:4], addr[:2])))
        port = int(hex_port, 16)
        return ipaddr, port


class tcp(_TcpUdpBase):
    """/proc/<pid>/net/tcp
    """

    # From Linux kernel source: include/net/tcp_states.h
    __tcp_states = {'01': 'ESTABLISHED',
                    '02': 'SYN_SENT',
                    '03': 'SYN_RECV',
                    '04': 'FIN_WAIT1',
                    '05': 'FIN_WAIT2',
                    '06': 'TIME_WAIT',
                    '07': 'CLOSE',
                    '08': 'CLOSE_WAIT',
                    '09': 'LAST_ACK',
                    '0A': 'LISTEN',
                    '0B': 'CLOSING'}

    def _parse(self, data):
        lines = data.splitlines()
        header = lines.pop(0).split()
        header.pop(0) # skip "sl" 
        header.append('other')
        result = {}
        for line in lines:
            parts = line.split()
            (slot, local_address, rem_address, st, tx_rx_queue, tr_tm_when,
             retrnsmt, uid, timeout, inode) = parts[:10]
            local_addr, local_port = self._parse_addr(local_address)
            remote_addr, remote_port = self._parse_addr(rem_address)
            other = parts[10:]
            slot = int(slot.split(':', 1)[0])
            st = self.__tcp_states[st]
            tx_queue, rx_queue = tx_rx_queue.split(':', 1)
            tr, tm_when = tr_tm_when.split(':', 1)
            uid = int(uid)
            timeout = int(timeout)
            inode = int(inode)
            result[slot] = Dict(zip(header, ((local_addr, local_port),
                                             (remote_addr, remote_port),
                                             st, tx_queue, rx_queue, tr, 
                                             tm_when, retrnsmt, uid, timeout,
                                             inode, other)))
        return result


class udp(_TcpUdpBase):
    """/proc/<pid>/net/udp
    """

    def _parse(self, data):
        lines = data.splitlines()
        header = lines.pop(0).split()
        header.pop(0) # skip "sl" 
        result = {}
        for line in lines:
            (slot, local_address, rem_address, st, tx_rx_queue, 
             tr_tm_when, retrnsmt, uid, timeout, inode, ref, 
             pointer, drops) = line.split()
            local_addr, local_port = self._parse_addr(local_address)
            remote_addr, remote_port = self._parse_addr(rem_address)
            slot = int(slot.split(':', 1)[0])
            tx_queue, rx_queue = tx_rx_queue.split(':', 1)
            tr, tm_when = tr_tm_when.split(':', 1)
            uid = int(uid)
            timeout = int(timeout)
            inode = int(inode)
            result[slot] = Dict(
                            zip(header, ((local_addr, local_port),
                                         (remote_addr, remote_port),
                                         st, tx_queue, rx_queue, tr, tm_when,
                                         retrnsmt, uid, timeout, inode, ref,
                                         pointer, drops)))
        return result


class sockstat(ProcessFile):
    """/proc/<pid>/net/sockstat
    """

    def _parse(self, data):
        lines = data.splitlines()
        result = Dict()
        for line in lines:
            data_type, data = line.split(': ', 1)
            result[data_type] = Dict()
            for index, value in enumerate(data.split()):
                if not index % 2:
                    key = value
                else:
                    result[data_type][key] = int(value)
        return result


class dev_mcast(ProcessFile):
    """/proc/<pid>/net/dev_mcast
    """

    def _parse(self, data):
        lines = data.splitlines()
        result = Dict()
        for line in lines:
            index, interface, users, gusers, address = line.split()
            if interface in result:
                result[interface]['addresses'].append(address)
            else:
                result[interface] = Dict(index=int(index),
                                         users=int(users), 
                                         gusers=int(gusers),
                                         addresses=[address])
        return result
