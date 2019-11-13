"""
Tests for L{txzmq.factory} automatic shutdown.
"""
from txzmq.factory import ZmqFactory

from twisted.internet.test.reactormixins import ReactorBuilder
from twisted.internet.interfaces import IReactorCore


class ZmqReactorShutdownTestCase(ReactorBuilder):
    """
    Test case for L{zmq.twisted.factory.Factory}
    automatic shutdown when the reactor is shutting down.
    """

    requiredInterfaces = (IReactorCore,)

    def test_reactor_and_factory_shutdown(self):
        reactor = self.buildReactor()

        def _test():
            factory = ZmqFactory()
            factory.reactor = reactor
            factory.registerForShutdown()
            factory.shutdown()
            reactor.stop()
        reactor.callWhenRunning(_test)
        reactor.run()

    def test_reactor_shutdown(self):
        reactor = self.buildReactor()

        def _test():
            factory = ZmqFactory()
            factory.reactor = reactor
            factory.registerForShutdown()
            reactor.stop()
        reactor.callWhenRunning(_test)
        reactor.run()


globals().update(ZmqReactorShutdownTestCase.makeTestCaseClasses())
