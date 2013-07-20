
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
    dirutil.workaround_ticket47394()
    dirutil.selinuxCheckPortLabel()
    dirsrvGrpCreated, dirsrvUserCreated, rc = dirutil.check_dirsrv_user()
    if rc != 0:
        print "Initialization failed"
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
    print "Initialization failed. Stop the tests"
    quit()

# retrieve all the available tests
testModules = getTestModules(sys.argv[0])
nbTests = len(testModules)
print "Bugs fixes verification (%d bugs)" % nbTests
for testModule in testModules:
    
    # import the module containing the test
    test = import_module(testModule)

    # create an instance of the test. I was not able to call
    # outside of the module, the instance creation method
    # So I use a generic method 'create_test'
    test_object = test.create_test()
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
    print "\n\n Results:"
    print "\tstartup: %d%%" % (100*startup_success/len(testModules))
    print "\trun    : %d%%" % (100*run_success/len(testModules))
    print "\tcleanup: %d%%" % (100*cleanup_success/len(testModules))

if terminaison() != 0:
    print "Terminaison failed, please clean up..."
    quit()
