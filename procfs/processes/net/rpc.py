from procfs.core import ProcessFile, Dict


# /proc/net/rpc/nfsd documentation:
#   <kernel src>/fs/nfsd/stats.c : nfsd_proc_show
#               /net/sunrpc/stats.c : svc_seq_show
#               /fs/nfsd/nfsproc.c : nfsd_procedures2
#               /fs/nfsd/nfs3proc.c : nfsd_procedures3
#               /fs/nfsd/nfs4proc.c : nfsd_procedures4 nfsd4_ops
#   http://marc.info/?l=linux-nfs&m=119308862812388&w=1
#   http://article.gmane.org/gmane.linux.nfs/16594
class _BaseNfs(ProcessFile):
    """Base class for parsing /proc/net/rpc/nfs and /proc/net/rpc/nfsd
    """

    #_human_friendly_types = {'rc': 'reply_cache',
    #                         'fh': 'filehandle',
    #                         'th': 'threads',
    #                         'ra': 'read_ahead'}

    def _parse(self, data):
        lines = data.splitlines()
        result = Dict()
        for line in lines:
            str_values = line.split()
            type_ = str_values.pop(0)
            values = []
            for value in str_values:
                if '.' in value:
                    parser = float
                else:
                    parser = int
                values.append(parser(value))
            parser_name = '_parse_%s' % type_
            #if type_ in self._human_friendly_types:
            #    type_ = self._human_friendly_types[type_]
            if hasattr(self, parser_name):
                parser = getattr(self, parser_name)
                values = parser(*values)
            result[type_] = values
        return result

    def _parse_net(self, netcnt, netudpcnt, nettcpcnt, nettcpconn):
        return Dict(netcnt=netcnt, netudpcnt=netudpcnt,
                    nettcpcnt=nettcpcnt, nettcpconn=nettcpconn)

    def _parse_proc2(self, cnt, null, getattr, setattr, root, lookup,
                     readlink, read, writecache, write, create, remove,
                     rename, link, symlink, mkdir, rmdir, readdir, statfs):
        return Dict(null=null, getattr=getattr, setattr=setattr,
                    root=root, lookup=lookup, readlink=readlink,
                    read=read, writecache=writecache, write=write,
                    create=create, remove=remove, rename=rename,
                    link=link, symlink=symlink, mkdir=mkdir,
                    rmdir=rmdir, readdir=readdir, statfs=statfs)

    def _parse_proc3(self, cnt, null, getattr, setattr, lookup, access,
                     readlink, read, write, create, mkdir, symlink, mknod,
                     remove, rmdir, rename, link, readdir, readdirplus,
                     fsstat, fsinfo, pathconf, commit):
        return Dict(null=null, getattr=getattr, setattr=setattr,
                    lookup=lookup, access=access, readlink=readlink,
                    read=read, write=write, create=create, mkdir=mkdir,
                    symlink=symlink, mknod=mknod, remove=remove,
                    rmdir=rmdir, rename=rename, link=link,
                    readdir=readdir, readdirplus=readdirplus,
                    fsstat=fsstat, fsinfo=fsinfo, pathconf=pathconf,
                    commit=commit)


class nfsd(_BaseNfs):
    """/proc/net/rpc/nfsd
    """

    def _parse_rc(self, hits, misses, nocache):
        return Dict(hits=hits, misses=misses, nocache=nocache)

    def _parse_fh(self, stale, total_lookups, anonlookups, dir_not_in_cache,
                  nondir_not_in_cache):
        return Dict(stale=stale, total_lookups=total_lookups,
                    anonlookups=anonlookups,
                    dir_not_in_cache=dir_not_in_cache,
                    nondir_not_in_cache=nondir_not_in_cache)

    def _parse_io(self, read, written):
        return Dict(read=read, written=written)

    def _parse_th(self, threads, fullcnt, *busy_times):
        busy = {'10-20': busy_times[0],
                '20-30': busy_times[1],
                '30-40': busy_times[2],
                '40-50': busy_times[3],
                '50-60': busy_times[4],
                '60-70': busy_times[5],
                '70-80': busy_times[6],
                '80-90': busy_times[7],
                '90-100': busy_times[8]}
        return Dict(threads=threads, fullcnt=fullcnt, busy=busy)

    def _parse_rpc(self, cnt, badcnt, badfmt, badauth, badclnt):
        """See <linux-src>/net/sunrpc/stats.c : svc_seq_show
        """
        return Dict(cnt=cnt, badcnt=badcnt,
                    badfmt=badfmt, badauth=badauth,
                    badclnt=badclnt)

    def _parse_ra(self, cache_size, *depths):
        not_found = depths[-1]
        depth = {10: depths[0], 20: depths[1], 30: depths[2], 40: depths[3],
                 50: depths[4], 60: depths[5], 70: depths[6], 80: depths[7],
                 90: depths[8], 100: depths[9]}
        return Dict(cache_size=cache_size, depth=depth, not_found=not_found)

    def _parse_proc4(self, cnt, null, compound):
        return Dict(null=null, compound=compound)

#    def _parse_proc4ops(self, cnt, access, close, commit, create, delegreturn,
#                        getattr, getfh, link, lock, lockt, locku, lookup,
#                        lookupp, nverify, open, open_confirm, open_downgrade,
#                        putfh, putpubfh, putrootfh, read, readdir, readlink,
#                        remove, rename, renew, restorefh, savefh, secinfo,
#                        setattr, setclientid, setclientid_confirm, verify,
#                        write, release_lockowner, exchange_id, create_session,
#                        destroy_session, sequence):
#        return Dict(access=access, close=close, commit=commit,
#                    create=create, delegreturn=delegreturn,
#                    getattr=getattr, getfh=getfh, link=link, lock=lock,
#                    lockt=lockt, locku=locku, lookup=lookup,
#                    lookupp=lookupp, nverify=nverify, open=open,
#                    open_confirm=open_confirm,
#                    open_downgrade=open_downgrade, putfh=putfh,
#                    putpubfh=putpubfh, putrootfh=putrootfh, read=read,
#                    readdir=readdir, readlink=readlink, remove=remove,
#                    rename=rename, renew=renew, restorefh=restorefh,
#                    savefh=savefh, secinfo=secinfo, setattr=setattr,
#                    setclientid=setclientid,
#                    setclientid_confirm=setclientid_confirm,
#                    verify=verify, write=write,
#                    release_lockowner=release_lockowner,
#                    exchange_id=exchange_id,
#                    create_session=create_session,
#                    destroy_session=destroy_session, sequence=sequence)


class nfs(_BaseNfs):
    """/proc/net/rpc/nfs
    """

    def _parse_rpc(self, cnt, retrans, authrefresh):
        """See <linux-src>/net/sunrpc/stats.c : rpc_proc_show
        """
        return Dict(cnt=cnt, retrans=retrans, authrefresh=authrefresh)
