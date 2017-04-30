"""Implementation of the pekel protocol in pure Python."""

from io import BytesIO
import pickle
import six
from struct import pack, unpack
from typing import Any, IO, List, Tuple, Text, Union

Pekelable = Union[None, bool, int, bytes, Text, List[Any], Tuple[Any, ...]]

PROTO = b'\x80'  # protocol (same as pickle)
VERSION = b'\x02'  # protocol version (corresponding to pickle protocol 2)
STOP = b'.'

# Opcodes
NEWTRUE = b'\x88'
NEWFALSE = b'\x89'
BINSTRING = b'T'
SHORT_BINSTRING = b'U'
BINUNICODE = b'X'
BININT1 = b'K'
BININT2 = b'M'
BININT = b'J'
LONG1 = b'\x8a'
LONG4 = b'\x8b'
EMPTY_TUPLE = b')'
TUPLE1 = b'\x85'
TUPLE2 = b'\x86'
TUPLE3 = b'\x87'
TUPLE = b't'
MARK = b'('
EMPTY_LIST = b']'
LIST = b'l'

MARKER = object()


class NotPekelableError(TypeError):
    """Error thrown when an object cannot be pekeled."""


class UnpekelError(RuntimeError):
    """Raised when decoding a pekel fails."""


class Pekeler(object):
    def __init__(self, f):
        # type: (IO[bytes]) -> None
        self.f = f

    def dump(self, obj):
        # type: (Pekelable) -> None
        self.f.write(PROTO + VERSION)
        self._write_recursive(obj)
        self.f.write(STOP)

    def _write_recursive(self, obj):
        # type: (Pekelable) -> None
        if isinstance(obj, bool):
            if obj is True:
                self.f.write(NEWTRUE)
            elif obj is False:
                self.f.write(NEWFALSE)
            else:
                raise NotPekelableError(obj)
        elif isinstance(obj, six.integer_types):
            # This basically mirrors the Python 3 implementation of save_long
            if 0 <= obj <= 0xff:
                self.f.write(BININT1 + six.int2byte(obj))
            elif 0 <= obj <= 0xffff:
                self.f.write(BININT2 + pack('<H', obj))
            elif -0x80000000 <= obj <= 0x7fffffff:
                self.f.write(BININT + pack('<i', obj))
            else:
                # Use the pickle module to encode the long as a little-endian, two's complement
                # bytestring
                encoded = pickle.encode_long(obj)
                size = len(encoded)
                if size <= 0xff:
                    self.f.write(LONG1 + six.int2byte(size) + encoded)
                else:
                    # really big integer
                    self.f.write(LONG4 + pack('<i', size) + encoded)
        elif isinstance(obj, bytes):
            size = len(obj)
            if size <= 0xff:
                self.f.write(SHORT_BINSTRING + six.int2byte(size) + obj)
            else:
                self.f.write(BINSTRING + pack('<i', size) + obj)
        elif isinstance(obj, six.text_type):
            data = obj.encode('utf-8')
            self.f.write(BINUNICODE + pack('<i', len(data)) + data)
        elif isinstance(obj, tuple):
            size = len(obj)
            if size > 3:
                self.f.write(MARK)
            for elt in obj:
                self._write_recursive(elt)
            if size == 0:
                self.f.write(EMPTY_TUPLE)
            elif size == 1:
                self.f.write(TUPLE1)
            elif size == 2:
                self.f.write(TUPLE2)
            elif size == 3:
                self.f.write(TUPLE3)
            else:
                self.f.write(TUPLE)
        elif isinstance(obj, list):
            if not obj:
                self.f.write(EMPTY_LIST)
            else:
                self.f.write(MARK)
                for elt in obj:
                    self._write_recursive(elt)
                self.f.write(LIST)
        else:
            raise NotPekelableError(obj)


