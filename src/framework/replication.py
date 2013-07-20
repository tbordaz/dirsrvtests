import decimal
from common import *
import dirutil
import os
import re
import random
import string
import time


ENTRY_REPL_MANAGER_TEMPLATE = """
dn: $REPL_MANAGER_DN
uid: rmanager
givenName: r
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetorgperson
sn: manager
cn: r manager
userPassword: $REPL_MANAGER_PWD
"""

ENTRY_REPLICA_TEMPLATE = """
dn: cn=replica,cn="$SUFFIX",cn=mapping tree,cn=config
objectClass: nsDS5Replica
objectClass: top
nsDS5ReplicaRoot: $SUFFIX
nsDS5ReplicaType: $REPLICATYPE
nsDS5Flags: $REPLICAFLAG
nsDS5ReplicaId: $REPLICAID
nsds5ReplicaPurgeDelay: 604800
nsDS5ReplicaBindDN: $REPL_MANAGER_DN
cn: replica
"""

ENTRY_CHANGELOG_TEMPLATE = """
dn: cn=changelog5,cn=config
objectClass: top
objectClass: extensibleObject
cn: changelog5
nsslapd-changelogdir: $DIRSRV_DB_DIR/$DIRSRV_SLAPD_PREFIX$SERVERID/$DIRSRV_CLDB_DIR
"""

ENTRY_REPLICA_MGR_TEMPLATE = """
dn: cn=$LABEL,cn=replica,cn="$SUFFIX",cn=mapping tree,cn=config
objectclass: top
objectclass: nsds5replicationagreement
cn: $LABEL
nsds5replicahost: $HOSTNAME
nsds5replicaport: $PORT
nsds5ReplicaBindDN: $REPLMGRDN
nsds5replicabindmethod: SIMPLE
nsds5replicaroot: $SUFFIX
description: $LABEL
nsds5replicacredentials: $REPLMGRPWD
"""

RA_INITIALIZE_TEMPLATE = """
dn: cn=$LABEL,cn=replica,cn="$SUFFIX",cn=mapping tree,cn=config
changetype: modify
replace: nsds5beginreplicarefresh
nsds5beginreplicarefresh: start
"""

ENTRY_DUMMY = """
dn: uid=$UID,$SUFFIX
cn: test
sn: test
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetorgperson
uid: $UID
"""

sub_dict = dict(REPL_MANAGER_DN = REPL_MANAGER_DN,
                    REPL_MANAGER_PWD = COMMON_PASSWORD
                    )

class ReplicationManager():
    def __init__(self, rm_dn=None, rm_pwd=None):
        self.rm_dn = rm_dn
        self.rm_pwd = rm_pwd

        if rm_dn is None:
            self.rm_dn = REPL_MANAGER_DN

        if rm_pwd is None:
            self.rm_pwd = COMMON_PASSWORD

    def get_replication_manager_dn(self):
        return self.rm_dn

    def get_replication_manager_pwd(self):
        return self.rm_pwd

    def add_replication_manager(self, hostname=None, port=None, bindDn=None, bindDnPwd=None):
        if hostname is None:
            hostname = "localhost"

        if port is None:
            return 1

        if bindDn is None:
            bindDn = DIR_MANAGER_DN

        if bindDnPwd is None:
            bindDnPwd = COMMON_PASSWORD

        #print "add_replication_manager: %s:%d" % (hostname, int(port))
        inf_fd = dirutil.mk_ldapmodify_file(ENTRY_REPL_MANAGER_TEMPLATE, sub_dict)
        rc = dirutil.ldapmodify(hostname, port, bindDn, bindDnPwd, inf_fd.name, "-a -c")
        dirutil.rm_ldapmodify_file(inf_fd)

        return rc

