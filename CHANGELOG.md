# Changelog

## 2.0.0 (2018-01-18)
- Code efficiency refactoring and cleanup
- Rewrote a majority of the tests, now at 100% coverage
- ADDED `FlatDict.__eq__` and `FlatDict.__ne__` (#13 - [arm77](https://github.com/arm77))
- ADDED `FlatterDict` class that performs the list, set, and tuple coercion that was added in v1.20
- REMOVED coercion of lists and tuples from `FlatDict` that was added in 1.2.0. Alternative to (#12 - [rj-jesus](https://github.com/rj-jesus))
- REMOVED `FlatDict.has_key()` as it duplicates of `FlatDict.__contains__`
- ADDED Python 3.5 and 3.6 to support matrix
- REMOVED support for Python 2.6 and Python 3.2, 3.3

## 1.2.0 (2015-06-25)
- ADDED Support lists and tuples as well as dicts. (#4 - [alex-hutton](https://github.com/alex-hutton))

## 1.1.3 (2015-01-04)
- ADDED Python wheel support

## 1.1.2 (2013-10-09)
- Documentation and CI updates
- CHANGED use of `dict()` to a dict literal `{}`

## 1.1.1 (2012-08-17)
- ADDED `FlatDict.as_dict()`
- ADDED Python 3 support
- ADDED `FlatDict.set_delimiter()`
- Bugfixes and improvements from [naiquevin](https://github.com/naiquevin)


## 1.0.0 (2012-08-10)

- Initial release