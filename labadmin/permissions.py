from rest_framework.permissions import BasePermission
from rest_framework.authentication import get_authorization_header

from .models import Device


def get_token_from_request(request):
    auth = get_authorization_header(request).split()

    if len(auth) != 2:
        return None

    try:
        token = auth[1].decode()
    except UnicodeError:
        return None

    return token


class DeviceTokenPermission(BasePermission):
    def has_permission(self, request, view):
        token = get_token_from_request(request)
        if not token:
            return False

        try:
            Device.objects.get(token=token)
        except Device.DoesNotExist:
            return False

        return True
