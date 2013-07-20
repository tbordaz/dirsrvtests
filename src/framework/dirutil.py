from common import *
import string
import re
import tempfile
import subprocess
import os
import stat
import copy
import urllib2
import socket
import decimal
import sys
import grp
import pwd

try:
    from subprocess import CalledProcessError
except ImportError:
    # Python 2.4 doesn't implement CalledProcessError
    class CalledProcessError(Exception):
        """This exception is raised when a process run by check_call() returns
        a non-zero exit status. The exit status will be stored in the
        returncode attribute."""
        def __init__(self, returncode, cmd):
            self.returncode = returncode
            self.cmd = cmd
        def __str__(self):
            return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)


LDAPMODIFY = "/bin/ldapmodify"
LDAPSEARCH = "/bin/ldapsearch"

def class2bugid(object):
    name = object.__class__.__name__
    idx = re.search("\d", name)
    if idx:
        bugid = name[idx.start()::]
        if decimal.Decimal(bugid):
              return bugid
    print 0

def template_str(txt, vars):
    val = string.Template(txt).substitute(vars)

    # eval() is a special string one can insert into a template to have the
    # Python interpreter evaluate the string. This is intended to allow
    # math to be performed in templates.
    pattern = re.compile('(eval\s*\(([^()]*)\))')
    val = pattern.sub(lambda x: str(eval(x.group(2))), val)

    return val

def write_tmp_file(txt):
    fd = tempfile.NamedTemporaryFile()
    fd.write(txt)
    fd.flush()
    #fd.close()
    return fd

def remove_tmp_file(fd):
    if file_exists(fd.name):
        try:
            fd.close()
            os.remove(fd.name)
            return 0
        except os.error, err:
                #onerror(os.remove, fd.name, sys.exc_info())
                return 1

def file_exists(filename):
    try:
        mode = os.stat(filename)[stat.ST_MODE]
        if stat.S_ISREG(mode):
            return True
        else:
            return False
    except:
        return False

def dir_exists(filename):
    try:
        mode = os.stat(filename)[stat.ST_MODE]
        if stat.S_ISDIR(mode):
            return True
        else:
            return False
    except:
        return False

def shell_quote(string):
    return "'" + string.replace("'", "'\\''") + "'"



def nolog_replace(string, nolog):
    """Replace occurences of strings given in `nolog` with XXXXXXXX"""
    for value in nolog:
        if not isinstance(value, basestring):
            continue

        quoted = urllib2.quote(value)
        shquoted = shell_quote(value)
        for nolog_value in (shquoted, value, quoted):
            string = string.replace(nolog_value, 'XXXXXXXX')
    return string



def run(args, stdin=None, raiseonerr=True,
        nolog=(), env=None, capture_output=True, cwd=None):
    """
    Execute a command and return stdin, stdout and the process return code.

    args is a list of arguments for the command

    stdin is used if you want to pass input to the command

    raiseonerr raises an exception if the return code is not zero

    nolog is a tuple of strings that shouldn't be logged, like passwords.
    Each tuple consists of a string to be replaced by XXXXXXXX.

    For example, the command ['/usr/bin/setpasswd', '--password', 'Secret123', 'someuser']

    We don't want to log the password so nolog would be set to:
    ('Secret123',)

    The resulting log output would be:

    /usr/bin/setpasswd --password XXXXXXXX someuser

    If an value isn't found in the list it is silently ignored.
    """
    p_in = None
    p_out = None
    p_err = None

    if isinstance(nolog, basestring):
        # We expect a tuple (or list, or other iterable) of nolog strings.
        # Passing just a single string is bad: strings are also, so this
        # would result in every individual character of that string being
        # replaced by XXXXXXXX.
        # This is a sanity check to prevent that.
        raise ValueError('nolog must be a tuple of strings.')

    if env is None:
        # copy default env
        env = copy.deepcopy(os.environ)
        env["PATH"] = "/bin:/sbin:/usr/bin:/usr/sbin"
    if stdin:
        p_in = subprocess.PIPE
    if capture_output:
        p_out = subprocess.PIPE
        p_err = subprocess.PIPE

    arg_string = nolog_replace(' '.join(args), nolog)
    #root_logger.debug('Starting external process')
    #root_logger.debug('args=%s' % arg_string)
    #print "starting args=%s" % arg_string

    try:
        p = subprocess.Popen(args, stdin=p_in, stdout=p_out, stderr=p_err,
                             close_fds=True, env=env, cwd=cwd)
        stdout,stderr = p.communicate(stdin)
        stdout,stderr = str(stdout), str(stderr)    # Make pylint happy
    except KeyboardInterrupt:
        #root_logger.debug('Process interrupted')
        print "Process interrupted"
        p.wait()
        raise
    except:
        #root_logger.debug('Process execution failed')
        print "Process execution failed"
        raise

    #root_logger.debug('Process finished, return code=%s', p.returncode)

    # The command and its output may include passwords that we don't want
    # to log. Replace those.
    if capture_output:
        stdout = nolog_replace(stdout, nolog)
        stderr = nolog_replace(stderr, nolog)
        #print stdout
        #print stderr
        #root_logger.debug('stdout=%s' % stdout)
        #root_logger.debug('stderr=%s' % stderr)

    if p.returncode != 0 and raiseonerr:
        raise CalledProcessError(p.returncode, arg_string)

    return (stdout, stderr, p.returncode)

