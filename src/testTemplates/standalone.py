
from framework.dirsrvtests_log import console_display
from standAloneDS import *
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
    t = MyTicketname()
    return t

class MyTicketname():

    def __init__(self):
        self.bugid = int(dirutil.class2bugid(self))
        self.url = "https://fedorahosted.org/389/ticket/" + str(self.bugid)
        self.instance = None
        self.step = 0

    def __log_msg(self, phase, msg):
        return "Test %6d [%-7s (%2d)]: %s" % (self.bugid, phase, self.__get_step(), msg)
        #print '{0:10} ==> {1:10d}'.format(phase, self.bugid)

    def __init_step(self):
        self.step = 0

    def __next_step(self):
        self.step += 1

    def __get_step(self):
        return self.step

    def startup(self):
        self.__init_step()

        if not self.instance is None:
            logging_display(WARNING, self.__log_msg("startup", "Instance already created"))
            return 1
        self.__next_step()

        self.instance = StandAloneDS("standalone", self.bugid)
        if self.instance.create_instance() != 0:
            logging_display(WARNING, self.__log_msg("startup", "Fail to create the instance"))
            return 1
        self.__next_step()

        console_display(self.__log_msg("startup", "PASS"))
        return 0


    def cleanup(self):
        self.__init_step()

        if self.instance is None:
            logging_display(WARNING, self.__log_msg("cleanup", "Invalid instance value"))
            return 1
        self.__next_step()

        if self.instance.remove_instance() != 0:
            logging_display(WARNING, self.__log_msg("cleanup", "Fail to cleanup the instance"))
            return 1
        self.__next_step()

        console_display(self.__log_msg("cleanup", "PASS"))
        return 0



    def run(self):
        self.__init_step()

        # body of the test case

        self.__log_msg("run", "PASS")
        return 0

