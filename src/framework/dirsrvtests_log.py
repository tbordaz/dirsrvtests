
from common import *
import logging
import os
import time

def logging_init(command):
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
    logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(name)-12s %(levelname)-8s : %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filename=logfile,
                    filemode='w'
                    )
    console_display(msg)
    console_display("\t- log file: %s" % logfile)
    
    return 0

def logging_display(level, msg):
    if level == CRITICAL:
        logging.critial(msg)
    elif level == WARNING:
        logging.warning(msg)
    elif level == INFO:
        logging.info(msg)
    else:
        logging.debug(msg)

def console_init():
    console = logging.StreamHandler()
    console.setLevel(logging.CRITICAL)
    formatter = logging.Formatter('    %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def console_display(msg):
    logging.critical(msg)

