#!env/bin/python

"""
Trying simple REQ/REP interaction to verify that txZMQ works.

Required for Python3 until Trial stats working.
"""
from __future__ import print_function, unicode_literals

import os
import sys

from twisted.internet import reactor

rootdir = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
sys.path.insert(0, rootdir)
os.chdir(rootdir)

from txzmq import ZmqEndpoint, ZmqFactory, ZmqREQConnection, ZmqREPConnection

zf = ZmqFactory()
endpoint = "ipc:///tmp/txzmq-test"


req = ZmqREQConnection(zf, ZmqEndpoint("connect", endpoint))
rep = ZmqREPConnection(zf, ZmqEndpoint("bind", endpoint))


def gotMessage(messageId, message):
    rep.reply(messageId, b"REP: " + message)

rep.gotMessage = gotMessage
exitCode = 0


def start():
    def gotReply(reply):
        if reply != [b"REP: REQ1"]:
            print("Unexpected reply: %r" % (reply, ))

            global exitCode
            exitCode = 1
            req.shutdown()
            rep.shutdown()
            reactor.callLater(0, reactor.stop)
            return

        print("OK")
        req.shutdown()
        rep.shutdown()
        reactor.callLater(0, reactor.stop)

    req.sendMsg(b"REQ1").addCallback(gotReply)

reactor.callWhenRunning(reactor.callLater, 1, start)

reactor.run()
sys.exit(exitCode)
