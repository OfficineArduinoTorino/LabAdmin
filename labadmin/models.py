from django.db import models
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import Template, Context
from django.utils import timezone
from django.utils.text import slugify

from versatileimagefield.fields import VersatileImageField

import uuid


class TimeSlotManager(models.Manager):
    def can_now(self):
        """Filters the queryset for this moment"""
        n = timezone.now()
        qs = self.get_queryset()
        return qs.filter(
            hour_start__lte=n.time(),
            hour_end__gte=n.time(),
            weekday_start__lte=n.isoweekday(),
            weekday_end__gte=n.isoweekday()
        )


class TimeSlot(models.Model):
    """
    TimeSlots are assigned to Roles
    """
    WEEKDAY_CHOICES = (
        (1,'Monday'),
        (2,'Tuesday'),
        (3,'Wednesday'),
        (4,'Thursday'),
        (5,'Friday'),
        (6,'Saturday'),
        (7,'Sunday')
    )
    name=models.CharField(max_length=50)
    weekday_start=models.SmallIntegerField(default=0, choices=WEEKDAY_CHOICES)
    weekday_end=models.SmallIntegerField(default=0, choices=WEEKDAY_CHOICES)
    hour_start=models.TimeField()
    hour_end=models.TimeField()

    objects = TimeSlotManager()

    def have_permission_now(self):
        n = timezone.now()
        return self.weekday_start <= n.weekday <= self.weekday_end and self.hour_start <= n.time <= self.hour_end

    def __str__(self):
        return "%s: %s - %s, %s - %s"%(self.name, self.WEEKDAY_CHOICES[self.weekday_start-1][1],self.WEEKDAY_CHOICES[self.weekday_end-1][1],self.hour_start,self.hour_end)


class Card(models.Model):
    """A card with a radio device"""
    nfc_id = models.BigIntegerField(unique=True)
    credits = models.IntegerField(default=0)

    def __str__(self):
        return "{}".format(self.nfc_id)

    def log_credits_update(self, amount, user=None, from_admin=False):
        LogCredits.objects.create(
            card=self,
            amount=amount,
            user=user,
            from_admin=from_admin,
        )


