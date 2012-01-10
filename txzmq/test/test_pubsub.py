"""
Tests for L{txzmq.pubsub}.
"""
from twisted.trial import unittest

from txzmq.connection import ZmqEndpoint, ZmqEndpointType
from txzmq.factory import ZmqFactory
from txzmq.pubsub import ZmqPubConnection, ZmqSubConnection
from txzmq.test import _wait


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
        r = ZmqTestSubConnection(
            self.factory, ZmqEndpoint(ZmqEndpointType.Bind, "ipc://test-sock"))
        s = ZmqPubConnection(
            self.factory, ZmqEndpoint(ZmqEndpointType.Connect,
            "ipc://test-sock"))

        r.subscribe('tag')
        s.publish('xyz', 'different-tag')
        s.publish('abcd', 'tag1')
        s.publish('efgh', 'tag2')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [['tag1', 'abcd'], ['tag2', 'efgh']]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.01).addCallback(check)

    def test_send_recv_pgm(self):
        r = ZmqTestSubConnection(self.factory, ZmqEndpoint(
            ZmqEndpointType.Bind, "epgm://127.0.0.1;239.192.1.1:5556"))
        s = ZmqPubConnection(self.factory, ZmqEndpoint(
            ZmqEndpointType.Connect, "epgm://127.0.0.1;239.192.1.1:5556"))

        r.subscribe('tag')
        s.publish('xyz', 'different-tag')
        s.publish('abcd', 'tag1')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [['tag1', 'abcd']]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.2).addCallback(check)

    def test_send_recv_multiple_endpoints(self):
        r = ZmqTestSubConnection(
            self.factory,
            ZmqEndpoint(ZmqEndpointType.Bind, "tcp://127.0.0.1:5556"),
            ZmqEndpoint(ZmqEndpointType.Bind, "inproc://endpoint"))
        s1 = ZmqPubConnection(
            self.factory,
            ZmqEndpoint(ZmqEndpointType.Connect, "tcp://127.0.0.1:5556"))
        s2 = ZmqPubConnection(
            self.factory,
            ZmqEndpoint(ZmqEndpointType.Connect, "inproc://endpoint"))

        r.subscribe('')
        s1.publish('111', 'tag1')
        s2.publish('222', 'tag2')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [['tag2', '222'], ['tag1', '111']]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.2).addCallback(check)
