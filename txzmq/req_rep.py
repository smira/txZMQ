"""
ZeroMQ REQ-REP wrappers.
"""
from __future__ import unicode_literals

import uuid
import warnings

from zmq import constants

from twisted.internet import defer, reactor

from txzmq.connection import ZmqConnection


class ZmqRequestTimeoutError(Exception):
    """
    Request has been timed out.
    """


class ZmqREQConnection(ZmqConnection):
    """
    A Request ZeroMQ connection.

    This is implemented with an underlying DEALER socket, even though
    semantics are closer to REQ socket.

    Socket mimics request-reply behavior by sending each message with unique
    uuid and recording Deferred associated with the message. When reply comes,
    it uses that Deferred to pass response back to the caller.

    :var defaultRequestTimeout: default timeout for requests, disabled
        by default (seconds)
    :type defaultRequestTimeout: float
    """
    socketType = constants.DEALER
    defaultRequestTimeout = None

    # the number of new UUIDs to generate when the pool runs out of them
    UUID_POOL_GEN_SIZE = 5

    def __init__(self, *args, **kwargs):
        self._requests = {}
        self._uuids = []

        ZmqConnection.__init__(self, *args, **kwargs)

    def _getNextId(self):
        """
        Returns an unique id.

        By default, generates pool of UUID in increments
        of ``UUID_POOL_GEN_SIZE``. Could be overridden to
        provide custom ID generation.

        :return: generated unique "on the wire" message ID
        :rtype: str
        """
        if not self._uuids:
            for _ in range(self.UUID_POOL_GEN_SIZE):
                self._uuids.append(uuid.uuid4().bytes)
        return self._uuids.pop()

    def _releaseId(self, msgId):
        """
        Release message ID to the pool.

        @param msgId: message ID, no longer on the wire
        @type msgId: C{str}
        """
        self._uuids.append(msgId)
        if len(self._uuids) > 2 * self.UUID_POOL_GEN_SIZE:
            self._uuids[-self.UUID_POOL_GEN_SIZE:] = []

    def _cancel(self, msgId):
        """
        Cancel outstanding REQ, drop reply silently.

        @param msgId: message ID to cancel
        @type msgId: C{str}
        """
        _, canceller = self._requests.pop(msgId, (None, None))

        if canceller is not None and canceller.active():
            canceller.cancel()

    def _timeoutRequest(self, msgId):
        """
        Cancel timedout request.
        @param msgId: message ID to cancel
        @type msgId: C{str}
        """
        d, _ = self._requests.pop(msgId, (None, None))
        if not d.called:
            d.errback(ZmqRequestTimeoutError(msgId))

    def sendMsg(self, *messageParts, **kwargs):
        """
        Send request and deliver response back when available.

        :param messageParts: message data
        :type messageParts: tuple
        :param timeout: as keyword argument, timeout on request
        :type timeout: float
        :return: Deferred that will fire when response comes back
        """
        messageId = self._getNextId()
        d = defer.Deferred(canceller=lambda _: self._cancel(messageId))

        timeout = kwargs.pop('timeout', None)
        if timeout is None:
            timeout = self.defaultRequestTimeout
        assert len(kwargs) == 0, "Unsupported keyword argument"

        canceller = None
        if timeout is not None:
            canceller = reactor.callLater(timeout, self._timeoutRequest,
                                          messageId)

        self._requests[messageId] = (d, canceller)
        self.send([messageId, b''] + list(messageParts))
        return d

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        Dispatches message to back to the requestor.

        :param message: message data
        """
        msgId, msg = message[0], message[2:]
        self._releaseId(msgId)
        d, canceller = self._requests.pop(msgId, (None, None))

        if canceller is not None and canceller.active():
            canceller.cancel()

        if d is None:
            # reply came for timed out or cancelled request, drop it silently
            return

        d.callback(msg)


class ZmqREPConnection(ZmqConnection):
    """
    A Reply ZeroMQ connection.

    This is implemented with an underlying ROUTER socket, but the semantics
    are close to REP socket.
    """
    socketType = constants.ROUTER

    def __init__(self, *args, **kwargs):
        self._routingInfo = {}  # keep track of routing info

        ZmqConnection.__init__(self, *args, **kwargs)

    def reply(self, messageId, *messageParts):
        """
        Send reply to request with specified ``messageId``.

        :param messageId: message uuid
        :type messageId: str
        :param messageParts: message data
        :type messageParts: list
        """
        routingInfo = self._routingInfo.pop(messageId)
        self.send(routingInfo + [messageId, b''] + list(messageParts))

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        :param message: message data
        """
        i = message.index(b'')
        assert i > 0
        (routingInfo, msgId, payload) = (
            message[:i - 1], message[i - 1], message[i + 1:])
        msgParts = payload[0:]
        self._routingInfo[msgId] = routingInfo
        self.gotMessage(msgId, *msgParts)

    def gotMessage(self, messageId, *messageParts):
        """
        Called on incoming request.

        Override this method in subclass and reply using
        :meth:`reply` using the same ``messageId``.

        :param messageId: message uuid
        :type messageId: str
        :param messageParts: message data
        """
        raise NotImplementedError(self)


class ZmqXREPConnection(ZmqREPConnection):
    """
    Provided for backwards compatibility.

    Deprecated in favour of either ZmqREPConnection or ZmqROUTERConnection.

    """

    def __init__(self, factory, *endpoints):
        warnings.warn("ZmqXREPConnection is deprecated in favour of "
                      "either ZmqREPConnection or ZmqROUTERConnection",
                      DeprecationWarning)
        ZmqREPConnection.__init__(self, factory)
        self.addEndpoints(endpoints)


class ZmqXREQConnection(ZmqREQConnection):
    """
    Provided for backwards compatibility.

    Deprecated in favour of either ZmqREQConnection or ZmqDEALERConnection.

    """

    def __init__(self, factory, *endpoints):
        warnings.warn("ZmqXREQConnection is deprecated in favour of "
                      "either ZmqREQConnection or ZmqDEALERConnection",
                      DeprecationWarning)
        ZmqREQConnection.__init__(self, factory)
        self.addEndpoints(endpoints)
