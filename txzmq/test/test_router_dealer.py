"""
Tests for L{txzmq.router_dealer}.
"""
from twisted.internet import defer, reactor
from twisted.trial import unittest

from txzmq.connection import ZmqEndpoint, ZmqEndpointType
from txzmq.factory import ZmqFactory
from txzmq.router_dealer import ZmqRouterConnection, ZmqDealerConnection


class ZmqTestRouterConnection(ZmqRouterConnection):
    message_count = 0

    def gotMessage(self, senderId, message):
        assert senderId == b'dealer'

        if message == b'stop':
            reactor.callLater(0, self.sendMsg, b'dealer', b'exit')
        else:
            self.message_count += 1
            self.sendMsg(b'dealer', b'event')
            for _ in range(2):
                reactor.callLater(0, self.sendMsg, b'dealer', b'event')


class ZmqTestDealerConnection(ZmqDealerConnection):
    message_count = 0

    def gotMessage(self, message):
        if message == b'event':
            self.message_count += 1
        elif message == b'exit':
            self.d.callback(None)
        else:
            assert False, "received unexpected message: %r" % (message,)


class ZmqRouterDealerTwoFactoryConnectionTestCase(unittest.TestCase):
    """
    Test case for L{txzmq.req_rep} with ROUTER/DEALER in two factories.
    """

    REQUEST_COUNT = 10000

    def setUp(self):
        self.factory1 = ZmqFactory()
        dealer_endpoint = ZmqEndpoint(ZmqEndpointType.connect, "ipc://#7")
        self.dealer = ZmqTestDealerConnection(self.factory1, dealer_endpoint,
                                              identity=b'dealer')
        self.dealer.d = defer.Deferred()

        self.factory2 = ZmqFactory()
        router_endpoint = ZmqEndpoint(ZmqEndpointType.bind, "ipc://#7")
        self.router = ZmqTestRouterConnection(self.factory2, router_endpoint,
                                              identity=b'router')

    def tearDown(self):
        self.factory2.shutdown()
        self.factory1.shutdown()

    def test_start(self):
        for _ in range(self.REQUEST_COUNT):
            reactor.callLater(0, self.dealer.sendMsg, b'req')
        reactor.callLater(0, self.dealer.sendMsg, b'stop')

        def checkResults(_):
            self.failUnlessEqual(self.dealer.message_count,
                                 3 * self.REQUEST_COUNT)
            self.failUnlessEqual(self.router.message_count, self.REQUEST_COUNT)

        return self.dealer.d.addCallback(checkResults)
