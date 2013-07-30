from common import *
from dirsrvtests_log import *
import replication
import dirutil
import os
import replication

INF_TEMPLATE = """
[General]
FullMachineName=   $FQDN
SuiteSpotUserID=   $USER
SuiteSpotGroup=    $GROUP

[slapd]
ServerPort=   $PORT
ServerIdentifier=   $SERVERID
Suffix=   $SUFFIX
RootDN=   cn=Directory Manager
RootDNPwd= $PASSWORD
"""


class DsInstance():
    def __init__(self, serverid=None, realm_name=None, fqdn=None, dm_password=None, suffix=None, userID=None, groupID=None, port_normal=None):
        self.serverid    = serverid
        self.realm_name  = realm_name
        self.fqdn        = fqdn
        self.dm_password = dm_password
        self.suffix      = suffix
        self.repl_mgr    = None

        if userID == None:
            self.userID = DS_USER
        else:
            self.userID = userID

        if groupID == None:
            self.groupID = DS_GROUP
        else:
            self.groupID = groupID

        self.port        = port_normal
        self.sub_dict = dict(SERVERID=self.serverid,
                             REALM=self.realm_name,
                             FQDN=self.fqdn,
                             PASSWORD=self.dm_password,
                             SUFFIX=self.suffix,
                             PORT=self.port,
                             USER=self.userID,
                             GROUP=self.groupID,
                         )
        self.open_ports = []

    def get_replication_manager(self):
        return self.repl_mgr

    def get_port(self):
        return self.port

    def get_hostname(self):
        return self.fqdn
    
    def create_instance(self):
        inf_txt = dirutil.template_str(INF_TEMPLATE, self.sub_dict)
        inf_fd = dirutil.write_tmp_file(inf_txt)
        if dirutil.file_exists(CMD_SETUP):
            try:
                logName = os.getlogin()
                if logName != "root":
                    args = [CMD_SUDO, CMD_SETUP, "--silent", "--logfile", "/tmp/tofuthierry", "-f", inf_fd.name]
                else:
                    args = [CMD_SETUP, "--silent", "--logfile", "/tmp/tofuthierry", "-f", inf_fd.name]
            except:
                args = [CMD_SUDO, CMD_SETUP, "--silent", "--logfile", "/tmp/tofuthierry", "-f", inf_fd.name]

            dirutil.run(args)
            self.open_ports.append(self.port);
            return 0
        else:
            slogging_display(CRITICAL, "Failure missing " + CMD_SETUP)
            return 1

    def remove_instance(self):
        instance_name =  DIRSRV_SLAPD_PREFIX + self.serverid
        if dirutil.file_exists(CMD_REMOVE):
            try:
                logName = os.getlogin()
                if logName != "root":
                    args = [CMD_SUDO, CMD_REMOVE, "-i", instance_name]
                else:
                    args = [CMD_REMOVE, "-i", instance_name]
            except:
                args = [CMD_SUDO, CMD_SETUP, "--silent", "--logfile", "/tmp/tofuthierry", "-f", inf_fd.name]

            dirutil.run(args)
            return 0
        else:
            logging_display(CRITICAL, "Failure: command missing " + CMD_REMOVE)
            return 1

    def setup_master(self, replicaId):

        # add a replication manager
        self.repl_mgr = replication.ReplicationManager()
        if self.repl_mgr.add_replication_manager(self.fqdn, self.port) != 0:
            return 1

        # enable replication on the suffix
        replica = replication.Replica(REPLICAROLE_MASTER, self.fqdn, self.port, self.serverid, self.suffix, replicaId)
        replica.enable_replication()


        return 0

    def setup_consumer(self):

        # add a replication manager
        self.repl_mgr = replication.ReplicationManager()
        if self.repl_mgr.add_replication_manager(hostname=self.fqdn, port=self.port) != 0:
            return 1

        # enable replication on the suffix
        replica = replication.Replica(REPLICAROLE_CONSUMER, self.fqdn, self.port, self.serverid, self.suffix, None)
        replica.enable_replication()

        return 0



