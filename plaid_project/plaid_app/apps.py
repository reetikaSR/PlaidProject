from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PlaidAppConfig(AppConfig):
    name = "plaid_project.plaid_app"
    verbose_name = _("plaid_app")

    def ready(self):
        try:
            import plaid_project.plaid_app.signals  # noqa F401
        except ImportError:
            pass
