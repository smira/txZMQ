#!/usr/bin/env python

"""
Example txZMQ pubsub server:

    examples/pubsub/server.py --method=bind --endpoint=ipc:///tmp/sock

Be sure to also run the client example (in another terminal window):

    examples/pubsub/client.py --method=connect --endpoint=ipc:///tmp/sock

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
    print "Publishing %r ..." % data
    server.publish(data)
    print "Done."
    reactor.callLater(1, publish, server)


def onConnect(server):
    print "Connected!"
    publish(server)


endpoint = ZmqEndpoint(options.method, options.endpoint)
server = ZmqPubConnection(endpoint)
deferred = server.listen(ZmqFactory())
deferred.addCallback(onConnect)
reactor.run()
