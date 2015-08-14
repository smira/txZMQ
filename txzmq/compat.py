import sys

PY3 = sys.version_info[0] == 3

if PY3:  # pragma: no cover
    binary_string_type = bytes
else:  # pragma: no cover
    binary_string_type = str

if PY3:  # pragma: no cover
    def is_nonstr_iter(v):
        if isinstance(v, (str, bytes)):
            return False
        return hasattr(v, '__iter__')
else:  # pragma: no cover
    def is_nonstr_iter(v):
        return hasattr(v, '__iter__')
