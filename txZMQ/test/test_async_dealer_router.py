"""
Test for high volume usage of Router / Dealer in L{txZMQ.connection}.
"""

from twisted.trial import unittest
from txZMQ.factory import ZmqFactory
from txZMQ.connection import ZmqConnection, ZmqEndpoint, ZmqEndpointType
from txZMQ.test import _wait
from zmq.core import constants
from twisted.internet.defer import inlineCallbacks, Deferred, DeferredList
from random import random
from uuid import uuid4
from twisted.internet import reactor


class ZmqTestServer(ZmqConnection):

    """ROUTER server. Responds to PING requests with a routed PONG response."""

    socketType = constants.ROUTER
    requests = 0  # PING requests received
    responses = 0 # PING responses sent

    def messageReceived(self, message):
        self.requests += 1 # Increment request count.
        route, msg_id, data = message # Get message parts
        if data != "PING": # Verify message
            raise Exception("Did not receive well formed PING.")
        # Respond with PONG asynchronously within a second.
        reactor.callLater(random(), self.pong, route, msg_id)

    def pong(self, route, msg_id):
        self.responses += 1 # Increment response count.
        self.send([route, msg_id, "PONG"]) # Respond.


class ZmqTestClient(ZmqConnection):

    """Dealer client. Makes PING requests and verifies PONG responses."""

    socketType = constants.DEALER
    requests = 0  # PING requests sent
    responses = 0 # PONG responses received

    def __init__(self, *args, **kwargs):
        # Dictionary of (msg_id, deferred) pairs that callback when a 
        # PONG response is received or errback after a 5 second timeout.
        self.deferreds = {} 
        # Dictionary of (msg_id, timeout) pairs. Used to cancel timeout
        # if a PONG response is received.
        self.timeouts = {}
        super(ZmqTestClient, self).__init__(*args, **kwargs)

    def ping(self):
        self.requests += 1 # Increment request count.
        msg_id = uuid4().hex # Unique message ID
        self.deferreds[msg_id] = Deferred() # Deferred waiting on PONG response.
        # Timeout for the PONG response.
        self.timeouts[msg_id] = reactor.callLater(5, self.timeout, msg_id)
        # Send PING
        self.send([msg_id, "PING"])
        # Return PONG deferred.
        return self.deferreds[msg_id]

    def messageReceived(self, message):
        self.responses += 1 # Increment response count.
        msg_id, data = message # Message parts
        if data != "PONG": # Verify message
            raise Exception("Did not receive well formed PONG.")
        self.timeouts[msg_id].cancel() # Cancel the timeout.
        # Callback the deferred verifying the PONG response.
        self.deferreds[msg_id].callback(True) 

    def timeout(self, msg_id):
        # Errback the deferred indicating a timeout.
        self.deferreds[msg_id].errback(Exception("Timeout after %s requests "
            "and %s responses: %s" % (self.requests, self.responses, msg_id)))


@inlineCallbacks
def ping(client):
    """Makes 100 ping requests. Waits for a response before pinging again."""
    for i in range(0, 100):
        yield client.ping()


class ZmqAsyncDealerRouterTestCase(unittest.TestCase):
    """
    Test case for L{zmq.twisted.connection.Connection}.
    """

    def setUp(self):
        self.factory = ZmqFactory()

    def tearDown(self):
        self.factory.shutdown()
    
    @inlineCallbacks
    def test_async_dealer_router(self):
        # Bind the ROUTER PONG server, wait for a second to make sure the
        # the socket is ready.
        bind_ep = ZmqEndpoint(ZmqEndpointType.Bind, "tcp://127.0.0.1:5000")
        server = ZmqTestServer(self.factory, bind_ep)
        yield _wait(1)
        # Connect the DEALER PING client, wait for a second to make sure the
        # socket is ready.
        connect_ep = ZmqEndpoint(ZmqEndpointType.Connect, "tcp://127.0.0.1:5000")
        client = ZmqTestClient(self.factory, connect_ep)
        yield _wait(1)
        # Launch 10 pingers, which will each ping 100 times and wait 
        # for completion.
        results = yield DeferredList([ping(client) for x in range(0,10)])
        # Server requests and responses should be 1:1
        self.failUnlessEqual(server.requests, server.responses)
        # Client requests and responses should be 1:1
        self.failUnlessEqual(client.requests, client.responses)
        # Servers and clients requests and responses should also match.
        self.failUnlessEqual(client.requests, server.responses)
        for row in results:
            if not row[0]:
                raise row[1] # Raise any errors encountered.

