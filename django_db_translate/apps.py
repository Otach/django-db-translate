from django.apps import AppConfig
from django.contrib import admin


class DBTranslateConfig(AppConfig):
    name = 'django_db_translate'
    label = "dbtranslate"

    def ready(self):
        from .admin import site
        site._registry = admin.site._registry

