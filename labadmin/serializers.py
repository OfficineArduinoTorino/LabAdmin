from labadmin.models import (
    Card, UserProfile
)

from rest_framework import serializers


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('id','name')


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('nfc_id', 'credits')


class CardUpdateSerializer(serializers.Serializer):
    nfc_id = serializers.IntegerField()
    amount = serializers.IntegerField()

# class LogdoorSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Logdoor
#         fields = ('id', 'hour', 'user','doorOpened')
#
# class NfcSerializer(serializers.ModelSerializer):
#
#     def get_object(self):
#         try:
#             u = UserProfile.objects.get(nfcId=self.nfcId)
#             return u
#         except UserProfile.DoesNotExist:
#             return None
#
#     class Meta:
#         model = UserProfile
#         fields = ('id','nfcId')
#
# class UserProfileSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = UserProfile
#         fields = ('id', 'username','utype', 'signup', 'subscriptionEnd', 'needSubcription', 'nfcId')

# class PermissionSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Permission
#         fields = ("id","user","devicetype","level")
#
#
# class LogdeviceSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Logdevice
#         fields = (
#             'id'
#             ,'user'
#             ,'device'
#             ,'bootDevice'
#             ,'shutdownDevice'
#             ,'startWork'
#             ,'finishWork'
#             ,'hourlyCost'
#         )
