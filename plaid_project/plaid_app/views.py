# system imports
import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from plaid import errors

# local imports
from .models import PlaidToken, Transaction, Account, create_plaid_token
from .serializers import PlaidTokenSerializer, TransactionSerializer, AccountSerializer
from .client import PlaidClient
from .signals import fetch_transactions, fetch_accounts
from .tasks import fetch_accounts_task, fetch_transactions_task


class PlaidTokenViewSet(viewsets.ModelViewSet):
    queryset = PlaidToken.objects.all()
    serializer_class = PlaidTokenSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        public_token = request.data.get('public_token', None)
        institution_id = request.data.get('institution_id', None)

        # bad request if any one of them is missing
        if not institution_id:
            return Response("Invalid Institution Id", status=status.HTTP_400_BAD_REQUEST)

        exchange = self.exchange_token(public_token, request.user.id)

        retries = 0

        while exchange is None and retries < 3:
            public_token = PlaidTokenViewSet.create_public_token(institution_id)
            exchange = self.exchange_token(public_token, request.user.id)
            retries += 1

        if exchange is None:
            return Response("Try Again!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # save the access token and the item id
        created = create_plaid_token(exchange['item_id'], request.user.id, exchange['access_token'], institution_id)

        fetch_accounts.send(sender=self.__class__, access_token=exchange['access_token'], user_id=request.user.id,
                            item_id=exchange['item_id'])

        if created:
            return Response("Item Created", status=status.HTTP_201_CREATED)
        else:
            return Response("Item already exists for this institution", status=status.HTTP_409_CONFLICT)

    @staticmethod
    def create_public_token(institution_id):
        try:
            headers = {'Content-Type': "application/json"}
            data = {
                "institution_id":institution_id,
                "public_key": settings.PLAID_PUBLIC_KEY,
                "initial_products": ["transactions", "auth"]}
            response = requests.post(url="https://sandbox.plaid.com/sandbox/public_token/create", headers=headers,
                                     data=json.dumps(data))
            return json.loads(response.content.decode('utf-8'))['public_token']
        except Exception:
            return None

    def exchange_token(self, public_token, user_id):
        # get the client wrapper
        client = PlaidClient()

        return client.exchange_token(user_id, public_token)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def list(self, request, *args, **kwargs):
        institution_id = request.query_params.get('institution_id', None)
        account_id = request.query_params.get('account_id')

        if not institution_id or not account_id:
            return Response("Invalid Institution id or Account Id", status=status.HTTP_400_BAD_REQUEST)

        try:
            plaid_token = PlaidToken.objects.get(user_id=request.user.id, institution_id=institution_id)
        except PlaidToken.DoesNotExist:
            return Response("user not registered with this institution", status=status.HTTP_401_UNAUTHORIZED)

        queryset = self.get_queryset().filter(account_id=account_id).order_by('-transaction_date')

        transactions = TransactionSerializer(queryset, many=True).data

        return Response(transactions, status=status.HTTP_200_OK)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def list(self, request, *args, **kwargs):
        institution_id = request.query_params.get('institution_id', None)

        if not institution_id:
            return Response("Invalid Institution id", status=status.HTTP_400_BAD_REQUEST)

        try:
            plaid_token = PlaidToken.objects.get(user_id=request.user.id, institution_id=institution_id)
        except PlaidToken.DoesNotExist:
            return Response("User not registered with this institution", status=status.HTTP_401_UNAUTHORIZED)

        queryset = self.get_queryset().filter(item_id=plaid_token['item_id'])

        accounts = AccountSerializer(queryset, many=True)

        return Response(accounts, status=status.HTTP_200_OK)


def handle_webhook(payload):
    if payload['webhook_type'] != 'TRANSACTIONS':
        return

    if payload['webhook_code'] == 'INITIAL_UPDATE':
        plaid_token = PlaidToken.objects.get(item_id=payload['item_id'])
        fetch_transactions_task.delay(plaid_token['user_id'], plaid_token['access_token'])
    elif payload['webhook_code'] == 'HISTORICAL_UPDATE':
        plaid_token = PlaidToken.objects.get(item_id=payload['item_id'])
        fetch_transactions_task.delay(plaid_token['user_id'], plaid_token['access_token'])
    elif payload['webhook_code'] == 'DEFAULT_UPDATE':
        plaid_token = PlaidToken.objects.get(item_id=payload['item_id'])
        fetch_transactions_task.delay(plaid_token['user_id'], plaid_token['access_token'])
    elif payload['webhook_code'] == 'TRANSACTIONS_REMOVED':
        Transaction.objects.delete(transaction_id__in=payload['removed_transactions'])


@api_view(['POST', ])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated, ))
def webhook_receiver(request):
    if 'payload' in request.POST:
        payload = json.loads(request.POST['payload'])
    else:
        payload = json.loads(request.body)

    handle_webhook(payload)

    return Response('Webhook received', status=status.HTTP_202_ACCEPTED)
