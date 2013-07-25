import os.path

import common
import UserString
import string

from standAloneDS import *
import replication
import dirutil
import shutil
import pwd
import sys
import os
import re
import decimal
from importlib import import_module
import time
import tempfile
import base64
import stat
import grp
import logging
from dirsrvtests_log import *



#logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
#logging.basicConfig(filename='example.log',level=logging.DEBUG)

#logging_init()
#logging_display(DEBUG, 'This message should go to the log file')
#console_init()
#console_display("message for the console")
#logging_display(WARNING, 'And this, too')
#quit()


dirsrvUserCreated = False
dirsrvGrpCreated = False

def getTestModules(command):
    testTopDir = os.path.dirname(command)
    testModules = []
    for file in os.listdir(testTopDir):

        if os.path.isdir(os.path.join(testTopDir, file)):
            if ((len(listSpecificTests) != 0) and (file not in listSpecificTests)):
                # We defined a list of specific test to run
                # if testModule is not part of this list... skip it
                continue

            if file in listDirsToSkip:
                # this directory is from the framework, skip it
                continue

            testModules.append(file)
    return testModules

def initialization():
    global dirsrvGrpCreated, dirsrvUserCreated
    
    #
    # first thing to do to allow logging
    # False: because this is not the Nose wrapper
    #
    if logging_init(sys.argv[0], False) != 0:
        return 1
    console_init()

    #
    # misc.
    #
    dirutil.workaround_ticket47394()
    dirutil.selinuxCheckPortLabel()
    dirsrvGrpCreated, dirsrvUserCreated, rc = dirutil.check_dirsrv_user()
    if rc != 0:
        logging_display(CRITICAL, "Initialization failed")
        return 1
    
    return 0

def terminaison():
    global dirsrvGrpCreated, dirsrvUserCreated
    dirutil.clean_dirsrv_user(dirsrvGrpCreated, dirsrvUserCreated)
    #dirutil.clean_dirsrv_user(True, True)
    return 0



#for param in os.environ.keys():
#    print "%20s %s" % (param,os.environ[param])



# list the specific tests to run (e.g "ticket570")
listSpecificTests = []

# list the specific directory that are NOT tests
listDirsToSkip = ["testTemplates", "framework"]


# counters for test results statistics
startup_success = 0
run_success = 0
cleanup_success = 0


#initialization required before running the tests
if initialization() != 0:
    logging_display(CRITICAL, "Initialization failed. Stop the tests")
    quit()

# retrieve all the available tests
testModules = getTestModules(sys.argv[0])
nbTests = len(testModules)
console_display("Bugs fixes verification (%d bugs)" % nbTests)
for testModule in testModules:
    
    # import the module containing the test
    # "test_" added for nose
    test = import_module("test_" + testModule)

    # create an instance of the test. I was not able to call
    # outside of the module, the instance creation method
    # So I use a generic method 'create_test'
    test_object = test.create_object()
    if test_object.startup() == 0:
        startup_success += 1

        if test_object.run() == 0:
            run_success += 1

        if test_object.cleanup() == 0:
            cleanup_success += 1
    else:
        # run phase is not spawned in case of startup failure
        if test_object.cleanup() == 0:
            cleanup_success += 1

if nbTests > 0:
    console_display("\n\t Results:")
    console_display("\tstartup: %d%%" % (100*startup_success/len(testModules)))
    console_display("\trun    : %d%%" % (100*run_success/len(testModules)))
    console_display("\tcleanup: %d%%" % (100*cleanup_success/len(testModules)))

if terminaison() != 0:
    logging_display(CRITICAL, "Terminaison failed, please clean up...")
    quit()
