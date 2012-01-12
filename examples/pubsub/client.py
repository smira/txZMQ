#!/usr/bin/env python

"""
Example txZMQ pubsub client:

    examples/pubsub/client.py --method=connect --endpoint=ipc:///tmp/sock

Be sure to also run the server example (in another terminal window):

    examples/pubsub/server.py --method=bind --endpoint=ipc:///tmp/sock

"""
import os
import sys

from twisted.internet import reactor

rootdir = os.path.realpath(os.path.join(
    os.path.dirname(sys.argv[0]), '..', '..'))
sys.path.insert(0, rootdir)
os.chdir(rootdir)

from examples.pubsub import base

from txzmq import ZmqEndpoint, ZmqFactory, ZmqSubConnection


(options, args) = base.getOptionsAndArgs()


class MySubscriber(ZmqSubConnection):

    def gotMessage(self, message, tag):
        print "Message received: %s (%s)" % (message, tag)


def onConnect(client):
    print "Connected!"
    client.subscribe("")


endpoint = ZmqEndpoint(options.method, options.endpoint)
client = MySubscriber(endpoint)
deferred = client.connect(ZmqFactory())
deferred.addCallback(onConnect)
reactor.run()
