.. txZMQ documentation master file, created by
   sphinx-quickstart on Mon Oct 29 00:35:01 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

txZMQ - ØMQ for Twisted
=======================

txZMQ allows to integrate easily `ØMQ <http://zeromq.org>`_ sockets into
Twisted event loop (reactor).

txZMQ supports both CPython and PyPy, and ØMQ library version 2.2.x or 3.2.x.

txZMQ introduces support for general 0MQ sockets by class :class:`txzmq.ZmqConnection`
that can do basic event loop integration, sending-receiving messages in
non-blocking manner, scatter-gather for multipart messages.

txZMQ uses ØMQ APIs to get file descriptor that is used to signal pending
actions from ØMQ library IO thread running in separate thread. This is used in
a custom file descriptor reader, which is then added to the Twisted reactor.

From this class, one may implement the various patterns defined by ØMQ. For
example, special descendants of the :class:`txzmq.ZmqConnection` class,
:class:`txzmq.ZmqPubConnection` and :class:`txzmq.ZmqSubConnection`, add special nice features for
PUB/SUB sockets.

Request/reply pattern is achieved via DEALER/ROUTER sockets and classes :class:`txzmq.ZmqREQConnection`,
:class:`txzmq.ZmqREPConnection`, which provide REQ-REP like semantics in asynchronous case.

Other socket types could be easily derived from :class:`txzmq.ZmqConnection`.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   examples
   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

