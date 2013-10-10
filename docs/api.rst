API Documentation
-----------------

.. automodule:: txzmq

Factory
^^^^^^^

All ZeroMQ connections should belong to some context, txZMQ wraps that into
concept of factory that tracks all connections created and wraps context.

Factory could be used as an easy way to close all connections and clean
up Twisted reactor.

.. autoclass:: txzmq.ZmqFactory
    :members:

    .. automethod:: __init__(self)

Base Connection
^^^^^^^^^^^^^^^

:class:`ZmqConnection` isn't supposed to be used explicitly, it is base
for different socket types.

.. autoclass:: txzmq.ZmqEndpointType
    :members:

.. autoclass:: txzmq.ZmqEndpoint

.. autoclass:: txzmq.ZmqConnection
    :members:

    .. automethod:: __init__(self, factory, endpoint=None, identity=None)