class Replica():
    def __init__(self, role=None, hostname=None, port=None, serverid=None, suffix=None, replicaId=None):
        self.role=role
        self.hostname = hostname
        self.port = port
        self.serverid= serverid
        self.suffix = suffix
        self.replicaType = None
        self.replicaId = replicaId
        self.replicaFlag = None

        if hostname is None:
            self.hostname = "localhost"


    def __add_changelog(self):
        sub_dict["DIRSRV_DB_DIR"] = DIRSRV_DB_DIR
        sub_dict["DIRSRV_SLAPD_PREFIX"] = DIRSRV_SLAPD_PREFIX
        sub_dict["DIRSRV_CLDB_DIR"] = DIRSRV_CLDB_DIR
        sub_dict["SERVERID"] = self.serverid
        inf_fd = dirutil.mk_ldapmodify_file(ENTRY_CHANGELOG_TEMPLATE, sub_dict)
        rc = dirutil.ldapmodify(self.hostname, self.port, DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-a -c")
        dirutil.rm_ldapmodify_file(inf_fd)
        del sub_dict["DIRSRV_DB_DIR"]
        del sub_dict["DIRSRV_SLAPD_PREFIX"]
        del sub_dict["DIRSRV_CLDB_DIR"]
        del sub_dict["SERVERID"]
        return rc

    def __enable_replication(self):
        # add the replica
        sub_dict["SUFFIX"] = self.suffix
        sub_dict["REPLICATYPE"] = self.replicaType
        sub_dict["REPLICAID"] = self.replicaId
        sub_dict["REPLICAFLAG"] = self.replicaFlag
        inf_fd = dirutil.mk_ldapmodify_file(ENTRY_REPLICA_TEMPLATE, sub_dict)
        rc = dirutil.ldapmodify(self.hostname, self.port, DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-a -c")
        dirutil.rm_ldapmodify_file(inf_fd)
        del sub_dict["SUFFIX"]
        del sub_dict["REPLICATYPE"]
        del sub_dict["REPLICAID"]
        del sub_dict["REPLICAFLAG"]

    def enable_replication(self):
        #check the role
        if ((self.role is None) and
            (self.role != REPLICAROLE_MASTER) and
            (self.role != REPLICAROLE_HUB) and
            (self.role != REPLICAROLE_CONSUMER)):
            print "enable_replicaion: invalid role"
            return 1

        #check the suffix
        if self.suffix is None:
            print "enable_replication: invalid suffix"
            return 1

        # check serverid
        if self.serverid is None:
            print "enable_replication: invalid serverid"
            return 1
        else:
            cldir = DIRSRV_DB_DIR + "/" + DIRSRV_SLAPD_PREFIX + self.serverid
            if not dirutil.dir_exists(cldir):
                print "enable_replication: invalid serverid: %s does not exist" % self.serverid


        #check the replicaType
        if (self.role == REPLICAROLE_MASTER):
            # master
            self.replicaType = REPLICATYPE_MASTER
        else:
            # consumer or hub
            self.replicaType = REPLICATYPE_CONSUMER

        # check the replicaId
        if self.replicaType == REPLICATYPE_MASTER:
            # this is a master -> replicaId should be a decimal [0..CONSUMER_REPLICAID]
            if self.replicaId is None:
                print "enable_replication: invalid replicaId (it should be decimal)"
                return 1
            if not decimal.Decimal(self.replicaId):
                print "enable_replication: invalid replicaId (it should be decimal)" + self.replicaId
                return 1
            if ((self.replicaId <= 0) or (CONSUMER_REPLICAID <= self.replicaId)):
                print "enable_replication: invalid replicaId (it should be [0..%d] instead of %d" % (CONSUMER_REPLICAID, self.replicaId)
        else:
            # for Hub/consumer
            self.replicaId = CONSUMER_REPLICAID

        # assign the replica Flag
        if ((self.role == REPLICAROLE_MASTER) or (self.role == REPLICAROLE_HUB)):
            self.replicaFlag = REPLICAFLAG_LOG_CHG
        else:
            self.replicaFlag = REPLICAFLAG_NOLOG_CHG

        # check we have a backend for that suffix
        filter = "(&(%s)(cn=%s))" % (SUFFIX_FILTER, self.suffix)
        stdout, stderr, rc = dirutil.ldapsearch(self.hostname, self.port, DIR_MANAGER_DN, COMMON_PASSWORD, MAPPING_TREE_DN, filter, SCOPE_ONE, "cn")
        if rc != 0:
            print "Fail to retrieve the backend suffixe %s" % filter

        # check we have not a replica for it
        base = "cn=%s,%s" % (self.suffix, MAPPING_TREE_DN)
        stdout, stderr, rc = dirutil.ldapsearch(self.hostname, self.port, DIR_MANAGER_DN, COMMON_PASSWORD, base, REPLICA_FILTER, SCOPE_ONE, "cn")
        if rc != 0:
            print "Fail to look up for replica"
            return 1
        for line in re.split('\n', stdout):
            if line.startswith("dn: "):
                print "Fail the replica already exist: " + line
                return 1

        # add the changelog
        if (self.replicaFlag == REPLICAFLAG_LOG_CHG):
            self.__add_changelog()

        # create the replica
        self.__enable_replication()

        return 0


class ReplicaAgreement():
    def __init__(self, suffix, label, supplier_hostname, supplier_port, consumer_hostname, consumer_port, replica_mgr_dn, replica_mgr_pwd):
        self.suffix = suffix
        self.label = label
        self.supplier_hostname = supplier_hostname
        self.supplier_port = supplier_port
        self.consumer_hostname = consumer_hostname
        self.consumer_port = consumer_port
        self.replica_mgr_dn = replica_mgr_dn
        self.replica_mgr_pwd = replica_mgr_pwd


    def __create(self):
        sub_dict["SUFFIX"] = self.suffix
        sub_dict["HOSTNAME"] = self.consumer_hostname
        sub_dict["PORT"] = self.consumer_port
        sub_dict["REPLMGRDN"] = self.replica_mgr_dn
        sub_dict["REPLMGRPWD"] = self.replica_mgr_pwd
        sub_dict["LABEL"] = self.label
        inf_fd = dirutil.mk_ldapmodify_file(ENTRY_REPLICA_MGR_TEMPLATE, sub_dict)
        rc = dirutil.ldapmodify(self.supplier_hostname, self.supplier_port, DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-a -c")
        dirutil.rm_ldapmodify_file(inf_fd)
        del sub_dict["SUFFIX"]
        del sub_dict["HOSTNAME"]
        del sub_dict["PORT"]
        del sub_dict["REPLMGRDN"]
        del sub_dict["REPLMGRPWD"]
        del sub_dict["LABEL"]

        return rc

    def initialize_consumer(self):
        sub_dict["SUFFIX"] = self.suffix
        sub_dict["LABEL"] = self.label
        inf_fd = dirutil.mk_ldapmodify_file(RA_INITIALIZE_TEMPLATE, sub_dict)
        rc = dirutil.ldapmodify(self.supplier_hostname, self.supplier_port, DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-c")
        dirutil.rm_ldapmodify_file(inf_fd)
        del sub_dict["SUFFIX"]
        del sub_dict["LABEL"]

        return rc

    def check_replication(self):
        uid = ''.join(random.choice(string.ascii_lowercase) for x in range(10))
        sub_dict["SUFFIX"] = self.suffix
        sub_dict["UID"] = uid
        inf_fd = dirutil.mk_ldapmodify_file(ENTRY_DUMMY, sub_dict)
        rc = dirutil.ldapmodify(self.supplier_hostname, self.supplier_port, DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-a -c")
        dirutil.rm_ldapmodify_file(inf_fd)
        del sub_dict["UID"]
        del sub_dict["SUFFIX"]
        if rc != 0:
            print "Fail to check replication is working"
            return 1


        # check the entry is on the supplier
        stdout, stderr, rc = dirutil.ldapsearch(self.supplier_hostname, self.supplier_port, DIR_MANAGER_DN, COMMON_PASSWORD, self.suffix, "uid=%s" % uid, SCOPE_SUB, "dn")
        if rc != 0:
            print "Fail to retrieve the test entry from the supplier"
            return 1
        found = 0
        searched_uid = "dn: uid=%s" % uid
        for line in re.split('\n', stdout):
            if line.startswith(searched_uid):
                found = 1
                break

        if found == 0:
            print "Fail the test entry is not on the supplier"
            return 1

        time.sleep(10)
        # check the entry is on the consumer
        tries = 0
        found = 0
        while tries < 10:
                time.sleep(1)
            
                stdout, stderr, rc = dirutil.ldapsearch(self.consumer_hostname, self.consumer_port, DIR_MANAGER_DN, COMMON_PASSWORD, self.suffix, "uid=%s" % uid, SCOPE_SUB, "dn")
                if ((rc != 0) and (rc != 10)):
                    # it could still be under initialisation
                    print "Fail to retrieve the test entry from the consumer"
                    return 1
                for line in re.split('\n', stdout):
                    if line.startswith(searched_uid):
                        found = 1
                        break

                if found == 1:
                    # the entry was finally replicated
                    break
                    
                tries += 1

        if found == 0:
            print "Fail the test entry is not on the consumer"
            return 1


        return 0


    def create(self):
        if self.suffix is None:
            print "Fail to create ReplicaAgreement: suffix not defined"

        if self.supplier_hostname is None:
            self.supplier_hostname = "localhost"

        if self.consumer_hostname is None:
            self.consumer_hostname = "localhost"

        supplier_free, consumer_free = dirutil.check_ports(self.supplier_port, self.consumer_port)
        if supplier_free:
            print "Fail to create ReplicaAgreement: supplier not on port %d" % self.supplier_port
            return 1
        if consumer_free:
            print "Fail to create ReplicaAgreement: consumer not on port %d" % self.consumer_port
            return 1

        # check replica_mgr is valid
        stdout, stderr, rc = dirutil.ldapsearch(self.consumer_hostname, self.consumer_port, self.replica_mgr_dn, self.replica_mgr_pwd, "", "objectclass=*", SCOPE_BASE, "dn")
        if rc != 0:
            print "Fail to valid replication manager %s on %s:%d" % (self.replica_mgr_dn, self.consumer_hostname, self.consumer_port)

        if self.label is None:
            self.label = "RA to %s:%d" % (self.replica_mgr_dn, self.consumer_hostname)

        if self.__create() != 0:
            print "Fail to create the replication agreement entry"
            return 1

        return 0

        
