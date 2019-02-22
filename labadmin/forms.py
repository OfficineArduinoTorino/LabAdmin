from django import forms
from django.contrib.admin.helpers import ActionForm

from .models import Sketch, UserProfile


class DeviceActionForm(ActionForm):
    sketch = forms.ModelChoiceField(queryset=Sketch.objects.all(), empty_label=None)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'name', 'picture', 'address', 'tax_code', 'vat_id', 'bio'
        ]
