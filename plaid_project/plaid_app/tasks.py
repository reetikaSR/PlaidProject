from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import transaction
from config import celery_app
from django.dispatch import receiver

from .signals import fetch_transactions, fetch_accounts
from .models import Transaction, Account
from .client import PlaidClient


@celery_app.task(name='fetch_transactions_task')
def fetch_transactions_task(user_id, access_token):
    client = PlaidClient()

    curr_date = datetime.now()

    then_date = curr_date - relativedelta(years=2)

    transactions = client.get_transactions(user_id, access_token,
                                           then_date.strftime('%Y-%m-%d'),
                                           curr_date.strftime('%Y-%m-%d'))

    existing_transactions = \
        {t.id: t for t in Transaction.objects.select_for_update()
            .filter(transaction_id__in=[t['transaction_id'] for t in transactions])}

    list_transaction_create_objs= []
    list_transaction_update_objs= []

    for transaction in transactions:
        if transaction['transaction_id'] in existing_transactions:
            new_transaction = existing_transactions['transaction_id']
            map_transaction_obj(new_transaction, transaction, user_id)
            list_transaction_update_objs.append(new_transaction)
        else:
            new_transaction = Transaction()
            map_transaction_obj(new_transaction, transaction, user_id)
            list_transaction_create_objs.append(new_transaction)

    with transaction.atomic():
        Transaction.objects.bulk_update(list_transaction_update_objs, ignore_conflicts=True)

    with transaction.atomic():
        Transaction.objects.bulk_create(list_transaction_create_objs, ignore_conflicts=True)


@celery_app.task(name='fetch_accounts_task')
def fetch_accounts_task(user_id, access_token, item_id):
    client = PlaidClient()

    accounts, message = client.get_accounts(user_id, access_token)

    list_account_objs = []

    for account in accounts:
        new_account = Account()
        new_account.id = account['account_id']
        new_account.name = account['name']
        new_account.type = account['type']
        new_account.sub_type = account['subtype']
        new_account.available_balance = account['balances']['available'] if account['balances']['available'] else 0
        new_account.current_balance = account['balances']['current'] if account['balances']['current'] else 0
        new_account.user_id = user_id
        new_account.item_id = item_id

        list_account_objs.append(new_account)

    with transaction.atomic():
        Account.objects.bulk_create(list_account_objs, ignore_conflicts=True)


@receiver(fetch_transactions)
def fetch_transactions_signal_receiver(sender, access_token, user_id, *args, **kwargs):
    fetch_transactions_task.delay(access_token, user_id)


@receiver(fetch_accounts)
def fetch_accounts_signal_receiver(sender, access_token, user_id, *args, **kwargs):
    fetch_accounts_task.delay(access_token, user_id)


def map_transaction_obj(new_transaction, transaction, user_id):
    new_transaction.account_id = transaction['account_id']
    new_transaction.account_owner = transaction['account_owner']
    new_transaction.amount = transaction['amount']
    new_transaction.transaction_id = transaction['transaction_id']
    new_transaction.transaction_date = datetime.strptime(transaction['date'], '%Y-%m-%d')
    new_transaction.category_id = transaction['category_id']
    new_transaction.category = transaction['category']
    new_transaction.user_id = user_id

