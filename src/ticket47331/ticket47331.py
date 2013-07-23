
from dirsrvtests_log import *
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

CN_TEST1 = "cn=test1"
CN_TEST2 = "cn=test2"
PASSWORD = "Secret12"

ADD_ENTRIES = """
dn: $CN_TEST1,$SUFFIX
objectClass: inetorgperson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: test
sn: test1
cn: test1
userPassword: $PASSWORD

dn: $CN_TEST2,$SUFFIX
objectClass: inetorgperson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: test
sn: test2
cn: test2
userPassword: $PASSWORD
"""

DEL_ANONYMOUS_ACI = """
dn: $SUFFIX
changetype: modify
delete: aci
aci: (targetattr!="userPassword")(version 3.0; acl "Enable anonymous access"; allow (read, search, compare) userdn="ldap:///anyone";)
"""

ADD_SELF_ACI = """
dn: $SUFFIX
changetype: modify
add: aci
aci: (targetattr="*")(version 3.0; acl "Allow self entry access"; allow (read,search,compare) userdn = "ldap:///self";)
"""

def create_test():
    t = Ticket47331()
    return t

class Ticket47331():

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
            logging_display(INFO, self.__log_msg("startup", "Instance already created"))
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

    def cleanup_force(self):
        self.__init_step()
        #fake initialization to allow removal of the instance
        self.instance = StandAloneDS("standalone", self.bugid)
        self.instance.create_instance(False)

        if self.instance.remove_instance() != 0:
            logging_display(WARNING, self.__log_msg("cleanup", "Fail to cleanup the instance"))
            return 1
        self.__next_step()

        console_display(self.__log_msg("cleanup", "PASS"))
        return 0
        self.__next_step()

    def run(self):
        self.__init_step()

        instance = self.instance

        sub_dict = dict(SUFFIX=instance.get_suffix(),
                CN_TEST1=CN_TEST1,
                CN_TEST2=CN_TEST2,
                PASSWORD=PASSWORD)
        inf_fd = dirutil.mk_ldapmodify_file(ADD_ENTRIES, sub_dict)
        rc = dirutil.ldapmodify(instance.get_hostname(), instance.get_normal_port(), instance.get_rootDN(), instance.get_rootDNPwd(), inf_fd.name, "-a -c")
        dirutil.rm_ldapmodify_file(inf_fd)
        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "Fail Add entries"))
            return 1
        self.__next_step()

        #
        # Delete the suffix anonymous aci
        inf_fd = dirutil.mk_ldapmodify_file(DEL_ANONYMOUS_ACI, sub_dict)
        rc = dirutil.ldapmodify(instance.get_hostname(), instance.get_normal_port(), instance.get_rootDN(), instance.get_rootDNPwd(), inf_fd.name, "-a -c")
        dirutil.rm_ldapmodify_file(inf_fd)
        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "Fail Del aci "))
            return 1
        self.__next_step()


        #
        # Add the self  aci
        inf_fd = dirutil.mk_ldapmodify_file(ADD_SELF_ACI, sub_dict)
        rc = dirutil.ldapmodify(instance.get_hostname(), instance.get_normal_port(), instance.get_rootDN(), instance.get_rootDNPwd(), inf_fd.name, "-a -c")
        dirutil.rm_ldapmodify_file(inf_fd)
        if rc != 0:
            logging_display(WARNING, self.__log_msg("run", "Fail ADD aci "))
            return 1
        self.__next_step()

        stdout,stderr, rc = dirutil.ldapsearch(instance.get_hostname(), instance.get_normal_port(), CN_TEST1 + "," + instance.get_suffix(), PASSWORD, instance.get_suffix(), "cn=test*", None, "dn")

        # Check the number of retrieved entries
        nb_entries=0
        for line in re.split('\n', stdout):
            if line.startswith("dn: "):
              nb_entries += 1
        if nb_entries != 1:
            logging_display(WARNING, self.__log_msg("run", "%s retrieved %d entries (1 expected)" % CN_TEST1, nb_entries))
            return 1
        self.__next_step()

        # Check that the retrieved entry is the one expected "dn: cn=test1,$SUFFIX"
        fail = False
        
        if fail:
            logging_display(WARNING, self.__log_msg("run", "Retrieved entry \"%s\" is not the expected (%s)" % retrieved_dn, expected_dn))
            return 1
        self.__next_step()


        #
        # Search the entries findable by test1
        #
        stdout,stderr, rc = dirutil.ldapsearch(instance.get_hostname(), instance.get_normal_port(), CN_TEST2 + "," + instance.get_suffix(), PASSWORD, instance.get_suffix(), "cn=test*", None, "dn")

        # Check the number of retrieved entries
        nb_entries=0
        for line in re.split('\n', stdout):
            if line.startswith("dn: "):
                nb_entries += 1
        if nb_entries != 1:
            logging_display(WARNING, self.__log_msg("run", "%s retrieved %d entries (1 expected)" % CN_TEST2, nb_entries))
            return 1
        self.__next_step()

        # Check that the retrieved entry is the one expected "dn: cn=test2,$SUFFIX"
        fail = False
        for line in re.split('\n', stdout):
            if line.startswith("dn: "):
                retrieved_dn = line[4:].lower()
                expected_dn = (CN_TEST2 + "," + instance.get_suffix()).lower()
                if retrieved_dn != expected_dn:
                    fail=True
                    break
        if fail:
            logging_display(WARNING, self.__log_msg("run", "Retrieved entry \"%s\" is not the expected (%s)" % retrieved_dn, expected_dn))
            return 1
        self.__next_step()

        console_display(self.__log_msg("run", "PASS"))
        return 0


