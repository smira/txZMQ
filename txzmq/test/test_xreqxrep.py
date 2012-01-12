"""
Tests for L{txzmq.xreq_xrep}.
"""
from twisted.internet import defer
from twisted.trial import unittest

from txzmq.connection import ZmqEndpoint, ZmqEndpointType
from txzmq.factory import ZmqFactory
from txzmq.test import _wait
from txzmq.xreq_xrep import ZmqXREPConnection, ZmqXREQConnection


class ZmqTestXREPConnection(ZmqXREPConnection):
    identity = 'service'

    def gotMessage(self, message_id, *message_parts):
        if not hasattr(self, 'messages'):
            self.messages = []
        self.messages.append([message_id, message_parts])
        self.reply(message_id, *message_parts)


class ZmqConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """

    def setUp(self):
        self.factory = ZmqFactory()
        ZmqXREQConnection.identity = 'client'
        self.r = ZmqTestXREPConnection(
                ZmqEndpoint(ZmqEndpointType.bind, "ipc://#3"))
        self.r.listen(self.factory)
        self.s = ZmqXREQConnection(
                ZmqEndpoint(ZmqEndpointType.connect, "ipc://#3"))
        self.s.connect(self.factory)
        self.count = 0

        def get_next_id():
            self.count += 1
            return 'msg_id_%d' % (self.count,)

        self.s._getNextId = get_next_id

    def tearDown(self):
        ZmqXREQConnection.identity = None
        self.factory.shutdown()

    def test_send_recv(self):
        self.s.sendMsg('aaa', 'aab')
        self.s.sendMsg('bbb')

        def check(ignore):
            result = getattr(self.r, 'messages', [])
            expected = [['msg_id_1', ('aaa', 'aab')], ['msg_id_2', ('bbb',)]]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.01).addCallback(check)

    def test_send_recv_reply(self):
        d = self.s.sendMsg('aaa')

        def check_response(response):
            self.assertEqual(response, ['aaa'])

        d.addCallback(check_response)
        return d

    def test_lot_send_recv_reply(self):
        deferreds = []
        for i in range(10):
            msg_id = "msg_id_%d" % (i,)
            d = self.s.sendMsg('aaa')

            def check_response(response, msg_id):
                self.assertEqual(response, ['aaa'])

            d.addCallback(check_response, msg_id)
            deferreds.append(d)
        return defer.DeferredList(deferreds)

    def xtest_cleanup_requests(self):
        """The request dict is cleanedup properly."""
        def check(ignore):
            self.assertEqual(self.s._requests, {})

        return self.s.sendMsg('aaa').addCallback(check)
