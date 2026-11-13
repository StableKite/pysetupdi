from collections.abc import Callable, Generator
from contextlib import AbstractContextManager
from datetime import datetime
from typing import assert_type

from pysetupdi import Device, devices
from pysetupdi.constants import DEVPKEY, DevicePropertyKeys, DIGCF_PRESENT
from pysetupdi.property import Property
from pysetupdi.structures import DEVPROPKEY, SP_DEVINFO_DATA, GUID, DeviceInfoData, DevicePropertyKey


class Parsed:
    def __init__(self, data: bytes) -> None:
        self.data = data


@Property.add_parser(0x777701)
def parse_custom(data: bytes) -> Parsed:
    return Parsed(data)


assert_type(parse_custom, Callable[[bytes], Parsed])
assert_type(Property.add_parser(0x777702, func=parse_custom), Callable[[bytes], Parsed])
assert_type(Property.add_parser(0x777703, None, parse_custom), Callable[[bytes], Parsed])
assert_type(Property(b'payload', 0x777701), object)


def device_contract(device: Device) -> None:
    assert_type(device.device_desc, str)
    assert_type(device.ui_number, int)
    assert_type(device.hardware_id, list[str])
    assert_type(device.class_guid, GUID)
    assert_type(device.security, bytes)
    assert_type(device.power_data, tuple[int, ...])
    assert_type(device.exclusive, bool)
    assert_type(device.install_date, datetime)
    assert_type(device.parent, Device)
    assert_type(device.children, list[Device])
    assert_type(device.siblings, list[Device])
    assert_type(device.open(), AbstractContextManager[Device])
    with device.open() as opened:
        assert_type(opened, Device)
        assert_type(opened.get_property_keys(), list[DevicePropertyKey])
        assert_type(opened.get_property(DEVPKEY.Device.InstanceId), object)
        assert_type(opened[DevicePropertyKeys.Device.InstanceId], object)


def constructor_contract() -> None:
    guid = GUID('{00112233-4455-6677-8899-AABBCCDDEEFF}')
    assert_type(bytes(guid), bytes)
    assert_type(str(guid), str)
    GUID(guid)
    GUID(bytearray(bytes(guid)))
    GUID(memoryview(bytes(guid)))
    key = DEVPROPKEY(guid, 7, 'example')
    assert_type(key, DevicePropertyKey)
    assert_type(key.pid, int)
    assert_type(key.name, str | None)
    info = SP_DEVINFO_DATA()
    assert_type(info, DeviceInfoData)
    assert_type(info.size, int)
    assert_type(info.dev_inst, int)
    assert_type(Device('typed-only'), Device)
    iterator = devices(guid=guid, enumerator=None, hwnd_parent=None, flags=DIGCF_PRESENT)
    assert_type(iterator, Generator[Device, None, None])
    iterator.close()


if __name__ == '__main__':
    constructor_contract()
    parsed = Property(b'payload', 0x777701)
    assert isinstance(parsed, Parsed) and parsed.data == b'payload'
