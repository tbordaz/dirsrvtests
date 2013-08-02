
from dirsrvtests_log import console_display
from standAloneDS import *
from common import *
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
from subprocess import call
import datetime


runByNose=False

def create_object():
    t = Ticket490()
    return t

def test_ticket490():
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

    t = Ticket490()
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


class Ticket490():

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

        instance = self.instance

        # set the entry cache to 1Gb to store all entries in it
        bkInstance = backend.BackendInstance(instance.get_hostname(), instance.get_normal_port(), instance.get_suffix())
        ONE_GIGA = 1000000000
        value, rc = bkInstance.getCachememsize()
        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "Fail to retrieve the cachesize"))
            return 1
        if int(value) < ONE_GIGA:
            bkInstance.setCachememsize(ONE_GIGA)
            value, rc = bkInstance.getCachememsize()
            if value != ONE_GIGA:
                logging_display(WARNING, self.__log_msg("run", "Fail to set the cachesize"))
                return 1
        self.__next_step()

        # retrieve the import command
        importCommand = bkInstance.get_importcommand()

        # update the schema
        instance.stop()
        self.__next_step()

        schemaFiles = []
        for file in schemaFiles:
            schemaFile = os.path.dirname(__file__) + "/" + file
            if not dirutil.file_exists(schemaFile):
                logging_display(WARNING, self.__log_msg("run", "Fail to retrieve schema file %s" % schemaFile))
                return 1
            if instance.update_schema(schemaFile) != 0:
                logging_display(WARNING, self.__log_msg("run", "Fail to copy schema file %s" % schemaFile))
                return 1
        self.__next_step()


        # decompress the import file
        inFilename  = "userRoot.ldif.gz"
        outFilename = inFilename[:-3]
        inFilePath  = os.path.dirname(__file__) + "/" + inFilename
        outFilePath = os.path.dirname(__file__) + "/" + outFilename
        f = open(outFilePath, 'w')
        call([CMD_GUNZIP, '-c', inFilePath], stdout=f)
        f.close()
        if not dirutil.file_exists(outFilePath):
            logging_display(WARNING, self.__log_msg("run", "Fail to unzip %s" % inFilename))
            return 1
        self.__next_step()

        # move the import file to /tmp so that it can be accessed
        importFilePath = "/tmp/" + os.path.basename(outFilePath)
        call([CMD_SUDO, CMD_MOVE, outFilePath, importFilePath])
        args = [CMD_SUDO, CMD_CHOWN, DS_USER + ":" + DS_GROUP, importFilePath]
        stdout, stderr, rc = dirutil.run(args)
        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "Fail to chown: %s %s" % (DS_USER + ":" + DS_GROUP, importFilePath)))
            logging_display(WARNING, stdout)
            return 1
        self.__next_step()

        # import the file
        rc = bkInstance.importBackendOffline(importCommand, importFilePath)
        self.__next_step()

        # start the instance but due to roles.. wait a bit
        instance.start()
        time.sleep(5)
        self.__next_step()
        

        ROLES = [ "cn=Managed_1,o=intra,SUFFIX",
                "cn=Managed_2,o=intra,SUFFIX",
                "cn=Managed_3,o=intra,SUFFIX",
                "cn=Managed_1,o=intra,SUFFIX",
                "cn=Managed_2,o=intra,SUFFIX",
                "cn=Managed_3,o=intra,SUFFIX",]
        firstLookup = 0
        Failure = False
        for role in ROLES:
            # For each role we do a lookup
            # the first lookup is expensive because we need to prime the entry cache
            # the others lookups will be much rapid
            role = role.replace("SUFFIX", instance.get_suffix())
            start = time.time()
            filter = "(nsrole=\"%s\")" % (role)
            stdout, stderr, rc = dirutil.ldapsearch(instance.get_hostname(), instance.get_normal_port(), DIR_MANAGER_DN, COMMON_PASSWORD, instance.get_suffix(), filter, SCOPE_SUB, "nsroledn")
            if rc != 0:
                logging_display(WARNING, self.__log_msg("run", "Fail to do ldapsearch filter=%s" % (filter)))
                logging_display(WARNING, stdout)
                return 1
            end = time.time()

            if firstLookup == 0:
                # first lookup, just record the time spent
                firstLookup = end - start
            else:
                # check that the spent time for the others ldapsearch
                # is 100 times less.
                # if this ratio is to unstable we may reduce it to 50 times
                # or even less
                RATIO = 100
                if (end-start) > (firstLookup/RATIO):
                    logging_display(WARNING, self.__log_msg("run", "Fail time too long %f vs %f initial" % (end-start, firstLookup)))
                    Failure = True



        if Failure:
            console_display(self.__log_msg("run", "FAIL"))
            return 1
        else:
            console_display(self.__log_msg("run", "PASS"))
            return 0

