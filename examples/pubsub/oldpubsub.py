#!/usr/bin/env python

"""
Example txZMQ client.

    examples/pubsub/oldpubsub.py --method=bind --endpoint=ipc:///tmp/sock --mode=publisher

    examples/pubsub/oldpubsub.py --method=connect --endpoint=ipc:///tmp/sock --mode=subscriber
"""
import os
import sys
import time
from optparse import OptionParser

from twisted.internet import reactor, defer

rootdir = os.path.realpath(os.path.join(
    os.path.dirname(sys.argv[0]), '..', '..'))
sys.path.insert(0, rootdir)
os.chdir(rootdir)

from examples.pubsub import base

from txzmq import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection


(options, args) = base.getOptionsAndArgs()

def publish(server):
    data = str(time.time())
    print "publishing %r" % data
    server.publish(data)
    reactor.callLater(1, publish, server)

def doPrint(*args):
    print "message received: %r" % (args, )

zf = ZmqFactory()
e = ZmqEndpoint(options.method, options.endpoint)
if options.mode == "publisher":
    server = ZmqPubConnection(e)
    server.listen(zf)
    publish(server)
elif options.mode == "subscriber":
    client = ZmqSubConnection(e)
    client.connect(zf)
    client.subscribe("")
    client.gotMessage = doPrint
reactor.run()
