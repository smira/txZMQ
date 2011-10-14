"""
Tests for L{txZMQ.xreq_xrep}.
"""
from twisted.trial import unittest
from twisted.internet import defer

from txZMQ.factory import ZmqFactory
from txZMQ.connection import ZmqEndpointType, ZmqEndpoint
from txZMQ.xreq_xrep import ZmqXREQConnection, ZmqXREPConnection
from txZMQ.test import _wait


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
        self.r = ZmqTestXREPConnection(self.factory,
                ZmqEndpoint(ZmqEndpointType.Bind, "ipc://#3"))
        self.s = ZmqXREQConnection(self.factory,
                ZmqEndpoint(ZmqEndpointType.Connect, "ipc://#3"))
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

        return _wait(0.01).addCallback(
                lambda _: self.failUnlessEqual(getattr(self.r, 'messages', []),
                    [['msg_id_1', ('aaa', 'aab')], ['msg_id_2', ('bbb',)]], "Message should have been received"))

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
        return self.s.sendMsg('aaa').addCallback(lambda _: self.assertEqual(self.s._requests, {}))
