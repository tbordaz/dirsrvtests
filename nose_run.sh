#!/bin/bash


CMD=$0
DIR=`dirname $CMD`
cd $DIR
export PYTHONPATH=/usr/lib64/python27.zip:/usr/lib64/python2.7:/usr/lib64/python2.7/plat-linux2:/usr/lib64/python2.7/lib-tk:/usr/lib64/python2.7/lib-old:/usr/lib64/python2.7/lib-dynload:/usr/lib64/python2.7/site-packages:/usr/lib64/python2.7/site-packages/PIL:/usr/lib64/python2.7/site-packages/gst-0.10:/usr/lib64/python2.7/site-packages/gtk-2.0:/usr/lib/python2.7/site-packages:/usr/lib/python2.7/site-packages/setuptools-0.6c11-py2.7.egg-info

ADDED_PYTHONPATH=
NOSE_HOMEDIR="${PWD}"
ADDED_NOSEPATH="${NOSE_HOMEDIR}"
for f in `find src/* -type d | egrep -v 'testTemplates' `
do
	ADDED_PYTHONPATH=${ADDED_PYTHONPATH}:${PWD}/$f
    ADDED_NOSEPATH="${ADDED_NOSEPATH} ${PWD}/$f"
done
export PYTHONPATH=$PYTHONPATH:$ADDED_PYTHONPATH:$PWD/src


#nosetests -v $ADDED_NOSEPATH --collect-only
nosetests -v -s -w ${NOSE_HOMEDIR} $ADDED_NOSEPATH