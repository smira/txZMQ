"""
Tests for L{txzmq.factory} automatic shutdown.

The _z_ infix is used to have this test a last-called one.
"""
from twisted.trial import unittest

from txzmq.factory import ZmqFactory

from twisted.internet import reactor

class ZmqReactorShutdownTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.factory.Factory} automatic shutdown when the reactor is shutting down.
    """

    def setUp(self):
        self.factory = ZmqFactory()
        self.factory.registerForShutdown()
        self.factory.shutdown()

    def test_reactor_shutdown(self):
        reactor.stop()

