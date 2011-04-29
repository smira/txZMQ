"""
Tests for L{txZMQ.connection}.
"""

from twisted.trial import unittest
from twisted.internet.interfaces import IReadDescriptor, IFileDescriptor
from zope.interface import verify as ziv

from txZMQ.factory import ZmqFactory
from txZMQ.connection import ZmqConnection, ZmqEndpoint, ZmqEndpointType
from txZMQ.test import _wait
from zmq.core import constants


class ZmqTestSender(ZmqConnection):
    socketType = constants.PUSH


class ZmqTestReceiver(ZmqConnection):
    socketType = constants.PULL

    def messageReceived(self, message):
        if not hasattr(self, 'messages'):
            self.messages = []

        self.messages.append(message)


class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """

    def setUp(self):
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()

    def test_interfaces(self):
        ziv.verifyClass(IReadDescriptor, ZmqConnection)
        ziv.verifyClass(IFileDescriptor, ZmqConnection)

    def test_init(self):
        ZmqTestReceiver(self.factory, ZmqEndpoint(ZmqEndpointType.Bind, "inproc://#1"))
        ZmqTestSender(self.factory, ZmqEndpoint(ZmqEndpointType.Connect, "inproc://#1"))

    def test_repr(self):
        self.failUnlessEqual("ZmqTestReceiver(ZmqFactory(), (ZmqEndpoint(type='bind', address='inproc://#1'),))",
                repr(ZmqTestReceiver(self.factory, ZmqEndpoint(ZmqEndpointType.Bind, "inproc://#1"))))

    def test_send_recv(self):
        r = ZmqTestReceiver(self.factory, ZmqEndpoint(ZmqEndpointType.Bind, "inproc://#1"))
        s = ZmqTestSender(self.factory, ZmqEndpoint(ZmqEndpointType.Connect, "inproc://#1"))

        s.send('abcd')

        return _wait(0.01).addCallback(
                lambda _: self.failUnlessEqual(getattr(r, 'messages', []), [['abcd']], "Message should have been received"))

    def test_send_recv_tcp(self):
        r = ZmqTestReceiver(self.factory, ZmqEndpoint(ZmqEndpointType.Bind, "tcp://127.0.0.1:5555"))
        s = ZmqTestSender(self.factory, ZmqEndpoint(ZmqEndpointType.Connect, "tcp://127.0.0.1:5555"))

        for i in xrange(100):
            s.send(str(i))

        return _wait(0.01).addCallback(
                lambda _: self.failUnlessEqual(getattr(r, 'messages', []), map(lambda i: [str(i)], xrange(100)), "Messages should have been received"))

    def test_send_recv_tcp_large(self):
        r = ZmqTestReceiver(self.factory, ZmqEndpoint(ZmqEndpointType.Bind, "tcp://127.0.0.1:5555"))
        s = ZmqTestSender(self.factory, ZmqEndpoint(ZmqEndpointType.Connect, "tcp://127.0.0.1:5555"))

        s.send(["0" * 10000, "1" * 10000])

        return _wait(0.01).addCallback(
                lambda _: self.failUnlessEqual(getattr(r, 'messages', []), [["0" * 10000, "1" * 10000]], "Messages should have been received"))
