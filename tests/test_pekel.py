# coding: utf-8
"""Tests for pekel."""

import pekel
import unittest

CASES = [
    (-1, b'\x80\x02J\xff\xff\xff\xff.'),
    (0, b'\x80\x02K\x00.'),
    (1, b'\x80\x02K\x01.'),
    (2, b'\x80\x02K\x02.'),
    (255, b'\x80\x02K\xff.'),
    (256, b'\x80\x02M\x00\x01.'),
    (-255, b'\x80\x02J\x01\xff\xff\xff.'),
    (-256, b'\x80\x02J\x00\xff\xff\xff.'),
    (65535, b'\x80\x02M\xff\xff.'),
    (65536, b'\x80\x02J\x00\x00\x01\x00.'),
    (-65535, b'\x80\x02J\x01\x00\xff\xff.'),
    (-65536, b'\x80\x02J\x00\x00\xff\xff.'),
    (2 ** 31 - 1, b'\x80\x02J\xff\xff\xff\x7f.'),
    (2 ** 31, b'\x80\x02\x8a\x05\x00\x00\x00\x80\x00.'),
    (2 ** 63 - 1, b'\x80\x02\x8a\x08\xff\xff\xff\xff\xff\xff\xff\x7f.'),
    (2 ** 63, b'\x80\x02\x8a\t\x00\x00\x00\x00\x00\x00\x00\x80\x00.'),
    (2 ** 127,
     b'\x80\x02\x8a\x11\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00.'),
    (b'', b'\x80\x02U\x00.'),
    (b'x' * 255,
     b'\x80\x02U\xffxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.'),
    (b'x' * 256,
     b'\x80\x02T\x00\x01\x00\x00xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.'),
    (b'\xff', b'\x80\x02U\x01\xff.'),
    (u'', b'\x80\x02X\x00\x00\x00\x00.'),
    (u'x', b'\x80\x02X\x01\x00\x00\x00x.'),
    (u'é', b'\x80\x02X\x02\x00\x00\x00\xc3\xa9.'),
    (u'x' * 256,
     b'\x80\x02X\x00\x01\x00\x00xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.'),
    (True, b'\x80\x02\x88.'),
    (False, b'\x80\x02\x89.'),
    (None, b'\x80\x02N.'),
    ((), b'\x80\x02).'),
    ((1,), b'\x80\x02K\x01\x85.'),
    ((1, 2), b'\x80\x02K\x01K\x02\x86.'),
    ((1, 2, 3), b'\x80\x02K\x01K\x02K\x03\x87.'),
    ((1, 2, 3, 4), b'\x80\x02(K\x01K\x02K\x03K\x04t.'),
    ([], b'\x80\x02].'),
    ([1], b'\x80\x02(K\x01l.'),
    ([1, 2], b'\x80\x02(K\x01K\x02l.'),
]


class TestPekel(unittest.TestCase):
    mod = pekel.pypekel

    def test(self):
        # type: () -> None
        for obj, pekeled in CASES:
            self.assertEqual(self.mod.dumps(obj), pekeled)
            self.assertEqual(self.mod.loads(pekeled), obj)


if __name__ == '__main__':
    unittest.main()