def host_port_open(host, port, socket_type=socket.SOCK_STREAM, socket_timeout=None):
    for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket_type):
        af, socktype, proto, canonname, sa = res
        try:
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error:
                s = None
                continue

            if socket_timeout is not None:
                s.settimeout(socket_timeout)

            s.connect(sa)

            if socket_type == socket.SOCK_DGRAM:
                s.send('')
                s.recv(512)

            return True
        except socket.error, e:
            pass
        finally:
            if s:
                s.close()

    return False

def check_ports(normal, secure):
    """
    Check of Directory server ports are open.

    Returns a tuple with two booleans, one for unsecure port 389 and one for
    secure port 636. True means that the port is free, False means that the
    port is taken.
    """
    if normal is None:
        normal = 389
    if secure is None:
        secure = 636

    ds_unsecure = not host_port_open(None, normal)
    ds_secure = not host_port_open(None, secure)
    return (ds_unsecure, ds_secure)

def get_fqdn():
    fqdn = ""
    try:
        fqdn = socket.getfqdn()
    except:
        try:
            fqdn = socket.gethostname()
        except:
            fqdn = ""
    return fqdn

def mk_ldapmodify_file(cmd, dictionnary):
    inf_txt = template_str(cmd, dictionnary)
    #print inf_txt
    inf_fd = write_tmp_file(inf_txt)
    return inf_fd

def rm_ldapmodify_file(inf_fd):
    remove_tmp_file(inf_fd)

def ldapmodify(hostname=None, port=None, bind_dn=None, bind_dn_pwd=None, inputFile=None, flags=None, raiseErr=True):

    if inputFile is None:
        print "ldapmodify: Invalid input file"
        return 1

    if hostname is None:
        print "ldapmodify: Invalid host name"
        return 1

    if ((port is None) or (port <= 0) or (port > 60000)):
        print "ldapmodify: Invalid port number"
        return 1

    if bind_dn is None:
        #anonymous bind
        bind_dn = ""
        bind_dn_pwd = ""

    if file_exists(inputFile):

        # this is the basic command
        args = [LDAPMODIFY, "-h", hostname, "-p", str(port), "-D", str(bind_dn), "-w", str(bind_dn_pwd), "-f", inputFile]

        # Then add the optional flags
        for x in flags.split(" "):
            args.append(x)

        # do no catch error (False) but print stdout/stderr if command fails
        stdout, stderr, rc = run(args, None, False)
        if rc != 0:
            print stdout
            print stderr

        return rc
    else:
        print "ldapmodify: File not existing (%s)" % inputFile
        return 1

def ldapsearch(hostname=None, port=None, bind_dn=None, bind_dn_pwd=None, base=None, filter=None, scope=None, attributes=None, raiseErr=True):

    if hostname is None:
        print "ldapsearch: Invalid host name"
        return 1

    if ((port is None) or (port <= 0) or (port > 60000)):
        print "ldapsearch: Invalid port number"
        return 1

    if bind_dn is None:
        #anonymous bind
        bind_dn = ""
        bind_dn_pwd = ""

    if base is None:
        print "ldapsearch: Invalid base DN"
        return 1
    #if base[0] != '"':
    #    base = "\"%s\"" % base

    if filter is None:
        filter = "objectclass=*"
    #make it simple (no processing of \ or leading ' ')
    #if filter[0] != '"':
    #    filter = "\"%s\"" % filter

    if scope is None:
        scope = "subtree"

    if attributes is None:
        attributes = "*"


    # this is the basic command
    args = [LDAPSEARCH, "-LLL", "-h", hostname, "-p", str(port), "-D", str(bind_dn), "-w", str(bind_dn_pwd), "-b", base, "-s", scope, filter, attributes]


    # do no catch error (False) but print stdout/stderr if command fails
    stdout, stderr, rc = run(args, None, False)
    if rc != 0:
        print stdout
        print stderr

    return stdout, stderr, rc

