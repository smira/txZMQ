Twisted bindings for ZeroMQ
===========================

txZMQ allows to integrate easily `ZeroMQ <http://zeromq.org>`_ sockets into
Twisted event loop (reactor).

Supports CPython and PyPy.

Requirements:

* ZeroMQ library >= 2.1 (heavily tested with 2.1.4)

Python packages required:

* pyzmq (for CPython)
* pyzmq-ctypes (for PyPy)
* Twisted

txZMQ introduces support for general ZeroMQ sockets by class ``ZmqConnection``
that can do basic event loop integration, sending-receiving messages in
non-blocking manner, scatter-gather for multipart messages.

Special descendants of that class, ``ZmqPubConnection`` and ``ZmqSubConnection``
add special nice features for PUB/SUB sockets.

Request/reply pattern is achieved via XREQ/XREP sockets and classes ``ZmqXREQConnection``, 
``ZmqXREPConection`` (by verterok).

Other socket types could be easily derived from ``ZmqConnection``.

Example::

    import sys

    from optparse import OptionParser

    from twisted.internet import reactor, defer

    parser = OptionParser("")
    parser.add_option("-m", "--method", dest="method", help="0MQ socket connection: bind|connect")
    parser.add_option("-e", "--endpoint", dest="endpoint", help="0MQ Endpoint")
    parser.add_option("-M", "--mode", dest="mode", help="Mode: publisher|subscriber")

    parser.set_defaults(method="connect", endpoint="epgm://eth1;239.0.5.3:10011")

    (options, args) = parser.parse_args()

    from txZMQ import ZmqFactory, ZmqEndpoint, ZmqPubConnection, ZmqSubConnection
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

The same example is available in source code::

    examples/pub_sub.py --method=bind --endpoint=ipc:///tmp/sock --mode=publisher

    examples/pub_sub.py --method=connect --endpoint=ipc:///tmp/sock --mode=subscriber

Hacking
-------

Source code for txZMQ is available at `github <https://github.com/smira/txZMQ>`_,
forks and pull requests are welcome.

To start hacking, please install ``virtualenv`` and ``pip``.  In fresh checkout,
run::

    make env

(If your ``virtualenv`` binary has different name, you can specify it via
``make`` variables: ``make env VIRTUALENV=virtualenv-2.7``)

This should make new virtual environment at ``env/`` and install txZMQ and development requirements.

Run tests and style checks::

    make