class Unpekeler(object):
    def __init__(self, f):
        # type: (IO[bytes]) -> None
        self.f = f
        self.stack = []  # type: List[Union[object, Pekelable]]

    def load(self):
        # type: () -> Pekelable
        while True:
            opcode = self.f.read(1)
            if opcode == STOP:
                break
            try:
                fn = self.DISPATCH[opcode]
            except KeyError:
                raise UnpekelError('Unrecognized opcode {!r}'.format(opcode))
            else:
                fn(self)
        if len(self.stack) != 1:
            raise UnpekelError('Stray data on the stack')
        return self.stack[0]

    def dispatch_proto(self):
        # type: () -> None
        version = self.f.read(1)
        if version != VERSION:
            raise UnpekelError('Unsupported protocol version {!r}'.format(version))

    def dispatch_newtrue(self):
        # type: () -> None
        self.stack.append(True)

    def dispatch_newfalse(self):
        # type: () -> None
        self.stack.append(False)

    def dispatch_binstring(self):
        # type: () -> None
        size_bytes = self.f.read(4)
        size = unpack('<i', size_bytes)[0]
        self.stack.append(self.f.read(size))

    def dispatch_short_binstring(self):
        # type: () -> None
        size_bytes = self.f.read(1)
        size = ord(size_bytes)
        self.stack.append(self.f.read(size))

    def dispatch_binunicode(self):
        # type: () -> None
        size_bytes = self.f.read(4)
        size = unpack('<i', size_bytes)[0]
        self.stack.append(self.f.read(size).decode('utf-8'))

    def dispatch_binint1(self):
        # type: () -> None
        obj = ord(self.f.read(1))
        self.stack.append(obj)

    def dispatch_binint2(self):
        # type: () -> None
        obj = unpack('<H', self.f.read(2))[0]
        self.stack.append(obj)

    def dispatch_binint(self):
        # type: () -> None
        obj = unpack('<i', self.f.read(4))[0]
        self.stack.append(obj)

    def dispatch_long1(self):
        # type: () -> None
        size = ord(self.f.read(1))
        data = self.f.read(size)
        self.stack.append(pickle.decode_long(data))

    def dispatch_long4(self):
        # type: () -> None
        size = unpack('<i', self.f.read(4))[0]
        data = self.f.read(size)
        self.stack.append(pickle.decode_long(data))

    def dispatch_mark(self):
        # type: () -> None
        self.stack.append(MARKER)

    def dispatch_empty_tuple(self):
        # type: () -> None
        self.stack.append(())

    def dispatch_tuple1(self):
        # type: () -> None
        self.stack[-1] = (self.stack[-1],)

    def dispatch_tuple2(self):
        # type: () -> None
        self.stack[-2:] = [(self.stack[-2], self.stack[-1])]

    def dispatch_tuple3(self):
        # type: () -> None
        self.stack[-3:] = [(self.stack[-3], self.stack[-2], self.stack[-1])]

    def dispatch_tuple(self):
        # type: () -> None
        idx = self.nearest_marker()
        self.stack[idx] = tuple(self.stack[idx + 1:])
        del self.stack[idx + 1:]

    def dispatch_empty_list(self):
        # type: () -> None
        self.stack.append([])

    def dispatch_list(self):
        # type: () -> None
        idx = self.nearest_marker()
        self.stack[idx] = self.stack[idx + 1:]
        del self.stack[idx + 1:]

    def nearest_marker(self):
        # type: () -> int
        idx = len(self.stack) - 1
        while idx >= 0:
            if self.stack[idx] is MARKER:
                return idx
            idx -= 1
        raise UnpekelError('Could not find marker')

    DISPATCH = {
        PROTO: dispatch_proto,
        NEWTRUE: dispatch_newtrue,
        NEWFALSE: dispatch_newfalse,
        BINSTRING: dispatch_binstring,
        SHORT_BINSTRING: dispatch_short_binstring,
        BINUNICODE: dispatch_binunicode,
        BININT1: dispatch_binint1,
        BININT2: dispatch_binint2,
        BININT: dispatch_binint,
        LONG1: dispatch_long1,
        LONG4: dispatch_long4,
        MARK: dispatch_mark,
        EMPTY_TUPLE: dispatch_empty_tuple,
        TUPLE1: dispatch_tuple1,
        TUPLE2: dispatch_tuple2,
        TUPLE3: dispatch_tuple3,
        TUPLE: dispatch_tuple,
        EMPTY_LIST: dispatch_empty_list,
        LIST: dispatch_list,
    }


def dump(obj, f):
    # type: (Pekelable, IO[bytes]) -> None
    """Pekel an object to a file."""
    pekeler = Pekeler(f)
    pekeler.dump(obj)


def dumps(obj):
    # type: (Pekelable) -> bytes
    """Pekel an object and return the result."""
    f = BytesIO()
    pekeler = Pekeler(f)
    pekeler.dump(obj)
    return f.getvalue()


def load(f):
    # type: (IO[bytes]) -> Pekelable
    """Loads a pekeled object from a file."""
    unpekeler = Unpekeler(f)
    return unpekeler.load()


def loads(data):
    # type: (bytes) -> Pekelable
    """Loads a pekeled object from a string."""
    unpekeler = Unpekeler(BytesIO(data))
    return unpekeler.load()
