"""
Tests for L{txzmq.pubsub}.
"""
from twisted.trial import unittest

from txzmq.connection import ZmqEndpoint, ZmqEndpointType
from txzmq.factory import ZmqFactory
from txzmq.pubsub import ZmqPubConnection, ZmqSubConnection
from txzmq.test import _wait

from zmq.error import ZMQError


class ZmqTestSubConnection(ZmqSubConnection):
    def gotMessage(self, message, tag):
        if not hasattr(self, 'messages'):
            self.messages = []

        self.messages.append([tag, message])


def _detect_epgm():
    """
    Utility function to test for presence of epgm:// in zeromq.
    """
    import zmq

    context = zmq.Context()
    socket = zmq.Socket(context, zmq.constants.PUB)

    try:
        socket.bind("epgm://127.0.0.1;239.192.1.1:5557")

        return True
    except ZMQError:
        return False


class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.

    In ZeroMQ 2.x, subscription is handled on receiving side:
    incoming messages are simply filtered, that's why connection.subscribe
    works immediately.

    In ZeroMQ 3.x, subscription is handled on publisher side:
    subscriber sends message to the publisher and publisher adjusts
    filtering on its side. So connection.subscribe doesn't start filtering
    immediately, it takes some time for messages to pass through the channel.
    """

    def setUp(self):
        self.factory = ZmqFactory()
        ZmqPubConnection.allowLoopbackMulticast = True

    def tearDown(self):
        del ZmqPubConnection.allowLoopbackMulticast
        self.factory.shutdown()

    def test_send_recv(self):
        r = ZmqTestSubConnection(
            self.factory, ZmqEndpoint(ZmqEndpointType.bind, "ipc://test-sock"))
        s = ZmqPubConnection(
            self.factory, ZmqEndpoint(ZmqEndpointType.connect,
                                      "ipc://test-sock"))

        r.subscribe(b'tag')

        def publish(ignore):
            s.publish(b'xyz', b'different-tag')
            s.publish(b'abcd', b'tag1')
            s.publish(b'efgh', b'tag2')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [[b'tag1', b'abcd'], [b'tag2', b'efgh']]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.01).addCallback(publish) \
            .addCallback(lambda _: _wait(0.01)).addCallback(check)

    def test_send_recv_pgm(self):
        r = ZmqTestSubConnection(self.factory, ZmqEndpoint(
            ZmqEndpointType.bind, "epgm://127.0.0.1;239.192.1.1:5556"))

        s = ZmqPubConnection(self.factory, ZmqEndpoint(
            ZmqEndpointType.connect, "epgm://127.0.0.1;239.192.1.1:5556"))

        r.subscribe(b'tag')

        def publish(ignore):
            s.publish(b'xyz', b'different-tag')
            s.publish(b'abcd', b'tag1')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [[b'tag1', b'abcd']]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.2).addCallback(publish) \
            .addCallback(lambda _: _wait(0.2)).addCallback(check)

    def test_send_recv_multiple_endpoints(self):
        r = ZmqTestSubConnection(
            self.factory,
            ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:5556"))
        r.addEndpoints([ZmqEndpoint(ZmqEndpointType.bind,
                                    "inproc://endpoint")])
        s1 = ZmqPubConnection(
            self.factory,
            ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:5556"))
        s2 = ZmqPubConnection(
            self.factory,
            ZmqEndpoint(ZmqEndpointType.connect, "inproc://endpoint"))

        r.subscribe(b'')

        def publish(ignore):
            s1.publish(b'111', b'tag1')
            s2.publish(b'222', b'tag2')

        def check(ignore):
            result = getattr(r, 'messages', [])
            expected = [[b'tag1', b'111'], [b'tag2', b'222']]
            self.failUnlessEqual(
                sorted(result), expected, "Message should have been received")

        return _wait(0.1).addCallback(publish) \
            .addCallback(lambda _: _wait(0.1)).addCallback(check)

    if not _detect_epgm():
        test_send_recv_pgm.skip = "epgm:// not available"
