"""
Tests for L{txzmq.req_rep}.
"""
from twisted.internet import defer, reactor
from twisted.trial import unittest

from txzmq.connection import ZmqEndpoint, ZmqEndpointType
from txzmq.factory import ZmqFactory
from txzmq.test import _wait
from txzmq.req_rep import ZmqREPConnection, ZmqREQConnection


class ZmqTestREPConnection(ZmqREPConnection):
    def gotMessage(self, messageId, *messageParts):
        if not hasattr(self, 'messages'):
            self.messages = []
        self.messages.append([messageId, messageParts])
        self.reply(messageId, *messageParts)


class ZmqREQREPConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.req_rep.ZmqREPConnection}.
    """

    def setUp(self):
        self.factory = ZmqFactory()
        b = ZmqEndpoint(ZmqEndpointType.bind, "ipc://#3")
        self.r = ZmqTestREPConnection(self.factory, b)
        c = ZmqEndpoint(ZmqEndpointType.connect, "ipc://#3")
        self.s = ZmqREQConnection(self.factory, c, identity='client')

    def tearDown(self):
        self.factory.shutdown()

    def test_getNextId(self):
        self.failUnlessEqual([], self.s._uuids)
        id1 = self.s._getNextId()
        self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE - 1, len(self.s._uuids))
        self.failUnlessIsInstance(id1, str)

        id2 = self.s._getNextId()
        self.failUnlessIsInstance(id2, str)

        self.failIfEqual(id1, id2)

        ids = [self.s._getNextId() for _ in range(1000)]
        self.failUnlessEqual(len(ids), len(set(ids)))

    def test_releaseId(self):
        self.s._releaseId(self.s._getNextId())
        self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE, len(self.s._uuids))

    def test_send_recv(self):
        self.count = 0

        def get_next_id():
            self.count += 1
            return 'msg_id_%d' % (self.count,)

        self.s._getNextId = get_next_id

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
        return defer.DeferredList(deferreds, fireOnOneErrback=True)

    def test_cleanup_requests(self):
        """The request dict is cleanedup properly."""
        def check(ignore):
            self.assertEqual(self.s._requests, {})
            self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE, len(self.s._uuids))

        return self.s.sendMsg('aaa').addCallback(check)


class ZmqReplyConnection(ZmqREPConnection):
    def messageReceived(self, message):
        if not hasattr(self, 'message_count'):
            self.message_count = 0

        if message[1] == 'stop':
            reactor.callLater(0, self.send, ['master', 'exit'])
        else:
            self.message_count += 1
            self.send(['master', 'event'])
            for _ in xrange(2):
                reactor.callLater(0, self.send, ['master', 'event'])


class ZmqRequestConnection(ZmqREQConnection):
    def messageReceived(self, message):
        if not hasattr(self, 'message_count'):
            self.message_count = 0
        if message[0] == 'event':
            self.message_count += 1
        elif message[0] == 'exit':
            self.d.callback(None)
        else:
            assert False


class ZmqREQREPTwoFactoryConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.req_rep} with REQ/REP in two factories.
    """

    REQUEST_COUNT = 10000

    def setUp(self):
        self.factory1 = ZmqFactory()
        self.factory2 = ZmqFactory()
        c = ZmqEndpoint(ZmqEndpointType.connect, "tcp://127.0.0.1:7859")
        self.c1 = ZmqRequestConnection(self.factory1, c, identity='master')
        b = ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:7859")
        self.c2 = ZmqReplyConnection(self.factory2, b, identity='slave')
        self.c1.d = defer.Deferred()

    def tearDown(self):
        self.factory2.shutdown()
        self.factory1.shutdown()

    def test_start(self):
        for _ in xrange(self.REQUEST_COUNT):
            reactor.callLater(0, self.c1.send, 'req')
        reactor.callLater(0, self.c1.send, 'stop')

        def checkResults(_):
            self.failUnlessEqual(self.c1.message_count, 3 * self.REQUEST_COUNT)
            self.failUnlessEqual(self.c2.message_count, self.REQUEST_COUNT)

        return self.c1.d.addCallback(checkResults)
