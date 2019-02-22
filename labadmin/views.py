import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext as _
from django.db import transaction, IntegrityError
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin

from labadmin.forms import UserProfileForm
from labadmin.serializers import (
    UserProfileSerializer, CardSerializer, CardUpdateSerializer
)
from labadmin.models import (
    Card,
    Device,
    Group,
    LogAccess,
    LogDevice,
    LogError,
    UserProfile,
    DeviceUserCode
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from oauth2_provider.models import AccessToken

from .notifications import mqtt_publish
from .permissions import (
    get_token_from_request, DeviceTokenPermission
)


MQTT_ENTRANCE_TOPIC = getattr(settings, 'LABADMIN_MQTT_ENTRANCE_TOPIC', 'labadmin/entrance')


class LoginByNFC(APIView):
    """
    API For Login (return user informations)
    In order to use this API send a POST with a value named 'nfc_id'
    The return value is a json array with users associated to the card

    If the nfc code isn't correct or valid, the API save in 'LogError' a new error that contains the error then return an error message to client (HTTP_400_BAD_REQUEST)
    """

    def post(self, request, format=None):
        nfc = request.data.get('nfc_id')
        users = UserProfile.objects.filter(card__nfc_id=nfc)
        if not users.exists():
            LogError(description="Api: Login By NFC - NFC not Valid", code=nfc).save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        return Response(UserProfileSerializer(users, many=True).data, status=status.HTTP_200_OK)


class GetUserFromNFCMixin(object):
    def get_card_user_from_nfc_id(self, nfc_id):
        try:
            card = Card.objects.get(nfc_id=nfc_id)
            user = card.userprofile
        except Card.DoesNotExist:
            card = None
            user = None
        return card, user


class GetUserFromDeviceUserCodeMixin(object):
    def get_card_user_from_code(self, code, device):
        try:
            device_user_code = DeviceUserCode.objects.get(code=code, device=device)
            user = device_user_code.userprofile
            card = user.card
        except DeviceUserCode.DoesNotExist:
            card = None
            user = None
        return card, user


class OpenDoor(APIView, GetUserFromNFCMixin, GetUserFromDeviceUserCodeMixin):
    """
    API For Opening the Door
    In order to use this API send a POST with one of:
        - 'nfc_id': nfc id as integer
        - 'code': 64 char max code
    The nfc_id will match a Card, the code will match a DeviceUserCode.
    The return value is a json array with:
        'users': an object with 'id' and 'name' of users
        'utype': 'fablab' if there's a user in the 'Fablab'group or 'other'
        'datetime': datetime objects of the current time
        'open': return if the user can open the door or not

    If the nfc code isn't correct or valid, the API save in 'LogError' a new error that contains the error then return an alert message to client (HTTP_400_BAD_REQUEST)
    If the card does not have permissions to open the door a status code of 403 is returned to the user
    """

    permission_classes = (DeviceTokenPermission,)

    def post(self, request, format=None):
        token = get_token_from_request(request)
        try:
            device = Device.objects.get(token=token)
        except Device.DoesNotExist:
            LogError(description="Api: Open Door - token not valid", code=token or '').save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        nfc_id = request.data.get('nfc_id')
        card, user = self.get_card_user_from_nfc_id(nfc_id)

        if user is None:
            code = request.data.get('code')
            card, user = self.get_card_user_from_code(code, device)

        if user is None:
            if nfc_id:
                LogError.objects.create(
                    description="Api: Open Door - nfc ID not valid", code=nfc_id, device=device
                )
            else:
                LogError.objects.create(
                    description="Api: Open Door - device code not valid",
                    code=code or '',
                    device=device
                )
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        can_open = user.can_use_device_now(device)
        users = UserProfile.objects.filter(pk=user.pk)
        log_access = LogAccess.objects.log(card=card, opened=can_open, device=device)
        if not can_open:
            return Response("", status=status.HTTP_403_FORBIDDEN)

        users_pks = users.values_list('pk', flat=True)
        if Group.objects.filter(userprofile__in=users_pks, name__icontains='Fablab').exists():
            utype = "fablab"
        else:
            utype = "other"

        MQTT_ENTRANCE_NOTIFICATION = getattr(settings, 'LABADMIN_NOTIFY_MQTT_ENTRANCE', False)
        if MQTT_ENTRANCE_NOTIFICATION and log_access.opened:
            payload = {
                'user': user.name,
                'state': _('entrance')
            }
            try:
                mqtt_publish(MQTT_ENTRANCE_TOPIC, json.dumps(payload))
            except Exception as e:
                LogError(description="Api: Open Door By NFC - failed to publish to mqtt", code=e, device=device).save()

        data = {
            "users": UserProfileSerializer(users, many=True).data,
            "type": utype,
            "datetime": log_access.datetime,
            "open": log_access.opened
        }
        return Response(data, status=status.HTTP_201_CREATED)


class DeviceStartUse(APIView, GetUserFromNFCMixin, GetUserFromDeviceUserCodeMixin):
    """
    API to track the start of a device usage by an user.
    In case of success returns a json HTTP 201
    Adds a new 'LogDevice' object if the user can use the device, otherwise returns an error.

    In order to use this API send a POST with one of:
        - 'nfc_id': nfc id as integer
        - 'code': code, max 64 char
    The nfc_id will match a Card, the code will match a DeviceUserCode.
    """

    permission_classes = (DeviceTokenPermission,)

    def post(self, request, format=None):
        token = get_token_from_request(request)
        try:
            device = Device.objects.get(token=token)
        except Device.DoesNotExist:
            LogError(description="Api: Use Device - token not valid", code=token or '').save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        nfc_id = request.data.get('nfc_id')
        card, user = self.get_card_user_from_nfc_id(nfc_id)

        if user is None:
            code = request.data.get('code')
            card, user = self.get_card_user_from_code(code, device)

        if user is None:
            if nfc_id:
                LogError.objects.create(
                    description="Api: Use Device - nfc ID not valid", code=nfc_id, device=device
                )
            else:
                LogError.objects.create(
                    description="Api: Use Device - code not valid", code=code or '', device=device
                )
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        if not user.can_use_device_now(device):
            LogError.objects.create(
                description="Api: Use Device - card {} can't use device {}".format(nfc_id, token),
                device=device
            )
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        # cleanup leaked instances
        log = LogDevice.objects.filter(device=device, inWorking=True)
        for ll in log:
            ll.stop()

        now = timezone.now()
        log = LogDevice.objects.create(
            device=device, user=user, startWork=now, bootDevice=now,
            shutdownDevice=now + timezone.timedelta(seconds=10),
            finishWork=now + timezone.timedelta(seconds=10),
            hourlyCost=device.hourlyCost
        )
        return Response(
            {"cost": log.hourlyCost}, status=status.HTTP_201_CREATED
        )


class DeviceStopUse(APIView, GetUserFromNFCMixin, GetUserFromDeviceUserCodeMixin):
    """
    API to track the stop of a device usage by an user.
    In case of success returns a json HTTP 200
    Updates the 'LogDevice' object for the user on this device, otherwise returns an error.

    In order to use this API send a POST with one of:
        - 'nfc_id': nfc id as integer
        - 'code': code, max 64 char
    The nfc_id will match a Card, the code will match a DeviceUserCode.
    """

    permission_classes = (DeviceTokenPermission,)

    def post(self, request, format=None):
        token = get_token_from_request(request)
        try:
            device = Device.objects.get(token=token)
        except Device.DoesNotExist:
            LogError(description="Api: Stop use Device - token not valid", code=token or '').save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)


        nfc_id = request.data.get('nfc_id')
        card, user = self.get_card_user_from_nfc_id(nfc_id)

        if user is None:
            code = request.data.get('code')
            card, user = self.get_card_user_from_code(code, device)

        if user is None:
            if nfc_id:
                LogError.objects.create(
                    description="Api: Stop use Device - nfc ID not valid", code=nfc_id, device=device
                )
            else:
                LogError.objects.create(
                    description="Api: Stop use Device - code not valid", code=code or '', device=device
                )
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        try:
            log = LogDevice.objects.get(device=device, user=user, inWorking=True)
        except LogDevice.DoesNotExist:
            code = "card {} for device with token {}".format(nfc_id, token)
            LogError(description="Api: Stop use Device - no device log found", code=code, device=device).save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        log.stop()

        return Response({"cost": log.priceWork()}, status=status.HTTP_200_OK)


