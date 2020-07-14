from rest_framework import serializers

from .models import PlaidToken, Transaction, Account


class PlaidTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaidToken
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'