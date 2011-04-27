"""
Tests for L{txZMQ.factory}.
"""

from twisted.trial import unittest

from txZMQ.factory import ZmqFactory


class ZmqFactoryTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.factory.Factory}.
    """

    def setUp(self):
        self.factory = ZmqFactory()

    def test_shutdown(self):
        self.factory.shutdown()
