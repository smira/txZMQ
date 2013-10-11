API Documentation
-----------------

.. automodule:: txzmq

Factory
^^^^^^^

All ØMQ connections should belong to some context, txZMQ wraps that into
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

Publish-Subscribe
^^^^^^^^^^^^^^^^^

For information on publish-subscribe in ØMQ, please read either 
`reference <http://api.zeromq.org/3-2:zmq-socket>`_
or `guide <http://zguide.zeromq.org/page:all>`_ (look for publish-subscribe).


.. note::

    These classes use PUB and SUB sockets from ØMQ. Special framing is implemented 
    to support sending tag: tag and message are separated by zero byte and sent over
    as single message. This is related to the way PUB-SUB works with PGM (UDP multicast):
    multipart messages are sent as multiple datagrams and they get mixed together if
    several publishers exist in the same broadcast domain.

.. autoclass:: txzmq.ZmqPubConnection
    :show-inheritance:
    :members:

.. autoclass:: txzmq.ZmqSubConnection
    :show-inheritance:
    :members:
    
Push-Pull
^^^^^^^^^

For information on push and pull sockets in ØMQ, please read either 
`reference <http://api.zeromq.org/3-2:zmq-socket>`_
or `guide <http://zguide.zeromq.org/page:all>`_ (look for pull or push).


.. autoclass:: txzmq.ZmqPushConnection
    :show-inheritance:
    :members:

.. autoclass:: txzmq.ZmqPullConnection
    :show-inheritance:
    :members:


Request-Reply and Router-Dealer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For information on these socket types in ØMQ, please read either 
`reference <http://api.zeromq.org/3-2:zmq-socket>`_
or `guide <http://zguide.zeromq.org/page:all>`_ (look for router/dealer and request/reply).


.. autoclass:: txzmq.ZmqREQConnection
    :show-inheritance:
    :members:

.. autoclass:: txzmq.ZmqREPConnection
    :show-inheritance:
    :members:

.. autoclass:: txzmq.ZmqRouterConnection
    :show-inheritance:
    :members:

.. autoclass:: txzmq.ZmqDealerConnection
    :show-inheritance:
    :members:


    


