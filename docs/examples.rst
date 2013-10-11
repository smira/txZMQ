Examples
--------

Publish-Subscribe
^^^^^^^^^^^^^^^^^

Here is an example of using txZMQ with publish and subscribe
(`examples/push_pull.py <https://github.com/smira/txZMQ/blob/master/examples/pub_sub.py>`_):

.. literalinclude:: ../examples/pub_sub.py

The same example is available in the source code. You can run it from the
checkout directory with the following commands (in two different terminals)::

    examples/pub_sub.py --method=bind --endpoint=ipc:///tmp/sock --mode=publisher

    examples/pub_sub.py --method=connect --endpoint=ipc:///tmp/sock --mode=subscriber

Push-Pull
^^^^^^^^^

Example for push and pull socket is available in 
`examples/push_pull.py <https://github.com/smira/txZMQ/blob/master/examples/push_pull.py>`_.

.. literalinclude:: ../examples/push_pull.py
