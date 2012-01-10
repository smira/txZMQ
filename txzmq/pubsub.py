"""
ZeroMQ PUB-SUB wrappers.
"""
from zmq.core import constants

from txzmq.connection import ZmqConnection


class ZmqPubConnection(ZmqConnection):
    """
    Publishing in broadcast manner.
    """
    socketType = constants.PUB

    def publish(self, message, tag=''):
        """
        Broadcast L{message} with specified L{tag}.

        @param message: message data
        @type message: C{str}
        @param tag: message tag
        @type tag: C{str}
        """
        self.send(tag + '\0' + message)


class ZmqSubConnection(ZmqConnection):
    """
    Subscribing to messages.
    """
    socketType = constants.SUB

    def subscribe(self, tag):
        """
        Subscribe to messages with specified tag (prefix).

        @param tag: message tag
        @type tag: C{str}
        """
        self.socket.setsockopt(constants.SUBSCRIBE, tag)

    def unsubscribe(self, tag):
        """
        Unsubscribe from messages with specified tag (prefix).

        @param tag: message tag
        @type tag: C{str}
        """
        self.socket.setsockopt(constants.UNSUBSCRIBE, tag)

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        if len(message) == 2:
            # compatibility receiving of tag as first part
            # of multi-part message
            self.gotMessage(message[1], message[0])
        else:
            self.gotMessage(*reversed(message[0].split('\0', 1)))

    def gotMessage(self, message, tag):
        """
        Called on incoming message recevied by subscriber

        @param message: message data
        @param tag: message tag
        """
        raise NotImplementedError(self)
