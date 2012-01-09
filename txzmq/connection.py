"""
ZeroMQ connection.
"""

from collections import deque, namedtuple

from zmq.core.socket import Socket
from zmq.core import constants, error

from zope.interface import implements
from twisted.internet.interfaces import IReadDescriptor, IFileDescriptor
from twisted.python import log


class ZmqEndpointType(object):
    """
    Endpoint could be "bound" or "connected".
    """
    Bind = "bind"
    Connect = "connect"


ZmqEndpoint = namedtuple('ZmqEndpoint', ['type', 'address'])


class ZmqConnection(object):
    """
    Connection through ZeroMQ, wraps up ZeroMQ socket.

    @cvar socketType: socket type, from ZeroMQ
    @cvar allowLoopbackMulticast: is loopback multicast allowed?
    @type allowLoopbackMulticast: C{boolean}
    @cvar multicastRate: maximum allowed multicast rate, kbps
    @type multicastRate: C{int}
    @cvar highWaterMark: hard limit on the maximum number of outstanding messages
        0MQ shall queue in memory for any single peer
    @type highWaterMark: C{int}

    @ivar factory: ZeroMQ Twisted factory reference
    @type factory: L{ZmqFactory}
    @ivar socket: ZeroMQ Socket
    @type socket: L{Socket}
    @ivar endpoints: ZeroMQ addresses for connect/bind
    @type endpoints: C{list} of L{ZmqEndpoint}
    @ivar fd: file descriptor of zmq mailbox
    @type fd: C{int}
    @ivar queue: output message queue
    @type queue: C{deque}
    """
    implements(IReadDescriptor, IFileDescriptor)

    socketType = None
    allowLoopbackMulticast = False
    multicastRate = 100
    highWaterMark = 0
    identity = None

    def __init__(self, factory, *endpoints):
        """
        Constructor.

        @param factory: ZeroMQ Twisted factory
        @type factory: L{ZmqFactory}
        @param endpoints: ZeroMQ addresses for connect/bind
        @type endpoints: C{list} of L{ZmqEndpoint}
        """
        self.factory = factory
        self.endpoints = endpoints
        self.socket = Socket(factory.context, self.socketType)
        self.queue = deque()
        self.recv_parts = []

        self.fd = self.socket.getsockopt(constants.FD)
        self.socket.setsockopt(constants.LINGER, factory.lingerPeriod)
        self.socket.setsockopt(constants.MCAST_LOOP, int(self.allowLoopbackMulticast))
        self.socket.setsockopt(constants.RATE, self.multicastRate)
        self.socket.setsockopt(constants.HWM, self.highWaterMark)
        if self.identity is not None:
            self.socket.setsockopt(constants.IDENTITY, self.identity)

        self._connectOrBind()

        self.factory.connections.add(self)

        self.factory.reactor.addReader(self)

    def shutdown(self):
        """
        Shutdown connection and socket.
        """
        self.factory.reactor.removeReader(self)

        self.factory.connections.discard(self)

        self.socket.close()
        self.socket = None

        self.factory = None

    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.factory, self.endpoints)

    def fileno(self):
        """
        Part of L{IFileDescriptor}.

        @return: The platform-specified representation of a file descriptor
                 number.
        """
        return self.fd

    def connectionLost(self, reason):
        """
        Called when the connection was lost.

        Part of L{IFileDescriptor}.

        This is called when the connection on a selectable object has been
        lost.  It will be called whether the connection was closed explicitly,
        an exception occurred in an event handler, or the other end of the
        connection closed it first.

        @param reason: A failure instance indicating the reason why the
                       connection was lost.  L{error.ConnectionLost} and
                       L{error.ConnectionDone} are of special note, but the
                       failure may be of other classes as well.
        """
        log.err(reason, "Connection to ZeroMQ lost in %r" % (self))
        if self.factory:
            self.factory.reactor.removeReader(self)

    def _readMultipart(self):
        """
        Read multipart in non-blocking manner, returns with ready message
        or raising exception (in case of no more messages available).
        """
        while True:
            self.recv_parts.append(self.socket.recv(constants.NOBLOCK))
            if not self.socket.getsockopt(constants.RCVMORE):
                result, self.recv_parts = self.recv_parts, []

                return result

    def doRead(self):
        """
        Some data is available for reading on your descriptor.

        ZeroMQ is signalling that we should process some events.

        Part of L{IReadDescriptor}.
        """
        events = self.socket.getsockopt(constants.EVENTS)
        if (events & constants.POLLIN) == constants.POLLIN:
            while True:
                if self.factory is None:  # disconnected
                    return
                try:
                    message = self._readMultipart()
                except error.ZMQError as e:
                    if e.errno == constants.EAGAIN:
                        break

                    raise e

                log.callWithLogger(self, self.messageReceived, message)
        if (events & constants.POLLOUT) == constants.POLLOUT:
            self._startWriting()

    def _startWriting(self):
        """
        Start delivering messages from the queue.
        """
        while self.queue:
            try:
                self.socket.send(self.queue[0][1], constants.NOBLOCK | self.queue[0][0])
            except error.ZMQError as e:
                if e.errno == constants.EAGAIN:
                    break
                self.queue.popleft()
                raise e
            self.queue.popleft()

    def logPrefix(self):
        """
        Part of L{ILoggingContext}.

        @return: Prefix used during log formatting to indicate context.
        @rtype: C{str}
        """
        return 'ZMQ'

    def send(self, message):
        """
        Send message via ZeroMQ.

        @param message: message data
        """
        if not hasattr(message, '__iter__'):
            self.queue.append((0, message))
        else:
            self.queue.extend([(constants.SNDMORE, m) for m in message[:-1]])
            self.queue.append((0, message[-1]))

        # this is crazy hack: if we make such call, zeromq happily signals available events
        # on other connections
        self.socket.getsockopt(constants.EVENTS)

        self._startWriting()

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        raise NotImplementedError(self)

    def _connectOrBind(self):
        """
        Connect and/or bind socket to endpoints.
        """
        for endpoint in self.endpoints:
            if endpoint.type == ZmqEndpointType.Connect:
                self.socket.connect(endpoint.address)
            elif endpoint.type == ZmqEndpointType.Bind:
                self.socket.bind(endpoint.address)
            else:
                assert False, "Unknown endpoint type %r" % endpoint
