from django.apps import AppConfig


class GatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gates'
    def ready(self):
        from gates import scheduler
        scheduler.start()
