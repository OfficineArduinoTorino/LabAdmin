from django.contrib import admin, messages

from labadmin.models import (
    Card,
    Category,
    Device,
    Group,
    LogAccess,
    LogCredits,
    LogDevice,
    LogError,
    Payment,
    Role,
    Sketch,
    TimeSlot,
    UserProfile,
    DeviceUserCode,
)

from .forms import DeviceActionForm


class CardAdmin(admin.ModelAdmin):
    list_display = ('nfc_id', 'user', 'credits')
    search_fields = ('nfc_id', 'userprofile__user__username')
    ordering = ('-nfc_id',)

    def user(self, obj):
        try:
            return obj.userprofile.user
        except AttributeError:
            return 'n.d.'

    def save_model(self, request, obj, form, change):
        obj.save()
        obj.log_credits_update(amount=obj.credits, user=request.user, from_admin=True)

admin.site.register(Card, CardAdmin)


class DeviceUserCodeInline(admin.TabularInline):
    model = DeviceUserCode


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'card', 'displaygroups','firstSignup', 'lastSignup', 'subscription')
    ordering = ('name','-needSubscription','-endSubscription') # The negative sign indicate descendent order
    search_fields = ('card__nfc_id', 'name', 'user__username',)
    inlines = [DeviceUserCodeInline]

    def subscription(self, obj):
        return obj.endSubscription if obj.needSubscription else "lifetime membership"

admin.site.register(UserProfile, UserProfileAdmin)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'valid',)
    ordering = ('name',)

admin.site.register(Role, RoleAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)


admin.site.register(Group, GroupAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)

admin.site.register(Category, CategoryAdmin)

class SketchAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)

admin.site.register(Sketch, SketchAdmin)


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'hourlyCost', 'category', 'mac', 'last_activity')
    ordering = ('name',)
    action_form = DeviceActionForm
    actions = ['render_sketch_for_device']

    def render_sketch_for_device(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, 'Only one device sketch can be rendered at a time', level=messages.ERROR)
            return
        sketch_id = request.POST['sketch']
        sketch = Sketch.objects.get(pk=sketch_id)
        device = queryset.first()
        return sketch.render(device, request)

admin.site.register(Device, DeviceAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('date', 'value', 'user',)
    ordering = ('-date','user',)

admin.site.register(Payment, PaymentAdmin)


class LogAccessAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'user', 'card', 'opened', 'device')
    ordering = ('-datetime', 'card',)

    def user(self, obj):
        return obj.card.userprofile

admin.site.register(LogAccess,LogAccessAdmin)


class LogDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device', 'bootDevice', 'shutdownDevice', 'startWork', 'finishWork', 'inWorking', 'priceWork',)
    ordering = ('-bootDevice','-startWork',)

admin.site.register(LogDevice, LogDeviceAdmin)

class LogErrorAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'description', 'code', 'device')
    ordering = ('-datetime',)

admin.site.register(LogError, LogErrorAdmin)

class LogCreditsAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'card', 'amount', 'user', 'from_admin')
    list_filter = ('user',)

admin.site.register(LogCredits, LogCreditsAdmin)


class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'weekday_start', 'weekday_end', 'hour_start', 'hour_end',)
    ordering = ('name',)

admin.site.register(TimeSlot, TimeSlotAdmin)
