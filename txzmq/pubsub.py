"""
ZeroMQ PUB-SUB wrappers.
"""
from zmq import constants

from txzmq.connection import ZmqConnection


class ZmqPubConnection(ZmqConnection):
    """
    Publishing in broadcast manner.
    """
    socketType = constants.PUB

    def publish(self, message, tag=''):
        """
        Publish `message` with specified `tag`.

        :param message: message data
        :type message: str
        :param tag: message tag
        :type tag: str
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
    Subscribing to messages published by publishers.

    Subclass this class and implement :meth:`gotMessage` to handle incoming
    messages.
    """
    socketType = constants.SUB

    def subscribe(self, tag):
        """
        Subscribe to messages with specified tag (prefix).

        Function may be called several times.

        :param tag: message tag
        :type tag: str
        """
        self.socket.set(constants.SUBSCRIBE, tag)

    def unsubscribe(self, tag):
        """
        Unsubscribe from messages with specified tag (prefix).

        Function may be called several times.

        :param tag: message tag
        :type tag: str
        """
        self.socket.set(constants.UNSUBSCRIBE, tag)

    def messageReceived(self, message):
        """
        Overridden from :class:`ZmqConnection` to process
        and unframe incoming messages.

        All parsed messages are passed to :meth:`gotMessage`.

        :param message: message data
        """
        self.gotMessage(*message)

    def gotMessage(self, *args):
        """
        Called on incoming message recevied by subscriber.

        Should be overridden to handle incoming messages.

        :param message: message data
        :param tag: message tag
        """
        raise NotImplementedError(self)
