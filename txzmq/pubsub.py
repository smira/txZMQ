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

    def publish(self, tag, message):
        """
        Broadcast L{message} with specified L{tag}.

        @param message: message data
        @type message: C{str}
        @param tag: message tag
        @type tag: C{str}
        """
        self.publish_multipart([tag, message])

    def publish_multipart(self, message):
        """
        Broadcast L{message} with specified L{tag}

        @param message: message data
        @type message: C{list}
        """

        self.send(message)


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
        self.socket_set(constants.SUBSCRIBE, tag)

    def unsubscribe(self, tag):
        """
        Unsubscribe from messages with specified tag (prefix).

        @param tag: message tag
        @type tag: C{str}
        """
        self.socket_set(constants.UNSUBSCRIBE, tag)

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        self.gotMessage(*message)

    def gotMessage(self, *args):
        """
        Called on incoming message recevied by subscriber

        @param message: message data
        @param tag: message tag
        """
        raise NotImplementedError(self)
