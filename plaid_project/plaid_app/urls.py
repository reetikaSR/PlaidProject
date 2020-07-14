from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'plaid_app', views.PlaidTokenViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'accounts', views.AccountViewSet)

app_name = "plaid_app"

urlpatterns = router.urls
