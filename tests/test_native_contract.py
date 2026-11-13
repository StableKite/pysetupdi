"""Real Windows parsers and read-only SetupAPI; no device state changes."""
import ctypes
import datetime
import inspect
import struct
import unittest

import pysetupdi
from pysetupdi import constants as c
from pysetupdi.property import Property
from pysetupdi.structures import GUID, DeviceInfoData, DevicePropertyKey, DEVPROPKEY, SP_DEVINFO_DATA


class NativeContractTests(unittest.TestCase):
    def test_guid_and_structures(self):
        text = '{00112233-4455-6677-8899-AABBCCDDEEFF}'
        raw = bytes.fromhex('33221100554477668899aabbccddeeff')
        for value in (text, raw, bytearray(raw), memoryview(raw), GUID(text), list(raw)):
            with self.subTest(input_type=type(value).__name__):
                guid = GUID(value)
                self.assertEqual(bytes(guid), raw)
                self.assertEqual(str(guid), text)
        with self.assertRaisesRegex(ValueError, 'at least 16'):
            GUID(b'\x00')
        self.assertIs(DEVPROPKEY, DevicePropertyKey)
        self.assertIs(SP_DEVINFO_DATA, DeviceInfoData)
        self.assertEqual(ctypes.sizeof(DevicePropertyKey), 20)
        self.assertEqual(ctypes.sizeof(DeviceInfoData), 32 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28)
        info = DeviceInfoData()
        self.assertEqual(info.size, ctypes.sizeof(info))
        info.dev_inst = 7
        self.assertEqual(info.DevInst, 7)
        info.DevInst = 9
        self.assertEqual(info.dev_inst, 9)
        key = DevicePropertyKey(text, 7, 'sample')
        self.assertEqual(bytes(key), raw + struct.pack('<I', 7))
        self.assertEqual(key, DevicePropertyKey(raw, 7))
        self.assertNotEqual(key, object())
        self.assertTrue(str(key).startswith('sample, '))

    def test_all_numeric_scalar_and_array_formats(self):
        formats = [(c.DEVPROP_TYPE_INT16, 'h', -23), (c.DEVPROP_TYPE_UINT16, 'H', 65000),
                   (c.DEVPROP_TYPE_INT32, 'i', -123456), (c.DEVPROP_TYPE_UINT32, 'I', 0xabcdef12),
                   (c.DEVPROP_TYPE_INT64, 'q', -123456789012), (c.DEVPROP_TYPE_UINT64, 'Q', 0xfedcba9876543210),
                   (c.DEVPROP_TYPE_FLOAT, 'f', 1.25), (c.DEVPROP_TYPE_DOUBLE, 'd', -1.25)]
        for kind, fmt, value in formats:
            with self.subTest(kind=kind):
                self.assertEqual(Property(struct.pack('<' + fmt, value), kind), value)
                self.assertEqual(Property(struct.pack('<' + fmt * 2, value, value), kind | c.DEVPROP_TYPEMOD_ARRAY), [value, value])
        self.assertEqual(Property(b'\xff', c.DEVPROP_TYPE_SBYTE), -1)
        self.assertEqual(Property(b'\xff', c.DEVPROP_TYPE_BYTE), 255)
        # Preserve the established raw/tuple results for these public handlers.
        self.assertEqual(Property(b'\xff\x00', c.DEVPROP_TYPE_SBYTE | c.DEVPROP_TYPEMOD_ARRAY), b'\xff\x00')
        self.assertEqual(Property(b'\xff\x00', c.DEVPROP_TYPE_BYTE | c.DEVPROP_TYPEMOD_ARRAY), (255, 0))

    def test_composite_arrays(self):
        guid = GUID('{00112233-4455-6677-8899-AABBCCDDEEFF}')
        values = Property(bytes(guid) * 2, c.DEVPROP_TYPE_GUID | c.DEVPROP_TYPEMOD_ARRAY)
        self.assertEqual([str(value) for value in values], [str(guid)] * 2)
        self.assertEqual(Property(b'\x00\xff', c.DEVPROP_TYPE_BOOLEAN | c.DEVPROP_TYPEMOD_ARRAY), [False, True])
        self.assertEqual(Property(struct.pack('<qq', -12345, 25000), c.DEVPROP_TYPE_CURRENCY | c.DEVPROP_TYPEMOD_ARRAY), [-1.2345, 2.5])
        decimal = struct.pack('<HBBIQ', 0, 0, 0, 0x12345678, 0)
        self.assertEqual(Property(decimal, c.DEVPROP_TYPE_DECIMAL), float(0x12345678 << 64))
        self.assertEqual(Property(decimal * 2, c.DEVPROP_TYPE_DECIMAL | c.DEVPROP_TYPEMOD_ARRAY), [float(0x12345678 << 64)] * 2)
        key = DevicePropertyKey(guid, 7)
        keys = Property(bytes(key) * 2, c.DEVPROP_TYPE_DEVPROPKEY | c.DEVPROP_TYPEMOD_ARRAY)
        self.assertEqual(keys, [key, key])

    def test_dates_errors_and_strings(self):
        self.assertEqual(Property(struct.pack('<d', 2.5), c.DEVPROP_TYPE_DATE), datetime.datetime(1900, 1, 1, 12))
        self.assertEqual(Property(bytes(8), c.DEVPROP_TYPE_FILETIME), datetime.datetime(1601, 1, 1))
        error = Property(struct.pack('<i', 2), c.DEVPROP_TYPE_ERROR)
        self.assertEqual(error, (2, ctypes.FormatError(2)))
        self.assertEqual(Property(struct.pack('<ii', 2, 5), c.DEVPROP_TYPE_ERROR | c.DEVPROP_TYPEMOD_ARRAY), [(2, ctypes.FormatError(2)), (5, ctypes.FormatError(5))])
        status = Property(struct.pack('<I', 0xc0000005), c.DEVPROP_TYPE_NTSTATUS)
        self.assertEqual(status[0], -1073741819)
        self.assertIsInstance(status[1], str)
        self.assertTrue(status[1])
        self.assertEqual(Property('hello\0'.encode('utf-16-le'), c.DEVPROP_TYPE_STRING), 'hello')
        self.assertEqual(Property('a\0b\0\0'.encode('utf-16-le'), c.DEVPROP_TYPE_STRING_LIST), ['a', 'b'])
        self.assertIsNone(Property(b'', c.DEVPROP_TYPE_NULL))
        with self.assertRaises(AttributeError):
            Property(b'', c.DEVPROP_TYPE_EMPTY)

    def test_real_factory_and_custom_registration(self):
        self.assertTrue(inspect.isclass(Property))
        original = dict(Property._property_type)
        try:
            token = object()
            def parser(data):
                self.assertIsInstance(data, bytes)
                return token
            self.assertIs(Property.add_parser(0x700000, 1, parser), parser)
            self.assertIs(Property(b'x', 0x700000), token)
            self.assertEqual(Property(b'xy', 0x700000 | c.DEVPROP_TYPEMOD_ARRAY), [token, token])
            self.assertIs(Property.add_parser(0x700001)(parser), parser)
            self.assertIs(Property.add_parser(0x700002, func=parser), parser)
            self.assertIs(Property(b'x', 0x700001), token)
        finally:
            Property._property_type.clear()
            Property._property_type.update(original)

    def test_read_only_actual_device_information(self):
        iterator = pysetupdi.devices()
        try:
            device = next(iterator)
            self.assertIsNone(device._handle)
            with device.open() as opened:
                self.assertIs(opened, device)
                keys = device.get_property_keys()
                self.assertTrue(keys)
                self.assertTrue(all(isinstance(key, DevicePropertyKey) for key in keys))
                identifier = device[c.DEVPKEY.Device.InstanceId]
                self.assertIsInstance(identifier, str)
                with device.open() as nested:
                    self.assertIs(nested, device)
                    self.assertEqual(device.get_property(c.DEVPKEY.Device.InstanceId), identifier)
                self.assertEqual(device.get_property(c.DEVPKEY.Device.InstanceId), identifier)
            self.assertIsNone(device._handle)
            with self.assertRaises(AttributeError):
                device.friendly_name = 'forbidden'
        finally:
            iterator.close()


if __name__ == '__main__':
    unittest.main()
