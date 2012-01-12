"""
Tests for L{txzmq.pubsub}.
"""
from zmq.core import constants, error
from zmq.core.socket import Socket

from twisted.trial import unittest

from txzmq import exceptions
from txzmq.connection import ZmqEndpoint, ZmqEndpointType
from txzmq.factory import ZmqFactory
from txzmq.pubsub import ZmqPubConnection, ZmqSubConnection
from txzmq.test import _wait


class ZmqTestSubConnection(ZmqSubConnection):

    def gotMessage(self, message, tag):
        if not hasattr(self, 'messages'):
            self.messages = []

        self.messages.append([tag, message])


class TweakedSocket(Socket):

    def __init__(self, *args, **kwargs):
        super(TweakedSocket, self).__init__(*args, **kwargs)
        self.factory = None


class TestSocketSuccess(TweakedSocket):

    def setSuccess(self):
        self.factory.testMessage = "Fake success!"

    def setsockopt(self, optInt, optVal):
        super(TestSocketSuccess, self).setsockopt(optInt, optVal or "")
        self.setSuccess()


class TestSocketFailure(TweakedSocket):

    def setFailure(self):
        raise Exception("ohnoz!")

    def setsockopt(self, optInt, optVal):
        super(TestSocketFailure, self).setsockopt(optInt, optVal or "")
        self.setFailure()


def createTweakedSocket(factory):
    socket = factory.socketClass(
        factory.context, factory.connection.socketType)
    factory.connection.fd = socket.getsockopt(constants.FD)
    socket.factory = factory
    return socket


class BaseTestCase(unittest.TestCase):
    """
    This should be subclassed by the other test cases in this module.
    """
    def setUp(self):
        self.factory = ZmqFactory()
        self.factory.testMessage = ""
        ZmqPubConnection.allowLoopbackMulticast = True

    def tearDown(self):
        del ZmqPubConnection.allowLoopbackMulticast
        self.factory.shutdown()


class ZmqSubConnectionTestCase(BaseTestCase):
    """
    Test case for L{txzmq.pubsub.ZmqSubConnection}.
    """
    def patchSocket(self, socketClass, connection):
        self.factory.socketClass = socketClass
        self.factory.connection = connection
        self.patch(
            self.factory.connection, '_createSocket', createTweakedSocket)

    def test_subscribe_success(self):

        def checkSubscribe(ignored):
            self.assertEqual(self.factory.testMessage, "Fake success!")

        def checkConnect(client):
            self.assertEqual(self.factory.testMessage, "")
            d = client.subscribe("tag")
            d.addCallback(checkSubscribe)

        s = ZmqSubConnection(
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5556"))
        self.patchSocket(TestSocketSuccess, s)
        d = s.connect(self.factory)
        d.addCallback(checkConnect)
        return d

    def test_subscribe_fail(self):

        def checkSubscribe(error):
            self.assertEqual(str(error), "exceptions.Exception: ohnoz!")

        def checkConnect(client):
            self.assertEqual(self.factory.testMessage, "")
            failure = client.subscribe("tag")
            d = self.assertFailure(failure, exceptions.SubscribingError)
            d.addCallback(checkSubscribe)

        s = ZmqSubConnection(
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5556"))
        self.patchSocket(TestSocketFailure, s)
        d = s.connect(self.factory)
        d.addCallback(checkConnect)
        return d

    def test_unsubscribe_success(self):

        def checkSubscribe(ignored):
            self.assertEqual(self.factory.testMessage, "Fake success!")

        def checkConnect(client):
            self.assertEqual(self.factory.testMessage, "")
            d = client.unsubscribe(None)
            d.addCallback(checkSubscribe)

        s = ZmqSubConnection(
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5556"))
        self.patchSocket(TestSocketSuccess, s)
        d = s.connect(self.factory)
        d.addCallback(checkConnect)
        return d

    def test_unsubscribe_fail(self):

        def checkUnsubscribe(error):
            self.assertEqual(str(error), "exceptions.Exception: ohnoz!")

        def checkConnect(client):
            self.assertEqual(self.factory.testMessage, "")
            failure = client.unsubscribe(None)
            d = self.assertFailure(failure, exceptions.UnsubscribingError)
            d.addCallback(checkUnsubscribe)

        s = ZmqSubConnection(
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5556"))
        self.patchSocket(TestSocketFailure, s)
        d = s.connect(self.factory)
        d.addCallback(checkConnect)
        return d


class ZmqPubConnectionTestCase(BaseTestCase):
    """
    Test case for L{txzmq.pubsub.ZmqPubConnection}.
    """
    def test_publish_success(self):

        def fakeSend(message):
            self.factory.testMessage = message

        def checkPublish(server):
            expected = "\x00a really special message"
            self.assertEqual(self.factory.testMessage, expected)

        def checkListen(server):
            self.assertEqual(self.factory.testMessage, "")
            d = server.publish("a really special message")
            d.addCallback(checkPublish)

        s = ZmqPubConnection(
            ZmqEndpoint(ZmqEndpointType.bind, "inproc://#1"))
        self.patch(s, 'send', fakeSend)
        d = s.listen(self.factory)
        d.addCallback(checkListen)
        return d

    def test_publish_fail(self):

        def fakeSend(factory):
            raise Exception("ohnoz!")

        def checkPublish(error):
            self.assertEqual(str(error), "exceptions.Exception: ohnoz!")

        def checkListen(server):
            self.assertEqual(self.factory.testMessage, "")
            failure = server.publish("a really special message")
            d = self.assertFailure(failure, exceptions.PublishingError)
            d.addCallback(checkPublish)

        s = ZmqPubConnection(
            ZmqEndpoint(ZmqEndpointType.bind, "inproc://#1"))
        self.patch(s, 'send', fakeSend)
        d = s.listen(self.factory)
        d.addCallback(checkListen)
        return d


class ZmqPubSubConnectionsTestCase(BaseTestCase):
    """
    Test case for mixed L{txzmq.pubsub.ZmqPubConnection} and
    L{txzmq.pubsub.ZmqSubConnection}.
    """
    def test_send_recv(self):
        r = ZmqTestSubConnection(
            ZmqEndpoint(ZmqEndpointType.bind, "ipc://test-sock"))
        r.listen(self.factory)
        s = ZmqPubConnection(
            ZmqEndpoint(ZmqEndpointType.connect, "ipc://test-sock"))
        s.connect(self.factory)

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
        r = ZmqTestSubConnection(ZmqEndpoint(
            ZmqEndpointType.bind, "epgm://127.0.0.1;239.192.1.1:5556"))
        r.listen(self.factory)
        s = ZmqPubConnection(ZmqEndpoint(
            ZmqEndpointType.connect, "epgm://127.0.0.1;239.192.1.1:5556"))
        s.connect(self.factory)

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
            ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5556"),
            ZmqEndpoint(ZmqEndpointType.bind, "inproc://endpoint"))
        r.listen(self.factory)
        s1 = ZmqPubConnection(
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5556"))
        s1.connect(self.factory)
        s2 = ZmqPubConnection(
            ZmqEndpoint(ZmqEndpointType.connect, "inproc://endpoint"))
        s2.connect(self.factory)

        r.subscribe('')
        s1.publish('111', 'tag1')
        s2.publish('222', 'tag2')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [['tag2', '222'], ['tag1', '111']]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.2).addCallback(check)
