import django.dispatch

fetch_transactions = django.dispatch.Signal(providing_args=['access_token', 'user_id'])

fetch_accounts = django.dispatch.Signal(providing_args=['access_token', 'user_id', 'item_id'])