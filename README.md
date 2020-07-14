# PlaidProject

To register on plaid:
URL: /plaid/plaid_app/
METHOD: POST
BODY: @param1:public_token, @param2:institution_id

To fetch the transactions:
URL: /plaid/transactions/
METHOD: GET
QUERY_PARAMS: @param1:institution_id, @param2:account_id

To fetch the accounts:
URL: /plaid/accounts/
METHOD: GET
QUERY_PARAMS: @param1:institution_id
