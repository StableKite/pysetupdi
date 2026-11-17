"""Read existing cached results of real constructors and Windows enumeration."""
import unittest
from unittest.mock import patch

from pysetupdi import Device, devices


class StoredInstanceIdTests(unittest.TestCase):
    def test_constructor_stores_supplied_string_without_opening(self):
        for identifier in ('ROOT\\STORED_ONLY', '', 'USB\\Unicode_\u0418\u0414'):
            with self.subTest(identifier=identifier):
                device = Device(identifier)
                self.assertIsNone(device._handle)
                with patch.object(Device, 'open', side_effect=AssertionError('opened handle')), patch.object(Device, 'get_property', side_effect=AssertionError('queried Windows')):
                    self.assertIs(device._instance_id, identifier)
                self.assertIsNone(device._handle)

    def test_actual_enumeration_stored_id_and_unchanged_dynamic_property(self):
        iterator = devices()
        try:
            device = next(iterator)
            identifier = device._instance_id
            self.assertIsInstance(identifier, str)
            self.assertTrue(identifier)
            self.assertIsNone(device._handle)
            self.assertEqual(device.instance_id, identifier)
            self.assertIsNone(device._handle)
            with patch.object(Device, 'open', side_effect=AssertionError('opened handle')), patch.object(Device, 'get_property', side_effect=AssertionError('queried Windows')):
                self.assertIs(device._instance_id, identifier)
            self.assertIsNone(device._handle)
        finally:
            iterator.close()


if __name__ == '__main__':
    unittest.main()
