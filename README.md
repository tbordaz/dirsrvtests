dirsrvtests
===========

Upstream tests for 389 Directory Server


This repo contains a test framework and the tests related to the 389 Directory Server fedora project (http://directory.fedoraproject.org/wiki/Main_Page).
The test framework and the tests are written in python.

The framework contains a set of DS topologies template: standalone, single master - single consumer, 2 masters - 2 consumers (fully meshed).
The tests are stored in subdirectories (e.g. ticket570).
To write a test, it is recommended to copy an existing test that use the required topology, then to replace the run() method with your own test case
