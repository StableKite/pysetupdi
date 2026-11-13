from pysetupdi import Device, devices
from pysetupdi.constants import DEVPKEY
from pysetupdi.property import Property
from pysetupdi.structures import GUID, DevicePropertyKey

def bad_parser(data: str) -> int:
    return len(data)

def invalid_calls(device: Device) -> None:
    Device(123)  # E
    GUID(object())  # E
    DevicePropertyKey(GUID(), 'wrong')  # E
    DevicePropertyKey(GUID(), 1, 2)  # E
    device.open(1)  # E
    device.get_property('wrong')  # E
    device['wrong']  # E
    device.get_property_keys(1)  # E
    device.friendly_name = 'write forbidden'  # E
    device.parent = device  # E
    label: str = device.ui_number  # E
    count: int = device.friendly_name  # E
    raw: bytes = device.get_property(DEVPKEY.Device.InstanceId)  # E
    Property('wrong', 1)  # E
    Property(b'data', 'wrong')  # E
    Property.add_parser(1, func=bad_parser)  # E
    Property.add_parser(1, length='wrong')  # E
    devices(guid=object())  # E
    devices(enumerator=1)  # E
    devices(hwnd_parent='wrong')  # E
    devices(flags='wrong')  # E
    binary: bytes = device.power_data  # E
    print(label, count, raw, binary)
