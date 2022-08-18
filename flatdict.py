"""
This is a fork of FlatDict by Gavin M. Roy.
The original license is retained here:

Copyright (c) 2013-2020 Gavin M. Roy
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 * Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software without
   specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""
FlatDict is a dict object that allows for single level, delimited
key/value pair mapping of nested dictionaries.

"""
import sys

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

__version__ = '4.0.1'

NO_DEFAULT = object()

# class KeyTree(tuple):
#     pass

KeyTree = tuple


class TupleFlatDict(MutableMapping):
    """
    A fork of FlatDict that uses tuples to represent the tree rather than delimited strings
    """
    _COERCE = dict

    def __init__(self, value=None, dict_class=dict):
        super().__init__()
        self._values = dict_class()
        self._dict_class = dict_class
        self.update(value)

    def __contains__(self, key):
        """Check to see if the key exists, checking for both delimited and
        not delimited key values.

        :param mixed key: The key to check for
        """
        if self._has_delimiter(key):
            pk, ck = self._split_key(key)
            return pk in self._values and ck in self._values[pk]
        return key in self._values

    @staticmethod
    def _split_key(key):
        assert len(key) > 1
        pk, *ck = key
        ck = TupleFlatDict._squash_key(ck)
        return pk, ck

    def _join_keys(self, *args):
        retval = []
        for k in args:
            if self._has_delimiter(k):
                retval += list(k)
            else:
                retval.append(k)
        return KeyTree(retval)

    @staticmethod
    def _squash_key(x):
        assert len(x)
        if len(x) == 1:
            return x[0]
        return KeyTree(x)

    def __delitem__(self, key):
        """Delete the item for the specified key, automatically dealing with
        nested children.

        :param mixed key: The key to use
        :raises: KeyError

        """
        if key not in self:
            raise KeyError
        if self._has_delimiter(key):
            pk, ck = self._split_key(key)
            del self._values[pk][ck]
            if not self._values[pk]:
                del self._values[pk]
        else:
            del self._values[key]

    def __eq__(self, other):
        """Check for equality against the other value

        :param other: The value to compare
        :type other: TupleFlatDict
        :rtype: bool
        :raises: TypeError

        """
        if isinstance(other, dict):
            return self.as_dict() == other
        elif not isinstance(other, TupleFlatDict):
            raise TypeError
        return self.as_dict() == other.as_dict()

    def __ne__(self, other):
        """Check for inequality against the other value

        :param other: The value to compare
        :type other: dict or TupleFlatDict
        :rtype: bool

        """
        return not self.__eq__(other)

    def __getitem__(self, key):
        """Get an item for the specified key, automatically dealing with
        nested children.

        :param mixed key: The key to use
        :rtype: mixed
        :raises: KeyError

        """
        values = self._values
        key = key if self._has_delimiter(key) else [key]

        for part in key:
            values = values[part]
        return values

    def __iter__(self):
        """Iterate over the flat dictionary key and values

        :rtype: Iterator
        :raises: RuntimeError

        """
        return iter(self.keys())

    def __len__(self):
        """Return the number of items.

        :rtype: int

        """
        return len(self.keys())

    def __reduce__(self):
        """Return state information for pickling

        :rtype: tuple

        """
        return TupleFlatDict, (self.as_dict())

    def __repr__(self):
        """Return the string representation of the instance.

        :rtype: str

        """
        return f'<{TupleFlatDict.__name__} id={id(self)} {str(self)}>"'

    def __setitem__(self, key, value):
        """Assign the value to the key, dynamically building nested
        FlatDict items where appropriate.

        :param mixed key: The key for the item
        :param mixed value: The value for the item
        :raises: TypeError

        """
        if isinstance(value, self._COERCE) and not isinstance(value, TupleFlatDict):
            value = TupleFlatDict(value, dict_class=self._dict_class)
        if self._has_delimiter(key):
            pk, ck = self._split_key(key)
            if pk not in self._values:
                self._values[pk] = TupleFlatDict({ck: value}, dict_class=self._dict_class)
                return
            elif not isinstance(self._values[pk], TupleFlatDict):
                raise TypeError(f'Assignment to invalid type for key {pk}')
            self._values[pk][ck] = value
        else:
            self._values[key] = value

    def __str__(self):
        """Return the string value of the instance.

        :rtype: str

        """
        return '{{{}}}'.format(', '.join(
            ['{!r}: {!r}'.format(k, self[k]) for k in self.keys()]))

    def as_dict(self):
        """Return the :class:`~flatdict.FlatDict` as a :class:`dict`

        :rtype: dict

        """
        out = self._dict_class()
        for key in self.keys():
            if self._has_delimiter(key):
                pk, ck = self._split_key(key)
                if pk not in out:
                    out[pk] = {}
                if self._has_delimiter(ck):
                    ck, _ = self._split_key(ck)
                if isinstance(self._values[pk][ck], TupleFlatDict):
                    out[pk][ck] = self._values[pk][ck].as_dict()
                else:
                    out[pk][ck] = self._values[pk][ck]
            else:
                out[key] = self._values[key]
        return out

    def clear(self):
        """Remove all items from the flat dictionary."""
        self._values.clear()

    def copy(self):
        """Return a shallow copy of the flat dictionary.

        :rtype: flatdict.FlatDict

        """
        return TupleFlatDict(value=self.as_dict(),dict_class=self._dict_class)

    def get(self, key, d=None):
        """Return the value for key if key is in the flat dictionary, else
        default. If default is not given, it defaults to ``None``, so that this
        method never raises :exc:`KeyError`.

        :param mixed key: The key to get
        :param mixed d: The default value
        :rtype: mixed

        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return d

    def items(self):
        """Return a copy of the flat dictionary's list of ``(key, value)``
        pairs.

        .. note:: CPython implementation detail: Keys and values are listed in
            an arbitrary order which is non-random, varies across Python
            implementations, and depends on the flat dictionary's history of
            insertions and deletions.

        :rtype: list

        """
        return [(k, self.__getitem__(k)) for k in self.keys()]

    def iteritems(self):
        """Return an iterator over the flat dictionary's (key, value) pairs.
        See the note for :meth:`flatdict.FlatDict.items`.

        Using ``iteritems()`` while adding or deleting entries in the flat
        dictionary may raise :exc:`RuntimeError` or fail to iterate over all
        entries.

        :rtype: Iterator
        :raises: RuntimeError

        """
        for item in self.items():
            yield item

    def iterkeys(self):
        """Iterate over the flat dictionary's keys. See the note for
        :meth:`flatdict.FlatDict.items`.

        Using ``iterkeys()`` while adding or deleting entries in the flat
        dictionary may raise :exc:`RuntimeError` or fail to iterate over all
        entries.

        :rtype: Iterator
        :raises: RuntimeError

        """
        for key in self.keys():
            yield key

    def itervalues(self):
        """Return an iterator over the flat dictionary's values. See the note
        :meth:`flatdict.FlatDict.items`.

        Using ``itervalues()`` while adding or deleting entries in the flat
        dictionary may raise a :exc:`RuntimeError` or fail to iterate over all
        entries.

        :rtype: Iterator
        :raises: RuntimeError

        """
        for value in self.values():
            yield value

    def keys(self):
        """Return a copy of the flat dictionary's list of keys.
        See the note for :meth:`flatdict.FlatDict.items`.

        :rtype: list

        """
        keys = []

        for pk, value in self._values.items():
            if isinstance(value, (TupleFlatDict, dict)):
                nested = [self._join_keys(pk, ck) for ck in value.keys()]
                keys += nested if nested else [pk]
            else:
                keys.append(pk)

        return keys

    def pop(self, key, default=NO_DEFAULT):
        """If key is in the flat dictionary, remove it and return its value,
        else return default. If default is not given and key is not in the
        dictionary, :exc:`KeyError` is raised.

        :param mixed key: The key name
        :param mixed default: The default value
        :rtype: mixed

        """
        if key not in self and default != NO_DEFAULT:
            return default
        value = self[key]
        self.__delitem__(key)
        return value

    def setdefault(self, key, default):
        """If key is in the flat dictionary, return its value. If not,
        insert key with a value of default and return default.
        default defaults to ``None``.

        :param mixed key: The key name
        :param mixed default: The default value
        :rtype: mixed

        """
        if key not in self:
            self.__setitem__(key, default)
        return self.__getitem__(key)

    def update(self, other=None, **kwargs):
        """Update the flat dictionary with the key/value pairs from other,
        overwriting existing keys.

        ``update()`` accepts either another flat dictionary object or an
        iterable of key/value pairs (as tuples or other iterables of length
        two). If keyword arguments are specified, the flat dictionary is then
        updated with those key/value pairs: ``d.update(red=1, blue=2)``.

        :param iterable other: Iterable of key, value pairs
        :rtype: None

        """
        [self.__setitem__(k, v) for k, v in dict(other or kwargs).items()]

    def values(self):
        """Return a copy of the flat dictionary's list of values. See the note
        for :meth:`flatdict.FlatDict.items`.

        :rtype: list

        """
        return [self.__getitem__(k) for k in self.keys()]

    def _has_delimiter(self, key):
        """Checks to see if the key contains the delimiter.
        :rtype: bool
        """
        return isinstance(key, KeyTree)

    def get_flat_view(self):
        """
        Return a dictionary whose keys and values correspond to the nested keys from the .keys() method,
        and .values() correspond to the leaves of said keys form the .values() method.

        This makes it easy to iterate through the whole structure as a flattened dict.
        :return:
        """
        return dict(self)

class TupleFlatDefaultDict(TupleFlatDict):
    def __init__(self, _default_factory, **values):
        from collections import defaultdict
        from functools import partial
        super().__init__(
            value=(values if len(values) else None),
            dict_class=partial(defaultdict, _default_factory)
        )


if __name__ == '__main__':
    def __san_check():
        from flatdict import FlatDict
        a = TupleFlatDict({
            "a": {
                "b": {
                    "c"
                }
            }
        })
        add = a.as_dict()
        print(add)
        a = {"Root": {
            "A": 1,
            "B": {
                "B-1": 2,
                "B-3": 3
            },
            2: None,
            3.14159: "Aojdsvka"

        }}

        flat_a = TupleFlatDict(a)
        print(flat_a)
        print(flat_a.keys())


    __san_check()
