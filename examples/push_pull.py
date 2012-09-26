#!env/bin/python

"""
Example txzmq client.

    examples/push_pull.py --method=connect --endpoint=ipc:///tmp/sock
    --mode=push

    examples/push_pull.py --method=bind --endpoint=ipc:///tmp/sock
    --mode=pull
"""
import os
import socket
import sys
import time
from optparse import OptionParser

from twisted.internet import reactor, defer

rootdir = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0,rootdir)
os.chdir(rootdir)

from txzmq import ZmqEndpoint, ZmqFactory, ZmqPushConnection, ZmqPullConnection


parser = OptionParser("")
parser.add_option("-m", "--method", dest="method", help="0MQ socket connection: bind|connect")
parser.add_option("-e", "--endpoint", dest="endpoint", help="0MQ Endpoint")
parser.add_option("-M", "--mode", dest="mode", help="Mode: push|pull")
parser.set_defaults(method="connect", endpoint="ipc:///tmp/txzmq-pc-demo")

(options, args) = parser.parse_args()

zf = ZmqFactory()
e = ZmqEndpoint(options.method, options.endpoint)

if options.mode == "push":
    s = ZmqPushConnection(zf, e)

    def produce():
        data = [str(time.time()), socket.gethostname()]
        print "producing %r" % data
        s.push(data)

        reactor.callLater(1, produce)

    reactor.callWhenRunning(produce)
else:
    s = ZmqPullConnection(zf, e)

    def doPrint(message):
        print "consuming %r" % (message,)

    s.onPull = doPrint

reactor.run()
