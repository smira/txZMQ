"""
ZeroMQ Twisted factory which is controlling ZeroMQ context.
"""
from zmq.core.context import Context

from twisted.internet import reactor


class ZmqFactory(object):
    """
    I control individual ZeroMQ connections.

    Factory creates and destroys ZeroMQ context.

    @cvar reactor: reference to Twisted reactor used by all the connections
    @cvar ioThreads: number of IO threads ZeroMQ will be using for this context
    @type ioThreads: C{int}
    @cvar: lingerPeriod: number of milliseconds to block when closing socket
        (terminating context), when there are some messages pending to be sent
    @type lingerPeriod: C{int}

    @ivar connections: set of instanciated L{ZmqConnection}s
    @type connections: C{set}
    @ivar context: ZeroMQ context
    @type context: L{Context}
    """

    reactor = reactor
    ioThreads = 1
    lingerPeriod = 100

    def __init__(self):
        """
        Constructor.

        Create ZeroMQ context.
        """
        self.connections = set()
        self.context = Context(self.ioThreads)

    def __repr__(self):
        return "ZmqFactory()"

    def shutdown(self):
        """
        Shutdown factory.

        This is shutting down all created connections
        and terminating ZeroMQ context.
        """
        for connection in self.connections.copy():
            connection.shutdown()

        self.connections = None

        self.context.term()
        self.context = None

    def registerForShutdown(self):
        """
        Register factory to be automatically shut down
        on reactor shutdown.
        """
        reactor.addSystemEventTrigger('during', 'shutdown', self.shutdown)
