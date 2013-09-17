#!/bin/bash


CMD=$0
DIR=`dirname $CMD`
cd $DIR
export PYTHONPATH=/usr/lib64/python27.zip:/usr/lib64/python2.7:/usr/lib64/python2.7/plat-linux2:/usr/lib64/python2.7/lib-tk:/usr/lib64/python2.7/lib-old:/usr/lib64/python2.7/lib-dynload:/usr/lib64/python2.7/site-packages:/usr/lib64/python2.7/site-packages/PIL:/usr/lib64/python2.7/site-packages/gst-0.10:/usr/lib64/python2.7/site-packages/gtk-2.0:/usr/lib/python2.7/site-packages:/usr/lib/python2.7/site-packages/setuptools-0.6c11-py2.7.egg-info

export PYTHONPATH=$PYTHONPATH:$ADDED_PYTHONPATH:$PWD/src:$PWD/src/framework

echo $PYTHONPATH
py.test  -s 
