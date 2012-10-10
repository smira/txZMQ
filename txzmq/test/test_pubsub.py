"""
Tests for L{txzmq.pubsub}.
"""
from twisted.trial import unittest

from txzmq.connection import ZmqEndpoint, ZmqEndpointType
from txzmq.factory import ZmqFactory
from txzmq.pubsub import ZmqPubConnection, ZmqSubConnection
from txzmq.test import _wait

import time


class ZmqTestSubConnection(ZmqSubConnection):
    def gotMessage(self, message, tag):
        if not hasattr(self, 'messages'):
            self.messages = []

        self.messages.append([tag, message])


class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """

    def setUp(self):
        self.factory = ZmqFactory()
        ZmqPubConnection.allowLoopbackMulticast = True

    def tearDown(self):
        del ZmqPubConnection.allowLoopbackMulticast
        self.factory.shutdown()

    def test_send_recv(self):
        # For unknown reasons, this only works with zeromq3 if the sub socket is
        # connecting and the pub socket is binding.  It works both ways with
        # zeromq2.
        r = ZmqTestSubConnection(
            self.factory, ZmqEndpoint(ZmqEndpointType.connect,
                                      "ipc://test-sock"))
        s = ZmqPubConnection(
            self.factory, ZmqEndpoint(ZmqEndpointType.bind,
                                      "ipc://test-sock"))

        r.subscribe('tag')
        time.sleep(0.5)
        s.publish('xyz', 'different-tag')
        s.publish('abcd', 'tag1')
        s.publish('efgh', 'tag2')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [['tag1', 'abcd'], ['tag2', 'efgh']]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.01).addCallback(check)

    def test_send_recv_multiple_endpoints(self):
        # For unknown reasons, this only works with zeromq3 if the sub socket is
        # connecting and the pub socket is binding.  It works both ways with
        # zeromq2.
        s1 = ZmqPubConnection(
            self.factory,
            ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5556"))
        s2 = ZmqPubConnection(
            self.factory,
            ZmqEndpoint(ZmqEndpointType.bind, "inproc://endpoint"))

        r = ZmqTestSubConnection(
            self.factory,
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5556"))
        r.addEndpoints([ZmqEndpoint(ZmqEndpointType.connect,
                                    "inproc://endpoint")])
        r.subscribe('')
        time.sleep(0.5)
        s1.publish('111', 'tag1')
        s2.publish('222', 'tag2')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [['tag1', '111'], ['tag2', '222']]
            self.failUnlessEqual(
                sorted(result), expected, "Message should have been received")

        return _wait(0.2).addCallback(check)
