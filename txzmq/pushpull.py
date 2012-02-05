"""
ZeroMQ PUSH-PULL wrappers.
"""
from zmq.core import constants

from txzmq.connection import ZmqConnection


class ZmqPushConnection(ZmqConnection):
    """
    Publishing in broadcast manner.
    """
    socketType = constants.PUSH

    def push(self, message):
        """
        Push a message L{message}.

        @param message: message data
        @type message: C{str}
        """
        self.send(message)


class ZmqPullConnection(ZmqConnection):
    """
    Pull messages from a socket
    """
    socketType = constants.PULL

    def messageReceived(self, message):
        """
        Called on incoming message from ZeroMQ.

        @param message: message data
        """
        self.onPull(message)

    def onPull(self, message):
        """
        Called on incoming message received by puller.

        @param message: message data
        """
        raise NotImplementedError(self)
