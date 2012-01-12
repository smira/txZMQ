class ZmqError(Exception):
    """
    General txZMQ error.
    """


class ConnectionError(ZmqError):
    """
    Raised when there is an issue connecting to a server.
    """


class ListenError(ZmqError):
    """
    Raised when there is an issue connecting to a server.
    """


class SubscribingError(ZmqError):
    """
    Raised when there is an issue subscribing.
    """


class UnsubscribingError(ZmqError):
    """
    Raised when there is an issue unsubscribing.
    """


class PublishingError(ZmqError):
    """
    Raised when there is an issue publishing.
    """
