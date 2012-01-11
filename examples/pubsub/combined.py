#!/usr/bin/env python

"""
Example txZMQ client.

    examples/pubsub/combined.py --method=bind --endpoint=ipc:///tmp/sock --mode=publisher

    examples/pubsub/combined.py --method=connect --endpoint=ipc:///tmp/sock --mode=subscriber
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


class MySubscriber(ZmqSubConnection):

    def gotMessage(self, message, tag):
        print "message received: %s (%s)" % (message, tag)


endpoint = ZmqEndpoint(options.method, options.endpoint)
if options.mode == "publisher":
    server = ZmqPubConnection(endpoint)
    server.listen(ZmqFactory())
    publish(server)
elif options.mode == "subscriber":
    client = MySubscriber(endpoint)
    client.connect(ZmqFactory())
    client.subscribe("")
reactor.run()
