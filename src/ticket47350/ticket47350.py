from singleMasterDS import *
import dirutil
import shutil
import pwd
import sys
import os
import re
import time
import tempfile
import base64
import stat

def create_test():
    t = Ticket47350()
    return t

class Ticket47350():
    def __init__(self):
        self.bugid = int(dirutil.class2bugid(self))
        self.topology = None
        self.step = 0
        return


    def __log_msg(self, phase, msg):
        print 'Test %d [%s (%d)]: %s' % (self.bugid, phase, self.__get_step(), msg)
        #print '{0:10} ==> {1:10d}'.format(phase, self.bugid)

    def __init_step(self):
        self.step = 0

    def __next_step(self):
        self.step += 1

    def __get_step(self):
        return self.step


    def startup(self):
        self.__init_step()

        # Allocate the topology
        if self.topology is not None:
            self.__log_msg("startup", "topology already initialized")
        self.topology = SingleMasterDS("master", "consumer", self.bugid)
        self.__next_step()

        # create the master/consumer instance
        if self.topology.create() != 0:
            self.__log_msg("startup", "Fail to create the singleMaster topology")
            return 1
        self.__next_step()

        # setup replication
        if self.topology.setup_replication() != 0:
            self.__log_msg("startup", "Fail to create the replication topology")
            return 1
        self.__next_step()

        self.__log_msg("startup", "PASS")
        return 0
    
    def cleanup(self):
        self.__init_step()
        if self.topology.remove() != 0:
            self.__log_msg("cleanup", "Fail to remove the singleMaster topology")
            return 1
        self.__next_step()

        self.__log_msg("cleanup", "PASS")
        return 0

    def run(self):
        print "     !!! Test to be implemented !!!!"
        return 0