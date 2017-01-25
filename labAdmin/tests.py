import datetime
import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone, dateparse

from .models import (
    Card, Group, LogAccess, Role, TimeSlot, UserProfile,
    LogCredits, Category, Device, LogDevice
)


class TestLabAdmin(TestCase):
    @classmethod
    def setUpTestData(cls):
        full_timeslot = TimeSlot.objects.create(
            name="any day",
            weekday_start=1,
            weekday_end=7,
            hour_start=dateparse.parse_time("00:00:00"),
            hour_end=dateparse.parse_time("23:59:59"),
        )

        full_devices_role = Role.objects.create(
            name="Devices Access",
        )
        full_devices_role.time_slots.add(full_timeslot)

        devices_group = Group.objects.create(name="Full Devices access")
        devices_group.roles.add(full_devices_role)

        card = Card.objects.create(nfc_id=123456)
        user = User.objects.create(username="alessandro.monaco")
        u = UserProfile.objects.create(
            user=user,
            card=card,
            name="Alessandro Monaco",
            needSubscription=False,
            endSubscription=timezone.now()
        )
        u.groups.add(devices_group)

        noperm_card = Card.objects.create(nfc_id=654321)
        noperm_user = User.objects.create(username="nopermission")
        noperm_up = UserProfile.objects.create(
            user=noperm_user,
            card=noperm_card,
            name="No Permission",
            needSubscription=False,
            endSubscription=timezone.now()
        )

        category = Category.objects.create(
            name="category"
        )
        full_devices_role.categories.add(category)

        device = Device.objects.create(
            name="device",
            hourlyCost=1.0,
            category=category,
            mac="00:00:00:00:00:00"
        )

        cls.card = card
        cls.noperm_card = noperm_card
        cls.userprofile = u
        cls.noperm_userprofile = noperm_up
        cls.device = device

    def test_login_by_nfc(self):
        client = Client()
        url = reverse('nfc-users')
        data = {
            'nfc_id': self.card.nfc_id
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(len(response_data), 1)
        user_profile = response_data[0]
        self.assertEqual(user_profile['id'], self.userprofile.pk)
        self.assertEqual(user_profile['name'], self.userprofile.name)

        data = {
            'nfc_id': 0
        }
        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)

        response = client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_open_door_by_nfc(self):

        self.assertFalse(LogAccess.objects.all().exists())

        client = Client()
        auth = 'Token {}'.format(self.device.token)
        url = reverse('open-door-nfc')
        data = {
            'nfc_id': self.card.nfc_id
        }
        response = client.post(url, data, format='json', HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertIn('users', response_data)
        self.assertEqual(len(response_data['users']), 1)
        user_profile = response_data['users'][0]
        self.assertEqual(user_profile['id'], self.userprofile.pk)
        self.assertEqual(user_profile['name'], self.userprofile.name)
        self.assertEqual(response_data['type'], 'other')
        self.assertIn('datetime', response_data)
        self.assertEqual(response_data['open'], self.userprofile.can_use_device_now(self.device))

        users = UserProfile.objects.all()
        logaccess = LogAccess.objects.filter(users=users, card=self.card)
        self.assertTrue(logaccess.exists())

        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

        data = {
            'nfc_id': 0
        }
        response = client.post(url, data, format='json', HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        response = client.get(url, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 405)

    def test_get_card_credits(self):

        client = Client()
        url = reverse('card-credits')
        card = Card.objects.create(
            nfc_id=1,
            credits=1
        )
        data = {
            'nfc_id': card.nfc_id
        }

        auth = 'Token {}'.format(self.device.token)
        response = client.get(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response_data, {
            'nfc_id': card.nfc_id,
            'credits': 1
        })

        data = {
            'nfc_id': 0
        }
        response = client.get(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        # no auth token
        response = client.get(url, data)
        self.assertEqual(response.status_code, 403)

    def test_update_card_credits(self):
        client = Client()
        auth = 'Token {}'.format(self.device.token)
        url = reverse('card-credits')
        card = Card.objects.create(
            nfc_id=1,
            credits=10
        )

        self.assertEqual(LogCredits.objects.count(), 0)

        # not enough credits
        data = {
            'nfc_id': card.nfc_id,
            'amount': -20
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 403)

        # can't add credits
        data = {
            'nfc_id': card.nfc_id,
            'amount': 10
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        # consume credits
        data = {
            'nfc_id': card.nfc_id,
            'amount': -10
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(str(response.content, encoding='utf8'))
        self.assertEqual(response_data, {
            'nfc_id': 1,
            'credits': 0
        })

        self.assertEqual(LogCredits.objects.count(), 1)

        data = {
            'nfc_id': 0
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        data = {
            'nfc_id': 1,
            'amount': 'amount'
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        # no auth
        data = {
            'nfc_id': 0
        }
        response = client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_device_token_creation(self):
        category = Category.objects.create(
            name="category"
        )

        device = Device.objects.create(
            name="device",
            hourlyCost=1.0,
            category=category,
            mac="00:00:00:00:00:00"
        )
        self.assertTrue(device.token)

        # token is created once
        old_token = device.token
        device.save()
        device = Device.objects.get(pk=device.pk)
        self.assertEqual(old_token, device.token)

    def test_device_stop(self):
        now = timezone.now()
        logdevice = LogDevice.objects.create(
            device=self.device,
            user=self.userprofile,
            bootDevice=now,
            startWork=now,
            shutdownDevice=now,
            finishWork=now,
            hourlyCost=self.device.hourlyCost,
        )
        logdevice.stop()
        self.assertEqual(logdevice.startWork, logdevice.bootDevice)
        self.assertTrue(logdevice.startWork < logdevice.finishWork)
        self.assertEqual(logdevice.finishWork, logdevice.shutdownDevice)

    def test_logdevice_pricework(self):
        now = timezone.now()
        logdevice = LogDevice.objects.create(
            device=self.device,
            user=self.userprofile,
            bootDevice=now,
            startWork=now,
            shutdownDevice=now,
            finishWork=now,
            hourlyCost=self.device.hourlyCost,
        )

        self.assertEqual(logdevice.priceWork(), 'inWorking...')
        logdevice.stop()
        logdevice.finishWork = logdevice.finishWork + datetime.timedelta(seconds=60)
        logdevice.save()
        self.assertEqual(logdevice.priceWork(), 0.02)

    def test_device_last_activity(self):
        self.assertEqual(self.device.last_activity(), '')

        now = timezone.now()
        logdevice = LogDevice.objects.create(
            device=self.device,
            user=self.userprofile,
            bootDevice=now,
            startWork=now,
            shutdownDevice=now,
            finishWork=now,
            hourlyCost=self.device.hourlyCost,
        )

        self.assertTrue(logdevice.inWorking)
        self.assertTrue(self.device.last_activity() >= logdevice.startWork)

        logdevice.stop()
        self.assertFalse(logdevice.inWorking)
        self.assertEqual(self.device.last_activity(), logdevice.finishWork)

    def test_device_start_use(self):
        client = Client()
        auth = 'Token {}'.format(self.device.token)
        url = reverse('device-use-start')

        self.assertFalse(LogDevice.objects.filter(device=self.device).exists())

        # not authenticated
        data = {
            'nfc_id': self.card.nfc_id,
        }
        response = client.post(url, data)
        self.assertEqual(response.status_code, 403)

        # invalid data
        data = {
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        data = {
            'nfc_id': 0
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        # not enough permissions
        data = {
            'nfc_id': self.noperm_card.nfc_id,
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        # ok
        data = {
            'nfc_id': self.card.nfc_id,
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(LogDevice.objects.count(), 1)
        self.assertTrue(
            LogDevice.objects.filter(device=self.device, user=self.userprofile, inWorking=True).exists()
        )
        self.assertJSONEqual(response.content.decode('utf-8'), {
            'cost': self.device.hourlyCost
        })

        # ok too but the previous LogDevice is closed
        data = {
            'nfc_id': self.card.nfc_id,
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(LogDevice.objects.count(), 2)
        self.assertEqual(
            LogDevice.objects.filter(device=self.device, user=self.userprofile, inWorking=True).count(), 1
        )

    def test_device_stop_use(self):
        client = Client()
        auth = 'Token {}'.format(self.device.token)
        url = reverse('device-use-stop')

        self.assertFalse(LogDevice.objects.filter(device=self.device).exists())

        # not authenticated
        data = {
            'nfc_id': self.card.nfc_id,
        }
        response = client.post(url, data)
        self.assertEqual(response.status_code, 403)

        # invalid data
        data = {
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        data = {
            'nfc_id': 0
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        # no open logdevice
        data = {
            'nfc_id': self.card.nfc_id,
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 400)

        now = timezone.now()
        LogDevice.objects.create(
            device=self.device,
            user=self.userprofile,
            startWork=now,
            bootDevice=now,
            shutdownDevice=now,
            finishWork=now,
            hourlyCost="0.0"
        )

        # ok
        data = {
            'nfc_id': self.card.nfc_id,
        }
        response = client.post(url, data, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LogDevice.objects.count(), 1)
        self.assertTrue(
            LogDevice.objects.filter(device=self.device, user=self.userprofile, inWorking=False).exists()
        )
        self.assertJSONEqual(response.content.decode('utf-8'), {
            'cost': 0
        })

    def test_user_can_use_device_now(self):
        self.assertTrue(self.userprofile.can_use_device_now(self.device))

    def test_user_can_use_device_now_invalid_role(self):
        timeslot = TimeSlot.objects.create(
            name="any day for invalid role",
            weekday_start=1,
            weekday_end=7,
            hour_start=dateparse.parse_time("00:00:00"),
            hour_end=dateparse.parse_time("23:59:59"),
        )

        role = Role.objects.create(
            name="invalid role",
            valid=False
        )
        role.time_slots.add(timeslot)

        group = Group.objects.create(name="group with invalid role")
        group.roles.add(role)
        self.noperm_userprofile.groups.add(group)
        self.assertFalse(self.noperm_userprofile.can_use_device_now(self.device))

    def test_user_can_use_device_now_no_group(self):
        self.assertFalse(self.noperm_userprofile.can_use_device_now(self.device))

    def test_user_can_use_device_role_not_categories(self):
        timeslot = TimeSlot.objects.create(
            name="any day",
            weekday_start=1,
            weekday_end=7,
            hour_start=dateparse.parse_time("00:00:00"),
            hour_end=dateparse.parse_time("23:59:59"),
        )

        role = Role.objects.create(
            name="role",
        )
        role.time_slots.add(timeslot)

        group = Group.objects.create(name="group")
        group.roles.add(role)
        self.noperm_userprofile.groups.add(group)
        self.assertFalse(self.noperm_userprofile.can_use_device_now(self.device))


class TimeSlotTests(TestCase):
    def test_timeslot_manager_now(self):
        now = timezone.now()
        now_time = now.time()
        now_weekday = now.isoweekday()

        # enough for the tests to work :)
        end = now + datetime.timedelta(minutes=1)
        end_time = end.time()
        end_weekday = now.isoweekday()

        self.assertFalse(TimeSlot.objects.can_now().exists())

        open_ts = TimeSlot.objects.create(
            hour_start=now_time,
            hour_end=end_time,
            weekday_start=now_weekday,
            weekday_end=end_weekday
        )

        closed_ts_weekday = TimeSlot.objects.create(
            hour_start=now_time,
            hour_end=end_time,
            weekday_start=end_weekday+1,
            weekday_end=end_weekday+1
        )

        closed_ts_hour = TimeSlot.objects.create(
            hour_start=now_time,
            hour_end=now_time,
            weekday_start=now_weekday,
            weekday_end=end_weekday
        )

        ts_now = TimeSlot.objects.can_now()
        self.assertTrue(ts_now.exists())
        self.assertEqual(ts_now.count(), 1)
        self.assertEqual(ts_now.first().pk, open_ts.pk)