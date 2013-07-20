#!/bin/bash


CMD=$0
DIR=`dirname $CMD`
cd $DIR
export PYTHONPATH=/usr/lib64/python27.zip:/usr/lib64/python2.7:/usr/lib64/python2.7/plat-linux2:/usr/lib64/python2.7/lib-tk:/usr/lib64/python2.7/lib-old:/usr/lib64/python2.7/lib-dynload:/usr/lib64/python2.7/site-packages:/usr/lib64/python2.7/site-packages/PIL:/usr/lib64/python2.7/site-packages/gst-0.10:/usr/lib64/python2.7/site-packages/gtk-2.0:/usr/lib/python2.7/site-packages:/usr/lib/python2.7/site-packages/setuptools-0.6c11-py2.7.egg-info


for f in `find src/* -type d | egrep -v 'testTemplates' `
do
	ADDED_PATH=${ADDED_PATH}:${PWD}/$f
done
export PYTHONPATH=$PYTHONPATH:$ADDED_PATH:$PWD/src

python $PWD/src/dirsrvtests.py

