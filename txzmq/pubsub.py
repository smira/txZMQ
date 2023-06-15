"""
ZeroMQ PUB-SUB wrappers.
"""
from __future__ import unicode_literals

from zmq import constants

from txzmq.connection import ZmqConnection


class ZmqPubConnection(ZmqConnection):
    """
    Publishing in broadcast manner.
    """
    socketType = constants.PUB

    def publish(self, message, tag=b''):
        """
        Publish `message` with specified `tag`.

        :param message: message data
        :type message: str
        :param tag: message tag
        :type tag: str
        """
        if isinstance(tag, str):
            tag = tag.encode()
        if isinstance(message, str):
            message = message.encode()
        self.send(tag + self.topicSep + message)


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
        self.socket.setsockopt(constants.SUBSCRIBE, tag)

    def unsubscribe(self, tag):
        """
        Unsubscribe from messages with specified tag (prefix).

        Function may be called several times.

        :param tag: message tag
        :type tag: str
        """
        self.socket.setsockopt(constants.UNSUBSCRIBE, tag)

    def messageReceived(self, message):
        """
        Overridden from :class:`ZmqConnection` to process
        and unframe incoming messages.

        All parsed messages are passed to :meth:`gotMessage`.

        :param message: message data
        """
        if len(message) == 2:
            # compatibility receiving of tag as first part
            # of multi-part message
            self.gotMessage(message[1], message[0])
        else:
            self.gotMessage(*reversed(message[0].split(self.topicSep, 1)))

    def gotMessage(self, message, tag):
        """
        Called on incoming message received by subscriber.

        Should be overridden to handle incoming messages.

        :param message: message data
        :param tag: message tag
        """
        raise NotImplementedError(self)
