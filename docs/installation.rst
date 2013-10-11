Installation
============

Short version::

    pip install txZMQ


Requirements
------------

C libraries required:

* ØMQ library 2.2.x or 3.2.x

Python packages required:

* pyzmq >= 13
* Twisted

MacOS X
-------

On Mac OS X with Homebrew, please run::

    brew install --with-pgm zeromq

This would install ØMQ 2.2.0, for 3.2.x please run::

    brew install --with-pgm --devel zeromq

Ubuntu/Debian
-------------

Install ØMQ library with headers::

    apt-get install libzmq-dev

Package name could aslo be ``libzmq3-dev`` for version 3.x.