class UserProfile(models.Model):
    """
    The User Profile
    """
    user=models.OneToOneField(User)

    name=models.CharField(max_length=200)
    address = models.CharField(max_length=200, null=True, blank=True)
    tax_code = models.CharField(max_length=50, null=True, blank=True)
    vat_id = models.CharField(max_length=50, null=True, blank=True)
    picture = VersatileImageField(upload_to="labadmin/users/pictures", null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    firstSignup = models.DateField(null=True)
    lastSignup = models.DateField(null=True)
    endSubscription = models.DateField()
    needSubscription = models.BooleanField(default=True)

    card = models.OneToOneField(Card, null=True, blank=True)

    # define Many-To-Many fields
    groups=models.ManyToManyField('Group')

    def subscription_end(self):
        return self.endSubscription if self.needSubscription else "Subscription not needed"

    def has_valid_subscription(self):
        if not self.needSubscription:
            return True
        return self.needSubscription and self.endSubscription > timezone.now().date()

    def can_use_device_now(self, device):
        if not self.has_valid_subscription():
            return False
        roles = self.groups.values_list('roles__pk', flat=True).distinct()
        return TimeSlot.objects.can_now().filter(
            role__in=roles, role__valid=True, role__categories=device.category
        ).exists()

    def displaygroups(self):
        data = []
        for g in self.groups.all():
            data.append(g.name)
        return ",".join(data)

    def __str__(self):
        return self.name

class Category(models.Model):
    name=models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return "%s"%(self.name)

class Group(models.Model):
    name=models.CharField(max_length=50)
    # define Many-To-Many fields
    roles=models.ManyToManyField('Role')

    def __str__(self):
        return self.name

class Role(models.Model):
    name=models.CharField(max_length=50)

    time_slots=models.ManyToManyField(TimeSlot)
    valid=models.BooleanField(default=True)

    # define Many-To-Many Fieds
    categories=models.ManyToManyField('Category',blank=True)

    def __str__(self):
        return self.name


class Sketch(models.Model):
    name = models.CharField(max_length=100)
    code = models.TextField()
    file_format = models.CharField(max_length=10, default='.txt')

    def __str__(self):
        return self.name

    def render(self, device, request):
        t = Template(self.code)
        c = Context({'device': device, 'user': request.user.userprofile})
        data = t.render(c)
        slug = slugify('{} {}'.format(device.name, self.name))
        filename = '{}{}'.format(slug, self.file_format)

        response = HttpResponse(data, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response

    class Meta:
        verbose_name_plural = 'Sketches'


class Device(models.Model):
    name = models.CharField(max_length=100)
    hourlyCost = models.FloatField(default=0.0)
    category = models.ForeignKey('Category')
    mac = models.CharField(max_length=30)
    token = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return "%010d - %s" %(self.id, self.name)

    def last_activity(self):
        logaccess = self.logaccess_set.order_by('-id').first()
        if logaccess:
            return str(logaccess)
        logdevice = self.logdevice_set.order_by('-id').first()
        if not logdevice:
            return ''
        if logdevice.inWorking:
            return timezone.now()
        return logdevice.finishWork

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
        super(Device, self).save(*args, **kwargs)


class DeviceUserCode(models.Model):
    """A code that permits access to a device for a specific user"""
    userprofile = models.ForeignKey(UserProfile)
    device = models.ForeignKey(Device)
    code = models.CharField(max_length=64)

    def __str__(self):
        return self.code

    class Meta:
        unique_together = (('userprofile', 'device', 'code'),)


class Payment(models.Model):
    date = models.DateField(default=timezone.now().today)
    value=models.FloatField(default=0.0)
    user=models.ForeignKey(UserProfile)

class LogError(models.Model):
    datetime = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=200)
    code = models.CharField(default='', blank=True, max_length=200)
    device = models.ForeignKey(Device, null=True, blank=True)

class LogAccessManager(models.Manager):
    def log(self, card, opened, device):
        l = LogAccess.objects.create(card=card, opened=opened, device=device)
        return l

class LogAccess(models.Model):
    datetime = models.DateTimeField(default=timezone.now)
    card = models.ForeignKey(Card)
    opened = models.BooleanField(default=False)
    device = models.ForeignKey(Device, null=True, blank=True)

    objects= LogAccessManager()

    def __str__(self):
        return "{:%d/%m/%Y %H:%M} {} enter {}permitted".format(
            self.datetime, self.card.userprofile, "" if self.opened else "not "
        )

class LogDevice(models.Model):
    hourlyCost=models.FloatField(default=0.0)
    user=models.ForeignKey('UserProfile')
    device=models.ForeignKey('Device')
    bootDevice=models.DateTimeField()
    startWork=models.DateTimeField()
    finishWork=models.DateTimeField()
    shutdownDevice=models.DateTimeField()
    inWorking=models.BooleanField(default=True)

    def priceWork(self):
        if self.inWorking:
            return 'inWorking...'
        delta = self.finishWork - self.startWork
        duration = delta.total_seconds() / 3600
        return round(self.hourlyCost * duration, 2)

    def stop(self):
        n = timezone.now()
        self.inWorking = False
        self.finishWork = n
        self.shutdownDevice = n
        self.save(update_fields=['finishWork', 'shutdownDevice', 'inWorking'])

    def __str__(self):
        return "user: %s\ndevice: %s\nboot: %s\nstart: %s\ninWorking: %s\nHourlyCost: %f" %(self.user, self.device, self.bootDevice, self.startWork, "yes" if self.inWorking else "no\nshutdown: %s\nfinish: %s"%(self.shutdownDevice, self.finishWork), self.hourlyCost)


class LogCredits(models.Model):
    datetime = models.DateTimeField(default=timezone.now)
    card = models.ForeignKey(Card)
    amount = models.IntegerField()
    user = models.ForeignKey(User, null=True, blank=True)
    from_admin = models.BooleanField(default=False)

    def __str__(self):
        if self.from_admin:
            return '{} {} set credits for card {} to {} from admin'.format(
                self.datetime,
                self.user,
                self.card,
                self.amount
            )
        return '{} {} updated credits for card {} by {}'.format(
            self.datetime,
            self.user if self.user else '<AnonymousUser>',
            self.card,
            self.amount
        )
