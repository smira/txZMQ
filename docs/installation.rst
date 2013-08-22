Installation
============

Short version::

    pip install txZMQ


Requirements
------------

C libraries required:

* ØMQ library 2.2.x or 3.2.x

Python packages required:

* pyzmq (for CPython)
* pyzmq-ctypes (for PyPy)
* Twisted

MacOS X
-------

On Mac OS X with Homebrew, please run::

    brew install --with-pgm zeromq

This would install ØMQ 2.2.0, for 3.2.x please run::

    brew install --with-pgm --devel zeromq

    