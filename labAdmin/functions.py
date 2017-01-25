from labAdmin.models import (
    Device
)


def get_device_by_mac_or_None(mac):
    """
    Function that return the Device that has the mac passed as parameter else returns None
    """
    try:
        d = Device.objects.get(mac=mac)
        return d
    except Device.DoesNotExist:
        return None
