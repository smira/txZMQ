Twisted bindings for ZeroMQ
===========================

txZMQ allows to integrate easily `ZeroMQ <http://zeromq.org>`_ sockets into
Twisted event loop (reactor).

Requirements:

* ZeroMQ library >= 2.1 (heavily tested with 2.1.4)

Python packages required:

* pyzmq
* Twisted

txZMQ introduces support for general ZeroMQ sockets by class ``ZmqConnection``
that can do basic event loop integration, sending-receiving messages in
non-blocking manner, scatter-gather for multipart messages.

Special descendants of that class, ``ZmqPubConnection`` and ``ZmqSubConnection``
add special nice features for PUB/SUB sockets.

Other socket types could be easily derived from ``ZmqConnection`` except for 
REQ/REP sockets that may require more work, as reply should be send immediately
upon receiving message (currently ``ZmqConnection`` will try to read all available
message and write queued messages in parallel).

Example::

    import sys

    from optparse import OptionParser

    from twisted.internet import reactor, defer
    from twisted.python import log

    observer = log.FileLogObserver(sys.stderr)
    log.addObserver(observer.emit)

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
