from pysetupdi import Device


def invalid_stored_read(device: Device) -> None:
    number: int = device._instance_id  # E
    print(number)


def invalid_stored_return(device: Device) -> int:
    return device._instance_id  # E
