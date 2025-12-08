from django.conf import settings
from django.urls import reverse
from django.utils.translation import activate

from django_db_translate.translations import registry


class DBTranslateAdminMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Admin interface should always be in the default language
        if request.path.startswith(reverse('admin:index')):
            activate(settings.LANGUAGE_CODE)
            return self.get_response(request)

        lang = request.GET.get("lang")
        if lang is not None and lang in registry.available_locales_codes:
            activate(lang)
            request.LANGUAGE_CODE = lang
        else:
            lang = None

        response = self.get_response(request)

        if lang:
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )

        return response
