Twisted bindings for ØMQ
========================

.. contents::

Introduction
------------

txZMQ allows to integrate easily `ØMQ <http://zeromq.org>`_ sockets into
Twisted event loop (reactor).

txZMQ supports both CPython and PyPy.


Requirements
------------

Non-Python library required:

* ØMQ library >= 2.1 (heavily tested with 2.1.4)

Python packages required:

* pyzmq (for CPython)
* pyzmq-ctypes (for PyPy)
* Twisted


Details
-------

txZMQ introduces support for general ØMQ sockets by class ``ZmqConnection``
that can do basic event loop integration, sending-receiving messages in
non-blocking manner, scatter-gather for multipart messages.

txZMQ uses ØMQ APIs to get file descriptor that is used to signal pending
actions from ØMQ library IO thread running in separate thread. This is used in
a custom file descriptor reader, which is then added to the Twisted reactor.

From this class, one may implement the various patterns defined by ØMQ. For
example, special descendants of the ``ZmqConnection`` class,
``ZmqPubConnection`` and ``ZmqSubConnection``, add special nice features for
PUB/SUB sockets.

Request/reply pattern is achieved via XREQ/XREP sockets and classes ``ZmqXREQConnection``, 
``ZmqXREPConection``.

Other socket types could be easily derived from ``ZmqConnection``.


Example
-------

Here is an example of creating a txZMQ server::

    from txzmq import ZmqEndpoint, ZmqFactory, ZmqPubConnection

    def publish(server):
        data = str(time.time())
        print "Publishing %r ..." % data
        server.publish(data)
        print "Done."
        reactor.callLater(1, publish, server)

    def onConnect(server):
        print "Connected!"
        publish(server)

    endpoint = ZmqEndpoint("bind", "ipc:///tmp/sock")
    server = ZmqPubConnection(endpoint)
    deferred = server.listen(ZmqFactory())
    deferred.addCallback(onConnect)
    reactor.run()

Here is an example of creating a txZMQ client::

    from txzmq import ZmqEndpoint, ZmqFactory, ZmqPubConnection

    class MySubscriber(ZmqSubConnection):

        def gotMessage(self, message, tag):
            print "Message received: %s (%s)" % (message, tag)

    def onConnect(client):
        print "Connected!"
        client.subscribe("")

    endpoint = ZmqEndpoint("connect", "ipc:///tmp/sock")
    client = MySubscriber(endpoint)
    deferred = client.connect(ZmqFactory())
    deferred.addCallback(onConnect)
    reactor.run()

Examples similar to this are available in the source code. You can run them
from the command line with passed options. Be sure to read the comments at the
beginning of the example files for usage information.


Hacking
-------

Source code for txZMQ is available at `github <https://github.com/smira/txZMQ>`_;
forks and pull requests are welcome.

To start hacking, fork at github and clone to your working directory. To use
the Makefile (for running unit tests, checking for PEP8 compliance and running
pyflakes), you will want to have ``virtualenv`` installed (it includes a
``pip`` installation).

Create a branch, add some unit tests, write your code, check it and test it!
Some useful make targets are:

* ``make env``
* ``make check``
* ``make test``

If you don't have an environment set up, a new one will be created for you in
``./env``. Additionally, txZMQ will be installed as well as required
development libs.
