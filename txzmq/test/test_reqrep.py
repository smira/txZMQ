"""
Tests for L{txzmq.req_rep}.
"""
from twisted.internet import defer, reactor
from twisted.trial import unittest

from txzmq.connection import ZmqEndpoint, ZmqEndpointType
from txzmq.factory import ZmqFactory
from txzmq.test import _wait
from txzmq.req_rep import ZmqREPConnection, ZmqREQConnection, \
    ZmqRequestTimeoutError
from txzmq.compat import binary_string_type


class ZmqTestREPConnection(ZmqREPConnection):
    def gotMessage(self, messageId, *messageParts):
        if not hasattr(self, 'messages'):
            self.messages = []
        self.messages.append([messageId, messageParts])
        self.reply(messageId, *messageParts)


class ZmqSlowREPConnection(ZmqREPConnection):
    def gotMessage(self, messageId, *messageParts):
        reactor.callLater(0.1, self.reply, messageId, *messageParts)


class ZmqREQREPConnectionTestCase(unittest.TestCase):
    """
    Test case for L{zmq.req_rep.ZmqREPConnection}.
    """

    def setUp(self):
        self.factory = ZmqFactory()
        b = ZmqEndpoint(ZmqEndpointType.bind, "ipc://#3")
        self.r = ZmqTestREPConnection(self.factory, b)
        c = ZmqEndpoint(ZmqEndpointType.connect, "ipc://#3")
        self.s = ZmqREQConnection(self.factory, c, identity=b'client')

    def tearDown(self):
        self.factory.shutdown()

    def test_getNextId(self):
        self.failUnlessEqual([], self.s._uuids)
        id1 = self.s._getNextId()
        self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE - 1, len(self.s._uuids))
        self.failUnlessIsInstance(id1, binary_string_type)

        id2 = self.s._getNextId()
        self.failUnlessIsInstance(id2, binary_string_type)

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
            return b'msg_id_' + str(self.count).encode()

        self.s._getNextId = get_next_id

        self.s.sendMsg(b'aaa', b'aab')
        self.s.sendMsg(b'bbb')

        def check(ignore):
            result = getattr(self.r, 'messages', [])
            expected = [[b'msg_id_1', (b'aaa', b'aab')],
                        [b'msg_id_2', (b'bbb',)]]
            self.failUnlessEqual(
                result, expected, "Message should have been received")

        return _wait(0.01).addCallback(check)

    def test_send_recv_reply(self):
        d = self.s.sendMsg(b'aaa')

        def check_response(response):
            self.assertEqual(response, [b'aaa'])

        d.addCallback(check_response)
        return d

    def test_lot_send_recv_reply(self):
        deferreds = []
        for i in range(10):
            msg_id = "msg_id_%d" % (i,)
            d = self.s.sendMsg(b'aaa')

            def check_response(response, msg_id):
                self.assertEqual(response, [b'aaa'])

            d.addCallback(check_response, msg_id)
            deferreds.append(d)
        return defer.DeferredList(deferreds, fireOnOneErrback=True)

    def test_cleanup_requests(self):
        """The request dict is cleanedup properly."""
        def check(ignore):
            self.assertEqual(self.s._requests, {})
            self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE, len(self.s._uuids))

        return self.s.sendMsg(b'aaa').addCallback(check)

    def test_cancel(self):
        d = self.s.sendMsg(b'aaa')
        d.cancel()

        def check_requests(_):
            self.assertEqual(self.s._requests, {})
            self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE,
                                 len(self.s._uuids) + 1)

        return d.addCallbacks(lambda _: self.fail("Should have errored"),
                              lambda fail: fail.trap(
                              "twisted.internet.defer.CancelledError")) \
            .addCallback(check_requests) \
            .addCallback(lambda _: _wait(0.01))

    def test_cancel_with_timeout(self):
        d = self.s.sendMsg(b'aaa', timeout=10.0)
        d.cancel()

        def check_requests(_):
            self.assertEqual(self.s._requests, {})
            self.failUnlessEqual(self.s.UUID_POOL_GEN_SIZE,
                                 len(self.s._uuids) + 1)

        return d.addCallbacks(lambda _: self.fail("Should have errored"),
                              lambda fail: fail.trap(
                              "twisted.internet.defer.CancelledError")) \
            .addCallback(check_requests) \
            .addCallback(lambda _: _wait(0.01))

    def test_send_timeout_ok(self):
        return self.s.sendMsg(b'aaa', timeout=0.1).addCallback(
            lambda response: self.assertEquals(response, [b'aaa'])
        )

    def test_send_timeout_fail(self):
        b = ZmqEndpoint(ZmqEndpointType.bind, "ipc://#4")
        ZmqSlowREPConnection(self.factory, b)
        c = ZmqEndpoint(ZmqEndpointType.connect, "ipc://#4")
        s = ZmqREQConnection(self.factory, c, identity=b'client2')

        return s.sendMsg(b'aaa', timeout=0.05) \
            .addCallbacks(lambda _: self.fail("Should timeout"),
                          lambda fail: fail.trap(ZmqRequestTimeoutError)) \
            .addCallback(lambda _: _wait(0.1))


class ZmqReplyConnection(ZmqREPConnection):
    def messageReceived(self, message):
        if not hasattr(self, 'message_count'):
            self.message_count = 0

        if message[1] == b'stop':
            reactor.callLater(0, self.send, [b'master', b'exit'])
        else:
            self.message_count += 1
            self.send([b'master', b'event'])
            for _ in range(2):
                reactor.callLater(0, self.send, [b'master', b'event'])


class ZmqRequestConnection(ZmqREQConnection):
    def messageReceived(self, message):
        if not hasattr(self, 'message_count'):
            self.message_count = 0
        if message[0] == b'event':
            self.message_count += 1
        elif message[0] == b'exit':
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
        self.c1 = ZmqRequestConnection(self.factory1, c, identity=b'master')
        b = ZmqEndpoint(ZmqEndpointType.bind, "tcp://127.0.0.1:7859")
        self.c2 = ZmqReplyConnection(self.factory2, b, identity=b'slave')
        self.c1.d = defer.Deferred()

    def tearDown(self):
        self.factory2.shutdown()
        self.factory1.shutdown()

    def test_start(self):
        for _ in range(self.REQUEST_COUNT):
            reactor.callLater(0, self.c1.send, b'req')
        reactor.callLater(0, self.c1.send, b'stop')

        def checkResults(_):
            self.failUnlessEqual(self.c1.message_count, 3 * self.REQUEST_COUNT)
            self.failUnlessEqual(self.c2.message_count, self.REQUEST_COUNT)

        return self.c1.d.addCallback(checkResults)
