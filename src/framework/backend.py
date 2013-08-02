
import decimal
from common import *
from dirsrvtests_log import *
import dirutil
import os
import re
import random
import string
import time

MOD_CACHEMEMSIZE_TEMPLATE = """
dn: $DN
changetype: modify
replace: $ATTR_CACHEMEMSIZE
$ATTR_CACHEMEMSIZE: $VALUE
"""

class BackendInstance():
    def __init__(self, hostname, port, suffix):
        self.hostname = hostname
        self.port = port
        self.suffix = suffix
        self.cachememsize = None
        self.backend = None

    def __getBackend(self):
        if self.backend is not None:
            return self.backend, 0

        # check we have a backend for that suffix
        filter = "(&(%s)(cn=%s))" % (SUFFIX_FILTER, self.suffix)
        stdout, stderr, rc = dirutil.ldapsearch(self.hostname, self.port, DIR_MANAGER_DN, COMMON_PASSWORD, MAPPING_TREE_DN, filter, SCOPE_ONE, ATTR_BACKEND)
        if rc != 0:
            logging_display(WARNING, "Fail to retrieve the backend suffixe %s" % filter)
            return None, 1
        self.backend = dirutil.findFirstValue(stdout, ATTR_BACKEND)
        return self.backend, 0




    def getCachememsize(self):
        if self.cachememsize is not None:
            return self.cachememsize, 0

        # check we have a backend for that suffix
        backendName, rc = self.__getBackend()
        if rc != 0:
            logging_display(WARNING, "Fail to retrieve the backend name")
            return self.cachememsize, 1

        filter = "(cn=%s)" % backendName
        stdout, stderr, rc = dirutil.ldapsearch(self.hostname, self.port, DIR_MANAGER_DN, COMMON_PASSWORD, LDBM_CONFIG, filter, SCOPE_ONE, ATTR_CACHEMEMSIZE)
        if rc != 0:
            logging_display(WARNING, "Fail to retrieve the backend suffixe %s" % filter)
            logging_display(WARNING, stdout)
            return 0, 1
        self.cachememsize = dirutil.findFirstValue(stdout, ATTR_CACHEMEMSIZE)
        return self.cachememsize, 0

    def setCachememsize(self, value):
        self.cachememsize = None

        # check we have a backend for that suffix
        backendName, rc = self.__getBackend()
        if rc != 0:
            logging_display(WARNING, "Fail to retrieve the backend name")
            return 1

        # get the backend instance DN
        filter = "(cn=%s)" % backendName
        stdout, stderr, rc = dirutil.ldapsearch(self.hostname, self.port, DIR_MANAGER_DN, COMMON_PASSWORD, LDBM_CONFIG, filter, SCOPE_ONE, ATTR_DN)
        if rc != 0:
            logging_display(WARNING, "Fail to retrieve the backend suffixe %s" % filter)
            logging_display(WARNING, stdout)
            return 1
        dn = dirutil.findFirstValue(stdout, ATTR_DN)

        # update its cachememsize
        sub_dict = dict(DN = dn,
                    VALUE = value,
                    ATTR_CACHEMEMSIZE = ATTR_CACHEMEMSIZE
                    )
        inf_fd = dirutil.mk_ldapmodify_file(MOD_CACHEMEMSIZE_TEMPLATE, sub_dict)
        rc = dirutil.ldapmodify(self.hostname, self.port, DIR_MANAGER_DN, COMMON_PASSWORD, inf_fd.name, "-c")
        if rc != 0:
            logging_display(WARNING, "Fail change the cachememsize to %d" % value)
            #logging_display(WARNING, stdout)
            return 1
        
        self.cachememsize = value
        return 0

    def get_importcommand(self):

        filter = "(cn=config)"
        stdout, stderr, rc = dirutil.ldapsearch(self.hostname, self.port, DIR_MANAGER_DN, COMMON_PASSWORD, CONFIG_DN, filter, SCOPE_BASE, ATTR_INSTANCEDIR)
        if rc != 0:
            logging_display(WARNING, "Fail retrieve the import command" % value)
            return None
        command = dirutil.findFirstValue(stdout, ATTR_INSTANCEDIR) + "/" + DIRSRV_CMD_LDIF2DB
        return command

    def get_backendname(self):
        backendName, rc = self.__getBackend()
        if rc != 0:
            logging_display(WARNING, "Fail to retrieve the backend name")
            return None
        return backendName

    def importBackendOffline(self, command, filename):
        backendName, rc = self.__getBackend()
        if rc != 0:
            logging_display(WARNING, "Fail to retrieve the backend name")
            return 1
        if not dirutil.file_exists(filename):
            logging_display(WARNING, "Fail to retrieve the backend name")
            return 1

        args = [CMD_SUDO, command, "-n", backendName, "-i", filename]
        stdout, stderr, rc = dirutil.run(args)
        if rc != 0:
            logging_display(WARNING, "Fail to import")
            logging_display(WARNING, stdout)
            return 1

        return 0
