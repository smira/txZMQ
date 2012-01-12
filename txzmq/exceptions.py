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
