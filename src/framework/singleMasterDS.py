from replication import ReplicaAgreement
from common import *
import dirutil
import socket
from dsinstance import *



class SingleMasterDS():
    def __init__(self, masterServerId=None, consumerServerId=None, bugId=None):
        self.masterServerId = None
        self.consumerServerId = None
        self.bugId = bugId
        self.master_normal_port = None
        self.master_secure_port = None
        self.consumer_normal_port = None
        self.consumer_secure_port = None
        self.master_dsinstance  = None
        self.consumer_dsinstance = None
        self.hostname    = None
        self.domain_name = None
        self.suffix      = None
        self.rootDN      = DIR_MANAGER_DN
        self.rootDNPwd   = COMMON_PASSWORD
        self.userID      = DS_USER
        self.groupID     = DS_GROUP


        # get serverid
        if self.masterServerId is None:
            self.masterServerId = SINGLEMASTER_MASTER_SERVERID

        if self.consumerServerId is None:
            self.consumerServerId = SINGLEMASTER_CONSUMER_SERVERID

        # force the ports (normal/secure)
        self.master_normal_port = SINGLEMASTER_MASTER_PORT
        self.master_secure_port = SINGLEMASTER_MASTER_SPORT
        self.consumer_normal_port = SINGLEMASTER_CONSUMER_PORT
        self.consumer_secure_port = SINGLEMASTER_CONSUMER_SPORT


        # set hostname
        self.hostname = dirutil.get_fqdn()

        # set the domain name from the hostname
        hostname = self.hostname.split(".")
        self.domain_name = ".".join(str(x) for x in hostname[1:])

        # set the suffix
        self.suffix = ",".join("dc=" + str(x) for x in hostname[1:])

    def get_suffix(self):
        return self.suffix

    def get_master_instance(self):
        return self.master_dsinstance

    def get_consumer_instance(self):
        return self.consumer_dsinstance

    def get_hostname(self):
        return self.hostname

    def __valid_inst_info(self, normal_port=None, secure_port=None):
        if ((normal_port is None) or (secure_port is None)):
            return False

        ports = dirutil.check_ports(normal_port, secure_port)
        if not ((ports[0] is True) and (ports[1] is True)):
            print "Port ldap:%d and/or ldaps:%d already taken" % (normal_port, secure_port)
            return False

        if self.hostname is None:
            print "Invalid hostname"
            return False

        if self.domain_name is None:
            print "Invalid domain name"
            return False

        return True

    def __create_instance(self, serverid=None, normal_port=None, secure_port=None):
        if not self.__valid_inst_info(normal_port, secure_port):
            print "Invalid ports number: %d - %d" % (int(normal_port), int(secure_port))
            return None
        instance = DsInstance(serverid, self.domain_name, self.hostname, self.rootDNPwd, self.suffix , self.userID, self.groupID, normal_port )
        if instance.create_instance() != 0:
            print "Fail to create the instance"
            return None
        else:
            print "     - Instance slapd-%s created" % serverid
            return instance

    def create(self):
        self.master_dsinstance = self.__create_instance(self.masterServerId, self.master_normal_port, self.master_secure_port)
        if self.master_dsinstance is None:
            return 1

        self.consumer_dsinstance = self.__create_instance(self.consumerServerId, self.consumer_normal_port, self.consumer_secure_port)
        if self.consumer_dsinstance is None:
            return 1

        return 0

    
    def remove(self):
        rc = 0
        if self.master_dsinstance == None:
            print "Error: master not defined"
            rc = 1
        else:
            if self.master_dsinstance.remove_instance() != 0:
                print "Error: Fail to remove the master instance"
                rc = 1

        if self.consumer_dsinstance == None:
            print "Error: master not defined"
            rc = 1
        else:
            if self.consumer_dsinstance.remove_instance() != 0:
                print "Error: Fail to remove the consumer instance"
                rc = 1
                
        return rc

    def setup_replication(self):

        # initialise replication on master
        if self.master_dsinstance.setup_master(SINGLEMASTER_MASTER_REPLICAID) != 0:
            print "Fail to setup replication on the master"
            return 1
        print "     - Master replication enabled"

        # initialize replication on consumer
        if self.consumer_dsinstance.setup_consumer() != 0:
            print "Fail to setup replication on the consumer"
            return 1
        print "     - Consumer replication enabled"

        # initialize a replication agreement master->consumer
        repl_mgr = self.master_dsinstance.get_replication_manager()
        replica_mgr_dn  = repl_mgr.get_replication_manager_dn()
        replica_mgr_pwd = repl_mgr.get_replication_manager_pwd()
        ra = ReplicaAgreement(self.suffix, "RA M -> C",
                                self.hostname, self.master_normal_port,
                                self.hostname, self.consumer_normal_port,
                                replica_mgr_dn, replica_mgr_pwd)
        if ra.create() != 0:
            return 1
        print "     - Replica agreement M -> C done"

        if ra.initialize_consumer() != 0:
            return 1
        print "     - Consumer Initialized"

        if ra.check_replication() != 0:
            return 1
        print "     - Replication checked"

        return 0

 


