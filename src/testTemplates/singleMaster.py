from framework.dirsrvtests_log import console_display
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
import random
import string


runByNose=False


def create_object():
    t = Myticketname()
    return t

def test_ticketname():
    global runByNose

    #
    # in order to prevent display of message on the console
    #
    runByNose = True



    #
    # initialize the file logging for this test
    # True: because this is the Nose wrapper
    #
    ticket = os.path.dirname(__file__)
    assert (logging_init(ticket, True) == 0)

    t = MyTicketname()
    assert (t is not None)
    try:

        assert(t.startup() == 0)
        try:
            assert(t.run() == 0)
        except AssertionError:
            raise
        except:
            pass

    except AssertionError:
        raise
    except:
        pass

    finally:
        assert(t.cleanup() == 0)
        
class Myticketname():
    def __init__(self):
        self.bugid = int(dirutil.class2bugid(self))
        self.url = "https://fedorahosted.org/389/ticket/" + str(self.bugid)
        self.topology = None
        self.step = 0
        return


    def __log_msg(self, phase, msg):
        return "Test %6d [%-7s (%2d)]: %s" % (self.bugid, phase, self.__get_step(), msg))
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
            logging_display(INFO, self.__log_msg("startup", "topology already initialized"))
        self.topology = SingleMasterDS("master", "consumer", self.bugid)
        self.__next_step()

        # create the master/consumer instances
        if self.topology.create() != 0:
            logging_display(WARNING, self.__log_msg("startup", "Fail to create the singleMaster topology"))
            return 1
        self.__next_step()

        # setup replication
        if self.topology.setup_replication() != 0:
            logging_display(WARNING, self.__log_msg("startup", "Fail to create the replication topology"))
            return 1
        self.__next_step()

        console_display(self.__log_msg("startup", "PASS"))
        return 0

    def cleanup(self):
        self.__init_step()

        if self.topology.remove() != 0:
            logging_display(WARNING, self.__log_msg("cleanup", "Fail to remove the singleMaster topology"))
            return 1
        self.__next_step()

        console_display(self.__log_msg("cleanup", "PASS"))
        return 0



    def run(self):
        self.__init_step()


        console_display(self.__log_msg("run", "PASS"))
        return 0