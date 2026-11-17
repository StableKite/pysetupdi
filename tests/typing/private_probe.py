from pysetupdi import Device


def private_identifier(device: Device) -> str:
    return device._instance_id
