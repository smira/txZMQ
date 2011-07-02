"""
ZeroMQ PUB-SUB wrappers.
"""

from twisted.internet import defer
from zmq.core import constants

from txZMQ.connection import ZmqConnection


class ZmqXREQConnection(ZmqConnection):
    """
    A XREQ connection.
    """
    socketType = constants.XREQ

    def __init__(self, factory, *endpoints):
        ZmqConnection.__init__(self, factory, *endpoints)
        self._requests = {}

    def get_next_id(self):
        """Returns an unique id."""
        raise NotImplementedError(self)

    def sendMsg(self, *message_parts):
        """
        Send L{message} with specified L{tag}.

        @param message_parts: message data
        @type message: C{tuple}
        """
        d = defer.Deferred()
        message_id = self.get_next_id()
        self._requests[message_id] = d
        message = [message_id, '']
        message.extend(message_parts)
        self.send(message)
        return d

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        msg_id, _, msg = message[0], message[1], message[2:]
        self._requests[msg_id].callback(msg)


class ZmqXREPConnection(ZmqConnection):
    """
    A XREP connection.
    """
    socketType = constants.XREP

    def __init__(self, factory, *endpoints):
        ZmqConnection.__init__(self, factory, *endpoints)
        self._routing_info = {} # keep track of routing info

    def reply(self, message_id, *message_parts):
        """
        Send L{message} with specified L{tag}.

        @param message_id: message uuid
        @type message_id: C{str}
        @param message: message data
        @type message: C{str}
        """
        routing_info = self._routing_info[message_id]
        msg = []
        msg.extend(routing_info)
        msg.append(message_id)
        msg.append('')
        msg.extend(message_parts)
        self.send(msg)

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        for i, msg in enumerate(message):
            if msg == '':
                break
        routing_info, msg_id, payload = message[:i-1], message[i-1], message[i+1:]
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
