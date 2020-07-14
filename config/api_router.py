from django.conf import settings
from django.conf.urls import url
from django.urls.conf import include
from rest_framework.routers import DefaultRouter, SimpleRouter

from plaid_project.users.api.views import UserViewSet

router = DefaultRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls'))
    ]
