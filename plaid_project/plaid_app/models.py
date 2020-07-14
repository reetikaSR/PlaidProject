# system imports
from django.db.utils import IntegrityError
from django.contrib.postgres.fields.array import ArrayField
from django.db import models


# local imports
from ..users.models import User


class PlaidToken(models.Model):
    access_token = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_id = models.CharField(max_length=128)
    institution_id = models.CharField(max_length=64)

    class Meta:
        index_together = ('user', 'institution_id')
        unique_together = ('user', 'institution_id')

    def __str__(self):
        return "item_id:{pk} user:{user}".format(pk=self.item_id, user=self.user_id)


class Account(models.Model):
    """Account Model.
    """
    id = models.CharField(max_length=128, primary_key=True)
    name = models.CharField(max_length=64)
    available_balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    type = models.CharField(max_length=64)
    sub_type = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_id = models.CharField(max_length=128)

    def __str__(self):
        return "account_id:{pk} account_name:{name}".format(pk=self.pk, name=self.name)


class Transaction(models.Model):
    account_id = models.CharField(max_length=128)
    account_owner = models.CharField(max_length=128, null=True)  # todo: can be an object
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=128, unique=True)
    transaction_date = models.DateTimeField()
    category_id = models.CharField(max_length=64)
    category = ArrayField(models.CharField(max_length=64), default=list)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class LogEvents(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=64)
    link_session_id = models.CharField(max_length=64, null=True)
    request_id = models.CharField(max_length=64)
    message = models.TextField()
    code = models.CharField(max_length=64)


def log_event(user_id, code, message, request_id, type, link_session_id=None):
    LogEvents.objects.create(user_id=user_id,
                             type=type,
                             link_session_id=link_session_id,
                             request_id=request_id,
                             message=message,
                             code=code)


def create_plaid_token(item_id, user_id, access_token, institution_id):
    try:
        obj, created = PlaidToken.objects.get_or_create(
                item_id=item_id,
                user_id=user_id,
                access_token=access_token,
                institution_id=institution_id
            )
        return created
    except IntegrityError:
        return False
