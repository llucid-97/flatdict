FlatDict
========

*This is a fork of Gavin M. Roy 's Flat Dict package : https://github.com/gmr/flatdict

I have modified it to use tuples to represent the key tree instead of delimited strings.
This extends it to allow arbitrary types (except tuples) to be used as keys.

(NOTE the ``FlatterDict`` class hasn't been changed.)

========

``FlatDict``is a dict class that allows for single level key/value pair mapping of nested dictionaries.

You can interact with ``FlatDict`` like a normal dictionary and access child
dictionaries as you normally would or with the composite key.

*For example:*

.. code-block:: python

    value = FlatDict({'foo': {'bar': 'baz', 'qux': 'corge'}, 1:{2:'two',3:'three'}})

*would be the same as:*

.. code-block:: python

    value == {('foo', 'bar'): 'baz', ('foo', 'qux'): 'corge', (1, 2): 'two', (1, 3): 'three'}

*values can be accessed as:*

.. code-block:: python

    print(foo['foo','bar'])

    # or

    print(foo['foo']['bar'])
