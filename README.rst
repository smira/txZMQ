Twisted bindings for 0MQ
========================

.. image:: https://coveralls.io/repos/smira/txZMQ/badge.png
    :target: https://coveralls.io/r/smira/txZMQ

.. image:: https://badge.fury.io/py/txZMQ.svg
    :target: https://badge.fury.io/py/txZMQ

Introduction
------------

txZMQ allows to integrate easily `ØMQ <http://zeromq.org>`_ sockets into
Twisted event loop (reactor).

txZMQ supports both CPython and PyPy and ØMQ library version 2.2.x or 3.2.x.

Documentation is available at `ReadTheDocs <http://txzmq.readthedocs.org>`_.


Requirements
------------

C library required:

* ØMQ library 2.2.x or 3.2.x

Python packages required:

* pyzmq >= 13 (for CPython & PyPy)
* Twisted


Details
-------

txZMQ introduces support for general 0MQ sockets by class ``ZmqConnection``
that can do basic event loop integration, sending-receiving messages in
non-blocking manner, scatter-gather for multipart messages.

txZMQ uses ØMQ APIs to get file descriptor that is used to signal pending
actions from ØMQ library IO thread running in separate thread. This is used in
a custom file descriptor reader, which is then added to the Twisted reactor.


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
