from common import STANDALONE_SERVERID
import dirutil
import socket
from common import *
from dsinstance import *


class StandAloneDS():

        def __init__(self, serverid=None, bugid=None, user=None, group=None):
            self.serverid = serverid
            self.bugid = bugid
            self.normal_port = None
            self.secure_port = None
            self.dsinstance  = None
            self.hostname    = None
            self.domain_name = None
            self.suffix      = None
            self.rootDN      = DIR_MANAGER_DN
            self.rootDNPwd   = COMMON_PASSWORD
            self.userID      = DS_USER
            self.groupID     = DS_GROUP

            # get serverid
            if self.serverid is None:
                self.serverid = STANDALONE_SERVERID

            # compute the ports (normal) from bugid
            if bugid is None:
                self.normal_port = 1389
            else:
                self.normal_port = bugid % MAX_PORTNUMBER

            # Assuming it can be run by non "root" take the port above 1000
            if self.normal_port < 1000:
                self.normal_port += 1000

            self.secure_port = self.normal_port + 1
            self.dsinstance = None

            # set hostname
            self.hostname = dirutil.get_fqdn()
            
            # set the domain name from the hostname
            hostname = self.hostname.split(".")
            self.domain_name = ".".join(str(x) for x in hostname[1:])

            # set the suffix
            self.suffix = ",".join("dc=" + str(x) for x in hostname[1:])

            # set the userID
            if user != None:
                self.userID = user

            # set the groupID
            if group != None:
                self.groupID = group


        def get_bugid(self):
            return self.bugid;

        def get_normal_port(self):
            return self.normal_port

        def get_hostname(self):
            return self.hostname

        def get_rootDN(self):
            return self.rootDN

        def get_rootDN_str(self):
            str = "\"%s\"" % self.rootDN
            #print "rootDN=" + str
            return str

        def get_rootDNPwd(self):
            return self.rootDNPwd

        def get_suffix(self):
            return self.suffix

        def __valid_inst_info(self):
            ports = dirutil.check_ports(self.normal_port, self.secure_port)
            if not ((ports[0] is True) and (ports[1] is True)):
                logging_display(WARNING, "Port ldap:%d and/or ldaps:%d already taken" % (self.normal_port, self.secure_port))
                return False

            if self.hostname is None:
                logging_display(WARNING, "Invalid hostname")
                return False

            if self.domain_name is None:
                logging_display(WARNING, "Invalid domain name")
                return False

            return True

        def create_instance(self, realCreation=True):
            if not self.__valid_inst_info():
                return 1
            #print "hostname=" + self.hostname
            #print "domaine_name=" + self.domain_name
            #print "suffix=" + self.suffix
            #print "userID=" + self.userID
            #print "gourpID=" + self.groupID
            self.dsinstance = DsInstance(self.serverid, self.domain_name, self.hostname, self.rootDNPwd, self.suffix , self.userID, self.groupID, self.normal_port )
            if (realCreation and (self.dsinstance.create_instance() != 0)):
                logging_display(WARNING, "Fail to create the instance")
                return 1
            else:
                logging_display(INFO, "     - Instance created")
                return 0


        def remove_instance(self):
            if self.dsinstance == None:
                logging_display(WARNING, "Error: no instance to remove")
                return 1
            if self.dsinstance.remove_instance() != 0:
                logging_display(WARNING, "Fail to remove the instance")
                return 1
            else:
                logging_display(INFO, "     - Instance removed")
                return 0