class UserIdentity(APIView):
    def get(self, request, format=None):
        token_string = request.GET.get('access_token')
        now = timezone.now()
        token = get_object_or_404(AccessToken, token=token_string, expires__gt=now, user__isnull=False)
        user = token.user
        if not user.is_active:
            raise Http404

        try:
            up = user.userprofile
        except UserProfile.DoesNotExist:
            up = None

        content = {
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
        }

        if up:
            meta = request.META
            if meta['SERVER_PORT'] and meta['SERVER_PORT'] not in ('443', '80'):
                port = ':{}'.format(meta['SERVER_PORT'])
            else:
                port = ''
            base_url = '{}://{}{}'.format(request.scheme, meta['SERVER_NAME'], port)
            groups = up.groups.values_list('name', flat=True)
            content.update({
                'name': up.name,
                'avatar_url': '{}{}'.format(base_url, up.picture.url) if up.picture else '',
                'bio': up.bio or '',
                'groups': groups,
            })
        return Response(content)

class CardCredits(APIView):
    """
    API for getting card credits
    In order to use this API send a GET with:
    - 'nfc_id', to identifiy the card

    The return value is a json array with the nfc_id and the credits amount for the card.

    If the nfc code isn't valid a 'LogError' instance is saved and returns 400 status code
    """

    permission_classes = (DeviceTokenPermission,)

    def get(self, request, format=None):
        token = get_token_from_request(request)
        try:
            device = Device.objects.get(token=token)
        except Device.DoesNotExist:
            LogError(description="Api: Update Card Credits - token not valid", code=token or '').save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        nfc = request.query_params.get('nfc_id')
        try:
            card = Card.objects.get(nfc_id=nfc)
        except Card.DoesNotExist:
            LogError(description="Api: Update Card Credits - NFC not Valid", code=nfc or '', device=device).save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        return Response(CardSerializer(card).data, status=status.HTTP_200_OK)

    """
    API for updating card credits
    In order to use this API send a POST with:
    - 'nfc_id', to identifiy the card
    - 'amount', integer to add to credit amount

    The return value is a json array with the nfc_id and new credits amount for the card.

    The amount must be negative and if there's not enough credits it'll returns 403 status code
    If the amount or the nfc code isn't valid a 'LogError' instance is saved and status code 400 returned
    """
    def post(self, request, format=None):
        token = get_token_from_request(request)
        try:
            device = Device.objects.get(token=token)
        except Device.DoesNotExist:
            LogError(description="Api: Update Card Credits - token not valid", code=token or '').save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        serializer = CardUpdateSerializer(data=request.data)
        nfc = serializer.initial_data.get('nfc_id')
        if not serializer.is_valid():
            LogError(description="Api: Update Card Credits - Invalid data", code=nfc or '', device=device).save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        try:
            # avoid race conditions updating the card model
            with transaction.atomic():
                try:
                    card = Card.objects.get(nfc_id=nfc)
                except Card.DoesNotExist:
                    LogError(description="Api: Update Card Credits - NFC not Valid", code=nfc, device=device).save()
                    return Response("", status=status.HTTP_400_BAD_REQUEST)

                amount = serializer.data['amount']
                if amount >= 0:
                    msg = "Api: Update Card Credits - amount can only be negative: {}".format(
                        amount
                    )
                    LogError(description=msg, code=nfc, device=device).save()
                    return Response("", status=status.HTTP_400_BAD_REQUEST)

                new_amount = card.credits + amount
                if new_amount < 0:
                    msg = "Api: Update Card Credits - Not enough credits: requested {} of {} available".format(
                        amount, card.credits
                    )
                    LogError(description=msg, code=nfc, device=device).save()
                    return Response("", status=status.HTTP_403_FORBIDDEN)

                # update the card with the new credits amount
                card.credits = new_amount
                card.save(update_fields=['credits'])
                user = request.user if request.user.is_authenticated() else None
                card.log_credits_update(amount=amount, user=user)

        except IntegrityError:
            LogError(description="Api: Update Card Credits - IntegrityError", code=nfc, device=device).save()
            return Response("", status=status.HTTP_400_BAD_REQUEST)

        return Response(CardSerializer(card).data, status=status.HTTP_200_OK)


class UserProfileView(TemplateResponseMixin, View):
    template_name = 'labadmin/userprofile.html'

    def get(self, request, *args, **kwargs):
        try:
            up = request.user.userprofile
        except UserProfile.DoesNotExist:
            up = None
        form = UserProfileForm(instance=up)
        return self.render_to_response({'form': form, 'user': request.user})

    def post(self, request, *args, **kwargs):
        try:
            up = request.user.userprofile
        except UserProfile.DoesNotExist:
            up = None
        form = UserProfileForm(request.POST, request.FILES, instance=up)
        if form.is_valid():
            up = form.save(commit=False)
            up.user = request.user
            if not up.endSubscription:
                up.endSubscription = timezone.now()
            up.save()
            messages.add_message(request, messages.INFO, 'Profile updated correctly')
            return redirect('labadmin-user-profile')
        return self.render_to_response({'form': form, 'user': request.user})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfileView, self).dispatch(*args, **kwargs)
