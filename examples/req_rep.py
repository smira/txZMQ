#!env/bin/python

"""
Example txzmq client.

    examples/req_rep.py --method=connect --endpoint=ipc:///tmp/req_rep_sock --mode=req

    examples/req_rep.py --method=bind --endpoint=ipc:///tmp/req_rep_sock --mode=rep
"""
import os
import sys
import time
import zmq
from optparse import OptionParser

from twisted.internet import reactor

rootdir = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, rootdir)
os.chdir(rootdir)

from txzmq import ZmqEndpoint, ZmqFactory, ZmqREQConnection, ZmqREPConnection, ZmqRequestTimeoutError


parser = OptionParser("")
parser.add_option("-m", "--method", dest="method", help="0MQ socket connection: bind|connect")
parser.add_option("-e", "--endpoint", dest="endpoint", help="0MQ Endpoint")
parser.add_option("-M", "--mode", dest="mode", help="Mode: req|rep")
parser.set_defaults(method="connect", endpoint="ipc:///tmp/txzmq-pc-demo")

(options, args) = parser.parse_args()

zf = ZmqFactory()
e = ZmqEndpoint(options.method, options.endpoint)

if options.mode == "req":
    s = ZmqREQConnection(zf, e)

    def produce():
        # data = [str(time.time()), socket.gethostname()]
        data = str(time.time())

        print "Requesting %r" % data
        try:
            d = s.sendMsg(data, timeout=0.95)

            def doPrint(reply):
                print("Got reply: %s" % (reply))

            def onTimeout(fail):
                fail.trap(ZmqRequestTimeoutError)
                print "Timeout on request, is reply server running?"

            d.addCallback(doPrint).addErrback(onTimeout)

        except zmq.error.Again:
            print "Skipping, no pull consumers..."

        reactor.callLater(1, produce)

    reactor.callWhenRunning(reactor.callLater, 1, produce)
else:
    s = ZmqREPConnection(zf, e)

    def doPrint(messageId, message):
        print "Replying to %s, %r" % (messageId, message)
        s.reply(messageId, "%s %r " % (messageId, message))

    s.gotMessage = doPrint

reactor.run()
