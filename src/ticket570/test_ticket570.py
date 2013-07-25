from dirsrvtests_log import *
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


ENTRY_DUMMY = """
dn: uid=$UID,$SUFFIX
cn: foo
cn: value1
cn: value2
sn: test
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetorgperson
uid: $UID
"""

MOD_ENTRY_DUMMY = """
dn: uid=$UID,$SUFFIX
changetype: modify
replace: cn
cn: $TESTVALUE
cn: newvalue1
cn: newvalue2
"""

runByNose=False

def create_object():
    t = Ticket570()
    return t

def test_ticket570():
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

    t = Ticket570()
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

class Ticket570():
    def __init__(self):
        self.bugid = int(dirutil.class2bugid(self))
        self.topology = None
        self.step = 0
        return


    def __log_msg(self, phase, msg):
        return "Test %6d [%-7s (%2d)]: %s" % (self.bugid, phase, self.__get_step(), msg)

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

        # create the master/consumer instance
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

        master = self.topology.get_master_instance()
        suffix = self.topology.get_suffix()
        uid = ''.join(random.choice(string.ascii_lowercase) for x in range(10))
        sub_dict = dict(UID = uid,
                    SUFFIX = suffix
                    )

        # create a test entry with 'cn' that
        # at least contains the value 'foo'
        inf_fd = dirutil.mk_ldapmodify_file(ENTRY_DUMMY, sub_dict)
        rc = dirutil.ldapmodify(self.topology.get_hostname(), master.get_port(), DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-a -c")
        dirutil.rm_ldapmodify_file(inf_fd)

        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "Fail to create the test entry"))
            return 1
        self.__next_step()


        #
        # now modify/replace 'cn' attribute with a set of values containing 'FOO'
        #
        sub_dict["TESTVALUE"] = "FOO"
        inf_fd = dirutil.mk_ldapmodify_file(MOD_ENTRY_DUMMY, sub_dict)
        rc = dirutil.ldapmodify(self.topology.get_hostname(), master.get_port(), DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-c")
        dirutil.rm_ldapmodify_file(inf_fd)

        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "FAIL: modify return %d" % rc))
            return 1
        self.__next_step()

        # check it contains 'FOO'
        stdout, stderr, rc = dirutil.ldapsearch(self.topology.get_hostname(), master.get_port(), DIR_MANAGER_DN, COMMON_PASSWORD, suffix, "uid=%s" % uid, SCOPE_SUB, "cn")
        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "FAIL: retrieve the entry return %d" % rc))
            return 1
        self.__next_step()

        found = 0
        for line in re.split('\n', stdout):
                if line.startswith("cn: FOO"):
                    found = 1
                    break
        if found == 0:
            logging_display(WARNING, self.__log_msg("run", "FAIL: entry does not contain FOO"))
            logging_display(WARNING, self.__log_msg("run", stdout))
            return 1
        self.__next_step()


        #
        # now modify/replace AGAIN 'cn' attribute with a set of values containing 'FOO' AGAIN
        #
        sub_dict["TESTVALUE"] = "FOO"
        inf_fd = dirutil.mk_ldapmodify_file(MOD_ENTRY_DUMMY, sub_dict)
        rc = dirutil.ldapmodify(self.topology.get_hostname(), master.get_port(), DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-c")
        dirutil.rm_ldapmodify_file(inf_fd)

        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "FAIL: modify return %d" % rc))
            return 1
        self.__next_step()

        # check it contains 'FOO'
        stdout, stderr, rc = dirutil.ldapsearch(self.topology.get_hostname(), master.get_port(), DIR_MANAGER_DN, COMMON_PASSWORD, suffix, "uid=%s" % uid, SCOPE_SUB, "cn")
        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "FAIL: retrieve the entry return %d" % rc))
            return 1
        self.__next_step()

        found = 0
        for line in re.split('\n', stdout):
                if line.startswith("cn: FOO"):
                    found = 1
                    break
        if found == 0:
            logging_display(WARNING, self.__log_msg("run", "FAIL: entry does not contain FOO"))
            logging_display(WARNING, self.__log_msg("run", stdout))
            return 1
        self.__next_step()



        #
        # now modify/replace 'cn' attribute with a set of values containing 'foo'
        #
        sub_dict["TESTVALUE"] = "foo"
        inf_fd = dirutil.mk_ldapmodify_file(MOD_ENTRY_DUMMY, sub_dict)
        rc = dirutil.ldapmodify(self.topology.get_hostname(), master.get_port(), DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-c")
        dirutil.rm_ldapmodify_file(inf_fd)

        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "FAIL: modify return %d" % rc))
            return 1
        self.__next_step()

        # check it contains 'FOO'
        stdout, stderr, rc = dirutil.ldapsearch(self.topology.get_hostname(), master.get_port(), DIR_MANAGER_DN, COMMON_PASSWORD, suffix, "uid=%s" % uid, SCOPE_SUB, "cn")
        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "FAIL: retrieve the entry return %d" % rc))
            return 1
        self.__next_step()

        found = 0
        for line in re.split('\n', stdout):
                if line.startswith("cn: foo"):
                    found = 1
                    break
        if found == 0:
            logging_display(WARNING, self.__log_msg("run", "FAIL: entry does not contain foo"))
            logging_display(WARNING, self.__log_msg("run", stdout))
            return 1
        self.__next_step()

        console_display(self.__log_msg("run", "PASS"))
        return 0