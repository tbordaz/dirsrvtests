#
# This module is specific to nose framework
#
import os.path

import common
import UserString
import string

from standAloneDS import *
import replication
import dirutil
import shutil
import pwd
import sys, getopt
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

#
# this module will use the dirsrvtests_log under framework
#
ADDED_PATH = os.path.abspath(os.path.dirname(__file__)) + "/framework"
sys.path = sys.path + [ADDED_PATH]
#print sys.path

#
# Flag for user/group dirsrv/dirsrv creation
# Not really usefull with nose, because there is no 'final' method to do cleanup
dirsrvUserCreated = False
dirsrvGrpCreated = False

def initialization():
    global dirsrvGrpCreated, dirsrvUserCreated

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



#
# this is the
def test_dirsrvtests():
    rc = initialization()
    if (rc != 0):
        logging_display(CRITICAL, "Initialization failed. Stop the tests")
        assert (rc == 0)
        