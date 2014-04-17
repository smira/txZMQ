#!env/bin/python

"""
Trying simple REQ/REP interaction to verify that txZMQ works.

Required for Python3 until Trial stats working.
"""
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
    rep.reply(messageId, "REP: " + message)

rep.gotMessage = gotMessage
exitCode = 0


def start():
    def gotReply(reply):
        if reply != ["REP: REQ1"]:
            print "Unexpected reply: %r" % (reply, )

            global exitCode
            exitCode = 1
            reactor.crash()
            return

        print "OK"
        reactor.crash()

    req.sendMsg("REQ1").addCallback(gotReply)

reactor.callWhenRunning(reactor.callLater, 1, start)

reactor.run()
sys.exit(exitCode)
