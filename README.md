# pysetupdi
Python SetupAPI Wrapper

`devices` function generates iterable of Devices which is selected by given parameters. The parameters of `devices`
is similar to SetupDiGetClassDevs. Properties of each device can be accessed by accessing pre-defined properties or
giving DevicePropertyKey object as an index to device object.

~~~python
hard_disk_drives = devices('{4d36e967-e325-11ce-bfc1-08002be10318}')
for hard_disk_drive in hard_disk_drives:
    print(hard_disk_drive.device_desc)
~~~

You can also query information about devices by console command

~~~
C:\> pysetupdi -g {4d36e967-e325-11ce-bfc1-08002be10318} list
C:\> pysetupdi -i "SCSI\DISK&VEN_SAMSUN_&PROD_MZNTE256HMHP-000\4&103D1686&0&000000" get pdo_name
~~~

The package includes a PEP 561 marker and public interface stubs. `Device`
properties are read-only, `open()` is a context manager, and raw
`get_property()` / `__getitem__()` results have type `object`: the public
`Property.add_parser()` registry permits arbitrary parser return values.
The `Property` class object is described as its actual callable factory
interface, not as the instance type of its results. Its registration decorator
preserves the supplied parser's argument and result types. Runtime class
identity and parser registration remain unchanged.

`ui_number` is an integer. `power_data` retains the existing parser's
`tuple[int, ...]` result. The raw binary, byte-array, and custom-handler results
are preserved. See the Windows property definitions for
[UINumber](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/devpkey-device-uinumber)
and [PowerData](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/devpkey-device-powerdata).

The native tests use actual Windows libraries and read-only device-information
queries. Linux validation covers packaging and Windows-target static analysis;
native import and device access require Windows. Static package checks resolve
the supplied `.pyi` interfaces; they do not claim strict analysis of the raw
`ctypes` implementation files that those interfaces describe.

The stored `Device._instance_id` field is described as `str`, matching the
constructor and the IDs obtained by `devices()`. Reading this existing field
does not open a handle or query Windows. The `instance_id` property continues
to query Windows and retains its established behavior. No runtime API is added.
