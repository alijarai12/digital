from django.apps import AppConfig


class DmapsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dmaps"

    def ready(self):
        import dmaps.signals
