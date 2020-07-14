from plaid import Client
from plaid import errors
from django.conf import settings
from .models import log_event


class PlaidClient:
    def __init__(self):
        self.client = Client(client_id=settings.PLAID_CLIENT_ID,
                             secret=settings.PLAID_SECRET,
                             public_key=settings.PLAID_PUBLIC_KEY,
                             environment=settings.PLAID_ENV)

    def exchange_token(self, user_id, public_token):
        try:
            exchange = self.client.Item.public_token.exchange(public_token)
            return exchange
        except errors.PlaidError as e:
            log_event(user_id, e.code, e.message, e.request_id, e.type)

        return None

    def get_transactions(self, user_id, access_token, start_date, end_date, account_ids=None):
        try:
            response = self.client.Transactions.get(access_token, start_date=start_date, end_date=end_date,
                                                    account_ids=account_ids)

            transactions = response['transactions']

            # the transactions in the response are paginated, so make multiple calls while increasing the offset to
            # retrieve all transactions
            while len(transactions) < response['total_transactions']:
                response = self.client.Transactions.get(access_token, start_date=start_date, end_date=end_date,
                                                        offset=len(transactions)
                                                        )
                transactions.extend(response['transactions'])

            return transactions
        except errors.PlaidError as e:
            log_event(user_id, e.code, e.message, e.request_id, e.type)

        return list()

    def get_accounts(self, user_id, access_token):
        try:
            response = self.client.Auth.get(access_token)
            return response['accounts'], "OK"
        except errors.PlaidError as e:
            log_event(user_id, e.code, e.message, e.request_id, e.type)
        return list(), e.message


