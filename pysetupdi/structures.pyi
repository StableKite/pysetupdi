from _typeshed import ReadableBuffer
from collections.abc import Iterable
from ctypes import Array, Structure, c_ubyte
from typing import SupportsBytes, SupportsIndex

_GuidInput = str | ReadableBuffer | SupportsBytes | SupportsIndex | Iterable[SupportsIndex]

class _GUID(Structure):
    Data1: int
    Data2: int
    Data3: int
    Data4: Array[c_ubyte]
    def __init__(self, guid: _GuidInput = ...) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class GUID:
    def __init__(self, guid: _GuidInput = ...) -> None: ...
    def __bytes__(self) -> bytes: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class DevicePropertyKey(Structure):
    fmtid: _GUID
    pid: int
    name: str | None
    def __init__(self, guid: _GuidInput, pid: int, name: str | None = ...) -> None: ...
    def __eq__(self, key: object) -> bool: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class DeviceInfoData(Structure):
    cbSize: int
    ClassGuid: _GUID
    DevInst: int
    Reserved: int | None
    size: int
    dev_inst: int
    class_guid: _GUID
    def __init__(self) -> None: ...

SP_DEVINFO_DATA = DeviceInfoData
DEVPROPKEY = DevicePropertyKey
