
from common import *
import logging
import os
import time

logFileForNose=None

def logging_init(command, nose):
    global logFileForNose

    #
    # Check the log dir exists
    dirsrvtestsLog = "%s/../logs" % os.path.dirname(command)
    if not os.path.isdir(dirsrvtestsLog):
        msg = "\t- %s created" % dirsrvtestsLog
        try:
            os.makedirs(dirsrvtestsLog)
        except KeyError:
            print "Fail to create logging directory %s" % dirsrvtestsLog
            return 1
    else:
        msg = "\t- %s exists" % dirsrvtestsLog

    #
    # Then record the log file
    #
    logfile = "%s/log.%s" % (dirsrvtestsLog , time.strftime("%m_%d_%Y_%H_%M_%S"))
    if nose:
        logFileForNose = open(logfile, 'w')
    else:
        logFileForNose = None
        logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)-8s : %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filename=logfile,
                    filemode='w'
                    )
    console_display(msg)
    console_display("\t- log file: %s" % logfile)
    
    return 0

def logging_display(level, msg):
    global logFileForNose

    # in case of None, write directly on the log file
    if logFileForNose is not None:
        if level == CRITICAL:
            newmsg = "CRITICAL : %s" % msg
        elif level == WARNING:
            newmsg = "WARNING  : %s" % msg
        elif level == INFO:
            newmsg = "INFO     : %s" % msg
        else:
            newmsg = "DEBUG    : %s" % msg
        logFileForNose.write(newmsg + '\n')
    else:
        # else rely on the standard logging mechanism
        if level == CRITICAL:
            logging.critial(msg)
        elif level == WARNING:
            logging.warning(msg)
        elif level == INFO:
            logging.info(msg)
        else:
            logging.debug(msg)

def console_init():
    global logFileForNose

    if logFileForNose is None:
        console = logging.StreamHandler()
        console.setLevel(logging.CRITICAL)
        formatter = logging.Formatter('    %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

def console_display(msg):
    global logFileForNose

    if logFileForNose is not None:
        newmsg = "CONSOLE  : %s" % msg
        logFileForNose.write(newmsg + '\n')
    else:
        logging.critical(msg)

