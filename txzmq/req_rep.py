"""
ZeroMQ REQ-REP wrappers.
"""
import uuid
import warnings

from zmq.core import constants

from twisted.internet import defer

from txzmq.connection import ZmqConnection


class ZmqREQConnection(ZmqConnection):
    """
    A REQ connection.

    This is implemented with an underlying DEALER socket, even though
    semantics are closed to REQ socket.
    """
    socketType = constants.DEALER

    # the number of new UUIDs to generate when the pool runs out of them
    UUID_POOL_GEN_SIZE = 5

    def __init__(self, factory, endpoint=None):
        ZmqConnection.__init__(self, factory, endpoint)
        self._requests = {}
        self._uuids = []

    def _getNextId(self):
        """
        Returns an unique id.
        """
        if not self._uuids:
            for _ in range(self.UUID_POOL_GEN_SIZE):
                self._uuids.append(str(uuid.uuid4()))
        return self._uuids.pop()

    def sendMsg(self, *message_parts):
        """
        Send L{message} with specified L{tag}.

        @param message_parts: message data
        @type message: C{tuple}
        """
        d = defer.Deferred()
        message_id = self._getNextId()
        self._requests[message_id] = d
        self.send([message_id, ''] + list(message_parts))
        return d

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        msg_id, _, msg = message[0], message[1], message[2:]
        d = self._requests.pop(msg_id)
        d.callback(msg)

        self._uuids.append(msg_id)
        if len(self._uuids) > 2 * self.UUID_POOL_GEN_SIZE:
            self._uuids[-self.UUID_POOL_GEN_SIZE:] = []


class ZmqREPConnection(ZmqConnection):
    """
    A REP connection.

    This is implemented with an underlying ROUTER socket, but the semantics
    are close to REP socket.
    """
    socketType = constants.ROUTER

    def __init__(self, factory, endpoint=None):
        ZmqConnection.__init__(self, factory, endpoint)
        self._routing_info = {}  # keep track of routing info

    def reply(self, message_id, *message_parts):
        """
        Send L{message} with specified L{tag}.

        @param message_id: message uuid
        @type message_id: C{str}
        @param message: message data
        @type message: C{str}
        """
        routing_info = self._routing_info.pop(message_id)
        self.send(routing_info + [message_id, ''] + list(message_parts))

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        i = message.index('')
        assert i > 0
        (routing_info, msg_id, payload) = (
            message[:i - 1], message[i - 1], message[i + 1:])
        msg_parts = payload[0:]
        self._routing_info[msg_id] = routing_info
        self.gotMessage(msg_id, *msg_parts)

    def gotMessage(self, message_id, *message_parts):
        """
        Called on incoming message.

        @param message_parts: message data
        @param tag: message tag
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
        self.add_endpoints(endpoints)


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
        self.add_endpoints(endpoints)
