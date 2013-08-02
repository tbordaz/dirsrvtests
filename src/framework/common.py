#
# Directory file/dir names
#
DIRSRV_INSTANCES_DIR = "/etc/dirsrv"
DIRSRV_DB_DIR        = "/var/lib/dirsrv"
DIRSRV_LOCK_DIR      = "/var/lock/dirsrv"
DIRSRV_CLDB_DIR      = "changelogdb"
DIRSRV_SLAPD_PREFIX  = "slapd-"
DIRSRV_SCHEMA_DIR    = "schema"

DIRSRV_CMD_LDIF2DB   = "ldif2db"

#
# Directory entries
#
DIR_MANAGER_DN = "cn=directory manager"
REPL_MANAGER_DN = "uid=rmanager,cn=config"
MAPPING_TREE_DN = "cn=mapping tree,cn=config"
LDBM_CONFIG = "cn=ldbm database,cn=plugins,cn=config"
CONFIG_DN = "cn=config"

COMMON_PASSWORD = "Secret123"

#
# Owners/Label
#
SELINUX_DIRSRV_LABEL = "ldap_port_t"
DS_USER = 'dirsrv'
DS_GROUP = 'dirsrv'


#
# search admin entries
#
SCOPE_BASE = "base"
SCOPE_ONE = "one"
SCOPE_SUB = "sub"
SUFFIX_FILTER = "nsslapd-state=backend"
REPLICA_FILTER = "objectclass=nsDS5Replica"
ATTR_REPLICAROOT = "nsDS5ReplicaRoot"
ATTR_CACHEMEMSIZE= "nsslapd-cachememsize"
ATTR_BACKEND = "nsslapd-backend"
ATTR_DN = "dn"
ATTR_INSTANCEDIR = "nsslapd-instancedir"


#
# Replica Roles/Type/Flags
#
REPLICAROLE_MASTER    = "master"
REPLICAROLE_HUB       = "hub"
REPLICAROLE_CONSUMER  = "consumer"
REPLICATYPE_MASTER    = 3
REPLICATYPE_HUB       = 2
REPLICATYPE_CONSUMER  = 2
REPLICAFLAG_LOG_CHG   = 1
REPLICAFLAG_NOLOG_CHG = 0

#
# ServerId
#
STANDALONE_SERVERID             = "testinstance"
SINGLEMASTER_MASTER_SERVERID    = "master"
SINGLEMASTER_CONSUMER_SERVERID  = "consumer"
MULTIMASTER_MASTER_1_SERVERID   = "master1"
MULTIMASTER_MASTER_2_SERVERID   = "master2"
MULTIMASTER_CONSUMER_1_SERVERID = "consumer1"
MULTIMASTER_CONSUMER_2_SERVERID = "consumer2"

#
# replicaId
#
SINGLEMASTER_MASTER_REPLICAID   = 1
MULTIMASTER_MASTER_1_REPLICAID  = 1
MULTIMASTER_MASTER_2_REPLICAID  = 2
CONSUMER_REPLICAID              = 65535

#
# Ports
STANDALONE_PORT   = 39000
STANDALONE_SPORT  = 39001

SINGLEMASTER_MASTER_PORT    = 39002
SINGLEMASTER_MASTER_SPORT   = 39003
SINGLEMASTER_CONSUMER_PORT  = 39004
SINGLEMASTER_CONSUMER_SPORT = 39005

MULTIMASTER_MASTER_1_PORT    = 39006
MULTIMASTER_MASTER_1_SPORT   = 39007
MULTIMASTER_MASTER_2_PORT    = 39008
MULTIMASTER_MASTER_2_SPORT   = 39009
MULTIMASTER_CONSUMER_1_PORT  = 39010
MULTIMASTER_CONSUMER_1_SPORT = 39011
MULTIMASTER_CONSUMER_2_PORT  = 39012
MULTIMASTER_CONSUMER_2_SPORT = 39013

DIRSRVTEST_MIN_PORT = STANDALONE_PORT
DIRSRVTEST_MAX_PORT = MULTIMASTER_CONSUMER_2_SPORT
MAX_PORTNUMBER = 50000

#
# admin Commands
#
CMD_SUDO    = "/bin/sudo"
CMD_CHMOD   = "/bin/chmod"
CMD_USERADD = "/usr/sbin/useradd"
CMD_USERDEL = "/usr/sbin/userdel"
CMD_GRPADD  = "/usr/sbin/groupadd"
CMD_GRPDEL  = "/usr/sbin/groupdel"
CMD_SETUP   = "/usr/sbin/setup-ds.pl"
CMD_REMOVE  = "/usr/sbin/remove-ds.pl"
CMD_SELINUX_SEMANAGE = "/usr/sbin/semanage"
CMD_LDAPMODIFY = "/bin/ldapmodify"
CMD_LDAPSEARCH = "/bin/ldapsearch"
CMD_SYSTEMCTL  = "/bin/systemctl"
CMD_OPT_START  = "start"
CMD_OPT_STOP   = "stop"
CMD_MOVE       = "/bin/mv"
CMD_COPY       = "/bin/cp"
CMD_CHOWN      = "/bin/chown"
CMD_CHMOD      = "/bin/chmod"
CMD_GUNZIP     = "/usr/bin/gunzip"

#
# logging for the dirsrvtests themself
#   - CRITICAL: general failure of the framework. Remaining tests will not be proceeded
#   - WARNING : specific failure during a given test. The test will terminate and remaining tests will be proceeded
#   - INFO    : specific failure during a given test. The test will continue and remaining tests will be proceeded
#   - DEBUG   : informative message usually used during test debugging
#
CRITICAL = 4
WARNING  = 3
INFO     = 2
DEBUG    = 1

