"""
Tests for L{txzmq.connection}.
"""
from zmq.core import constants

from zope.interface import verify as ziv

from twisted.internet.interfaces import IFileDescriptor, IReadDescriptor
from twisted.trial import unittest

from txzmq import exceptions
from txzmq.connection import ZmqConnection, ZmqEndpoint, ZmqEndpointType
from txzmq.factory import ZmqFactory
from txzmq.test import _wait


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
        receiver = ZmqTestReceiver(
            self.factory, ZmqEndpoint(ZmqEndpointType.bind, "inproc://#1"))
        sender = ZmqTestSender(
            self.factory, ZmqEndpoint(ZmqEndpointType.connect, "inproc://#1"))
        # XXX perform some actual checks here

    def test_repr(self):
        expected = ("ZmqTestReceiver(ZmqFactory(), "
                    "(ZmqEndpoint(type='bind', address='inproc://#1'),))")
        r = ZmqTestReceiver(
            ZmqEndpoint(ZmqEndpointType.bind, "inproc://#1"))
        r.connect(self.factory)
        self.failUnlessEqual(expected, repr(r))

    def test_send_recv(self):
        r = ZmqTestReceiver(
            ZmqEndpoint(ZmqEndpointType.bind, "inproc://#1"))
        r.listen(self.factory)
        s = ZmqTestSender(
            ZmqEndpoint(ZmqEndpointType.connect, "inproc://#1"))
        s.connect(self.factory)

        s.send('abcd')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [['abcd']]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.01).addCallback(check)

    def test_send_recv_tcp(self):
        r = ZmqTestReceiver(
            ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5555"))
        r.listen(self.factory)
        s = ZmqTestSender(
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5555"))
        s.connect(self.factory)

        for i in xrange(100):
            s.send(str(i))

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = map(lambda i: [str(i)], xrange(100))
            self.failUnlessEqual(
                result, expected, "Messages should have been received")

        return _wait(0.01).addCallback(check)

    def test_send_recv_tcp_large(self):
        r = ZmqTestReceiver(
            ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5555"))
        r.listen(self.factory)
        s = ZmqTestSender(
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5555"))
        s.connect(self.factory)
        s.send(["0" * 10000, "1" * 10000])

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [["0" * 10000, "1" * 10000]]
            self.failUnlessEqual(
                result, expected, "Messages should have been received")

        return _wait(0.01).addCallback(check)

    def test_connect_success(self):

        def fakeConnectOrBind(ignored):
            self.factory.testMessage = "Fake success!"

        def check(ignored):
            self.assertEqual(self.factory.testMessage, "Fake success!")

        s = ZmqTestSender(
            ZmqEndpoint(ZmqEndpointType.connect, "inproc://#1"))
        self.patch(s, '_connectOrBind', fakeConnectOrBind)
        d = s.connect(self.factory)
        d.addCallback(check)
        return d

    def test_connect_fail(self):

        def fakeConnectOrBind(factory):
            raise Exception("ohnoz!")

        def check(error):
            self.assertEqual(str(error), "ohnoz!")

        s = ZmqTestSender(
            ZmqEndpoint(ZmqEndpointType.connect, "inproc://#1"))
        self.patch(s, '_connectOrBind', fakeConnectOrBind)
        failure = s.connect(self.factory)
        d = self.assertFailure(failure, exceptions.ConnectionError)
        d.addCallback(check)
        return d

    def test_listen_success(self):

        def fakeConnectOrBind(ignored):
            self.factory.testMessage = "Fake success!"

        def check(ignored):
            self.assertEqual(self.factory.testMessage, "Fake success!")

        s = ZmqTestReceiver(
            ZmqEndpoint(ZmqEndpointType.bind, "inproc://#1"))
        self.patch(s, '_connectOrBind', fakeConnectOrBind)
        d = s.listen(self.factory)
        d.addCallback(check)
        return d

    def test_listen_fail(self):

        def fakeConnectOrBind(factory):
            raise Exception("ohnoz!")

        def check(error):
            self.assertEqual(str(error), "ohnoz!")

        s = ZmqTestReceiver(
            ZmqEndpoint(ZmqEndpointType.bind, "inproc://#1"))
        self.patch(s, '_connectOrBind', fakeConnectOrBind)
        failure = s.listen(self.factory)
        d = self.assertFailure(failure, exceptions.ListenError)
        d.addCallback(check)
        return d
