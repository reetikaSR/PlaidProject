# system imports
from django import forms

# local imports
from .models import Account, PlaidToken


class PlaidTokenAdminForm(forms.ModelForm):

    class Meta:
        model = PlaidToken
        fields = '__all__'


class AccountAdminForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = '__all__'
