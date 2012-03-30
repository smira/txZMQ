Twisted bindings for 0MQ
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

* ØMQ library >= 2.1 (heavily tested with 2.1.10)

Python packages required:

* pyzmq (for CPython)
* pyzmq-ctypes (for PyPy)
* Twisted


Details
-------

txZMQ introduces support for general 0MQ sockets by class ``ZmqConnection``
that can do basic event loop integration, sending-receiving messages in
non-blocking manner, scatter-gather for multipart messages.

txZMQ uses ØMQ APIs to get file descriptor that is used to signal pending
actions from ØMQ library IO thread running in separate thread. This is used in
a custom file descriptor reader, which is then added to the Twisted reactor.

From this class, one may implement the various patterns defined by 0MQ. For
example, special descendants of the ``ZmqConnection`` class,
``ZmqPubConnection`` and ``ZmqSubConnection``, add special nice features for
PUB/SUB sockets.

Request/reply pattern is achieved via DEALER/ROUTER sockets and classes ``ZmqREQConnection``, 
``ZmqREPConection``, which provide REQ-REP like semantics in asynchronous case.

Other socket types could be easily derived from ``ZmqConnection``.

Upgrading from 0.3.x
--------------------

If you're upgrading from version 0.3.1 and earlier, please apply following
changes to your code:

* root package name was changed from ``txZMQ`` to ``txzmq``, adjust your
  imports accordingly;
* ``ZmqEndpointType.Connect`` has been renamed to ``ZmqEndpointType.connect``;
* ``ZmqEndpointType.Bind`` has been renamed to ``ZmqEndpointType.bind``;
* ``ZmqConnection.__init__`` has been changed to accept keyword arguments
  instead of list of endpoints; if you were using one endpoint, no changes
  are required; if using multiple endpoints, please look for ``add_endpoints``
  method.


Example
-------

Here is an example of using txZMQ::

    import sys

    from optparse import OptionParser

    from twisted.internet import reactor, defer

    parser = OptionParser("")
    parser.add_option("-m", "--method", dest="method", help="0MQ socket connection: bind|connect")
    parser.add_option("-e", "--endpoint", dest="endpoint", help="0MQ Endpoint")
    parser.add_option("-M", "--mode", dest="mode", help="Mode: publisher|subscriber")

    parser.set_defaults(method="connect", endpoint="epgm://eth1;239.0.5.3:10011")

    (options, args) = parser.parse_args()

    from txzmq import ZmqFactory, ZmqEndpoint, ZmqPubConnection, ZmqSubConnection
    import time

    zf = ZmqFactory()
    e = ZmqEndpoint(options.method, options.endpoint)

    if options.mode == "publisher":
        s = ZmqPubConnection(zf, e)

        def publish():
            data = str(time.time())
            print "publishing %r" % data
            s.publish(data)

            reactor.callLater(1, publish)

        publish()
    else:
        s = ZmqSubConnection(zf, e)
        s.subscribe("")

        def doPrint(*args):
            print "message received: %r" % (args, )

        s.gotMessage = doPrint

    reactor.run()

The same example is available in the source code. You can run it from the
checkout directory with the following commands (in two different terminals)::

    examples/pub_sub.py --method=bind --endpoint=ipc:///tmp/sock --mode=publisher

    examples/pub_sub.py --method=connect --endpoint=ipc:///tmp/sock --mode=subscriber

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
