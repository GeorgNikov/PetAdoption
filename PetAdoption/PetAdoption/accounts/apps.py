from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PetAdoption.accounts'

    def ready(self):
        import PetAdoption.accounts.signals