def __selinuxPortInSet(port, set):
    inSet = False
    for value in re.split(',', set):
        if value.find('-') != -1:
            #this is a range defined in set
            v1, v2 = re.split('-', value)
            minValue = int(v1)
            maxValue = int(v2)
            if ((minValue <= port) and (port <= maxValue)):
                inSet = True
                break
        else:
            if (int(value) == port):
                inSet = True
                break
    return inSet


def selinuxCheckPortLabel():
    if not file_exists(CMD_SELINUX_SEMANAGE):
        return 1
    args = [CMD_SUDO, CMD_SELINUX_SEMANAGE, "port", "-l"]
    stdout, stderr, rc = run(args, None, False)
    if rc != 0:
        print "Fail to retrieve selinux ports labels (need to be 'root')"
        return 1
    found = 0
    for line in re.split('\n', stdout):
        if ((line.find(SELINUX_DIRSRV_LABEL) != -1) and line.find("tcp")):
            found = 1
            break
    if found == 1:
        #The label is found
        m = re.search('(?<=tcp)', line)
        set = line[m.end()::].replace(" ", "")
        port = DIRSRVTEST_MIN_PORT
        while port <= DIRSRVTEST_MAX_PORT:
            # check DIRSRV ports are present in the list
            if not __selinuxPortInSet(port, set):
                print "     - selinux: add %d in %s label" % (port, SELINUX_DIRSRV_LABEL)
                args = [CMD_SUDO, CMD_SELINUX_SEMANAGE, "port", "-a", "-t", SELINUX_DIRSRV_LABEL, "-p", "tcp", str(port)]
                stdout, stderr, rc = run(args, None, False)
                if rc != 0:
                    print stdout
                    print "Fail add the port in the label: skip"
            port += 1
    return


# it checks that the group/user exists
# else it creates them
# it returns (bool grpCreated, bool userCreated, rc)
def check_dirsrv_user():
    grpCreate  = False
    userCreate = False
    
    # check the group
    try:
        gp = grp.getgrnam(DS_GROUP)
        print "     - group %s exists" % DS_GROUP
    except KeyError:
        args = [CMD_SUDO, CMD_GRPADD, "-r", DS_GROUP]
        stdout, stderr, rc = run(args, None, False)
        if rc != 0:
            print stdout
            print stderr
            # neither group and user have been created
            return (grpCreate, userCreate, 1)

        grpCreate = True

    # check the user
    try:
        user = pwd.getpwnam(DS_USER)
        print "     - user %s exists" % DS_USER
    except KeyError:
        args = [CMD_SUDO, CMD_USERADD, "-g", DS_GROUP,
                        "-c", "DS System User",
                        "-d", "/var/lib/dirsrv",
                        "-s", "/sbin/nologin",
                        "-M", "-r", DS_USER]
        stdout, stderr, rc = run(args, None, False)
        if rc != 0:
            print stdout
            print stderr
            if grpCreate:
                # try to do some cleanup
                args = [CMD_SUDO, CMD_GRPDEL, DS_GROUP]
                stdout, stderr, rc = run(args, None, False)
                if rc != 0:
                    print stdout
                    print stderr
                    print "Fail to add the user %s AND to remove the added goup %s" % (DS_USER, DS_GROUP)
                    return (grpCreate, userCreate, 1)

            print "Fail to add the user %s" % (DS_USER)
            return (grpCreate, userCreate, 1)

        userCreate = True

    if grpCreate:
        print "     - group %s created" % DS_GROUP
    if userCreate:
        print "     - user %s created" % DS_USER
    return (grpCreate, userCreate, 0)



def clean_dirsrv_user(grpCreate, userCreate):
    # delete the user before the group
    if userCreate:
        args = [CMD_SUDO, CMD_USERDEL, DS_USER]
        stdout, stderr, rc = run(args, None, False)
        if rc != 0:
            print stdout
            print stderr
            print "Fail to remove the added user %s" % (DS_USER)
        else:
            print "     - user %s removed" % DS_USER

    if grpCreate:
        args = [CMD_SUDO, CMD_GRPDEL, DS_GROUP]
        stdout, stderr, rc = run(args, None, False)
        print "     - group %s removed" % DS_GROUP

    return


# workaround ticket 47394
# that prevent to create an instance for an other user
def workaround_ticket47394():
    if dir_exists(DIRSRV_LOCK_DIR):
        args = [ CMD_SUDO, CMD_CHMOD, "o+rwx", DIRSRV_LOCK_DIR]
        stdout, stderr, rc = run(args, None, False)
        if rc != 0:
            print stdout
            print stderr
            print "Fail change permission %s" % (DIRSRV_LOCK_DIR)
     
