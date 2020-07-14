# system imports
from django.contrib import admin
from django.contrib.admin import ModelAdmin

# local imports
from .models import Account, PlaidToken
from .forms import AccountAdminForm, PlaidTokenAdminForm


@admin.register(Account)
class AccountAdmin(ModelAdmin):

    form = AccountAdminForm


@admin.register(PlaidToken)
class PlaidTokenAdmin(ModelAdmin):

    form = PlaidTokenAdminForm
